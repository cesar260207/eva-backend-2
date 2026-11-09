from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.models import Count
from django.utils import timezone


def semana_abierta(fecha, hoy=None):
	"""Devuelve si una fecha de actividad todavía pertenece a una semana abierta."""
	hoy = hoy or timezone.localdate()
	if fecha > hoy:
		return False
	lunes_actual = hoy - timedelta(days=hoy.weekday())
	if hoy.weekday() == 0:
		return fecha >= lunes_actual - timedelta(days=7)
	return fecha >= lunes_actual


def validar_fecha_actividad(fecha, periodo):
	hoy = timezone.localdate()
	if fecha > hoy:
		raise ValidationError({'fecha': 'La fecha de la actividad no puede estar en el futuro.'})
	if not semana_abierta(fecha, hoy):
		raise ValidationError({'fecha': 'El cierre semanal impide registrar una actividad de una semana anterior.'})
	if not periodo.fecha_inicio <= fecha <= periodo.fecha_termino:
		raise ValidationError({'fecha': f'La fecha debe estar dentro del período «{periodo}».'})


def validar_limite_diario(funcionario, fecha, periodo):
	maximo = int(periodo.obtener_parametro('max_ingresos_diarios', '7'))
	if not funcionario or maximo <= 0:
		return
	desde = timezone.make_aware(__import__('datetime').datetime.combine(fecha, __import__('datetime').time.min))
	hasta = desde + timedelta(days=1)
	from .models import Actividad
	ingresos = Actividad.objects.filter(funcionario_autor=funcionario, fecha__gte=desde, fecha__lt=hasta).count()
	if ingresos >= maximo:
		raise ValidationError({'fecha': f'El máximo de ingresos para el día es {maximo}.'})


def evaluar_puntaje(actividad):
	"""Calcula la elegibilidad operativa, conservando el historial aunque no puntúe."""
	if getattr(actividad, 'gestion_interna', False):
		return False, 'Otra gestión: actividad interna solicitada por el delegado.'
	if getattr(actividad, 'tipo_accion', 'ejecucion') == 'gestion_previa':
		return False, 'Gestión previa: no puntúa, pero conserva el historial.'
	if not getattr(actividad, 'contacto_nombre', None) or not getattr(actividad, 'contacto_telefono', None):
		return False, 'Falta el nombre y teléfono del usuario.'
	return True, ''


def dias_ausencia(funcionario, periodo, hasta=None):
	"""Cuenta días de ausencia sin duplicar fechas superpuestas."""
	hasta = hasta or periodo.fecha_termino
	desde = periodo.fecha_inicio
	dias = set()
	for ausencia in funcionario.ausencias.filter(desde__lte=hasta, hasta__gte=desde):
		inicio = max(desde, ausencia.desde)
		termino = min(hasta, ausencia.hasta)
		dias.update(desde + timedelta(days=i) for i in range((termino - inicio).days + 1))
	return len(dias)


def porcentaje_esperado_ajustado(funcionario, periodo, fecha=None):
	fecha = min(fecha or timezone.localdate(), periodo.fecha_termino)
	transcurridos, total = periodo._dias_transcurridos(fecha)
	ausentes_transcurridos = dias_ausencia(funcionario, periodo, fecha)
	ausentes_total = dias_ausencia(funcionario, periodo)
	computables_transcurridos = max(transcurridos - ausentes_transcurridos, 0)
	computables_total = max(total - ausentes_total, 1)
	return (Decimal(computables_transcurridos) * 100 / Decimal(computables_total)).quantize(Decimal('0.01'))
