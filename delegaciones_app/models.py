from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, time, timedelta
from decimal import Decimal
import json
import uuid

DOS_DECIMALES = Decimal('0.01')


class Delegacion(models.Model):
	nombre = models.CharField(max_length=255, unique=True)
	estado = models.BooleanField(default=True)
	ambito = models.CharField(max_length=255, null=True, blank=True)
	# Ajuste 8: se conserva para no perder el texto que se muestra y se busca en el mantenedor.
	enfasis = models.TextField(null=True, blank=True)

	class Meta:
		db_table = 'delegacion'
		ordering = ['nombre']
		verbose_name = 'delegación'
		verbose_name_plural = 'delegaciones'

	def __str__(self):
		return self.nombre

	def get_identificador(self):
		return self.nombre

	def set_estado(self, estado):
		self.estado = estado
		self.save(update_fields=['estado'])

	def asignar_funcionario(self, funcionario):
		funcionario.delegacion = self
		funcionario.save(update_fields=['delegacion'])

	def ultimos_indicadores(self, periodo):
		"""Último Indicador de cada meta de los funcionarios de la delegación en el período."""
		ultimos = {}
		indicadores = Indicador.objects.filter(periodo=periodo, meta__funcionario__delegacion=self).select_related('meta__item', 'meta__funcionario').order_by('fecha_calculo', 'pk')
		for indicador in indicadores:
			ultimos[indicador.meta_id] = indicador
		return list(ultimos.values())

	@staticmethod
	def promedio_ponderado(indicadores):
		"""Cumplimiento promedio de los indicadores, ponderado por el ponderador de cada meta (RN-005)."""
		total_ponderador = sum(indicador.meta.ponderador for indicador in indicadores)
		if not total_ponderador:
			return Decimal('0.00')
		total_ponderado = sum(indicador.ponderacion for indicador in indicadores)
		return (total_ponderado * 100 / total_ponderador).quantize(DOS_DECIMALES)

	def obtener_cumplimiento_global(self, periodo):
		return self.promedio_ponderado(self.ultimos_indicadores(periodo))


class Cargo(models.Model):
	nombre = models.CharField(max_length=255)
	vigencia = models.BooleanField(default=True)

	class Meta:
		db_table = 'cargo'
		ordering = ['nombre']

	def __str__(self):
		return self.nombre

	def verificar_vigencia(self):
		return self.vigencia

	def actualizar_ponderaciones(self, item, valor):
		if item.cargo_id != self.pk:
			raise ValidationError(f'El ítem «{item}» no pertenece al cargo «{self}».')
		item.ponderacion = Decimal(valor)
		item.full_clean()
		item.save(update_fields=['ponderacion'])


class Rol(models.Model):
	nombre_rol = models.CharField(max_length=255, unique=True)

	class Meta:
		db_table = 'rol'
		ordering = ['nombre_rol']
		verbose_name_plural = 'roles'

	def __str__(self):
		return self.nombre_rol


class Funcionario(models.Model):
	# Ajuste 1: el diseño no indica cómo inicia sesión un funcionario.
	usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='funcionario')
	identificador_institucional = models.CharField(max_length=255, unique=True)
	nombre = models.CharField(max_length=255)
	cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT, related_name='funcionarios')
	# Ajuste 3: null para roles de alcance global (administrador, coordinador).
	delegacion = models.ForeignKey(Delegacion, on_delete=models.PROTECT, null=True, blank=True, related_name='funcionarios')
	estado = models.BooleanField(default=True)
	roles = models.ManyToManyField(Rol, through='FuncionarioRol', related_name='funcionarios')

	class Meta:
		db_table = 'funcionario'
		ordering = ['nombre']

	def __str__(self):
		return self.nombre

	def get_identificador(self):
		return self.identificador_institucional

	def reasignar_cargo(self, nuevo_cargo):
		if not nuevo_cargo.verificar_vigencia():
			raise ValidationError(f'El cargo «{nuevo_cargo}» no está vigente.')
		self.cargo = nuevo_cargo
		self.save(update_fields=['cargo'])

	def registrar_actividad(self, datos):
		actividad = Actividad(funcionario_autor=self, **datos)
		if not actividad.delegacion_id:
			actividad.delegacion_id = self.delegacion_id
		actividad.generar_codigo_verificador()
		actividad.full_clean()
		actividad.save()
		return actividad

	def subir_evidencia(self, actividad, archivo, comentario=None):
		evidencia = Evidencia(actividad=actividad, funcionario_autor=self, archivo_vinculo=archivo, metadatos={'comentario': comentario} if comentario else None)
		# El código de la evidencia se asigna al guardarla.
		evidencia.full_clean(exclude=['codigo_evidencia'])
		actividad.vincular_evidencia(evidencia)
		return evidencia


