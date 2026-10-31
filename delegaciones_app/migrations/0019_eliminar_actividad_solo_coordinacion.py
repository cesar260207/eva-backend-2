"""Eliminar actividades es una operación crítica: la hacen la coordinación y la administración.

Hasta ahora quien registró una actividad podía eliminarla mientras no estuviera aprobada. Desde esta
versión eliminar exige el permiso delete_actividad. El Administrador ya lo tiene (la 0015 le dio todos los
permisos de la aplicación); esta migración se lo agrega al Coordinador. Delegado y Funcionario no lo
tienen: si se equivocan, corrigen con «Modificar actividad».

Cambia una fila de auth_group_permissions; no toca datos de las tablas propias. La reversa la quita.
"""
from django.contrib.auth.management import create_permissions
from django.db import migrations

APP = 'delegaciones_app'
PERMISO = 'delete_actividad'


def _grupo_y_permiso(apps):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    return Group.objects.filter(name='Coordinador').first(), Permission.objects.get(content_type__app_label=APP, codename=PERMISO)


def dar_permiso(apps, schema_editor):
    # Como en la 0015 y la 0018: en una base nueva los permisos se crean después de migrar.
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None
    coordinador, permiso = _grupo_y_permiso(apps)
    if coordinador:
        coordinador.permissions.add(permiso)


def quitar_permiso(apps, schema_editor):
    coordinador, permiso = _grupo_y_permiso(apps)
    if coordinador:
        coordinador.permissions.remove(permiso)


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('delegaciones_app', '0018_perfiles_por_jerarquia'),
    ]

    operations = [
        migrations.RunPython(dar_permiso, quitar_permiso),
    ]
