"""Filtros e informes compartidos por las listas (actividades, agenda) y por los informes exportables (RF-032, RF-033)."""
import csv
from datetime import date, datetime, time, timedelta

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone

from .models import Actividad, Compromiso

TIPOS_INFORME = [('actividades', 'Actividades'), ('compromisos', 'Compromisos'), ('cumplimiento', 'Cumplimiento por delegación')]
PLAZOS = [('vencidos', 'Vencidos'), ('por_vencer', 'Próximos a vencer')]


def _fecha(valor):
    try:
        return date.fromisoformat(valor)
    except (TypeError, ValueError):
        return None


def _entero(valor):
    return int(valor) if valor and str(valor).isdigit() else None


def _inicio_del_dia(dia):
    return timezone.make_aware(datetime.combine(dia, time.min))


def filtrar_actividades(actividades, datos):
    """Aplica q, delegacion, estado, periodo, desde y hasta; un valor inválido se ignora."""
    texto = (datos.get('q') or '').strip()
    if texto:
        actividades = actividades.filter(Q(codigo_verificador__icontains=texto) | Q(solicitud_problema__icontains=texto) | Q(item__nombre__icontains=texto))
    if _entero(datos.get('delegacion')):
        actividades = actividades.filter(delegacion_id=int(datos['delegacion']))
    if datos.get('estado') in dict(Actividad.ESTADOS):
        actividades = actividades.filter(estado=datos['estado'])
    if _entero(datos.get('periodo')):
        actividades = actividades.filter(item__periodo_id=int(datos['periodo']))
    desde, hasta = _fecha(datos.get('desde')), _fecha(datos.get('hasta'))
    if desde:
        actividades = actividades.filter(fecha__gte=_inicio_del_dia(desde))
    if hasta:
        # Rango de instantes y no __date: en MySQL __date exige las tablas de zonas horarias.
        actividades = actividades.filter(fecha__lt=_inicio_del_dia(hasta + timedelta(days=1)))
    return actividades


def filtrar_compromisos(compromisos, datos):
    """Aplica q, delegacion, estado, plazo, periodo, desde y hasta (sobre la fecha comprometida)."""
    texto = (datos.get('q') or '').strip()
    if texto:
        compromisos = compromisos.filter(
            Q(folio__icontains=texto) | Q(descripcion__icontains=texto) | Q(solicitante__icontains=texto) | Q(delegacion__nombre__icontains=texto)
        )
    if _entero(datos.get('delegacion')):
        compromisos = compromisos.filter(delegacion_id=int(datos['delegacion']))
    if datos.get('estado') in dict(Compromiso.ESTADOS):
        compromisos = compromisos.filter(estado=datos['estado'])
    hoy = timezone.localdate()
    if datos.get('plazo') == 'vencidos':
        compromisos = compromisos.exclude(estado='realizado').filter(fecha_comprometida__lt=hoy)
    elif datos.get('plazo') == 'por_vencer':
        compromisos = compromisos.exclude(estado='realizado').filter(fecha_comprometida__gte=hoy, fecha_comprometida__lte=hoy + timedelta(days=settings.COMPROMISO_DIAS_ALERTA))
    desde, hasta = _fecha(datos.get('desde')), _fecha(datos.get('hasta'))
    if _entero(datos.get('periodo')):
        from .models import Periodo
        periodo = Periodo.objects.filter(pk=int(datos['periodo'])).first()
        if periodo:
            desde, hasta = max(filter(None, [desde, periodo.fecha_inicio])), min(filter(None, [hasta, periodo.fecha_termino]))
    if desde:
        compromisos = compromisos.filter(fecha_comprometida__gte=desde)
    if hasta:
        compromisos = compromisos.filter(fecha_comprometida__lte=hasta)
    return compromisos


def situacion_de_plazo(compromiso):
    """Etiqueta y clase Bootstrap de un compromiso según su estado y su plazo (RF-018, RF-019)."""
    if compromiso.vencido:
        return 'Vencido', 'danger'
    if compromiso.proximo_a_vencer:
        return 'Próximo a vencer', 'warning'
    return compromiso.get_estado_display(), 'success' if compromiso.estado == 'realizado' else 'warning'


def filas_de_actividades(actividades):
    """Columnas y filas planas de un informe de actividades."""
    columnas = ['Código', 'Fecha', 'Delegación', 'Ítem', 'Funcionario', 'Estado', 'Solicitud o problema']
    filas = [
        [a.codigo_verificador, timezone.localtime(a.fecha).strftime('%d-%m-%Y %H:%M'), a.delegacion.nombre, a.item.nombre,
         a.funcionario_autor.nombre, a.get_estado_display(), a.solicitud_problema]
        for a in actividades
    ]
    return columnas, filas


def filas_de_compromisos(compromisos):
    """Columnas y filas planas de un informe de compromisos."""
    columnas = ['Folio', 'Delegación', 'Eje', 'Solicitante', 'Responsable', 'Fecha comprometida', 'Estado', 'Situación del plazo', 'Descripción']
    filas = [
        [c.folio, c.delegacion.nombre, c.eje, c.solicitante, c.funcionario_responsable.nombre if c.funcionario_responsable_id else '',
         c.fecha_comprometida.strftime('%d-%m-%Y'), c.get_estado_display(), situacion_de_plazo(c)[0], c.descripcion]
        for c in compromisos
    ]
    return columnas, filas


def filas_de_cumplimiento(resultados, esperado):
    """Columnas y filas planas de un informe de cumplimiento por delegación."""
    columnas = ['Delegación', 'Cumplimiento (%)', 'Esperado al día (%)', 'Diferencia (puntos)', 'Estado']
    filas = [
        [r['nombre'], r['cumplimiento'], esperado, r['diferencia'] if r['diferencia'] is not None else '', r['estado']]
        for r in resultados
    ]
    return columnas, filas


def respuesta_csv(nombre_archivo, columnas, filas):
    """CSV con BOM y separador «;» para que Excel en configuración regional chilena lo abra con tildes y columnas."""
    respuesta = HttpResponse(content_type='text/csv; charset=utf-8')
    respuesta['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    respuesta.write('﻿')
    escritor = csv.writer(respuesta, delimiter=';')
    escritor.writerow(columnas)
    escritor.writerows(filas)
    return respuesta
