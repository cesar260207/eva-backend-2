from .permisos import ADMINISTRADOR, COORDINADOR, tiene_rol


def permisos(request):
    """Variables de permisos para las plantillas (por ejemplo, el menú de Administración)."""
    return {'puede_administrar': tiene_rol(request.user, ADMINISTRADOR, COORDINADOR)}
