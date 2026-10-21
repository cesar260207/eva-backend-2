# Checklist de la entrega

Este documento resume la pauta compartida por el equipo. El proyecto se migró al modelo de 17 clases y se revisó en local. El servidor EC2 corresponde a la versión anterior del modelo y está pendiente de actualizar (ver la sección de despliegue del README.md y la sección «EC2» más abajo).

## Requisito de equipo

- [x] Completar los CRUD de exactamente **8 mantenedores visuales**, dos por cada integrante del equipo de cuatro:
  Delegaciones, Cargos, Roles, Funcionarios, Catálogo, Períodos, Ítems medibles y Metas.
  - [x] Los ocho comparten las vistas genéricas de `crud.py` (listado con búsqueda, nuevo, modificar y eliminar o desactivar con confirmación).
  - [x] Roles y Funcionarios son solo de administración; los demás, de administración y coordinación.
  - [x] Actividades (`/actividades/`) y compromisos (`/agenda/`) tienen sus propias pantallas y no cuentan como mantenedores adicionales.
- [x] Administrar cualquier entidad adicional del modelo en Django Admin, sin convertirla en un noveno mantenedor visual. `MedicionDelegacion` es una entidad adicional para conservar los indicadores importados.

## Base de datos y Django ORM

- [x] Definir modelos relacionales, relaciones y claves foráneas: las 17 clases del diseño más `FuncionarioRol` y `MedicionDelegacion`.
- [x] Crear migraciones para las entidades del proyecto (`0007` a `0014` llevan los datos al modelo de 17 clases).
- [x] Importar los datos de `solicitudes.json` y `metas_delegaciones.json` mediante `seed_demo`.
- [x] Verificar localmente que los registros de ambos JSON se cargaron y que no faltan registros.
- [x] Confirmar que los modelos coinciden con las migraciones (`makemigrations --check --dry-run`).
- [ ] Sincronizar el esquema y los registros con la base de datos SQL compatible destinada a la entrega.
- [x] Confirmar que las vistas obtienen datos mediante consultas Django ORM y plantillas Django.
- [x] Preparar una explicación de entidades, relaciones y finalidad de las tablas (`MODELO_DATOS.md`).

## Django Admin y aplicación

- [x] Registrar todas las entidades del modelo en Django Admin (las 19 tablas; la auditoría solo se consulta).
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

- [x] Django Admin: modelos, migraciones, registros y operaciones CRUD.
- [x] phpMyAdmin: todas las tablas, estructura, relaciones y registros.
- [x] GitHub: repositorio remoto, commits, remoto configurado y clonación.
- [x] EC2: conexión SSH, proyecto clonado, entorno virtual y aplicación ejecutándose.
- [ ] Capturas de AWS, terminal Linux, aplicación, GitHub, migraciones/modelos, tablas phpMyAdmin y uso de IA.

## EC2

- [x] Crear/preparar instancia EC2 Linux con Python, venv, Django, Git, servidor web y base de datos compatible.
- [x] Clonar desde el repositorio GitHub, configurar variables de entorno, instalar dependencias, migrar y cargar datos (versión anterior del modelo).
- [x] Verificar aplicación y phpMyAdmin desde EC2.
- [ ] Actualizar el servidor al modelo de 17 clases: respaldo con `mysqldump`, anotar el commit actual, `git pull`, `pip install`, `migrate`, `calcular_indicadores`, `collectstatic`, reiniciar Gunicorn y verificar. Las migraciones `0011` a `0013` aún no se ensayaron sobre MySQL.

## Pruebas

- [x] Pruebas unitarias por caso de uso con el CU y los RF en el docstring (`test_unit_*.py`) y los 8 casos de login.
- [x] Pruebas de integración en `test_integracion.py`.
- [x] `PLAN_DE_PRUEBAS.md` con la tabla CP, CU, RF, método de prueba y resultado, generado con `python manage.py plan_pruebas`.
- [x] Implementados RF-021, RF-030 y RF-037 (resumen colectivo, actividad reciente y alertas), sin migraciones nuevas.
- [ ] Los requisitos RF-015, 020, 025, 031 y 035 quedan declarados como pendientes: necesitan modelos nuevos o decisiones de diseño que el informe no define.

## Notas del estado actual

- `MODELO_DATOS.md` explica las 17 clases y las dos tablas adicionales, sus reglas de negocio, sus relaciones, la migración al modelo nuevo y los requisitos pendientes.
- `settings.py` exige `SECRET_KEY` desde `.env`; no hay clave secreta de respaldo en el codigo.
- WhiteNoise esta configurado para servir archivos estaticos con `DEBUG=False`; Gunicorn se instala solo en sistemas distintos de Windows.
- Se conserva `fecha_ingreso` importada, Agenda permite buscar y Resumen consulta el historico de `MedicionDelegacion`.
- `Auditoria` es inmutable: no se modifica ni se elimina, ni siquiera desde Django Admin, que solo permite consultarla. Registra también los accesos denegados.
- Los ocho mantenedores tienen CRUD propio.

- El proyecto cuenta con ocho entradas en `MANTENEDORES`.
- Las 19 tablas del modelo están registradas en Admin.
- La base local provisional se migró y recibió los datos de demostración; las verificaciones de Django y consistencia de migraciones pasaron.
- Despliegue real en EC2: Amazon Linux 2023, MySQL 8.4 (no MariaDB), Gunicorn como servicio systemd, Nginx como proxy inverso y phpMyAdmin con PHP-FPM protegido con doble autenticación.
- La base local con XAMPP/MariaDB 10.4 no era compatible con Django 5.2; por eso la base definitiva es MySQL 8.4 en la EC2.
- XAMPP reportó un error de checksum de Aria al configurar privilegios de un usuario de aplicación local; `gestion_user` quedó sin privilegios sobre la base.
