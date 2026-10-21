"""Resultados de medición por delegación para la portada, el dashboard, el semáforo y el resumen.

Todo sale de los Indicador ya calculados (ver Indicador.generar y el comando calcular_indicadores);
aquí solo se agrupan y se presentan.
"""
from decimal import Decimal

from django.utils import timezone

from .models import Delegacion, Periodo

# Código del semáforo (RN-008) -> etiqueta y clase de Bootstrap.
COLORES = {'verde': ('Verde', 'success'), 'ambar': ('Ámbar', 'warning'), 'rojo': ('Rojo', 'danger')}


def periodos_con_indicadores():
    return Periodo.objects.filter(indicadores__isnull=False).distinct().order_by('-fecha_inicio')


def periodo_vigente(periodo_id=None):
    """El período pedido si tiene indicadores; si no, el abierto más reciente y, en su defecto, el más reciente."""
    periodos = periodos_con_indicadores()
    if periodo_id and str(periodo_id).isdigit():
        elegido = periodos.filter(pk=int(periodo_id)).first()
        if elegido:
            return elegido
    return periodos.filter(estado='abierto').first() or periodos.first()


def _numero(valor):
    return format(Decimal(valor).normalize(), 'f')


def resultados_por_delegacion(periodo, texto=''):
    """Una fila por delegación activa con metas en el período."""
    if periodo is None:
        return []
    hoy = timezone.localdate()
    delegaciones = Delegacion.objects.filter(estado=True, funcionarios__metas__item__periodo=periodo).distinct()
    if texto:
        delegaciones = delegaciones.filter(nombre__icontains=texto)
    resultados = []
    for delegacion in delegaciones:
        indicadores = delegacion.ultimos_indicadores(periodo)
        cumplimiento = Delegacion.promedio_ponderado(indicadores)
        ultimo_calculo = max((timezone.localtime(i.fecha_calculo).date() for i in indicadores), default=None)
        if indicadores:
            etiqueta, clase = COLORES[periodo.calcular_semaforo(cumplimiento)]
        else:
            etiqueta, clase = 'Sin cálculo', 'secondary'
        resultados.append({
            'nombre': delegacion.nombre,
            'cumplimiento': cumplimiento,
            'ancho': min(cumplimiento, Decimal(100)),
            'estado': etiqueta,
            'estado_class': clase,
            'ultimos_datos': ultimo_calculo,
            'dias_desde_registro': (hoy - ultimo_calculo).days if ultimo_calculo else None,
            'detalle': [f'{i.meta.item.nombre}: {_numero(i.avance)} de {_numero(i.meta.valor_objetivo)} {i.meta.unidad}' for i in indicadores],
        })
    return resultados


def promedio_general(resultados):
    if not resultados:
        return Decimal('0.00')
    return (sum(fila['cumplimiento'] for fila in resultados) / len(resultados)).quantize(Decimal('0.01'))
