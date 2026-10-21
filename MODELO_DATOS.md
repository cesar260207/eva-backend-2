# Modelo de datos

La estructura se define en `delegaciones_app/models.py`. Django crea y modifica
las tablas al ejecutar las migraciones (`python manage.py migrate`); no se crean
manualmente desde phpMyAdmin. El ORM usa estas mismas tablas en las vistas y en
Django Admin.

El modelo implementa las 17 clases del diseño (diagrama de clases del informe),
más dos tablas adicionales: `FuncionarioRol`, que resuelve la relación
muchos a muchos entre funcionarios y roles, y `MedicionDelegacion`, que conserva
el histórico importado de la Matriz SGR. En total son 19 tablas propias.

## Las 17 clases y las dos tablas adicionales

### Organización y acceso

| Clase | Propósito | Relaciones principales |
|---|---|---|
| `Delegacion` | Unidad territorial municipal. | Tiene funcionarios, actividades y compromisos. Calcula su cumplimiento ponderado. |
| `Cargo` | Cargo de los funcionarios y su vigencia. | Tiene funcionarios e ítems medibles. |
| `Rol` | Rol que define permisos: administrador, coordinador, delegado, funcionario, verificador y consulta. | Se asigna a funcionarios mediante `FuncionarioRol`. |
| `Funcionario` | Persona con cuenta de acceso, cargo, delegación opcional y uno o más roles. | `usuario` uno a uno con el usuario de Django; autor de actividades y compromisos. |
| `UsuarioMaestro` | Superusuario con alcance total. | `usuario` uno a uno opcional con el usuario de Django. |
| `FuncionarioRol` (adicional) | Asigna un rol a un funcionario. | Único por funcionario y rol. |

### Medición

| Clase | Propósito | Relaciones principales |
|---|---|---|
| `Periodo` | Ventana de medición con fechas, estado (borrador, abierto, cerrado), días computables y umbral colectivo. | Tiene ítems, parámetros e indicadores. |
| `ParametroVersionado` | Parámetro de cálculo de un período, por ejemplo el máximo de cumplimiento. | FK a `Periodo`; único por período y clave. |
| `ItemMedible` | Ítem que se evalúa a un cargo en un período, con su ponderación. | FK a `Cargo` y `Periodo`; tiene metas. |
| `Catalogo` | Actividades, servicios, tipos de atención e ítems normalizados. | Código único; lo usan las actividades. |
| `Meta` | Objetivo de un funcionario sobre un ítem, con su ponderador. | FK a `ItemMedible` y `Funcionario`; tiene indicadores. |
| `Indicador` | Resultado calculado de una meta: avance, cumplimiento, cumplimiento ponderado y semáforo. | FK a `Meta` y `Periodo`. Cada cálculo agrega un registro nuevo. |
| `MedicionDelegacion` (adicional) | Histórico por delegación y fecha, importado de la Matriz SGR. | FK a `Delegacion`; delegación y fecha únicas en conjunto. |

### Operación

| Clase | Propósito | Relaciones principales |
|---|---|---|
| `Actividad` | Atención o acción territorial registrada por un funcionario, con código verificador único. | FK a `Funcionario`, `Delegacion`, `ItemMedible`, `Catalogo` y, opcional, `Compromiso`. |
| `Evidencia` | Archivo que respalda una actividad (JPG, PNG o PDF, hasta el tamaño configurado). | FK a `Actividad` (se borra con ella) y a su autor. |
| `Validacion` | Decisión de un verificador sobre una evidencia: aprobada, rechazada o con corrección pedida. | FK a `Evidencia` y al verificador. Queda como historial. |
| `Compromiso` | Solicitud o acuerdo territorial con responsable, plazo, estado y folio único. | FK a `Delegacion`, `Funcionario` e `ItemMedible` opcional. |
| `HistorialCompromiso` | Cada cambio de estado, derivación o cierre de un compromiso, con su autor. | FK a `Compromiso` y `Funcionario`. |
| `Auditoria` | Registro inmutable de las operaciones críticas y de los accesos denegados. | FK opcional a `Funcionario` o `UsuarioMaestro`. |

