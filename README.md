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
- Autenticación Django (login, logout, vistas protegidas) con cuatro **perfiles de acceso** que son
  grupos de Django con permisos y siguen la jerarquía de la Municipalidad: **Administrador** (acceso
  total), **Coordinador** y **Delegado** (permisos intermedios) y **Profesional** (permisos mínimos).
  Ver «Seguridad y perfiles».
- **Panel distinto por perfil** al iniciar sesión (`/gestion/panel/`).
- **Recuperación de contraseña por correo** con token seguro de un solo uso.
- Roles de trabajo (administrador, coordinador, delegado y funcionario),
  con acceso limitado a la delegación de cada usuario.
- Doce mantenedores visuales con CRUD propio, búsqueda, validaciones y eliminación con confirmación; un registro
  con datos relacionados no se elimina, se desactiva y la confirmación explica la razón:
  Delegaciones, Cargos, Roles, Funcionarios, Catálogo, Períodos, Ítems medibles y Metas.
- Registro de actividades con código verificador único e inmutable, carga de evidencias
  (JPG, PNG o PDF, hasta 5 MB), revisión por delegados y coordinación y anulación de aprobaciones con motivo.
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
- Reglas de la reunión de octubre 2026 ([docs/REQUERIMIENTOS_V2.md](docs/REQUERIMIENTOS_V2.md)): actividades sin
  puntaje cuando son gestión interna, gestión previa o no tienen nombre y teléfono del contacto; máximo de 7
  ingresos diarios; cierre semanal al registrar; tope de 120 % por ítem; felicitaciones y reclamos que informa el
  delegado y aplica o rechaza la coordinación desde la lista de ajustes; ausencias que el delegado registra desde
  el semáforo; atención social por etapas; comentarios en las actividades.
- El semáforo se recalcula al aprobar una actividad, al decidir un ajuste, al registrar o borrar una ausencia y al
  cambiar una tarea del tubo de un ítem tipo «tubo».
- Carga de la Matriz SGR (13 cargos y sus ítems) e importación de las organizaciones comunitarias del municipio,
  con comandos que no publican datos personales.

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
`Auditoria`. Se suman `FuncionarioRol`, `Organizacion`, `Ajuste`, `Ausencia`,
`CasoSocial` y `Comentario`, además de `MedicionDelegacion`, que conserva los indicadores iniciales de
`metas_delegaciones.json`. Las vistas obtienen los datos exclusivamente
mediante el ORM de Django.

Código de la aplicación:

- `models.py`: clases y reglas de negocio.
- `permisos.py`: roles y control de acceso.
- `crud.py`, `forms.py`: los doce mantenedores y sus formularios.
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

`seed_demo` crea dos períodos: julio-septiembre 2026 y el trimestre que incluye la fecha actual. En este
último carga los 13 cargos de la matriz (`data/matriz_cargos.json`), el ítem «Atención de casos sociales» con
una meta de 2 para `funcionario.centro` (aprobar una actividad cambia el semáforo de rojo a ámbar), y ejemplos
ficticios de organización, felicitación por decidir, ausencia y atención social.

Datos del municipio (nunca se suben a GitHub; se copian al servidor por `scp`):

```bash
# Matriz SGR: del Excel a data/matriz_cargos.json (sin nombres de personas) y luego a un período
python manage.py generar_matriz "<ruta>/MATRIZ SGR TRIMESTRE.xlsx"
python manage.py cargar_matriz data/matriz_cargos.json --periodo "Trimestre octubre-diciembre 2026"
# Organizaciones comunitarias: asigna la delegación por territorio y el tipo por el nombre
python manage.py importar_organizaciones "<ruta>/organizaciones_comunitarias.xlsx"
```

`makemigrations` se usa durante el desarrollo cuando cambian los modelos; al
instalar o desplegar se aplican las migraciones versionadas con `migrate`.

Abrir `http://127.0.0.1:8000/` e ingresar con una cuenta demo: cada perfil llega a su panel.
La administración se hace desde **Administración** en el menú (`/administracion/`).