class FuncionarioRol(models.Model):
	funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
	rol = models.ForeignKey(Rol, on_delete=models.PROTECT)

	class Meta:
		db_table = 'funcionario_rol'
		constraints = [models.UniqueConstraint(fields=['funcionario', 'rol'], name='funcionario_rol_unico')]

	def __str__(self):
		return f'{self.funcionario} - {self.rol}'


class UsuarioMaestro(models.Model):
	# Ajuste 2: enlace opcional con el usuario de Django, para los superusuarios.
	usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='usuario_maestro')
	identificador_maestro = models.CharField(max_length=255, unique=True)
	nombre = models.CharField(max_length=255)
	nivel_dominio = models.CharField(max_length=255)
	estado = models.BooleanField(default=True)

	class Meta:
		db_table = 'usuario_maestro'
		verbose_name = 'usuario maestro'
		verbose_name_plural = 'usuarios maestros'

	def __str__(self):
		return self.nombre


class VersionOptimistaMixin:
	"""RF-034 y RNF-003: control de concurrencia optimista con el campo version."""

	MENSAJE_CONCURRENCIA = 'El registro fue modificado por otro usuario. Recarga la página y vuelve a intentarlo.'

	def save(self, *args, **kwargs):
		if self._state.adding:
			return super().save(*args, **kwargs)
		with transaction.atomic():
			# Solo actualiza si nadie cambió la versión desde que se leyó el registro.
			actualizados = type(self).objects.filter(pk=self.pk, version=self.version).update(version=models.F('version') + 1)
			if not actualizados:
				raise ValidationError(self.MENSAJE_CONCURRENCIA)
			self.version += 1
			if kwargs.get('update_fields') is not None:
				kwargs['update_fields'] = {*kwargs['update_fields'], 'version'}
			return super().save(*args, **kwargs)


class Actividad(VersionOptimistaMixin, models.Model):
	ESTADOS = [('borrador', 'Borrador'), ('pendiente', 'Pendiente de revisión'), ('aprobada', 'Aprobada'), ('rechazada', 'Rechazada'), ('correccion', 'Requiere corrección')]
	codigo_verificador = models.CharField(max_length=50, unique=True, editable=False)
	funcionario_autor = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name='actividades')
	# Ajuste 9: se conserva para filtrar y medir por delegación (también la de coordinadores sin delegación).
	delegacion = models.ForeignKey(Delegacion, on_delete=models.PROTECT, related_name='actividades')
	item = models.ForeignKey('ItemMedible', on_delete=models.PROTECT, related_name='actividades')
	catalogo = models.ForeignKey('Catalogo', on_delete=models.PROTECT, null=True, blank=True, related_name='actividades')
	compromiso = models.ForeignKey('Compromiso', on_delete=models.SET_NULL, null=True, blank=True, related_name='actividades')
	fecha = models.DateTimeField()
	solicitud_problema = models.TextField()
	accion = models.TextField()
	contacto_nombre = models.CharField(max_length=255, null=True, blank=True)
	contacto_telefono = models.CharField(max_length=20, null=True, blank=True)
	estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
	version = models.PositiveIntegerField(default=1, editable=False)
	# Ajuste 7: orden de listados.
	creada = models.DateTimeField(auto_now_add=True)
	actualizada = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'actividad'
		ordering = ['-fecha', '-creada']

	def __str__(self):
		return f'{self.codigo_verificador} - {self.solicitud_problema[:50]}'

	def generar_codigo_verificador(self):
		"""RN-010: código único e inmutable, generado al registrar la actividad."""
		if not self.codigo_verificador:
			self.codigo_verificador = f'EVD-{timezone.localdate():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}'
		return self.codigo_verificador

	def clean(self):
		super().clean()
		if self.item_id:
			periodo = self.item.periodo
			periodo.verificar_editable()
			if self.fecha and not periodo.fecha_inicio <= timezone.localtime(self.fecha).date() <= periodo.fecha_termino:
				raise ValidationError({'fecha': f'La fecha de la actividad debe estar dentro del período «{periodo}».'})

	def save(self, *args, **kwargs):
		self.generar_codigo_verificador()
		if not self._state.adding:
			guardado = Actividad.objects.filter(pk=self.pk).values_list('codigo_verificador', flat=True).first()
			if guardado and guardado != self.codigo_verificador:
				raise ValidationError('El código verificador de una actividad no se puede modificar.')
		super().save(*args, **kwargs)

	def cambiar_estado(self, nuevo_estado):
		if nuevo_estado not in dict(self.ESTADOS):
			raise ValidationError(f'Estado de actividad no válido: {nuevo_estado}.')
		if self.estado == 'aprobada' and nuevo_estado != 'aprobada':
			raise ValidationError('Una actividad aprobada ya suma al avance y no cambia de estado.')
		self.estado = nuevo_estado
		self.save(update_fields=['estado', 'actualizada'])

	def vincular_evidencia(self, evidencia):
		evidencia.actividad = self
		evidencia.save()
		evidencia.enviar_a_revision()

	def actualizar_indicadores(self):
		"""Cada validación deja un Indicador nuevo en las metas del ítem; los períodos cerrados quedan congelados (RN-013)."""
		if not self.item_id or self.item.periodo.estado == 'cerrado':
			return []
		metas = self.item.metas.select_related('funcionario', 'item__periodo')
		# calcular_avance solo cuenta las actividades de la delegación de la meta.
		return [Indicador.generar(meta) for meta in metas if meta.funcionario.delegacion_id in (None, self.delegacion_id)]


