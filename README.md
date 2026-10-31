# SGR La Serena

Aplicacion web (Django) del Sistema de Gestion de Resultados para las Delegaciones
Municipales de La Serena. Persistencia 100% en base de datos relacional (MySQL),
administrable desde pantallas propias (Django Templates + Bootstrap, **sin Django Admin**) y
desplegable en una instancia AWS EC2.

## Incluye

- Modelo de 17 clases (más dos tablas adicionales) con las reglas de negocio en los modelos.
- Dashboard, semáforo y resumen de cumplimiento por delegación, calculados desde los indicadores.
- Ficha personal del funcionario: metas, avance, diferencia con lo esperado, detalle de la fórmula,
  evidencias y compromisos.
- Autenticación Django (login, logout, vistas protegidas) con tres **perfiles de acceso** que son
  grupos de Django con permisos: **Administrador** (acceso total), **Supervisor** (permisos
  intermedios) y **Administrativo** (permisos mínimos). Ver «Seguridad y perfiles».
- **Panel distinto por perfil** al iniciar sesión (`/gestion/panel/`).
- **Recuperación de contraseña por correo** con token seguro de un solo uso.
- Roles de trabajo (administrador, coordinador, delegado, funcionario, verificador y consulta),
  con acceso limitado a la delegación de cada usuario.
- Ocho mantenedores visuales con CRUD propio, búsqueda y baja lógica donde corresponde:
  Delegaciones, Cargos, Roles, Funcionarios, Catálogo, Períodos, Ítems medibles y Metas.
- Registro de actividades con código verificador único e inmutable, carga de evidencias
  (JPG, PNG o PDF, hasta 5 MB), revisión por verificadores y anulación de aprobaciones con motivo.
- Tubo de trabajo (tareas con la comunidad) con responsable, plazos, alerta de vencimiento, estados controlados, historial
  y un resumen por responsable y estado.
- Alertas por vencimientos, evidencias pendientes de revisión, ausencia de registros y avance bajo lo esperado.
- Actividad reciente por funcionario: registros, último ingreso, días sin ingreso y promedio diario.
- Filtros en las listas, que se conservan al volver desde un detalle, e informes de actividades,
  compromisos y cumplimiento en pantalla, para imprimir y en CSV.
- Control de períodos: un período cerrado no se modifica salvo reapertura con motivo.
- Control de concurrencia: si dos usuarios editan un mismo registro, el segundo recibe un aviso.
- Auditoría inmutable de operaciones críticas y de accesos denegados, con consulta para administración.
- Gestión de usuarios propia: crear cuentas, asignar perfil (grupo) y roles, activar o desactivar,
  desde el mantenedor «Funcionarios y usuarios». Django Admin no está instalado ni publicado.
- Variables de entorno para toda configuración sensible (nunca escritas en el código).

### Nombres en la interfaz

El sistema usa en pantalla el término de la Municipalidad (Matriz SGR):

| En la interfaz | En el código y la base de datos | En el diseño |
|---|---|---|
| «Tubo de trabajo» (la lista completa) | modelo `Compromiso`, tabla `compromiso`, ruta `/agenda/` | «Agenda colectiva» (CU-12) |
| «Tarea» (cada registro del tubo) | una fila de `Compromiso` | un compromiso |

El modelo, la tabla y las URL conservan su nombre original; solo cambian los textos visibles.
Las etiquetas de los estados van en femenino (Ingresada, Pendiente, En proceso, Realizada), pero en la
base se guardan los mismos valores de siempre (`ingresado`, `pendiente`, `proceso`, `realizado`).

## Arquitectura de datos

Toda la informacion vive en el modelo relacional de `delegaciones_app` (ver
`delegaciones_app/models.py`), que implementa las 17 clases del diseño:
`Delegacion`, `Cargo`, `Rol`, `Funcionario`, `UsuarioMaestro`, `Periodo`,
`ParametroVersionado`, `ItemMedible`, `Catalogo`, `Meta`, `Indicador`,
`Actividad`, `Evidencia`, `Validacion`, `Compromiso`, `HistorialCompromiso` y
`Auditoria`. Se suman `FuncionarioRol` (la relación entre funcionarios y roles) y
`MedicionDelegacion`, que conserva los indicadores iniciales de
`metas_delegaciones.json`. Las vistas obtienen los datos exclusivamente
mediante el ORM de Django.

Código de la aplicación:

- `models.py`: clases y reglas de negocio.
- `permisos.py`: roles y control de acceso.
- `crud.py`, `forms.py`: los ocho mantenedores y sus formularios.
- `views.py`, `informes.py`, `medicion.py`: actividades, compromisos, informes y cálculo de resultados.
- `auditoria.py`: auditoría y su consulta.
- `gestion_app`: dashboard, semáforo, resumen, ficha personal e informes.

La descripción de entidades, reglas, relaciones y migración está en
[MODELO_DATOS.md](MODELO_DATOS.md).

Los archivos `data/solicitudes.json` y `data/metas_delegaciones.json` de la
version anterior del proyecto se conservan solo como **fuente de carga inicial**
para el comando `seed_demo` (una migracion de datos, no una fuente en tiempo de
ejecucion). Ninguna vista los vuelve a leer.

## Instalacion local

### 1. Requisitos previos

- Python 3.11+
- MySQL Server (o MariaDB) corriendo localmente, con phpMyAdmin si se quiere
  inspeccionar las tablas visualmente.
- Git.

### 2. Clonar y preparar el entorno

```bash
git clone <URL_DEL_REPOSITORIO>
cd eva-backend-2
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con tus propios valores (clave secreta nueva, credenciales de tu
MySQL local). **Este archivo nunca se sube a git** (esta en `.gitignore`).
La aplicación no arranca si falta `SECRET_KEY`; reemplaza el valor de ejemplo
por una clave propia antes de ejecutar Django.

### 4. Crear la base de datos en MySQL

```sql
CREATE DATABASE gestion_laserena CHARACTER SET utf8mb4;
CREATE USER 'gestion_user'@'localhost' IDENTIFIED BY 'tu-clave';
GRANT ALL PRIVILEGES ON gestion_laserena.* TO 'gestion_user'@'localhost';
FLUSH PRIVILEGES;
```

(Usa los mismos valores en `DB_NAME` / `DB_USER` / `DB_PASSWORD` del `.env`.)

### 5. Migrar y cargar datos de demostracion

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py calcular_indicadores
python manage.py runserver
```

`calcular_indicadores` crea el indicador de cada meta de los períodos abiertos; se
repite cuando se cargan metas o actividades directamente en la base.

`makemigrations` se usa durante el desarrollo cuando cambian los modelos; al
instalar o desplegar se aplican las migraciones versionadas con `migrate`.

Abrir `http://127.0.0.1:8000/` e ingresar con una cuenta demo: cada perfil llega a su panel.
La administración se hace desde **Administración** en el menú (`/administracion/`).

> ¿No tienes MySQL instalado y solo quieres probar la app rapido? Pon
> `DB_ENGINE=sqlite` en tu `.env` para usar SQLite localmente. Para la entrega
> (evidencia de phpMyAdmin) se necesita `DB_ENGINE=mysql`.

Tres reglas son configurables desde el `.env` (ver `.env.example`):
`EVIDENCIA_TAMANO_MAXIMO_MB` (tamaño máximo de una evidencia, 5 por defecto),
`COMPROMISO_DIAS_ALERTA` (días de anticipación para marcar un compromiso como
próximo a vencer, 3 por defecto) y `ALERTA_DIAS_SIN_REGISTRO` (días sin registrar
actividades para emitir una alerta, 7 por defecto).

Configura `DB_PORT` segun el puerto donde escucha tu servidor. En el equipo
local actual MariaDB usa `3307`; MySQL/MariaDB con configuracion estandar,
incluido el servidor EC2 del ejemplo, usa `3306`. Esta diferencia va en el
`.env` individual y no se debe subir junto con contrasenas o claves.

## Cuentas demo

Las cuentas se crean con la clave que se indique al cargar los datos
(`python manage.py seed_demo --password TU_CLAVE`), con la variable de
entorno `DEMO_PASSWORD`, o con una clave aleatoria que el comando muestra una
sola vez si no se indica ninguna. No hay claves fijas en el repositorio.

| Usuario | Perfil (grupo) | Rol | Ambito |
|---|---|---|---|
| `admin.demo` | Administrador | Administrador | Todas las delegaciones |
| `coordinador.demo` | Supervisor | Coordinador | Todas las delegaciones |
| `funcionario.centro` | Administrativo | Funcionario | Centro: registra actividades y sube evidencias |
| `verificador.demo` | Administrativo | Delegado + Verificador | Delegado de Centro: revisa las evidencias de Centro |