> ¿No tienes MySQL instalado y solo quieres probar la app rapido? Pon
> `DB_ENGINE=sqlite` en tu `.env` para usar SQLite localmente. Para la entrega
> (evidencia de phpMyAdmin) se necesita `DB_ENGINE=mysql`.

Las reglas de negocio se versionan por período: tope de cumplimiento (120 % por defecto),
máximo de 7 ingresos diarios, felicitaciones (+10 %, máximo 3) y reclamos (-30 %).
Tres reglas operativas siguen configurables desde el `.env` (ver `.env.example`):
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
| `coordinador.demo` | Coordinador | Coordinador | Todas las delegaciones |
| `delegado.demo` | Delegado | Delegado | Delegado de Centro: revisa las evidencias de Centro |
| `funcionario.centro` | Profesional | Funcionario | Centro: registra actividades y sube evidencias |

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
- `/administracion/`: índice de los doce mantenedores.
- `/administracion/<mantenedor>/`: listado, búsqueda y controles de cada mantenedor
  (`delegaciones`, `cargos`, `roles`, `funcionarios`, `catalogo`, `organizaciones`, `periodos`, `parametros`,
  `items`, `metas`, `ajustes`, `ausencias`).
- `/administracion/auditoria/`: consulta de solo lectura de la auditoría (perfil Administrador).
- `/administracion/perfiles/`: perfiles, sus permisos y sus usuarios (perfil Administrador).
- `/gestion/`, `/gestion/semaforo/`, `/gestion/resumen/`: medicion y cumplimiento.
- `/gestion/mi-ficha/`: ficha personal del funcionario.
- `/gestion/informes/`: informes de actividades, compromisos, resumen por responsable, actividad reciente
  y cumplimiento (pantalla, imprimir y CSV).
- `/gestion/alertas/`: alertas según tu rol y tu ámbito.
- `/territorio/`: contexto institucional.
- `/ajustes/nuevo/`: informar una felicitación o un reclamo (Delegado; también en el menú del usuario).
  La coordinación los aplica o rechaza desde `/administracion/ajustes/`.
- `/ausencias/nuevo/`: registrar una ausencia (Delegado, desde el botón del semáforo).
- `/casos-sociales/nuevo/`: registrar una atención social (Profesional; también en el menú del usuario).
- `/actividad/<código>/comentario/`: comentar una actividad (botón «Comentar» del detalle).

## Roles de trabajo y flujo

| Rol | Qué hace | Qué ve |
|---|---|---|
| Administrador | Configura cuentas y mantenedores, consulta auditoría y supervisa el sistema | Todas las delegaciones y funciones |
| Coordinador | Gestiona a los delegados: asigna o cambia el delegado de cada delegación (`/coordinacion/delegados/`), les asigna tareas del tubo, revisa evidencias y sigue el avance de todas. No hace el trabajo operativo: no sube evidencias en nombre de otros. Su panel muestra todas las delegaciones con su avance y su delegado | Todas las delegaciones |
| Delegado | Trabaja su delegación: revisa (aprueba o rechaza) sus evidencias, registra actividades y tareas tomadas en terreno. Su panel muestra lo que espera su revisión, su tubo de trabajo y sus métricas | Solo su delegación (registros y métricas) |
| Profesional | Registra actividades, sube evidencias y registra compromisos de su delegación | Su delegación |

- **Tareas del tubo de trabajo: quién y dónde las crea.** Se agregan solo desde la página del tubo
  (`/agenda/`), con el botón «+ Agregar al tubo de trabajo», que ven únicamente quienes pueden crear:
  - administración y coordinación: para cualquier delegación, eligiendo al delegado responsable;
  - delegado y profesional: para su propia delegación, y la tarea queda a su cargo;
  - la migración `0024_migrar_roles_obsoletos` ya trasladó los roles retirados `verificador` y `consulta` a `delegado` y `funcionario`, respectivamente.

  Los paneles, la pantalla de delegados y la página de cada delegación solo llevan al tubo («Ver tubo de
  trabajo»). La regla está en `permisos.ROLES_CREAN_TAREAS`. Solo coordinación y administración eliminan tareas.
