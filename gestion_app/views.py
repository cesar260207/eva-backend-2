from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from delegaciones_app.medicion import periodo_vigente, periodos_con_indicadores, promedio_general, resultados_por_delegacion
from delegaciones_app.models import MedicionDelegacion


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