Las cuentas demo no tienen correo. Para probar la recuperación de contraseña, entra como
`admin.demo`, abre **Administración → Funcionarios y usuarios**, edita la cuenta y escribe un
correo real.

Los datos son sinteticos y solo sirven para demostracion academica.

## Rutas principales

- `/`: portada SGR.
- `/login/`: inicio de sesion (lleva a `/gestion/panel/`, el panel de tu perfil).
- `/recuperar/`: recuperación de contraseña por correo.
- `/solicitudes/`: listado de compromisos (con buscador).
- `/actividades/`: actividades autorizadas, con filtros por delegación, estado, período y fechas.
- `/actividad/nueva/`: registro de actividades; `/actividad/<código>/` muestra su detalle,
  evidencias, revisión y anulación de la aprobación.
- `/evidencia/<código>/archivo/`: abre o descarga el archivo de una evidencia, con los mismos permisos de su actividad.
- `/agenda/`: tubo de trabajo (sus tareas), con filtros y alerta de vencimiento.
- `/actividad/<código>/evidencia/`: subir evidencia a una actividad.
- `/coordinacion/delegados/`: delegados por delegación, su carga y su asignación (coordinación).
- `/administracion/`: índice de los ocho mantenedores.
- `/administracion/<mantenedor>/`: listado, búsqueda y controles de cada mantenedor
  (`delegaciones`, `cargos`, `roles`, `funcionarios`, `catalogo`, `periodos`, `items`, `metas`).
- `/administracion/auditoria/`: consulta de solo lectura de la auditoría (perfil Administrador).
- `/administracion/perfiles/`: perfiles, sus permisos y sus usuarios (perfil Administrador).
- `/gestion/`, `/gestion/semaforo/`, `/gestion/resumen/`: medicion y cumplimiento.
- `/gestion/mi-ficha/`: ficha personal del funcionario.
- `/gestion/informes/`: informes de actividades, compromisos, resumen por responsable, actividad reciente
  y cumplimiento (pantalla, imprimir y CSV).
- `/gestion/alertas/`: alertas según tu rol y tu ámbito.
- `/territorio/`: contexto institucional.

## Roles de trabajo y flujo

| Rol | Qué hace | Qué ve |
|---|---|---|
| Coordinador | Gestiona a los delegados: los asigna a su delegación (`/coordinacion/delegados/`) y les asigna compromisos | Todas las delegaciones |
| Delegado | Trabaja su delegación: revisa (aprueba o rechaza) las evidencias de su delegación y registra compromisos tomados en terreno | Solo su delegación (registros y métricas) |
| Verificador | Revisa evidencias | Su delegación si tiene una; si no, todas |
| Funcionario | Registra actividades, sube evidencias y registra compromisos de su delegación | Su delegación |

- **Compromisos:** los crea la coordinación (eligiendo la delegación y el delegado responsable) o
  el delegado/funcionario para su propia delegación, quedando a su cargo. Solo coordinación y
  administración los eliminan.
- **Evidencias:** se suben desde el botón «Subir evidencia» (lista o detalle), separado de
  «Modificar». La lista de actividades indica si cada una tiene evidencia cargada.
- **Revisión:** aprobar, o rechazar indicando el motivo. Quien registró corrige y sube una evidencia
  nueva, y la actividad vuelve a revisión. Nadie revisa una actividad que registró él mismo.

## Seguridad y perfiles

| Perfil (grupo Django) | Nivel | Puede | No puede |
|---|---|---|---|
| Administrador | Acceso total | Los 8 mantenedores, gestión de usuarios y perfiles, todas las transacciones, auditoría, visión global | — |
| Supervisor | Intermedio | 6 mantenedores (delegaciones, cargos, catálogo, períodos, ítems, metas), transacciones, información operacional | Usuarios, roles, perfiles, auditoría |
| Administrativo | Mínimo | Registrar y seguir sus actividades, evidencias y compromisos; su ficha | Mantenedores, usuarios, eliminar compromisos, cerrar períodos, auditoría |

- Los grupos y sus permisos (`view`, `add`, `change`, `delete` de cada tabla) los crea la migración
  `0015_perfiles_de_acceso`, que además asigna perfil a los usuarios existentes según sus roles.
- Cada vista de mantenedor exige el permiso de Django de su acción (`PermisoRequeridoMixin` en
  `delegaciones_app/permisos.py`); los botones Agregar, Modificar y Eliminar se muestran según esos permisos.
