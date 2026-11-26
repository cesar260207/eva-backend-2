from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import Q, Sum
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, time, timedelta
from decimal import Decimal
import json
import re
import uuid

from .rut import normalizar_rut, validar_rut

DOS_DECIMALES = Decimal('0.01')
# RF-010: teléfono de contacto con dígitos, espacios, guiones o paréntesis y un + inicial opcional (6 a 20 caracteres).
FORMATO_TELEFONO = re.compile(r'^[+(]?[0-9][0-9 ()\-]{5,18}$')


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
	# Evaluación 3: la cuenta se crea con una contraseña temporal que se debe cambiar en el primer ingreso.
	debe_cambiar_contrasena = models.BooleanField(default=False)

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
		verbose_name = 'rol asignado'
		verbose_name_plural = 'roles asignados'
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


class Organizacion(models.Model):
	TIPOS = [
		('junta_vecinos', 'Junta de vecinos'),
		('funcional', 'Organización funcional'),
		('adulto_mayor', 'Club de adulto mayor'),
		('deportiva', 'Organización deportiva'),
		('cultural', 'Centro de madres / cultural / juvenil'),
		('comite', 'Comité de vecinos, allegados o seguridad'),
		('sin_clasificar', 'Sin clasificar'),
	]
	nombre = models.CharField(max_length=255)
	tipo = models.CharField(max_length=30, choices=TIPOS, default='sin_clasificar')
	personalidad_juridica = models.CharField(max_length=50, blank=True)
	domicilio = models.CharField(max_length=255, blank=True)
	territorio = models.CharField(max_length=255, blank=True)
	socios_activos = models.PositiveIntegerField(null=True, blank=True)
	fecha_constitucion = models.DateField(null=True, blank=True)
	numero_registro = models.CharField(max_length=100, blank=True)
	fecha_inscripcion = models.DateField(null=True, blank=True)
	registro_direccion = models.CharField(max_length=255, blank=True)
	delegacion = models.ForeignKey(Delegacion, on_delete=models.PROTECT, null=True, blank=True, related_name='organizaciones')
	# «territorio» conserva el texto del registro municipal importado; la unidad territorial normalizada es esta FK.
	unidad_territorial = models.ForeignKey('Territorio', on_delete=models.PROTECT, null=True, blank=True, related_name='organizaciones')
	verificada = models.BooleanField(default=False)
	observaciones = models.TextField(blank=True)
	activa = models.BooleanField(default=True)

	class Meta:
		ordering = ['nombre']
		constraints = [
			models.UniqueConstraint(fields=['nombre', 'territorio'], name='organizacion_nombre_territorio_unico'),
		]

	def __str__(self):
		return self.nombre

	def clean(self):
		super().clean()
		if self.unidad_territorial_id and self.delegacion_id and self.unidad_territorial.delegacion_id != self.delegacion_id:
			raise ValidationError({'unidad_territorial': 'El territorio debe pertenecer a la delegación de la organización.'})


