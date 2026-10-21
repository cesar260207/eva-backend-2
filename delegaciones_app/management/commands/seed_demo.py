import json
import os
import secrets
from datetime import date, datetime
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from delegaciones_app.models import (
    Actividad, Cargo, Catalogo, Compromiso, Delegacion, Evidencia, Funcionario, FuncionarioRol, Indicador, ItemMedible,
    MedicionDelegacion, Meta, ParametroVersionado, Periodo, Rol, UsuarioMaestro, Validacion,
)
from delegaciones_app.permisos import ROLES_DEL_SISTEMA

PERIODO = 'Trimestre julio-septiembre 2026'
ITEM = 'Seguridad y prevencion'

DELEGACIONES = {
    'Centro': ('Centro historico, administrativo, comercial y patrimonial', 'Atencion territorial y gestion del espacio publico.'),
    'Rural': ('Localidades y comunidades rurales dispersas', 'Acercamiento de servicios, emergencias y coordinacion intersectorial.'),
    'La Antena': ('Sector urbano oriental y barrios asociados', 'Participacion vecinal y apoyo social comunitario.'),
    'La Pampa': ('Sector urbano sur y areas residenciales', 'Asistencia social, subsidios y servicios comunitarios.'),
    'Avenida del Mar': ('Borde costero, turismo, residencial y servicios', 'Coordinacion estacional, seguridad y prevencion.'),
    'Las Compañías': ('Sector urbano norte de alta densidad', 'Gestión comunitaria y operativos sociales.'),
}

# (código, tipo, nombre): el catálogo se busca por tipo y nombre, así convive con lo que dejó la migración de datos.
CATALOGO = [
    ('ACT-TERR', 'actividad', 'Gestión territorial'),
    ('SRV-SOL', 'servicio', 'Solicitud ciudadana'),
    ('AT-OPER', 'atencion', 'Operativo en terreno'),
    ('AT-SOL', 'atencion', 'Solicitud ciudadana'),
    ('ITEM-SEG', 'item', ITEM),
]

ESTADOS_COMPROMISO = {'Pendiente': 'pendiente', 'En proceso': 'proceso', 'Realizado': 'realizado'}
ESTADOS_MEDICION = {'Verde': 'verde', 'Amarillo': 'amarillo', 'Rojo': 'rojo'}


