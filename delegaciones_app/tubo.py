"""Ingreso opcional de actividades y gestiones sociales al Tubo de seguimiento (Evaluación 3).

Una actividad o una gestión social puede ingresar o no al Tubo. Si ingresa, se crea una tarea (Compromiso) en la
delegación de quien la registra, a su cargo, con los datos de contacto ya ingresados (campos autocompletados), y el
registro queda vinculado a esa tarea. Desde ahí la tarea sigue el flujo normal del Tubo con su historial.
"""
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Compromiso

DIAS_PLAZO_POR_DEFECTO = 14
EJE_POR_TIPO = {'actividad': 'Gestión Social', 'caso_social': 'Gestión Social'}


def _texto(valor, por_defecto):
    return (valor or '').strip() or por_defecto


def crear_tarea(*, funcionario, delegacion, solicitante, telefono, descripcion, fecha_base, plazo=None, interna=False, territorio='', rut='', vecino=None):
    """Crea la tarea del Tubo y su primer historial. La valida como cualquier otra tarea (full_clean)."""
    if delegacion is None:
        raise ValidationError('Para ingresar al Tubo, el registro necesita una delegación.')
    tarea = Compromiso(
        tipo='solicitud', delegacion=delegacion, funcionario_responsable=funcionario,
        origen='interno' if interna else 'externo',
        solicitante=_texto(solicitante, 'Sin nombre informado')[:255], solicitante_telefono=(telefono or '')[:20],
        solicitante_rut=rut or '', vecino=vecino,
        territorio=_texto(territorio, delegacion.nombre)[:255], descripcion=_texto(descripcion, 'Sin descripción'),
        fecha_ingreso=timezone.localdate(),
        fecha_comprometida=plazo or (fecha_base + timedelta(days=DIAS_PLAZO_POR_DEFECTO)),
    )
    tarea.folio = Compromiso.generar_folio('solicitud')
    tarea.full_clean()
    tarea.save()
    tarea.registrar_historial(funcionario, '', 'Ingreso al Tubo desde un registro')
    return tarea


def ingresar_actividad(actividad, funcionario, plazo=None):
    """Crea la tarea del Tubo para una actividad recién registrada y la vincula."""
    tarea = crear_tarea(
        funcionario=funcionario, delegacion=actividad.delegacion, solicitante=actividad.contacto_nombre,
        telefono=actividad.contacto_telefono, descripcion=actividad.solicitud_problema,
        fecha_base=timezone.localtime(actividad.fecha).date(), plazo=plazo, interna=actividad.gestion_interna,
        territorio=actividad.lugar,
    )
    actividad.compromiso = tarea
    actividad.save(update_fields=['compromiso', 'actualizada'])
    return tarea


def ingresar_caso_social(caso, funcionario, plazo=None):
    """Crea la tarea del Tubo para una gestión social y la vincula."""
    vecino = caso.vecino
    tarea = crear_tarea(
        funcionario=funcionario, delegacion=funcionario.delegacion, solicitante=caso.nombre_usuario, telefono=caso.telefono_usuario,
        descripcion=f'Gestión social: {caso.get_tipo_display()}{" - " + caso.subtipo if caso.subtipo else ""}. {caso.observacion}'.strip(),
        fecha_base=timezone.localdate(), plazo=plazo, rut=vecino.rut if vecino else '', vecino=vecino,
        territorio=vecino.territorio.nombre if vecino else '',
    )
    caso.compromiso = tarea
    caso.save(update_fields=['compromiso'])
    return tarea
