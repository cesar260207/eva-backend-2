"""Permisos por rol y por perfil.

Perfil = nivel de permisos; rol = función y alcance. Los roles salen del Funcionario del usuario y
definen su función en el flujo de trabajo (quién registra, quién verifica, qué delegación ve). Los
perfiles son los grupos de Django y siguen la jerarquía Administrador > Coordinador > Delegado >
Funcionario (migraciones 0015 y 0018): sus permisos deciden el acceso a los mantenedores, la revisión
de evidencias, la auditoría y los perfiles. En la pauta de la evaluación, Coordinador y Delegado son
los perfiles intermedios («Supervisor») y Funcionario el mínimo («Administrativo»).
"""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect

from .models import Auditoria, Funcionario, Rol, UsuarioMaestro

ADMINISTRADOR = 'administrador'
COORDINADOR = 'coordinador'
DELEGADO = 'delegado'
FUNCIONARIO = 'funcionario'
VERIFICADOR = 'verificador'
CONSULTA = 'consulta'

# Los permisos consultan estos nombres: no se renombran ni se eliminan desde el mantenedor de roles.
ROLES_DEL_SISTEMA = (ADMINISTRADOR, COORDINADOR, DELEGADO, FUNCIONARIO, VERIFICADOR, CONSULTA)

MENSAJE_SIN_PERMISO = 'No tienes permiso para acceder a esta sección.'

# Perfiles de acceso: grupos de Django con sus permisos (migraciones 0015 y 0018), de mayor a menor.
PERFIL_ADMINISTRADOR = 'Administrador'
PERFIL_COORDINADOR = 'Coordinador'
PERFIL_DELEGADO = 'Delegado'
PERFIL_FUNCIONARIO = 'Funcionario'
PERFILES = (PERFIL_ADMINISTRADOR, PERFIL_COORDINADOR, PERFIL_DELEGADO, PERFIL_FUNCIONARIO)

# Rol que aporta cada perfil de alcance global: así ver todas las delegaciones sigue al grupo asignado.
# El perfil Delegado no aporta alcance: un delegado ve solo la delegación de su ficha.
ROL_DEL_PERFIL = {PERFIL_ADMINISTRADOR: ADMINISTRADOR, PERFIL_COORDINADOR: COORDINADOR}

# Quién revisa evidencias (aprobar, rechazar, anular): estos roles, cada uno dentro de su ámbito, y solo
# con un perfil que tenga el permiso de registrar validaciones (Administrador, Coordinador o Delegado).
ROLES_REVISORES = (ADMINISTRADOR, COORDINADOR, DELEGADO, VERIFICADOR)
PERMISO_REVISAR = 'delegaciones_app.add_validacion'


def roles_de(user):
    """Nombres de los roles activos del usuario.

    Un superusuario o un UsuarioMaestro activo cuenta siempre como administrador, y los perfiles
    Administrador y Coordinador aportan los roles administrador y coordinador.
    Un Funcionario con estado inactivo no aporta roles, ni los de su perfil.
    """
    if not user.is_authenticated or not user.is_active:
        return frozenset()
    roles = set(Rol.objects.filter(funcionarios__usuario=user, funcionarios__estado=True).values_list('nombre_rol', flat=True))
    if user.is_superuser or UsuarioMaestro.objects.filter(usuario=user, estado=True).exists():
        roles.add(ADMINISTRADOR)
    if not Funcionario.objects.filter(usuario=user, estado=False).exists():
        for perfil in user.groups.filter(name__in=ROL_DEL_PERFIL).values_list('name', flat=True):
            roles.add(ROL_DEL_PERFIL[perfil])
    return frozenset(roles)


def perfil_sugerido(roles):
    """Perfil que corresponde a un conjunto de nombres de rol: el de mayor alcance."""
    if ADMINISTRADOR in roles:
        return PERFIL_ADMINISTRADOR
    if COORDINADOR in roles:
        return PERFIL_COORDINADOR
    if DELEGADO in roles or VERIFICADOR in roles:
        return PERFIL_DELEGADO
    return PERFIL_FUNCIONARIO


def asignar_perfil(usuario, perfil=None):
    """Deja al usuario en un solo perfil. Sin perfil indicado, se deduce de sus roles."""
    if perfil is None:
        perfil = perfil_sugerido(set(Rol.objects.filter(funcionarios__usuario=usuario).values_list('nombre_rol', flat=True)))
    nombre = perfil.name if isinstance(perfil, Group) else perfil
    usuario.groups.remove(*Group.objects.filter(name__in=PERFILES).exclude(name=nombre))
    usuario.groups.add(Group.objects.get(name=nombre))


def perfil_de(user):
    """Perfil con que se presenta el panel del usuario: el de mayor alcance que tenga."""
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return PERFIL_ADMINISTRADOR
    grupos = set(user.groups.filter(name__in=PERFILES).values_list('name', flat=True))
    for perfil in PERFILES:
        if perfil in grupos:
            return perfil
    return perfil_sugerido(roles_de(user))


