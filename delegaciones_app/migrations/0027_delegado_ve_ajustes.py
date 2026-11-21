from django.db import migrations


# Regla 8: el delegado consulta los ajustes de su delegación en el mantenedor de ajustes
# (la lista filtra por delegación). Solo agrega una fila en auth_group_permissions.
PERMISO = ('delegaciones_app', 'view_ajuste')


def _permiso_y_perfil(apps):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    perfil = Group.objects.filter(name='Delegado').first()
    permiso = Permission.objects.filter(content_type__app_label=PERMISO[0], codename=PERMISO[1]).first()
    return perfil, permiso


def agregar(apps, schema_editor):
    perfil, permiso = _permiso_y_perfil(apps)
    if perfil and permiso:
        perfil.permissions.add(permiso)


def quitar(apps, schema_editor):
    perfil, permiso = _permiso_y_perfil(apps)
    if perfil and permiso:
        perfil.permissions.remove(permiso)


class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('delegaciones_app', '0026_alter_ajuste_respaldo'),
    ]

    operations = [
        migrations.RunPython(agregar, quitar),
    ]
