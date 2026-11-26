"""Datos del dashboard con gráficos (Evaluación 3): avance, cumplimiento, estado de compromisos, carga de trabajo y tendencia.

Este módulo solo agrupa y calcula geometría; los gráficos se dibujan en la plantilla con HTML y SVG, sin bibliotecas
externas, para que funcionen sin conexión y se lean también como tabla (cada gráfico trae su tabla de datos).
"""
from collections import OrderedDict
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.db.models import Count
from django.utils import timezone


ESTADOS_TAREA = [('ingresado', 'Ingresadas', 1), ('pendiente', 'Pendientes', 2), ('proceso', 'En proceso', 3), ('realizado', 'Realizadas', 4)]
# Carga de trabajo: actividades por estado (aprobadas, en revisión, devueltas para corregir).
ESTADOS_CARGA = [('aprobada', 'Aprobadas', 1), ('pendiente', 'En revisión', 2), ('devueltas', 'Rechazadas o con antecedentes pedidos', 3)]
SEMANAS_MAXIMAS = 26


def _porcentaje(parte, total):
    return (Decimal(parte) * 100 / Decimal(total)).quantize(Decimal('0.1')) if total else Decimal('0')


def _segmentos(conteos, definicion):
    total = sum(conteos.get(clave, 0) for clave, _, _ in definicion)
    return total, [
        {'clave': clave, 'etiqueta': etiqueta, 'serie': serie, 'valor': conteos.get(clave, 0), 'ancho': _porcentaje(conteos.get(clave, 0), total)}
        for clave, etiqueta, serie in definicion
    ]


def estado_de_compromisos(compromisos):
    """Una fila por delegación con sus tareas por estado (barra apilada al 100 %) y las vencidas."""
    filas = OrderedDict()
    hoy = timezone.localdate()
    for fila in compromisos.values('delegacion__nombre', 'estado').annotate(total=Count('pk')).order_by('delegacion__nombre'):
        filas.setdefault(fila['delegacion__nombre'], {})[fila['estado']] = fila['total']
    vencidas = dict(
        compromisos.exclude(estado='realizado').filter(fecha_comprometida__lt=hoy)
        .values_list('delegacion__nombre').annotate(total=Count('pk')).order_by()
    )
    resultado = []
    for nombre, conteos in filas.items():
        total, segmentos = _segmentos(conteos, ESTADOS_TAREA)
        resultado.append({'nombre': nombre, 'total': total, 'segmentos': segmentos, 'vencidas': vencidas.get(nombre, 0),
                          'pct_realizado': _porcentaje(conteos.get('realizado', 0), total)})
    return resultado


def carga_de_trabajo(actividades, compromisos):
    """Por funcionario: actividades del rango por estado y tareas abiertas a su cargo (barra apilada en escala común)."""
    por_funcionario = OrderedDict()
    for fila in actividades.values('funcionario_autor_id', 'funcionario_autor__nombre', 'estado').annotate(total=Count('pk')).order_by('funcionario_autor__nombre'):
        clave = 'devueltas' if fila['estado'] in ('rechazada', 'antecedentes') else fila['estado']
        datos = por_funcionario.setdefault(fila['funcionario_autor_id'], {'nombre': fila['funcionario_autor__nombre'], 'conteos': {}})
        datos['conteos'][clave] = datos['conteos'].get(clave, 0) + fila['total']
    abiertas = dict(
        compromisos.exclude(estado='realizado').values_list('funcionario_responsable_id').annotate(total=Count('pk')).order_by()
    )
    for funcionario_id, total in abiertas.items():
        nombre = compromisos.filter(funcionario_responsable_id=funcionario_id).values_list('funcionario_responsable__nombre', flat=True).first()
        por_funcionario.setdefault(funcionario_id, {'nombre': nombre, 'conteos': {}})
    filas = []
    for funcionario_id, datos in por_funcionario.items():
        total, segmentos = _segmentos(datos['conteos'], ESTADOS_CARGA)
        filas.append({'nombre': datos['nombre'], 'total': total, 'segmentos': segmentos, 'tareas_abiertas': abiertas.get(funcionario_id, 0)})
    filas.sort(key=lambda fila: (-fila['total'], fila['nombre'] or ''))
    maximo = max((fila['total'] for fila in filas), default=0)
    for fila in filas:
        # Escala común: el largo de la barra compara la carga entre funcionarios.
        fila['largo'] = _porcentaje(fila['total'], maximo)
        for segmento in fila['segmentos']:
            segmento['ancho'] = _porcentaje(segmento['valor'], fila['total'])
    return filas


def _lunes(dia):
    return dia - timedelta(days=dia.weekday())