- **Evidencias:** solo quien registró la actividad las sube, desde el botón «Subir evidencia» (lista o detalle), separado de
  «Modificar». La lista de actividades indica si cada una tiene evidencia cargada.
- **Revisión:** aprobar, o rechazar indicando el motivo. Quien registró corrige y sube una evidencia
  nueva, y la actividad vuelve a revisión. Nadie revisa una actividad que registró él mismo.

## Transacciones

Las cuatro transacciones del sistema. Cada una valida los datos con un formulario de Django, guarda dentro
de `transaction.atomic()` (si algo falla no queda nada a medias), deja un registro en la auditoría y
responde con un mensaje de éxito o de error.

### 1. Registro de actividad

- **Quién:** cualquier funcionario con cuenta. Queda como autor y la actividad, en su delegación.
- **Dónde:** `/actividad/nueva/` (vista `actividad_nueva`, formulario `ActividadForm`).
- **Validaciones:** campos obligatorios, fecha dentro del período del ítem, ítem de un período abierto,
  teléfono con formato válido. Al modificar, el control de versión rechaza los cambios si otra persona
  guardó antes.
- **Qué guarda:** la actividad con un código verificador único e inmutable (`EVD-fecha-sufijo`) y el
  evento `crear` en la auditoría. Luego lleva a «Subir evidencia».
- **Después:** el autor o la coordinación la modifican mientras no esté aprobada ni su período esté
  cerrado. Eliminarla es una operación crítica: exige el permiso `delete_actividad` (Coordinador y
  Administrador) y una confirmación que avisa cuántas evidencias se borran con ella.

### 2. Carga y revisión de evidencias

- **Carga:** `/actividad/<código>/evidencia/` (vista `evidencia_subir`, formulario `EvidenciaForm`). Solo
  el autor sube evidencias, en JPG, PNG o PDF de hasta 5 MB. La evidencia queda pendiente de revisión.
- **Revisión:** botones Aprobar y Rechazar del detalle de la actividad (vista `revisar_actividad`,
  formulario `RevisionForm`). Revisa quien tiene un rol revisor y el permiso `add_validacion` de su
  perfil, dentro de su ámbito y nunca sobre una actividad propia. Rechazar exige un motivo.
- **Qué guarda:** una `Validacion` por cada evidencia pendiente, el nuevo estado de la actividad, el
  recálculo de los indicadores de las metas y el evento `aprobar` o `rechazar` en la auditoría. Si se
  rechaza, el autor corrige y la actividad vuelve a revisión.
- **Anulación:** una aprobación se anula con motivo (vista `anular_actividad`): la actividad deja de sumar
  al avance y la validación original queda en el historial.

### 3. Tubo de trabajo (tareas con la comunidad)

- **Quién:** administración y coordinación, para cualquier delegación y eligiendo al responsable; delegado
  y funcionario, para su delegación y a su cargo (`permisos.ROLES_CREAN_TAREAS`).
- **Dónde:** `/agenda/`, botón «+ Agregar al tubo de trabajo» (vista `compromiso_nuevo`, formulario
  `CompromisoForm`).
- **Qué guarda:** la tarea con un folio único (`AGR-fecha-sufijo`), su primera línea de historial
  («Creación de la tarea») y el evento `crear` en la auditoría.
- **Cambios de estado:** Ingresada, Pendiente, En proceso y Realizada, solo por transiciones permitidas
  (`Compromiso.set_estado`). Los hace el responsable o la coordinación; cada cambio agrega una línea al
  historial con su observación y queda en la auditoría.
- **Eliminar:** solo coordinación y administración. Una tarea vencida sin realizar no se elimina: se
  conserva con su historial.

### 4. Asignación de delegados

- **Quién:** la coordinación y la administración.
- **Dónde:** `/coordinacion/delegados/` (vista `delegados`, formulario `AsignarDelegadoForm`).
- **Validaciones:** solo funcionarios activos con el rol delegado y delegaciones activas; no se asigna a
  alguien a la delegación que ya tiene.
