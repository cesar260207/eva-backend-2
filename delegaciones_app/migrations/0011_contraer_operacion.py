# Fase «contraer» del patrón ampliar, migrar, contraer (1 de 3): operación.
# Elimina los campos antiguos de Actividad, Evidencia, Compromiso e HistorialCompromiso y vuelve
# obligatorios los del diseño. Los datos ya se copiaron en 0010_migrar_datos.
#
# fecha_hora -> fecha y autor_funcionario -> autor se declaran con RenameField: si se dejaran como
# «borrar un campo y modificar otro» (lo que propone makemigrations), se perderían las fechas y los autores.
#
# No hay vuelta atrás segura sobre datos reales: el plan de despliegue es restaurar el respaldo.

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models
from django.db.models import Q

# (modelo, campo, también revisar texto vacío)
OBLIGATORIOS = [
    ('Actividad', 'codigo_verificador', True), ('Actividad', 'funcionario_autor', False), ('Actividad', 'item', False),
    ('Actividad', 'fecha_hora', False), ('Actividad', 'solicitud_problema', False),
    ('Evidencia', 'codigo_evidencia', True), ('Evidencia', 'funcionario_autor', False),
    ('Evidencia', 'archivo_vinculo', False), ('Evidencia', 'fecha_carga', False),
    ('Compromiso', 'funcionario_responsable', False), ('Compromiso', 'origen', False),
    ('HistorialCompromiso', 'autor_funcionario', False),
    ('Auditoria', 'evento', False), ('Auditoria', 'identificador_registro', False),
]


def verificar_antes_de_contraer(apps, schema_editor):
    """Avisa con claridad si algún campo que pasará a ser obligatorio quedó vacío, en vez de fallar con un error de la base."""
    problemas = []
    for modelo, campo, revisar_texto in OBLIGATORIOS:
        filtro = Q(**{f'{campo}__isnull': True})
        if revisar_texto:
            filtro |= Q(**{campo: ''})
        total = apps.get_model('delegaciones_app', modelo).objects.filter(filtro).count()
        if total:
            problemas.append(f'{modelo}.{campo}: {total} fila(s) vacías')
    if problemas:
        raise RuntimeError('No se puede contraer el esquema; revisa la migración de datos (0010). ' + '; '.join(problemas))


class Migration(migrations.Migration):

    dependencies = [
        ('delegaciones_app', '0010_migrar_datos'),
    ]

    operations = [
        migrations.RunPython(verificar_antes_de_contraer, migrations.RunPython.noop),

        # Actividad
        migrations.RemoveField(model_name='actividad', name='codigo'),
        migrations.RemoveField(model_name='actividad', name='funcionario'),
        migrations.RemoveField(model_name='actividad', name='fecha'),
        migrations.RemoveField(model_name='actividad', name='tipo_atencion'),
        migrations.RemoveField(model_name='actividad', name='descripcion'),
        migrations.RemoveField(model_name='actividad', name='item_medicion'),
        migrations.RemoveField(model_name='actividad', name='contacto'),
        migrations.RemoveField(model_name='actividad', name='telefono'),
        migrations.RenameField(model_name='actividad', old_name='fecha_hora', new_name='fecha'),
        migrations.AlterField(
            model_name='actividad',
            name='codigo_verificador',
            field=models.CharField(editable=False, max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='actividad',
            name='funcionario_autor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='actividades', to='delegaciones_app.funcionario'),
        ),
        migrations.AlterField(
            model_name='actividad',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='actividades', to='delegaciones_app.itemmedible'),
        ),
        migrations.AlterField(model_name='actividad', name='fecha', field=models.DateTimeField()),
        migrations.AlterField(model_name='actividad', name='solicitud_problema', field=models.TextField()),
        migrations.AlterModelTable(name='actividad', table='actividad'),

        # Evidencia
        migrations.RemoveField(model_name='evidencia', name='archivo'),
        migrations.RemoveField(model_name='evidencia', name='comentario'),
        migrations.RemoveField(model_name='evidencia', name='aprobada'),
        migrations.RemoveField(model_name='evidencia', name='revisada_por'),
        migrations.RemoveField(model_name='evidencia', name='creada'),
        migrations.AlterField(
            model_name='evidencia',
            name='codigo_evidencia',
            field=models.CharField(editable=False, max_length=60, unique=True),
        ),
        migrations.AlterField(
            model_name='evidencia',
            name='funcionario_autor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='evidencias', to='delegaciones_app.funcionario'),
        ),
        migrations.AlterField(
            model_name='evidencia',
            name='archivo_vinculo',
            field=models.FileField(max_length=255, upload_to='evidencias/%Y/%m/', validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png', 'pdf'])]),
        ),
        migrations.AlterField(model_name='evidencia', name='fecha_carga', field=models.DateTimeField(default=django.utils.timezone.now)),
        migrations.AlterModelTable(name='evidencia', table='evidencia'),

        # Compromiso
        migrations.RemoveField(model_name='compromiso', name='responsable'),
        migrations.AlterField(
            model_name='compromiso',
            name='funcionario_responsable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='compromisos', to='delegaciones_app.funcionario'),
        ),
        migrations.AlterField(
            model_name='compromiso',
            name='origen',
            field=models.CharField(choices=[('interno', 'Interno'), ('externo', 'Externo')], max_length=255),
        ),
        migrations.AlterModelTable(name='compromiso', table='compromiso'),

        # HistorialCompromiso
        migrations.RemoveField(model_name='historialcompromiso', name='autor'),
        migrations.RenameField(model_name='historialcompromiso', old_name='autor_funcionario', new_name='autor'),
        migrations.AlterField(
            model_name='historialcompromiso',
            name='autor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='historial_compromisos', to='delegaciones_app.funcionario'),
        ),
        migrations.AlterField(model_name='historialcompromiso', name='observacion', field=models.TextField(blank=True, null=True)),
        migrations.AlterModelTable(name='historialcompromiso', table='historial_compromiso'),
    ]
