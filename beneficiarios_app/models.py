"""Modelos del módulo de beneficiarios.

Evento          -> una actividad de infancia de un año (Navidad 2026, Día del Niño 2027...).
UnidadMunicipal -> quién ingresa la solicitud: las seis delegaciones, Gabinete, DIDECO y Depto. de la Familia.
Inscripcion     -> un menor inscrito en un evento. Un RUT se inscribe una sola vez por evento.
"""
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from delegaciones_app.models import Delegacion, Funcionario, Organizacion
from delegaciones_app.rut import normalizar_rut, validar_rut


def anio_actual():
    return timezone.localdate().year


def rut_canonico(valor):
    """RUT sin puntos, con guion y sin ceros a la izquierda: «09.876.543-2» y «9876543-2» son el mismo niño."""
    rut = normalizar_rut(valor)
    if not rut:
        return ''
    cuerpo, dv = rut.rsplit('-', 1)
    return f"{cuerpo.lstrip('0') or '0'}-{dv}"


class Evento(models.Model):
    TIPOS = [
        ('navidad', 'Navidad'),
        ('dia_nino', 'Día del Niño'),
        ('aniversario', 'Aniversario'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPOS)
    anio = models.PositiveIntegerField('año', default=anio_actual)
    inscripciones_abiertas = models.BooleanField(default=True, help_text='Con las inscripciones cerradas nadie puede inscribir ni modificar.')
    descripcion = models.CharField('descripción', max_length=255, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-anio', 'tipo']
        verbose_name = 'evento'
        verbose_name_plural = 'eventos'
        constraints = [models.UniqueConstraint(fields=['tipo', 'anio'], name='evento_tipo_anio_unico')]

    def __str__(self):
        return f'{self.get_tipo_display()} {self.anio}'


class UnidadMunicipal(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    # Las delegaciones territoriales se enlazan con la Delegacion del núcleo: sus funcionarios quedan en esta unidad.
    delegacion = models.OneToOneField(Delegacion, on_delete=models.SET_NULL, null=True, blank=True, related_name='unidad_municipal')
    # Unidades sin delegación (Gabinete, DIDECO, Depto. de la Familia): funcionarios asignados a mano.
    funcionarios = models.ManyToManyField(Funcionario, blank=True, related_name='unidades_municipales')
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'unidad municipal'
        verbose_name_plural = 'unidades municipales'

    def __str__(self):
        return self.nombre


validar_telefono = RegexValidator(r'^9\d{8}$', 'Ingresa un celular de 9 dígitos que comience con 9 (ej: 912345678).')
validar_folio = RegexValidator(r'^\d{5,12}$', 'El folio de la Cartola RSH tiene solo números (entre 5 y 12 dígitos).')


class Inscripcion(models.Model):
    RANGOS_EDAD = [
        ('0-2', '0 - 2 años'),
        ('3-5', '3 - 5 años'),
        ('6-8', '6 - 8 años'),
        ('9-10', '9 - 10 años'),
        ('11+', '11 años o más'),
    ]
    GENEROS = [('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro'), ('N', 'Prefiero no decir')]
    TRAMOS_RSH = [(t, f'{t}%') for t in (40, 50, 60, 70, 80, 90, 100)]

    evento = models.ForeignKey(Evento, on_delete=models.PROTECT, related_name='inscripciones')
    unidad = models.ForeignKey(UnidadMunicipal, on_delete=models.PROTECT, related_name='inscripciones', verbose_name='unidad municipal')
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='inscripciones_beneficiarios')
    correo_registro = models.EmailField('correo de quien registra', blank=True)
    nombre = models.CharField('nombre del menor', max_length=200)
    rut = models.CharField('RUT del menor', max_length=12, validators=[validar_rut])
    rango_edad = models.CharField('rango de edad', max_length=5, choices=RANGOS_EDAD)
    genero = models.CharField('género', max_length=1, choices=GENEROS)
    folio_rsh = models.CharField('N° de folio Cartola RSH', max_length=12, validators=[validar_folio])
    tramo_rsh = models.PositiveSmallIntegerField('tramo RSH', choices=TRAMOS_RSH)
    organizacion = models.ForeignKey(Organizacion, on_delete=models.PROTECT, null=True, blank=True, related_name='inscripciones_beneficiarios', verbose_name='JJ.VV. u organización')
    organizacion_otra = models.CharField('otra agrupación', max_length=255, blank=True)
    telefono = models.CharField('teléfono de contacto', max_length=9, validators=[validar_telefono])
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = 'inscripción'
        verbose_name_plural = 'inscripciones'
        constraints = [models.UniqueConstraint(fields=['evento', 'rut'], name='inscripcion_rut_unico_por_evento')]

    def __str__(self):
        return f'{self.nombre} ({self.rut}) - {self.evento}'

    @property
    def organizacion_nombre(self):
        return self.organizacion.nombre if self.organizacion_id else self.organizacion_otra

    def save(self, *args, **kwargs):
        self.rut = rut_canonico(self.rut)
        self.nombre = ' '.join(self.nombre.split())
        super().save(*args, **kwargs)
