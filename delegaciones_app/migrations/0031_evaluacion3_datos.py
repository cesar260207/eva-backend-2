"""Evaluación 3: datos iniciales del modelo nuevo.

1. Territorios: se crean a partir del texto «territorio» de las organizaciones que ya tienen delegación, y cada
   organización queda enlazada a su unidad territorial (el texto original se conserva).
2. Permisos de los perfiles para las tablas nuevas (territorios, vecinos, membresías, hitos y subtipos de atención)
   y para consultar las gestiones sociales.
"""
from django.contrib.auth.management import create_permissions
from django.db import migrations

APP = 'delegaciones_app'
TODAS = ('view', 'add', 'change', 'delete')
NUEVOS = ('territorio', 'vecino', 'membresiaorganizacion', 'hito', 'responsablehito', 'subtipoatencion')


def _nombre_territorio(texto):
    return ' '.join((texto or '').split())[:255]


def crear_territorios(apps, schema_editor):
    Organizacion = apps.get_model(APP, 'Organizacion')
    Territorio = apps.get_model(APP, 'Territorio')
    cache = {}
    for organizacion in Organizacion.objects.filter(delegacion__isnull=False, unidad_territorial__isnull=True).exclude(territorio=''):
        nombre = _nombre_territorio(organizacion.territorio)
        if not nombre:
            continue
        clave = (organizacion.delegacion_id, nombre.lower())
        if clave not in cache:
            existente = Territorio.objects.filter(delegacion_id=organizacion.delegacion_id, nombre__iexact=nombre).first()
            cache[clave] = existente or Territorio.objects.create(delegacion_id=organizacion.delegacion_id, nombre=nombre)
        organizacion.unidad_territorial = cache[clave]
        organizacion.save(update_fields=['unidad_territorial'])


def quitar_territorios(apps, schema_editor):
    Organizacion = apps.get_model(APP, 'Organizacion')
    Organizacion.objects.update(unidad_territorial=None)
    apps.get_model(APP, 'Territorio').objects.all().delete()


def _permisos(Permission, codigos):
    encontrados = list(Permission.objects.filter(content_type__app_label=APP, codename__in=codigos))
    faltantes = set(codigos) - {permiso.codename for permiso in encontrados}
    if faltantes:
        raise RuntimeError('Faltan permisos para los perfiles: ' + ', '.join(sorted(faltantes)))
    return encontrados


PERMISOS_POR_PERFIL = {
    'Administrador': [f'{accion}_{modelo}' for modelo in NUEVOS for accion in TODAS],
    'Coordinador': [f'{accion}_{modelo}' for modelo in NUEVOS for accion in TODAS],
    # El delegado mantiene vecinos, membresías e hitos de su delegación; consulta territorios y subtipos.
    'Delegado': [
        'view_territorio', 'view_subtipoatencion', 'view_casosocial',
        *[f'{accion}_{modelo}' for modelo in ('vecino', 'membresiaorganizacion', 'hito', 'responsablehito') for accion in ('view', 'add', 'change')],
    ],
    # El profesional registra vecinos al atenderlos y consulta el resto; modifica solo sus gestiones sociales.
    'Profesional': [
        'view_territorio', 'view_subtipoatencion', 'view_hito', 'view_membresiaorganizacion',
        'view_vecino', 'add_vecino', 'change_vecino', 'view_casosocial', 'change_casosocial',
    ],
}


def asignar_permisos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    # En una base limpia los permisos de los modelos nuevos aún no existen cuando corre la migración.
    for app_config in apps.get_app_configs():
        if app_config.label == APP:
            app_config.models_module = True
            create_permissions(app_config, apps=apps, verbosity=0)
            app_config.models_module = None
    for nombre, codigos in PERMISOS_POR_PERFIL.items():
        perfil = Group.objects.filter(name=nombre).first()
        if perfil:
            perfil.permissions.add(*_permisos(Permission, codigos))


def quitar_permisos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    for nombre, codigos in PERMISOS_POR_PERFIL.items():
        perfil = Group.objects.filter(name=nombre).first()
        if perfil:
            perfil.permissions.remove(*Permission.objects.filter(content_type__app_label=APP, codename__in=codigos))


class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('delegaciones_app', '0030_evaluacion3_modelo'),
    ]

    operations = [
        migrations.RunPython(crear_territorios, quitar_territorios),
        migrations.RunPython(asignar_permisos, quitar_permisos),
    ]