- **Qué guarda:** la nueva delegación del funcionario y el evento `asignar_delegado` en la auditoría, con
  la delegación anterior y la nueva. Desde ese momento el delegado ve y revisa solo esa delegación.

## Seguridad y perfiles

Perfil = nivel de permisos (grupo de Django); rol = función y alcance (tabla `rol`). Los cuatro perfiles
son Administrador, Coordinador, Delegado y Profesional; cada uno recibe los permisos de las tareas que realiza.

**Cierre de sesión.** En todos los perfiles la sesión se cierra tras 30 minutos sin actividad (cada página abierta
renueva el plazo) y al cerrar el navegador. El plazo se cambia con `SESSION_INACTIVIDAD_MINUTOS` en el `.env`.
`python manage.py clearsessions` borra de la base las sesiones vencidas (semanal, ver el plan de mantención).

| Perfil (grupo Django) | En la pauta | Roles que lo usan | Puede | No puede |
|---|---|---|---|---|
| Administrador | Administrador (acceso total) | administrador | Los 12 mantenedores, gestión de usuarios y perfiles, todas las transacciones, auditoría, visión global | — |
| Coordinador | Coordinación | coordinador | Gestionar los seis mantenedores operativos, ver y editar organizaciones, ajustes, ausencias, casos sociales, comentarios y parámetros; decidir ajustes, revisar evidencias y eliminar actividades y tareas en todas las delegaciones | Funcionarios, roles, perfiles, auditoría |
| Delegado | Delegación | delegado | Verificar organizaciones de su delegación, crear ajustes y ausencias de su equipo, comentar y trabajar el tubo y las actividades de su delegación | Otras delegaciones, usuarios, eliminar, auditoría |
| Profesional | Profesional | funcionario | Ver organizaciones de su delegación, crear casos sociales y comentarios, registrar y seguir sus actividades, evidencias y tareas | Mantenedores fuera de su alcance, revisión de evidencias, usuarios, eliminar actividades o tareas, auditoría |

- Los grupos y sus permisos (`view`, `add`, `change`, `delete` de cada tabla) los crean las migraciones
  `0015_perfiles_de_acceso` (tres perfiles iniciales) y `0018_perfiles_por_jerarquia` (renombra
  Supervisor a Coordinador y Administrativo a Funcionario, crea Delegado y mueve allí a los delegados).
  Las migraciones `0024_migrar_roles_obsoletos` y `0025_permisos_perfiles_operativos` retiran los roles antiguos
  y asignan los permisos de mantenedores por perfil. La `0019_eliminar_actividad_solo_coordinacion` da al Coordinador el permiso
  `delete_actividad`: eliminar actividades es una operación crítica que Delegado y Profesional no hacen
  (corrigen con «Modificar actividad»).
- Revisar evidencias exige el rol (delegado, coordinador o administrador) **y** el permiso
  `add_validacion` del perfil (`permisos.puede_revisar`): el perfil Profesional nunca revisa. El delegado
  revisa solo las actividades de su delegación; las de otra responden 404.
- Ámbito: quien trabaja una delegación (delegado, profesional) ve solo su delegación en actividades, tubo de
  trabajo, portada, panel, medición, semáforo, resumen, informes (pantalla y CSV), alertas y ficha. Un
  registro de otra delegación (actividad, evidencia, tarea o página de la delegación) responde 404 y el
  intento queda en la auditoría.
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

Pasos para obtener la «contraseña de aplicación» de Gmail (no se usa la clave normal de la cuenta):

1. En la cuenta de Google que enviará los correos, activar la **verificación en dos pasos**
   (Cuenta de Google → Seguridad).
2. Abrir **Contraseñas de aplicaciones** (`https://myaccount.google.com/apppasswords`), escribir un
   nombre (por ejemplo «SGR La Serena») y crearla.
3. Copiar los 16 caracteres que muestra Google, sin espacios, en `EMAIL_HOST_PASSWORD` del `.env`.
   Ese valor nunca se sube a GitHub.
