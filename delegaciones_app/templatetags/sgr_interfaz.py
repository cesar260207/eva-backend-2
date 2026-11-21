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
def campos_restantes(form, nombres):
    """Campos visibles que no están en la lista: así ningún campo queda fuera de un formulario agrupado a mano."""
    excluidos = set(str(nombres).split())
    return [campo for campo in form.visible_fields() if campo.name not in excluidos]
