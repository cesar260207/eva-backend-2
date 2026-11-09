import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from delegaciones_app.models import Cargo, ItemMedible, ParametroVersionado, Periodo


class Command(BaseCommand):
    help = 'Carga cargos e ítems de la Matriz SGR desde un JSON versionado.'

    def add_arguments(self, parser):
        parser.add_argument('archivo', type=Path)
        parser.add_argument('--periodo', required=True, help='Nombre del período de destino.')

    def handle(self, *args, **options):
        archivo, nombre_periodo = options['archivo'], options['periodo']
        periodo = Periodo.objects.filter(nombre=nombre_periodo).first()
        if not periodo:
            raise CommandError(f'No existe el período «{nombre_periodo}».')
        try:
            datos = json.loads(archivo.read_text(encoding='utf-8'))
        except (OSError, ValueError) as error:
            raise CommandError(f'No se pudo leer la matriz: {error}') from error
        filas = datos.get('cargos', datos) if isinstance(datos, dict) else datos
        if not isinstance(filas, list):
            raise CommandError('La matriz debe contener una lista de cargos.')
        total_items = 0
        for fila in filas:
            cargo, _ = Cargo.objects.get_or_create(nombre=str(fila['nombre']).strip(), defaults={'vigencia': True})
            for item in fila.get('items', []):
                ItemMedible.objects.update_or_create(
                    cargo=cargo, periodo=periodo, nombre=str(item['nombre']).strip(),
                    defaults={
                        'servicio': str(item.get('servicio') or '').strip(),
                        'ponderacion': item.get('ponderacion', 0),
                        'tipo_calculo': item.get('tipo_calculo', 'actividades'),
                    },
                )
                total_items += 1
        ParametroVersionado.objects.update_or_create(
            periodo=periodo, clave='maximo_cumplimiento',
            defaults={'valor': '120', 'descripcion': 'Tope definido por la regla nueva de octubre 2026.'},
        )
        self.stdout.write(self.style.SUCCESS(f'Matriz cargada: {len(filas)} cargos y {total_items} ítems.'))
