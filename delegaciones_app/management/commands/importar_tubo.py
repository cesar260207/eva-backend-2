"""Importa una hoja TUBO o TUBO CARTAS de la Matriz SGR (exportada a CSV) como tareas del Tubo de seguimiento.

Uso:
    python manage.py importar_tubo "<carpeta>/02_TUBO_COMPANIAS.csv" --delegacion "Las Compañías"
    python manage.py importar_tubo "<carpeta>/04_TUBO_CARTAS.csv" --delegacion "Centro" --aplicar

Sin --aplicar solo revisa: muestra cuántas filas entrarían y por qué se descarta cada una, sin guardar nada.
El folio de cada tarea importada sale de su contenido (AGR-IMP-… o CAR-IMP-…), así que repetir la importación
no duplica tareas. Los archivos de la planilla tienen nombres y teléfonos reales: se leen desde la carpeta del
usuario y no se copian al repositorio (RNF-019).
"""
import csv
import hashlib
import re
from datetime import datetime
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from delegaciones_app.models import Compromiso, Delegacion, Funcionario, HistorialCompromiso
from delegaciones_app.permisos import DELEGADO

ESTADOS_SOLICITUD = {'INGRESADO': 'ingresado', 'PENDIENTE': 'pendiente', 'EN PROCESO': 'proceso', 'REALIZADO': 'realizado'}
# Tubo de cartas: «aprobada» espera la acción comprometida; «finalizada» y «no aplica» (solo para conocimiento) se cierran.
ESTADOS_CARTA = {'EN PROCESO': 'proceso', 'APROBADA': 'proceso', 'FINALIZADA': 'realizado', 'NO APLICA': 'realizado'}
COLUMNAS = {
    'solicitud': {
        'fecha': ('FECHA SOLICITUD',), 'descripcion': ('ACTIVIDAD/ SOLICITUD/ PROBLEMA', 'ACTIVIDAD/SOLICITUD/PROBLEMA'),
        'origen': ('INT EXT',), 'solicitante': ('SOLICITANTE',), 'territorio': ('TERRITORIO',), 'responsable': ('RESPONSABLE',),
        'compromiso': ('FECHA DE COMPROMISO',), 'apoyo': ('AREA/PERSONA APOYO',), 'observacion': ('AVANCE, OBSERVACIONES',),
        'estado': ('ESTATUS',),
    },
    'carta': {
        'fecha': ('FECHA',), 'numero': ('Nº', 'N°'), 'para': ('PARA',), 'solicitante': ('REMITE',), 'telefono': ('FONO CONTACTO',),
        'descripcion': ('ACTIVIDAD O TEMA',), 'compromiso': ('FECHA DE LA ACTIVIDAD',), 'responsable': ('ENCARGADO DE SEGUIMIENTO',),
        'estado': ('ESTADO',), 'apoyo': ('DERIVADA A',), 'observacion': ('OBSERVACION',),
    },
}


def _texto(valor):
    return re.sub(r'\s+', ' ', str(valor or '')).strip()


def leer_fecha(valor):
    """Fecha ISO (2026-07-06) o día/mes/año; None para textos como «13/7/ al 23» o años imposibles (0206)."""
    texto = _texto(valor)
    for formato in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
        try:
            fecha = datetime.strptime(texto[:10], formato).date()
        except ValueError:
            continue
        return fecha if 2000 <= fecha.year <= 2100 else None
    return None


def leer_telefono(valor):
    """Solo un teléfono chileno reconocible (8 o 9 dígitos, con o sin 56); un correo u otro texto se descarta."""
    digitos = re.sub(r'\D', '', _texto(valor))
    if digitos.startswith('56') and len(digitos) == 11:
        digitos = digitos[2:]
    return digitos if len(digitos) in (8, 9) else ''


def detectar_tipo(filas):
    cabecera = ' '.join(_texto(v).upper() for fila in filas[:2] for v in fila)
    return 'carta' if 'CARTA' in cabecera else 'solicitud'


def ubicar_columnas(filas, tipo):
    """Fila de encabezado y posición de cada campo, buscando los títulos de la hoja (no posiciones fijas)."""
    for numero, fila in enumerate(filas[:6]):
        titulos = [_texto(v).upper() for v in fila]
        posiciones = {}
        for campo, opciones in COLUMNAS[tipo].items():
            posiciones[campo] = next((titulos.index(op.upper()) for op in opciones if op.upper() in titulos), None)
        if posiciones['descripcion'] is not None and posiciones['estado'] is not None:
            return numero, posiciones
    raise CommandError('No se encontró la fila de encabezados del tubo (ACTIVIDAD y ESTATUS/ESTADO).')