def validar_tamano_evidencia(archivo):
	"""CU-09.2 y RNF-017: rechaza el archivo que supera el tamaño máximo configurado (por defecto 5 MB)."""
	try:
		tamano = archivo.size
	except (OSError, ValueError):
		return  # archivo ya guardado y ausente del disco, o campo vacío: no hay nada que medir
	maximo_mb = settings.EVIDENCIA_TAMANO_MAXIMO_MB
	if tamano > maximo_mb * 1024 * 1024:
		raise ValidationError(f'El archivo pesa {tamano / 1024 / 1024:.1f} MB y el máximo permitido es {maximo_mb} MB.')


EXTENSIONES_EVIDENCIA = ['jpg', 'jpeg', 'png', 'pdf']


class Evidencia(models.Model):
	ESTADOS_REVISION = [('pendiente', 'Pendiente de revisión'), ('aprobada', 'Aprobada'), ('rechazada', 'Rechazada'), ('correccion', 'Requiere corrección')]
	codigo_evidencia = models.CharField(max_length=60, unique=True, editable=False)
	actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, related_name='evidencias')
	funcionario_autor = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name='evidencias')
	archivo_vinculo = models.FileField(upload_to='evidencias/%Y/%m/', max_length=255, validators=[FileExtensionValidator(EXTENSIONES_EVIDENCIA), validar_tamano_evidencia])
	fecha_carga = models.DateTimeField(default=timezone.now)
	metadatos = models.JSONField(null=True, blank=True)
	estado_revision = models.CharField(max_length=20, choices=ESTADOS_REVISION, default='pendiente')

	class Meta:
		db_table = 'evidencia'

	def __str__(self):
		return f'{self.actividad.codigo_verificador} - {self.archivo_vinculo.name or "sin archivo"}'

	def _siguiente_codigo(self):
		prefijo = self.actividad.codigo_verificador
		numero = Evidencia.objects.filter(actividad_id=self.actividad_id).count() + 1
		while Evidencia.objects.filter(codigo_evidencia=f'{prefijo}-{numero:02d}').exists():
			numero += 1
		return f'{prefijo}-{numero:02d}'

	def save(self, *args, **kwargs):
		if not self._state.adding:
			guardado = Evidencia.objects.filter(pk=self.pk).values_list('codigo_evidencia', flat=True).first()
			if guardado and guardado != self.codigo_evidencia:
				raise ValidationError('El código de una evidencia no se puede modificar.')
		if not self.codigo_evidencia and self.actividad_id:
			self.codigo_evidencia = self._siguiente_codigo()
		super().save(*args, **kwargs)

	def enviar_a_revision(self):
		self.estado_revision = 'pendiente'
		self.save(update_fields=['estado_revision'])
		if self.actividad.estado != 'aprobada':
			self.actividad.cambiar_estado('pendiente')

	def descargar_archivo(self):
		return self.archivo_vinculo.url if self.archivo_vinculo else None

	def reemplazar_archivo(self, nuevo_archivo):
		self.archivo_vinculo = nuevo_archivo
		self.full_clean()
		self.save()
		self.enviar_a_revision()


