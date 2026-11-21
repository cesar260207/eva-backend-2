# Trazabilidad de requerimientos

Reemplaza a la Tabla 38 del informe (trazabilidad con wireframes). Cada requerimiento funcional se sigue hasta
la pantalla real del sistema. Las pantallas que no son una URL son comandos que se ejecutan en el servidor.

| Requerimiento | Épica | Caso de alto nivel | Casos de detalle | Pantalla |
| --- | --- | --- | --- | --- |
| RF-001 Administrar delegaciones | EP-08 Administración, seguridad y trazabilidad | G10 Gestionar delegaciones | CU-86 Registrar delegación; CU-88 Modificar delegación; CU-89 Eliminar delegación | `/administracion/delegaciones/nuevo/`; `/administracion/delegaciones/<id>/editar/`; `/administracion/delegaciones/<id>/eliminar/` |
| RF-002 Administrar usuarios y roles | EP-08 Administración, seguridad y trazabilidad | G13 Gestionar funcionarios y usuarios | CU-104 Registrar funcionario; CU-106 Modificar funcionario; CU-98 Registrar rol | `/administracion/funcionarios/nuevo/`; `/administracion/funcionarios/<id>/editar/`; `/administracion/roles/nuevo/` |
| RF-003 Configurar cargos y funciones | EP-08 Administración, seguridad y trazabilidad | G11 Gestionar cargos | CU-93 Registrar cargo; CU-95 Modificar cargo | `/administracion/cargos/nuevo/`; `/administracion/cargos/<id>/editar/` |
| RF-004 Mantener catálogo de actividades y servicios | EP-08 Administración, seguridad y trazabilidad | G14 Gestionar catálogo | CU-112 Registrar elemento de catálogo; CU-114 Modificar elemento de catálogo | `/administracion/catalogo/nuevo/`; `/administracion/catalogo/<id>/editar/` |
| RF-005 Configurar períodos de medición | EP-08 Administración, seguridad y trazabilidad | G15 Gestionar períodos y parámetros | CU-117 Registrar período; CU-28 Abrir, cerrar o reabrir período | `/administracion/periodos/nuevo/`; `/administracion/periodos/<id>/estado/<acción>/` |
| RF-006 Configurar ponderaciones | EP-02 Medición y desempeño | G16 Gestionar ítems medibles y metas | CU-04 Registrar ítem medible; CU-129 Modificar ítem medible | `/administracion/items/nuevo/`; `/administracion/items/<id>/editar/` |
| RF-007 Configurar metas y umbrales | EP-02 Medición y desempeño | G16 Gestionar ítems medibles y metas | CU-05 Registrar meta; CU-133 Modificar meta | `/administracion/metas/nuevo/`; `/administracion/metas/<id>/editar/` |
| RF-008 Presentar ficha personal | EP-05 Monitoreo y control de gestión | G17 Consultar resultados | CU-06 Seguimiento de avance (ficha personal) | `/gestion/mi-ficha/` |
| RF-009 Registrar actividades | EP-01 Registro y gestión de actividades | G02 Gestionar actividades | CU-01 Registrar actividad | `/actividad/nueva/` |
| RF-010 Validar campos de actividad | EP-01 Registro y gestión de actividades | G02 Gestionar actividades | CU-01 Registrar actividad; CU-42 Modificar actividad | `/actividad/nueva/`; `/actividad/<código>/editar/` |
| RF-011 Generar código verificador de evidencia | EP-01 Registro y gestión de actividades | G02 Gestionar actividades | CU-01 Registrar actividad | `/actividad/nueva/` |
| RF-012 Asociar evidencia | EP-03 Evidencias y verificación | G03 Gestionar evidencias | CU-09 Subir evidencia; CU-52 Ver evidencia | `/actividad/<código>/evidencia/`; `/evidencia/<código>/archivo/` |
| RF-013 Validar evidencia | EP-03 Evidencias y verificación | G04 Validar actividades | CU-11 Aprobar o rechazar actividad | `/actividad/<código>/aprobar/ o /rechazar/` |
| RF-014 Controlar puntuación por validación | EP-03 Evidencias y verificación | G04 Validar actividades | CU-11 Aprobar o rechazar actividad; CU-54 Anular aprobación | `/actividad/<código>/aprobar/ o /rechazar/`; `/actividad/<código>/anular/` |
| RF-015 Registrar atención social por etapas | EP-01 Registro y gestión de actividades | G08 Gestionar atenciones sociales | CU-03 Registrar atención social | `/casos-sociales/nuevo/` |
| RF-016 Crear compromisos en agenda colectiva | EP-04 Agenda colectiva y compromisos | G05 Gestionar tubo de trabajo | CU-02 Registrar compromiso | `/agenda/nueva/` |
| RF-017 Asignar compromiso | EP-04 Agenda colectiva y compromisos | G05 Gestionar tubo de trabajo | CU-02 Registrar compromiso; CU-58 Modificar tarea | `/agenda/nueva/`; `/agenda/<id>/editar/` |
| RF-018 Gestionar estados | EP-04 Agenda colectiva y compromisos | G05 Gestionar tubo de trabajo | CU-13 Actualizar estado de la tarea | `/agenda/<id>/estado/<estado>/` |
| RF-019 Controlar plazos | EP-04 Agenda colectiva y compromisos | G05 Gestionar tubo de trabajo | CU-14 Seguimiento de compromisos; CU-12 Consultar agenda compartida | `/solicitudes/`; `/agenda/` |
| RF-020 Relacionar agenda y medición | EP-04 Agenda colectiva y compromisos | G05 Gestionar tubo de trabajo | CU-13 Actualizar estado de la tarea | `/agenda/<id>/estado/<estado>/` |
| RF-021 Generar resumen colectivo | EP-05 Monitoreo y control de gestión | G17 Consultar resultados | CU-18 Consultar resumen ejecutivo | `/gestion/panel/ y /gestion/resumen/` |
| RF-022 Calcular avance actual | EP-05 Monitoreo y control de gestión | G17 Consultar resultados | CU-06 Seguimiento de avance (ficha personal); CU-16 Consultar semáforo de cumplimiento | `/gestion/mi-ficha/`; `/gestion/semaforo/` |
| RF-023 Calcular porcentaje de cumplimiento | EP-05 Monitoreo y control de gestión | G17 Consultar resultados | CU-06 Seguimiento de avance (ficha personal) | `/gestion/mi-ficha/` |
| RF-024 Calcular cumplimiento ponderado | EP-05 Monitoreo y control de gestión | G17 Consultar resultados | CU-06 Seguimiento de avance (ficha personal) | `/gestion/mi-ficha/` |
| RF-025 Aplicar incentivos y penalizaciones | EP-02 Medición y desempeño | G06 Gestionar ajustes de puntaje | CU-67 Aplicar o rechazar ajuste | `/ajustes/<id>/aplicar/ o /rechazar/` |
| RF-026 Calcular meta esperada al día | EP-05 Monitoreo y control de gestión | G17 Consultar resultados | CU-17 Comparar avance esperado y real | `/gestion/` |
| RF-027 Mostrar semáforo de avance | EP-05 Monitoreo y control de gestión | G17 Consultar resultados | CU-16 Consultar semáforo de cumplimiento | `/gestion/semaforo/` |
| RF-028 Mostrar tablero personal | EP-05 Monitoreo y control de gestión | G17 Consultar resultados | CU-06 Seguimiento de avance (ficha personal) | `/gestion/mi-ficha/` |
| RF-029 Mostrar tablero de delegación | EP-05 Monitoreo y control de gestión | G17 Consultar resultados | CU-136 Consultar territorio y delegación; CU-18 Consultar resumen ejecutivo | `/territorio/ y /delegacion/<nombre>/`; `/gestion/panel/ y /gestion/resumen/` |
| RF-030 Medir actividad reciente | EP-06 Reportabilidad y toma de decisiones | G18 Generar informes | CU-20 Generar informe | `/gestion/informes/` |
| RF-031 Mostrar vista global por cargos | EP-05 Monitoreo y control de gestión | G17 Consultar resultados | Sin caso: no implementado (postergado) | · |
| RF-032 Buscar y filtrar información | EP-06 Reportabilidad y toma de decisiones | G18 Generar informes | CU-20 Generar informe; CU-41 Consultar actividades | `/gestion/informes/`; `/actividades/ y /actividad/<código>/` |
| RF-033 Generar y exportar informes | EP-06 Reportabilidad y toma de decisiones | G18 Generar informes | CU-20 Generar informe | `/gestion/informes/` |
| RF-034 Permitir trabajo simultáneo | EP-01 Registro y gestión de actividades | G02 Gestionar actividades | CU-42 Modificar actividad | `/actividad/<código>/editar/` |
| RF-035 Facilitar coordinación | EP-01 Registro y gestión de actividades | G02 Gestionar actividades | CU-24 Comentar actividad | `/actividad/<código>/comentario/` |
| RF-036 Mantener trazabilidad | EP-08 Administración, seguridad y trazabilidad | G19 Consultar auditoría y perfiles | CU-30 Consultar auditoría de cambios | `/administracion/auditoria/` |
| RF-037 Emitir alertas | EP-05 Monitoreo y control de gestión | G17 Consultar resultados | CU-31 Consultar alertas | `/gestion/alertas/` |
| RF-038 Versionar parámetros | EP-08 Administración, seguridad y trazabilidad | G15 Gestionar períodos y parámetros | CU-121 Registrar parámetro; CU-25 Modificar parámetro | `/administracion/parametros/nuevo/`; `/administracion/parametros/<id>/editar/` |
| RF-039 Importar organizaciones comunitarias con su delegación y tipo (octubre 2026) | EP-01 Registro y gestión de actividades | G09 Gestionar organizaciones comunitarias | CU-83 Importar organizaciones; CU-79 Consultar organizaciones | comando importar_organizaciones (servidor); `/administracion/organizaciones/` |
| RF-040 Registrar la gestión interna como otra gestión (octubre 2026) | EP-01 Registro y gestión de actividades | G02 Gestionar actividades | CU-01 Registrar actividad | `/actividad/nueva/` |
| RF-041 Exigir nombre y teléfono del contacto para puntuar (octubre 2026) | EP-01 Registro y gestión de actividades | G02 Gestionar actividades | CU-01 Registrar actividad | `/actividad/nueva/` |
| RF-042 Limitar los ingresos diarios a 7 (octubre 2026) | EP-01 Registro y gestión de actividades | G02 Gestionar actividades | CU-01 Registrar actividad | `/actividad/nueva/` |
| RF-043 Cerrar la semana de ingresos (octubre 2026) | EP-01 Registro y gestión de actividades | G02 Gestionar actividades | CU-01 Registrar actividad; CU-42 Modificar actividad | `/actividad/nueva/`; `/actividad/<código>/editar/` |
| RF-044 Registrar gestiones previas sin puntaje (octubre 2026) | EP-01 Registro y gestión de actividades | G02 Gestionar actividades | CU-01 Registrar actividad | `/actividad/nueva/` |
| RF-045 Limitar el cumplimiento de cada ítem a 120 % (octubre 2026) | EP-08 Administración, seguridad y trazabilidad | G15 Gestionar períodos y parámetros | CU-25 Modificar parámetro | `/administracion/parametros/<id>/editar/` |
| RF-046 Registrar felicitaciones y reclamos (octubre 2026) | EP-02 Medición y desempeño | G06 Gestionar ajustes de puntaje | CU-64 Informar felicitación o reclamo; CU-67 Aplicar o rechazar ajuste | `/ajustes/nuevo/`; `/ajustes/<id>/aplicar/ o /rechazar/` |
| RF-047 Registrar ausencias desde el semáforo (octubre 2026) | EP-02 Medición y desempeño | G07 Gestionar ausencias | CU-71 Registrar ausencia; CU-72 Consultar ausencias | `/ausencias/nuevo/`; `/administracion/ausencias/` |
| RF-048 Mostrar el resultado del equipo (octubre 2026) | EP-05 Monitoreo y control de gestión | G17 Consultar resultados | CU-18 Consultar resumen ejecutivo | `/gestion/panel/ y /gestion/resumen/` |
| RF-049 Cargar la matriz de cargos (octubre 2026) | EP-02 Medición y desempeño | G16 Gestionar ítems medibles y metas | CU-131 Cargar matriz de cargos | comando cargar_matriz (servidor) |
| RF-050 Calcular el ítem del tubo de trabajo (octubre 2026) | EP-04 Agenda colectiva y compromisos | G05 Gestionar tubo de trabajo | CU-13 Actualizar estado de la tarea | `/agenda/<id>/estado/<estado>/` |
