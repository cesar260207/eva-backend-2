from django.core.management.base import BaseCommand

from delegaciones_app.models import Indicador, Meta


class Command(BaseCommand):
    help = 'Calcula un Indicador nuevo para cada Meta cuyo período no esté cerrado (RN-003 a RN-009).'

    def handle(self, *args, **options):
        creados, omitidos = 0, 0
        for meta in Meta.objects.select_related('item__periodo', 'funcionario'):
            # RN-013: los resultados de un período cerrado quedan congelados.
            if meta.item.periodo.estado == 'cerrado':
                omitidos += 1
                continue
            indicador = Indicador.generar(meta)
            creados += 1
            self.stdout.write(f'  {meta}: avance {indicador.avance}, cumplimiento {indicador.cumplimiento} %, semáforo {indicador.semaforo}')
        self.stdout.write(self.style.SUCCESS(f'Indicadores calculados: {creados}. Metas omitidas por período cerrado: {omitidos}.'))
