"""Utilidades compartidas por los módulos de pruebas (no se descubre como prueba porque no empieza con «test»)."""
from django.contrib.auth.models import User

from .models import Cargo, Funcionario, FuncionarioRol, Rol

CLAVE_PRUEBA = 'clave-segura'


def crear_funcionario(username, *roles, cargo=None, delegacion=None):
    """Usuario de Django con su Funcionario y roles (la migración 0010 crea los seis roles del sistema)."""
    usuario = User.objects.create_user(username, password=CLAVE_PRUEBA)
    cargo = cargo or Cargo.objects.get_or_create(nombre='Profesional territorial')[0]
    funcionario = Funcionario.objects.create(usuario=usuario, identificador_institucional=username, nombre=username, cargo=cargo, delegacion=delegacion)
    for rol in roles:
        FuncionarioRol.objects.create(funcionario=funcionario, rol=Rol.objects.get(nombre_rol=rol))
    return usuario
