from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError


class Delegacion(models.Model):
	nombre = models.CharField(max_length=120, unique=True)
	territorio = models.CharField(max_length=180)
	enfasis = models.TextField()
	activa = models.BooleanField(default=True)

	class Meta:
		ordering = ['nombre']
		verbose_name = 'delegación'
		verbose_name_plural = 'delegaciones'

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

	def __str__(self):
		return f'{self.codigo} - {self.descripcion[:50]}'


class Evidencia(models.Model):
	actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, related_name='evidencias')
	archivo = models.FileField(upload_to='evidencias/%Y/%m/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'pdf'])])
	comentario = models.TextField(blank=True)
	aprobada = models.BooleanField(null=True, blank=True)
	revisada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='evidencias_revisadas')
	creada = models.DateTimeField(auto_now_add=True)


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


class HistorialCompromiso(models.Model):
	compromiso = models.ForeignKey(Compromiso, on_delete=models.CASCADE, related_name='historial')
	autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
	estado_anterior = models.CharField(max_length=20)
	estado_nuevo = models.CharField(max_length=20)
	observacion = models.TextField(blank=True)
	fecha = models.DateTimeField(auto_now_add=True)


class Auditoria(models.Model):
	usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
	accion = models.CharField(max_length=80)
	entidad = models.CharField(max_length=80)
	identificador = models.CharField(max_length=80)
	detalle = models.JSONField(default=dict)
	fecha = models.DateTimeField(auto_now_add=True)
