# Guía de la exposición del SGR

Exposición de Ingeniería de Software del lunes 23 de noviembre de 2026. Tiempo máximo: 10:59 minutos, sin informe. El guion suma 9:30 minutos y deja 1:29 de margen.

Los datos que no salen del repositorio quedan marcados con «[COMPLETAR POR EL GRUPO]». Los documentos que todavía no existen se citan con la tarea del plan de trabajo que los crea.

## 1. Accesos

- URL: `http://3.225.119.192` (con http: https todavía no está activo).
- Usuarios y contraseñas: en `ACCESOS_EXPOSICION.txt`, en la raíz del proyecto. Ese archivo no se sube a GitHub (está en `.gitignore`); la plantilla es [ACCESOS_EXPOSICION.example.txt](ACCESOS_EXPOSICION.example.txt).
- Datos preparados en el servidor: período «Trimestre octubre-diciembre 2026» abierto, ítem «Atención de casos sociales» (cargo Profesional SGR, ponderación 100) y una meta de valor objetivo 2 para «Funcionario Centro» (cuenta `funcionario.centro`). Con objetivo 2, aprobar una sola actividad cambia el semáforo de rojo a ámbar.

Conviene abrir dos ventanas del navegador (una normal y una privada) para tener al Profesional y al Delegado con sesión iniciada al mismo tiempo, sin perder tiempo entrando y saliendo.

## 2. Flujos en vivo

Se muestran tres flujos, elegidos por su valor para el municipio: el registro en terreno (lo que hoy se hace en planillas), la revisión que decide si una gestión cuenta, y el control de acceso que protege los datos.

### Flujo 1. El Profesional registra una actividad con su evidencia (1:30)

Usuario: `funcionario.centro` (Profesional, delegación Centro).

1. Entrar con la cuenta. El sistema muestra el panel del perfil Profesional.
2. Elegir «Registrar actividad con evidencia» en el panel (o «Actividades» y «+ Nueva actividad»).
3. Completar delegación Centro, ítem «Atención de casos sociales», tipo de atención, fecha de hoy, solicitud y acción. En el contacto, escribir un nombre y el teléfono `abc`.
4. Pulsar «Guardar actividad». El formulario vuelve con el error junto al campo teléfono y no guarda nada.
5. Corregir el teléfono (por ejemplo `912345678`) y guardar. El sistema genera el código EVD y pasa a subir la evidencia.
6. Elegir un JPG, PNG o PDF de menos de 5 MB y pulsar «Subir evidencia». La actividad queda «pendiente de revisión».

Qué se destaca: validación del formulario (CU-01.1, CU-01.2), código verificador (CU-10), regla 2 de octubre (sin nombre y teléfono del contacto la actividad no suma) y evidencia obligatoria (CU-09).

### Flujo 2. El Delegado revisa la actividad y el semáforo cambia (1:30)

Usuario: `delegado.demo` (Delegado, delegación Centro).

1. Entrar con la cuenta, abrir «Actividades» y la actividad recién registrada.
2. Pulsar «Rechazar» sin escribir el motivo. El sistema no lo permite: «El rechazo de una evidencia exige un motivo: quien registró la actividad lo necesita para corregirla.»
3. Pulsar «Aprobar». La actividad pasa a «aprobada» y los indicadores se recalculan.
4. Abrir «Resultados» y «Semáforo de avance». Si aparece otro período, elegir «Trimestre octubre-diciembre 2026». La delegación Centro pasa de rojo a ámbar.
5. En la ventana del Profesional, abrir el menú del usuario y «Mi ficha»: la meta de «Atención de casos sociales» muestra el avance con la actividad aprobada.

Qué se destaca: nadie revisa su propio trabajo, el rechazo exige motivo (CU-11, RN-009), solo lo aprobado suma (CU-11.2) y el semáforo se calcula con lo esperado al día (CU-16).

### Flujo 3. Control de acceso y auditoría (0:30)

1. En la ventana del Profesional, escribir `http://3.225.119.192/administracion/auditoria/`. El sistema vuelve al inicio con el aviso de permiso insuficiente y deja el intento en la auditoría.
2. Entrar como `admin.demo` y abrir «Administración» y «Consultar auditoría»: aparecen el registro de la actividad, la aprobación y el acceso denegado recién hechos, sin opción de editar ni borrar.

Qué se destaca: perfiles con permisos distintos (CU-26.1) y trazabilidad de solo lectura (CU-30, CU-30.1).

### Ensayo y estado antes de la clase

