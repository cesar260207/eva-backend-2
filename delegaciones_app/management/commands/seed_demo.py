import json
from datetime import date
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from delegaciones_app.models import Actividad, CatalogoItem, Compromiso, Delegacion, MetaMedicion, PerfilUsuario, PeriodoMedicion


class Command(BaseCommand):
    help = 'Carga delegaciones, usuarios y registros ficticios para la demostracion SGR.'

    def handle(self, *args, **options):
        delegaciones = {
            'Centro': ('Centro historico, administrativo, comercial y patrimonial', 'Atencion territorial y gestion del espacio publico.'),
            'Rural': ('Localidades y comunidades rurales dispersas', 'Acercamiento de servicios, emergencias y coordinacion intersectorial.'),
            'La Antena': ('Sector urbano oriental y barrios asociados', 'Participacion vecinal y apoyo social comunitario.'),
            'La Pampa': ('Sector urbano sur y areas residenciales', 'Asistencia social, subsidios y servicios comunitarios.'),
            'Avenida del Mar': ('Borde costero, turismo, residencial y servicios', 'Coordinacion estacional, seguridad y prevencion.'),
            'Las Compañías': ('Sector urbano norte de alta densidad', 'Gestión comunitaria y operativos sociales.'),
        }
        objetos = {}
        for nombre, datos in delegaciones.items():
            objetos[nombre], _ = Delegacion.objects.update_or_create(nombre=nombre, defaults={'territorio': datos[0], 'enfasis': datos[1], 'activa': True})

        cuentas = [
            ('admin.demo', 'Administrador', 'administrador', None),
            ('coordinador.demo', 'Coordinador SGR', 'coordinador', None),
            ('funcionario.centro', 'Funcionario Centro', 'funcionario', 'Centro'),
            ('verificador.demo', 'Verificador SGR', 'verificador', None),
        ]
        usuarios = {}
        for username, nombre, rol, delegacion in cuentas:
            usuario, creado = User.objects.get_or_create(username=username, defaults={'first_name': nombre})
            if creado:
                usuario.set_password('Demo2026!')
                usuario.save()
            if rol == 'administrador':
                usuario.is_staff = True
                usuario.is_superuser = True
                usuario.save(update_fields=['is_staff', 'is_superuser'])
            PerfilUsuario.objects.update_or_create(usuario=usuario, defaults={'rol': rol, 'delegacion': objetos.get(delegacion)})
            usuarios[username] = usuario

        # Carga inicial (una sola vez): los compromisos ficticios se importan
        # desde data/solicitudes.json hacia la base de datos relacional. Las
        # vistas de la aplicacion ya NO leen este archivo; solo se usa aqui
        # como fuente de datos de demostracion.
        archivo = Path(__file__).resolve().parents[3] / 'data' / 'solicitudes.json'
        solicitudes = json.loads(archivo.read_text(encoding='utf-8')).get('solicitudes', [])
        funcionario = usuarios['funcionario.centro']
        for item in solicitudes:
            delegacion = objetos.get(item['delegacion'])
            if not delegacion:
                continue
            Compromiso.objects.update_or_create(folio=item['folio'], defaults={'delegacion': delegacion, 'responsable': funcionario, 'solicitante': 'Organizacion territorial', 'territorio': item['delegacion'], 'eje': item.get('eje', 'Gestión Social'), 'descripcion': item['descripcion'], 'fecha_comprometida': item['fecha_compromiso'], 'estado': {'Pendiente': 'pendiente', 'En proceso': 'proceso', 'Realizado': 'realizado'}.get(item['estado'], 'ingresado')})

        Actividad.objects.get_or_create(codigo='EVD-DEMO-0001', defaults={'funcionario': funcionario, 'delegacion': objetos['Centro'], 'fecha': date(2026, 9, 1), 'tipo_atencion': 'Solicitud ciudadana', 'descripcion': 'Orientacion vecinal sobre reparacion de luminaria.', 'accion': 'Derivacion a unidad municipal responsable y seguimiento territorial.', 'item_medicion': 'Seguridad y prevencion', 'estado': 'aprobada'})
        for nombre, objetivo in [('Centro', 10), ('Rural', 10), ('La Antena', 10), ('La Pampa', 10), ('Avenida del Mar', 10), ('Las Compañías', 10)]:
            MetaMedicion.objects.update_or_create(delegacion=objetos[nombre], nombre='Seguridad y prevencion', defaults={'objetivo': objetivo, 'periodo_inicio': date(2026, 7, 1), 'periodo_termino': date(2026, 9, 30), 'ponderador': 100, 'activa': True})
        PeriodoMedicion.objects.update_or_create(nombre='Trimestre julio-septiembre 2026', defaults={'inicio': date(2026, 7, 1), 'termino': date(2026, 9, 30), 'estado': 'abierto', 'version_parametros': 1, 'umbral_colectivo': 80, 'maximo_cumplimiento': 150})
        catalogos = [
            ('actividad', 'ACT-TERR', 'Gestión territorial'),
            ('servicio', 'SRV-SOL', 'Solicitud ciudadana'),
            ('atencion', 'AT-OPER', 'Operativo en terreno'),
            ('item', 'ITEM-SEG', 'Seguridad y prevencion'),
        ]
        for categoria, codigo, nombre in catalogos:
            CatalogoItem.objects.update_or_create(categoria=categoria, codigo=codigo, defaults={'nombre': nombre, 'activo': True})
        self.stdout.write(self.style.SUCCESS('Datos demo cargados. Usuario demo: coordinador.demo / Demo2026!'))
