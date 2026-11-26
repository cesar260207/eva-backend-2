"""Cambio obligatorio de la contraseña temporal en el primer ingreso (Evaluación 3).

Una cuenta creada o restablecida por la administración recibe una contraseña temporal y queda marcada con
Funcionario.debe_cambiar_contrasena. Mientras la marca siga activa, cualquier página redirige a «Cambiar
contraseña»: solo se permiten esa página, cerrar la sesión y los archivos estáticos.
"""
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

from .models import Funcionario


class CambioContrasenaObligatorioMiddleware:
    RUTAS_PERMITIDAS = ('cambiar_contrasena', 'logout')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._debe_cambiar(request):
            return redirect('cambiar_contrasena')
        return self.get_response(request)

    def _debe_cambiar(self, request):
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            return False
        ruta = request.path
        if ruta.startswith(('/' + settings.STATIC_URL.lstrip('/'), '/' + settings.MEDIA_URL.lstrip('/'))):
            return False
        if ruta in {reverse(nombre) for nombre in self.RUTAS_PERMITIDAS}:
            return False
        return Funcionario.objects.filter(usuario=user, debe_cambiar_contrasena=True).exists()
