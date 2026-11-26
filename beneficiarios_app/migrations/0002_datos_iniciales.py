"""Datos iniciales del módulo de beneficiarios.

1. Las nueve unidades municipales del desplegable del Google Form. Las seis delegaciones se enlazan con su Delegacion
   si ya existe; si se crea después (seed_demo), el enlace se hace solo la primera vez que se usa (alcance.py).
2. La actividad «Navidad 2026» con inscripciones abiertas (el Google Form de fin de año que reemplaza este módulo).
3. Permisos por perfil:
   - los cuatro perfiles inscriben y ven las inscripciones de su unidad;
   - Coordinador y Administrador además modifican y eliminan cualquier inscripción y administran actividades y unidades.
"""
from django.contrib.auth.management import create_permissions
from django.db import migrations

APP = 'beneficiarios_app'
DELEGACIONES = ['Las Compañías', 'La Pampa', 'La Antena', 'Rural', 'Avenida del Mar', 'Centro']
OTRAS_UNIDADES = ['Gabinete', 'DIDECO', 'Departamento de la Familia']

BASICOS = ['add_inscripcion', 'view_inscripcion', 'view_evento']
GESTION = BASICOS + [
    'change_inscripcion', 'delete_inscripcion', 'add_evento', 'change_evento',
    'view_unidadmunicipal', 'add_unidadmunicipal', 'change_unidadmunicipal',
]
PERMISOS_POR_PERFIL = {
    'Administrador': GESTION,
    'Coordinador': GESTION,
    'Delegado': BASICOS,
    'Profesional': BASICOS,
}


def cargar(apps, schema_editor):
    UnidadMunicipal = apps.get_model(APP, 'UnidadMunicipal')
    Evento = apps.get_model(APP, 'Evento')
    Delegacion = apps.get_model('delegaciones_app', 'Delegacion')
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    for nombre in DELEGACIONES:
        UnidadMunicipal.objects.get_or_create(
            nombre=f'Delegación {nombre}',
            defaults={'delegacion': Delegacion.objects.filter(nombre__iexact=nombre).first()},
        )
    for nombre in OTRAS_UNIDADES:
        UnidadMunicipal.objects.get_or_create(nombre=nombre)
    Evento.objects.get_or_create(tipo='navidad', anio=2026, defaults={
        'descripcion': 'Actividad de fin de año - Infancias 2026', 'inscripciones_abiertas': True,
    })

    # En una base limpia los permisos de los modelos nuevos aún no existen cuando corre la migración.
    for app_config in apps.get_app_configs():
        if app_config.label == APP:
            app_config.models_module = True
            create_permissions(app_config, apps=apps, verbosity=0)
            app_config.models_module = None
    for perfil_nombre, codigos in PERMISOS_POR_PERFIL.items():
        perfil = Group.objects.filter(name=perfil_nombre).first()
        if perfil:
            perfil.permissions.add(*Permission.objects.filter(content_type__app_label=APP, codename__in=codigos))


def deshacer(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    for perfil_nombre, codigos in PERMISOS_POR_PERFIL.items():
        perfil = Group.objects.filter(name=perfil_nombre).first()
        if perfil:
            perfil.permissions.remove(*Permission.objects.filter(content_type__app_label=APP, codename__in=codigos))


class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('delegaciones_app', '0031_evaluacion3_datos'),
        (APP, '0001_inicial'),
    ]

    operations = [
        migrations.RunPython(cargar, deshacer),
    ]
