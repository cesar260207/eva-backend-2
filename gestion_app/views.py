from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.shortcuts import redirect, render
from django.utils import timezone

from delegaciones_app import medicion
from delegaciones_app.alertas import alertas_de
from delegaciones_app.informes import (
    TIPOS_INFORME, filas_de_actividad_reciente, filas_de_actividades, filas_de_compromisos, filas_de_cumplimiento, filas_de_resumen,
    filtrar_actividades, filtrar_compromisos, respuesta_csv,
)
from delegaciones_app.medicion import periodo_vigente, periodos_con_indicadores, promedio_general, resultados_por_delegacion
from delegaciones_app.crud import mantenedores_visibles
from delegaciones_app.models import Actividad, Auditoria, Compromiso, Delegacion, Evidencia, Funcionario, MedicionDelegacion, Periodo
from delegaciones_app.permisos import (
    DELEGADO, PERFIL_ADMINISTRADOR, PERFIL_COORDINADOR, PERFIL_DELEGADO, PERFILES, delegacion_propia, funcionario_de, perfil_de, puede_revisar,
    roles_de,
)
from delegaciones_app.views import _delegaciones_visibles
from delegaciones_app.views import _actividades_autorizadas, _compromisos_autorizados


def _solo_su_delegacion(user, resultados):
    """Resultados por delegación que el usuario puede ver: un delegado ve solo los de su delegación."""
    propia = delegacion_propia(user)
    return [fila for fila in resultados if fila['nombre'] == propia.nombre] if propia else resultados


def _contexto_medicion(request):
    """Datos comunes del dashboard, el semáforo y el resumen: período elegido y resultados por delegación."""
    periodo = periodo_vigente(request.GET.get('periodo'))
    texto = request.GET.get('q', '').strip()
    return {
        'periodo': periodo,
        'periodos': periodos_con_indicadores(),
        'query': texto,
        'delegacion_propia': delegacion_propia(request.user),
        'delegaciones': _solo_su_delegacion(request.user, resultados_por_delegacion(periodo, texto)),
        'hoy': timezone.localdate(),
        'esperado': periodo.porcentaje_esperado() if periodo else None,
        'tope': periodo.obtener_parametro('maximo_cumplimiento', '150') if periodo else None,
    }


def _resumen_operacional(user):
    """Cifras de actividades y compromisos dentro del ámbito del usuario, comunes a los tres paneles."""
    actividades = _actividades_autorizadas(user)
    abiertos = list(_compromisos_autorizados(user).exclude(estado='realizado'))
    return {
        'actividades_total': actividades.count(),
        'actividades_pendientes': actividades.filter(estado='pendiente').count(),
        'actividades_aprobadas': actividades.filter(estado='aprobada').count(),
        'compromisos_abiertos': len(abiertos),
        'compromisos_vencidos': sum(1 for c in abiertos if c.vencido),
        'compromisos_por_vencer': sum(1 for c in abiertos if not c.vencido and c.proximo_a_vencer),
    }