class Validacion(models.Model):
	DECISIONES = [('aprobada', 'Aprobada'), ('rechazada', 'Rechazada'), ('correccion', 'Requiere corrección')]
	evidencia = models.ForeignKey(Evidencia, on_delete=models.CASCADE, related_name='validaciones')
	funcionario_verificador = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name='validaciones')
	decision = models.CharField(max_length=20, choices=DECISIONES)
	fecha = models.DateTimeField(default=timezone.now)
	observacion = models.TextField(null=True, blank=True)
	resultado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	# Número de revisión de la evidencia (1.ª, 2.ª, ...).
	version = models.PositiveIntegerField(default=1)

	class Meta:
		db_table = 'validacion'
		ordering = ['-fecha']
		verbose_name = 'validación'
		verbose_name_plural = 'validaciones'

	def __str__(self):
		return f'{self.evidencia} - {self.get_decision_display()} (v{self.version})'

	@transaction.atomic
	def _decidir(self, decision, observacion):
		"""RN-009: la decisión se refleja en la evidencia y en la actividad; solo «aprobada» aporta al avance."""
		self.decision = decision
		self.observacion = observacion
		self.version = Validacion.objects.filter(evidencia_id=self.evidencia_id).count() + 1
		self.save()
		self.evidencia.estado_revision = decision
		self.evidencia.save(update_fields=['estado_revision'])
		self.evidencia.actividad.cambiar_estado(decision)
		return self

	def aprobar_evidencia(self, observacion=None):
		return self._decidir('aprobada', observacion)

	def rechazar_evidencia(self, motivo):
		if not (motivo or '').strip():
			raise ValidationError('El rechazo de una evidencia exige un motivo.')
		return self._decidir('rechazada', motivo)

	def solicitar_correccion(self, observacion):
		if not (observacion or '').strip():
			raise ValidationError('La solicitud de corrección exige una observación.')
		return self._decidir('correccion', observacion)


class Compromiso(VersionOptimistaMixin, models.Model):
	ESTADOS = [('ingresado', 'Ingresado'), ('pendiente', 'Pendiente'), ('proceso', 'En proceso'), ('realizado', 'Realizado')]
	EJES = [
		('Seguridad', 'Seguridad'),
		('DISERCO', 'DISERCO'),
		('Gestión Social', 'Gestión Social'),
		('Organizaciones Comunitarias', 'Organizaciones Comunitarias'),
	]
	ORIGENES = [('interno', 'Interno'), ('externo', 'Externo')]
	# Ajuste 4: folio, eje, delegacion, descripcion y fecha_ingreso vienen de data/solicitudes.json.
	folio = models.CharField(max_length=30, unique=True)
	delegacion = models.ForeignKey(Delegacion, on_delete=models.PROTECT, related_name='compromisos')
	funcionario_responsable = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name='compromisos')
	item = models.ForeignKey('ItemMedible', on_delete=models.PROTECT, null=True, blank=True, related_name='compromisos')
	origen = models.CharField(max_length=255, choices=ORIGENES)
	solicitante = models.CharField(max_length=255)
	territorio = models.CharField(max_length=255)
	eje = models.CharField(max_length=40, choices=EJES, default='Gestión Social')
	descripcion = models.TextField()
	fecha_comprometida = models.DateField()
	fecha_ingreso = models.DateField(default=timezone.localdate)
	estado = models.CharField(max_length=20, choices=ESTADOS, default='ingresado')
	observacion = models.TextField(blank=True)
	area_apoyo = models.CharField(max_length=255, null=True, blank=True)
	# Ajuste 10: orden de la agenda.
	creado = models.DateTimeField(auto_now_add=True)
	version = models.PositiveIntegerField(default=1, editable=False)

	class Meta:
		db_table = 'compromiso'
		ordering = ['-fecha_comprometida', '-creado']

	def __str__(self):
		return f'{self.folio} - {self.descripcion[:50]}'

	@property
	def vencido(self):
		return self.estado != 'realizado' and self.fecha_comprometida < timezone.localdate()

	@property
	def dias_para_vencer(self):
		return (self.fecha_comprometida - timezone.localdate()).days

	@property
	def proximo_a_vencer(self):
		"""RF-019: no está realizado y vence dentro de los días de alerta configurados (por defecto 3)."""
		return self.estado != 'realizado' and 0 <= self.dias_para_vencer <= settings.COMPROMISO_DIAS_ALERTA

	def estados_permitidos(self):
		"""RF-018: transiciones controladas. Se avanza hacia adelante (se pueden saltar etapas) y un
		compromiso realizado solo se reabre a «en proceso»."""
		orden = [estado for estado, _ in self.ESTADOS]
		siguientes = ['proceso'] if self.estado == 'realizado' else orden[orden.index(self.estado) + 1:]
		etiquetas = dict(self.ESTADOS)
		return [(estado, etiquetas[estado]) for estado in siguientes]

	def validar_transicion(self, estado):
		etiquetas = dict(self.ESTADOS)
		if estado not in etiquetas:
			raise ValidationError(f'Estado de compromiso no válido: {estado}.')
		if estado not in [permitido for permitido, _ in self.estados_permitidos()]:
			raise ValidationError(f'Transición no permitida: de «{etiquetas[self.estado]}» a «{etiquetas[estado]}».')

	def motivo_no_eliminable(self):
		"""CU-14.2: un incumplimiento (vencido y sin realizar) se conserva con su historial de seguimiento."""
		if self.vencido:
			return 'El compromiso está vencido sin realizarse: se conserva con su historial de seguimiento.'
		return None

	def delete(self, *args, **kwargs):
		motivo = self.motivo_no_eliminable()
		if motivo:
			raise ValidationError(motivo)
		return super().delete(*args, **kwargs)

	def registrar_historial(self, autor, estado_anterior, observacion=None):
		HistorialCompromiso.objects.create(
			compromiso=self, autor=autor,
			estado_anterior=estado_anterior, estado_nuevo=self.estado, observacion=observacion or '',
		)

	@transaction.atomic
	def set_estado(self, estado, autor, observacion=None):
		self.validar_transicion(estado)
		anterior = self.estado
		self.estado = estado
		self.save(update_fields=['estado'])
		self.registrar_historial(autor, anterior, observacion)

	@transaction.atomic
	def derivar_compromiso(self, nuevo_responsable, autor):
		if self.estado == 'realizado':
			raise ValidationError('Un compromiso realizado no se puede derivar.')
		anterior = self.funcionario_responsable
		self.funcionario_responsable = nuevo_responsable
		self.save(update_fields=['funcionario_responsable'])
		self.registrar_historial(autor, self.estado, f'Derivado de {anterior or "sin responsable"} a {nuevo_responsable}.')

	@transaction.atomic
	def cerrar_compromiso(self, resolucion, autor):
		if not (resolucion or '').strip():
			raise ValidationError('Cerrar un compromiso exige una resolución.')
		self.validar_transicion('realizado')
		anterior = self.estado
		self.estado = 'realizado'
		self.observacion = resolucion
		self.save(update_fields=['estado', 'observacion'])
		self.registrar_historial(autor, anterior, resolucion)