Django también crea tablas internas de autenticación, sesiones y permisos; no
son mantenedores del equipo.

## Relaciones resumidas

```text
Usuario Django 1 ── 1 Funcionario ── N FuncionarioRol ── 1 Rol
Usuario Django 1 ── 0..1 UsuarioMaestro
Delegacion     1 ── N Funcionario (opcional: los roles globales no tienen)
Cargo          1 ── N Funcionario
Cargo          1 ── N ItemMedible ── N Meta ── N Indicador
Periodo        1 ── N ItemMedible
Periodo        1 ── N ParametroVersionado
Periodo        1 ── N Indicador
Funcionario    1 ── N Meta
Funcionario    1 ── N Actividad (autor) ── N Evidencia ── N Validacion
ItemMedible    1 ── N Actividad
Catalogo       1 ── N Actividad
Delegacion     1 ── N Actividad
Delegacion     1 ── N Compromiso ── N HistorialCompromiso
Funcionario    1 ── N Compromiso (responsable)
Compromiso     1 ── N Actividad (opcional)
Delegacion     1 ── N MedicionDelegacion
Funcionario    1 ── N Auditoria
```

`1 ── N` indica que una fila del lado izquierdo puede relacionarse con varias
del lado derecho; cada fila hija apunta a una fila padre mediante una llave
foránea. Las reglas `on_delete` protegen la información relacionada (`PROTECT`)
o eliminan a los hijos junto con su entidad dueña (`CASCADE`), según el modelo.
Las tablas llevan los nombres físicos del diagrama (`delegacion`, `cargo`,
`funcionario_rol`, `item_medible`, etc.).

## Reglas de negocio en el modelo

Las reglas viven en métodos y en `clean()` de los modelos, no en las vistas, de
modo que valen igual desde la aplicación, el admin y los comandos.

| Regla | Dónde se aplica |
|---|---|
| RN-001: las ponderaciones de un cargo en un período no superan 100 % al guardar un ítem y suman exactamente 100 % al iniciar el período. | `ItemMedible.clean()` y `Periodo.iniciar_periodo()` |
| RN-002: el valor objetivo de una meta es mayor que cero. | Validador de `Meta.valor_objetivo` |
| RN-003 y RN-009: el avance cuenta las actividades aprobadas del ítem, dentro del período, con una validación aprobada; si el funcionario de la meta tiene delegación, solo las de esa delegación. | `Meta.actividades_que_aportan()` e `Indicador.calcular_avance()` |
| RN-004: cumplimiento = avance / meta × 100. | `Meta.evaluar_progreso()` |
| RN-005: cumplimiento ponderado, con tope (150 % por defecto, configurable por período). | `Indicador.calcular_cumplimiento()` |
| RN-006: el cumplimiento colectivo debe alcanzar el umbral del período. | `Periodo.alcanza_umbral()` |
| RN-007: meta esperada al día = días transcurridos / días totales × 100. | `Periodo.porcentaje_esperado()` |
| RN-008: semáforo verde si alcanza lo esperado, ámbar si llega al 60 % de lo esperado, rojo si no. | `Periodo.calcular_semaforo()` |
| RN-010: el código verificador de una actividad es único e inmutable. | `Actividad.generar_codigo_verificador()` y `save()` |
| RN-013: un período cerrado no se modifica, ni sus ítems, metas, parámetros e indicadores; solo se reabre con motivo y queda auditado. | `Periodo.verificar_editable()` y `ControlPeriodoCerradoMixin` |

El control de concurrencia (RF-034) usa el campo `version` de `Actividad` y
`Compromiso`: si dos usuarios editan el mismo registro, gana quien guarda
primero y el otro recibe el aviso de que debe recargar.