- El perfil se asigna al crear o editar un usuario en el mantenedor de funcionarios.
- Un funcionario desactivado pierde los permisos de su perfil (`delegaciones_app/backends.py`).
- Recuperación de contraseña: `/recuperar/` pide el correo, Django genera un token firmado de un
  solo uso que vence en `PASSWORD_RESET_TIMEOUT` segundos (1 hora), se envía el enlace por SMTP,
  el enlace valida el token, permite fijar la nueva contraseña y confirma el cambio, que queda en la auditoría.

### Configurar el correo

Sin variables de correo, el mensaje de recuperación se imprime en la consola donde corre Django.
Para enviarlo de verdad (por ejemplo con Gmail), agrega al `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-cuenta@gmail.com
EMAIL_HOST_PASSWORD=contrasena-de-aplicacion-de-16-caracteres
DEFAULT_FROM_EMAIL=SGR La Serena <tu-cuenta@gmail.com>
```

En Gmail, la contraseña de aplicación se crea en la cuenta de Google con la verificación en dos
pasos activa. AWS bloquea el puerto 25 de salida, por eso se usa el 587.

## Validacion y pruebas

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py plan_pruebas
```

Las pruebas están en `delegaciones_app`:

- `test_unit_*.py`: pruebas unitarias por caso de uso. Cada una declara en su docstring el CU y
  los requisitos que verifica, por ejemplo «CU-27.1 Restringir elemento duplicado (RF-004)».
  Incluyen los 8 casos de login (`test_unit_autenticacion.py`).
- `test_integracion.py`: pruebas de integración de las vistas, los permisos y la migración de datos.
- `pruebas_base.py`: datos de apoyo compartidos (no es una prueba).

`plan_pruebas` ejecuta todo y escribe `PLAN_DE_PRUEBAS.md`: cobertura por caso de uso y por
requisito, la tabla CP, CU, RF, método de prueba y resultado, y las fichas de login.

## Alcance y requisitos pendientes

Todos los casos de uso de la especificación detallada (CU-01 a CU-30, con sus extensiones) tienen pruebas. Entre los requisitos
funcionales no están implementados: RF-015 (atención social por etapas), RF-020 (el cierre de un
compromiso no alimenta el indicador), RF-025 (incentivos y penalizaciones), RF-031 (vista global
por cargos) y RF-035 (comentarios). El detalle de cada uno está en [MODELO_DATOS.md](MODELO_DATOS.md)
y en la sección 4 de [PLAN_DE_PRUEBAS.md](PLAN_DE_PRUEBAS.md).

## Despliegue en AWS EC2

Guia del despliegue real: instancia EC2 con Amazon Linux 2023, MySQL 8.4,
Gunicorn como servicio systemd, Nginx como proxy inverso y phpMyAdmin con
PHP-FPM. El codigo se trae desde GitHub con Git.

### 1. Instancia y red

- Amazon Linux 2023, usuario `ec2-user`.
- Grupo de seguridad con SSH (22) y HTTP (80). El puerto 3306 (MySQL) **no** se abre.
- Elastic IP asociada, para que la IP publica no cambie al detener e iniciar la instancia.

```bash
ssh -i tu-llave.pem ec2-user@<IP_PUBLICA_EC2>
```

### 2. Dependencias del sistema

```bash
sudo dnf install -y python3.14 python3.14-pip git nginx gcc pkgconf-pkg-config unzip
```

MySQL 8.4 se instala desde el repositorio oficial de MySQL (no MariaDB), junto
con `mysql-community-server` y `mysql-community-devel` (necesario para compilar
`mysqlclient`).

### 3. Swap persistente (instancia con poca memoria)

```bash
sudo fallocate -l 1G /swapfile && sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 4. Clonar el proyecto y preparar Python

```bash
cd /var/www
sudo git clone https://github.com/cesar260207/eva-backend-2.git
cd eva-backend-2
python3.14 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn
pip install --no-cache-dir --no-binary mysqlclient mysqlclient
```

`mysqlclient` se compila contra MySQL para evitar el error
`libmariadb.so.3: cannot open shared object file`.

### 5. Base de datos y archivo `.env`

```sql
CREATE DATABASE gestion_laserena CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci;
CREATE USER 'gestion_user'@'localhost' IDENTIFIED BY '<CLAVE_SEGURA>';
GRANT ALL PRIVILEGES ON gestion_laserena.* TO 'gestion_user'@'localhost';
```

```bash
cp .env.example .env
chmod 600 .env
nano .env   # SECRET_KEY, DEBUG=False, ALLOWED_HOSTS=<IP_PUBLICA_EC2>, datos de la base y del correo
```