class Actividad(VersionOptimistaMixin, models.Model):
	# «antecedentes»: el verificador pidió más antecedentes; el autor completa y la actividad vuelve a revisión.
	ESTADOS = [
		('borrador', 'Borrador'), ('pendiente', 'Pendiente de revisión'), ('aprobada', 'Aprobada'), ('rechazada', 'Rechazada'),
		('antecedentes', 'Solicitud de más antecedentes'),
	]
	# Estados en que el autor corrige y la actividad vuelve a la cola de revisión.
	ESTADOS_CORREGIBLES = ('rechazada', 'antecedentes')
	TIPOS_ACCION = [('ejecucion', 'Ejecución'), ('gestion_previa', 'Gestión previa')]
	codigo_verificador = models.CharField(max_length=50, unique=True, editable=False)
	funcionario_autor = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name='actividades')
	# Ajuste 9: se conserva para filtrar y medir por delegación (también la de coordinadores sin delegación).
	delegacion = models.ForeignKey(Delegacion, on_delete=models.PROTECT, related_name='actividades')
	# Requerimiento de noviembre: «dónde» se hizo la actividad, más preciso que la delegación (opcional).
	lugar = models.CharField(max_length=255, blank=True, default='')
	item = models.ForeignKey('ItemMedible', on_delete=models.PROTECT, related_name='actividades')
	catalogo = models.ForeignKey('Catalogo', on_delete=models.PROTECT, null=True, blank=True, related_name='actividades')
	subtipo_atencion = models.ForeignKey('SubtipoAtencion', on_delete=models.PROTECT, null=True, blank=True, related_name='actividades')
	hito = models.ForeignKey('Hito', on_delete=models.SET_NULL, null=True, blank=True, related_name='actividades')
	compromiso = models.ForeignKey('Compromiso', on_delete=models.SET_NULL, null=True, blank=True, related_name='actividades')
	fecha = models.DateTimeField()
	solicitud_problema = models.TextField()
	accion = models.TextField()
	contacto_nombre = models.CharField(max_length=255, null=True, blank=True)
	contacto_telefono = models.CharField(max_length=20, null=True, blank=True)
	organizacion = models.ForeignKey(Organizacion, on_delete=models.PROTECT, null=True, blank=True, related_name='actividades')
	tipo_accion = models.CharField(max_length=20, choices=TIPOS_ACCION, default='ejecucion')
	gestion_interna = models.BooleanField(default=False)
	cuenta_puntaje = models.BooleanField(default=True)
	motivo_sin_puntaje = models.TextField(blank=True)
	estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
	version = models.PositiveIntegerField(default=1, editable=False)
	# Ajuste 7: orden de listados.
	creada = models.DateTimeField(auto_now_add=True)
	actualizada = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'actividad'
		verbose_name = 'actividad'
		verbose_name_plural = 'actividades'
		ordering = ['-fecha', '-creada']
		indexes = [
			# Búsquedas frecuentes: actividades del autor por día (límite diario), cola de revisión por delegación y estado.
			models.Index(fields=['funcionario_autor', 'fecha'], name='actividad_autor_fecha_idx'),
			models.Index(fields=['delegacion', 'estado'], name='actividad_deleg_estado_idx'),
		]

	def __str__(self):
		return f'{self.codigo_verificador} - {self.solicitud_problema[:50]}'

	def generar_codigo_verificador(self):
		"""RN-010: código único e inmutable, generado al registrar la actividad."""
		if not self.codigo_verificador:
			self.codigo_verificador = f'EVD-{timezone.localdate():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}'
		return self.codigo_verificador

	def clean(self):
		super().clean()
		if self.organizacion_id and self.delegacion_id and self.organizacion.delegacion_id != self.delegacion_id:
			raise ValidationError({'organizacion': 'La organización debe pertenecer a la delegación de la actividad.'})
		from .reglas import validar_fecha_actividad, validar_limite_diario, evaluar_puntaje

		if self.compromiso_id:
			self.gestion_interna = self.compromiso.gestion_interna
		if self.subtipo_atencion_id and self.subtipo_atencion.tipo_id != self.catalogo_id:
			raise ValidationError({'subtipo_atencion': 'El subtipo debe pertenecer al tipo de atención elegido.'})
		if self.hito_id and self.delegacion_id and self.hito.delegacion_id != self.delegacion_id:
			raise ValidationError({'hito': 'El hito debe pertenecer a la delegación de la actividad.'})

		if self.contacto_telefono and not FORMATO_TELEFONO.match(self.contacto_telefono):
			raise ValidationError({'contacto_telefono': 'El teléfono debe tener entre 6 y 20 caracteres: dígitos, espacios, guiones o paréntesis, con un + o un paréntesis inicial.'})
		if self.item_id:
			periodo = self.item.periodo
			periodo.verificar_editable()
			if self.fecha and not periodo.fecha_inicio <= timezone.localtime(self.fecha).date() <= periodo.fecha_termino:
				raise ValidationError({'fecha': f'La fecha de la actividad debe estar dentro del período «{periodo}».'})
			if self.fecha:
				fecha = timezone.localtime(self.fecha).date()
				# Regla 4: el cierre semanal impide ingresar actividades de una semana anterior, pero no corregir
				# una ya registrada (por ejemplo, una rechazada) mientras no se cambie el día de su fecha.
				validar_fecha_actividad(fecha, periodo, cierre_semanal=self._state.adding or self._cambia_el_dia(fecha))
				if self._state.adding and self.funcionario_autor_id:
					validar_limite_diario(self.funcionario_autor, fecha, periodo)
		self.cuenta_puntaje, self.motivo_sin_puntaje = evaluar_puntaje(self)

	def _cambia_el_dia(self, fecha):
		guardada = Actividad.objects.filter(pk=self.pk).values_list('fecha', flat=True).first()
		return guardada is None or timezone.localtime(guardada).date() != fecha

	def save(self, *args, **kwargs):
		self.generar_codigo_verificador()
		if not self._state.adding:
			guardado = Actividad.objects.filter(pk=self.pk).values_list('codigo_verificador', flat=True).first()
			if guardado and guardado != self.codigo_verificador:
				raise ValidationError('El código verificador de una actividad no se puede modificar.')
		super().save(*args, **kwargs)

	def cambiar_estado(self, nuevo_estado, anulando=False):
		if nuevo_estado not in dict(self.ESTADOS):
			raise ValidationError(f'Estado de actividad no válido: {nuevo_estado}.')
		if self.estado == 'aprobada' and nuevo_estado != 'aprobada' and not anulando:
			raise ValidationError('Una actividad aprobada ya suma al avance y no cambia de estado.')
		self.estado = nuevo_estado
		self.save(update_fields=['estado', 'actualizada'])

	def vincular_evidencia(self, evidencia):
		evidencia.actividad = self
		evidencia.save()
		evidencia.enviar_a_revision()

	@transaction.atomic
	def anular_aprobacion(self, motivo, verificador):
		"""CU-07.2 y RN-009: deja sin efecto la aprobación. La actividad deja de sumar al avance y los
		indicadores se recalculan hacia abajo. La validación aprobada original se conserva como historial."""
		if self.estado != 'aprobada':
			raise ValidationError('Solo se puede anular una actividad aprobada.')
		if not (motivo or '').strip():
			raise ValidationError('La anulación de una aprobación exige un motivo.')
		if self.item_id:
			self.item.periodo.verificar_editable()  # RN-013
		for evidencia in self.evidencias.filter(estado_revision='aprobada'):
			Validacion(evidencia=evidencia, funcionario_verificador=verificador).anular_evidencia(motivo)
		if self.estado == 'aprobada':  # aprobada sin evidencias, como las importadas del sistema anterior
			self.cambiar_estado('rechazada', anulando=True)
		self.actualizar_indicadores()

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
	ESTADOS_REVISION = [('pendiente', 'Pendiente de revisión'), ('aprobada', 'Aprobada'), ('rechazada', 'Rechazada'), ('antecedentes', 'Más antecedentes solicitados')]
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
	# La revisión aprueba, rechaza con motivo o solicita más antecedentes; quien registró corrige y vuelve a enviar.
	DECISIONES = [('aprobada', 'Aprobada'), ('rechazada', 'Rechazada'), ('antecedentes', 'Más antecedentes solicitados')]
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
	def _decidir(self, decision, observacion, anulando=False):
		"""RN-009: la decisión se refleja en la evidencia y en la actividad; solo «aprobada» aporta al avance."""
		self.decision = decision
		self.observacion = observacion
		self.version = Validacion.objects.filter(evidencia_id=self.evidencia_id).count() + 1
		self.save()
		self.evidencia.estado_revision = decision
		self.evidencia.save(update_fields=['estado_revision'])
		self.evidencia.actividad.cambiar_estado(decision, anulando=anulando)
		return self

	def anular_evidencia(self, motivo):
		"""CU-07.2: deja sin efecto una evidencia aprobada; la actividad ya no aporta al avance (RN-009)."""
		if not (motivo or '').strip():
			raise ValidationError('La anulación de una aprobación exige un motivo.')
		return self._decidir('rechazada', motivo, anulando=True)

	def aprobar_evidencia(self, observacion=None):
		return self._decidir('aprobada', observacion)

	def rechazar_evidencia(self, motivo):
		if not (motivo or '').strip():
			raise ValidationError('El rechazo de una evidencia exige un motivo.')
		return self._decidir('rechazada', motivo)

	def solicitar_antecedentes(self, detalle):
		"""Evaluación 3: el verificador pide más antecedentes; la actividad no suma hasta que se apruebe."""
		if not (detalle or '').strip():
			raise ValidationError('La solicitud de más antecedentes exige indicar qué falta.')
		return self._decidir('antecedentes', detalle)