class MedicionDelegacion(models.Model):
	ESTADOS = [('verde', 'Verde'), ('amarillo', 'Amarillo'), ('rojo', 'Rojo')]
	delegacion = models.ForeignKey(Delegacion, on_delete=models.PROTECT, related_name='mediciones')
	cumplimiento = models.DecimalField(max_digits=5, decimal_places=2)
	meta = models.DecimalField(max_digits=5, decimal_places=2)
	fecha_datos = models.DateField()
	estado_reportado = models.CharField(max_length=12, choices=ESTADOS)
	observacion = models.TextField(blank=True)

	class Meta:
		db_table = 'medicion_delegacion'
		ordering = ['delegacion__nombre', '-fecha_datos']
		constraints = [models.UniqueConstraint(fields=['delegacion', 'fecha_datos'], name='medicion_delegacion_fecha_unica')]

	def __str__(self):
		return f'{self.delegacion} - {self.fecha_datos}: {self.cumplimiento}%'


class Periodo(models.Model):
	ESTADOS = [('borrador', 'Borrador'), ('abierto', 'Abierto'), ('cerrado', 'Cerrado')]
	# Ajuste 6: el nombre se muestra en pantallas.
	nombre = models.CharField(max_length=255, unique=True)
	fecha_inicio = models.DateField()
	fecha_termino = models.DateField()
	dias_computables = models.PositiveIntegerField(default=0, editable=False)
	estado = models.CharField(max_length=255, choices=ESTADOS, default='borrador')
	# RN-006: umbral colectivo del período.
	umbral_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=80)
	version_parametros = models.PositiveIntegerField(default=1)

	_reapertura = False

	class Meta:
		db_table = 'periodo'
		ordering = ['-fecha_inicio']

	def __str__(self):
		return self.nombre

	def _estado_guardado(self):
		if not self.pk:
			return None
		return Periodo.objects.filter(pk=self.pk).values_list('estado', flat=True).first()

	def verificar_editable(self, estado=None):
		"""RN-013: un período cerrado no se modifica salvo reapertura auditada."""
		if (estado or self.estado) == 'cerrado':
			raise ValidationError(f'El período «{self.nombre}» está cerrado; solo se modifica mediante reapertura auditada.')

	def clean(self):
		if not self._reapertura and self._estado_guardado() == 'cerrado':
			self.verificar_editable('cerrado')
		if self.fecha_inicio and self.fecha_termino and self.fecha_termino < self.fecha_inicio:
			raise ValidationError('La fecha de término no puede ser anterior al inicio.')

	def save(self, *args, **kwargs):
		if not self._reapertura and self._estado_guardado() == 'cerrado':
			self.verificar_editable('cerrado')
		self.dias_computables = (self.fecha_termino - self.fecha_inicio).days + 1
		super().save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		if self._estado_guardado() == 'cerrado':
			self.verificar_editable('cerrado')
		return super().delete(*args, **kwargs)

	def iniciar_periodo(self):
		if self.estado != 'borrador':
			raise ValidationError('Solo se puede iniciar un período en borrador.')
		# RN-001: al iniciar, los ítems de cada cargo deben sumar exactamente 100 %.
		sumas = self.items.values('cargo', 'cargo__nombre').annotate(total=Sum('ponderacion'))
		incompletos = [f"{fila['cargo__nombre']} ({fila['total']} %)" for fila in sumas if fila['total'] != 100]
		if incompletos:
			raise ValidationError('Las ponderaciones de cada cargo deben sumar 100 %: ' + ', '.join(incompletos))
		self.estado = 'abierto'
		self.save(update_fields=['estado'])

	def cerrar_periodo(self):
		if self.estado != 'abierto':
			raise ValidationError('Solo se puede cerrar un período abierto.')
		self.estado = 'cerrado'
		self.save(update_fields=['estado'])

	@transaction.atomic
	def reabrir_periodo(self, motivo, usuario):
		if self.estado != 'cerrado':
			raise ValidationError('Solo se puede reabrir un período cerrado.')
		if not (motivo or '').strip():
			raise ValidationError('La reapertura de un período exige un motivo.')
		self.estado = 'abierto'
		self.version_parametros += 1
		self._reapertura = True
		try:
			self.save(update_fields=['estado', 'version_parametros'])
		finally:
			self._reapertura = False
		Auditoria.registrar_evento(
			usuario, 'reabrir_periodo', 'Periodo', self.pk,
			{'estado': 'cerrado'}, {'estado': 'abierto', 'motivo': motivo, 'version_parametros': self.version_parametros},
		)

	def _dias_transcurridos(self, fecha=None):
		fecha = fecha or timezone.localdate()
		total = (self.fecha_termino - self.fecha_inicio).days + 1
		return min(max((fecha - self.fecha_inicio).days + 1, 0), total), total

	def calcular_dias_restantes(self, fecha=None):
		transcurridos, total = self._dias_transcurridos(fecha)
		return total - transcurridos

	def porcentaje_esperado(self, fecha=None):
		"""RN-007: meta esperada al día = días transcurridos / días totales × 100."""
		transcurridos, total = self._dias_transcurridos(fecha)
		return (Decimal(transcurridos) * 100 / Decimal(total)).quantize(DOS_DECIMALES)

	def calcular_semaforo(self, cumplimiento, fecha=None):
		"""RN-008: verde si alcanza lo esperado al día, ámbar si llega al 60 % de lo esperado, rojo si no."""
		esperado = self.porcentaje_esperado(fecha)
		if cumplimiento >= esperado:
			return 'verde'
		if cumplimiento >= esperado * Decimal('0.6'):
			return 'ambar'
		return 'rojo'

	def obtener_parametro(self, clave, defecto=None):
		parametro = self.parametros.filter(clave=clave).first()
		return parametro.valor if parametro else defecto

	def alcanza_umbral(self, cumplimiento):
		"""RN-006: el cumplimiento colectivo debe alcanzar el umbral mínimo del período."""
		return cumplimiento >= self.umbral_minimo


