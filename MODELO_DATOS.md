# Modelo de datos

La estructura se define en `delegaciones_app/models.py`. Django crea y modifica
las tablas al ejecutar las migraciones (`python manage.py migrate`); no se crean
manualmente desde phpMyAdmin. El ORM usa estas mismas tablas en las vistas propias del
sistema; desde la Evaluación Sumativa 3 no se usa Django Admin.

Los perfiles de acceso (Administrador, Coordinador, Delegado y Profesional) son las tablas de grupos y
permisos de `django.contrib.auth` (`auth_group`, `auth_group_permissions`, `auth_user_groups`).
La migración `0015_perfiles_de_acceso` creó los tres perfiles de la pauta (Administrador, Supervisor y
Administrativo) y la `0018_perfiles_por_jerarquia` los dejó según la jerarquía de la Municipalidad:
renombra Supervisor a Coordinador y Administrativo a Funcionario (conservan su id, permisos y usuarios),
crea Delegado y mueve allí a los usuarios con rol delegado o verificador. La
`0019_eliminar_actividad_solo_coordinacion` agrega al Coordinador el permiso `delete_actividad`
(una fila de `auth_group_permissions`): eliminar actividades queda para Coordinador y Administrador.

**Perfil y rol.** El perfil es el nivel de permisos; el rol, la función y el alcance. Los dos roles que
revisan evidencias quedan así:

- `delegado`: trabaja su delegación (tubo de trabajo, actividades) y además verifica, con las mismas
  funciones del verificador pero limitadas a su delegación. Usa el perfil Delegado.
- `verificador`: se conserva para no romper datos existentes. Revisa evidencias de su delegación o, si no
  tiene, de todas. También usa el perfil Delegado.

Revisar exige el rol y el permiso `add_validacion` del perfil. La tabla `rol` solo guarda el nombre
(`nombre_rol`), así que esta descripción vive en la documentación y en `permisos.py`; la migración 0018
no modifica las tablas `rol`, `funcionario` ni `funcionario_rol`.

**Equivalencia de nombres.** «Tubo de trabajo» en la interfaz = modelo `Compromiso` (tabla
`compromiso`) = «Agenda colectiva» del diseño (CU-12). Cada registro del tubo se muestra como una
«tarea». La migración `0016_textos_tubo_de_trabajo` solo cambia los nombres visibles y las etiquetas de
los estados; no ejecuta SQL ni modifica datos.

El modelo implementa las 17 clases del diseño (diagrama de clases del informe),
más dos tablas adicionales: `FuncionarioRol`, que resuelve la relación
muchos a muchos entre funcionarios y roles, y `MedicionDelegacion`, que conserva
el histórico importado de la Matriz SGR. Los requerimientos de octubre 2026 agregaron cinco modelos
(`Organizacion`, `Ajuste`, `Ausencia`, `CasoSocial` y `Comentario`, sección «Modelos de los requerimientos
de octubre 2026»). En total son 24 tablas propias. El diagrama de clases actualizado está en
[docs/DIAGRAMA_CLASES.md](docs/DIAGRAMA_CLASES.md).

## Las 17 clases y las dos tablas adicionales

### Organización y acceso

| Clase | Propósito | Relaciones principales |
|---|---|---|
| `Delegacion` | Unidad territorial municipal. | Tiene funcionarios, actividades y compromisos. Calcula su cumplimiento ponderado. |
| `Cargo` | Cargo de los funcionarios y su vigencia. | Tiene funcionarios e ítems medibles. |
| `Rol` | Rol que define la función y el alcance: administrador, coordinador, delegado (también verifica en su delegación) y funcionario. La migración `0024` trasladó y eliminó los roles retirados `verificador` y `consulta`. | Se asigna a funcionarios mediante `FuncionarioRol`. |
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
| `Validacion` | Decisión de un verificador sobre una evidencia: aprobada o rechazada (con motivo). | FK a `Evidencia` y al verificador. Queda como historial. |
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
Delegacion     1 ── N Organizacion (opcional) ── N Actividad / Compromiso (opcional)
Periodo        1 ── N Ajuste ── 0..1 Funcionario o 0..1 Delegacion (destinatario)
Funcionario    1 ── N Ausencia ── 1 Periodo
Funcionario    1 ── N CasoSocial
Actividad      1 ── N Comentario (o Compromiso 1 ── N Comentario)
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
| RN-005: cumplimiento ponderado, con tope (120 % por defecto desde la regla 7 de octubre, configurable por período con `maximo_cumplimiento`). | `Indicador.calcular_cumplimiento()` |
| RN-006: el cumplimiento colectivo debe alcanzar el umbral del período. | `Periodo.alcanza_umbral()` |
| RN-007: meta esperada al día = días transcurridos / días totales × 100. | `Periodo.porcentaje_esperado()` |
| RN-008: semáforo verde si alcanza lo esperado, ámbar si llega al 60 % de lo esperado, rojo si no. | `Periodo.calcular_semaforo()` |
| RN-010: el código verificador de una actividad es único e inmutable. | `Actividad.generar_codigo_verificador()` y `save()` |
| RN-013: un período cerrado no se modifica, ni sus ítems, metas, parámetros e indicadores; solo se reabre con motivo y queda auditado. | `Periodo.verificar_editable()` y `ControlPeriodoCerradoMixin` |

