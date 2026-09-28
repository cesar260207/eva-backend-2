# Checklist de la entrega

Este documento resume la pauta compartida por el equipo. El orden de trabajo acordado es completar y revisar el proyecto local primero; desplegar en EC2 queda para la etapa final.

## Requisito de equipo

- [ ] Completar los CRUD de exactamente **8 mantenedores visuales**, dos por cada integrante del equipo de cuatro:
  Delegaciones, Perfiles, Catálogo, Períodos, Actividades, Evidencias, Compromisos y Metas.
  - [x] Actividades: CRUD propio sobre el listado `/actividades/` (agregar, modificar, eliminar con confirmación y buscar).
  - [x] Evidencias: CRUD propio en `/administracion/evidencias/` (agregar, modificar, eliminar con confirmación y buscar).
- [ ] Administrar cualquier entidad adicional del modelo en Django Admin, sin convertirla en un noveno mantenedor visual. `MedicionDelegacion` es una entidad adicional para conservar los indicadores importados.

## Base de datos y Django ORM

- [x] Definir modelos relacionales, relaciones y claves foráneas.
- [x] Crear migraciones para las entidades del proyecto.
- [x] Importar los datos de `solicitudes.json` y `metas_delegaciones.json` mediante `seed_demo`.
- [x] Verificar localmente que los registros de ambos JSON se cargaron y que no faltan registros.
- [x] Confirmar que los modelos coinciden con las migraciones (`makemigrations --check --dry-run`).
- [ ] Sincronizar el esquema y los registros con la base de datos SQL compatible destinada a la entrega.
- [ ] Confirmar que las vistas obtienen datos mediante consultas Django ORM y plantillas Django.
- [ ] Preparar una explicación de entidades, relaciones y finalidad de las tablas.

## Django Admin y aplicación

- [x] Registrar todas las entidades del modelo en Django Admin.
- [ ] Verificar en Admin creación, visualización, búsqueda, edición, eliminación y navegación por relaciones.
- [ ] Revisar listados, tablas/tarjetas y enlaces de navegación Bootstrap.
- [ ] Mostrar Agregar, Modificar, Eliminar y Buscar en cada vista de listado. La pauta permite marcadores de posición para los botones del sitio en esta evaluación; el entregable también menciona CRUD operativo, así que Admin debe tener CRUD funcional.

## GitHub y documentación

- [ ] Confirmar que el repositorio GitHub propio contiene el código completo y el historial de desarrollo.
- [ ] Subir los cambios en commits y comprobar el remoto.
- [ ] Mantener README y `.gitignore`; no subir `.env` ni credenciales.
- [ ] Preparar documento técnico PDF o Word: descripción y objetivo, funcionalidades, arquitectura, carpetas/apps y base de datos.
- [ ] Documentar prompts de IA, respuestas y aplicación en el proyecto.

## Evidencias para la revisión presencial

- [ ] Django Admin: modelos, migraciones, registros y operaciones CRUD.
- [ ] phpMyAdmin: todas las tablas, estructura, relaciones y registros.
- [ ] GitHub: repositorio remoto, commits, remoto configurado y clonación.
- [ ] EC2: conexión SSH, proyecto clonado, entorno virtual y aplicación ejecutándose.
- [ ] Capturas de AWS, terminal Linux, aplicación, GitHub, migraciones/modelos, tablas phpMyAdmin y uso de IA.

## EC2 — dejar para el final

- [ ] Crear/preparar instancia EC2 Linux con Python, venv, Django, Git, servidor web y base de datos compatible.
- [ ] Clonar desde el repositorio GitHub, configurar variables de entorno, instalar dependencias, migrar y cargar datos.
- [ ] Verificar aplicación y phpMyAdmin desde EC2.

## Notas del estado actual

- `MODELO_DATOS.md` explica las once entidades, sus relaciones y la migracion de los JSON.
- `settings.py` exige `SECRET_KEY` desde `.env`; no hay clave secreta de respaldo en el codigo.
- WhiteNoise esta configurado para servir archivos estaticos con `DEBUG=False`; Gunicorn se instala solo en sistemas distintos de Windows.
- Se conserva `fecha_ingreso` importada, Agenda permite buscar y Resumen consulta el historico de `MedicionDelegacion`.
- `Auditoria` permite altas, cambios y eliminaciones solo al superusuario en Django Admin; la decision queda explicada en `MODELO_DATOS.md`.
- Delegaciones, Catalogo (rama `crud-catalogo`), Actividades y Evidencias tienen CRUD propio; quedan cuatro CRUD propios por implementar: Perfiles, Periodos, Compromisos y Metas.

- El proyecto cuenta con ocho entradas en `MANTENEDORES`.
- Las 11 entidades del modelo están registradas en Admin; la comprobación confirmó acceso de permisos CRUD para un superusuario.
- La base local provisional se migró y recibió los datos de demostración; las verificaciones de Django y consistencia de migraciones pasaron.
- En XAMPP existe `gestion_laserena` con codificación `utf8mb4`, pero sigue sin tablas: MariaDB 10.4.32 no es compatible con Django 5.2 (requiere MariaDB 10.5+). Por ahora `.env` usa SQLite localmente. Para phpMyAdmin se deberá usar una base compatible en la etapa final.
- XAMPP reportó un error de checksum de Aria al configurar privilegios de un usuario de aplicación local; `gestion_user` quedó sin privilegios sobre la base.
