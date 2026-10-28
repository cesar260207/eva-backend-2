# Checklist de la entrega — Evaluación Sumativa 3

Pauta: aplicación web con CRUD, autenticación, perfiles, recuperación de contraseña y sin Django Admin.
Equipo de cuatro integrantes: se exigen 8 mantenedores y 4 transacciones.

## Autenticación (15 pts)

- [x] Ingreso con usuario y contraseña (`/login/`) y cierre de sesión (Salir, POST a `/logout/`).
- [x] Vistas protegidas con `@login_required`, `PermisoRequeridoMixin` y `permiso_requerido`.
- [x] Al ingresar, cada usuario llega al panel de su perfil (`LOGIN_REDIRECT_URL = 'panel'`).

## Perfiles y permisos (15 pts)

- [x] Tres grupos de Django con permisos: Administrador, Supervisor y Administrativo (migración `0015_perfiles_de_acceso`).
- [x] Creación de usuarios y asignación de grupo desde **Administración → Funcionarios y usuarios**.
- [x] Restricciones funcionales: los mantenedores, la auditoría y los perfiles exigen el permiso de Django correspondiente.
- [x] Página de consulta de perfiles y permisos: `/administracion/perfiles/`.

## Recuperación de contraseña (15 pts)

- [x] Solicitud por correo (`/recuperar/`), token seguro de Django, enlace por correo, validación del token, nueva contraseña y confirmación.
- [x] Enlace en la pantalla de login; el cambio queda en la auditoría.
- [ ] Configurar `EMAIL_*` en el `.env` de EC2 (Gmail con contraseña de aplicación) y probar con un correo real.
- [ ] Poner un correo real a las cuentas que se usarán en la demostración.

## Dashboard por perfil (10 pts)

- [x] Panel Administrador: visión global, gestión de usuarios, los 8 mantenedores, transacciones, auditoría reciente.
- [x] Panel Supervisor: mantenedores autorizados, transacciones, cumplimiento y alertas operacionales.
- [x] Panel Administrativo: solo sus funciones y la lista de operaciones restringidas.

## Mantenedores (20 pts) y transacciones (10 pts)

- [x] 8 mantenedores con crear, buscar, listar, modificar y eliminar o desactivar: Delegaciones, Cargos, Roles,
  Funcionarios y usuarios, Catálogo, Períodos, Ítems medibles y Metas.
- [x] Transacciones: registro de actividad con evidencia, revisión de evidencias (Validacion), compromisos con
  historial de estados y apertura, cierre y reapertura de períodos.

## Ajustes de la revisión del equipo

- [x] Quién crea compromisos: coordinación (asigna a un delegado) o delegado/funcionario en su delegación; explicado en la agenda.
- [x] Botón «Subir evidencia» con pantalla propia, separado de «Modificar».
- [x] Indicador de evidencia (cargada / sin evidencia) en el listado de actividades.
- [x] Vista de revisión sin elementos de carga sobrantes.
- [x] Revisión: solo aprobar o rechazar con motivo (se quitó «solicitar corrección»).
- [x] El delegado ve solo su delegación (registros, filtros, medición, semáforo, resumen, informes).
- [x] Coordinador separado del delegado: pantalla «Delegados» para asignarlos y asignarles compromisos; el delegado revisa las evidencias de su delegación.
- [x] Diseño más ordenado: menú agrupado, esquinas rectas, tablas y paneles uniformes.

## Sin Django Admin

- [x] `django.contrib.admin` fuera de `INSTALLED_APPS`, sin ruta `/admin/` y sin `admin.py`.

## Base de datos, EC2, GitHub, IA

- [x] Modelos, relaciones y migraciones (`makemigrations --check` sin cambios pendientes).
- [ ] EC2: `git pull`, `.env` con correo, `migrate`, `collectstatic` y reinicio de Gunicorn (ver README, «Actualizar un servidor ya desplegado»).
- [ ] Subir los cambios a GitHub en commits.
- [x] Evidencia de IA actualizada en `evidencias_ia.md`.
- [ ] Documento técnico PDF/Word con capturas (login, recuperación, 3 paneles, mantenedores, transacciones, EC2, GitHub, IA).

## Pruebas

- [x] `python manage.py test`: 530 pruebas en verde, incluidas las de `test_unit_seguridad.py` y `test_unit_delegaciones.py`.
- [x] `PLAN_DE_PRUEBAS.md` regenerado con `python manage.py plan_pruebas`.