@login_required
def panel(request):
    """Panel de inicio según el perfil autenticado (Administrador, Coordinador, Delegado o Funcionario).

    Cada perfil ve un panel distinto: el administrador, la visión global con todos los mantenedores,
    las transacciones y la gestión de usuarios; el coordinador, los mantenedores y transacciones que
    sus permisos autorizan, todas las delegaciones con su delegado y la información operacional; el
    delegado, su delegación (lo que debe revisar, su tubo de trabajo y sus métricas); el funcionario, sus funciones.
    """
    user = request.user
    perfil = perfil_de(user)
    contexto = {
        'perfil': perfil,
        'funcionario': funcionario_de(user),
        'roles': sorted(roles_de(user)),
        'alertas': alertas_de(user)[:5],
        **_resumen_operacional(user),
    }
    if perfil in (PERFIL_ADMINISTRADOR, PERFIL_COORDINADOR):
        periodo = periodo_vigente()
        delegaciones = resultados_por_delegacion(periodo) if periodo else []
        delegados = {}
        for delegado in Funcionario.objects.filter(estado=True, roles__nombre_rol=DELEGADO, delegacion__isnull=False).select_related('delegacion').distinct():
            delegados.setdefault(delegado.delegacion.nombre, []).append(delegado.nombre)
        for fila in delegaciones:
            fila['delegados'] = ', '.join(delegados.get(fila['nombre'], []))
        contexto.update({
            'mantenedores': [m for m in mantenedores_visibles(user) if m['permitido']],
            'periodo': periodo,
            'delegaciones': delegaciones,
            'promedio': promedio_general(delegaciones),
            'evidencias_pendientes': Evidencia.objects.filter(actividad__in=_actividades_autorizadas(user), estado_revision='pendiente').count(),
        })
    if perfil == PERFIL_ADMINISTRADOR:
        contexto.update({
            'usuarios_activos': User.objects.filter(is_active=True).count(),
            'usuarios_inactivos': User.objects.filter(is_active=False).count(),
            'perfiles': [
                (grupo.name, grupo.user_set.filter(is_active=True).count())
                for grupo in sorted(Group.objects.filter(name__in=PERFILES), key=lambda g: PERFILES.index(g.name))
            ],
            'funcionarios_activos': Funcionario.objects.filter(estado=True).count(),
            'delegaciones_activas': Delegacion.objects.filter(estado=True).count(),
            'periodos_abiertos': Periodo.objects.filter(estado='abierto').count(),
            'auditoria_reciente': Auditoria.objects.select_related('funcionario', 'usuario_maestro').order_by('-pk')[:6],
        })
        plantilla = 'gestion_app/panel_administrador.html'
    elif perfil == PERFIL_COORDINADOR:
        plantilla = 'gestion_app/panel_coordinador.html'
    elif perfil == PERFIL_DELEGADO:
        propia, periodo = delegacion_propia(user), periodo_vigente()
        contexto.update({
            'delegacion_propia': propia,
            'periodo': periodo,
            'resultado_delegacion': _solo_su_delegacion(user, resultados_por_delegacion(periodo))[:1] if periodo and propia else [],
            # Lo que espera su revisión: actividades de su delegación con evidencias pendientes, salvo las propias.
            'por_revisar': list(
                _actividades_autorizadas(user).filter(evidencias__estado_revision='pendiente')
                .exclude(funcionario_autor=contexto['funcionario']).distinct()[:8]
            ),
            'tareas_abiertas': list(_compromisos_autorizados(user).exclude(estado='realizado').order_by('fecha_comprometida')[:8]),
        })
        plantilla = 'gestion_app/panel_delegado.html'
    else:
        propio = contexto['funcionario']
        periodo = periodo_vigente()
        contexto.update({
            'delegacion_propia': delegacion_propia(user),
            'resultado_delegacion': _solo_su_delegacion(user, resultados_por_delegacion(periodo))[:1] if periodo and delegacion_propia(user) else [],
            'mis_actividades': Actividad.objects.filter(funcionario_autor=propio).select_related('delegacion').order_by('-fecha')[:5] if propio else [],
            'mis_compromisos': Compromiso.objects.filter(funcionario_responsable=propio).exclude(estado='realizado').order_by('fecha_comprometida')[:5] if propio else [],
            'puede_revisar': puede_revisar(user),
        })
        plantilla = 'gestion_app/panel_funcionario.html'
    return render(request, plantilla, contexto)


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
        'mediciones_historicas': (
            MedicionDelegacion.objects.select_related('delegacion').filter(delegacion=contexto['delegacion_propia'])
            if contexto['delegacion_propia'] else MedicionDelegacion.objects.select_related('delegacion')
        )[:12],
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
        resultados = _solo_su_delegacion(request.user, resultados_por_delegacion(periodo, ''))
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
        'delegaciones_filtro': _delegaciones_visibles(request.user), 'periodos_filtro': Periodo.objects.order_by('-fecha_inicio'),
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

