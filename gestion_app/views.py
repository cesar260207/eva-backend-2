from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from delegaciones_app import medicion
from delegaciones_app.medicion import periodo_vigente, periodos_con_indicadores, promedio_general, resultados_por_delegacion
from delegaciones_app.models import MedicionDelegacion
from delegaciones_app.permisos import funcionario_de, roles_de


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
    return render(request, 'gestion_app/ficha.html', contexto)

