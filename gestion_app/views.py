from django.shortcuts import render
from django.utils import timezone

from delegaciones_app.models import MetaMedicion


def _color_porcentaje(cumplimiento):
    if cumplimiento >= 80:
        return 'Verde', 'success'
    if cumplimiento >= 65:
        return 'Amarillo', 'warning'
    return 'Rojo', 'danger'


def _datos_medicion():
    """Cumplimiento por delegación calculado en vivo desde la base de datos
    (modelo MetaMedicion + actividades aprobadas), sin depender de archivos JSON."""
    metas = list(MetaMedicion.objects.select_related('delegacion').filter(activa=True))
    hoy = timezone.localdate()
    resultado = []
    for meta in metas:
        cumplimiento = round(meta.cumplimiento, 2)
        estado, estado_class = _color_porcentaje(cumplimiento)
        resultado.append({
            'nombre': meta.delegacion.nombre,
            'cumplimiento': cumplimiento,
            'meta': meta.objetivo,
            'ultimos_datos': meta.periodo_termino,
            'estado': estado,
            'estado_class': estado_class,
            'dias_desde_registro': (hoy - meta.periodo_termino).days,
            'observacion': f'{meta.nombre}: {meta.avance_calculado} actividades aprobadas.',
        })
    return resultado


def dashboard(request):
    return render(request, 'gestion_app/dashboard.html', {'delegaciones': _datos_medicion()})


def semaforo(request):
    return render(request, 'gestion_app/semaforo.html', {'delegaciones': _datos_medicion()})


def resumen(request):
    delegaciones = _datos_medicion()

    total = 0
    for item in delegaciones:
        total += item.get('cumplimiento', 0)
    promedio = round(total / len(delegaciones), 2) if delegaciones else 0
    mejor = max(delegaciones, key=lambda x: x.get('cumplimiento', 0), default={})
    critico = min(delegaciones, key=lambda x: x.get('cumplimiento', 0), default={})

    return render(request, 'gestion_app/resumen.html', {
        'promedio': promedio,
        'mejor': mejor,
        'critico': critico,
        'delegaciones': delegaciones,
    })
