"""Utilidades de auditoría y su consulta de solo lectura (HU-30, CU-30, RF-036, RNF-008)."""
import json
from datetime import date, datetime, time, timedelta

from django import forms
from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q
from django.utils import timezone
from django.utils.text import capfirst
from django.views.generic import ListView

from .models import Auditoria
from .permisos import PermisoRequeridoMixin

# La auditoría guarda los valores como JSON para no perder nada; la consulta los muestra como texto legible.
EVENTOS = {
    'crear': 'Creación', 'editar': 'Modificación', 'eliminar': 'Eliminación', 'borrado': 'Eliminación',
    'cambio_estado': 'Cambio de estado', 'cargar_evidencia': 'Carga de evidencia', 'exportar': 'Exportación',
    'aprobar': 'Aprobación', 'rechazar': 'Rechazo', 'anular_aprobacion': 'Anulación de aprobación',
    'informar_ajuste': 'Ajuste informado', 'aplicar_ajuste': 'Ajuste aplicado', 'rechazar_ajuste': 'Ajuste rechazado',
    'asignar_delegado': 'Asignación de delegado', 'restablecer_contrasena': 'Restablecimiento de contraseña',
    'acceso_denegado': 'Acceso denegado', 'iniciar_periodo': 'Inicio de período', 'cerrar_periodo': 'Cierre de período',
    'reabrir_periodo': 'Reapertura de período',
}
# Claves que no son campos de un modelo (las guardan las vistas).
CLAVES = {
    'metodo': 'Método', 'ruta': 'Ruta', 'motivo': 'Motivo', 'medio': 'Medio', 'filtros': 'Filtros',
    'filas': 'Filas exportadas', 'campos': 'Campos modificados', 'evidencia': 'Evidencia',
}
TILDES = {
    'periodo': 'período', 'item': 'ítem', 'delegacion': 'delegación', 'descripcion': 'descripción',
    'ponderacion': 'ponderación', 'telefono': 'teléfono', 'accion': 'acción', 'observacion': 'observación',
    'codigo': 'código', 'catalogo': 'catálogo', 'organizacion': 'organización', 'numero': 'número',
    'termino': 'término', 'constitucion': 'constitución', 'inscripcion': 'inscripción', 'direccion': 'dirección',
    'calculo': 'cálculo', 'version': 'versión', 'area': 'área', 'gestion': 'gestión', 'ambito': 'ámbito',
    'enfasis': 'énfasis', 'juridica': 'jurídica', 'decision': 'decisión', 'dias': 'días', 'vinculo': 'vínculo',
    'minimo': 'mínimo', 'revision': 'revisión', 'informacion': 'información',
}


def _con_tildes(texto):
    return ' '.join(TILDES.get(palabra, palabra) for palabra in str(texto).replace('_', ' ').split())


def _modelo(entidad):
    try:
        return apps.get_model('delegaciones_app', entidad)
    except LookupError:
        return None


def etiqueta_evento(evento):
    return EVENTOS.get(evento, capfirst(_con_tildes(evento)))


def etiqueta_entidad(entidad):
    modelo = _modelo(entidad)
    return capfirst(_con_tildes(modelo._meta.verbose_name)) if modelo else capfirst(_con_tildes(entidad))


def _campo(modelo, clave):
    try:
        return modelo._meta.get_field(clave) if modelo else None
    except FieldDoesNotExist:
        return None


def _etiqueta_campo(modelo, clave):
    if clave in CLAVES:
        return CLAVES[clave]
    campo = _campo(modelo, clave)
    return capfirst(_con_tildes(campo.verbose_name if campo else clave))


def _valor(modelo, clave, valor):
    if valor is None or valor == '':
        return '(vacío)'
    if isinstance(valor, bool):
        return 'Sí' if valor else 'No'
    if isinstance(valor, list):
        if clave == 'campos':
            return ', '.join(_etiqueta_campo(modelo, campo) for campo in valor) or '(ninguno)'
        return ', '.join(_valor(modelo, clave, elemento) for elemento in valor) or '(ninguno)'
    if isinstance(valor, dict):
        return '; '.join(f'{_etiqueta_campo(modelo, k)}: {_valor(modelo, k, v)}' for k, v in valor.items())
    campo = _campo(modelo, clave)
    if campo is not None and campo.choices:
        return str(dict(campo.flatchoices).get(valor, valor))
    texto = str(valor)
    if len(texto) == 10 and texto[4] == '-' and texto[7] == '-':  # fecha ISO 2026-10-01 → 01-10-2026
        fecha = _fecha(texto)
        if fecha:
            return fecha.strftime('%d-%m-%Y')
    return texto


def detalle_legible(texto, entidad):
    """Valores de un evento como [(campo, valor)] legibles: «Valor objetivo», «20.00»; sin llaves ni comillas."""
    if not texto:
        return []
    try:
        datos = json.loads(texto)
    except (TypeError, ValueError):
        return [('', texto)]
    modelo = _modelo(entidad)
    if not isinstance(datos, dict):
        return [('', _valor(modelo, '', datos))]
    return [(_etiqueta_campo(modelo, clave), _valor(modelo, clave, valor)) for clave, valor in datos.items()]


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


class AuditoriaConsulta(PermisoRequeridoMixin, ListView):
    """Consulta con filtros del historial de operaciones críticas. Es de solo lectura: no ofrece
    ninguna acción para modificar o eliminar registros (HU-30, escenario 2)."""

    permiso_requerido = 'delegaciones_app.view_auditoria'
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
        for evento in contexto['eventos']:
            evento.evento_legible = etiqueta_evento(evento.evento)
            evento.entidad_legible = etiqueta_entidad(evento.entidad)
            evento.detalle_anterior = detalle_legible(evento.valor_anterior, evento.entidad)
            evento.detalle_nuevo = detalle_legible(evento.valor_nuevo, evento.entidad)
        eventos = Auditoria.objects.order_by().values_list('evento', flat=True).distinct()
        entidades = Auditoria.objects.order_by().values_list('entidad', flat=True).distinct()
        contexto.update(
            filtros=self.request.GET,
            eventos_disponibles=sorted(((e, etiqueta_evento(e)) for e in eventos), key=lambda par: par[1]),
            entidades_disponibles=sorted(((e, etiqueta_entidad(e)) for e in entidades), key=lambda par: par[1]),
            consulta_sin_pagina=consulta.urlencode(),
        )
        return contexto