- Ensayar de preferencia en un computador local con `python manage.py seed_demo`. Si se ensaya en el servidor, después del ensayo el Coordinador debe abrir la actividad aprobada y usar «Anular aprobación» con un motivo: los indicadores se recalculan hacia abajo y el semáforo vuelve a rojo. Las actividades de ensayo no aprobadas se pueden eliminar como Coordinador.
- El sistema acepta como máximo 7 actividades por autor y por día (parámetro `max_ingresos_diarios`). Un ensayo hecho el mismo lunes, con la fecha del lunes, ocupa cupos de ese tope.
- El cierre semanal (regla 4) solo acepta fechas de la semana en curso; el lunes también acepta la semana anterior. En la demo se usa la fecha de hoy.

## 3. Requerimientos no funcionales: qué mostrar en la presentación

Estos requerimientos no se ven bien en vivo; van como captura o fragmento de código en una diapositiva.

| Requerimiento | Qué mostrar | Archivo y línea |
| --- | --- | --- |
| Autenticación | Pantalla de inicio de sesión y fragmento de las vistas protegidas | `gestion_laserena/urls.py:17` (LoginView); `@login_required` en 21 vistas de `delegaciones_app/views.py` y 7 de `gestion_app/views.py`; `LOGIN_URL` en `gestion_laserena/settings.py:164` |
| Permisos por perfil | Fragmento del mixin que exige el permiso y registra el intento | `delegaciones_app/permisos.py:195` (PermisoRequeridoMixin) y `:175` (`_denegar`); permisos de cada perfil en `delegaciones_app/migrations/0025_permisos_perfiles_operativos.py` y `0027_delegado_ve_ajustes.py` |
| Funcionario desactivado sin permisos | Fragmento del backend de autenticación | `delegaciones_app/backends.py:7` (PerfilBackend) |
| Contraseñas con hash | Captura de la columna `password` de un usuario: muestra `pbkdf2_sha256$` y las iteraciones, nunca la contraseña. Se obtiene con `python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.get(username='funcionario.centro').password[:40])"` | Hasher por defecto de Django (PBKDF2); validadores de contraseña en `gestion_laserena/settings.py:123` |
| Auditoría de solo lectura | Fragmento de `save` y `delete` que rechazan cambios | `delegaciones_app/models.py:1064` (AuditoriaQuerySet), `:1094` (save), `:1100` (delete), `:1110` (registrar_evento) |
| Cierre semanal | Fragmento de la regla y de dónde se aplica | `delegaciones_app/reglas.py:14` (semana_abierta) y `:25` (validar_fecha_actividad); se llama en `delegaciones_app/models.py:290` solo al registrar o al cambiar la fecha |
| Protección CSRF y cabeceras | Fragmento de settings | `gestion_laserena/settings.py:57` (CsrfViewMiddleware), `:65` a `:67` (nosniff, referrer, X-Frame-Options) |
| Semáforo | Fragmento de la regla de colores | `delegaciones_app/medicion.py:36` (`_semaforo`: verde si alcanza lo esperado, ámbar desde el 60 %) |

## 4. Guion con cronómetro

La columna «Presenta» propone a cada integrante según su área en el plan de pruebas (`RESPONSABLES_POR_CU` en `delegaciones_app/plan_pruebas.py`). [COMPLETAR POR EL GRUPO]: confirmar o cambiar.

