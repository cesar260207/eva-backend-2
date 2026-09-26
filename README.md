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
  Compromisos y Metas. Todos usan Django ORM y ofrecen busqueda; Delegaciones
  y Catalogo tienen CRUD propio en la aplicacion. Los seis mantenedores restantes
  todavia enlazan sus acciones a Django Admin mientras se implementan sus CRUD.
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

## Cuentas demo

Todas usan la clave `Demo2026!`:

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

Guia resumida para desplegar sobre una instancia EC2 con Ubuntu Server (Linux),
usando Git para traer el codigo desde GitHub y Gunicorn como servidor WSGI.

### 1. Conectarse a la instancia

```bash
ssh -i tu-llave.pem ubuntu@<IP_PUBLICA_EC2>
```

### 2. Instalar dependencias del sistema

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git mysql-server \
    libmysqlclient-dev pkg-config phpmyadmin
```

(Durante la instalacion de `phpmyadmin`, selecciona `apache2` o configura tu
propio servidor web segun lo que uses; sigue el asistente para conectar
phpMyAdmin a MySQL.)

### 3. Clonar el proyecto desde GitHub

```bash
git clone <URL_DEL_REPOSITORIO>
cd eva-backend-2
```

### 4. Entorno virtual y dependencias Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 5. Configurar MySQL y el archivo `.env`

```bash
sudo mysql -e "CREATE DATABASE gestion_laserena CHARACTER SET utf8mb4;"
sudo mysql -e "CREATE USER 'gestion_user'@'localhost' IDENTIFIED BY 'tu-clave-segura';"
sudo mysql -e "GRANT ALL PRIVILEGES ON gestion_laserena.* TO 'gestion_user'@'localhost'; FLUSH PRIVILEGES;"

cp .env.example .env
nano .env   # completar SECRET_KEY, DEBUG=False, ALLOWED_HOSTS=<IP_PUBLICA_EC2>, credenciales DB
```

### 6. Migraciones, datos demo y estaticos

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser   # opcional, cuenta propia ademas de admin.demo
python manage.py collectstatic --noinput
```

### 7. Ejecutar el servidor

Para la revision (rapido, sirve para demostrar el funcionamiento):

```bash
python manage.py runserver 0.0.0.0:8000
```

Abre el **Security Group** de la instancia para permitir trafico entrante en el
puerto 8000 (o 80 si usas Gunicorn + Nginx). Verifica en el navegador:
`http://<IP_PUBLICA_EC2>:8000/`.

Para un despliegue mas cercano a produccion, sirve con Gunicorn:

```bash
pip install gunicorn
gunicorn gestion_laserena.wsgi:application --bind 0.0.0.0:8000
```

### 8. Evidencia a mostrar durante la revision

- Conexion SSH activa a la instancia EC2.
- `git log --oneline` mostrando el historial de commits.
- `git remote -v` mostrando el repositorio remoto configurado.
- La aplicacion respondiendo en el navegador desde la IP publica de EC2.
- `/admin/` con las entidades del modelo: crear, editar, eliminar, buscar y
  navegar entre relaciones (por ejemplo, desde una `Actividad` a sus
  `Evidencia`s).
- phpMyAdmin mostrando las tablas generadas por las migraciones de Django y
  sus registros.

## Evidencia de uso de IA

Documenta en `evidencias_ia.md` (o en el documento tecnico entregable) los
prompts usados durante el desarrollo, las respuestas obtenidas y como se
aplicaron al codigo final.