## Ocho mantenedores visuales

La interfaz presenta exactamente ocho mantenedores en `/administracion/`:
Delegaciones, Cargos, Roles, Funcionarios, Catálogo, Períodos, Ítems medibles
y Metas. Los ocho salen de un solo registro (`MANTENEDORES` en
`delegaciones_app/crud.py`) y comparten las mismas cuatro vistas genéricas:
listado con búsqueda, nuevo, modificar y eliminar o desactivar.

- Roles y Funcionarios son solo de administración. Los demás los administran
  administración y coordinación.
- Donde corresponde se desactiva en vez de eliminar, para conservar el
  historial: delegaciones, cargos, funcionarios (que también desactiva su
  cuenta) y elementos de catálogo.
- Los seis roles que consultan los permisos son del sistema y no se eliminan ni se renombran.
  Nadie puede desactivar su propia cuenta.
- Los períodos tienen las acciones Iniciar, Cerrar y Reabrir (con motivo) en su
  listado.
- Al guardar una meta se genera su indicador; al eliminarla, se avisa cuántos
  indicadores se pierden.

Las actividades (`/actividades/`) y los compromisos (`/agenda/`) tienen sus
propias pantallas, con filtros por rol y delegación, y no son mantenedores
adicionales. `MedicionDelegacion` se administra solo en Django Admin, que
registra las 19 tablas.

### Reglas de las actividades

- Una actividad `aprobada` no se modifica ni se elimina desde la aplicación,
  para nadie, porque ya suma al avance. Un verificador, un coordinador o un
  administrador puede **anular su aprobación** con un motivo obligatorio: la
  actividad pasa a `rechazada`, deja de sumar, los indicadores se recalculan
  hacia abajo y la validación original queda en el historial.
- Una actividad `rechazada` sí se puede editar. Al guardarla vuelve a
  `pendiente`, para que el verificador revise la corrección.
- Solo quien la registró, la coordinación o la administración modifican una
  actividad. Los demás reciben un mensaje, y el intento queda en la auditoría.
- Eliminar una actividad borra también sus evidencias (`CASCADE`); la pantalla
  de confirmación indica cuántas se eliminan.
- No se registran ni modifican actividades de un período cerrado (RN-013).
- La fecha de la actividad debe caer dentro del período de su ítem, y el
  teléfono de contacto, si se informa, debe tener entre 6 y 20 caracteres:
  dígitos, espacios, guiones o paréntesis, con un `+` o un paréntesis inicial
  opcional.

### Reglas de las evidencias

- Formatos permitidos: JPG, JPEG, PNG y PDF. El tamaño máximo es de 5 MB y se
  cambia con `EVIDENCIA_TAMANO_MAXIMO_MB`. El rechazo informa el motivo exacto.
- El código de cada evidencia deriva del de su actividad (`EVD-...-01`) y no
  cambia.
- Rechazar o pedir corrección exige una observación. Solo una validación
  aprobada hace que la actividad aporte al avance.
- Django no borra del disco el archivo de una evidencia eliminada o reemplazada.

### Reglas de los compromisos

- El responsable y la fecha comprometida son obligatorios.
- Los estados avanzan: ingresado, pendiente, en proceso y realizado, y se pueden
  saltar etapas. Un compromiso realizado solo se reabre a «en proceso». Cada
  cambio queda en `HistorialCompromiso` con su autor y observación.
- Se considera próximo a vencer el que vence dentro de los días de
  `COMPROMISO_DIAS_ALERTA` (3 por defecto) y vencido el que pasó su fecha sin
  realizarse. Un compromiso vencido no se elimina: se conserva con su historial.
- Cerrar un compromiso exige una resolución, y uno realizado no se deriva.

## Auditoría

