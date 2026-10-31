"""«Tubo de trabajo» en la interfaz: cada Compromiso se muestra como una «tarea».

Solo cambian los nombres visibles y las etiquetas de los estados (en femenino). No se ejecuta SQL:
la tabla compromiso, sus columnas y los valores guardados (por ejemplo «realizado») no cambian.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delegaciones_app', '0015_perfiles_de_acceso'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='compromiso',
            options={'ordering': ['-fecha_comprometida', '-creado'], 'verbose_name': 'tarea del tubo de trabajo', 'verbose_name_plural': 'tareas del tubo de trabajo'},
        ),
        migrations.AlterModelOptions(
            name='historialcompromiso',
            options={'verbose_name': 'historial de tarea', 'verbose_name_plural': 'historial de tareas'},
        ),
        migrations.AlterField(
            model_name='compromiso',
            name='estado',
            field=models.CharField(choices=[('ingresado', 'Ingresada'), ('pendiente', 'Pendiente'), ('proceso', 'En proceso'), ('realizado', 'Realizada')], default='ingresado', max_length=20),
        ),
    ]
