from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import json
import uuid


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
