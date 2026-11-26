"""Matriz por cargos (hoja SALON de la Matriz SGR, RF-031) y resumen de los tubos (hojas TUBO y TUBO CARTAS).

En la planilla, SALON copiaba a mano celdas de cada hoja de cargo y varias apuntaban a filas equivocadas
(ver docs/MATRIZ_SGR_HALLAZGOS.md). Aquí cada fila sale de los Indicador ya calculados de cada meta, con la
misma regla para todos los cargos: cumplimiento = avance / meta (con tope) y ponderado = ponderador × cumplimiento.
"""
from decimal import Decimal

from django.db.models import Count
from django.utils import timezone

from .medicion import ficha_personal
from .models import Compromiso

# Bloques de la hoja SALON (columna A), en su mismo orden. Cada cargo cae en el primero cuyo prefijo coincide.
AREAS = (
    ('Apoyo administrativo', ('Apoyo administrativo',)),
    ('Territorial OO.CC.', ('Territorial',)),
    ('DISERCO', ('Coordinador DISERCO',)),
    ('Gestión social', ('Gestor social',)),
    ('Planificación y control', ('Planificación', 'Planificacion')),
    ('Seguridad', ('Gestor de seguridad',)),
)
OTRAS = 'Otros cargos'


def area_de(cargo):
    nombre = str(cargo)
    for area, prefijos in AREAS:
        if nombre.startswith(prefijos):
            return area
    return OTRAS


def calendario(periodo, hoy=None):
    """Recuadro de fechas de SALON: inicio, cierre, días totales, transcurridos y al cierre, y lo esperado al día."""
    hoy = hoy or timezone.localdate()
    restantes = periodo.calcular_dias_restantes(hoy)
    return {
        'inicio': periodo.fecha_inicio, 'termino': periodo.fecha_termino, 'total': periodo.dias_computables,
        'transcurridos': periodo.dias_computables - restantes, 'restantes': restantes,
        'esperado': periodo.porcentaje_esperado(hoy),
    }


def matriz_por_cargos(periodo, funcionarios):
    """Bloques de SALON con una ficha por funcionario: ítems, ponderador, meta, avance, % y ponderado, y su total."""
    if periodo is None:
        return []
    funcionarios = (
        funcionarios.filter(estado=True, metas__item__periodo=periodo).select_related('cargo', 'delegacion')
        .distinct().order_by('delegacion__nombre', 'cargo__nombre', 'nombre')
    )
    bloques = {area: [] for area, _ in AREAS}
    for funcionario in funcionarios:
        ficha = ficha_personal(funcionario, periodo)
        bloques.setdefault(area_de(funcionario.cargo), []).append({
            'funcionario': funcionario,
            'filas': ficha['filas'],
            'ponderador_total': sum((fila['ponderador'] for fila in ficha['filas']), Decimal('0')),
            'total': ficha['cumplimiento_total'],
            'estado': ficha['estado_total'],
            'estado_class': ficha['estado_total_class'],
            'diferencia': ficha['diferencia_total'],
        })
    return [{'area': area, 'personas': personas} for area, personas in bloques.items() if personas]


def resumen_de_tubos(compromisos, periodo=None):
    """Por delegación y tubo: tareas por estado y % realizado (columnas R a V de las hojas TUBO y TUBO CARTAS)."""
    if periodo is not None:
        compromisos = compromisos.filter(fecha_ingreso__gte=periodo.fecha_inicio, fecha_ingreso__lte=periodo.fecha_termino)
    conteos = compromisos.values('delegacion__nombre', 'tipo', 'estado').annotate(total=Count('pk')).order_by('delegacion__nombre', 'tipo')
    filas = {}
    for fila in conteos:
        clave = (fila['delegacion__nombre'], fila['tipo'])
        resumen = filas.setdefault(clave, {
            'delegacion': fila['delegacion__nombre'], 'tubo': dict(Compromiso.TIPOS)[fila['tipo']],
            **{estado: 0 for estado, _ in Compromiso.ESTADOS}, 'total': 0,
        })
        resumen[fila['estado']] = fila['total']
        resumen['total'] += fila['total']
    for resumen in filas.values():
        resumen['realizado_pct'] = (Decimal(resumen['realizado']) * 100 / resumen['total']).quantize(Decimal('0.01'))
        pendientes = resumen['ingresado'] + resumen['pendiente']
        resumen['pendiente_pct'] = (Decimal(pendientes) * 100 / resumen['total']).quantize(Decimal('0.01'))
    return list(filas.values())


def filas_para_exportar(bloques):
    """Columnas y filas planas de la matriz por cargos, para Excel o CSV."""
    columnas = ['Área', 'Delegación', 'Funcionario', 'Cargo', 'Ítem', 'Ponderador (%)', 'Meta', 'Avance', 'Cumplimiento (%)', 'Ponderado']
    filas = []
    for bloque in bloques:
        for persona in bloque['personas']:
            funcionario = persona['funcionario']
            base = [bloque['area'], str(funcionario.delegacion or 'Alcance global'), funcionario.nombre, str(funcionario.cargo)]
            for fila in persona['filas']:
                filas.append(base + [fila['item'], fila['ponderador'], fila['objetivo'], fila['avance'], fila['cumplimiento'], fila['ponderacion']])
            filas.append(base + ['TOTAL PONDERADO', persona['ponderador_total'], '', '', '', persona['total']])
    return columnas, filas

