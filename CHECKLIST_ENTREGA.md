# Checklist de la entrega: Evaluación Sumativa 3

Pauta: aplicación web con CRUD, autenticación, perfiles, recuperación de contraseña y sin Django Admin.
Equipo de cuatro integrantes: se exigen 8 mantenedores y 4 transacciones.

## Autenticación (15 pts)

- [x] Ingreso con usuario y contraseña (`/login/`) y cierre de sesión (Salir, POST a `/logout/`).
- [x] Vistas protegidas con `@login_required`, `PermisoRequeridoMixin` y `permiso_requerido`.
- [x] Al ingresar, cada usuario llega al panel de su perfil (`LOGIN_REDIRECT_URL = 'panel'`).

## Perfiles y permisos (15 pts)

- [x] Cuatro grupos de Django con permisos por jerarquía: Administrador, Coordinador, Delegado y Profesional
  (migraciones `0015`, `0018`, `0019`, `0022` que renombra Funcionario a Profesional, `0025`, `0027` y `0028`).
- [x] Creación de usuarios y asignación de grupo desde **Administración → Funcionarios y usuarios**.
- [x] Restricciones funcionales: los mantenedores, la auditoría y los perfiles exigen el permiso de Django
  correspondiente; revisar evidencias exige `add_validacion`; eliminar actividades exige `delete_actividad`.
- [x] El perfil Profesional no hace operaciones críticas: no revisa, no elimina, no administra.
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
- [x] Panel Profesional: solo sus funciones y la lista de operaciones restringidas.

## Mantenedores (20 pts)

