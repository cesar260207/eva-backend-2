# Sprint backlog repriorizado por los requerimientos de octubre 2026

## Llegada de los requerimientos

- **Fecha de la reunión de octubre:** [COMPLETAR POR EL GRUPO].
- **Sprint en curso cuando llegaron:** [COMPLETAR POR EL GRUPO] (el informe planificó sprints de 3 semanas, de Sprint 0 a Sprint 4; Tabla 30).
- **Qué llegó:** el documento «Nuevo Requerimientos Octubre 2026» (10 reglas y los tipos de organización), la Matriz SGR trimestral con 13 hojas de cargo, el descriptor de funciones y la base de datos de juntas de vecinos. El detalle formalizado está en [REQUERIMIENTOS_V2.md](REQUERIMIENTOS_V2.md).

## Criterio de priorización

Se ordenó por el valor para el municipio:

1. **Lo que cambia el puntaje de un funcionario.** Si el cálculo no aplica una regla, la matriz evalúa mal a las personas: entra primero.
2. **Lo que el delegado o la coordinación necesitan para aplicar las reglas** (botones, accesos, ausencias desde el semáforo): sin pantalla, la regla existe pero nadie la usa.
3. **Lo que mejora la operación sin cambiar el puntaje** (importación de organizaciones, carga de la matriz).
4. **Lo que depende de terceros o no cambia el resultado de la medición** (HTTPS con dominio municipal, monitoreo, vista global por cargos): se posterga al product backlog o al plan de mantención.

## Duración del sprint

La duración del sprint **no se alargó ni se acortó**: se mantuvieron las 3 semanas del plan. Lo que no cabía se movió al product backlog según el criterio anterior. [CONFIRMAR POR EL GRUPO las fechas de inicio y término del sprint.]

## Sprint backlog antes de los requerimientos de octubre

Según el plan del informe (Tabla 30, Sprint 4 «Calidad y entrega») y las historias P2 pendientes:

| Elemento | Origen |
| --- | --- |
| Pruebas integrales y correcciones | Plan de sprints, Sprint 4 |
| HTTPS (RNF-006) | Plan de sprints, Sprint 4 |
| Despliegue, manuales y demostración | Plan de sprints, Sprint 4 |
| HU-03 Atención social por etapas (RF-015), P2 | Backlog, «si hay capacidad» |
| HU-24 Comentarios (RF-035), P2 | Backlog, «si hay capacidad» |
| HU-08 Vista global por cargos (RF-031), P2 | Backlog, «si hay capacidad» |

## Sprint backlog después de repriorizar

### Entró al sprint

| Tarea | Por qué entró (valor) | Requerimiento | Evidencia |
| --- | --- | --- | --- |
| Reglas de octubre en el modelo: gestión interna, contacto obligatorio, 7 ingresos diarios, cierre semanal, gestión previa, tope 120 %, ajustes, ausencias, ítem tipo tubo | Cambian el puntaje de cada funcionario | RF-040 a RF-047, RF-050 | Pull request #16 (commits ffbb5e2 y 7b1a99f, merge f910537) |
| Corregir el conteo de días de ausencia | Contaba mal los días y bajaba lo esperado de más | RF-047 | 6781d88 |
| Cierre semanal solo al registrar | Bloqueaba corregir una actividad rechazada | RF-043 | 791b9ac |
| Arreglar las 26 pruebas que fallaban desde el PR #16 | El plan de pruebas marcaba «Reprobado» en los casos de la demostración | Todos | 93bab31 |
| Ajustes sin delegación no suman los de otras personas | Error de cálculo encontrado al escribir las pruebas | RF-046 | 3e31b5b |
| Pruebas de las reglas de octubre | Sin pruebas no hay evidencia de que la regla funciona | RF-040 a RF-047 | 2fe7e6f |
| Accesos a informar ajuste, atención social y comentarios (y arreglo de los comentarios, que no se guardaban) | La regla existía pero nadie podía usarla desde la interfaz | RF-046, RF-015, RF-035 | 193eed5 |
| Botones «Aplicar» y «Rechazar» ajustes | Ningún ajuste se aplicaba nunca | RF-046 | 3c2aaef |
| Recalcular el semáforo al decidir ajustes, ausencias y tareas del tubo | El semáforo mostraba un resultado viejo hasta correr un comando | RF-027 | ca7fad0 |
| Registrar ausencias desde el semáforo | Regla 9: lo debe hacer el delegado en esa pantalla | RF-047 | 21833b3 |
| Casilla de gestión interna en actividades sueltas | Regla 1 también para actividades sin tarea | RF-040 | 5d34235 |
| Importar organizaciones por territorio y tipo | 1.812 organizaciones quedaban sin delegación | RF-039 | a394a65 |
| Cargar la matriz de 13 cargos sin nombres de personas | Los cargos reales reemplazan los 4 genéricos | RF-049 | 6a2ce4b |
| Parámetros y preguntas pendientes de la matriz | La matriz y el documento de octubre no coinciden | RNF-020 | d895c89 |
| Datos de demostración del trimestre actual | La demostración necesita un período vigente como el del servidor | | Commit de `seed_demo` (tarea 15) |
| HU-03 Atención social (RF-015) y HU-24 Comentarios (RF-035) | Atención social: la matriz tiene cinco hojas de gestor social que la registran. Comentarios: el modelo llegó con el PR #16 y solo faltaba hacerlo usable | RF-015, RF-035 | PR #16 y 193eed5 |
| Casos de uso, requerimientos v2, diagrama de clases, plan de mantención | Evidencia escrita del proceso y requisitos de la rúbrica | | 0859227 y commits de documentación |