class Compromiso(VersionOptimistaMixin, models.Model):
	# En la interfaz cada compromiso es una «tarea» del tubo de trabajo: las etiquetas van en femenino.
	ESTADOS = [('ingresado', 'Ingresada'), ('pendiente', 'Pendiente'), ('proceso', 'En proceso'), ('realizado', 'Realizada')]
	EJES = [
		('Seguridad', 'Seguridad'),
		('DISERCO', 'DISERCO'),
		('Gestión Social', 'Gestión Social'),
		('Organizaciones Comunitarias', 'Organizaciones Comunitarias'),
	]
	ORIGENES = [('interno', 'Interno'), ('externo', 'Externo')]
	# Evaluación 3: el Tubo de seguimiento (solicitudes) y el Tubo de cartas comparten estructura, permisos e historial.
	TIPOS = [('solicitud', 'Solicitud'), ('carta', 'Carta')]
	PREFIJOS_FOLIO = {'solicitud': 'AGR', 'carta': 'CAR'}
	# Ajuste 4: folio, eje, delegacion, descripcion y fecha_ingreso vienen de data/solicitudes.json.
	folio = models.CharField(max_length=30, unique=True)
	tipo = models.CharField(max_length=20, choices=TIPOS, default='solicitud')
	delegacion = models.ForeignKey(Delegacion, on_delete=models.PROTECT, related_name='compromisos')
	funcionario_responsable = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name='compromisos')
	item = models.ForeignKey('ItemMedible', on_delete=models.PROTECT, null=True, blank=True, related_name='compromisos')
	origen = models.CharField(max_length=255, choices=ORIGENES)
	solicitante = models.CharField(max_length=255)
	solicitante_rut = models.CharField(max_length=12, blank=True, validators=[validar_rut])
	solicitante_telefono = models.CharField(max_length=20, blank=True)
	vecino = models.ForeignKey('Vecino', on_delete=models.PROTECT, null=True, blank=True, related_name='compromisos')
	territorio = models.CharField(max_length=255)
	organizacion = models.ForeignKey(Organizacion, on_delete=models.PROTECT, null=True, blank=True, related_name='compromisos')
	gestion_interna = models.BooleanField(default=False)
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
		verbose_name = 'tarea del tubo de trabajo'
		verbose_name_plural = 'tareas del tubo de trabajo'
		indexes = [
			# Búsqueda dinámica del Tubo (por RUT o nombre del solicitante) y filtros por delegación, tipo y estado.
			models.Index(fields=['solicitante_rut'], name='compromiso_rut_idx'),
			models.Index(fields=['solicitante'], name='compromiso_solicitante_idx'),
			models.Index(fields=['delegacion', 'tipo', 'estado'], name='compromiso_deleg_tipo_est_idx'),
		]

	def __str__(self):
		return f'{self.folio} - {self.descripcion[:50]}'

	@classmethod
	def generar_folio(cls, tipo='solicitud'):
		"""Folio único generado por el sistema: AGR-AAAAMMDD-XXXXX (solicitud) o CAR-AAAAMMDD-XXXXX (carta)."""
		prefijo = cls.PREFIJOS_FOLIO.get(tipo, 'AGR')
		while True:
			folio = f'{prefijo}-{timezone.localdate():%Y%m%d}-{uuid.uuid4().hex[:5].upper()}'
			if not cls.objects.filter(folio=folio).exists():
				return folio

	def clean(self):
		super().clean()
		self.solicitante_rut = normalizar_rut(self.solicitante_rut)
		if self.vecino_id:
			# Autocompletado: si se eligió un vecino registrado, sus datos completan los que falten.
			self.solicitante_rut = self.solicitante_rut or self.vecino.rut
			self.solicitante = self.solicitante or self.vecino.nombre_completo
			self.solicitante_telefono = self.solicitante_telefono or self.vecino.telefono
		self.gestion_interna = self.origen == 'interno'
		if self.organizacion_id and self.delegacion_id and self.organizacion.delegacion_id != self.delegacion_id:
			raise ValidationError({'organizacion': 'La organización debe pertenecer a la delegación de la tarea.'})

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
			raise ValidationError(f'Estado de tarea no válido: {estado}.')
		if estado not in [permitido for permitido, _ in self.estados_permitidos()]:
			raise ValidationError(f'Transición no permitida: de «{etiquetas[self.estado]}» a «{etiquetas[estado]}».')

	def motivo_no_eliminable(self):
		"""CU-14.2: un incumplimiento (vencido y sin realizar) se conserva con su historial de seguimiento."""
		if self.vencido:
			return 'La tarea está vencida sin realizarse: se conserva con su historial de seguimiento.'
		return None

	def save(self, *args, **kwargs):
		self.solicitante_rut = normalizar_rut(self.solicitante_rut)
		if not self.folio:
			self.folio = self.generar_folio(self.tipo)
		super().save(*args, **kwargs)
		self.actualizar_indicadores()

	def delete(self, *args, **kwargs):
		motivo = self.motivo_no_eliminable()
		if motivo:
			raise ValidationError(motivo)
		resultado = super().delete(*args, **kwargs)
		self.actualizar_indicadores()
		return resultado

	def actualizar_indicadores(self):
		"""Ítem tipo «tubo»: crear, cambiar de estado o eliminar una tarea cambia el porcentaje realizado de su delegación."""
		metas = Meta.objects.filter(funcionario__delegacion_id=self.delegacion_id)
		# «Pendientes en el tubo» mira todas las tareas de la delegación, tengan o no un ítem asignado.
		afectadas = Q(item__tipo_calculo='tubo_pendientes')
		if self.item_id and self.item.tipo_calculo == 'tubo':
			afectadas |= Q(item_id=self.item_id)
		if self.tipo != 'solicitud':
			return []
		return Indicador.recalcular(metas.filter(afectadas))

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
			raise ValidationError('Una tarea realizada no se puede derivar.')
		anterior = self.funcionario_responsable
		self.funcionario_responsable = nuevo_responsable
		self.save(update_fields=['funcionario_responsable'])
		self.registrar_historial(autor, self.estado, f'Derivado de {anterior or "sin responsable"} a {nuevo_responsable}.')

	@transaction.atomic
	def cerrar_compromiso(self, resolucion, autor):
		if not (resolucion or '').strip():
			raise ValidationError('Cerrar una tarea exige una resolución.')
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
		verbose_name = 'medición de delegación'
		verbose_name_plural = 'mediciones de delegación'
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
		verbose_name = 'período'
		verbose_name_plural = 'períodos'
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
		incompletos = [f"{fila['cargo__nombre']} ({Decimal(fila['total']).quantize(DOS_DECIMALES)} %)" for fila in sumas if fila['total'] != 100]
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
	TIPOS_CALCULO = [
		('actividades', 'Conteo de actividades'),
		('tubo', '% del tubo realizado'),
		# Hoja SALON, ítem de Planificación y control: puntaje por tramos según la proporción de tareas pendientes.
		('tubo_pendientes', 'Pendientes en el tubo (por tramos)'),
	]
	TIPOS_TUBO = ('tubo', 'tubo_pendientes')
	cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT, related_name='items')
	periodo = models.ForeignKey(Periodo, on_delete=models.PROTECT, related_name='items')
	nombre = models.CharField(max_length=255)
	servicio = models.CharField(max_length=255, null=True, blank=True)
	ponderacion = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
	tipo_calculo = models.CharField(max_length=20, choices=TIPOS_CALCULO, default='actividades')

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
				raise ValidationError({'ponderacion': f'Las ponderaciones del cargo en el período sumarían {Decimal(total).quantize(DOS_DECIMALES)} %; no pueden superar 100 %.'})


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
		# Una asignación por funcionario e ítem (el ítem ya fija el cargo y el trimestre): sin metas duplicadas.
		constraints = [models.UniqueConstraint(fields=['item', 'funcionario'], name='meta_item_funcionario_unica')]

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

	def actividades_que_aportan(self, periodo=None):
		"""RN-003 y RN-009: actividades aprobadas del ítem, dentro del período, con una validación aprobada.

		Si el funcionario de la meta tiene delegación, solo cuentan las de esa delegación.
		"""
		periodo = periodo or self.item.periodo
		# Rango de instantes en hora de Chile; evita __date, que en MySQL exige tablas de zonas horarias.
		desde = timezone.make_aware(datetime.combine(periodo.fecha_inicio, time.min))
		hasta = timezone.make_aware(datetime.combine(periodo.fecha_termino + timedelta(days=1), time.min))
		actividades = Actividad.objects.filter(
			item=self.item,
			estado='aprobada',
			fecha__gte=desde,
			fecha__lt=hasta,
			evidencias__validaciones__decision='aprobada',
			cuenta_puntaje=True,
			tipo_accion='ejecucion',
		)
		if self.funcionario.delegacion_id:
			actividades = actividades.filter(delegacion_id=self.funcionario.delegacion_id)
		return actividades.distinct()


