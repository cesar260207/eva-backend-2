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
visuales adicionales.

## Comandos para crear y revisar el esquema

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
python manage.py showmigrations
```

En phpMyAdmin se selecciona `gestion_laserena` para inspeccionar tablas,
columnas, llaves foráneas y registros. Django genera el esquema a partir de las
migraciones.
