"""Importación de planillas Excel de inscripción (las que entregan las JJ.VV.).

Cada fila se valida con el mismo InscripcionForm de la inscripción manual: RUT con dígito verificador, RUT ya
inscrito en la actividad («RUT ya ingresado por <unidad>»), teléfono, folio, etc. Además se detectan RUT repetidos
dentro del mismo archivo. Las filas válidas se guardan; las demás se informan con su número de fila y el motivo.
"""
import re
import unicodedata
from dataclasses import dataclass, field

from django.db import transaction
from django.http import HttpResponse

from delegaciones_app.models import Organizacion

from .forms import InscripcionForm
from .models import Inscripcion, rut_canonico

MAX_FILAS = 2000
MAX_BYTES = 2 * 1024 * 1024

COLUMNAS_PLANTILLA = ['Nombre del menor', 'RUT', 'Rango de edad', 'Género', 'Folio RSH', 'Tramo RSH (%)',
                      'JJ.VV. o agrupación', 'Teléfono']

# Palabras clave que identifican cada columna, en orden de prioridad (el encabezado se normaliza sin tildes).
CLAVES = {
    'rut': ('rut',),
    'nombre': ('nombre',),
    'rango_edad': ('rango', 'edad'),
    'genero': ('genero', 'sexo'),
    'folio_rsh': ('folio',),
    'tramo_rsh': ('tramo', 'porcentaje', 'rsh'),
    'organizacion': ('jj', 'junta', 'agrupacion', 'organizacion'),
    'telefono': ('telefono', 'fono', 'celular', 'contacto'),
}


def _normalizar(texto):
    texto = unicodedata.normalize('NFKD', str(texto or '')).encode('ascii', 'ignore').decode()
    return re.sub(r'\s+', ' ', texto).strip().lower()


def _texto(valor):
    """Valor de celda como texto; los números enteros que Excel guarda como 912345678.0 pierden el «.0»."""
    if valor is None:
        return ''
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor).strip()


def rango_desde(valor):
    """«6-8», «6 - 8 años», 7 o «7 años» -> '6-8'. Devuelve '' si no se reconoce."""
    texto = _normalizar(_texto(valor))
    if not texto:
        return ''
    numeros = [int(n) for n in re.findall(r'\d+', texto)]
    if not numeros:
        return ''
    inicio = numeros[0]  # «6 - 8» se ubica por su inicio; una edad suelta («7»), en el rango que la contiene
    for valor_rango, desde, hasta in (('0-2', 0, 2), ('3-5', 3, 5), ('6-8', 6, 8), ('9-10', 9, 10)):
        if desde <= inicio <= hasta:
            return valor_rango
    return '11+' if inicio >= 11 else ''


def genero_desde(valor):
    texto = _normalizar(_texto(valor))
    if texto in ('m', 'masculino', 'hombre', 'h', 'nino', 'varon'):
        return 'M'
    if texto in ('f', 'femenino', 'mujer', 'nina'):
        return 'F'
    if texto.startswith('prefiero') or texto in ('n', 'no informa', 'no responde', 'sin informacion'):
        return 'N'
    if texto in ('o', 'otro', 'otra'):
        return 'O'
    return texto  # el formulario lo rechazará con «opción no válida»


def tramo_desde(valor):
    """«40%», 40, 0.4 (formato porcentaje de Excel) -> '40'."""
    if isinstance(valor, (int, float)) and 0 < valor <= 1:
        return str(round(valor * 100))
    numeros = re.findall(r'\d+', _texto(valor))
    return numeros[0] if numeros else ''


@dataclass
class ResultadoFila:
    fila: int
    nombre: str
    rut: str
    errores: list = field(default_factory=list)

    @property
    def ok(self):
        return not self.errores


@dataclass
class ResultadoImportacion:
    filas: list = field(default_factory=list)
    error_general: str = ''
    guardado: bool = False

    @property
    def validas(self):
        return sum(1 for f in self.filas if f.ok)

    @property
    def con_error(self):
        return sum(1 for f in self.filas if not f.ok)


def _ubicar_encabezado(hoja):
    """Fila del encabezado (entre las 15 primeras) y la columna de cada campo."""
    for numero, fila in enumerate(hoja.iter_rows(min_row=1, max_row=15, values_only=True), start=1):
        textos = [_normalizar(c) for c in fila]
        if any('rut' in t for t in textos) and any('nombre' in t for t in textos):
            columnas = {}
            for campo, claves in CLAVES.items():
                for indice, texto in enumerate(textos):
                    if indice in columnas.values():
                        continue
                    if any(clave in texto for clave in claves):
                        columnas[campo] = indice
                        break
            return numero, columnas
    return None, {}


def _organizacion(nombre):
    nombre = ' '.join(nombre.split())
    return Organizacion.objects.filter(activa=True, nombre__iexact=nombre).first() if nombre else None