## Modelos de los requerimientos de octubre 2026

La reunión de octubre de 2026 agregó cinco modelos (migraciones `0021` a `0028`) y campos en `Actividad`,
`Compromiso` e `ItemMedible`. Con ellos el sistema tiene 24 tablas propias. Cada modelo se justifica por el
problema del municipio que resuelve y por la alternativa de diseño que se descartó.

### `Organizacion` (tabla `delegaciones_app_organizacion`)

- **Por qué existe.** La matriz registra a qué organización comunitaria se atendió y el municipio entregó su
  base de juntas de vecinos y organizaciones (2.709). Sin un modelo propio, el nombre de la organización se
  escribiría a mano en cada actividad, con variantes que impiden contar por organización o por tipo.
- **Relaciones.** `Delegacion` 1 a 0..N `Organizacion` (opcional: hay organizaciones sin territorio
  verificable); `Organizacion` 0..1 a 0..N `Actividad` y 0..1 a 0..N `Compromiso`. Todas con `PROTECT`: una
  organización con actividades no se borra, se desactiva (`activa`).
- **Restricciones.** Única por nombre y territorio (`organizacion_nombre_territorio_unico`); el tipo es uno de
  los del documento de octubre (junta de vecinos, funcional, adulto mayor, deportiva, cultural, comité) o
  «sin clasificar»; la actividad y la tarea solo aceptan organizaciones de su misma delegación
  (`Actividad.clean`, `Compromiso.clean`).
- **Decisión.** Se prefirió un catálogo propio a reutilizar `Catalogo`, porque la organización tiene datos
  legales (personalidad jurídica, registro, socios, fecha de constitución) y una verificación propia
  (`verificada`) que el catálogo genérico no tiene.

### `Ajuste` (tabla `delegaciones_app_ajuste`)

- **Por qué existe.** Regla 8: las felicitaciones suman y los reclamos restan al cumplimiento, pero solo con
  respaldo formal, informados por el delegado y aceptados por la coordinación. Hace falta guardar quién
  informó, quién decidió, cuándo y con qué documento.
- **Relaciones.** `Periodo` 1 a 0..N `Ajuste`; destinatario `Funcionario` 0..1 a 0..N o `Delegacion` 0..1 a
  0..N (exactamente uno de los dos); `informado_por` y `aplicado_por` a `Funcionario` 1 a 0..N.
- **Restricciones.** `clean` exige un solo destinatario, respaldo y emisor si es felicitación; el respaldo es
  JPG, PNG o PDF de hasta 5 MB (`0026`); estados informado, aplicado o rechazado; un período cerrado no se
  modifica (`ControlPeriodoCerradoMixin`). Al quedar aplicado o rechazado recalcula las metas de su
  destinatario (`actualizar_indicadores`).
- **Decisión.** Se descartó guardar el ajuste como un número en `Indicador.ajuste`, que era lo que había:
  un número no deja trazabilidad (quién, cuándo, con qué respaldo) ni permite rechazar. El indicador conserva
  el campo `ajuste` como resultado del cálculo, y el modelo `Ajuste` es la fuente.

### `Ausencia` (tabla `delegaciones_app_ausencia`)

- **Por qué existe.** Regla 9: los días libres, vacaciones, días administrativos, licencias y emergencias se
  descuentan de lo esperado al día; sin eso, un funcionario con licencia aparece en rojo.
- **Relaciones.** `Funcionario` 1 a 0..N `Ausencia`; `Periodo` 1 a 0..N `Ausencia`; `registrada_por` a
  `Funcionario`.
- **Restricciones.** Término no anterior al inicio; no se superpone con otra ausencia del mismo funcionario;
  tipo de una lista cerrada (con «Emergencia» desde la `0028`); período cerrado no se modifica. Al guardarla o
  borrarla recalcula las metas del funcionario.
