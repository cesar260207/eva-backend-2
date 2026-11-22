"""Filtros de presentación para las plantillas del SGR.

Solo cambian cómo se dibuja un formulario: no validan, no consultan la base de datos y no deciden
permisos. Django 5.2 ya agrega «aria-invalid» y «aria-describedby» a los campos con error o ayuda;
estos filtros agregan las clases de Bootstrap (incluida «is-invalid») y ordenan los campos en bloques.
"""
from django import template

register = template.Library()

TIPOS_CASILLA = ('checkbox', 'radio')


def _clase_base(widget):
    """Clase de Bootstrap que corresponde al widget cuando el formulario no la trae (por ejemplo, el ingreso)."""
    tipo = getattr(widget, 'input_type', None)
    if tipo in TIPOS_CASILLA:
        return 'form-check-input'
    if widget.__class__.__name__ in ('Select', 'SelectMultiple', 'NullBooleanSelect') or tipo == 'select':
        return 'form-select'
    return 'form-control'


@register.filter
def campo_sgr(campo, clases=''):
    """Dibuja el widget de un campo con las clases de Bootstrap, más «is-invalid» si el campo tiene errores.

    Uso: {{ form.telefono|campo_sgr }} o {{ form.password|campo_sgr:"form-control-lg" }}.
    """
    widget = campo.field.widget
    if campo.is_hidden:
        return campo.as_widget()
    lista = widget.attrs.get('class', '').split() or [_clase_base(widget)]
    lista += str(clases).split()
    if campo.errors:
        lista.append('is-invalid')
    return campo.as_widget(attrs={'class': ' '.join(dict.fromkeys(lista))})


@register.filter
def campos(form, nombres):
    """Campos visibles del formulario con esos nombres, en ese orden; omite los que el formulario no tenga.

    Uso: {% for campo in form|campos:"delegacion fecha" %}.
    """
    return [form[nombre] for nombre in str(nombres).split() if nombre in form.fields and not form[nombre].is_hidden]


@register.filter
def partes_cifra(texto):
    """Separa una cifra escrita en español para el conteo animado: '250.141' o '88,0 %'.

    Devuelve el número sin formato para «data-contar» («250141», «88.0»), la cantidad de decimales,
    el texto sin el signo de porcentaje y el sufijo. Uso: {% with c=urbano|partes_cifra %}.
    """
    texto = str(texto).strip()
    sufijo = '%' if texto.endswith('%') else ''
    numero = texto.rstrip('%').strip()
    entero, _, decimales = numero.partition(',')
    return {
        'plano': entero.replace('.', '') + ('.' + decimales if decimales else ''),
        'decimales': len(decimales),
        'texto': numero,
        'sufijo': sufijo,
    }


@register.filter
def avance(valor):
    """Porcentaje para dibujar un anillo o una barra: número con punto, entre 0 y 100.

    El cumplimiento puede pasar de 100 (tope 120 %); el dibujo se llena hasta 100 y el texto muestra el valor real.
    Uso: style="--avance: {{ fila.cumplimiento|avance }}".
    """
    try:
        numero = float(str(valor).replace(',', '.'))
    except (TypeError, ValueError):
        return '0'
    numero = min(max(numero, 0), 100)
    texto = f'{numero:.2f}'.rstrip('0').rstrip('.')
    return texto or '0'


@register.filter
def por_estado(registros, estado):
    """Registros con ese estado, en el mismo orden: arma las columnas del tablero del tubo de trabajo.
    Uso: {% with columna=compromisos|por_estado:valor %}.
    """
    return [registro for registro in registros if getattr(registro, 'estado', None) == estado]


@register.filter
def campos_restantes(form, nombres):
    """Campos visibles que no están en la lista: así ningún campo queda fuera de un formulario agrupado a mano."""
    excluidos = set(str(nombres).split())
    return [campo for campo in form.visible_fields() if campo.name not in excluidos]