- [x] 12 mantenedores con listar, buscar, agregar, modificar y eliminar con confirmación: Delegaciones, Cargos,
  Roles, Funcionarios y usuarios, Catálogo, Organizaciones, Períodos, Parámetros, Ítems medibles, Metas, Ajustes y
  Ausencias.
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
- [x] EC2 actualizado a `f910537` (PR #16) el 20 de noviembre de 2026, con las migraciones 0021 a 0026.
- [ ] EC2: desplegar la rama `feat/requerimientos-octubre` (migraciones 0027 y 0028) con los pasos del pull request.
- [ ] Subir la rama `feat/requerimientos-octubre` y unirla a `main` con un pull request.
- [x] Evidencia de IA actualizada en `evidencias_ia.md` (prompt 14).
- [ ] Documento técnico PDF/Word con capturas (login, recuperación, 4 paneles, mantenedores, transacciones,
  EC2, GitHub, IA).

## Pruebas

- [x] `python manage.py test`: 676 pruebas en verde (rama `feat/requerimientos-octubre`).
- [x] `PLAN_DE_PRUEBAS.md` regenerado con `python manage.py plan_pruebas`.

## Requerimientos de octubre 2026 y exposición final

- [x] Reglas de octubre implementadas y probadas ([docs/REQUERIMIENTOS_V2.md](docs/REQUERIMIENTOS_V2.md)).
- [x] Casos de uso al día con el código y prueba automática de sus actores ([docs/CASOS_DE_USO.md](docs/CASOS_DE_USO.md)).
- [x] Diagrama de clases, entidad-relación, paquetes y trazabilidad actualizados ([docs/DIAGRAMA_CLASES.md](docs/DIAGRAMA_CLASES.md), [docs/diagramas/](docs/diagramas/)).
- [x] Sprint backlog repriorizado con evidencia ([docs/BACKLOG_SPRINT.md](docs/BACKLOG_SPRINT.md)).
- [x] Plan de mantención con respaldo diario y pruebas en cada pull request ([docs/PLAN_MANTENCION.md](docs/PLAN_MANTENCION.md)).
- [x] Normativas y estándares ([docs/NORMATIVAS_Y_ESTANDARES.md](docs/NORMATIVAS_Y_ESTANDARES.md)).
- [x] Resultados medidos con CSV para gráficos ([docs/RESULTADOS.md](docs/RESULTADOS.md)).
- [x] Guía de la exposición y preguntas de la defensa ([docs/DEMO_EXPOSICION.md](docs/DEMO_EXPOSICION.md), [docs/PREGUNTAS_DEFENSA.md](docs/PREGUNTAS_DEFENSA.md)).
- [ ] Completar los datos marcados «[COMPLETAR POR EL GRUPO]» (reuniones, sprints, autoría de commits, contribución de cada integrante).
- [ ] Dejar privados `eva-backend-2` y `proyecto-de-titulo-en-local`, o limpiar su historial: el Excel de organizaciones con domicilios está en el historial de los dos y ambos son públicos.
- [ ] Crear `ACCESOS_EXPOSICION.txt` (a partir de la plantilla) y probar los accesos el día antes.
- [ ] Regenerar `docs/casos_uso/imagenes/diapositiva_g06.png` con Graphviz.
- [ ] En el servidor: crear `~/.my.cnf`, probar `scripts/respaldo.sh` y programarlo con cron.
- [ ] Preparar la presentación con la estructura de [docs/DEMO_EXPOSICION.md](docs/DEMO_EXPOSICION.md) sección 8.

## Evaluación 3 (entrega lunes 30-11-2026, 11:25)

Código (hecho y probado: suite completa en verde, ver [docs/PROTOCOLO_PRUEBAS.md](docs/PROTOCOLO_PRUEBAS.md)):

- [x] Contraseña temporal al crear o restablecer usuarios y cambio obligatorio en el primer ingreso (`/cuenta/cambiar-contrasena/`).
- [x] Bloqueo de ingreso tras 5 intentos fallidos (15 min), auditado.
- [x] Revisión con «Solicitar más antecedentes», alerta al autor y vuelta a revisión al completar.
- [x] Tubo de cartas (`/agenda/?tubo=carta`), búsqueda al escribir por código, RUT o nombre, filtro por funcionario.
- [x] El menú «Tareas» pasa a llamarse «Tubo»: reúne el Tubo de trabajo y el Tubo de cartas (cada registro del Tubo de trabajo sigue siendo una «tarea»).
- [x] Tareas realizadas cerradas para su responsable (solo coordinación las reabre).
- [x] Actividades y gestiones sociales pueden ingresar o no al Tubo; lista y edición de gestiones sociales (`/casos-sociales/`).
- [x] Mantenedores nuevos: territorios, vecinos (RUT validado), membresías y dirigencias, hitos con responsables, subtipos de atención.
- [x] Meta única por funcionario e ítem (restricción en la base), índices para búsquedas frecuentes, restricción CHECK de fechas.
- [x] Dashboard con gráficos y filtros (`/gestion/tablero/`), cada gráfico con su tabla de datos.
- [x] Respaldo portable `python manage.py respaldo` y su restauración probada.
- [x] Guía técnica [docs/IMPLEMENTACION.md](docs/IMPLEMENTACION.md), protocolo y [matriz de trazabilidad](docs/TRAZABILIDAD.md) generados.

Pendiente del equipo:

- [ ] Revisar y probar todo en local; recién entonces subir la rama y abrir el pull request.
- [ ] Asignar responsables en `RESPONSABLE_POR_AREA` (`delegaciones_app/protocolo.py`) y regenerar con `python manage.py protocolo_pruebas`.
- [ ] Ejecutar los casos manuales CP-05 (correo real) y CP-32 (revisión visual responsiva, tema oscuro, teclado),
      anotar su resultado en `RESULTADOS_MANUALES` y regenerar el protocolo.
- [ ] En EC2: `git pull`, `pip install -r requirements.txt`, `python manage.py migrate` (0030 y 0031), `collectstatic`,
      reiniciar Gunicorn; opcional `seed_demo` para los datos demo nuevos.
- [ ] Capturas o video breve de los flujos nuevos para el informe (sin reemplazar la demostración en vivo).