`Auditoria` registra altas, cambios y bajas de los mantenedores y del admin,
decisiones de validación, anulaciones, cambios de estado, reaperturas de
períodos, exportaciones de informes y accesos denegados por rol o por ámbito.
Es de solo lectura: un evento guardado no se vuelve a guardar ni se elimina, ni
individualmente ni en bloque, y el admin solo permite consultarla. La consulta
con filtros está en `/administracion/auditoria/` y es exclusiva de
administración.

## Migración de los JSON

`python manage.py seed_demo` carga `data/solicitudes.json` en `Compromiso`,
conservando folio, delegación, fechas, estado, eje y descripción. También carga
`data/metas_delegaciones.json` en `MedicionDelegacion` y crea delegaciones,
funcionarios, metas y actividades ficticias para la demostración. Los JSON son
fuentes de carga inicial; las páginas consultan la base relacional mediante
Django ORM.

El comando se puede volver a ejecutar: actualiza o reutiliza registros por sus
claves identificadoras para evitar duplicados. Los usuarios y registros de
demostración son sintéticos. Después de cargar los datos, o de cambiar metas
directamente en la base, `python manage.py calcular_indicadores` crea un
`Indicador` por cada meta de los períodos no cerrados.

## Comandos para crear y revisar el esquema

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py calcular_indicadores
python manage.py showmigrations
python manage.py plan_pruebas
```

`makemigrations` se ejecuta durante el desarrollo solo cuando cambian los
modelos; la instalación utiliza las migraciones ya versionadas. `plan_pruebas`
ejecuta las pruebas y regenera `PLAN_DE_PRUEBAS.md`.

En phpMyAdmin se selecciona `gestion_laserena` para inspeccionar tablas,
columnas, llaves foráneas y registros. Django genera el esquema a partir de las
migraciones.

## Ajustes respecto del diseño

El modelo de 17 clases del informe (Figuras 30 a 32 y 35) se implementa con
estos ajustes mínimos, porque el diseño no cubre algo que el sistema ya usa:

| N.º | Ajuste | Motivo |
|---|---|---|
| 1 | `Funcionario.usuario`: uno a uno con el usuario de Django. | El diseño no indica cómo inicia sesión un funcionario. |
| 2 | `UsuarioMaestro.usuario`: uno a uno opcional con el usuario de Django. | Enlaza a los superusuarios con su usuario maestro. |
| 3 | `Funcionario.delegacion` admite vacío. | Los roles de alcance global (administrador, coordinador) no pertenecen a una delegación. |
| 4 | `Compromiso` conserva `folio` (único), `eje`, `delegacion`, `descripcion` y `fecha_ingreso`. | Vienen de `data/solicitudes.json` y se muestran en la agenda. |
| 5 | `MedicionDelegacion` se conserva como entidad adicional. | Es el histórico importado de la Matriz SGR; no es una de las 17 clases. |
| 6 | `Periodo.nombre` (único). | Se muestra en las pantallas. |
| 7 | `Actividad.creada` y `Actividad.actualizada`. | Ordenan los listados. |
| 8 | `Delegacion.enfasis`. | Se muestra y se busca en el CRUD de delegaciones; se conserva para no perder el texto. |
| 9 | `Actividad.delegacion`. | Un coordinador sin delegación registra actividades de cualquier delegación, y el avance de cada meta se mide por delegación. |
| 10 | `Compromiso.creado`. | Ordena la agenda. |

### Decisiones de interpretación

- `ParametroVersionado` es único por período y clave. El tope de cumplimiento
  (RN-005) usa la clave `maximo_cumplimiento` y, si no existe, 150.
- `dias_computables` cuenta días de calendario.
- Algunos métodos reciben un parámetro más que el diagrama, porque la operación
  necesita saber quién la hace o sobre qué registro: `reabrir_periodo(motivo, usuario)`,
  `subir_evidencia(actividad, archivo)` y `set_estado`, `derivar_compromiso` y
  `cerrar_compromiso` con `autor`.
- Actividad y Evidencia tienen el estado adicional «correccion», que deja
  `Validacion.solicitar_correccion()`. `Validacion.version` es el número de
  revisión de la evidencia.
- `Indicador.ajuste` y `Validacion.resultado` se guardan, pero no entran en el
  cálculo, porque el informe no define cómo se aplican.
- Las transiciones de estado de un compromiso (avanzar, y reabrir un realizado
  solo a «en proceso») son una definición propia: el informe pide transiciones
  controladas sin detallarlas.
- Para anular una aprobación se agrega una validación «rechazada» en vez de
  borrar la «aprobada», de modo que el historial completo se conserve.

## Migración al modelo de 17 clases

Se aplicó el patrón ampliar, migrar y contraer, en las migraciones `0007` a
`0013`:

1. **Ampliar** (`0007` a `0009`): crea las tablas nuevas y agrega los campos
   nuevos como opcionales. Los campos antiguos que serían reemplazados admiten
   vacío, pero los formularios de entonces los seguían exigiendo.
   `Actividad.fecha_hora` y `HistorialCompromiso.autor_funcionario` son
   temporales: al contraer reemplazan a `fecha` y `autor` y toman su nombre.
2. **Migrar** (`0010_migrar_datos`): copia los datos con `RunPython` y se puede
   revertir. Informa en pantalla los casos especiales: códigos de catálogo
   repetidos, tipos de atención que no estaban en el catálogo, teléfonos
   recortados a 20 caracteres, períodos creados y sumas de ponderación
   distintas de 100 %. Las delegaciones sin funcionarios reciben un delegado
   provisional con cuenta inactiva, para conservar su meta.
3. **Contraer** (`0011` a `0013`): elimina los campos y tablas antiguos
   (`PerfilUsuario`, `CatalogoItem`, `PeriodoMedicion` y `MetaMedicion`) cuando las
   vistas ya usan el modelo nuevo, y ajusta los nombres de las tablas a los del
   diagrama. Los renombres se escribieron a mano con `RenameField` para no
   perder datos.

La migración `0014` agrega el validador del tamaño de las evidencias y no
cambia datos.

Después de migrar se ejecuta `python manage.py calcular_indicadores`. Una
actividad aprobada sin evidencias, permitida por el sistema anterior, no aporta
al avance (RN-009).

**Advertencias para un despliegue real**

- La contracción elimina tablas y campos: no tiene vuelta atrás segura sobre
  datos reales. Antes de migrar hay que hacer un respaldo (`mysqldump`) y, para
  volver atrás, se restaura ese respaldo.
- La migración se ensayó sobre SQLite con datos del esquema anterior (las
  cantidades de registros se conservaron y las llaves foráneas quedaron
  consistentes). Las migraciones `0011` a `0013` aún no se ejecutaron sobre
  MySQL: conviene ensayarlas primero sobre una copia de la base.

## Alcance y requisitos pendientes

Las pruebas y su cobertura por caso de uso y requisito están en
[PLAN_DE_PRUEBAS.md](PLAN_DE_PRUEBAS.md). Los requisitos funcionales que no
están completos son:

| Requisito | Estado |
|---|---|
| RF-015 Registrar atención social por etapas | No implementado. |
| RF-020 Relacionar agenda y medición | No implementado: cerrar un compromiso no alimenta el indicador del ítem. |
| RF-021 Generar resumen colectivo | Parcial: la agenda totaliza por estado y plazo, pero no por funcionario ni con porcentajes. |
| RF-025 Aplicar incentivos y penalizaciones | No implementado: `Indicador.ajuste` se guarda pero no entra al cálculo. |
| RF-030 Medir actividad reciente | Parcial: informa la fecha del último cálculo y los días transcurridos. |
| RF-031 Mostrar vista global por cargos | No implementado. |
| RF-035 Facilitar coordinación | No implementado: no hay comentarios asociados a registros. |
| RF-037 Emitir alertas | Parcial: solo alerta por vencimiento de compromisos. |
