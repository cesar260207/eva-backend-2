"""Alcance de cada usuario en el módulo de beneficiarios.

- Administración y Coordinación (puede_ver_todo) ven todas las inscripciones e inscriben a nombre de cualquier unidad.
- El resto solo trabaja con su(s) unidad(es): la de su delegación o aquellas a las que fue asignado (DIDECO, etc.).
Son datos de menores y del Registro Social de Hogares: nadie ve las inscripciones de otra unidad.
"""
from delegaciones_app.permisos import funcionario_de, puede_ver_todo

from .models import Inscripcion, UnidadMunicipal


def _enlazar_delegacion(delegacion):
    """Unidad de una delegación. Las delegaciones se crean después de migrar (seed_demo), así que el enlace se hace
    la primera vez que se necesita, buscando la unidad «Delegación <nombre>» que dejó la migración 0002."""
    unidad = UnidadMunicipal.objects.filter(delegacion=delegacion).first()
    if unidad:
        return unidad
    unidad = UnidadMunicipal.objects.filter(nombre__iexact=f'Delegación {delegacion.nombre}', delegacion__isnull=True).first()
    if unidad:
        unidad.delegacion = delegacion
        unidad.save(update_fields=['delegacion'])
    return unidad


def unidades_de(user):
    """Unidades a nombre de las cuales el usuario puede inscribir y cuyas inscripciones puede ver."""
    activas = UnidadMunicipal.objects.filter(activa=True)
    if puede_ver_todo(user):
        return activas
    funcionario = funcionario_de(user)
    if funcionario is None:
        return activas.none()
    ids = set(activas.filter(funcionarios=funcionario).values_list('pk', flat=True))
    if funcionario.delegacion_id:
        unidad = _enlazar_delegacion(funcionario.delegacion)
        if unidad and unidad.activa:
            ids.add(unidad.pk)
    return activas.filter(pk__in=ids)


def inscripciones_visibles(user):
    inscripciones = Inscripcion.objects.select_related('evento', 'unidad', 'organizacion', 'registrado_por')
    if puede_ver_todo(user):
        return inscripciones
    return inscripciones.filter(unidad__in=unidades_de(user))
