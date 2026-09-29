# SGR La Serena

Aplicacion web (Django) del Sistema de Gestion de Resultados para las Delegaciones
Municipales de La Serena. Persistencia 100% en base de datos relacional (MySQL),
administrable desde Django Admin y desplegable en una instancia AWS EC2.

## Incluye

- Dashboard territorial, agenda y semaforo de cumplimiento (calculados en vivo desde la BD).
- Autenticacion Django y perfiles por rol.
- CRUD de delegaciones para administradores y coordinadores.
- Ocho mantenedores visuales (dos por integrante para un equipo de cuatro):
  Delegaciones, Perfiles, Catálogo, Períodos, Actividades, Evidencias,
  Compromisos y Metas. Todos usan Django ORM y ofrecen búsqueda. Delegaciones,
  Perfiles, Catálogo, Períodos, Actividades y Evidencias tienen
  CRUD propio en la aplicación. Compromisos y Metas mantienen sus acciones en
  Django Admin mientras se implementan sus CRUD propios.
- Registro persistente de actividades con codigo unico y evidencias.
- Carga de evidencias y flujo de aprobacion/rechazo.
- Compromisos colectivos y auditoria de operaciones criticas.
- Filtrado de actividades por delegacion autorizada.
- Panel de Django Admin con todas las entidades: crear, modificar, eliminar, buscar y navegar por relaciones.
- Variables de entorno para toda configuracion sensible (nunca escritas en el codigo).

## Arquitectura de datos

Toda la informacion vive en el modelo relacional de `delegaciones_app` (ver
`delegaciones_app/models.py`): `Delegacion`, `PerfilUsuario`, `CatalogoItem`,
`PeriodoMedicion`, `Actividad`, `Evidencia`, `Compromiso`, `MetaMedicion`,
`MedicionDelegacion`, `HistorialCompromiso` y `Auditoria`. `MedicionDelegacion`
conserva los indicadores iniciales de `metas_delegaciones.json`, incluidos su
cumplimiento, meta, fecha, estado y observación. Las vistas obtienen los datos exclusivamente
mediante el ORM de Django (`objects.filter/get/aggregate`, etc.).

La descripción de entidades, relaciones y migración de JSON está en
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
python manage.py runserver
```

`makemigrations` se usa durante el desarrollo cuando cambian los modelos; al
instalar o desplegar se aplican las migraciones versionadas con `migrate`.

Abrir `http://127.0.0.1:8000/`. El panel de administracion esta en
`http://127.0.0.1:8000/admin/`.

> ¿No tienes MySQL instalado y solo quieres probar la app rapido? Pon
> `DB_ENGINE=sqlite` en tu `.env` para usar SQLite localmente. Para la entrega
> (evidencia de phpMyAdmin) se necesita `DB_ENGINE=mysql`.

Configura `DB_PORT` segun el puerto donde escucha tu servidor. En el equipo
local actual MariaDB usa `3307`; MySQL/MariaDB con configuracion estandar,
incluido el servidor EC2 del ejemplo, usa `3306`. Esta diferencia va en el
`.env` individual y no se debe subir junto con contrasenas o claves.

## Cuentas demo

Las cuentas se crean con la clave que se indique al cargar los datos
(`python manage.py seed_demo --password TU_CLAVE`), con la variable de
entorno `DEMO_PASSWORD`, o con una clave aleatoria que el comando muestra una
sola vez si no se indica ninguna. No hay claves fijas en el repositorio.

| Usuario | Rol | Ambito |
|---|---|---|
| `admin.demo` | Administrador (superusuario, accede a `/admin/`) | Todas las delegaciones |
| `coordinador.demo` | Coordinador | Todas las delegaciones |
| `funcionario.centro` | Funcionario | Centro |
| `verificador.demo` | Verificador | Revision de evidencias |

Los datos son sinteticos y solo sirven para demostracion academica.

## Rutas principales

- `/`: portada SGR.
- `/login/`: inicio de sesion.
- `/solicitudes/`: listado de compromisos (con buscador).
- `/actividades/`: actividades autorizadas (con buscador).
- `/actividad/nueva/`: registro persistente de actividades.
- `/agenda/`: compromisos y agenda colectiva.
- `/administracion/delegaciones/`: CRUD de delegaciones para roles autorizados.
- `/administracion/`: índice de los ocho mantenedores requeridos.
- `/administracion/<mantenedor>/`: listado, búsqueda y controles de cada mantenedor.
- `/admin/`: administracion completa de Django (todas las entidades).
- `/gestion/`, `/gestion/semaforo/`, `/gestion/resumen/`: medicion y cumplimiento.
- `/territorio/`: contexto institucional.

## Validacion

```bash
python manage.py check
python manage.py test
```

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
nano .env   # SECRET_KEY, DEBUG=False, ALLOWED_HOSTS=<IP_PUBLICA_EC2>, datos de la base
```

El `.env` nunca se sube a Git.

### 6. Migraciones, datos demo y estaticos

```bash
python manage.py migrate
python manage.py seed_demo          # entrega o genera la clave demo una sola vez
python manage.py collectstatic --noinput
```

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

Archivo `/etc/nginx/conf.d/eva-backend-2.conf`: sirve `/static/` y `/media/`
directamente, y pasa el resto al socket de Gunicorn.

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
- `/admin/` con las 11 entidades: crear, editar, eliminar, buscar y navegar
  relaciones (por ejemplo, Compromiso con su Historial).
- phpMyAdmin (`/phpmyadmin/`) mostrando tablas, estructura, relaciones y registros.

## Evidencia de uso de IA

Documenta en `evidencias_ia.md` (o en el documento tecnico entregable) los
prompts usados durante el desarrollo, las respuestas obtenidas y como se
aplicaron al codigo final.