4. Reiniciar Django (en EC2, `sudo systemctl restart gunicorn`) para que lea el `.env`.
5. Probar el envío: `python manage.py sendtestemail tu-correo@ejemplo.com`.

AWS bloquea el puerto 25 de salida, por eso se usa el 587 con TLS.

Variables: `EMAIL_BACKEND` (SMTP para enviar de verdad; sin ella, consola), `EMAIL_HOST`, `EMAIL_PORT`,
`EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` y
`PASSWORD_RESET_TIMEOUT` (vigencia del enlace en segundos, 3600 por defecto).

Seguridad del flujo: la pantalla responde lo mismo exista o no el correo (no revela qué cuentas
existen), una cuenta inactiva no recibe enlace, el token sirve una sola vez y vence. Las pruebas usan el
backend de correo en memoria (`locmem`) y cubren el envío, el enlace, el uso único y el vencimiento.

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

Cobertura del código y tiempos de respuesta (herramientas de desarrollo, no se instalan en el servidor):

```bash
pip install -r requirements-dev.txt
coverage run manage.py test && coverage report   # configuración en .coveragerc
python scripts/medir_tiempos.py                  # escribe docs/resultados/tiempos_respuesta.csv
```

GitHub Actions (`.github/workflows/pruebas.yml`) ejecuta `check`, revisa que no falten migraciones y corre
las pruebas en cada pull request. Los resultados medidos están en [docs/RESULTADOS.md](docs/RESULTADOS.md).

## Preguntas pendientes para el municipio

La matriz SGR y el documento de requerimientos de octubre 2026 no coinciden en algunos valores. El sistema
deja cada valor como parámetro versionado del período (mantenedor «Parámetros del período») y usa el del
documento de octubre hasta que el municipio confirme:

| Tema | Matriz SGR | Documento de octubre | Valor en el sistema | Parámetro |
|---|---|---|---|---|
| Tope del cumplimiento de cada ítem | 150 % | 120 % (regla 7) | 120 % | `maximo_cumplimiento` |
| Valor de un reclamo | -20 % en la hoja RECLAMOS y en «Coordinador DISERCO» y «Gestor social 1»; -30 % en las demás hojas de cargo | No lo fija | -30 % | `valor_reclamo` |
| Ponderaciones de «Planificación y control» | Suman 85 % | No lo fija | Se cargan como están; para iniciar el período el sistema exige 100 % por cargo | Ítems medibles |
| Meta del ítem «Emergencia» | En varias hojas coincide con el avance (por ejemplo, 304) | No lo fija | Se carga como está | Ítems medibles y metas |
| Felicitación dirigida a un gestor | No lo distingue | No valen las del usuario al gestor por mensaje; las informa el delegado | Se acepta para cualquier funcionario si tiene respaldo formal y la informa el delegado | Ajustes |
| Organizaciones sin delegación | 2 del territorio «ALFALFARES» y 22 sin territorio | No lo fija | Quedan sin delegación y sin verificar, para asignar a mano | Organizaciones |

`cargar_matriz` crea estos parámetros con los valores de la tabla, pero no pisa un valor que la
coordinación ya haya definido en el período.

## Alcance y requisitos pendientes

Todos los casos de uso de la especificación detallada (CU-01 a CU-30, con sus extensiones) tienen pruebas, y
`test_casos_de_uso.py` comprueba que los actores de los cuadros de casos de uso coinciden con los permisos
reales (184 de 184 combinaciones de perfil y pantalla). Con los requerimientos de octubre quedaron
implementados RF-015 (atención social), RF-020 (el ítem tipo «tubo» mide las tareas realizadas), RF-025
(felicitaciones y reclamos) y RF-035 (comentarios). Sigue pendiente RF-031 (vista global por cargos). El
detalle está en [docs/REQUERIMIENTOS_V2.md](docs/REQUERIMIENTOS_V2.md) y en la sección 4 de
[PLAN_DE_PRUEBAS.md](PLAN_DE_PRUEBAS.md).