def interpretar(fila, posiciones, tipo):
    """Datos de una tarea a partir de una fila, o un motivo de descarte."""
    def valor(campo):
        posicion = posiciones.get(campo)
        return _texto(fila[posicion]) if posicion is not None and posicion < len(fila) else ''

    descripcion, fecha = valor('descripcion'), leer_fecha(valor('fecha'))
    if not descripcion and not valor('fecha'):
        return None, None  # fila vacía de la plantilla (solo trae el número o la unidad)
    if not descripcion:
        return None, 'sin actividad o solicitud'
    if fecha is None:
        return None, 'sin fecha de ingreso válida'
    estados = ESTADOS_CARTA if tipo == 'carta' else ESTADOS_SOLICITUD
    estado_planilla = valor('estado').upper()
    estado = estados.get(estado_planilla, 'ingresado')
    compromiso = leer_fecha(valor('compromiso'))
    notas = []
    if valor('compromiso') and compromiso is None:
        notas.append(f'Fecha comprometida en la planilla: «{valor("compromiso")}».')
    if valor('responsable'):
        notas.append(f'Responsable en la planilla: {valor("responsable")}.')
    if tipo == 'carta':
        if valor('numero'):
            notas.append(f'Carta n.º {valor("numero")} dirigida a {valor("para") or "sin destinatario"}.')
        if estado_planilla in ('NO APLICA', 'APROBADA'):
            notas.append(f'Estado en la planilla: {estado_planilla.capitalize()}.')
    if valor('observacion'):
        notas.append(valor('observacion'))
    datos = {
        'tipo': tipo,
        'descripcion': descripcion,
        'fecha_ingreso': fecha,
        'fecha_comprometida': compromiso if compromiso and compromiso >= fecha else fecha,
        'origen': 'interno' if valor('origen').upper() == 'INT' else 'externo',
        'solicitante': valor('solicitante')[:255] or 'Sin dato',
        'solicitante_telefono': leer_telefono(valor('telefono')),
        'territorio': valor('territorio')[:255] or 'Sin dato',
        'area_apoyo': valor('apoyo')[:255] or None,
        'estado': estado,
        'observacion': '\n'.join(notas),
    }
    return datos, None


def folio_de(datos, delegacion):
    """Folio estable: el mismo contenido en la misma delegación siempre da el mismo folio."""
    huella = '|'.join([str(delegacion.pk), datos['tipo'], datos['fecha_ingreso'].isoformat(), datos['descripcion'], datos['solicitante']])
    prefijo = Compromiso.PREFIJOS_FOLIO[datos['tipo']]
    return f'{prefijo}-IMP-{hashlib.sha1(huella.encode("utf-8")).hexdigest()[:10].upper()}'


class Command(BaseCommand):
    help = 'Importa una hoja TUBO o TUBO CARTAS de la Matriz SGR (CSV) como tareas del Tubo. Sin --aplicar solo revisa.'

    def add_arguments(self, parser):
        parser.add_argument('archivo', type=Path)
        parser.add_argument('--delegacion', required=True, help='Delegación dueña del tubo (nombre exacto).')
        parser.add_argument('--responsable', help='Identificador institucional del funcionario responsable; por defecto, el delegado.')
        parser.add_argument('--tipo', choices=['solicitud', 'carta'], help='Tubo de destino; si se omite, se deduce del título de la hoja.')
        parser.add_argument('--aplicar', action='store_true', help='Guarda las tareas. Sin esta opción solo se revisa.')

    def handle(self, *args, **options):
        archivo = Path(options['archivo'])
        delegacion = Delegacion.objects.filter(nombre=options['delegacion']).first()
        if delegacion is None:
            raise CommandError(f'No existe la delegación «{options["delegacion"]}».')
        responsable = self._responsable(delegacion, options.get('responsable'))
        try:
            with archivo.open(encoding='utf-8-sig', newline='') as entrada:
                filas = list(csv.reader(entrada))
        except OSError as error:
            raise CommandError(f'No se pudo leer el archivo: {error}') from error
        tipo = options.get('tipo') or detectar_tipo(filas)
        encabezado, posiciones = ubicar_columnas(filas, tipo)

        nuevas, existentes, descartes = [], 0, {}
        vistos = set()
        for fila in filas[encabezado + 1:]:
            datos, motivo = interpretar(fila, posiciones, tipo)
            if datos is None:
                if motivo:
                    descartes[motivo] = descartes.get(motivo, 0) + 1
                continue
            folio = folio_de(datos, delegacion)
            if folio in vistos or Compromiso.objects.filter(folio=folio).exists():
                existentes += 1
                continue
            vistos.add(folio)
            nuevas.append((folio, datos))

        guardadas, errores = 0, []
        if options['aplicar'] and nuevas:
            with transaction.atomic():
                for folio, datos in nuevas:
                    tarea = Compromiso(folio=folio, delegacion=delegacion, funcionario_responsable=responsable, **datos)
                    try:
                        tarea.full_clean()
                    except ValidationError as error:
                        errores.append(f'{datos["fecha_ingreso"]} «{datos["descripcion"][:40]}»: {"; ".join(error.messages)}')
                        continue
                    tarea.save()
                    HistorialCompromiso.objects.create(
                        compromiso=tarea, autor=responsable, estado_anterior='', estado_nuevo=tarea.estado,
                        observacion=f'Importada desde la planilla ({archivo.name}).',
                    )
                    guardadas += 1

        nombre_tubo = dict(Compromiso.TIPOS)[tipo].lower()
        self.stdout.write(f'Tubo de {nombre_tubo} de {delegacion}: {len(nuevas)} tareas nuevas, {existentes} ya importadas.')
        for motivo, cantidad in sorted(descartes.items()):
            self.stdout.write(self.style.WARNING(f'Filas descartadas ({motivo}): {cantidad}'))
        for error in errores:
            self.stdout.write(self.style.ERROR(f'No se guardó {error}'))
        if options['aplicar']:
            self.stdout.write(self.style.SUCCESS(f'Se guardaron {guardadas} tareas.'))
        else:
            self.stdout.write('Solo revisión: no se guardó nada. Repite con --aplicar para importar.')

    @staticmethod
    def _responsable(delegacion, identificador):
        if identificador:
            funcionario = Funcionario.objects.filter(identificador_institucional=identificador, estado=True).first()
            if funcionario is None:
                raise CommandError(f'No existe un funcionario activo con el identificador «{identificador}».')
            return funcionario
        delegado = Funcionario.objects.filter(delegacion=delegacion, estado=True, roles__nombre_rol=DELEGADO).first()
        if delegado is None:
            raise CommandError(f'«{delegacion}» no tiene un delegado activo: indica el responsable con --responsable.')
        return delegado

