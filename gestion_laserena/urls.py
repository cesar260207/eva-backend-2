"""Rutas del proyecto.

No se publica Django Admin: toda la administración se hace desde las pantallas propias
(mantenedores, perfiles y auditoría en delegaciones_app). La recuperación de contraseña usa las
vistas de django.contrib.auth con plantillas propias en templates/registration/.
"""
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from delegaciones_app.cuentas import RestablecerContrasena, SolicitarRecuperacion

urlpatterns = [
    path('', include('delegaciones_app.urls')),
    path('gestion/', include('gestion_app.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Recuperación de contraseña: solicitud -> correo con enlace y token -> nueva contraseña -> confirmación.
    path('recuperar/', SolicitarRecuperacion.as_view(), name='password_reset'),
    path('recuperar/enviado/', auth_views.PasswordResetDoneView.as_view(extra_context={'minutos': settings.PASSWORD_RESET_TIMEOUT // 60}), name='password_reset_done'),
    path('recuperar/<uidb64>/<token>/', RestablecerContrasena.as_view(), name='password_reset_confirm'),
    path('recuperar/listo/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