def tendencia_semanal(actividades, desde, hasta):
    """Actividades registradas y aprobadas por semana (lunes a domingo) en el rango, con la geometría del gráfico de líneas."""
    inicio = _lunes(max(desde, hasta - timedelta(weeks=SEMANAS_MAXIMAS)))
    semanas = []
    lunes = inicio
    while lunes <= hasta:
        semanas.append(lunes)
        lunes += timedelta(days=7)
    if not semanas:
        return None
    desde_dt = timezone.make_aware(datetime.combine(inicio, time.min))
    hasta_dt = timezone.make_aware(datetime.combine(hasta + timedelta(days=1), time.min))
    registradas = {semana: 0 for semana in semanas}
    aprobadas = {semana: 0 for semana in semanas}
    for fecha, estado in actividades.filter(fecha__gte=desde_dt, fecha__lt=hasta_dt).values_list('fecha', 'estado'):
        semana = _lunes(timezone.localtime(fecha).date())
        if semana in registradas:
            registradas[semana] += 1
            if estado == 'aprobada':
                aprobadas[semana] += 1
    ancho, alto, izquierda, derecha, arriba, abajo = 640, 220, 40, 16, 16, 32
    maximo = max([*registradas.values(), 1])
    tope = maximo if maximo <= 5 else ((maximo + 4) // 5) * 5
    paso = (ancho - izquierda - derecha) / max(len(semanas) - 1, 1)

    def punto(indice, valor):
        return round(izquierda + indice * paso, 1), round(arriba + (alto - arriba - abajo) * (1 - valor / tope), 1)

    series = []
    for numero, (nombre, datos) in enumerate((('Registradas', registradas), ('Aprobadas', aprobadas)), start=1):
        puntos = [{'x': x, 'y': y, 'valor': datos[semana], 'semana': semana} for indice, semana in enumerate(semanas) for x, y in [punto(indice, datos[semana])]]
        series.append({'nombre': nombre, 'serie': numero, 'puntos': puntos,
                       'trazo': ' '.join(f'{p["x"]},{p["y"]}' for p in puntos), 'ultimo': puntos[-1],
                       'rotulo_y': max(puntos[-1]['y'] - 10, 10)})
    marcas_y = [{'valor': valor, 'y': punto(0, valor)[1]} for valor in sorted({0, tope // 2, tope})]
    cada = max(1, len(semanas) // 6)
    marcas_x = [{'texto': semana.strftime('%d-%m'), 'x': punto(indice, 0)[0]} for indice, semana in enumerate(semanas) if indice % cada == 0]
    filas = [{'semana': semana, 'registradas': registradas[semana], 'aprobadas': aprobadas[semana]} for semana in semanas]
    return {'ancho': ancho, 'alto': alto, 'izquierda': izquierda, 'derecha_x': ancho - derecha, 'base_y': alto - abajo,
            'series': series, 'marcas_y': marcas_y, 'marcas_x': marcas_x, 'filas': filas,
            'total_registradas': sum(registradas.values()), 'total_aprobadas': sum(aprobadas.values())}


def rango_de_fechas(datos, periodo):
    """Rango del filtro: el elegido o, sin elección, el del período (y sin período, las últimas 12 semanas)."""
    def leer(valor):
        try:
            return date.fromisoformat(valor)
        except (TypeError, ValueError):
            return None
    hoy = timezone.localdate()
    desde, hasta = leer(datos.get('desde')), leer(datos.get('hasta'))
    if periodo:
        desde = desde or periodo.fecha_inicio
        hasta = hasta or min(periodo.fecha_termino, max(hoy, periodo.fecha_inicio))
    desde = desde or hoy - timedelta(weeks=12)
    hasta = hasta or hoy
    if hasta < desde:
        desde, hasta = hasta, desde
    return desde, hasta


def filtro_compromisos(compromisos, delegacion=None, funcionario=None):
    if delegacion:
        compromisos = compromisos.filter(delegacion=delegacion)
    if funcionario:
        compromisos = compromisos.filter(funcionario_responsable=funcionario)
    return compromisos


def filtro_actividades(actividades, desde, hasta, delegacion=None, funcionario=None):
    actividades = actividades.filter(
        fecha__gte=timezone.make_aware(datetime.combine(desde, time.min)),
        fecha__lt=timezone.make_aware(datetime.combine(hasta + timedelta(days=1), time.min)),
    )
    if delegacion:
        actividades = actividades.filter(delegacion=delegacion)
    if funcionario:
        actividades = actividades.filter(funcionario_autor=funcionario)
    return actividades


def compromisos_vencidos(compromisos):
    return compromisos.exclude(estado='realizado').filter(fecha_comprometida__lt=timezone.localdate()).count()