class Indicador(ControlPeriodoCerradoMixin, models.Model):
	SEMAFOROS = [('verde', 'Verde'), ('ambar', 'Ámbar'), ('rojo', 'Rojo')]
	# Hoja TUBO: «pendiente» es una tarea que todavía no se empieza (Ingresada o Pendiente); «En proceso» ya se atiende.
	ESTADOS_PENDIENTES = ('ingresado', 'pendiente')
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

	@classmethod
	def recalcular(cls, metas):
		"""CU-06.1: un Indicador nuevo para cada meta afectada; las de un período cerrado quedan congeladas (RN-013)."""
		metas = metas.select_related('funcionario', 'item__periodo')
		return [cls.generar(meta) for meta in metas if meta.item.periodo.estado != 'cerrado']

	def calcular_avance(self):
		"""RN-003 y RN-009: actividades aprobadas del ítem en el período que tienen una validación aprobada.

		Si el funcionario de la meta tiene delegación, solo cuentan las actividades de esa delegación.
		"""
		tipo = self.meta.item.tipo_calculo
		if tipo in ItemMedible.TIPOS_TUBO:
			# Solo el Tubo de trabajo (solicitudes): las cartas tienen su propio Tubo y no cambian este porcentaje.
			# «Soluciones de ingresos al tubo» mira las tareas del ítem; «Pendientes» mira todo el tubo de la delegación.
			tareas = self.tareas_del_tubo(item=self.meta.item if tipo == 'tubo' else None)
			self._tareas_ingresadas = tareas.count()
			if tipo == 'tubo':
				self.avance = tareas.filter(estado='realizado').count()
			else:
				pendientes = tareas.filter(estado__in=self.ESTADOS_PENDIENTES).count()
				# El avance es el porcentaje de tareas pendientes (sin iniciar) sobre las ingresadas.
				self.avance = (Decimal(pendientes) * 100 / self._tareas_ingresadas).quantize(DOS_DECIMALES) if self._tareas_ingresadas else Decimal('0')
		else:
			self.avance = self.meta.actividades_que_aportan(self.periodo).count()
		return self.avance

	def tareas_del_tubo(self, item=None):
		"""Tareas del Tubo de trabajo de la delegación de la meta, ingresadas en el período y con contacto (RF-050)."""
		tareas = Compromiso.objects.filter(
			tipo='solicitud',
			fecha_ingreso__gte=self.periodo.fecha_inicio,
			fecha_ingreso__lte=self.periodo.fecha_termino,
			delegacion=self.meta.funcionario.delegacion,
			solicitante__isnull=False,
			solicitante_telefono__isnull=False,
		).exclude(solicitante='').exclude(solicitante_telefono='')
		return tareas.filter(item=item) if item is not None else tareas

	@staticmethod
	def puntaje_por_pendientes(porcentaje_pendiente):
		"""Hoja SALON, ítem «Pendientes en tubo menor a 10 %»: hasta 10 % pendiente vale 100 %; hasta 50 %, 50 %; sobre eso, 0 %.

		En la planilla el resultado quedaba como texto («100%»); aquí es un número y entra al cálculo como cualquier ítem.
		"""
		if porcentaje_pendiente <= 10:
			return Decimal('100')
		if porcentaje_pendiente <= 50:
			return Decimal('50')
		return Decimal('0')

	def calcular_cumplimiento(self):
		"""RN-004 y RN-005: cumplimiento con tope configurable y cumplimiento ponderado."""
		tope = Decimal(self.periodo.obtener_parametro('maximo_cumplimiento', '120'))
		tipo = self.meta.item.tipo_calculo
		total = getattr(self, '_tareas_ingresadas', 0)
		if tipo == 'tubo':
			bruto = Decimal(self.avance) * 100 / Decimal(total) if total else Decimal('0')
		elif tipo == 'tubo_pendientes':
			# Sin tareas no hay proporción que medir: igual que el ítem del tubo, queda en 0 % hasta que haya ingresos.
			bruto = self.puntaje_por_pendientes(Decimal(self.avance)) if total else Decimal('0')
		else:
			bruto = self.meta.evaluar_progreso(self.avance)
		base = min(bruto, tope)
		aplicados = Ajuste.objects.filter(periodo=self.periodo, estado='aplicado')
		felicitaciones = aplicados.filter(tipo='felicitacion')
		reclamos = aplicados.filter(tipo='reclamo')
		if self.meta.funcionario_id:
			# Regla 8: cuentan los ajustes del funcionario y los de su delegación, si tiene una (sin delegación,
			# delegacion=None traería los ajustes dirigidos a cualquier otra persona).
			destinatario = Q(funcionario=self.meta.funcionario)
			if self.meta.funcionario.delegacion_id:
				destinatario |= Q(delegacion_id=self.meta.funcionario.delegacion_id)
			felicitaciones = felicitaciones.filter(destinatario)
			reclamos = reclamos.filter(destinatario)
		cantidad_felicitaciones = min(felicitaciones.count(), int(self.periodo.obtener_parametro('max_felicitaciones', '3')))
		self.ajuste = (
			Decimal(cantidad_felicitaciones) * Decimal(self.periodo.obtener_parametro('valor_felicitacion', '10'))
			- Decimal(reclamos.count()) * abs(Decimal(self.periodo.obtener_parametro('valor_reclamo', '-30')))
		)
		self.cumplimiento = max(Decimal('0'), min(tope, base + self.ajuste))
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
		verbose_name = 'historial de tarea'
		verbose_name_plural = 'historial de tareas'

	def __str__(self):
		return f'{self.compromiso.folio}: {self.estado_anterior or "inicio"} -> {self.estado_nuevo}'