def procesar(archivo, user, evento, unidad, organizacion=None, organizacion_otra='', solo_revisar=False):
    from openpyxl import load_workbook

    resultado = ResultadoImportacion()
    try:
        libro = load_workbook(archivo, read_only=True, data_only=True)
    except Exception:  # archivo dañado o que no es .xlsx
        resultado.error_general = 'No se pudo leer el archivo. Debe ser una planilla Excel (.xlsx).'
        return resultado
    hoja = libro.worksheets[0]
    fila_encabezado, columnas = _ubicar_encabezado(hoja)
    if not fila_encabezado:
        resultado.error_general = 'No se encontró el encabezado: la planilla debe tener al menos las columnas «Nombre» y «RUT».'
        return resultado
    faltan = [c for c in ('nombre', 'rut', 'rango_edad', 'genero', 'folio_rsh', 'tramo_rsh', 'telefono') if c not in columnas]
    if faltan:
        etiquetas = dict(zip(['nombre', 'rut', 'rango_edad', 'genero', 'folio_rsh', 'tramo_rsh', 'organizacion', 'telefono'], COLUMNAS_PLANTILLA))
        resultado.error_general = 'Faltan columnas en la planilla: ' + ', '.join(etiquetas[c] for c in faltan) + '. Usa la plantilla del sistema.'
        return resultado

    vistos = {}
    nuevas = []
    for numero, fila in enumerate(hoja.iter_rows(min_row=fila_encabezado + 1, values_only=True), start=fila_encabezado + 1):
        celda = lambda campo: fila[columnas[campo]] if campo in columnas and columnas[campo] < len(fila) else None
        if all(_texto(c) == '' for c in fila):
            continue
        if len(resultado.filas) >= MAX_FILAS:
            resultado.error_general = f'La planilla supera el máximo de {MAX_FILAS} filas; se procesaron las primeras {MAX_FILAS}.'
            break
        nombre_org = _texto(celda('organizacion'))
        org = _organizacion(nombre_org) if nombre_org else organizacion
        datos = {
            'evento': evento.pk, 'unidad': unidad.pk,
            'nombre': _texto(celda('nombre')), 'rut': _texto(celda('rut')),
            'rango_edad': rango_desde(celda('rango_edad')), 'genero': genero_desde(celda('genero')),
            'folio_rsh': _texto(celda('folio_rsh')), 'tramo_rsh': tramo_desde(celda('tramo_rsh')),
            'organizacion': org.pk if org else '',
            'organizacion_otra': '' if org else (nombre_org or organizacion_otra),
            'telefono': _texto(celda('telefono')),
        }
        item = ResultadoFila(numero, datos['nombre'], datos['rut'])
        form = InscripcionForm(datos, user=user)
        if form.is_valid():
            rut = form.cleaned_data['rut']
            item.rut = rut
            if rut in vistos:
                item.errores.append(f'RUT repetido en la planilla (ya está en la fila {vistos[rut]}).')
            else:
                vistos[rut] = numero
                nuevas.append(form)
        else:
            for campo, errores in form.errors.items():
                etiqueta = form.fields[campo].label if campo in form.fields else ''
                for error in errores:
                    item.errores.append(f'{etiqueta}: {error}' if etiqueta else error)
        resultado.filas.append(item)

    if not solo_revisar and nuevas:
        with transaction.atomic():
            for form in nuevas:
                inscripcion = form.save(commit=False)
                inscripcion.registrado_por = user
                inscripcion.correo_registro = user.email
                inscripcion.save()
        resultado.guardado = True
    return resultado


def plantilla_excel():
    """Planilla para que las JJ.VV. llenen, con listas desplegables en edad, género y tramo."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    from openpyxl.worksheet.datavalidation import DataValidation

    libro = Workbook()
    hoja = libro.active
    hoja.title = 'Inscripción'
    hoja.append(COLUMNAS_PLANTILLA)
    for celda in hoja[1]:
        celda.font = Font(bold=True, color='FFFFFF')
        celda.fill = PatternFill('solid', fgColor='8A4B2D')
    hoja.append(['Ana Pérez Soto', '12345678-5', '6 - 8 años', 'Femenino', '123456789', '40%', 'JJ.VV. Villa El Sol', '912345678'])
    for letra, ancho in zip('ABCDEFGH', (30, 14, 16, 18, 14, 14, 30, 14)):
        hoja.column_dimensions[letra].width = ancho
    listas = {
        'C': [e for _, e in Inscripcion.RANGOS_EDAD],
        'D': [e for _, e in Inscripcion.GENEROS],
        'F': [e for _, e in Inscripcion.TRAMOS_RSH],
    }
    for letra, opciones in listas.items():
        validacion = DataValidation(type='list', formula1='"' + ','.join(opciones) + '"', allow_blank=True)
        hoja.add_data_validation(validacion)
        validacion.add(f'{letra}2:{letra}{MAX_FILAS + 1}')
    for letra in ('B', 'E', 'H'):  # como texto, para no perder ceros ni el guion
        for fila in range(2, MAX_FILAS + 2):
            hoja[f'{letra}{fila}'].number_format = '@'
    respuesta = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    respuesta['Content-Disposition'] = 'attachment; filename="plantilla_inscripcion_beneficiarios.xlsx"'
    libro.save(respuesta)
    return respuesta
