# Modelo de datos

La estructura se define en `delegaciones_app/models.py`. Django crea y modifica
las tablas al ejecutar las migraciones (`python manage.py migrate`); no se crean
manualmente desde phpMyAdmin. El ORM usa estas mismas tablas en las vistas y en
Django Admin.

## Entidades del proyecto

| Entidad | Propósito | Relaciones principales |
|---|---|---|
| `Delegacion` | Unidad territorial municipal. | Se relaciona con perfiles, actividades, compromisos, metas y mediciones. |
| `PerfilUsuario` | Rol, cargo y ámbito territorial de una cuenta. | `usuario` uno a uno con usuario Django; `delegacion` opcional. |
| `CatalogoItem` | Catálogo de actividades, servicios, tipos de atención e ítems de medición. | Categoría y código deben ser únicos en conjunto. |
| `PeriodoMedicion` | Periodo y parámetros usados para evaluar resultados. | Entidad independiente con fechas y umbrales. |
| `Actividad` | Atención o acción territorial registrada por un funcionario. | FK a `Delegacion` y usuario funcionario; puede tener evidencias. |
| `Evidencia` | Archivo y comentario que respaldan una actividad. | FK a `Actividad` y FK opcional al usuario que revisó. |
| `Compromiso` | Solicitud o acuerdo territorial con responsable, estado y fechas. | FK a `Delegacion` y usuario responsable; puede tener historial. |
| `HistorialCompromiso` | Cambios de estado y observaciones de un compromiso. | FK a `Compromiso` y usuario autor. |
| `MetaMedicion` | Objetivo por delegación y periodo; avance calculable desde actividades aprobadas. | FK a `Delegacion`. |
| `MedicionDelegacion` | Resultado por delegación y fecha: cumplimiento, meta, semáforo y observación. | FK a `Delegacion`; delegación y fecha son únicas en conjunto. |
| `Auditoria` | Registro de acciones relevantes efectuadas por usuarios. | FK al usuario que realizó la acción. |

Django también crea tablas internas de autenticación, sesiones y permisos; no
son mantenedores del equipo.

## Relaciones resumidas

```text
Usuario Django 1 ── 1 PerfilUsuario ── 0..1 Delegacion
Delegacion     1 ── N Actividad ────── N Evidencia
Usuario        1 ── N Actividad (funcionario)
Usuario        1 ── N Evidencia (revisor, opcional)
Delegacion     1 ── N Compromiso ───── N HistorialCompromiso
Usuario        1 ── N Compromiso (responsable)
Usuario        1 ── N HistorialCompromiso (autor)
Delegacion     1 ── N MetaMedicion
Delegacion     1 ── N MedicionDelegacion
Usuario        1 ── N Auditoria
```

`1 ── N` indica que una fila del lado izquierdo puede relacionarse con varias
del lado derecho; cada fila hija apunta a una fila padre mediante una llave
foránea. Las reglas `on_delete` protegen información relacionada o eliminan
evidencias e historial al borrar su entidad dueña, según el modelo.

## Migración de los JSON

`python manage.py seed_demo` carga `data/solicitudes.json` en `Compromiso`,
conservando folio, delegación, fechas, estado, eje y descripción. También carga
`data/metas_delegaciones.json` en `MedicionDelegacion`. Los JSON son fuentes de
carga inicial; las páginas consultan la base relacional mediante Django ORM.

El comando se puede volver a ejecutar: actualiza o reutiliza registros por sus
claves identificadoras para evitar duplicados. Los usuarios y registros de
demostración son sintéticos.

## Ocho mantenedores visuales

La interfaz presenta exactamente ocho mantenedores, dos por integrante:
Delegaciones, Perfiles, Catálogo, Períodos, Actividades, Evidencias,
Compromisos y Metas. `MedicionDelegacion`, `HistorialCompromiso` y `Auditoria`
son entidades adicionales administradas en Django Admin, no mantenedores
visuales adicionales. Delegaciones, Perfiles, Catálogo, Períodos, Actividades y
Evidencias cuentan con CRUD propio en la aplicación. Compromisos y Metas enlazan
sus acciones a Django Admin mientras se implementan sus CRUD propios.
El Catalogo no tiene llaves foraneas desde otras entidades actualmente, por lo
que su CRUD permite eliminar un item tras confirmacion. Si otros modelos pasan
a referenciarlo, se debe cambiar esa accion por desactivacion para conservar el
historial.