def tiene_rol(user, *roles):
    """True si el usuario tiene al menos uno de los roles indicados."""
    return bool(roles_de(user) & set(roles))


def puede_ver_todo(user):
    """Administración y coordinación ven los registros de todas las delegaciones."""
    return tiene_rol(user, ADMINISTRADOR, COORDINADOR)


# Quién agrega tareas al tubo de trabajo: administración y coordinación, para cualquier delegación y eligiendo
# al responsable; delegados y funcionarios, para su propia delegación y a su cargo. Verificador y consulta no.
ROLES_CREAN_TAREAS = (ADMINISTRADOR, COORDINADOR, DELEGADO, FUNCIONARIO)


def puede_crear_tarea(user):
    return tiene_rol(user, *ROLES_CREAN_TAREAS)


# Eliminar actividades es una operación crítica: solo los perfiles con este permiso (Coordinador y Administrador).
# Delegado y Funcionario corrigen sus errores con «Modificar actividad».
PERMISO_ELIMINAR_ACTIVIDAD = 'delegaciones_app.delete_actividad'


def puede_eliminar_actividad(user):
    return user.has_perm(PERMISO_ELIMINAR_ACTIVIDAD)


def puede_revisar(user):
    """Aprueba, rechaza o anula evidencias: un rol revisor con el permiso de su perfil. El perfil Funcionario
    no tiene ese permiso, así que nunca revisa aunque tenga asignado un rol revisor."""
    return tiene_rol(user, *ROLES_REVISORES) and user.has_perm(PERMISO_REVISAR)


def delegacion_propia(user):
    """Delegación a la que se limita lo que ve el usuario: la suya si no tiene alcance global
    (un delegado de Centro ve solo Centro). None si ve todas o si no tiene delegación asignada."""
    if puede_ver_todo(user):
        return None
    funcionario = funcionario_de(user)
    return funcionario.delegacion if funcionario and funcionario.delegacion_id else None


def funcionario_de(user):
    """Funcionario activo del usuario (con su delegación y cargo) o None."""
    if not user.is_authenticated:
        return None
    return Funcionario.objects.select_related('delegacion', 'cargo').filter(usuario=user, estado=True).first()


def registrar_acceso_denegado(request, entidad='Acceso', identificador=None, motivo='rol insuficiente'):
    """CU-26.1: un intento de acceso sin autorización queda en la auditoría (solo si el usuario está identificado)."""
    if request.user.is_authenticated:
        Auditoria.registrar_evento(
            request.user, 'acceso_denegado', entidad, identificador or request.path,
            None, {'metodo': request.method, 'ruta': request.path, 'motivo': motivo},
        )


def rol_requerido(*roles):
    """Decorador para vistas de función: exige sesión iniciada y alguno de los roles."""
    def decorador(vista):
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if not tiene_rol(request.user, *roles):
                registrar_acceso_denegado(request)
                messages.error(request, MENSAJE_SIN_PERMISO, fail_silently=True)
                return redirect('inicio')
            return vista(request, *args, **kwargs)
        return envoltura
    return decorador


def _denegar(request, motivo):
    registrar_acceso_denegado(request, motivo=motivo)
    messages.error(request, MENSAJE_SIN_PERMISO, fail_silently=True)
    return redirect('inicio')


def permiso_requerido(*permisos):
    """Decorador para vistas de función: exige sesión iniciada y al menos uno de los permisos de Django."""
    def decorador(vista):
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if not any(request.user.has_perm(permiso) for permiso in permisos):
                return _denegar(request, 'permiso insuficiente')
            return vista(request, *args, **kwargs)
        return envoltura
    return decorador


class PermisoRequeridoMixin(LoginRequiredMixin):
    """Mixin para vistas de clase: exige el permiso de Django de `permiso_requerido` (por ejemplo
    'delegaciones_app.change_periodo'). Los permisos llegan al usuario por su grupo (perfil)."""

    permiso_requerido = ''

    def get_permiso_requerido(self):
        return self.permiso_requerido

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.has_perm(self.get_permiso_requerido()):
            return _denegar(request, 'permiso insuficiente')
        # Sin sesión, LoginRequiredMixin redirige al login.
        return super().dispatch(request, *args, **kwargs)


class RolRequeridoMixin(LoginRequiredMixin):
    """Mixin para vistas de clase: define roles_permitidos y se comprueba antes de ejecutar la vista."""

    roles_permitidos = ()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not tiene_rol(request.user, *self.roles_permitidos):
            registrar_acceso_denegado(request)
            messages.error(request, MENSAJE_SIN_PERMISO, fail_silently=True)
            return redirect('inicio')
        # Sin sesión, LoginRequiredMixin redirige al login.
        return super().dispatch(request, *args, **kwargs)
