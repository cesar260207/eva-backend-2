import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delegaciones_app', '0004_compromiso_eje'),
    ]

    operations = [
        migrations.CreateModel(
            name='MedicionDelegacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cumplimiento', models.DecimalField(decimal_places=2, max_digits=5)),
                ('meta', models.DecimalField(decimal_places=2, max_digits=5)),
                ('fecha_datos', models.DateField()),
                ('estado_reportado', models.CharField(choices=[('verde', 'Verde'), ('amarillo', 'Amarillo'), ('rojo', 'Rojo')], max_length=12)),
                ('observacion', models.TextField(blank=True)),
                ('delegacion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='mediciones', to='delegaciones_app.delegacion')),
            ],
            options={
                'ordering': ['delegacion__nombre', '-fecha_datos'],
            },
        ),
        migrations.AddConstraint(
            model_name='mediciondelegacion',
            constraint=models.UniqueConstraint(fields=('delegacion', 'fecha_datos'), name='medicion_delegacion_fecha_unica'),
        ),
    ]