## Documentación

| Documento | Contenido |
|---|---|
| [docs/REQUERIMIENTOS_V2.md](docs/REQUERIMIENTOS_V2.md) | Requerimientos v2: los de octubre 2026 como RF y RNF, con criterio de aceptación y prueba |
| [docs/CASOS_DE_USO.md](docs/CASOS_DE_USO.md) | 19 gestiones de alto nivel y sus casos de detalle, cuadros y trazabilidad |
| [docs/DIAGRAMA_CLASES.md](docs/DIAGRAMA_CLASES.md) | Diagrama de clases desde los modelos reales, con las clases nuevas de octubre |
| [docs/diagramas/](docs/diagramas/) | Diagramas del informe que cambiaron: requerimientos, entidad-relación, paquetes y trazabilidad |
| [MODELO_DATOS.md](MODELO_DATOS.md) | Modelo de datos y justificación de cada modelo nuevo |
| [docs/BACKLOG_SPRINT.md](docs/BACKLOG_SPRINT.md) | Sprint backlog repriorizado por los requerimientos de octubre |
| [docs/PLAN_MANTENCION.md](docs/PLAN_MANTENCION.md) | Mantención correctiva, preventiva, adaptativa y perfectiva, con roles, recursos y calendario |
| [docs/NORMATIVAS_Y_ESTANDARES.md](docs/NORMATIVAS_Y_ESTANDARES.md) | Leyes 19.628 y 21.719, OWASP Top 10, ISO/IEC 25010 y estándares de código |
| [docs/RESULTADOS.md](docs/RESULTADOS.md) | Resultados medidos (pruebas, cobertura, requerimientos, tiempos) con CSV para gráficos |
| [docs/DEMO_EXPOSICION.md](docs/DEMO_EXPOSICION.md) | Guía de la exposición: flujos en vivo, guion y estructura |
| [docs/PREGUNTAS_DEFENSA.md](docs/PREGUNTAS_DEFENSA.md) | Preguntas probables de la defensa con su respuesta |

## Autoría de los commits

El historial de `main` incluye 9 commits firmados como «Tu Nombre <tu@email.com>», una firma genérica de Git
que no identifica a un integrante. Como la evaluación considera los aportes de cada uno, aquí queda quién los hizo:

