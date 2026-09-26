import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delegaciones_app', '0005_mediciondelegacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='compromiso',
            name='fecha_ingreso',
            field=models.DateField(default=django.utils.timezone.localdate),
        ),
    ]
