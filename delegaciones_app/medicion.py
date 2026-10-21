"""Resultados de medición por delegación para la portada, el dashboard, el semáforo y el resumen.

Todo sale de los Indicador ya calculados (ver Indicador.generar y el comando calcular_indicadores);
aquí solo se agrupan y se presentan.
"""
from decimal import Decimal

from django.db.models import Count
from django.utils import timezone

from .models import Compromiso, Delegacion, Evidencia, Indicador, Meta, Periodo

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
    esperado = periodo.porcentaje_esperado()
    delegaciones = Delegacion.objects.filter(estado=True, funcionarios__metas__item__periodo=periodo).distinct()
    if texto:
        delegaciones = delegaciones.filter(nombre__icontains=texto)
    resultados = []
    for delegacion in delegaciones:
        indicadores = delegacion.ultimos_indicadores(periodo)
        cumplimiento = Delegacion.promedio_ponderado(indicadores)
        ultimo_calculo = max((timezone.localtime(i.fecha_calculo).date() for i in indicadores), default=None)
        if indicadores:
            codigo = periodo.calcular_semaforo(cumplimiento)
            etiqueta, clase = COLORES[codigo]
        else:
            codigo = None
            etiqueta, clase = 'Sin cálculo', 'secondary'
        resultados.append({
            'nombre': delegacion.nombre,
            'cumplimiento': cumplimiento,
            'ancho': min(cumplimiento, Decimal(100)),
            'estado': etiqueta,
            'estado_class': clase,
            # CU-17: diferencia entre lo real y lo esperado al día; una desviación significativa es ámbar o rojo (RN-008).
            'diferencia': (cumplimiento - esperado).quantize(Decimal('0.01')) if indicadores else None,
            'desviacion': codigo in ('ambar', 'rojo'),
            'ultimos_datos': ultimo_calculo,
            'dias_desde_registro': (hoy - ultimo_calculo).days if ultimo_calculo else None,
            'detalle': [f'{i.meta.item.nombre}: {_numero(i.avance)} de {_numero(i.meta.valor_objetivo)} {i.meta.unidad}' for i in indicadores],
        })
    return resultados


def promedio_general(resultados):
    if not resultados:
        return Decimal('0.00')
    return (sum(fila['cumplimiento'] for fila in resultados) / len(resultados)).quantize(Decimal('0.01'))


def periodos_de(funcionario):
    """Períodos en los que el funcionario tiene metas."""
    return Periodo.objects.filter(items__metas__funcionario=funcionario).distinct().order_by('-fecha_inicio')


def periodo_de_ficha(funcionario, periodo_id=None):
    """El período pedido si el funcionario tiene metas en él; si no, el abierto más reciente y, en su defecto, el más reciente."""
    periodos = periodos_de(funcionario)
    if periodo_id and str(periodo_id).isdigit():
        elegido = periodos.filter(pk=int(periodo_id)).first()
        if elegido:
            return elegido
    return periodos.filter(estado='abierto').first() or periodos.first()


def _formula(meta, indicador, tope):
    """Detalle verificable del cálculo de una meta (CU-07.3): meta, avance, fórmula, ponderación y resultado."""
    bruto = meta.evaluar_progreso(indicador.avance)
    return [
        f'Cumplimiento = avance / meta × 100 = {_numero(indicador.avance)} / {_numero(meta.valor_objetivo)} × 100 = {_numero(bruto)} %',
        f'Máximo computable: {_numero(tope)} %' + (f'; se aplica el tope y queda en {_numero(indicador.cumplimiento)} %' if bruto > tope else ''),
        f'Cumplimiento ponderado = ponderador × cumplimiento = {_numero(meta.ponderador)} % × {_numero(indicador.cumplimiento)} % = {_numero(indicador.ponderacion)}',
    ]


def ficha_personal(funcionario, periodo):
    """Metas del funcionario en el período con su avance, cumplimiento, semáforo y detalle (CU-06, CU-17, CU-07.3)."""
    esperado = periodo.porcentaje_esperado()
    tope = Decimal(periodo.obtener_parametro('maximo_cumplimiento', '150'))
    metas = list(Meta.objects.filter(funcionario=funcionario, item__periodo=periodo).select_related('item', 'funcionario').order_by('item__nombre'))
    ultimos = {}
    for indicador in Indicador.objects.filter(meta__in=metas, periodo=periodo).select_related('meta').order_by('fecha_calculo', 'pk'):
        ultimos[indicador.meta_id] = indicador
    filas = []
    for meta in metas:
        indicador = ultimos.get(meta.pk)
        fila = {
            'meta': meta, 'item': meta.item.nombre, 'objetivo': meta.valor_objetivo, 'unidad': meta.unidad,
            'ponderador': meta.ponderador, 'sin_calculo': indicador is None, 'esperado': esperado,
            'actividades': list(meta.actividades_que_aportan(periodo)[:20]),
        }
        if indicador is None:
            fila.update(avance=0, cumplimiento=Decimal('0.00'), ponderacion=Decimal('0.00'), estado='Sin cálculo', estado_class='secondary',
                        diferencia=None, desviacion=False, cumplida=False, formula=[])
        else:
            codigo = periodo.calcular_semaforo(indicador.cumplimiento)
            etiqueta, clase = COLORES[codigo]
            fila.update(
                avance=indicador.avance, cumplimiento=indicador.cumplimiento, ponderacion=indicador.ponderacion,
                estado=etiqueta, estado_class=clase, diferencia=(indicador.cumplimiento - esperado).quantize(Decimal('0.01')),
                desviacion=codigo in ('ambar', 'rojo'),
                # CU-06.2: la meta se destaca como cumplida cuando el avance alcanza el objetivo.
                cumplida=indicador.avance >= meta.valor_objetivo, formula=_formula(meta, indicador, tope),
            )
        filas.append(fila)
    indicadores = list(ultimos.values())
    total = Delegacion.promedio_ponderado(indicadores)
    etiqueta, clase = COLORES[periodo.calcular_semaforo(total)] if indicadores else ('Sin cálculo', 'secondary')
    return {
        'filas': filas, 'esperado': esperado, 'tope': tope, 'cumplimiento_total': total,
        'estado_total': etiqueta, 'estado_total_class': clase,
        'diferencia_total': (total - esperado).quantize(Decimal('0.01')) if indicadores else None,
    }


def resumen_de_evidencias(funcionario, periodo):
    """Cuántas evidencias del funcionario hay en cada estado de revisión, en el período."""
    conteo = {estado: 0 for estado, _ in Evidencia.ESTADOS_REVISION}
    filas = Evidencia.objects.filter(funcionario_autor=funcionario, actividad__item__periodo=periodo).values('estado_revision').annotate(total=Count('pk'))
    for fila in filas:
        conteo[fila['estado_revision']] = fila['total']
    etiquetas = dict(Evidencia.ESTADOS_REVISION)
    return [{'estado': estado, 'etiqueta': etiquetas[estado], 'total': total} for estado, total in conteo.items()]


def resumen_de_compromisos(funcionario):
    """Compromisos que el funcionario tiene como responsable, agrupados por su situación respecto del plazo."""
    compromisos = list(Compromiso.objects.filter(funcionario_responsable=funcionario))
    vencidos = sum(1 for c in compromisos if c.vencido)
    por_vencer = sum(1 for c in compromisos if c.proximo_a_vencer)
    realizados = sum(1 for c in compromisos if c.estado == 'realizado')
    return {
        'total': len(compromisos), 'vencidos': vencidos, 'por_vencer': por_vencer, 'realizados': realizados,
        'vigentes': len(compromisos) - vencidos - por_vencer - realizados,
    }