El `.env` nunca se sube a Git. Para la recuperación de contraseña se agregan las variables
`EMAIL_*` de la sección «Configurar el correo».

**Actualizar un servidor ya desplegado** (por ejemplo, para la Evaluación Sumativa 3):

```bash
mysqldump -u gestion_user -p gestion_laserena > respaldo_$(date +%F).sql
git pull
source venv/bin/activate && pip install -r requirements.txt
nano .env                                  # agregar EMAIL_BACKEND, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD...
python manage.py migrate                   # 0015 crea los perfiles y asigna uno a cada usuario
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

### 6. Migraciones, datos demo y estaticos

```bash
python manage.py migrate
python manage.py seed_demo          # entrega o genera la clave demo una sola vez
python manage.py calcular_indicadores
python manage.py collectstatic --noinput
```

> Al actualizar una instalación que ya tiene datos del modelo anterior, las
> migraciones `0011` a `0013` eliminan tablas y campos antiguos y no se pueden
> deshacer con seguridad. Antes de migrar, hay que respaldar la base
> (`mysqldump -u gestion_user -p gestion_laserena > respaldo.sql`) y, si es posible,
> ensayar primero sobre una copia. Más detalle en [MODELO_DATOS.md](MODELO_DATOS.md).

### 7. Gunicorn como servicio systemd

Archivo `/etc/systemd/system/gunicorn.service`:

```ini
[Unit]
Description=Gunicorn daemon para Django (gestion_laserena)
After=network.target mysqld.service

[Service]
User=ec2-user
Group=nginx
WorkingDirectory=/var/www/eva-backend-2
ExecStart=/var/www/eva-backend-2/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/var/www/eva-backend-2/gunicorn.sock \
          gestion_laserena.wsgi:application

[Install]
WantedBy=multi-user.target
```

`Group=nginx` permite que Nginx lea el socket de Gunicorn.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn
```

### 8. Nginx como proxy inverso

Archivo `/etc/nginx/conf.d/eva-backend-2.conf`: sirve `/static/` directamente
y pasa el resto al socket de Gunicorn. **No publica `/media/`**: los archivos de
evidencia se entregan solo por la vista `evidencia/<código>/archivo/`, que exige
sesión y revisa que el usuario pueda ver la actividad (RNF-017). Si la
configuración tiene un bloque `location /media/`, se elimina.

```bash
sudo nginx -t && sudo systemctl reload nginx
```

Se accede con `http://<IP_PUBLICA_EC2>/` (sin https).

### 9. phpMyAdmin (PHP-FPM + Nginx)

1. Instalar `php8.4-fpm` con los modulos `mysqlnd`, `mbstring`, `xml`, `gd`,
   `intl` y `zip`, y activar el servicio (`systemctl enable --now php-fpm`).
2. Descargar phpMyAdmin 5.2.3 (`all-languages.zip`) en `/usr/share/phpmyadmin`.
3. Crear `config.inc.php` con `blowfish_secret` y `TempDir`, propiedad de
   `apache` con permisos 640.
4. Publicarlo en Nginx bajo `/phpmyadmin/` con `fastcgi_pass` al socket de PHP-FPM.
5. **Seguridad:** doble puerta. Autenticacion basica de Nginx
   (`auth_basic` con archivo `.htpasswd`) y despues el login de MySQL con
   `gestion_user` (no `root`). El puerto 3306 permanece cerrado.

### 10. Evidencia a mostrar durante la revision

- Instancia EC2 en ejecucion, IP publica e IP elastica.
- `git log --oneline`, `git remote -v` y `git status` limpio.
- `systemctl status` de mysqld, gunicorn, nginx y php-fpm en verde; `nginx -t`.
- La aplicacion respondiendo en el navegador desde la IP publica.
- Login con cada cuenta demo y su panel (Administrador, Supervisor, Administrativo).
- Mantenedores con CRUD y búsqueda; restricciones al entrar con un perfil sin permiso.
- Recuperación de contraseña: solicitud, correo recibido, enlace, cambio e ingreso con la nueva clave.
- phpMyAdmin (`/phpmyadmin/`) mostrando tablas, estructura, relaciones y registros.

## Evidencia de uso de IA

Documenta en `evidencias_ia.md` (o en el documento tecnico entregable) los
prompts usados durante el desarrollo, las respuestas obtenidas y como se
aplicaron al codigo final.
