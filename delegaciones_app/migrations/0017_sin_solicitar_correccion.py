"""La revisión queda en aprobar o rechazar: se elimina el estado «correccion» («Requiere corrección»).

Cada fila guardada con ese estado pasa a «rechazada» en las tres tablas (actividad, evidencia y
validacion). La observación que escribió el revisor no se toca: sigue siendo el motivo del rechazo, y
quien registró la actividad la corrige y la vuelve a enviar, como con cualquier rechazo.

La reversa no hace nada: tras la conversión no se distingue qué rechazo fue antes una corrección.
"""
from django.db import migrations, models


def correccion_a_rechazada(apps, schema_editor):
    apps.get_model('delegaciones_app', 'Actividad').objects.filter(estado='correccion').update(estado='rechazada')
    apps.get_model('delegaciones_app', 'Evidencia').objects.filter(estado_revision='correccion').update(estado_revision='rechazada')
    apps.get_model('delegaciones_app', 'Validacion').objects.filter(decision='correccion').update(decision='rechazada')


class Migration(migrations.Migration):

    dependencies = [
        ('delegaciones_app', '0016_textos_tubo_de_trabajo'),
    ]

    operations = [
        migrations.RunPython(correccion_a_rechazada, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='actividad',
            name='estado',
            field=models.CharField(choices=[('borrador', 'Borrador'), ('pendiente', 'Pendiente de revisión'), ('aprobada', 'Aprobada'), ('rechazada', 'Rechazada')], default='pendiente', max_length=20),
        ),
        migrations.AlterField(
            model_name='evidencia',
            name='estado_revision',
            field=models.CharField(choices=[('pendiente', 'Pendiente de revisión'), ('aprobada', 'Aprobada'), ('rechazada', 'Rechazada')], default='pendiente', max_length=20),
        ),
        migrations.AlterField(
            model_name='validacion',
            name='decision',
            field=models.CharField(choices=[('aprobada', 'Aprobada'), ('rechazada', 'Rechazada')], max_length=20),
        ),
    ]