class Ajuste(ControlPeriodoCerradoMixin, models.Model):
	TIPOS = [('felicitacion', 'Felicitación'), ('reclamo', 'Reclamo')]
	ORIGENES = [('usuario', 'Usuario'), ('delegacion', 'Delegación')]
	ESTADOS = [('informado', 'Informado'), ('aplicado', 'Aplicado'), ('rechazado', 'Rechazado')]
	tipo = models.CharField(max_length=20, choices=TIPOS)
	origen = models.CharField(max_length=20, choices=ORIGENES, default='usuario')
	emisor = models.CharField(max_length=255, blank=True)
	funcionario = models.ForeignKey(Funcionario, on_delete=models.PROTECT, null=True, blank=True, related_name='ajustes')
	delegacion = models.ForeignKey(Delegacion, on_delete=models.PROTECT, null=True, blank=True, related_name='ajustes')
	periodo = models.ForeignKey(Periodo, on_delete=models.PROTECT, related_name='ajustes')
	fecha = models.DateField(default=timezone.localdate)
	respaldo = models.FileField(
		upload_to='ajustes/%Y/%m/', null=True, blank=True,
		validators=[FileExtensionValidator(EXTENSIONES_EVIDENCIA), validar_tamano_evidencia],
	)
	observacion = models.TextField(blank=True)
	estado = models.CharField(max_length=20, choices=ESTADOS, default='informado')
	informado_por = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name='ajustes_informados')
	aplicado_por = models.ForeignKey(Funcionario, on_delete=models.PROTECT, null=True, blank=True, related_name='ajustes_aplicados')
	aplicado_en = models.DateTimeField(null=True, blank=True)

	def clean(self):
		super().clean()
		if bool(self.funcionario_id) == bool(self.delegacion_id):
			raise ValidationError('El ajuste debe dirigirse a un funcionario o a una delegación, pero no a ambos.')
		if not self.respaldo:
			raise ValidationError({'respaldo': 'El respaldo formal es obligatorio.'})
		if self.tipo == 'felicitacion' and not self.emisor.strip():
			raise ValidationError({'emisor': 'Indica quién emitió la felicitación.'})

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
		if self.estado in ('aplicado', 'rechazado'):
			self.actualizar_indicadores()

	def delete(self, *args, **kwargs):
		aplicado = self.estado == 'aplicado'
		resultado = super().delete(*args, **kwargs)
		if aplicado:
			self.actualizar_indicadores()
		return resultado

	def actualizar_indicadores(self):
		"""Regla 8: al aplicar o rechazar el ajuste se recalculan las metas de su destinatario (funcionario o delegación)."""
		metas = Meta.objects.filter(item__periodo_id=self.periodo_id)
		if self.funcionario_id:
			metas = metas.filter(funcionario_id=self.funcionario_id)
		else:
			metas = metas.filter(funcionario__delegacion_id=self.delegacion_id)
		return Indicador.recalcular(metas)


