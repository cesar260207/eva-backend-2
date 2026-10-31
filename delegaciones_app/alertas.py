"""Alertas (RF-037): vencimientos, evidencias pendientes, ausencia de registros y avance bajo el umbral.

Cada alerta identifica su motivo, el responsable, la fecha y un enlace al elemento afectado. Solo se calculan
sobre lo que el usuario ya puede ver, así que no revelan nada fuera de su ámbito.
"""
from datetime import timedelta

from django.conf import settings
from django.db.models import Max, Min
from django.urls import reverse
from django.utils import timezone

from .medicion import periodo_vigente, resultados_por_delegacion
from .models import Actividad, Funcionario
from .permisos import ADMINISTRADOR, COORDINADOR, DELEGADO, VERIFICADOR, funcionario_de, puede_ver_todo, tiene_rol
from .views import _actividades_autorizadas, _compromisos_autorizados

ORDEN_NIVEL = {'danger': 0, 'warning': 1}


def _alerta(tipo, etiqueta, nivel, motivo, responsable, fecha, url):
    return {'tipo': tipo, 'etiqueta': etiqueta, 'nivel': nivel, 'motivo': motivo, 'responsable': responsable, 'fecha': fecha, 'url': url}


def _plural(cantidad, singular, plural):
    return f'{cantidad} {singular if abs(cantidad) == 1 else plural}'


def alertas_de_vencimiento(user, hoy):
    """Compromisos vencidos o próximos a vencer dentro de los días de alerta (RF-019)."""
    alertas = []
    for compromiso in _compromisos_autorizados(user).exclude(estado='realizado'):
        url = f"{reverse('agenda')}?q={compromiso.folio}"
        if compromiso.vencido:
            motivo = f'Tarea {compromiso.folio} vencida hace {_plural(-compromiso.dias_para_vencer, "día", "días")}'
            nivel = 'danger'
        elif compromiso.proximo_a_vencer:
            cuando = 'vence hoy' if compromiso.dias_para_vencer == 0 else f'vence en {_plural(compromiso.dias_para_vencer, "día", "días")}'
            motivo, nivel = f'Tarea {compromiso.folio}: {cuando}', 'warning'
        else:
            continue
        alertas.append(_alerta('vencimiento', 'Vencimiento', nivel, motivo, compromiso.funcionario_responsable.nombre, compromiso.fecha_comprometida, url))
    return alertas


def alertas_de_evidencias_pendientes(user, hoy):
    """Actividades con evidencias esperando revisión; solo las ve quien puede revisarlas."""
    if not tiene_rol(user, ADMINISTRADOR, COORDINADOR, DELEGADO, VERIFICADOR):
        return []
    pendientes = (
        _actividades_autorizadas(user).filter(evidencias__estado_revision='pendiente')
        .annotate(desde=Min('evidencias__fecha_carga')).distinct()
    )
    alertas = []
    for actividad in pendientes:
        fecha = timezone.localtime(actividad.desde).date()
        espera = (hoy - fecha).days
        motivo = f'Evidencia de {actividad.codigo_verificador} pendiente de revisión desde hace {_plural(espera, "día", "días")}'
        alertas.append(_alerta(
            'evidencia', 'Evidencia pendiente', 'warning' if espera < 3 else 'danger', motivo,
            actividad.funcionario_autor.nombre, fecha, reverse('actividad_detalle', args=[actividad.codigo_verificador]),
        ))
    return alertas


def _funcionarios_a_vigilar(user):
    """Funcionarios con metas en un período abierto que el usuario puede supervisar."""
    funcionarios = Funcionario.objects.filter(estado=True, metas__item__periodo__estado='abierto').select_related('delegacion').distinct()
    if puede_ver_todo(user):
        return funcionarios
    propio = funcionario_de(user)
    if propio is None:
        return funcionarios.none()
    if tiene_rol(user, DELEGADO) and propio.delegacion_id:
        return funcionarios.filter(delegacion_id=propio.delegacion_id)
    return funcionarios.filter(pk=propio.pk)


def alertas_de_ausencia_de_registros(user, hoy):
    """Funcionarios con metas abiertas que no registran actividades hace más de ALERTA_DIAS_SIN_REGISTRO días."""
    limite = settings.ALERTA_DIAS_SIN_REGISTRO
    ultimos = dict(Actividad.objects.order_by().values_list('funcionario_autor').annotate(ultimo=Max('creada')))
    alertas = []
    for funcionario in _funcionarios_a_vigilar(user):
        ultimo = timezone.localtime(ultimos[funcionario.pk]).date() if funcionario.pk in ultimos else None
        if ultimo is None:
            motivo, fecha = f'{funcionario.nombre} aún no registra actividades', None
        elif (hoy - ultimo).days > limite:
            motivo, fecha = f'{funcionario.nombre} lleva {_plural((hoy - ultimo).days, "día", "días")} sin registrar actividades', ultimo
        else:
            continue
        alertas.append(_alerta('sin_registro', 'Sin registros', 'warning', motivo, funcionario.nombre, fecha, f"{reverse('informe')}?tipo=reciente"))
    return alertas


def alertas_de_avance_bajo(user, hoy):
    """Delegaciones cuyo cumplimiento está en rojo: no llega al 60 % de lo esperado al día (RN-008)."""
    periodo = periodo_vigente()
    if periodo is None:
        return []
    propio = funcionario_de(user)
    resultados = resultados_por_delegacion(periodo)
    if not puede_ver_todo(user):
        nombre = propio.delegacion.nombre if propio and propio.delegacion_id else None
        resultados = [fila for fila in resultados if fila['nombre'] == nombre]
    esperado = periodo.porcentaje_esperado(hoy)
    return [
        _alerta(
            'avance_bajo', 'Avance bajo el umbral', 'danger',
            f'Cumplimiento de {fila["cumplimiento"]} % frente a {esperado} % esperado al día en {periodo.nombre}',
            f'Delegación {fila["nombre"]}', hoy, f"{reverse('dashboard')}?periodo={periodo.pk}&q={fila['nombre']}",
        )
        for fila in resultados if fila['estado'] == 'Rojo'
    ]


def alertas_de(user, hoy=None):
    """Todas las alertas del usuario, las más graves primero y, dentro de cada nivel, por fecha."""
    hoy = hoy or timezone.localdate()
    alertas = [
        *alertas_de_vencimiento(user, hoy), *alertas_de_evidencias_pendientes(user, hoy),
        *alertas_de_ausencia_de_registros(user, hoy), *alertas_de_avance_bajo(user, hoy),
    ]
    return sorted(alertas, key=lambda alerta: (ORDEN_NIVEL[alerta['nivel']], alerta['fecha'] is None, alerta['fecha'] or hoy))
