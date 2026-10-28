"""Backend de autenticación: el de Django con una regla más sobre los permisos."""
from django.contrib.auth.backends import ModelBackend

from .models import Funcionario


class PerfilBackend(ModelBackend):
    """Autentica igual que ModelBackend, pero un usuario cuyo Funcionario está desactivado no
    recibe los permisos de su perfil (grupo) ni los propios, aunque su cuenta siga activa."""

    def _get_permissions(self, user_obj, obj, from_name):
        if user_obj.is_active and Funcionario.objects.filter(usuario=user_obj, estado=False).exists():
            return set()
        return super()._get_permissions(user_obj, obj, from_name)
