from django.db import migrations, models


# Regla 9: el tipo «Emergencia» de la hoja SEMAFORO de la matriz (solo cambia las opciones del campo, ninguna
# fila) y el delegado consulta las ausencias de su equipo (una fila en auth_group_permissions).
PERMISO = ('delegaciones_app', 'view_ausencia')


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
        ('delegaciones_app', '0027_delegado_ve_ajustes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ausencia',
            name='tipo',
            field=models.CharField(choices=[
                ('licencia', 'Licencia'), ('vacaciones', 'Vacaciones'), ('administrativo', 'Administrativo'),
                ('compensatorio', 'Compensatorio'), ('dia_libre', 'Día libre'), ('emergencia', 'Emergencia'),
            ], max_length=20),
        ),
        migrations.RunPython(agregar, quitar),
    ]
