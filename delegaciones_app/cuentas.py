"""Cuentas de acceso: recuperación de contraseña, contraseña temporal, cambio obligatorio y bloqueo por intentos.

Recuperación: se apoya en las vistas de django.contrib.auth. PasswordResetView genera el token con
default_token_generator (firmado con SECRET_KEY, de un solo uso y con vencimiento PASSWORD_RESET_TIMEOUT) y envía
el enlace; PasswordResetConfirmView valida el token y pide la nueva contraseña.

Contraseña temporal (Evaluación 3): la administración crea la cuenta (o restablece su clave) con una contraseña
temporal generada al azar; el funcionario debe cambiarla en su primer ingreso (ver middleware.py).

Bloqueo por intentos: tras LOGIN_MAX_INTENTOS fallos con el mismo usuario desde la misma IP, el ingreso queda
bloqueado LOGIN_BLOQUEO_MINUTOS minutos, aunque la contraseña siguiente sea correcta.
"""
import hashlib
import secrets
import string

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy

from .models import Auditoria, Funcionario

ALFABETO_TEMPORAL = string.ascii_letters + string.digits


def generar_contrasena_temporal(largo=12):
    """Contraseña temporal aleatoria (módulo secrets) con al menos una mayúscula, una minúscula y un dígito."""
    while True:
        clave = ''.join(secrets.choice(ALFABETO_TEMPORAL) for _ in range(largo))
        if any(c.islower() for c in clave) and any(c.isupper() for c in clave) and any(c.isdigit() for c in clave):
            return clave


class SolicitarRecuperacion(auth_views.PasswordResetView):
    """Pide el correo y, si pertenece a una cuenta activa, le envía el enlace con el token.

    Responde lo mismo exista o no el correo, para no revelar qué cuentas existen.
    """

    email_template_name = 'registration/password_reset_email.txt'
    html_email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'

    def form_valid(self, form):
        self.extra_email_context = {'minutos': settings.PASSWORD_RESET_TIMEOUT // 60}
        return super().form_valid(form)


class RestablecerContrasena(auth_views.PasswordResetConfirmView):
    """Valida el token del enlace y guarda la nueva contraseña; el cambio queda auditado.

    Quien recupera su contraseña por correo ya eligió una propia: se quita la marca de contraseña temporal.
    """

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        Funcionario.objects.filter(usuario=form.user).update(debe_cambiar_contrasena=False)
        Auditoria.registrar_evento(form.user, 'restablecer_contrasena', 'Usuario', form.user.username, None, {'medio': 'correo electrónico'})
        return respuesta


class CambiarContrasena(auth_views.PasswordChangeView):
    """Cambio de contraseña con sesión iniciada. Es obligatorio si la cuenta tiene una contraseña temporal."""

    template_name = 'registration/cambiar_contrasena.html'
    success_url = reverse_lazy('panel')

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['obligatorio'] = Funcionario.objects.filter(usuario=self.request.user, debe_cambiar_contrasena=True).exists()
        return contexto

    def form_valid(self, form):
        respuesta = super().form_valid(form)  # update_session_auth_hash: la sesión sigue abierta con la clave nueva
        temporal = Funcionario.objects.filter(usuario=self.request.user, debe_cambiar_contrasena=True).update(debe_cambiar_contrasena=False)
        Auditoria.registrar_evento(self.request.user, 'cambiar_contrasena', 'Usuario', self.request.user.username, None,
                                   {'contrasena_temporal_reemplazada': bool(temporal)})
        messages.success(self.request, 'Tu contraseña se cambió correctamente.')
        return respuesta


# Bloqueo por intentos fallidos

def _clave_intentos(username, ip):
    base = f'{(username or "").strip().lower()}|{ip or ""}'
    return 'sgr-login-' + hashlib.sha256(base.encode()).hexdigest()


def _ip(request):
    return request.META.get('REMOTE_ADDR', '') if request else ''


MENSAJE_BLOQUEO = 'Demasiados intentos fallidos. Por seguridad, el ingreso con este usuario quedó bloqueado por %(minutos)s minutos.'


class FormularioIngreso(AuthenticationForm):
    """AuthenticationForm con bloqueo temporal tras varios intentos fallidos seguidos (fuerza bruta)."""

    error_messages = {
        **AuthenticationForm.error_messages,
        'bloqueado': MENSAJE_BLOQUEO,
    }

    def clean(self):
        username = self.data.get('username', '')
        clave = _clave_intentos(username, _ip(self.request))
        if cache.get(clave, 0) >= settings.LOGIN_MAX_INTENTOS:
            raise ValidationError(self.error_messages['bloqueado'], code='bloqueado', params={'minutos': settings.LOGIN_BLOQUEO_MINUTOS})
        try:
            datos = super().clean()
        except ValidationError:
            intentos = cache.get(clave, 0) + 1
            cache.set(clave, intentos, settings.LOGIN_BLOQUEO_MINUTOS * 60)
            if intentos >= settings.LOGIN_MAX_INTENTOS:
                Auditoria.objects.create(evento='bloqueo_ingreso', entidad='Usuario', identificador_registro=username[:255],
                                         valor_nuevo=f'{intentos} intentos fallidos desde {_ip(self.request) or "IP desconocida"}')
            raise
        cache.delete(clave)
        return datos
