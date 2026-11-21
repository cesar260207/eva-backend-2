from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ('delegaciones_app', '0020_nombres_legibles_de_modelos'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organizacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('tipo', models.CharField(choices=[('junta_vecinos', 'Junta de vecinos'), ('funcional', 'Organización funcional'), ('adulto_mayor', 'Club de adulto mayor'), ('deportiva', 'Organización deportiva'), ('cultural', 'Centro de madres / cultural / juvenil'), ('comite', 'Comité de vecinos, allegados o seguridad'), ('sin_clasificar', 'Sin clasificar')], default='sin_clasificar', max_length=30)),
                ('personalidad_juridica', models.CharField(blank=True, max_length=50)),
                ('domicilio', models.CharField(blank=True, max_length=255)),
                ('territorio', models.CharField(blank=True, max_length=255)),
                ('verificada', models.BooleanField(default=False)),
                ('observaciones', models.TextField(blank=True)),
                ('activa', models.BooleanField(default=True)),
                ('delegacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='organizaciones', to='delegaciones_app.delegacion')),
            ],
            options={'ordering': ['nombre']},
        ),
        migrations.AddConstraint(
            model_name='organizacion',
            constraint=models.UniqueConstraint(fields=('nombre', 'territorio'), name='organizacion_nombre_territorio_unico'),
        ),
        migrations.AddField(
            model_name='actividad',
            name='cuenta_puntaje',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='actividad',
            name='gestion_interna',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='actividad',
            name='motivo_sin_puntaje',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='actividad',
            name='organizacion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='actividades', to='delegaciones_app.organizacion'),
        ),
        migrations.AddField(
            model_name='actividad',
            name='tipo_accion',
            field=models.CharField(choices=[('ejecucion', 'Ejecución'), ('gestion_previa', 'Gestión previa')], default='ejecucion', max_length=20),
        ),
        migrations.AddField(
            model_name='compromiso',
            name='gestion_interna',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='compromiso',
            name='organizacion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='compromisos', to='delegaciones_app.organizacion'),
        ),
        migrations.AddField(
            model_name='compromiso',
            name='solicitante_telefono',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='itemmedible',
            name='tipo_calculo',
            field=models.CharField(choices=[('actividades', 'Conteo de actividades'), ('tubo', '% del tubo realizado')], default='actividades', max_length=20),
        ),
        migrations.CreateModel(
            name='Ajuste',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('felicitacion', 'Felicitación'), ('reclamo', 'Reclamo')], max_length=20)),
                ('fecha', models.DateField(default=django.utils.timezone.localdate)),
                ('respaldo', models.FileField(blank=True, null=True, upload_to='ajustes/%Y/%m/')),
                ('observacion', models.TextField(blank=True)),
                ('estado', models.CharField(choices=[('informado', 'Informado'), ('aplicado', 'Aplicado'), ('rechazado', 'Rechazado')], default='informado', max_length=20)),
                ('aplicado_en', models.DateTimeField(blank=True, null=True)),
                ('aplicado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ajustes_aplicados', to='delegaciones_app.funcionario')),
                ('delegacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ajustes', to='delegaciones_app.delegacion')),
                ('funcionario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ajustes', to='delegaciones_app.funcionario')),
                ('informado_por', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ajustes_informados', to='delegaciones_app.funcionario')),
                ('periodo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ajustes', to='delegaciones_app.periodo')),
            ],
        ),
        migrations.CreateModel(
            name='Ausencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('licencia', 'Licencia'), ('vacaciones', 'Vacaciones'), ('administrativo', 'Administrativo'), ('compensatorio', 'Compensatorio'), ('dia_libre', 'Día libre')], max_length=20)),
                ('desde', models.DateField()),
                ('hasta', models.DateField()),
                ('observacion', models.TextField(blank=True)),
                ('funcionario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ausencias', to='delegaciones_app.funcionario')),
                ('periodo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ausencias', to='delegaciones_app.periodo')),
                ('registrada_por', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ausencias_registradas', to='delegaciones_app.funcionario')),
            ],
        ),
        migrations.CreateModel(
            name='CasoSocial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_usuario', models.CharField(max_length=255)),
                ('telefono_usuario', models.CharField(max_length=20)),
                ('etapa', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('tipo', models.CharField(choices=[('informe_social', 'Informe social'), ('subsidio_ips', 'Subsidio IPS'), ('pgu', 'PGU'), ('suf', 'SUF'), ('sap', 'SAP'), ('derivacion', 'Derivación')], max_length=30)),
                ('subtipo', models.CharField(blank=True, max_length=255)),
                ('observacion', models.TextField(blank=True)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('funcionario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='casos_sociales', to='delegaciones_app.funcionario')),
            ],
        ),
        migrations.CreateModel(
            name='Comentario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.TextField()),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('actividad', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comentarios', to='delegaciones_app.actividad')),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='comentarios', to='delegaciones_app.funcionario')),
                ('compromiso', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comentarios', to='delegaciones_app.compromiso')),
            ],
        ),
    ]
