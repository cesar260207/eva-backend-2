# Fase «contraer» del patrón ampliar, migrar, contraer (3 de 3): medición.
# Desaparecen CatalogoItem, PeriodoMedicion y MetaMedicion, que reemplazan Catalogo, Periodo,
# ParametroVersionado, ItemMedible, Meta e Indicador (los datos se copiaron en 0010_migrar_datos).
# MedicionDelegacion se conserva como histórico importado (ajuste 5) y solo cambia el nombre de su tabla.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('delegaciones_app', '0012_contraer_organizacion'),
    ]

    operations = [
        migrations.DeleteModel(name='MetaMedicion'),
        migrations.DeleteModel(name='CatalogoItem'),
        migrations.DeleteModel(name='PeriodoMedicion'),
        migrations.AlterModelTable(name='mediciondelegacion', table='medicion_delegacion'),
    ]
