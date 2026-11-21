import json
import re
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

# Hoja de la matriz del municipio y nombre del cargo. La fila 1 de cada hoja trae además el alias de la
# persona que ocupa el cargo: el nombre del cargo sale de esta tabla para no copiar nunca ese alias.
HOJAS_DE_CARGO = {
    'AP ADM.': 'Apoyo administrativo',
    'COOR DISERCO': 'Coordinador DISERCO',
    'T OC1': 'Territorial OO.CC. 1',
    'T OC 2': 'Territorial OO.CC. 2',
    'T OC 3': 'Territorial OO.CC. 3',
    'T OC 4': 'Territorial OO.CC. 4',
    'G SOC 1': 'Gestor social 1',
    'G SOC2': 'Gestor social 2',
    'G SOC3': 'Gestor social 3',
    'G SOC4': 'Gestor social 4',
    'G SOC5': 'Gestor social 5',
    'PLAN y CON': 'Planificación y control',
    'GES SEG': 'Gestor de seguridad',
}
SIGLAS = ('DISERCO', 'OO.CC.', 'OOCC', 'JJVV')
FIN_DE_ITEMS = ('CUMPLIMIENTO', 'FELICITACIONES', 'RECLAMOS', 'GESTION OPERATIVA')


def _texto(valor):
    return re.sub(r'\s+', ' ', str(valor)).strip() if valor not in (None, '') else ''


def _numero(valor):
    try:
        return Decimal(str(valor)) if valor not in (None, '') else None
    except ArithmeticError:
        return None


def _nombre_de_item(texto):
    """«ATENCION DE USUARIO TELEFONO» pasa a «Atencion de usuario telefono», conservando las siglas."""
    nombre = texto.capitalize()
    for sigla in SIGLAS:
        nombre = re.sub(re.escape(sigla), sigla, nombre, flags=re.IGNORECASE)
    return nombre


def leer_hoja(filas, cargo):
    """Ítems, ponderación (en %), meta trimestral, felicitación y reclamo de una hoja de cargo."""
    encabezado = next((i for i, fila in enumerate(filas[:6]) if any(_texto(v).upper() == 'PONDERADOR' for v in fila)), None)
    if encabezado is None:
        raise ValueError(f'La hoja de «{cargo}» no tiene la columna PONDERADOR.')
    titulos = [_texto(v).upper() for v in filas[encabezado]]
    col_ponderador = titulos.index('PONDERADOR')
    col_meta = next((i for i, titulo in enumerate(titulos) if titulo.startswith('META TRIMESTRE')), None)

    items, felicitacion, reclamo, en_items = [], None, None, True
    for fila in filas[encabezado + 1:]:
        textos = [_texto(v) for v in fila[:col_ponderador]]
        etiqueta = next((t for t in textos if t.upper().startswith(FIN_DE_ITEMS)), '')
        ponderador = _numero(fila[col_ponderador]) if col_ponderador < len(fila) else None
        if etiqueta.upper().startswith('FELICITACIONES'):
            felicitacion = ponderador
        elif etiqueta.upper().startswith('RECLAMOS'):
            reclamo = ponderador
            break
        if etiqueta or (ponderador is not None and ponderador > 1):
            en_items = False
        nombre = next((t for t in reversed(textos) if t), '')
        if not en_items or not nombre or ponderador is None or ponderador <= 0:
            continue
        meta = _numero(fila[col_meta]) if col_meta is not None and col_meta < len(fila) else None
        items.append({
            'nombre': _nombre_de_item(nombre),
            'ponderacion': float((ponderador * 100).quantize(Decimal('0.01'))),
            'meta_trimestre': float(meta) if meta is not None else None,
            'tipo_calculo': 'tubo' if 'TUBO' in nombre.upper() else 'actividades',
        })
    return {
        'nombre': cargo,
        'items': items,
        'felicitacion': float(felicitacion * 100) if felicitacion is not None else None,
        'reclamo': float(reclamo * 100) if reclamo is not None else None,
    }


def leer_matriz(libro):
    """Cargos de las hojas conocidas y las advertencias para revisar con el municipio."""
    hojas = {hoja.title.strip(): hoja for hoja in libro.worksheets}
    cargos, advertencias = [], []
    for hoja, cargo in HOJAS_DE_CARGO.items():
        if hoja not in hojas:
            advertencias.append(f'Falta la hoja «{hoja}» ({cargo}).')
            continue
        datos = leer_hoja([list(fila) for fila in hojas[hoja].iter_rows(max_row=40, values_only=True)], cargo)
        total = sum(Decimal(str(item['ponderacion'])) for item in datos['items'])
        if total != 100:
            advertencias.append(f'«{cargo}»: las ponderaciones suman {total.normalize():f} %, no 100 %.')
        cargos.append(datos)
    reclamos = sorted({cargo['reclamo'] for cargo in cargos if cargo['reclamo'] is not None})
    if len(reclamos) > 1:
        advertencias.append('El reclamo no vale lo mismo en todas las hojas: ' + ', '.join(f'{valor:g} %' for valor in reclamos) + '.')
    return cargos, advertencias


class Command(BaseCommand):
    help = 'Lee la Matriz SGR del municipio (Excel) y genera el JSON de cargos e ítems, sin nombres de personas.'

    def add_arguments(self, parser):
        parser.add_argument('excel', type=Path)
        parser.add_argument('--salida', type=Path, default=Path('data/matriz_cargos.json'))

    def handle(self, *args, **options):
        from openpyxl import load_workbook

        try:
            libro = load_workbook(Path(options['excel']), read_only=True, data_only=True)
            cargos, advertencias = leer_matriz(libro)
        except (OSError, ValueError, KeyError) as error:
            raise CommandError(f'No se pudo leer la matriz: {error}') from error
        datos = {'fuente': 'Matriz SGR trimestral del municipio', 'cargos': cargos, 'advertencias': advertencias}
        # call_command no aplica type=Path a las opciones que recibe por nombre.
        salida = Path(options['salida'])
        salida.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        for advertencia in advertencias:
            self.stdout.write(self.style.WARNING(advertencia))
        total = sum(len(cargo['items']) for cargo in cargos)
        self.stdout.write(self.style.SUCCESS(f'{len(cargos)} cargos y {total} ítems escritos en {salida}.'))
