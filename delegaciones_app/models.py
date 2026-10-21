from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import json
import uuid

DOS_DECIMALES = Decimal('0.01')


class Delegacion(models.Model):
	nombre = models.CharField(max_length=255, unique=True)
	territorio = models.CharField(max_length=180)
	enfasis = models.TextField()
	activa = models.BooleanField(default=True)
	# Campos del diseño. En la Etapa 4 reemplazan a activa y territorio.
	estado = models.BooleanField(default=True)
	ambito = models.CharField(max_length=255, null=True, blank=True)

	class Meta:
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

	def obtener_cumplimiento_global(self, periodo):
		"""Promedio del último indicador de cada meta de sus funcionarios, ponderado por el ponderador de la meta."""
		ultimos = {}
		indicadores = Indicador.objects.filter(periodo=periodo, meta__funcionario__delegacion=self).select_related('meta').order_by('fecha_calculo')
		for indicador in indicadores:
			ultimos[indicador.meta_id] = indicador
		total_ponderador = sum(indicador.meta.ponderador for indicador in ultimos.values())
		if not total_ponderador:
			return Decimal('0.00')
		total_ponderado = sum(indicador.ponderacion for indicador in ultimos.values())
		return (total_ponderado * 100 / total_ponderador).quantize(DOS_DECIMALES)


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


class PerfilUsuario(models.Model):
	ROLES = [
		('administrador', 'Administrador'),
		('coordinador', 'Coordinador'),
		('delegado', 'Delegado'),
		('funcionario', 'Funcionario'),
		('verificador', 'Verificador'),
		('consulta', 'Consulta'),
	]
	usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
	rol = models.CharField(max_length=20, choices=ROLES, default='consulta')
	delegacion = models.ForeignKey(Delegacion, on_delete=models.PROTECT, null=True, blank=True, related_name='perfiles')
	cargo = models.CharField(max_length=120, blank=True)

	def __str__(self):
		return f'{self.usuario.get_full_name() or self.usuario.username} - {self.get_rol_display()}'


class CatalogoItem(models.Model):
	CATEGORIAS = [('actividad', 'Actividad'), ('servicio', 'Servicio'), ('atencion', 'Tipo de atención'), ('item', 'Ítem de medición')]
	categoria = models.CharField(max_length=20, choices=CATEGORIAS)
	codigo = models.CharField(max_length=40)
	nombre = models.CharField(max_length=160)
	area = models.CharField(max_length=120, blank=True)
	activo = models.BooleanField(default=True)

	class Meta:
		constraints = [models.UniqueConstraint(fields=['categoria', 'codigo'], name='catalogo_categoria_codigo_unico')]
		ordering = ['categoria', 'nombre']

	def __str__(self):
		return f'{self.get_categoria_display()}: {self.nombre}'


class PeriodoMedicion(models.Model):
	ESTADOS = [('borrador', 'Borrador'), ('abierto', 'Abierto'), ('cerrado', 'Cerrado')]
	nombre = models.CharField(max_length=120, unique=True)
	inicio = models.DateField()
	termino = models.DateField()
	estado = models.CharField(max_length=20, choices=ESTADOS, default='borrador')
	version_parametros = models.PositiveIntegerField(default=1)
	umbral_colectivo = models.DecimalField(max_digits=5, decimal_places=2, default=80)
	maximo_cumplimiento = models.DecimalField(max_digits=5, decimal_places=2, default=150)

	def clean(self):
		if self.termino < self.inicio:
			raise ValidationError('La fecha de término no puede ser anterior al inicio.')

	@property
	def dias_computables(self):
		return (self.termino - self.inicio).days + 1

	def __str__(self):
		return self.nombre


class Actividad(models.Model):
	ESTADOS = [('borrador', 'Borrador'), ('pendiente', 'Pendiente de revisión'), ('aprobada', 'Aprobada'), ('rechazada', 'Rechazada')]
	codigo = models.CharField(max_length=32, unique=True, editable=False)
	funcionario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='actividades')
	delegacion = models.ForeignKey(Delegacion, on_delete=models.PROTECT, related_name='actividades')
	fecha = models.DateField()
	tipo_atencion = models.CharField(max_length=100)
	descripcion = models.TextField()
	accion = models.TextField()
	item_medicion = models.CharField(max_length=160)
	contacto = models.CharField(max_length=160, blank=True)
	telefono = models.CharField(max_length=40, blank=True)
	estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
	creada = models.DateTimeField(auto_now_add=True)
	actualizada = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-fecha', '-creada']

	def save(self, *args, **kwargs):
		if not self.codigo:
			self.codigo = f'EVD-{timezone.localdate():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}'
		super().save(*args, **kwargs)

	def __str__(self):
		return f'{self.codigo} - {self.descripcion[:50]}'


class Evidencia(models.Model):
	actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, related_name='evidencias')
	archivo = models.FileField(upload_to='evidencias/%Y/%m/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'pdf'])])
	comentario = models.TextField(blank=True)
	aprobada = models.BooleanField(null=True, blank=True)
	revisada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='evidencias_revisadas')
	creada = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		archivo = self.archivo.name if self.archivo else 'sin archivo'
		return f'{self.actividad.codigo} - {archivo}'


