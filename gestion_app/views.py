from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from delegaciones_app import medicion
from delegaciones_app.alertas import alertas_de
from delegaciones_app.informes import (
    TIPOS_INFORME, filas_de_actividad_reciente, filas_de_actividades, filas_de_compromisos, filas_de_cumplimiento, filas_de_resumen,
    filtrar_actividades, filtrar_compromisos, respuesta_csv,
)
from delegaciones_app.medicion import periodo_vigente, periodos_con_indicadores, promedio_general, resultados_por_delegacion
from delegaciones_app.models import Actividad, Auditoria, Compromiso, Delegacion, MedicionDelegacion, Periodo
from delegaciones_app.permisos import funcionario_de, roles_de
from delegaciones_app.views import _actividades_autorizadas, _compromisos_autorizados


def _contexto_medicion(request):
    """Datos comunes del dashboard, el semáforo y el resumen: período elegido y resultados por delegación."""
    periodo = periodo_vigente(request.GET.get('periodo'))
    texto = request.GET.get('q', '').strip()
    return {
        'periodo': periodo,
        'periodos': periodos_con_indicadores(),
        'query': texto,
        'delegaciones': resultados_por_delegacion(periodo, texto),
        'hoy': timezone.localdate(),
        'esperado': periodo.porcentaje_esperado() if periodo else None,
        'tope': periodo.obtener_parametro('maximo_cumplimiento', '150') if periodo else None,
    }


@login_required
def dashboard(request):
    return render(request, 'gestion_app/dashboard.html', _contexto_medicion(request))


@login_required
def semaforo(request):
    return render(request, 'gestion_app/semaforo.html', _contexto_medicion(request))


@login_required
def resumen(request):
    contexto = _contexto_medicion(request)
    delegaciones, periodo = contexto['delegaciones'], contexto['periodo']
    promedio = promedio_general(delegaciones)
    contexto.update({
        'promedio': promedio,
        'mejor': max(delegaciones, key=lambda fila: fila['cumplimiento'], default={}),
        'critico': min(delegaciones, key=lambda fila: fila['cumplimiento'], default={}),
        'alcanza_umbral': periodo.alcanza_umbral(promedio) if periodo else None,
        'mediciones_historicas': MedicionDelegacion.objects.select_related('delegacion')[:12],
    })
    return render(request, 'gestion_app/resumen.html', contexto)


@login_required
def ficha_personal(request):
    """Ficha personal del funcionario: metas, avance, cumplimiento, semáforo, evidencias y compromisos (CU-06, RF-008)."""
    funcionario = funcionario_de(request.user)
    if funcionario is None:
        messages.error(request, 'Tu cuenta no tiene un funcionario asociado, así que no tiene ficha personal.')
        return redirect('inicio')
    periodo = medicion.periodo_de_ficha(funcionario, request.GET.get('periodo'))
    contexto = {
        'funcionario': funcionario,
        'roles': sorted(roles_de(request.user)),
        'periodo': periodo,
        'periodos': medicion.periodos_de(funcionario),
        'hoy': timezone.localdate(),
        'compromisos': medicion.resumen_de_compromisos(funcionario),
    }
    if periodo:
        contexto.update(medicion.ficha_personal(funcionario, periodo))
        contexto['evidencias'] = medicion.resumen_de_evidencias(funcionario, periodo)
        propias = medicion.actividad_reciente(Actividad.objects.filter(funcionario_autor=funcionario), periodo)
        contexto['reciente'] = propias[0] if propias else None
    return render(request, 'gestion_app/ficha.html', contexto)


@login_required
def informe(request):
    """Informe filtrable de actividades, compromisos o cumplimiento, en pantalla, para imprimir o en CSV (RF-033).

    Solo incluye lo que el usuario ya puede ver en las listas; cada exportación queda en la auditoría.
    """
    tipo = request.GET.get('tipo') if request.GET.get('tipo') in dict(TIPOS_INFORME) else 'actividades'
    formato = request.GET.get('formato')
    periodo = periodo_vigente(request.GET.get('periodo')) if tipo in ('cumplimiento', 'reciente') else None
    if tipo == 'actividades':
        columnas, filas = filas_de_actividades(filtrar_actividades(_actividades_autorizadas(request.user), request.GET))
    elif tipo == 'compromisos':
        columnas, filas = filas_de_compromisos(filtrar_compromisos(_compromisos_autorizados(request.user), request.GET))
    elif tipo == 'resumen':
        columnas, filas = filas_de_resumen(filtrar_compromisos(_compromisos_autorizados(request.user), request.GET))
    elif tipo == 'reciente':
        actividades = filtrar_actividades(_actividades_autorizadas(request.user), {**request.GET.dict(), 'periodo': ''})
        columnas, filas = filas_de_actividad_reciente(medicion.actividad_reciente(actividades, periodo))
    else:
        resultados = resultados_por_delegacion(periodo, '')
        if request.GET.get('delegacion', '').isdigit():
            elegida = Delegacion.objects.filter(pk=int(request.GET['delegacion'])).first()
            resultados = [fila for fila in resultados if elegida and fila['nombre'] == elegida.nombre]
        columnas, filas = filas_de_cumplimiento(resultados, periodo.porcentaje_esperado() if periodo else '')
    if formato == 'csv':
        Auditoria.registrar_evento(request.user, 'exportar', 'Informe', tipo, None, {'filtros': request.GET.urlencode(), 'filas': len(filas)})
        return respuesta_csv(f'informe_{tipo}_{timezone.localdate():%Y%m%d}.csv', columnas, filas)
    parametros = request.GET.copy()
    parametros.pop('formato', None)
    return render(request, 'gestion_app/informe.html', {
        'tipo': tipo, 'nombre_tipo': dict(TIPOS_INFORME)[tipo], 'tipos': TIPOS_INFORME, 'columnas': columnas, 'filas': filas, 'filtros': request.GET,
        'imprimir': formato == 'imprimir', 'consulta': parametros.urlencode(), 'hoy': timezone.localdate(),
        'delegaciones_filtro': Delegacion.objects.filter(estado=True), 'periodos_filtro': Periodo.objects.order_by('-fecha_inicio'),
        'estados_filtro': Actividad.ESTADOS if tipo in ('actividades', 'reciente') else Compromiso.ESTADOS,
        'periodo_informe': periodo,
    })


@login_required
def alertas(request):
    """Alertas del usuario: vencimientos, evidencias pendientes, ausencia de registros y avance bajo el umbral (RF-037)."""
    lista = alertas_de(request.user)
    return render(request, 'gestion_app/alertas.html', {
        'alertas': lista,
        'peligro': sum(1 for alerta in lista if alerta['nivel'] == 'danger'),
        'advertencia': sum(1 for alerta in lista if alerta['nivel'] == 'warning'),
        'dias_sin_registro': settings.ALERTA_DIAS_SIN_REGISTRO,
        'dias_alerta': settings.COMPROMISO_DIAS_ALERTA,
    })

