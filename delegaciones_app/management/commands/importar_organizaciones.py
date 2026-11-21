import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from delegaciones_app.models import Delegacion, Organizacion

# Columna «Territ. deleg.» del Excel del municipio y la delegación del sistema. ALFALFARES y las filas sin
# territorio quedan sin delegación para que la coordinación las asigne a mano.
DELEGACION_POR_TERRITORIO = {
    'CIAS': 'Las Compañías', 'PAMPA': 'La Pampa', 'ANTENA': 'La Antena', 'AV DEL MAR': 'Avenida del Mar',
    'CENTRO': 'Centro', 'RURAL': 'Rural',
}

# Tipos del documento de requerimientos de octubre 2026, en orden: gana la primera regla que calza con el nombre.
# Lo que no calza es funcional: la Ley 19.418 distingue juntas de vecinos (territoriales) y organizaciones funcionales.
REGLAS_DE_TIPO = (
    ('junta_vecinos', r'JUNTAS? DE VECINOS|JUNTA VECINAL|^JJ\.? ?VV'),
    # Los comités de vivienda o de agua potable rural suelen constituirse como organizaciones funcionales.
    ('funcional', r'COMITE (DE |PRO )?(LA )?(VIVIENDA|AGUA|HABITACIONAL)|AGUA POTABLE|\bAPR\b'),
    ('adulto_mayor', r'ADULTOS? MAYOR(ES)?|TERCERA EDAD|ABUELIT'),
    ('deportiva', r'DEPORT|FUTBOL|RAYUELA|BASQUET|VOLEIBOL|ATLETISMO|CICLISMO|TENIS|BOXEO|KARATE|SKATE|\bSURF|PATIN|HANDBOL'),
    ('cultural', r'CENTRO DE MADRES|CENTRO DE PADRES|CULTURA|JUVENIL|JOVENES|FOLCLOR|FOLKLOR|\bBAILE|DANZA|\bCORO\b|MUSIC|TEATRO|\bARTE|ARTESAN|TALLER|CONJUNTO'),
    ('comite', r'\bCOMITE'),
)


def normalizar(texto):
    """Mayúsculas, sin tildes y con un solo espacio entre palabras."""
    sin_tildes = unicodedata.normalize('NFKD', str(texto or '')).encode('ascii', 'ignore').decode()
    return re.sub(r'\s+', ' ', sin_tildes).strip().upper()


def delegacion_de_territorio(territorio, delegaciones):
    """Delegación del territorio del Excel (CIAS, PAMPA, etc.) o por su nombre; None si no corresponde a ninguna."""
    clave = normalizar(territorio)
    nombre = DELEGACION_POR_TERRITORIO.get(clave, clave)
    return delegaciones.get(normalizar(nombre))


class Command(BaseCommand):
    help = 'Importa organizaciones comunitarias desde JSON o XLSX y conserva los registros no verificados.'

    def add_arguments(self, parser):
        parser.add_argument('archivo', type=Path)
        parser.add_argument('--anonimizar', action='store_true', help='Reemplaza domicilios por un texto neutro.')

    def handle(self, *args, **options):
        archivo = options['archivo']
        if not archivo.exists():
            raise CommandError(f'No existe el archivo {archivo}.')
        try:
            datos = self._leer_archivo(archivo)
        except (OSError, ValueError, ImportError) as error:
            raise CommandError(f'No se pudo leer el archivo de organizaciones: {error}') from error
        if not isinstance(datos, list):
            raise CommandError('El archivo debe contener una lista de organizaciones.')
        delegaciones = {normalizar(d.nombre): d for d in Delegacion.objects.all()}
        creadas = actualizadas = 0
        for fila in datos:
            nombre = str(fila.get('nombre') or fila.get('organizacion') or '').strip()
            if not nombre:
                continue
            territorio = str(fila.get('territorio') or fila.get('localidad') or '').strip()
            tipo = self._tipo(nombre, fila.get('tipo'))
            delegacion = delegacion_de_territorio(territorio, delegaciones)
            domicilio = 'Domicilio anonimizado' if options['anonimizar'] else str(fila.get('domicilio') or '').strip()
            defaults = {
                'tipo': tipo,
                'personalidad_juridica': str(fila.get('personalidad_juridica') or fila.get('rut') or '').strip(),
                'domicilio': domicilio,
                'socios_activos': self._entero(fila.get('socios_activos')),
                'fecha_constitucion': self._fecha(fila.get('fecha_constitucion')),
                'numero_registro': str(fila.get('numero_registro') or '').strip(),
                'fecha_inscripcion': self._fecha(fila.get('fecha_inscripcion')),
                'registro_direccion': str(fila.get('registro_direccion') or '').strip(),
                'delegacion': delegacion,
                'verificada': bool(delegacion and territorio),
                'observaciones': '' if delegacion else f'Importada sin delegación: territorio «{territorio or "sin dato"}». Asignar a mano.',
                'activa': True,
            }
            objeto, creado = Organizacion.objects.update_or_create(
                nombre=nombre, territorio=territorio, defaults=defaults,
            )
            creadas += int(creado)
            actualizadas += int(not creado)
        self.stdout.write(self.style.SUCCESS(f'Organizaciones creadas: {creadas}; actualizadas: {actualizadas}.'))

    @staticmethod
    def _leer_archivo(archivo):
        if archivo.suffix.lower() == '.json':
            return json.loads(archivo.read_text(encoding='utf-8'))
        if archivo.suffix.lower() not in ('.xlsx', '.xlsm'):
            raise ValueError('El archivo debe ser JSON o XLSX.')
        from openpyxl import load_workbook

        hoja = load_workbook(archivo, read_only=True, data_only=True).active
        filas = list(hoja.iter_rows(values_only=True))
        if not filas:
            return []
        encabezados = [str(valor or '').strip().casefold() for valor in filas[0]]
        aliases = {
            'nombre': ('organizaciones', 'organizacion', 'organización'),
            'domicilio': ('domicilio legal', 'domicilio'),
            'territorio': ('territ. deleg.', 'territorio', 'delegación'),
            'socios_activos': ('socios activos',),
            'fecha_constitucion': ('fecha constit.', 'fecha constitucion'),
            'numero_registro': ('n° reg. p.j.', 'nº reg. p.j.', 'numero registro'),
            'fecha_inscripcion': ('fecha inscripc en reg.', 'fecha inscripcion'),
            'registro_direccion': ('reg. dir. n°', 'reg. dir. nº', 'registro direccion'),
        }
        posiciones = {
            campo: next((encabezados.index(nombre) for nombre in nombres if nombre in encabezados), None)
            for campo, nombres in aliases.items()
        }
        return [
            {campo: fila[posicion] if posicion is not None and posicion < len(fila) else None for campo, posicion in posiciones.items()}
            for fila in filas[1:]
        ]

    @staticmethod
    def _entero(valor):
        try:
            return int(valor) if valor not in (None, '') else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _fecha(valor):
        if not valor:
            return None
        if hasattr(valor, 'date'):
            return valor.date()
        for formato in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y'):
            try:
                return datetime.strptime(str(valor).strip(), formato).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def _tipo(nombre, tipo):
        valor = str(tipo or '').lower()
        if valor:
            opciones = {clave: clave for clave, _ in Organizacion.TIPOS}
            if valor in opciones:
                return valor
        texto = normalizar(nombre)
        if not texto:
            return 'sin_clasificar'
        return next((tipo for tipo, patron in REGLAS_DE_TIPO if re.search(patron, texto)), 'funcional')
