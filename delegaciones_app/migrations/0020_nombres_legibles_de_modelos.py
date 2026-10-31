"""Nombres legibles de cinco modelos (actividades, roles asignados, mediciones de delegación, períodos y
registros de auditoría). Django los usa en los mensajes de datos relacionados de los mantenedores y en la
página de perfiles, que antes mostraban «actividads» o «funcionario rols». Solo cambia textos: no hay SQL."""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('delegaciones_app', '0019_eliminar_actividad_solo_coordinacion'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='actividad',
            options={'ordering': ['-fecha', '-creada'], 'verbose_name': 'actividad', 'verbose_name_plural': 'actividades'},
        ),
        migrations.AlterModelOptions(
            name='auditoria',
            options={'verbose_name': 'registro de auditoría', 'verbose_name_plural': 'registros de auditoría'},
        ),
        migrations.AlterModelOptions(
            name='funcionariorol',
            options={'verbose_name': 'rol asignado', 'verbose_name_plural': 'roles asignados'},
        ),
        migrations.AlterModelOptions(
            name='mediciondelegacion',
            options={'ordering': ['delegacion__nombre', '-fecha_datos'], 'verbose_name': 'medición de delegación', 'verbose_name_plural': 'mediciones de delegación'},
        ),
        migrations.AlterModelOptions(
            name='periodo',
            options={'ordering': ['-fecha_inicio'], 'verbose_name': 'período', 'verbose_name_plural': 'períodos'},
        ),
    ]
