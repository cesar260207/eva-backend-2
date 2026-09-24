from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delegaciones_app', '0003_periodomedicion_catalogoitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='compromiso',
            name='eje',
            field=models.CharField(
                choices=[
                    ('Seguridad', 'Seguridad'),
                    ('DISERCO', 'DISERCO'),
                    ('Gestión Social', 'Gestión Social'),
                    ('Organizaciones Comunitarias', 'Organizaciones Comunitarias'),
                ],
                default='Gestión Social',
                max_length=40,
            ),
        ),
        migrations.AlterModelOptions(
            name='compromiso',
            options={'ordering': ['-fecha_comprometida', '-creado']},
        ),
    ]
