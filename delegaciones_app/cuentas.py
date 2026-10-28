"""Recuperación de contraseña por correo electrónico.

Se apoya en las vistas de django.contrib.auth: PasswordResetView genera el token con
default_token_generator (firmado con SECRET_KEY, de un solo uso y con vencimiento
PASSWORD_RESET_TIMEOUT) y envía el enlace; PasswordResetConfirmView valida el token y pide la
nueva contraseña. Aquí solo se ajustan las plantillas y se deja el cambio en la auditoría.
"""
from django.conf import settings
from django.contrib.auth import views as auth_views

from .models import Auditoria


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
    """Valida el token del enlace y guarda la nueva contraseña; el cambio queda auditado."""

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        Auditoria.registrar_evento(form.user, 'restablecer_contrasena', 'Usuario', form.user.username, None, {'medio': 'correo electrónico'})
        return respuesta
