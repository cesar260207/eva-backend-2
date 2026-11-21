from django.db import migrations


def renombrar_perfil_profesional(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    antiguo = Group.objects.filter(name='Funcionario').first()
    nuevo = Group.objects.filter(name='Profesional').first()
    if antiguo and nuevo:
        for usuario in antiguo.user_set.all():
            usuario.groups.add(nuevo)
        antiguo.delete()
    elif antiguo:
        antiguo.name = 'Profesional'
        antiguo.save(update_fields=['name'])


def revertir_perfil_profesional(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    profesional = Group.objects.filter(name='Profesional').first()
    if profesional:
        profesional.name = 'Funcionario'
        profesional.save(update_fields=['name'])


class Migration(migrations.Migration):
    dependencies = [
        ('delegaciones_app', '0021_reglas_sgr'),
    ]

    operations = [
        migrations.RunPython(renombrar_perfil_profesional, revertir_perfil_profesional),
    ]
