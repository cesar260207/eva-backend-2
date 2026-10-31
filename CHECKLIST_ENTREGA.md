# Checklist de la entrega: Evaluación Sumativa 3

Pauta: aplicación web con CRUD, autenticación, perfiles, recuperación de contraseña y sin Django Admin.
Equipo de cuatro integrantes: se exigen 8 mantenedores y 4 transacciones.

## Autenticación (15 pts)

- [x] Ingreso con usuario y contraseña (`/login/`) y cierre de sesión (Salir, POST a `/logout/`).
- [x] Vistas protegidas con `@login_required`, `PermisoRequeridoMixin` y `permiso_requerido`.
- [x] Al ingresar, cada usuario llega al panel de su perfil (`LOGIN_REDIRECT_URL = 'panel'`).

## Perfiles y permisos (15 pts)

- [x] Cuatro grupos de Django con permisos por jerarquía: Administrador, Coordinador, Delegado y Funcionario
  (migraciones `0015_perfiles_de_acceso`, `0018_perfiles_por_jerarquia` y `0019_eliminar_actividad_solo_coordinacion`).
- [x] Creación de usuarios y asignación de grupo desde **Administración → Funcionarios y usuarios**.
- [x] Restricciones funcionales: los mantenedores, la auditoría y los perfiles exigen el permiso de Django
  correspondiente; revisar evidencias exige `add_validacion`; eliminar actividades exige `delete_actividad`.
- [x] El perfil Funcionario no hace operaciones críticas: no revisa, no elimina, no administra.
- [x] Página de consulta de perfiles y permisos: `/administracion/perfiles/`.

## Recuperación de contraseña (15 pts)

- [x] Solicitud por correo (`/recuperar/`), token seguro de Django, enlace por correo, validación del token,
  nueva contraseña y confirmación.
- [x] Enlace en la pantalla de login; el cambio queda en la auditoría.
- [x] Pruebas con correo en memoria: envío, enlace de un solo uso, vencimiento y respuesta que no revela cuentas.
- [ ] Configurar `EMAIL_*` en el `.env` de EC2 (Gmail con contraseña de aplicación) y probar con
  `python manage.py sendtestemail`.
- [ ] El día de la revisión, escribir un correo real en la cuenta demo que se usará (desde la interfaz).

## Dashboard por perfil (10 pts)

- [x] Panel Administrador: visión global, gestión de usuarios, los 8 mantenedores, transacciones y auditoría reciente.
- [x] Panel Coordinador: todas las delegaciones con su avance y su delegado, mantenedores autorizados y alertas.
- [x] Panel Delegado: su delegación, las evidencias que esperan su revisión, su tubo de trabajo y sus métricas.
- [x] Panel Funcionario: solo sus funciones y la lista de operaciones restringidas.

## Mantenedores (20 pts)

- [x] 8 mantenedores con listar, buscar, agregar, modificar y eliminar con confirmación: Delegaciones, Cargos,
  Roles, Funcionarios y usuarios, Catálogo, Períodos, Ítems medibles y Metas.
- [x] Eliminar borra el registro si no tiene datos relacionados; si los tiene, lo desactiva y la confirmación
  explica cuáles son.
- [x] Validaciones en cada formulario (duplicados, fechas, ponderaciones, contraseñas, perfil según el rol).

## Transacciones (10 pts)

- [x] Registro de actividad (`ActividadForm`).
- [x] Carga y revisión de evidencias (`EvidenciaForm` y `RevisionForm`).
- [x] Tubo de trabajo: tareas con historial de estados (`CompromisoForm`).
- [x] Asignación de delegados (`AsignarDelegadoForm`).
- [x] Las cuatro documentadas en el README, sección «Transacciones».

## Ajustes de la revisión del equipo

- [x] «Tubo de trabajo» y «tarea» en toda la interfaz, con un único botón «+ Agregar al tubo de trabajo».
- [x] «Modificar» en la página de cada registro, visible solo para quien puede usarlo.
- [x] Botón «Subir evidencia» con pantalla propia e indicador de evidencia en el listado de actividades.
- [x] Revisión: solo aprobar o rechazar con motivo (se quitó «Solicitar corrección»).
- [x] El delegado verifica y ve solo su delegación (registros, filtros, medición, informes, alertas).
- [x] Coordinador separado del delegado, cada uno con su panel.
- [x] Sin códigos internos (EP, HU, RF, MVP) en las pantallas.
- [x] Diseño ordenado: bordes rectos, encabezados uniformes, filtros en grilla.

## Sin Django Admin

- [x] `django.contrib.admin` fuera de `INSTALLED_APPS`, sin ruta `/admin/` y sin `admin.py`.

## Base de datos, EC2, GitHub, IA

- [x] Modelos, relaciones y migraciones (`makemigrations --check` sin cambios pendientes).
- [ ] EC2: respaldo con `mysqldump`, `git pull`, `migrate` (0016 a 0020), `collectstatic` y reinicio de
  Gunicorn (README, «Actualizar un servidor ya desplegado»).
- [ ] Subir la rama `feat/ajustes-grupo-y-evaluacion` y unirla a `main` con un pull request.
- [x] Evidencia de IA actualizada en `evidencias_ia.md` (prompt 13).
- [ ] Documento técnico PDF/Word con capturas (login, recuperación, 4 paneles, mantenedores, transacciones,
  EC2, GitHub, IA).

## Pruebas

- [x] `python manage.py test`: 581 pruebas en verde.
- [x] `PLAN_DE_PRUEBAS.md` regenerado con `python manage.py plan_pruebas`.
