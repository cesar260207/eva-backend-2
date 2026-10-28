"""Utilidades compartidas por los módulos de pruebas (no se descubre como prueba porque no empieza con «test»)."""
import shutil
import tempfile
from datetime import date, datetime, timedelta

from django.contrib.auth.models import User
from django.test import override_settings
from django.utils import timezone

from .models import (
    Actividad, Cargo, Catalogo, Compromiso, Delegacion, Evidencia, Funcionario, FuncionarioRol, ItemMedible, Periodo, Rol,
)
from .permisos import asignar_perfil

CLAVE_PRUEBA = 'clave-segura'


def crear_funcionario(username, *roles, cargo=None, delegacion=None):
    """Usuario de Django con su Funcionario, roles y el perfil que corresponde a esos roles, como lo deja el
    mantenedor de funcionarios (la migración 0010 crea los seis roles y la 0015 los tres perfiles)."""
    usuario = User.objects.create_user(username, password=CLAVE_PRUEBA)
    cargo = cargo or Cargo.objects.get_or_create(nombre='Profesional territorial')[0]
    funcionario = Funcionario.objects.create(usuario=usuario, identificador_institucional=username, nombre=username, cargo=cargo, delegacion=delegacion)
    for rol in roles:
        FuncionarioRol.objects.create(funcionario=funcionario, rol=Rol.objects.get(nombre_rol=rol))
    asignar_perfil(usuario)
    return usuario


class EscenarioBase:
    """Datos mínimos comunes a las pruebas unitarias de operación: un período abierto con un ítem, dos delegaciones,
    un funcionario autor y un verificador. Se usa como mixin de un TestCase y se arma con crear_escenario()."""

    def crear_escenario(self):
        media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media, ignore_errors=True)
        ajuste = override_settings(MEDIA_ROOT=media)
        ajuste.enable()
        self.addCleanup(ajuste.disable)

        self.cargo = Cargo.objects.create(nombre='Profesional territorial')
        self.centro = Delegacion.objects.create(nombre='Centro')
        self.rural = Delegacion.objects.create(nombre='Rural')
        self.periodo = Periodo.objects.create(nombre='Septiembre 2026', fecha_inicio=date(2026, 9, 1), fecha_termino=date(2026, 9, 30), estado='abierto')
        self.item = ItemMedible.objects.create(cargo=self.cargo, periodo=self.periodo, nombre='Atención territorial', ponderacion=100)
        self.catalogo = Catalogo.objects.create(codigo='AT-BASE', nombre='Operativo en terreno', tipo='atencion')
        self.usuario_autor = crear_funcionario('autor-base', 'funcionario', cargo=self.cargo, delegacion=self.centro)
        self.usuario_verificador = crear_funcionario('verificador-base', 'verificador', cargo=self.cargo)
        self.autor = self.usuario_autor.funcionario
        self.verificador = self.usuario_verificador.funcionario
        self.fecha_valida = timezone.make_aware(datetime(2026, 9, 10, 10, 0))

    def nueva_actividad(self, **cambios):
        datos = {
            'funcionario_autor': self.autor, 'delegacion': self.centro, 'item': self.item, 'catalogo': self.catalogo,
            'fecha': self.fecha_valida, 'solicitud_problema': 'Solicitud', 'accion': 'Acción',
        }
        datos.update(cambios)
        return Actividad.objects.create(**datos)

    def nueva_evidencia(self, actividad, **cambios):
        return Evidencia.objects.create(actividad=actividad, funcionario_autor=actividad.funcionario_autor, archivo_vinculo='evidencias/2026/09/respaldo.pdf', **cambios)

    def nuevo_compromiso(self, dias=60, folio='UNI-1', **cambios):
        datos = {
            'folio': folio, 'delegacion': self.centro, 'funcionario_responsable': self.autor, 'solicitante': 'Junta de vecinos',
            'territorio': 'Centro', 'descripcion': 'Poda de árboles', 'origen': 'externo',
            'fecha_comprometida': timezone.localdate() + timedelta(days=dias),
        }
        datos.update(cambios)
        return Compromiso.objects.create(**datos)
