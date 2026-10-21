"""Utilidades de auditoría y su consulta de solo lectura (HU-30, CU-30, RF-036, RNF-008)."""
from datetime import date, datetime, time, timedelta

from django import forms
from django.db.models import Q
from django.utils import timezone
from django.views.generic import ListView

from .models import Auditoria
from .permisos import ADMINISTRADOR, RolRequeridoMixin


def plano(valor):
    """Valor apto para guardar en la auditoría."""
    if hasattr(valor, 'all'):
        return [str(elemento) for elemento in valor.all()]
    if valor is None or isinstance(valor, (bool, int, float, str)):
        return valor
    return str(valor)


def valor_inicial(form, campo):
    """Valor del campo antes de editar; las claves foráneas se muestran con su nombre y no con su número."""
    campo_form = form.fields[campo]
    valor = form.get_initial_for_field(campo_form, campo)
    if isinstance(campo_form, forms.ModelChoiceField) and not isinstance(campo_form, forms.ModelMultipleChoiceField) and valor is not None:
        valor = campo_form.queryset.model.objects.filter(pk=valor).first()
    return valor


def cambios_de_formulario(form, ignorar=(), editando=None):
    """(valores anteriores, valores nuevos) de los campos que cambiaron en un formulario.

    Debe llamarse antes de guardar. Al crear no hay valores anteriores. `ignorar` excluye
    campos que no deben quedar en la auditoría, como las contraseñas.
    """
    if editando is None:
        editando = form.instance.pk is not None
    campos = [campo for campo in form.changed_data if campo not in ignorar]
    anterior = {campo: plano(valor_inicial(form, campo)) for campo in campos} if editando else None
    nuevo = {campo: plano(form.cleaned_data.get(campo)) for campo in campos}
    return anterior, nuevo


def _fecha(texto):
    try:
        return date.fromisoformat(texto)
    except ValueError:
        return None


class AuditoriaConsulta(RolRequeridoMixin, ListView):
    """Consulta con filtros del historial de operaciones críticas. Es de solo lectura: no ofrece
    ninguna acción para modificar o eliminar registros (HU-30, escenario 2)."""

    roles_permitidos = (ADMINISTRADOR,)
    template_name = 'delegaciones_app/crud/auditoria.html'
    context_object_name = 'eventos'
    paginate_by = 50

    def get_queryset(self):
        eventos = Auditoria.objects.select_related('funcionario', 'usuario_maestro').order_by('-fecha', '-pk')
        consulta = self.request.GET
        texto = consulta.get('q', '').strip()
        if texto:
            eventos = eventos.filter(
                Q(identificador_registro__icontains=texto) | Q(funcionario__nombre__icontains=texto)
                | Q(usuario_maestro__nombre__icontains=texto) | Q(valor_nuevo__icontains=texto)
            )
        if consulta.get('evento'):
            eventos = eventos.filter(evento=consulta['evento'])
        if consulta.get('entidad'):
            eventos = eventos.filter(entidad=consulta['entidad'])
        desde, hasta = _fecha(consulta.get('desde', '')), _fecha(consulta.get('hasta', ''))
        # Rango de instantes en hora de Chile; evita __date, que en MySQL exige tablas de zonas horarias.
        if desde:
            eventos = eventos.filter(fecha__gte=timezone.make_aware(datetime.combine(desde, time.min)))
        if hasta:
            eventos = eventos.filter(fecha__lt=timezone.make_aware(datetime.combine(hasta + timedelta(days=1), time.min)))
        return eventos

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        consulta = self.request.GET.copy()
        consulta.pop('page', None)
        contexto.update(
            filtros=self.request.GET,
            eventos_disponibles=Auditoria.objects.order_by().values_list('evento', flat=True).distinct().order_by('evento'),
            entidades_disponibles=Auditoria.objects.order_by().values_list('entidad', flat=True).distinct().order_by('entidad'),
            consulta_sin_pagina=consulta.urlencode(),
        )
        return contexto