### Salió o se postergó

| Elemento | Destino | Por qué |
| --- | --- | --- |
| HTTPS (RNF-006) | Plan de mantención perfectiva, prioridad alta | Necesita un dominio municipal y su certificado, que dependen de la Municipalidad; no cambia el cálculo del puntaje |
| HU-08 Vista global por cargos (RF-031) | Product backlog | Útil para la coordinación, pero no cambia el puntaje; el resumen por delegación cubre la vista de equipo (regla 10) |
| Monitoreo con alarmas (RNF-018) | Plan de mantención perfectiva | Es operación, no funcionalidad para el usuario |
| Copia de respaldos fuera del servidor | Plan de mantención perfectiva | Requiere un bucket S3 o almacenamiento institucional |
| Límite de intentos de inicio de sesión y páginas de error propias | Product backlog | Mejoras de seguridad y usabilidad sin efecto en la medición |

## Tablero por ciclo de vida

Estado de las tareas de esta fase al 21 de noviembre de 2026. La herramienta del tablero es [COMPLETAR POR EL GRUPO]; las columnas siguen el ciclo de vida, no la herramienta.

| Product backlog | Sprint backlog | En progreso | En pruebas | Desplegado |
| --- | --- | --- | --- | --- |
| HTTPS con dominio (RNF-006) | Desplegar la rama `feat/requerimientos-octubre` en AWS (migraciones 0027 y 0028) | Presentación de la exposición | Accesos del menú y comentarios (193eed5) | Reglas de octubre, modelos y mantenedores (PR #16, f910537, desplegado el 20 de noviembre de 2026) |
| Vista global por cargos (RF-031) | Respaldo automático con cron en el servidor | Completar los datos marcados [COMPLETAR POR EL GRUPO] | Botones de ajustes (3c2aaef) | Perfil Profesional y permisos por perfil (migraciones 0021 a 0026) |
| Monitoreo con CloudWatch (RNF-018) | Cargar la matriz y las organizaciones en el servidor | | Recálculo del semáforo (ca7fad0) | |
| Copia de respaldos en S3 | Regenerar la imagen `diapositiva_g06.png` con Graphviz | | Ausencias desde el semáforo (21833b3) | |
| Límite de intentos de login | Exigir las pruebas de GitHub Actions en `main` | | Gestión interna (5d34235) | |
| Páginas de error 404 y 500 | | | Importación de organizaciones (a394a65) | |
| | | | Matriz de cargos (6a2ce4b) | |
| | | | Correcciones de la FASE 1 (6781d88, 791b9ac, 93bab31, 3e31b5b, 2fe7e6f) | |

«En pruebas» significa que la tarea tiene su commit, pasa todas las pruebas automáticas y espera el pull request y el despliegue. Una tarea pasa a «Desplegado» cuando está en el servidor de AWS.