Actividades usa su listado propio (`/actividades/`), que ya filtra por rol y
delegación; la tarjeta del índice de mantenedores enlaza ahí para no duplicar
pantallas. Solo quien registró la actividad o un perfil con visión completa
(administrador o coordinador) puede modificarla o eliminarla, con estas reglas:

- Una actividad `aprobada` no se modifica ni se elimina desde la aplicación,
  para nadie. `MetaMedicion.avance_calculado` cuenta las actividades aprobadas
  según delegación, fecha e ítem de medición; cambiar esos datos o borrar la
  actividad alteraría en silencio un avance ya validado. Una corrección
  excepcional la hace el superusuario en Django Admin, que guarda su historial.
- Una actividad `rechazada` sí se puede editar, porque no suma al avance. Al
  guardarla vuelve a `pendiente`, de modo que el verificador revise la
  corrección antes de que cuente.
- Eliminar una actividad borra también sus evidencias (`on_delete=CASCADE`); la
  pantalla de confirmación indica cuántas se eliminarán.

El mantenedor de Evidencias (`/administracion/evidencias/`) es una herramienta
administrativa: no cambia el estado de la actividad asociada, así que tampoco
altera el avance. La aprobación o el rechazo de la actividad completa sigue en
el detalle de la actividad. El campo de revisión (`aprobada`) solo se ofrece a
quien puede validar y, al cambiarlo, registra en `revisada_por` quién lo hizo;
como el mantenedor está restringido a administración y coordinación, en la
práctica siempre aparece. Django no borra del disco el archivo de una evidencia
eliminada o reemplazada.

## Comandos para crear y revisar el esquema

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py showmigrations
```

`makemigrations` se ejecuta durante el desarrollo solo cuando cambian los
modelos; la instalacion utiliza las migraciones ya versionadas.

La entidad `Auditoria` se conserva como historial de acciones. Para cumplir el
criterio academico de administrar todas las entidades, el superusuario puede
crear, modificar y eliminar sus filas desde Django Admin. En produccion se
recomienda que los usuarios administrativos solo puedan consultarla y que
cualquier rectificacion se realice mediante una funcion controlada.

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
- `dias_computables` cuenta días de calendario. RN-001 se valida al guardar un
  ítem (la suma no puede superar 100 %) y al iniciar el período (debe ser
  exactamente 100 % por cargo).
- Algunos métodos reciben un parámetro más que el diagrama, porque la operación
  necesita saber quién la hace o sobre qué registro: `reabrir_periodo(motivo, usuario)`,
  `subir_evidencia(actividad, archivo)` y `set_estado`, `derivar_compromiso` y
  `cerrar_compromiso` con `autor`.
- Actividad y Evidencia tienen el estado adicional «correccion», que deja
  `Validacion.solicitar_correccion()`. `Validacion.version` es el número de
  revisión de la evidencia; el control de concurrencia (RF-034) está en el
  campo `version` de Actividad y Compromiso.
- `Indicador.ajuste` y `Validacion.resultado` se guardan, pero no entran en el
  cálculo, porque el informe no define cómo se aplican.
- El avance de una meta (RN-003 y RN-009) cuenta las actividades aprobadas del
  ítem en el período que tienen una validación aprobada; si el funcionario de la
  meta tiene delegación, solo las de esa delegación.

## Migración al modelo de 17 clases

Se aplica el patrón ampliar, migrar y contraer:

1. **Ampliar** (`0007` a `0009`): crea las tablas nuevas y agrega los campos
   nuevos como opcionales. Los campos antiguos que serán reemplazados admiten
   vacío, pero los formularios actuales los siguen exigiendo. `Actividad.fecha_hora`
   y `HistorialCompromiso.autor_funcionario` son temporales: al contraer
   reemplazan a `fecha` y `autor` y toman su nombre.
2. **Migrar** (`0010_migrar_datos`): copia los datos con `RunPython` y se puede
   revertir. Informa en pantalla los casos especiales: códigos de catálogo
   repetidos, tipos de atención que no estaban en el catálogo, teléfonos
   recortados a 20 caracteres, períodos creados y sumas de ponderación
   distintas de 100 %. Las delegaciones sin funcionarios reciben un delegado
   provisional con cuenta inactiva (apellido «(provisional)»), para conservar
   su meta.
3. **Contraer**: elimina los campos y tablas antiguos cuando las vistas ya usan
   el modelo nuevo.

Después de migrar se ejecuta `python manage.py calcular_indicadores`, que crea
un `Indicador` por cada meta de los períodos no cerrados. Una actividad
aprobada sin evidencias, permitida por el sistema anterior, no aporta al avance
(RN-009).