class Compromiso(models.Model):
	ESTADOS = [('ingresado', 'Ingresado'), ('pendiente', 'Pendiente'), ('proceso', 'En proceso'), ('realizado', 'Realizado')]
	EJES = [
		('Seguridad', 'Seguridad'),
		('DISERCO', 'DISERCO'),
		('Gestión Social', 'Gestión Social'),
		('Organizaciones Comunitarias', 'Organizaciones Comunitarias'),
	]
	folio = models.CharField(max_length=30, unique=True)
	delegacion = models.ForeignKey(Delegacion, on_delete=models.PROTECT, related_name='compromisos')
	responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='compromisos')
	solicitante = models.CharField(max_length=160)
	territorio = models.CharField(max_length=160)
	eje = models.CharField(max_length=40, choices=EJES, default='Gestión Social')
	descripcion = models.TextField()
	fecha_comprometida = models.DateField()
	fecha_ingreso = models.DateField(default=timezone.localdate)
	estado = models.CharField(max_length=20, choices=ESTADOS, default='ingresado')
	observacion = models.TextField(blank=True)
	creado = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-fecha_comprometida', '-creado']

	def __str__(self):
		return f'{self.folio} - {self.descripcion[:50]}'

	@property
	def vencido(self):
		from django.utils import timezone
		return self.estado != 'realizado' and self.fecha_comprometida < timezone.localdate()


class MetaMedicion(models.Model):
	delegacion = models.ForeignKey(Delegacion, on_delete=models.PROTECT, related_name='metas')
	nombre = models.CharField(max_length=160)
	objetivo = models.PositiveIntegerField(validators=[MinValueValidator(1)])
	avance = models.PositiveIntegerField(default=0)
	ponderador = models.DecimalField(max_digits=5, decimal_places=2, default=0)
	periodo_inicio = models.DateField()
	periodo_termino = models.DateField()
	tope_cumplimiento = models.DecimalField(max_digits=5, decimal_places=2, default=150)
	activa = models.BooleanField(default=True)

	def clean(self):
		if self.periodo_inicio and self.periodo_termino and self.periodo_termino < self.periodo_inicio:
			raise ValidationError('El término no puede ser anterior al inicio.')
		if self.ponderador is not None and self.ponderador > 100:
			raise ValidationError('El ponderador no puede superar 100%.')
	@property
	def avance_calculado(self):
		return self.delegacion.actividades.filter(
			fecha__range=(self.periodo_inicio, self.periodo_termino),
			item_medicion=self.nombre,
			estado='aprobada',
		).count()

	@property
	def cumplimiento(self):
		avance = self.avance_calculado
		return min((avance / self.objetivo) * 100, float(self.tope_cumplimiento))

	@property
	def resultado_ponderado(self):
		return float(self.ponderador) * self.cumplimiento / 100

	def __str__(self):
		return f'{self.delegacion.nombre} - {self.nombre}'


class MedicionDelegacion(models.Model):
	ESTADOS = [('verde', 'Verde'), ('amarillo', 'Amarillo'), ('rojo', 'Rojo')]
	delegacion = models.ForeignKey(Delegacion, on_delete=models.PROTECT, related_name='mediciones')
	cumplimiento = models.DecimalField(max_digits=5, decimal_places=2)
	meta = models.DecimalField(max_digits=5, decimal_places=2)
	fecha_datos = models.DateField()
	estado_reportado = models.CharField(max_length=12, choices=ESTADOS)
	observacion = models.TextField(blank=True)

	class Meta:
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

	def calcular_cumplimiento(self):
		"""RN-004 y RN-005: cumplimiento con tope configurable y cumplimiento ponderado."""
		tope = Decimal(self.periodo.obtener_parametro('maximo_cumplimiento', '150'))
		self.cumplimiento = min(self.meta.evaluar_progreso(self.avance), tope)
		self.ponderacion = (self.meta.ponderador * self.cumplimiento / 100).quantize(DOS_DECIMALES)
		return self.cumplimiento

	def actualizar_semaforo(self, fecha=None):
		"""RN-008: verde si alcanza lo esperado al día, ámbar si llega al 60 % de lo esperado, rojo si no."""
		esperado = self.periodo.porcentaje_esperado(fecha)
		if self.cumplimiento >= esperado:
			self.semaforo = 'verde'
		elif self.cumplimiento >= esperado * Decimal('0.6'):
			self.semaforo = 'ambar'
		else:
			self.semaforo = 'rojo'
		return self.semaforo


class HistorialCompromiso(models.Model):
	compromiso = models.ForeignKey(Compromiso, on_delete=models.CASCADE, related_name='historial')
	autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
	estado_anterior = models.CharField(max_length=20)
	estado_nuevo = models.CharField(max_length=20)
	observacion = models.TextField(blank=True)
	fecha = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'{self.compromiso.folio}: {self.estado_anterior or "inicio"} -> {self.estado_nuevo}'


class Auditoria(models.Model):
	usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
	accion = models.CharField(max_length=80)
	entidad = models.CharField(max_length=255)
	identificador = models.CharField(max_length=80)
	detalle = models.JSONField(default=dict)
	fecha = models.DateTimeField(auto_now_add=True)
	# Campos del diseño. En la Etapa 4 reemplazan a usuario, accion, identificador y detalle.
	funcionario = models.ForeignKey(Funcionario, on_delete=models.PROTECT, null=True, blank=True, related_name='auditorias')
	usuario_maestro = models.ForeignKey(UsuarioMaestro, on_delete=models.PROTECT, null=True, blank=True, related_name='auditorias')
	evento = models.CharField(max_length=255, null=True, blank=True)
	identificador_registro = models.CharField(max_length=255, null=True, blank=True)
	valor_anterior = models.TextField(null=True, blank=True)
	valor_nuevo = models.TextField(null=True, blank=True)

	def __str__(self):
		return f'{self.fecha:%Y-%m-%d %H:%M} - {self.accion} - {self.entidad} {self.identificador}'

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
			# Doble escritura temporal: los campos antiguos son obligatorios hasta la Etapa 4.
			usuario=usuario,
			accion=accion,
			identificador=str(identificador),
		)