class ControlPeriodoCerradoMixin:
	"""RN-013 para los registros que dependen de un período: no se crean, modifican ni eliminan si está cerrado."""

	def obtener_periodo(self):
		return self.periodo if self.periodo_id else None

	def _verificar_periodo(self):
		periodo = self.obtener_periodo()
		if periodo:
			periodo.verificar_editable()

	def clean(self):
		super().clean()
		self._verificar_periodo()

	def save(self, *args, **kwargs):
		self._verificar_periodo()
		super().save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		self._verificar_periodo()
		return super().delete(*args, **kwargs)


class ParametroVersionado(ControlPeriodoCerradoMixin, models.Model):
	periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='parametros')
	clave = models.CharField(max_length=255)
	valor = models.CharField(max_length=255)
	descripcion = models.TextField(null=True, blank=True)

	class Meta:
		db_table = 'parametro_versionado'
		verbose_name = 'parámetro versionado'
		verbose_name_plural = 'parámetros versionados'
		constraints = [models.UniqueConstraint(fields=['periodo', 'clave'], name='parametro_periodo_clave_unico')]

	def __str__(self):
		return f'{self.periodo} - {self.clave} = {self.valor}'


class ItemMedible(ControlPeriodoCerradoMixin, models.Model):
	cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT, related_name='items')
	periodo = models.ForeignKey(Periodo, on_delete=models.PROTECT, related_name='items')
	nombre = models.CharField(max_length=255)
	servicio = models.CharField(max_length=255, null=True, blank=True)
	ponderacion = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

	class Meta:
		db_table = 'item_medible'
		ordering = ['periodo', 'cargo', 'nombre']
		verbose_name = 'ítem medible'
		verbose_name_plural = 'ítems medibles'

	def __str__(self):
		return f'{self.nombre} ({self.cargo}, {self.periodo})'

	def clean(self):
		super().clean()
		# RN-001: la suma del cargo en el período no puede superar 100 %; iniciar_periodo() exige exactamente 100 %.
		if self.cargo_id and self.periodo_id and self.ponderacion is not None:
			otros = ItemMedible.objects.filter(cargo_id=self.cargo_id, periodo_id=self.periodo_id).exclude(pk=self.pk)
			total = (otros.aggregate(total=Sum('ponderacion'))['total'] or 0) + self.ponderacion
			if total > 100:
				raise ValidationError({'ponderacion': f'Las ponderaciones del cargo en el período sumarían {total} %; no pueden superar 100 %.'})