- **Decisión.** Es un modelo propio y no un campo del usuario (por ejemplo, «en licencia: sí o no») porque una
  persona tiene varias ausencias en un trimestre, cada una con fechas, tipo y quién la registró, y el cálculo
  necesita los días exactos (`reglas.dias_ausencia` cuenta los días sin duplicar los que se traslapan). Un
  campo del usuario solo diría el estado de hoy y perdería el historial que justifica el ajuste de la meta.

### `CasoSocial` (tabla `delegaciones_app_casosocial`)

- **Por qué existe.** El área social atiende a un mismo vecino hasta en tres gestiones (RF-015, hojas «G SOC»
  de la matriz) y la matriz lo registra por etapas.
- **Relaciones.** `Funcionario` 1 a 0..N `CasoSocial`.
- **Restricciones.** Etapa entre 1 y 3 (`clean`); la vista rechaza una cuarta gestión del mismo funcionario
  con el mismo vecino; tipo de una lista cerrada (informe social, subsidios, PGU, SUF, SAP, derivación).
- **Decisión.** Se separó de `Actividad` porque guarda datos personales sensibles del vecino (situación
  social) que no deben verse en las listas de actividades ni en los informes generales; con un modelo aparte
  el acceso se controla con sus propios permisos (`add_casosocial` solo para el Profesional).

### `Comentario` (tabla `delegaciones_app_comentario`)

- **Por qué existe.** RF-035: coordinar observaciones sobre una actividad o una tarea sin usar el campo de la
  actividad ni canales externos.
- **Relaciones.** `Actividad` 0..1 a 0..N `Comentario` y `Compromiso` 0..1 a 0..N `Comentario` (`CASCADE`: el
  comentario no tiene sentido sin su registro); `autor` a `Funcionario`.
- **Restricciones.** Pertenece a una actividad o a una tarea, no a ambas (`clean`).
- **Decisión.** Un solo modelo con dos llaves opcionales en vez de dos tablas de comentarios, porque el
  comentario tiene la misma forma en los dos casos y la regla «uno u otro» se valida en `clean`.

### Campos nuevos en modelos existentes

| Modelo | Campo | Para qué |
|---|---|---|
| `Actividad` | `tipo_accion` (ejecución o gestión previa) | Regla 5: la gestión previa no puntúa |
| `Actividad` | `gestion_interna` | Regla 1: el usuario es el delegado; casilla en el formulario desde esta versión |
| `Actividad` | `cuenta_puntaje`, `motivo_sin_puntaje` | Resultado de `reglas.evaluar_puntaje`: la actividad se guarda para el historial aunque no sume |
| `Compromiso` | `item`, `solicitante_telefono`, `gestion_interna`, `organizacion` | Ítem tipo «tubo»: porcentaje de tareas realizadas con contacto |
| `ItemMedible` | `tipo_calculo` (actividades o tubo) | La matriz mide «Soluciones de ingresos al tubo» como porcentaje, no como conteo |

### Reglas de octubre en el modelo

| Regla | Dónde se aplica |
|---|---|
| RN-014: puntúa solo con contacto, sin gestión interna y sin gestión previa (reglas 1, 2 y 5). | `reglas.evaluar_puntaje()` desde `Actividad.clean()` |
| RN-015: máximo de ingresos por autor y día, parámetro `max_ingresos_diarios` (regla 3). | `reglas.validar_limite_diario()` |
| RN-016: cierre semanal al registrar, no al corregir sin cambiar el día (regla 4). | `reglas.validar_fecha_actividad()` |
| RN-017: tope configurable (120 %), felicitaciones +10 (máximo 3) y reclamos -30 (reglas 7 y 8). | `Indicador.calcular_cumplimiento()` |
| RN-018: lo esperado al día descuenta las ausencias (regla 9). | `reglas.porcentaje_esperado_ajustado()` |

## Concurrencia

El control de concurrencia (RF-034) usa el campo `version` de `Actividad` y
`Compromiso`: si dos usuarios editan el mismo registro, gana quien guarda
primero y el otro recibe el aviso de que debe recargar.

## Ocho mantenedores visuales

La interfaz presenta exactamente ocho mantenedores en `/administracion/`:
Delegaciones, Cargos, Roles, Funcionarios, Catálogo, Períodos, Ítems medibles
y Metas. Los ocho salen de un solo registro (`MANTENEDORES` en
`delegaciones_app/crud.py`) y comparten las mismas cuatro vistas genéricas:
listado con búsqueda, nuevo, modificar y eliminar con confirmación.

- Roles y Funcionarios son solo de administración. Los demás los administran
  administración y coordinación.