| Tiempo | Parte | Qué se dice | Qué se muestra | Presenta |
| --- | --- | --- | --- | --- |
| 0:00 a 0:45 | Diagnóstico | La Municipalidad mide la Matriz SGR en planillas: sin trazabilidad, con cálculos a mano y sin control de quién registra. | Diapositiva del problema | [COMPLETAR POR EL GRUPO] |
| 0:45 a 1:30 | Propuesta de valor y plan de mejora | El SGR registra en terreno, exige evidencia, calcula el cumplimiento y muestra el semáforo al día. | Diapositiva de propuesta | [COMPLETAR POR EL GRUPO] |
| 1:30 a 2:30 | Metodología | Cadena de descartes de la sección 5 y cómo se ejecutó. | Diapositiva de metodología y tablero | [COMPLETAR POR EL GRUPO] |
| 2:30 a 3:15 | Requerimientos nuevos | Proceso de la sección 6: agrupar, RF y RNF, casos de uso, clases, tareas y repriorización. | Diapositiva con los pasos y su evidencia | [COMPLETAR POR EL GRUPO] |
| 3:15 a 4:00 | Diseño | Casos de uso de alto nivel (19 gestiones), diagrama de clases con las clases nuevas de octubre y arquitectura en AWS. | `docs/casos_uso/imagenes/alto_nivel_diapositiva.png` y diagrama de clases | [COMPLETAR POR EL GRUPO] |
| 4:00 a 5:30 | Demo, flujo 1 | Registro con error de teléfono y evidencia. | Navegador, sesión Profesional | Sugerido: Dante Fredes (actividades y evidencias) |
| 5:30 a 7:00 | Demo, flujo 2 | Rechazo sin motivo, aprobación y semáforo. | Navegador, sesión Delegado | Sugerido: Dante Fredes o Faride Luna (metas) |
| 7:00 a 7:30 | Demo, flujo 3 | Acceso denegado y auditoría. | Navegador, Profesional y Administrador | Sugerido: César Aranda (usuarios y roles) |
| 7:30 a 8:15 | Resultados | Números medidos (sección 7). | Gráficos de `docs/resultados/` | [COMPLETAR POR EL GRUPO] |
| 8:15 a 8:45 | Normativas y estándares | Ley 19.628 y Ley 21.719, OWASP, ISO/IEC 25010. | Tabla resumida | Sugerido: Vinzenz Lafferte (parámetros y períodos) |
| 8:45 a 9:20 | Plan de mantención | Correctiva, preventiva (respaldo diario), adaptativa y perfectiva, con roles y calendario. | Calendario de mantención | [COMPLETAR POR EL GRUPO] |
| 9:20 a 9:30 | Cierre | Qué queda pendiente y agradecimiento. | Diapositiva final | [COMPLETAR POR EL GRUPO] |

Si la demo se atrasa, se acorta el flujo 3 (basta con el acceso denegado) y se deja la auditoría como captura.

## 5. Metodología: cadena de descartes

Se cuenta como decisiones tomadas por las condiciones del proyecto, no como un cuadro comparativo.

1. **Los requerimientos venían en un documento**, lo que en principio permite planificar todo al inicio. Pero el tiempo era corto (unos cuatro meses), y Cascada exige terminar cada etapa antes de empezar la siguiente, sin dejar espacio para corregir. Se descarta Cascada.
2. **Los requerimientos cambiaron** con las entrevistas y con la reunión de octubre de 2026 (10 reglas nuevas y tipos de organización). Esto refuerza el descarte: un modelo secuencial no absorbe cambios a mitad del proyecto.
3. **Incremental tampoco calza**: planifica entregas largas y cerradas, y el municipio necesitaba ver avances funcionando con frecuencia para validar las reglas de medición.
4. **Por eso, un enfoque ágil**: Scrum adaptado al tamaño del grupo y prácticas de XP.

Cómo se ejecutó, con la evidencia del repositorio:

