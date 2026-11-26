"""RUT chileno: normalización y validación del dígito verificador (módulo 11).

El RUT se guarda siempre normalizado, sin puntos y con guion («12345678-5», «9876543-K»), para que la búsqueda
del Tubo por RUT encuentre el registro sin importar cómo lo escribió quien lo ingresó.
"""
import re

from django.core.exceptions import ValidationError

_CARACTERES_VALIDOS = re.compile(r'^[0-9]{1,8}[0-9K]$')


def _limpiar(valor):
    return re.sub(r'[\s.\-]', '', str(valor or '')).upper()


def digito_verificador(cuerpo):
    """Dígito verificador del cuerpo numérico de un RUT, como texto ('0' a '9' o 'K')."""
    suma, factor = 0, 2
    for digito in reversed(str(cuerpo)):
        suma += int(digito) * factor
        factor = 2 if factor == 7 else factor + 1
    resto = 11 - suma % 11
    return {11: '0', 10: 'K'}.get(resto, str(resto))


def normalizar_rut(valor):
    """«12.345.678-5» -> «12345678-5». Devuelve '' si el valor está vacío; no valida el dígito."""
    limpio = _limpiar(valor)
    if not limpio:
        return ''
    return f'{limpio[:-1]}-{limpio[-1]}'


def es_rut_valido(valor):
    limpio = _limpiar(valor)
    if not _CARACTERES_VALIDOS.match(limpio) or not limpio[:-1]:
        return False
    return digito_verificador(int(limpio[:-1])) == limpio[-1]


def validar_rut(valor):
    """Validador de Django: rechaza un RUT con formato o dígito verificador incorrecto."""
    if valor and not es_rut_valido(valor):
        raise ValidationError('El RUT no es válido: revisa los números y el dígito verificador.', code='rut_invalido')