class Catalogo(models.Model):
	TIPOS = [('actividad', 'Actividad'), ('servicio', 'Servicio'), ('atencion', 'Tipo de atención'), ('item', 'Ítem de medición')]
	codigo = models.CharField(max_length=50, unique=True)
	nombre = models.CharField(max_length=255)
	tipo = models.CharField(max_length=100, choices=TIPOS)
	subtipo = models.CharField(max_length=100, null=True, blank=True)
	area = models.CharField(max_length=100, null=True, blank=True)
	activo = models.BooleanField(default=True)

	class Meta:
		db_table = 'catalogo'
		ordering = ['tipo', 'nombre']
		verbose_name = 'elemento de catálogo'
		verbose_name_plural = 'catálogo'

	def __str__(self):
		return f'{self.get_tipo_display()}: {self.nombre}'

	def activar(self):
		self.activo = True
		self.save(update_fields=['activo'])

	def desactivar(self):
		self.activo = False
		self.save(update_fields=['activo'])


class Meta(ControlPeriodoCerradoMixin, models.Model):
	item = models.ForeignKey(ItemMedible, on_delete=models.PROTECT, related_name='metas')
	funcionario = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name='metas')
	# RN-002: el valor objetivo debe ser mayor que cero.
	valor_objetivo = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(DOS_DECIMALES)])
	unidad = models.CharField(max_length=255, default='actividades')
	# Porcentaje (0 a 100) con que la meta pesa en el cumplimiento colectivo.
	ponderador = models.DecimalField(max_digits=10, decimal_places=2, default=100, validators=[MinValueValidator(0)])

	class Meta:
		db_table = 'meta'
		ordering = ['item__nombre']

	def __str__(self):
		return f'{self.item.nombre} - {self.funcionario}'

	def obtener_periodo(self):
		return self.item.periodo if self.item_id else None

	def evaluar_progreso(self, valor_actual):
		"""RN-004: cumplimiento = valor actual / valor objetivo × 100."""
		return (Decimal(valor_actual) * 100 / self.valor_objetivo).quantize(DOS_DECIMALES)

	def actualizar_valor_objetivo(self, nuevo_valor):
		self.valor_objetivo = Decimal(nuevo_valor)
		self.full_clean()
		self.save(update_fields=['valor_objetivo'])


class Indicador(ControlPeriodoCerradoMixin, models.Model):
	SEMAFOROS = [('verde', 'Verde'), ('ambar', 'Ámbar'), ('rojo', 'Rojo')]
	meta = models.ForeignKey('Meta', on_delete=models.CASCADE, related_name='indicadores')
	periodo = models.ForeignKey(Periodo, on_delete=models.PROTECT, related_name='indicadores')
	fecha_calculo = models.DateTimeField(default=timezone.now)
	avance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	cumplimiento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	# Cumplimiento ponderado (RN-005).
	ponderacion = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	# Se guarda, pero el informe no define cómo se aplica: no entra en el cálculo.
	ajuste = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	semaforo = models.CharField(max_length=20, choices=SEMAFOROS, default='rojo')

	class Meta:
		db_table = 'indicador'
		ordering = ['-fecha_calculo']
		verbose_name_plural = 'indicadores'

	def __str__(self):
		return f'{self.meta} - {self.fecha_calculo:%Y-%m-%d}: {self.cumplimiento} %'

	@classmethod
	def generar(cls, meta, fecha=None):
		indicador = cls(meta=meta, periodo=meta.item.periodo)
		indicador.calcular_avance()
		indicador.calcular_cumplimiento()
		indicador.actualizar_semaforo(fecha)
		indicador.save()
		return indicador

	def calcular_avance(self):
		"""RN-003 y RN-009: actividades aprobadas del ítem en el período que tienen una validación aprobada.

		Si el funcionario de la meta tiene delegación, solo cuentan las actividades de esa delegación.
		"""
		# Rango de instantes en hora de Chile; evita __date, que en MySQL exige tablas de zonas horarias.
		desde = timezone.make_aware(datetime.combine(self.periodo.fecha_inicio, time.min))
		hasta = timezone.make_aware(datetime.combine(self.periodo.fecha_termino + timedelta(days=1), time.min))
		actividades = Actividad.objects.filter(
			item=self.meta.item,
			estado='aprobada',
			fecha__gte=desde,
			fecha__lt=hasta,
			evidencias__validaciones__decision='aprobada',
		)
		if self.meta.funcionario.delegacion_id:
			actividades = actividades.filter(delegacion_id=self.meta.funcionario.delegacion_id)
		self.avance = actividades.distinct().count()
		return self.avance

	def calcular_cumplimiento(self):
		"""RN-004 y RN-005: cumplimiento con tope configurable y cumplimiento ponderado."""
		tope = Decimal(self.periodo.obtener_parametro('maximo_cumplimiento', '150'))
		self.cumplimiento = min(self.meta.evaluar_progreso(self.avance), tope)
		self.ponderacion = (self.meta.ponderador * self.cumplimiento / 100).quantize(DOS_DECIMALES)
		return self.cumplimiento

	def actualizar_semaforo(self, fecha=None):
		"""RN-008: el color lo decide el período (ver Periodo.calcular_semaforo)."""
		self.semaforo = self.periodo.calcular_semaforo(self.cumplimiento, fecha)
		return self.semaforo


