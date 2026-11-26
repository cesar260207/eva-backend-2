# Guía técnica de implementación del SGR

Guía para que una tercera persona instale, configure, ejecute, respalde y recupere el Sistema de Gestión de Resultados (SGR)
sin explicaciones adicionales. El despliegue en AWS EC2 (Gunicorn, Nginx, phpMyAdmin) está paso a paso en el
[README](../README.md#despliegue-en-aws-ec2).

## 1. Versiones

| Componente | Versión | Dónde se fija |
|---|---|---|
| Python | 3.13.14 en desarrollo; 3.14 en GitHub Actions (mínimo 3.11) | `.github/workflows/pruebas.yml` |
| Django | 5.2.19 (rama LTS 5.2) | `requirements.txt` (`Django>=5.2,<5.3`) |
| django-environ | 0.14.0 | `requirements.txt` |
| whitenoise | 6.12.0 | `requirements.txt` |
| openpyxl | 3.1.5 (exportación a Excel) | `requirements.txt` |
| mysqlclient | 2.2.x (solo con MySQL) | `requirements.txt` |
| gunicorn | 23 o superior (solo Linux) | `requirements.txt` |
| Motor de base de datos | MySQL 8.0.16+ o MariaDB 10.5+ en producción (mínimos de Django 5.2; MySQL aplica las restricciones CHECK desde 8.0.16); SQLite 3 para desarrollo y pruebas | `.env` (`DB_ENGINE`) |
| Bootstrap | 5 (archivos locales en `static/bootstrap/`, sin CDN) | `static/` |

Herramientas de desarrollo (no van al servidor): `coverage` y `pip-audit` (`requirements-dev.txt`).

## 2. Instalación paso a paso

### 2.1 Linux o macOS

```bash
git clone <url-del-repositorio> sgr && cd sgr
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt            # con MySQL: antes, sudo apt install pkg-config libmysqlclient-dev
cp .env.example .env                       # y completar los valores (sección 3)
```

### 2.2 Windows (PowerShell)

```powershell
git clone <url-del-repositorio> sgr; cd sgr
py -3.13 -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env               # y completar los valores (sección 3)
$env:PYTHONIOENCODING = "utf-8"           # para ver bien los acentos en la consola (incidencia 2)
```

### 2.3 Base de datos

Con MySQL (producción), crear la base y su usuario (la contraseña la elige el administrador; nunca se versiona):

```sql
CREATE DATABASE gestion_laserena CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'gestion_user'@'localhost' IDENTIFIED BY '<contraseña>';
GRANT ALL PRIVILEGES ON gestion_laserena.* TO 'gestion_user'@'localhost';
```

Con SQLite (desarrollo rápido) basta `DB_ENGINE=sqlite` en el `.env`: la base `db.sqlite3` se crea sola.

### 2.4 Migraciones y datos iniciales

```bash
python manage.py migrate                                  # crea tablas, restricciones, índices, perfiles y permisos
python manage.py seed_demo --password "<clave-demo>"      # datos ficticios de demostración (repetible, no duplica)
python manage.py check && python manage.py makemigrations --check --dry-run
```

`migrate` deja listos los cuatro perfiles (Administrador, Coordinador, Delegado, Profesional) con sus permisos, los roles
del sistema y los territorios deducidos de las organizaciones ya cargadas (migración 0031). La migración 0030 se detiene
con un mensaje claro si encuentra metas duplicadas, en vez de dejar la base a medias.

Para crear el primer administrador real sin datos demo, usar la pantalla de funcionarios con la cuenta demo
`admin.demo` o `python manage.py createsuperuser`.

### 2.5 Correo (recuperación de contraseña)

Sin `EMAIL_BACKEND` los correos se imprimen en la consola (desarrollo). En producción, con Gmail y una contraseña de
aplicación (pasos en el README, «Configurar el correo»):

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<cuenta>@gmail.com
EMAIL_HOST_PASSWORD=<contraseña de aplicación>
DEFAULT_FROM_EMAIL=SGR La Serena <<cuenta>@gmail.com>
```

Probar con `python manage.py sendtestemail <correo>` (caso manual CP-05 del protocolo).

### 2.6 Ejecución

```bash
python manage.py runserver                 # desarrollo: http://127.0.0.1:8000/
gunicorn gestion_laserena.wsgi:application # producción (detrás de Nginx; ver README)
python manage.py collectstatic --noinput   # producción: estáticos servidos por WhiteNoise
```

## 3. Variables de entorno

Todas se documentan en [`.env.example`](../.env.example). El `.env` real no se versiona (`.gitignore`).

| Variable | Obligatoria | Uso |
|---|---|---|
| `SECRET_KEY` | Sí | Firma de sesiones y tokens de recuperación. Generar una propia y larga. |
| `DEBUG` | Sí | `False` en producción. |
| `ALLOWED_HOSTS` | Sí | Dominios o IP desde los que se atiende. |
| `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Sí con MySQL | Conexión a la base. |
| `EMAIL_*`, `DEFAULT_FROM_EMAIL`, `PASSWORD_RESET_TIMEOUT` | En producción | Correo de recuperación y vigencia del enlace (3600 s). |
| `SESSION_INACTIVIDAD_MINUTOS` | No (30) | Cierre de sesión por inactividad. |
| `LOGIN_MAX_INTENTOS`, `LOGIN_BLOQUEO_MINUTOS` | No (5 y 15) | Bloqueo de ingreso por intentos fallidos. |
| `CACHE_DIR` | No (`.cache/` del proyecto) | Caché en archivos compartida por los procesos de Gunicorn (guarda el contador de intentos). El usuario del servicio debe poder escribir en ella. |
| `COOKIES_SEGURAS`, `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`, `CSRF_TRUSTED_ORIGINS` | Con HTTPS | Cookies solo por HTTPS, redirección y HSTS. |
| `EVIDENCIA_TAMANO_MAXIMO_MB`, `COMPROMISO_DIAS_ALERTA`, `ALERTA_DIAS_SIN_REGISTRO` | No | Reglas configurables. |

## 4. Arquitectura

Aplicación web monolítica Django (patrón MTV): navegador → Nginx → Gunicorn → Django → MySQL. Las reglas de negocio están
en los modelos y en módulos de servicio; las vistas solo coordinan permisos, formularios y auditoría.

| Módulo | Responsabilidad |
|---|---|
| `gestion_laserena/` | Configuración (`settings.py` lee el `.env`), rutas raíz, WSGI. |
| `delegaciones_app/models.py` | Entidades, restricciones e invariantes (período cerrado, aprobada bloqueada, folios, RUT). |
| `delegaciones_app/reglas.py` | Reglas del cliente: cierre semanal, límite diario, puntaje, ausencias. |
| `delegaciones_app/permisos.py` | Perfiles (grupos con permisos) y roles (alcance por delegación). |
| `delegaciones_app/cuentas.py`, `middleware.py` | Recuperación, contraseña temporal, cambio obligatorio y bloqueo por intentos. |
| `delegaciones_app/crud.py` | 17 mantenedores genéricos con ámbito por delegación y auditoría. |
| `delegaciones_app/tubo.py` | Ingreso opcional de actividades y gestiones sociales al Tubo. |
| `delegaciones_app/views.py` | Actividades, evidencias, revisión, Tubo de trabajo y de cartas, gestiones sociales, búsqueda de vecinos. |
| `delegaciones_app/rut.py` | Normalización y validación de RUT (módulo 11). |
| `gestion_app/views.py`, `graficos.py` | Paneles por perfil, dashboard con gráficos, semáforo, resumen, informes. |
| `templates/`, `static/` | Interfaz (Bootstrap local, `sgr.css`, `sgr.js`, `sgr-formularios.js`). |

### Rutas agregadas en la Evaluación 3

| Ruta | Función |
|---|---|
| `/cuenta/cambiar-contrasena/` | Cambio de contraseña (obligatorio con contraseña temporal). |
| `/agenda/?tubo=carta` | Tubo de cartas (el Tubo de trabajo es `/agenda/`). Acepta `q`, `responsable`, `estado`, `plazo`, `desde`, `hasta` y `parcial=1` (búsqueda al escribir). |
| `/casos-sociales/`, `/casos-sociales/<id>/editar/` | Lista y edición de gestiones sociales. |
| `/vecinos/buscar/?rut=` o `?id=` | Datos de un vecino para autocompletar (JSON, con permiso y dentro del ámbito). |
| `/gestion/tablero/` | Dashboard con gráficos y filtros (período, delegación, funcionario, fechas). |
| `/administracion/territorios/`, `vecinos/`, `membresias/`, `hitos/`, `subtipos/` | Mantenedores nuevos. |

## 5. Estructura del repositorio

```
gestion_laserena/        configuración del proyecto
delegaciones_app/        modelos, reglas, vistas, formularios, migraciones, pruebas (test_*.py) y comandos
  management/commands/   seed_demo, respaldo, protocolo_pruebas, plan_pruebas, importar_organizaciones, ...
gestion_app/             paneles, dashboard, semáforo e informes
templates/ static/       interfaz
data/                    cargas iniciales sin datos personales (JSON)
docs/                    documentación, protocolo de pruebas, trazabilidad, resultados (CSV)
scripts/                 respaldo.sh (MySQL) y medición de tiempos
```

## 6. Perfiles de acceso

| Perfil | Alcance | Puede |
|---|---|---|
| Administrador | Todas las delegaciones | Todo, incluidos usuarios, perfiles y auditoría. |
| Coordinador | Todas las delegaciones | Mantenedores operativos (también territorios, vecinos, membresías, hitos y subtipos), revisión, ajustes, reabrir tareas realizadas. |
| Delegado | Su delegación | Revisar evidencias (aprobar, rechazar, pedir antecedentes), informar ajustes y ausencias, mantener vecinos, membresías e hitos. |
| Profesional | Su delegación | Registrar actividades, evidencias, tareas, gestiones sociales y vecinos; consultar el Tubo y modificar solo lo propio no cerrado. |

## 7. Respaldo y recuperación

**Portable (MySQL o SQLite):**

```bash
python manage.py respaldo --conservar 7          # respaldos/sgr_AAAAMMDD_HHMMSS.zip (datos.json + media/)
```

Restaurar en una base vacía:

```bash
python manage.py migrate
unzip sgr_AAAAMMDD_HHMMSS.zip -d restaurar
python manage.py loaddata restaurar/datos.json
cp -r restaurar/media/* <MEDIA_ROOT>/
```

**MySQL en producción:** `scripts/respaldo.sh` (mysqldump diario con retención de 7 diarios y 4 semanales; la contraseña va en
`~/.my.cnf` con permisos 600, nunca en el script). Restaurar: `gunzip -c ARCHIVO.sql.gz | mysql gestion_laserena`.

La recuperación se prueba automáticamente (caso CP-34). Los respaldos contienen datos personales: la carpeta `respaldos/`
está en `.gitignore` y no se sube al repositorio.

## 8. Pruebas y protocolo

```bash
python manage.py test                      # suite completa (menos de 1 minuto)
python manage.py protocolo_pruebas         # ejecuta la suite y genera docs/PROTOCOLO_PRUEBAS.md, docs/TRAZABILIDAD.md y CSV
python manage.py plan_pruebas              # plan detallado por caso de uso y requisito (PLAN_DE_PRUEBAS.md)
```

Los casos del protocolo, los defectos y los responsables se editan en `delegaciones_app/protocolo.py`; los resultados
obtenidos salen siempre de ejecutar las pruebas. Las incidencias de configuración resueltas están en la sección 8 del
protocolo generado.