class Ausencia(ControlPeriodoCerradoMixin, models.Model):
	TIPOS = [
		('licencia', 'Licencia'),
		('vacaciones', 'Vacaciones'),
		('administrativo', 'Administrativo'),
		('compensatorio', 'Compensatorio'),
		('dia_libre', 'Día libre'),
		('emergencia', 'Emergencia'),
	]
	funcionario = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name='ausencias')
	periodo = models.ForeignKey(Periodo, on_delete=models.PROTECT, related_name='ausencias')
	tipo = models.CharField(max_length=20, choices=TIPOS)
	desde = models.DateField()
	hasta = models.DateField()
	observacion = models.TextField(blank=True)
	registrada_por = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name='ausencias_registradas')

	def clean(self):
		super().clean()
		if self.hasta < self.desde:
			raise ValidationError({'hasta': 'La fecha de término no puede ser anterior al inicio.'})
		if self.funcionario_id and self.desde and self.hasta:
			solapada = Ausencia.objects.filter(
				funcionario_id=self.funcionario_id, desde__lte=self.hasta, hasta__gte=self.desde,
			).exclude(pk=self.pk)
			if solapada.exists():
				raise ValidationError('La ausencia se superpone con otra ausencia existente.')

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
		self.actualizar_indicadores()

	def delete(self, *args, **kwargs):
		resultado = super().delete(*args, **kwargs)
		self.actualizar_indicadores()
		return resultado

	def actualizar_indicadores(self):
		"""Regla 9: la ausencia cambia lo esperado al día del funcionario; se recalculan sus metas del período."""
		return Indicador.recalcular(Meta.objects.filter(item__periodo_id=self.periodo_id, funcionario_id=self.funcionario_id))


class CasoSocial(models.Model):
	TIPOS = [
		('informe_social', 'Informe social'),
		('subsidio_ips', 'Subsidio IPS'),
		('pgu', 'PGU'),
		('suf', 'SUF'),
		('sap', 'SAP'),
		('derivacion', 'Derivación'),
		('otras_gestiones', 'Otras gestiones sociales'),
	]
	# Hoja LISTA de la matriz: «tipo de atención» agrupa los tipos y cada subtipo tiene su forma de entrega.
	GRUPOS = {
		'informe_social': 'Informes sociales',
		'subsidio_ips': 'Gestión de subsidios', 'pgu': 'Gestión de subsidios', 'suf': 'Gestión de subsidios', 'sap': 'Gestión de subsidios',
		'derivacion': 'Derivaciones',
		'otras_gestiones': 'Otras gestiones sociales',
	}
	SUBTIPOS_INFORME = {
		'Informe aporte económico': 'Dinero',
		'Informe aporte material': 'Material',
		'Informe institución': 'Documento',
	}
	FORMAS_SUBSIDIO = {'subsidio_ips': 'Documento', 'pgu': 'Aporte', 'suf': 'Aporte', 'sap': 'Aporte'}
	# Fila 19 de las hojas G SOC: plazos de respuesta de la atención social (en días corridos).
	PLAZO_PROGRAMAR_VISITA = 10
	PLAZO_INFORME_TRAS_VISITA = 4
	PLAZO_TOTAL_INFORME = 20
	MAX_REINGRESOS_INFORME = 2

	funcionario = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name='casos_sociales')
	vecino = models.ForeignKey('Vecino', on_delete=models.PROTECT, null=True, blank=True, related_name='casos_sociales')
	# Una gestión social puede ingresar o no al Tubo: si ingresa, queda vinculada a su tarea.
	compromiso = models.ForeignKey(Compromiso, on_delete=models.SET_NULL, null=True, blank=True, related_name='casos_sociales')
	nombre_usuario = models.CharField(max_length=255)
	telefono_usuario = models.CharField(max_length=20)
	etapa = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)])
	tipo = models.CharField(max_length=30, choices=TIPOS)
	subtipo = models.CharField(max_length=255, blank=True)
	observacion = models.TextField(blank=True)
	# Seguimiento de la hoja G SOC: ingreso, visita (programada y realizada), entrega del informe y reingresos.
	fecha_ingreso = models.DateField(default=timezone.localdate)
	requiere_visita = models.BooleanField(default=False)
	fecha_programada_visita = models.DateField(null=True, blank=True)
	fecha_visita = models.DateField(null=True, blank=True)
	fecha_entrega_informe = models.DateField(null=True, blank=True)
	reingresos_informe = models.PositiveSmallIntegerField(default=0)
	creado = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = 'gestión social'
		verbose_name_plural = 'gestiones sociales'
		ordering = ['-creado']

	def __str__(self):
		return f'{self.get_tipo_display()} - {self.nombre_usuario}'

	@property
	def grupo(self):
		return self.GRUPOS.get(self.tipo, '')

	@property
	def forma(self):
		"""Forma de entrega según la hoja LISTA (dinero, material, documento o aporte); vacía si no aplica."""
		if self.tipo == 'informe_social':
			return self.SUBTIPOS_INFORME.get(self.subtipo, '')
		return self.FORMAS_SUBSIDIO.get(self.tipo, '')

	def clean(self):
		super().clean()
		if self.etapa > 3:
			raise ValidationError({'etapa': 'Un caso social puede tener como máximo tres gestiones.'})
		if self.telefono_usuario and not FORMATO_TELEFONO.match(self.telefono_usuario):
			raise ValidationError({'telefono_usuario': 'El teléfono debe tener entre 6 y 20 caracteres: dígitos, espacios, guiones o paréntesis.'})
		if self.tipo == 'informe_social' and self.subtipo not in self.SUBTIPOS_INFORME:
			raise ValidationError({'subtipo': 'Elige el tipo de informe: ' + ', '.join(self.SUBTIPOS_INFORME) + '.'})
		if self.reingresos_informe > self.MAX_REINGRESOS_INFORME:
			raise ValidationError({'reingresos_informe': f'Un informe se reingresa como máximo {self.MAX_REINGRESOS_INFORME} veces.'})
		if self.reingresos_informe and not self.fecha_entrega_informe:
			raise ValidationError({'reingresos_informe': 'Solo se reingresa un informe que ya fue entregado.'})
		errores = {}
		if not self.requiere_visita:
			for campo in ('fecha_programada_visita', 'fecha_visita'):
				if getattr(self, campo):
					errores[campo] = 'Marca «Requiere visita» para registrar fechas de visita.'
		ingreso = self.fecha_ingreso
		if ingreso:
			for campo in ('fecha_programada_visita', 'fecha_visita', 'fecha_entrega_informe'):
				valor = getattr(self, campo)
				if valor and valor < ingreso and campo not in errores:
					errores[campo] = 'No puede ser anterior a la fecha de ingreso.'
		if self.fecha_visita and self.fecha_entrega_informe and self.fecha_entrega_informe < self.fecha_visita:
			errores.setdefault('fecha_entrega_informe', 'El informe no puede entregarse antes de la visita.')
		if errores:
			raise ValidationError(errores)

	def plazos(self):
		"""Plazos de respuesta de la hoja G SOC, con los días que tomó cada tramo y si cumple.

		En la planilla cada diferencia se calculaba en una columna aparte y se comparaba a ojo con la fila 19.
		Un tramo sin fecha final queda «en curso» y se mide hasta hoy.
		"""
		hoy = timezone.localdate()
		filas = []

		def tramo(nombre, desde, hasta, limite, exacto=False):
			if not desde:
				return
			dias = ((hasta or hoy) - desde).days
			cumple = dias == 0 if exacto else dias <= limite
			filas.append({
				'nombre': nombre, 'dias': dias, 'limite': limite, 'en_curso': hasta is None,
				'cumple': cumple, 'vencido': hasta is None and not cumple,
			})

		if self.requiere_visita:
			tramo('Ingreso → visita programada', self.fecha_ingreso, self.fecha_programada_visita, self.PLAZO_PROGRAMAR_VISITA)
			if self.fecha_programada_visita:
				tramo('Visita programada → visita realizada', self.fecha_programada_visita, self.fecha_visita, 0, exacto=self.fecha_visita is not None)
			if self.fecha_visita:
				tramo('Visita → entrega del informe', self.fecha_visita, self.fecha_entrega_informe, self.PLAZO_INFORME_TRAS_VISITA)
		if self.tipo == 'informe_social':
			tramo('Ingreso → entrega del informe', self.fecha_ingreso, self.fecha_entrega_informe, self.PLAZO_TOTAL_INFORME)
		return filas