class HistorialCompromiso(models.Model):
	compromiso = models.ForeignKey(Compromiso, on_delete=models.CASCADE, related_name='historial')
	estado_anterior = models.CharField(max_length=20)
	estado_nuevo = models.CharField(max_length=20)
	autor = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name='historial_compromisos')
	fecha = models.DateTimeField(auto_now_add=True)
	observacion = models.TextField(null=True, blank=True)

	class Meta:
		db_table = 'historial_compromiso'

	def __str__(self):
		return f'{self.compromiso.folio}: {self.estado_anterior or "inicio"} -> {self.estado_nuevo}'


MENSAJE_AUDITORIA_SOLO_LECTURA = 'La auditoría es de solo lectura: sus registros no se modifican ni se eliminan (RNF-008).'


class AuditoriaQuerySet(models.QuerySet):
	"""Impide modificar o borrar auditoría en bloque: solo se agregan eventos."""

	def update(self, **kwargs):
		raise ValidationError(MENSAJE_AUDITORIA_SOLO_LECTURA)

	def delete(self):
		raise ValidationError(MENSAJE_AUDITORIA_SOLO_LECTURA)


class Auditoria(models.Model):
	objects = AuditoriaQuerySet.as_manager()

	funcionario = models.ForeignKey(Funcionario, on_delete=models.PROTECT, null=True, blank=True, related_name='auditorias')
	usuario_maestro = models.ForeignKey(UsuarioMaestro, on_delete=models.PROTECT, null=True, blank=True, related_name='auditorias')
	evento = models.CharField(max_length=255)
	fecha = models.DateTimeField(auto_now_add=True)
	entidad = models.CharField(max_length=255)
	identificador_registro = models.CharField(max_length=255)
	valor_anterior = models.TextField(null=True, blank=True)
	valor_nuevo = models.TextField(null=True, blank=True)

	class Meta:
		db_table = 'auditoria'

	def __str__(self):
		return f'{self.fecha:%Y-%m-%d %H:%M} - {self.evento} - {self.entidad} {self.identificador_registro}'

	def save(self, *args, **kwargs):
		# RNF-008: un evento ya registrado no se vuelve a guardar.
		if not self._state.adding:
			raise ValidationError(MENSAJE_AUDITORIA_SOLO_LECTURA)
		super().save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		raise ValidationError(MENSAJE_AUDITORIA_SOLO_LECTURA)

	@staticmethod
	def _como_texto(valor):
		if valor is None or isinstance(valor, str):
			return valor
		return json.dumps(valor, ensure_ascii=False, default=str)

	@classmethod
	def registrar_evento(cls, usuario, accion, entidad, identificador='', valor_anterior=None, valor_nuevo=None):
		"""Registra un evento a nombre del UsuarioMaestro del usuario o, si no tiene, de su Funcionario."""
		usuario_maestro = UsuarioMaestro.objects.filter(usuario=usuario).first()
		funcionario = None if usuario_maestro else Funcionario.objects.filter(usuario=usuario).first()
		return cls.objects.create(
			funcionario=funcionario,
			usuario_maestro=usuario_maestro,
			evento=accion,
			entidad=entidad,
			identificador_registro=str(identificador),
			valor_anterior=cls._como_texto(valor_anterior),
			valor_nuevo=cls._como_texto(valor_nuevo),
		)