- En delegaciones, cargos, funcionarios y catálogo, eliminar depende de los
  datos relacionados (`datos_relacionados` en `crud.py`, que recorre las tablas
  que apuntan al registro). Sin datos relacionados la fila se elimina; un
  funcionario se elimina junto con su cuenta y sus roles asignados. Con datos
  relacionados (por ejemplo, actividades o registros de auditoría) la fila se
  desactiva para conservar el historial, la confirmación dice cuáles son esos
  datos y un funcionario desactivado también pierde su cuenta activa. Una fila
  inactiva se vuelve a activar desde la misma lista.
- La migración 0020 da nombres legibles a cinco modelos (actividades, roles
  asignados, mediciones de delegación, períodos y registros de auditoría) para
  esos mensajes y para la página de perfiles. Solo cambia textos.
- Los seis roles que consultan los permisos son del sistema y no se eliminan ni se renombran.
  Nadie puede eliminar ni desactivar su propia cuenta.
- Los períodos tienen las acciones Iniciar, Cerrar y Reabrir (con motivo) en su
  listado.
- Al guardar una meta se genera su indicador; al eliminarla, se avisa cuántos
  indicadores se pierden.

Las actividades (`/actividades/`) y los compromisos (`/agenda/`) tienen sus
propias pantallas, con filtros por rol y delegación, y no son mantenedores
adicionales. `MedicionDelegacion` conserva los indicadores importados y se consulta en el
Resumen; no tiene mantenedor.

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
- La revisión solo aprueba o rechaza. Rechazar exige un motivo. Solo una validación
  aprobada hace que la actividad aporte al avance.
- El archivo se abre o descarga desde el detalle de la actividad, por la vista protegida
  `evidencia_archivo`: exige sesión y los mismos permisos de la actividad, y un intento fuera del ámbito queda
  en la auditoría. Nginx no publica `/media/`.
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
- La agenda incluye un resumen por responsable y estado, con el porcentaje realizado y el pendiente
  («pendiente» es todo lo que aún no está realizado). Sus totales coinciden con el detalle filtrado
  (RF-021).

### Actividad reciente y alertas

- La actividad reciente (RF-030) informa, por funcionario, la cantidad de registros del período, la
  fecha del último ingreso (la fecha en que se registró, no la del hecho), los días sin ingreso y el
  promedio diario sobre los días transcurridos del período. Está en la ficha personal y en un informe.
- Las alertas (RF-037) están en `/gestion/alertas/` y cada una trae motivo, responsable, fecha y enlace.
  Son cuatro: compromisos vencidos o próximos a vencer, evidencias pendientes de revisión (solo para
  quien puede revisar), funcionarios con metas abiertas sin registros hace más de
  `ALERTA_DIAS_SIN_REGISTRO` días (7 por defecto) y delegaciones en rojo, es decir, bajo el 60 % de lo
  esperado al día (RN-008). Cada usuario ve solo lo que corresponde a su ámbito.

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
- La opción «Solicitar corrección» se eliminó: la migración `0017_sin_solicitar_correccion`
  convierte cada fila con estado «correccion» en «rechazada» (en `actividad`, `evidencia` y
  `validacion`) y conserva la observación como motivo del rechazo. `Validacion.version` es el número
  de revisión de la evidencia.
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
- La migración se ensayó primero sobre SQLite y después sobre MySQL 8.4, con
  una copia de la base real del servidor. En ambos casos las cantidades de
  registros se conservaron y las llaves foráneas quedaron consistentes. El
  21-10-2026 se aplicó en el servidor con el mismo resultado. En cualquier otra
  instalación con datos del modelo anterior conviene repetir el ensayo sobre
  una copia de la base antes de migrar.

## Alcance y requisitos pendientes

Las pruebas y su cobertura por caso de uso y requisito están en
[PLAN_DE_PRUEBAS.md](PLAN_DE_PRUEBAS.md). Los requisitos funcionales que no
están completos son:

| Requisito | Estado |
|---|---|
| RF-015 Registrar atención social por etapas | Implementado con `CasoSocial` (octubre 2026): hasta tres gestiones por vecino. |
| RF-020 Relacionar agenda y medición | Implementado con el ítem tipo «tubo»: el porcentaje de tareas realizadas alimenta el indicador y se recalcula al cambiar el estado de una tarea. |
| RF-025 Aplicar incentivos y penalizaciones | Implementado con `Ajuste`: felicitaciones y reclamos aplicados por la coordinación entran al cálculo. |
| RF-031 Mostrar vista global por cargos | No implementado (postergado en el backlog, ver docs/BACKLOG_SPRINT.md). |
| RF-035 Facilitar coordinación | Implementado con `Comentario`: comentarios visibles en el detalle de la actividad. |