class Comentario(models.Model):
	actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, null=True, blank=True, related_name='comentarios')
	compromiso = models.ForeignKey(Compromiso, on_delete=models.CASCADE, null=True, blank=True, related_name='comentarios')
	autor = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name='comentarios')
	contenido = models.TextField()
	creado = models.DateTimeField(auto_now_add=True)

	def clean(self):
		super().clean()
		if bool(self.actividad_id) == bool(self.compromiso_id):
			raise ValidationError('El comentario debe asociarse a una actividad o a una tarea.')


class Territorio(models.Model):
	"""Unidad territorial (sector, villa o localidad) de una delegación. Normaliza el texto libre de territorio."""
	nombre = models.CharField(max_length=255)
	delegacion = models.ForeignKey(Delegacion, on_delete=models.PROTECT, related_name='territorios')
	descripcion = models.TextField(blank=True)
	activo = models.BooleanField(default=True)

	class Meta:
		db_table = 'territorio'
		ordering = ['delegacion__nombre', 'nombre']
		verbose_name = 'territorio'
		verbose_name_plural = 'territorios'
		constraints = [models.UniqueConstraint(fields=['delegacion', 'nombre'], name='territorio_delegacion_nombre_unico')]

	def __str__(self):
		return f'{self.nombre} ({self.delegacion})'


class Vecino(models.Model):
	"""Persona de la comunidad atendida por la delegación. Su delegación se deduce de su territorio (sin duplicarla)."""
	rut = models.CharField(max_length=12, unique=True, validators=[validar_rut])
	nombres = models.CharField(max_length=150)
	apellidos = models.CharField(max_length=150)
	telefono = models.CharField(max_length=20, blank=True)
	email = models.EmailField(blank=True)
	direccion = models.CharField(max_length=255, blank=True)
	territorio = models.ForeignKey(Territorio, on_delete=models.PROTECT, related_name='vecinos')
	fecha_registro = models.DateTimeField(auto_now_add=True)
	activo = models.BooleanField(default=True)

	class Meta:
		db_table = 'vecino'
		ordering = ['apellidos', 'nombres']
		verbose_name = 'vecino'
		verbose_name_plural = 'vecinos'
		indexes = [models.Index(fields=['apellidos', 'nombres'], name='vecino_nombre_idx')]

	def __str__(self):
		return f'{self.nombre_completo} ({self.rut})'

	@property
	def nombre_completo(self):
		return f'{self.nombres} {self.apellidos}'.strip()

	@property
	def delegacion(self):
		return self.territorio.delegacion if self.territorio_id else None

	def clean(self):
		super().clean()
		self.rut = normalizar_rut(self.rut)
		if self.telefono and not FORMATO_TELEFONO.match(self.telefono):
			raise ValidationError({'telefono': 'El teléfono debe tener entre 6 y 20 caracteres: dígitos, espacios, guiones o paréntesis.'})

	def save(self, *args, **kwargs):
		self.rut = normalizar_rut(self.rut)
		super().save(*args, **kwargs)


