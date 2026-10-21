# Fase «contraer» del patrón ampliar, migrar, contraer (2 de 3): organización y acceso.
# Auditoria y Delegacion dejan solo los campos del diseño y desaparece PerfilUsuario, que
# reemplazan Funcionario, Rol y FuncionarioRol (los datos se copiaron en 0010_migrar_datos).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delegaciones_app', '0011_contraer_operacion'),
    ]

    operations = [
        # Auditoria
        migrations.RemoveField(model_name='auditoria', name='usuario'),
        migrations.RemoveField(model_name='auditoria', name='accion'),
        migrations.RemoveField(model_name='auditoria', name='identificador'),
        migrations.RemoveField(model_name='auditoria', name='detalle'),
        migrations.AlterField(model_name='auditoria', name='evento', field=models.CharField(max_length=255)),
        migrations.AlterField(model_name='auditoria', name='identificador_registro', field=models.CharField(max_length=255)),
        migrations.AlterModelTable(name='auditoria', table='auditoria'),

        # Delegacion: territorio -> ambito y activa -> estado ya se copiaron; el énfasis se conserva (ajuste 8).
        migrations.RemoveField(model_name='delegacion', name='activa'),
        migrations.RemoveField(model_name='delegacion', name='territorio'),
        migrations.AlterField(model_name='delegacion', name='enfasis', field=models.TextField(blank=True, null=True)),
        migrations.AlterModelTable(name='delegacion', table='delegacion'),

        migrations.DeleteModel(name='PerfilUsuario'),
    ]
