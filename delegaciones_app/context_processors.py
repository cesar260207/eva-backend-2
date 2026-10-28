from .crud import PERMISOS_DE_MANTENEDORES
from .permisos import ADMINISTRADOR, COORDINADOR, delegacion_propia, perfil_de, tiene_rol


def permisos(request):
    """Variables de permisos para las plantillas: el menú de Administración aparece si el perfil
    del usuario tiene permiso para ver al menos un mantenedor."""
    user = request.user
    return {
        'puede_administrar': any(user.has_perm(permiso) for permiso in PERMISOS_DE_MANTENEDORES),
        'perfil_usuario': perfil_de(user),
        # Coordinación gestiona delegados; un delegado ve el acceso directo a su delegación.
        'es_coordinacion': tiene_rol(user, ADMINISTRADOR, COORDINADOR),
        'mi_delegacion': delegacion_propia(user),
    }
