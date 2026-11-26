"""
Django settings for gestion_laserena project.

Basado en 'django-admin startproject', ajustado para usar Django 5.2 LTS
con variables de entorno y MySQL (ver README.md, sección "Instalacion").

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import sys
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Variables de entorno: todo dato sensible (SECRET_KEY, credenciales de BD,
# ALLOWED_HOSTS, etc.) se lee desde un archivo .env que NO se sube a git
# (ver .gitignore). Se distribuye un .env.example como plantilla.
env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', 'testserver'])


# Application definition

# Sin django.contrib.admin: la administración se hace desde las pantallas propias del sistema.
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'delegaciones_app',
    'gestion_app',
    # Inscripción de beneficiarios de actividades de infancia (reemplaza el Google Form de fin de año).
    'beneficiarios_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Evaluación 3: quien tiene una contraseña temporal solo puede cambiarla o salir.
    'delegaciones_app.middleware.CambioContrasenaObligatorioMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
if not DEBUG:
    # En desarrollo, runserver sirve directamente los archivos de STATICFILES_DIRS.
    # WhiteNoise solo debe interceptar /static/ en despliegues con collectstatic.
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Cabeceras para reducir MIME sniffing, filtración de URLs y carga en iframes.
# HSTS y cookies Secure dependen de HTTPS y se configuran en el despliegue TLS.
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'
# Con HTTPS (producción) se activan desde el .env: cookies solo por HTTPS, redirección y HSTS.
SESSION_COOKIE_SECURE = env.bool('COOKIES_SEGURAS', default=False)
CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=0)
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

ROOT_URLCONF = 'gestion_laserena.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'delegaciones_app.context_processors.permisos',
            ],
        },
    },
]

WSGI_APPLICATION = 'gestion_laserena.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
#
# El motor se define con DB_ENGINE en el .env:
#   - "mysql"  (por defecto): usado en la instancia EC2, administrable con phpMyAdmin.
#   - "sqlite": util solo para pruebas rapidas en un equipo sin MySQL instalado.

if env('DB_ENGINE', default='mysql') == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': env('DB_NAME'),
            'USER': env('DB_USER'),
            'PASSWORD': env('DB_PASSWORD'),
            'HOST': env('DB_HOST', default='127.0.0.1'),
            'PORT': env('DB_PORT', default='3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        }
    }


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

# Las contraseñas se guardan con PBKDF2-SHA256 y sal (hasher por defecto de Django). Solo al ejecutar las pruebas
# se usa un hasher rápido, para que la suite no tarde por el costo deliberado de PBKDF2.
EJECUTANDO_PRUEBAS = len(sys.argv) > 1 and sys.argv[1] in ('test', 'plan_pruebas', 'protocolo_pruebas')
if EJECUTANDO_PRUEBAS:
    PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'es-cl'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
# STATIC_ROOT: destino de "python manage.py collectstatic" para servir
# los estáticos en la instancia EC2 (fuera del modo runserver de desarrollo).
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
# ModelBackend con una regla: un funcionario desactivado no recibe los permisos de su perfil.
AUTHENTICATION_BACKENDS = ['delegaciones_app.backends.PerfilBackend']

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'panel'  # cada perfil llega a su propio panel
LOGOUT_REDIRECT_URL = 'inicio'

# Cierre de sesión (RNF-004, OWASP A07). Por defecto Django mantiene la sesión dos semanas, aunque se cierre el
# navegador. Aquí la sesión vence tras SESSION_INACTIVIDAD_MINUTOS sin actividad (30 por defecto): cada página
# abierta renueva el plazo (SESSION_SAVE_EVERY_REQUEST) y la cookie no sobrevive al cierre del navegador.
SESSION_COOKIE_AGE = env.int('SESSION_INACTIVIDAD_MINUTOS', default=30) * 60
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True

# Correo para la recuperación de contraseña. Sin EMAIL_BACKEND en el .env los correos se muestran
# en la consola (útil en desarrollo); en EC2 se usa SMTP, por ejemplo Gmail con una contraseña de aplicación.
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_TIMEOUT = env.int('EMAIL_TIMEOUT', default=20)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER or 'no-responder@sgr.local')
# Vigencia del enlace de recuperación, en segundos (1 hora por defecto).
PASSWORD_RESET_TIMEOUT = env.int('PASSWORD_RESET_TIMEOUT', default=3600)

# Bloqueo por intentos fallidos de ingreso (fuerza bruta): tras LOGIN_MAX_INTENTOS fallos seguidos con el mismo usuario
# desde la misma IP, el ingreso se bloquea LOGIN_BLOQUEO_MINUTOS minutos.
LOGIN_MAX_INTENTOS = env.int('LOGIN_MAX_INTENTOS', default=5)
LOGIN_BLOQUEO_MINUTOS = env.int('LOGIN_BLOQUEO_MINUTOS', default=15)

# El contador de intentos vive en la caché. Con Gunicorn hay varios procesos (workers) y la caché en memoria es propia de
# cada uno: el bloqueo se saltaría repartiendo los intentos. Por eso se usa una caché en archivos, compartida por todos
# los procesos del servidor. En las pruebas se mantiene la caché en memoria de Django.
if not EJECUTANDO_PRUEBAS:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': env('CACHE_DIR', default=str(BASE_DIR / '.cache')),
        }
    }

# Reglas configurables sin tocar el código (RNF-015): tamaño máximo de una evidencia en MB (RNF-017)
# días de anticipación con que un compromiso se marca como próximo a vencer (RF-019)
# y días sin registrar actividades a partir de los cuales se emite una alerta (RF-037).
EVIDENCIA_TAMANO_MAXIMO_MB = env.int('EVIDENCIA_TAMANO_MAXIMO_MB', default=5)
COMPROMISO_DIAS_ALERTA = env.int('COMPROMISO_DIAS_ALERTA', default=3)
ALERTA_DIAS_SIN_REGISTRO = env.int('ALERTA_DIAS_SIN_REGISTRO', default=7)
if EJECUTANDO_PRUEBAS:
    # La caché en memoria dura todo el proceso de pruebas: sin este ajuste, los intentos fallidos de unas pruebas
    # bloquearían el ingreso en otras. Las pruebas del bloqueo fijan su propio máximo con override_settings.
    LOGIN_MAX_INTENTOS = 10_000
