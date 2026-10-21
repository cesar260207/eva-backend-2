"""Permisos por rol. Reemplazan a PerfilUsuario.rol: los roles salen del Funcionario del usuario."""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect

from .models import Rol, UsuarioMaestro

ADMINISTRADOR = 'administrador'
COORDINADOR = 'coordinador'
DELEGADO = 'delegado'
FUNCIONARIO = 'funcionario'
VERIFICADOR = 'verificador'
CONSULTA = 'consulta'

# Los permisos consultan estos nombres: no se renombran ni se eliminan desde el mantenedor de roles.
ROLES_DEL_SISTEMA = (ADMINISTRADOR, COORDINADOR, DELEGADO, FUNCIONARIO, VERIFICADOR, CONSULTA)

MENSAJE_SIN_PERMISO = 'No tienes permiso para acceder a esta sección.'


def roles_de(user):
    """Nombres de los roles activos del usuario.

    Un superusuario o un UsuarioMaestro activo cuenta siempre como administrador.
    Un Funcionario con estado inactivo no aporta roles.
    """
    if not user.is_authenticated or not user.is_active:
        return frozenset()
    roles = set(Rol.objects.filter(funcionarios__usuario=user, funcionarios__estado=True).values_list('nombre_rol', flat=True))
    if user.is_superuser or UsuarioMaestro.objects.filter(usuario=user, estado=True).exists():
        roles.add(ADMINISTRADOR)
    return frozenset(roles)


def tiene_rol(user, *roles):
    """True si el usuario tiene al menos uno de los roles indicados."""
    return bool(roles_de(user) & set(roles))


def rol_requerido(*roles):
    """Decorador para vistas de función: exige sesión iniciada y alguno de los roles."""
    def decorador(vista):
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if not tiene_rol(request.user, *roles):
                messages.error(request, MENSAJE_SIN_PERMISO, fail_silently=True)
                return redirect('inicio')
            return vista(request, *args, **kwargs)
        return envoltura
    return decorador


class RolRequeridoMixin(LoginRequiredMixin):
    """Mixin para vistas de clase: define roles_permitidos y se comprueba antes de ejecutar la vista."""

    roles_permitidos = ()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not tiene_rol(request.user, *self.roles_permitidos):
            messages.error(request, MENSAJE_SIN_PERMISO, fail_silently=True)
            return redirect('inicio')
        # Sin sesión, LoginRequiredMixin redirige al login.
        return super().dispatch(request, *args, **kwargs)