| Commit | Fecha | Descripción | Autor real |
|---|---|---|---|
| 5bce630 | 2026-09-23 | Initial project upload | [COMPLETAR POR EL GRUPO] |
| 25431ec | 2026-09-26 | feat: integra modelos relacionales, migraciones y mejoras de administración | [COMPLETAR POR EL GRUPO] |
| c42daec | 2026-09-26 | fix: mejora busqueda, historico y archivos estaticos | [COMPLETAR POR EL GRUPO] |
| 7271a86 | 2026-09-26 | Arreglo de Errores y Dependencias | [COMPLETAR POR EL GRUPO] |
| 647d6f0 | 2026-09-26 | corrigiendo las rutas | [COMPLETAR POR EL GRUPO] |
| dfc310e | 2026-09-27 | Mudanza de base de datos | [COMPLETAR POR EL GRUPO] |
| ffbb5e2 | 2026-11-09 | Actualizar proyecto SGR y mejorar usabilidad (llegó con el pull request #16) | [COMPLETAR POR EL GRUPO] |
| 7b1a99f | 2026-11-12 | Completar permisos operativos por perfil (llegó con el pull request #16) | [COMPLETAR POR EL GRUPO] |
| d279465 | 2026-11-20 | fix: tilde mal codificada en un comentario de settings.py | [COMPLETAR POR EL GRUPO] |

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
mysqldump --no-tablespaces -u gestion_user -p gestion_laserena > ~/respaldo_$(date +%F).sql   # debe terminar en «Dump completed»
git pull
source venv/bin/activate && pip install -r requirements.txt
nano .env                                  # agregar EMAIL_BACKEND, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD...
python manage.py migrate --plan            # lista las migraciones pendientes antes de aplicarlas
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

Qué hacen las migraciones de perfiles y permisos de la Evaluación Sumativa 3:

| Migración | Qué cambia | ¿Toca datos? |
|---|---|---|
| `0015_perfiles_de_acceso` | Crea los perfiles como grupos de Django y asigna uno a cada usuario según sus roles | Sí: `auth_group`, `auth_group_permissions`, `auth_user_groups` |
| `0016_textos_tubo_de_trabajo` | Nombres visibles «tarea» y «tubo de trabajo» | No: solo textos, sin SQL |
| `0017_sin_solicitar_correccion` | Las actividades, evidencias y validaciones en «corrección» pasan a «rechazada» y conservan su observación | Sí: actualiza esas filas, no borra ninguna |
| `0018_perfiles_por_jerarquia` | Renombra Supervisor a Coordinador y Administrativo a Funcionario, crea Delegado y mueve allí a los delegados y verificadores | Sí: grupos y asignaciones de usuarios |
| `0019_eliminar_actividad_solo_coordinacion` | Da al Coordinador el permiso `delete_actividad` | Sí: una fila de `auth_group_permissions` |
| `0020_nombres_legibles_de_modelos` | Nombres legibles de cinco modelos | No: solo textos, sin SQL |
| `0021_reglas_sgr` | Crea las tablas de Organizacion, Ajuste, Ausencia, CasoSocial y Comentario; agrega a Actividad `tipo_accion`, `gestion_interna`, `cuenta_puntaje`, `motivo_sin_puntaje` y `organizacion`; a Compromiso `item`, `solicitante_telefono`, `organizacion` y `gestion_interna`; a ItemMedible `tipo_calculo` | No mueve filas: tablas y columnas nuevas con valores por defecto (las actividades existentes quedan como «ejecución», sin gestión interna y con puntaje) |
| `0022_consolidar_perfiles` | Renombra el perfil (grupo) Funcionario a **Profesional**; si ya existían los dos, mueve los usuarios al Profesional y elimina el perfil Funcionario | Sí: `auth_group` y `auth_user_groups` |
| `0023_ajuste_emisor_ajuste_origen_and_more` | Emisor y origen del ajuste; datos de registro de la organización (socios, fechas, número de registro) | No: columnas nuevas |
| `0024_migrar_roles_obsoletos` | Mueve `verificador` a `delegado`, mueve usuarios de `consulta` al perfil y rol Profesional y **elimina los roles** `verificador` y `consulta` | Sí: `funcionario_rol`, `auth_user_groups` y `rol` (no se revierte) |
| `0025_permisos_perfiles_operativos` | Asigna a cada perfil permisos para los mantenedores y operaciones que le corresponden | Sí: grupos y permisos |
| `0026_alter_ajuste_respaldo` | El respaldo del ajuste acepta solo JPG, PNG o PDF de hasta 5 MB | No: solo la validación |
| `0027_delegado_ve_ajustes` | Da al Delegado `view_ajuste` para consultar los ajustes de su delegación | Sí: una fila en `auth_group_permissions` (se revierte) |
| `0028_ausencia_emergencia_delegado_ve_ausencias` | Agrega el tipo de ausencia «Emergencia» y da al Delegado `view_ausencia` | Sí: una fila en `auth_group_permissions` (se revierte); el tipo nuevo solo cambia las opciones del campo |

En un servidor que ya está en `f910537` (PR #16), `migrate --plan` debe listar solo la `0027` y la `0028`.

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
- Login con cada cuenta demo y su panel (Administrador, Coordinador, Delegado, Profesional).
- Mantenedores con CRUD y búsqueda; restricciones al entrar con un perfil sin permiso.
- Recuperación de contraseña: solicitud, correo recibido, enlace, cambio e ingreso con la nueva clave.
- phpMyAdmin (`/phpmyadmin/`) mostrando tablas, estructura, relaciones y registros.

## Evidencia de uso de IA

Documenta en `evidencias_ia.md` (o en el documento tecnico entregable) los
prompts usados durante el desarrollo, las respuestas obtenidas y como se
aplicaron al codigo final.