| Práctica | Evidencia en el repositorio | Dato del grupo |
| --- | --- | --- |
| Sprints | Primer commit el 23 de septiembre de 2026; trabajo integrado en 15 pull requests (del #1 al #16; el #15 no se unió) entre el 27 de septiembre y el 20 de noviembre de 2026 | Duración de cada sprint: [COMPLETAR POR EL GRUPO] |
| Reuniones del equipo | No quedan en el repositorio | Frecuencia real (por ejemplo, dos por semana): [COMPLETAR POR EL GRUPO] |
| Revisión del sprint con el cliente | Reunión de octubre de 2026 con requerimientos nuevos | Fechas: [COMPLETAR POR EL GRUPO] |
| Pruebas automáticas (XP) | 648 pruebas que pasan; `python manage.py plan_pruebas` genera el plan con su resultado | |
| Integración por pull request (XP) | Una rama por funcionalidad (`feature/…`, `fix/…`, `docs/…`) unida a main por pull request | |
| Revisión de código (XP) | [COMPLETAR POR EL GRUPO]: si los pull requests se revisaron, indicar quién revisó; el historial de Git no lo registra | |
| Tablero por ciclo de vida | Product backlog, Sprint backlog, En progreso, En pruebas y Desplegado (ver `docs/BACKLOG_SPRINT.md`, tarea 18) | Herramienta usada: [COMPLETAR POR EL GRUPO] (la herramienta no justifica la metodología) |

No se mencionan ceremonias que el grupo no hizo.

## 6. Qué hizo el grupo cuando llegaron los requerimientos nuevos

Fecha de la reunión de octubre: [COMPLETAR POR EL GRUPO].

| Paso | Qué se hizo | Evidencia |
| --- | --- | --- |
| 1. Agrupar los requerimientos | Las 10 reglas y los tipos de organización se agruparon por tema: registro de actividades, puntaje, ajustes, ausencias, atenciones sociales y organizaciones | `docs/REQUERIMIENTOS_V2.md` (tarea 17, pendiente) |
| 2. Identificar RF y RNF | Cada regla quedó como requerimiento con código, criterio de aceptación y prueba | `docs/REQUERIMIENTOS_V2.md` (tarea 17, pendiente) |
| 3. Ajustar los casos de uso | Nuevas gestiones G06 Ajustes de puntaje, G07 Ausencias y G08 Atenciones sociales; casos nuevos CU-32 a CU-139; actores comprobados contra el sistema (184 de 184) | `docs/CASOS_DE_USO.md`, commit 0859227 |
| 4. Actualizar el diagrama de clases | Modelos nuevos Organizacion, Ajuste, Ausencia, CasoSocial y Comentario | Migración `0021_reglas_sgr.py`; `docs/DIAGRAMA_CLASES.md` (tarea 19b, pendiente) |
| 5. Crear las tareas nuevas y repriorizar | Lo que no cabía en el sprint se postergó según su valor para el municipio; la duración del sprint no cambió | `docs/BACKLOG_SPRINT.md` (tarea 18, pendiente) |
| 6. Implementar | Reglas de octubre, modelos y mantenedores (pull request #16, commits ffbb5e2 y 7b1a99f); correcciones y accesos en la rama `feat/requerimientos-octubre` (commits 6781d88, 791b9ac, 193eed5 y 3c2aaef) | Historial de Git |
| 7. Probar | Se corrigieron las 26 pruebas que fallaban y se agregaron pruebas para cada regla nueva: de 601 a 648 pruebas, todas aprobadas | Commits 93bab31 y 2fe7e6f; `PLAN_DE_PRUEBAS.md` |

## 7. Números para la presentación

Medidos el 21 de noviembre de 2026 en la rama `feat/requerimientos-octubre`. La versión completa, con CSV para los gráficos, va en `docs/RESULTADOS.md` (tarea 20d).

- 648 pruebas automáticas, 648 aprobadas.
- 171 casos de uso en 19 gestiones; 184 de 184 combinaciones de perfil y pantalla coinciden con los actores de los cuadros.
- 27 migraciones de base de datos (0001 a 0027).
- 15 pull requests integrados en main.

## 8. Estructura de la presentación según la rúbrica

| Parte | Tiempo | Criterio de la rúbrica | Contenido |
| --- | --- | --- | --- |
| Diagnóstico | 0:45 | Documentación final con propuesta de valor (10) | Problema de la Matriz SGR en planillas |
| Propuesta de valor y plan de mejora | 0:45 | Documentación final con propuesta de valor (10) | Qué resuelve el SGR y para quién |
| Metodología y requerimientos nuevos | 1:45 | Exposición oral (10) y defensa (10) | Secciones 5 y 6 |
| Diseño | 0:45 | Documentación final (10) | Casos de uso, clases y arquitectura |
| Demostración en vivo | 3:30 | Funcionalidad en la demostración (20) | Sección 2 |
| Resultados con números | 0:45 | Presentación de resultados con datos cuantificables (10) | Sección 7 y `docs/RESULTADOS.md` |
| Normativas y estándares | 0:30 | Normativas y estándares (10) | `docs/NORMATIVAS_Y_ESTANDARES.md` (tarea 20c) |
| Plan de mantención | 0:35 | Plan de mantención (20) | `docs/PLAN_MANTENCION.md` (tarea 20b) |
| Cierre | 0:10 | Confección de la presentación (10) | Pendientes y cierre |

El plan de mantención vale 20 puntos: aunque su tiempo sea corto, la diapositiva debe mostrar roles, frecuencias y herramientas en un calendario.

## 9. Lista para el día antes

- [ ] El servidor responde en `http://3.225.119.192` y muestra la portada.
- [ ] Entrar con cada usuario de `ACCESOS_EXPOSICION.txt`: `admin.demo`, `coordinador.demo`, `delegado.demo` y `funcionario.centro`. Cada uno llega a su panel.
- [ ] El período «Trimestre octubre-diciembre 2026» está abierto y el semáforo de Centro está en rojo para ese período.
- [ ] La meta de `funcionario.centro` en «Atención de casos sociales» tiene valor objetivo 2 y avance 0.
- [ ] No quedan actividades de ensayo aprobadas (si las hay, anular la aprobación como Coordinador).
- [ ] Hay un JPG o PDF de prueba de menos de 5 MB en el escritorio del computador de la exposición.
- [ ] El Profesional no entra a la auditoría y el Administrador sí.
- [ ] Las capturas de la sección 3 están en la presentación.