class MembresiaOrganizacion(models.Model):
	"""Membresía de un vecino en una organización comunitaria y, si corresponde, su cargo en la directiva."""
	CARGOS = [
		('socio', 'Socio/a'), ('presidente', 'Presidente/a'), ('vicepresidente', 'Vicepresidente/a'),
		('secretario', 'Secretario/a'), ('tesorero', 'Tesorero/a'), ('director', 'Director/a'),
	]
	# Cargos de la directiva que solo una persona ocupa a la vez en cada organización.
	CARGOS_UNIPERSONALES = ('presidente', 'vicepresidente', 'secretario', 'tesorero')
	vecino = models.ForeignKey(Vecino, on_delete=models.PROTECT, related_name='membresias')
	organizacion = models.ForeignKey(Organizacion, on_delete=models.PROTECT, related_name='membresias')
	cargo = models.CharField(max_length=20, choices=CARGOS, default='socio')
	fecha_inicio = models.DateField(default=timezone.localdate)
	fecha_termino = models.DateField(null=True, blank=True)

	class Meta:
		db_table = 'membresia_organizacion'
		ordering = ['organizacion__nombre', 'cargo', 'vecino__apellidos']
		verbose_name = 'membresía o dirigencia'
		verbose_name_plural = 'membresías y dirigencias'
		constraints = [
			models.UniqueConstraint(fields=['vecino', 'organizacion', 'fecha_inicio'], name='membresia_vecino_org_inicio_unica'),
			models.CheckConstraint(condition=Q(fecha_termino__isnull=True) | Q(fecha_termino__gte=models.F('fecha_inicio')), name='membresia_fechas_validas'),
		]

	def __str__(self):
		return f'{self.vecino.nombre_completo} - {self.get_cargo_display()} en {self.organizacion}'

	@property
	def vigente(self):
		return self.fecha_termino is None or self.fecha_termino >= timezone.localdate()

	@property
	def es_dirigente(self):
		return self.cargo != 'socio'

	def _traslapadas(self, otras):
		"""Membresías de la misma organización cuyo período se cruza con el de esta."""
		otras = otras.filter(organizacion_id=self.organizacion_id).exclude(pk=self.pk)
		otras = otras.filter(Q(fecha_termino__isnull=True) | Q(fecha_termino__gte=self.fecha_inicio))
		if self.fecha_termino:
			otras = otras.filter(fecha_inicio__lte=self.fecha_termino)
		return otras

	def clean(self):
		super().clean()
		if not (self.vecino_id and self.organizacion_id and self.fecha_inicio):
			return
		if self.fecha_termino and self.fecha_termino < self.fecha_inicio:
			raise ValidationError({'fecha_termino': 'El término no puede ser anterior al inicio.'})
		if self._traslapadas(MembresiaOrganizacion.objects.filter(vecino_id=self.vecino_id)).exists():
			raise ValidationError('El vecino ya tiene una membresía en esta organización para esas fechas.')
		if self.cargo in self.CARGOS_UNIPERSONALES and self._traslapadas(MembresiaOrganizacion.objects.filter(cargo=self.cargo)).exists():
			raise ValidationError({'cargo': f'La organización ya tiene {self.get_cargo_display().lower()} vigente en esas fechas.'})


class Hito(models.Model):
	"""Hito territorial de la delegación (operativo, reunión con dirigentes, inauguración) con sus responsables."""
	ESTADOS = [('planificado', 'Planificado'), ('en_curso', 'En curso'), ('realizado', 'Realizado'), ('cancelado', 'Cancelado')]
	nombre = models.CharField(max_length=255)
	descripcion = models.TextField(blank=True)
	delegacion = models.ForeignKey(Delegacion, on_delete=models.PROTECT, related_name='hitos')
	territorio = models.ForeignKey(Territorio, on_delete=models.PROTECT, null=True, blank=True, related_name='hitos')
	fecha_programada = models.DateField()
	fecha_realizacion = models.DateField(null=True, blank=True)
	estado = models.CharField(max_length=20, choices=ESTADOS, default='planificado')
	responsables = models.ManyToManyField(Funcionario, through='ResponsableHito', related_name='hitos')
	creado = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'hito'
		ordering = ['-fecha_programada', 'nombre']
		verbose_name = 'hito'
		verbose_name_plural = 'hitos'
		indexes = [models.Index(fields=['delegacion', 'fecha_programada'], name='hito_deleg_fecha_idx')]

	def __str__(self):
		return f'{self.nombre} ({self.fecha_programada:%d-%m-%Y})'

	def clean(self):
		super().clean()
		if self.territorio_id and self.delegacion_id and self.territorio.delegacion_id != self.delegacion_id:
			raise ValidationError({'territorio': 'El territorio debe pertenecer a la delegación del hito.'})
		if self.estado == 'realizado' and not self.fecha_realizacion:
			raise ValidationError({'fecha_realizacion': 'Indica la fecha en que se realizó el hito.'})
		if self.fecha_realizacion and self.fecha_realizacion > timezone.localdate():
			raise ValidationError({'fecha_realizacion': 'La fecha de realización no puede estar en el futuro.'})


class ResponsableHito(models.Model):
	"""Funcionario responsable de un hito: uno principal y los de apoyo que hagan falta."""
	ROLES = [('principal', 'Responsable principal'), ('apoyo', 'Apoyo')]
	hito = models.ForeignKey(Hito, on_delete=models.CASCADE, related_name='asignaciones')
	funcionario = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name='asignaciones_hito')
	rol = models.CharField(max_length=20, choices=ROLES, default='apoyo')

	class Meta:
		db_table = 'responsable_hito'
		verbose_name = 'responsable de hito'
		verbose_name_plural = 'responsables de hitos'
		constraints = [models.UniqueConstraint(fields=['hito', 'funcionario'], name='responsable_hito_unico')]

	def __str__(self):
		return f'{self.funcionario} - {self.get_rol_display()} de {self.hito}'


class SubtipoAtencion(models.Model):
	"""Subtipo de un tipo de atención del catálogo (por ejemplo, «Alumbrado» dentro de «Solicitud ciudadana»)."""
	tipo = models.ForeignKey(Catalogo, on_delete=models.PROTECT, related_name='subtipos', limit_choices_to={'tipo': 'atencion'})
	nombre = models.CharField(max_length=255)
	activo = models.BooleanField(default=True)

	class Meta:
		db_table = 'subtipo_atencion'
		ordering = ['tipo__nombre', 'nombre']
		verbose_name = 'subtipo de atención'
		verbose_name_plural = 'subtipos de atención'
		constraints = [models.UniqueConstraint(fields=['tipo', 'nombre'], name='subtipo_atencion_tipo_nombre_unico')]

	def __str__(self):
		return f'{self.tipo.nombre} › {self.nombre}'

	def clean(self):
		super().clean()
		if self.tipo_id and self.tipo.tipo != 'atencion':
			raise ValidationError({'tipo': 'El subtipo debe colgar de un elemento del catálogo de tipo «Tipo de atención».'})


MENSAJE_AUDITORIA_SOLO_LECTURA = 'La auditoría es de solo lectura: sus registros no se modifican ni se eliminan.'


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
		verbose_name = 'registro de auditoría'
		verbose_name_plural = 'registros de auditoría'

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