class Command(BaseCommand):
    help = 'Carga delegaciones, funcionarios, metas y registros ficticios para la demostracion SGR (se puede repetir sin duplicar).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            help='Clave para las cuentas demo nuevas. Si se omite, se usa la variable DEMO_PASSWORD o se genera una aleatoria.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        clave = options.get('password') or os.environ.get('DEMO_PASSWORD')
        clave_generada = not clave
        if clave_generada:
            clave = secrets.token_urlsafe(12)
        self.clave = clave

        self.roles = {nombre: Rol.objects.get_or_create(nombre_rol=nombre)[0] for nombre in ROLES_DEL_SISTEMA}
        # Los cargos se crean solo si hace falta crear al funcionario, así no quedan sueltos en una base ya migrada.
        cargos = {
            'administrador': 'Administración SGR', 'coordinador': 'Coordinación SGR',
            'delegado': 'Delegado territorial', 'verificador': 'Verificación SGR',
        }
        delegaciones = {
            nombre: Delegacion.objects.update_or_create(nombre=nombre, defaults={'ambito': ambito, 'enfasis': enfasis, 'estado': True})[0]
            for nombre, (ambito, enfasis) in DELEGACIONES.items()
        }

        administrador = self._funcionario('admin.demo', 'Administrador', 'administrador', cargos['administrador'])
        self._funcionario('coordinador.demo', 'Coordinador SGR', 'coordinador', cargos['coordinador'])
        centro = self._funcionario('funcionario.centro', 'Funcionario Centro', 'funcionario', cargos['delegado'], delegaciones['Centro'])
        verificador = self._funcionario('verificador.demo', 'Verificador SGR', 'verificador', cargos['verificador'])
        self._configurar_administrador(administrador)

        # Un delegado por delegación; las que no tienen funcionario reciben uno con cuenta inactiva,
        # igual que la migración de datos, para que su meta tenga a quién asignarse.
        delegados = {'Centro': centro}
        for nombre, delegacion in delegaciones.items():
            if nombre != 'Centro':
                delegados[nombre] = self._funcionario(
                    f'delegado.{slugify(nombre)}', f'Delegado {nombre}', 'delegado', cargos['delegado'], delegacion, activo=False,
                )

        periodo = self._periodo()
        catalogo = self._catalogo()
        metas = self._metas(periodo, delegados)
        compromisos = self._compromisos(delegaciones, delegados)
        self._actividad_demo(delegaciones['Centro'], centro, verificador, metas['Centro'].item, catalogo[('atencion', 'Solicitud ciudadana')])
        mediciones = self._mediciones(delegaciones)
        indicadores = self._indicadores(periodo)

        if clave_generada:
            self.stdout.write(self.style.WARNING(f'Clave generada para las cuentas demo NUEVAS (se muestra una sola vez): {clave}'))
        self.stdout.write(f'{len(delegaciones)} delegaciones, {len(metas)} metas, {compromisos} compromisos, {mediciones} mediciones historicas, {indicadores} indicadores nuevos.')
        self.stdout.write(self.style.SUCCESS('Datos demo cargados. Cuentas demo: admin.demo, coordinador.demo, funcionario.centro, verificador.demo'))

    def _funcionario(self, username, nombre, rol, cargo_nombre, delegacion=None, activo=True):
        usuario, creado = User.objects.get_or_create(username=username, defaults={'first_name': nombre, 'is_active': activo})
        if creado:
            if activo:
                usuario.set_password(self.clave)
            else:
                usuario.set_unusable_password()
            usuario.save()
        funcionario = Funcionario.objects.filter(usuario=usuario).first()
        if funcionario is None:
            funcionario = Funcionario.objects.create(
                usuario=usuario, identificador_institucional=username, nombre=nombre, delegacion=delegacion, estado=activo,
                cargo=Cargo.objects.get_or_create(nombre=cargo_nombre)[0],
            )
        FuncionarioRol.objects.get_or_create(funcionario=funcionario, rol=self.roles[rol])
        return funcionario

    def _configurar_administrador(self, funcionario):
        usuario = funcionario.usuario
        usuario.is_staff = usuario.is_superuser = True
        usuario.save(update_fields=['is_staff', 'is_superuser'])
        UsuarioMaestro.objects.get_or_create(
            usuario=usuario,
            defaults={'identificador_maestro': usuario.username, 'nombre': funcionario.nombre, 'nivel_dominio': 'total'},
        )

    def _periodo(self):
        periodo = Periodo.objects.get_or_create(
            nombre=PERIODO,
            defaults={'fecha_inicio': date(2026, 7, 1), 'fecha_termino': date(2026, 9, 30), 'estado': 'abierto', 'umbral_minimo': 80, 'version_parametros': 1},
        )[0]
        ParametroVersionado.objects.get_or_create(
            periodo=periodo, clave='maximo_cumplimiento',
            defaults={'valor': '150', 'descripcion': 'Tope del cumplimiento de cada meta (RN-005).'},
        )
        return periodo

    def _catalogo(self):
        elementos = {}
        for codigo, tipo, nombre in CATALOGO:
            elemento = Catalogo.objects.filter(tipo=tipo, nombre=nombre).first()
            if elemento is None:
                elemento = Catalogo.objects.create(codigo=codigo, tipo=tipo, nombre=nombre, activo=True)
            elementos[(tipo, nombre)] = elemento
        return elementos

    def _metas(self, periodo, delegados):
        """Una meta de 10 actividades por delegación sobre un ítem compartido por cargo (suma 100 %, RN-001)."""
        metas = {}
        for nombre, delegado in delegados.items():
            item = ItemMedible.objects.get_or_create(nombre=ITEM, cargo=delegado.cargo, periodo=periodo, defaults={'ponderacion': 100})[0]
            metas[nombre] = Meta.objects.get_or_create(
                item=item, funcionario=delegado, defaults={'valor_objetivo': 10, 'unidad': 'actividades', 'ponderador': 100},
            )[0]
        return metas

    def _compromisos(self, delegaciones, delegados):
        """Carga inicial (una sola vez) desde data/solicitudes.json; las vistas ya no leen este archivo."""
        archivo = Path(__file__).resolve().parents[3] / 'data' / 'solicitudes.json'
        solicitudes = json.loads(archivo.read_text(encoding='utf-8')).get('solicitudes', [])
        total = 0
        for item in solicitudes:
            delegacion = delegaciones.get(item['delegacion'])
            if not delegacion:
                continue
            responsable = delegados[item['delegacion']]
            compromiso, creado = Compromiso.objects.update_or_create(folio=item['folio'], defaults={
                'delegacion': delegacion, 'funcionario_responsable': responsable, 'origen': 'externo',
                'solicitante': 'Organizacion territorial', 'territorio': item['delegacion'], 'eje': item.get('eje', 'Gestión Social'),
                'descripcion': item['descripcion'], 'fecha_comprometida': date.fromisoformat(item['fecha_compromiso']),
                'fecha_ingreso': date.fromisoformat(item['fecha_ingreso']), 'estado': ESTADOS_COMPROMISO.get(item['estado'], 'ingresado'),
            })
            if creado:
                compromiso.registrar_historial(responsable, '', 'Carga inicial desde solicitudes.json')
            total += 1
        return total

    def _actividad_demo(self, delegacion, autor, verificador, item, tipo_atencion):
        actividad, creada = Actividad.objects.get_or_create(codigo_verificador='EVD-DEMO-0001', defaults={
            'funcionario_autor': autor, 'delegacion': delegacion, 'item': item, 'catalogo': tipo_atencion,
            'fecha_hora': timezone.make_aware(datetime(2026, 9, 1, 10, 0)),
            'solicitud_problema': 'Orientacion vecinal sobre reparacion de luminaria.',
            'accion': 'Derivacion a unidad municipal responsable y seguimiento territorial.',
        })
        if creada:
            # La evidencia es ficticia (sin archivo): permite mostrar una actividad aprobada que suma al avance (RN-009).
            evidencia = Evidencia.objects.create(
                actividad=actividad, funcionario_autor=autor, archivo_vinculo='evidencias/demo/acta-demo.pdf',
                metadatos={'comentario': 'Evidencia ficticia de demostracion, sin archivo.'},
            )
            Validacion(evidencia=evidencia, funcionario_verificador=verificador).aprobar_evidencia('Aprobada en la carga de demostracion.')

    def _mediciones(self, delegaciones):
        archivo = Path(__file__).resolve().parents[3] / 'data' / 'metas_delegaciones.json'
        total = 0
        for item in json.loads(archivo.read_text(encoding='utf-8')).get('delegaciones', []):
            delegacion = delegaciones.get(item['nombre'])
            if not delegacion:
                continue
            MedicionDelegacion.objects.update_or_create(
                delegacion=delegacion, fecha_datos=date.fromisoformat(item['ultimos_datos']),
                defaults={
                    'cumplimiento': item['cumplimiento'], 'meta': item['meta'],
                    'estado_reportado': ESTADOS_MEDICION[item['estado']], 'observacion': item.get('observacion', ''),
                },
            )
            total += 1
        return total

    def _indicadores(self, periodo):
        """Calcula el indicador de las metas que todavía no tienen ninguno."""
        if periodo.estado == 'cerrado':
            return 0
        nuevos = 0
        for meta in Meta.objects.filter(item__periodo=periodo).select_related('funcionario', 'item__periodo'):
            if not meta.indicadores.exists():
                Indicador.generar(meta)
                nuevos += 1
        return nuevos
