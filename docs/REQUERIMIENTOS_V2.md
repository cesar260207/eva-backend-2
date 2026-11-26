# Documento de requerimientos del SGR, versión 2

La versión 1 está en el informe de diseño (etapa 2): RF-001 a RF-038, RNF-001 a RNF-018 y RN-001 a RN-013. Esta versión agrega los requerimientos que la Municipalidad de La Serena entregó en la reunión de octubre de 2026 («Nuevo Requerimientos Octubre 2026») y los que salen de la Matriz SGR trimestral y del descriptor de funciones. Los requerimientos de la versión 1 siguen vigentes salvo donde se indica.

## Registro de versiones

| Versión | Fecha | Origen | Cambios |
| --- | --- | --- | --- |
| v1 | Septiembre de 2026 | Informe de diseño (etapa 2) | RF-001 a RF-038, RNF-001 a RNF-018, RN-001 a RN-013 |
| v2 | Octubre y noviembre de 2026 | Reunión de octubre 2026, Matriz SGR y descriptor de funciones | RF-039 a RF-050 y RNF-019 a RNF-020; RF-015, RF-025 y RF-035 pasan de «no implementado» a implementados; RN-014 a RN-018 |
| v3 | Noviembre de 2026 | Matriz SGR completa: las 25 hojas y sus fórmulas | RF-063 a RF-065; RF-031 pasa de «no implementado» a implementado |

Fecha exacta de la reunión de octubre: [COMPLETAR POR EL GRUPO].

## Cómo se procesaron los requerimientos nuevos

1. **Agrupar.** Las reglas del documento de octubre se agruparon por tema: registro de actividades (reglas 1 a 5), cálculo del puntaje (reglas 6 y 7), ajustes (regla 8), ausencias (regla 9), trabajo en equipo (regla 10) y organizaciones comunitarias (tipos).
2. **Formalizar.** Cada regla quedó como requerimiento funcional (RF) o no funcional (RNF), con criterio de aceptación y la prueba automática que lo verifica. Las condiciones de cálculo se registraron además como reglas de negocio (RN).
3. **Ajustar el diseño.** Casos de uso nuevos en las gestiones G06 Ajustes de puntaje, G07 Ausencias y G08 Atenciones sociales ([CASOS_DE_USO.md](CASOS_DE_USO.md)) y clases nuevas en el modelo ([DIAGRAMA_CLASES.md](DIAGRAMA_CLASES.md)).
4. **Repriorizar.** Las tareas nuevas entraron al sprint backlog y lo que no cabía se postergó según su valor para el municipio ([BACKLOG_SPRINT.md](BACKLOG_SPRINT.md)).

## Requerimientos funcionales nuevos

Prioridad: Alta, si sin ella el puntaje de la matriz queda mal calculado; Media, si mejora la operación sin cambiar el puntaje.

| Código | Requerimiento | Origen | Prioridad | Criterio de aceptación | Prueba que lo verifica |
| --- | --- | --- | --- | --- | --- |
| RF-039 | El sistema deberá importar las organizaciones comunitarias del municipio con su delegación y su tipo. | Reunión de octubre 2026 (tipos de organización) y base de datos de juntas de vecinos | Media | Dado el Excel del municipio, cuando se importa, entonces CIAS, PAMPA, ANTENA y AV DEL MAR quedan en su delegación, el tipo se deduce del nombre (junta de vecinos, adulto mayor, deportiva, cultural, comité o funcional) y lo que no corresponde a una delegación queda sin verificar y con observación. | `ImportarOrganizacionesTests` (test_unit_organizacion.py) |
| RF-040 | El sistema deberá registrar como «otra gestión», sin puntaje, las actividades en que el usuario es el delegado. | Reunión de octubre 2026, regla 1 | Alta | Dada una actividad marcada como gestión interna o vinculada a una tarea de origen interno, cuando se aprueba, entonces no suma al avance y su motivo dice «Otra gestión». | `test_la_actividad_de_una_tarea_interna_es_otra_gestion`, `test_una_actividad_suelta_marcada_como_interna_es_otra_gestion`, `test_el_formulario_permite_marcar_gestion_interna` |
| RF-041 | El sistema deberá dejar sin puntaje las actividades que no lleven nombre y teléfono del usuario. | Reunión de octubre 2026, regla 2 | Alta | Dada una actividad sin nombre o sin teléfono del contacto, cuando se aprueba, entonces se conserva en el historial pero no suma. | `test_sin_nombre_o_telefono_del_usuario_no_puntua`, `test_una_actividad_aprobada_sin_contacto_no_suma_al_avance` |
| RF-042 | El sistema deberá impedir más de 7 ingresos de actividades por funcionario y día. | Reunión de octubre 2026, regla 3 | Alta | Dados 7 ingresos del mismo autor en un día, cuando intenta el octavo, entonces se rechaza; el máximo es un parámetro del período. | `test_el_octavo_ingreso_del_dia_se_rechaza`, `test_el_limite_diario_es_por_autor_y_por_dia`, `test_el_limite_diario_se_configura_por_periodo` |
| RF-043 | El sistema deberá cerrar la semana: desde el martes no se ingresan actividades de la semana anterior. | Reunión de octubre 2026, regla 4 | Alta | Dado que hoy es martes o un día posterior, cuando se registra una actividad de la semana anterior, entonces se rechaza; el lunes todavía se acepta. Corregir una actividad ya registrada (por ejemplo, rechazada) sí se permite. | `test_el_lunes_permite_la_semana_anterior`, `test_desde_martes_la_semana_anterior_se_cierra`, `test_no_se_ingresa_una_actividad_de_una_semana_cerrada`, `test_corregir_una_actividad_rechazada_antigua_la_devuelve_a_pendiente` |
| RF-044 | El sistema deberá registrar las gestiones previas a una acción (correos, coordinaciones, invitaciones) sin darles puntaje. | Reunión de octubre 2026, regla 5 | Alta | Dada una actividad de tipo «gestión previa», cuando se aprueba, entonces queda en el historial y no suma. | `test_la_gestion_previa_conserva_el_historial_sin_puntaje` |
| RF-045 | El sistema deberá limitar el cumplimiento de cada ítem a un máximo configurable, 120 % por defecto. | Reunión de octubre 2026, regla 7 | Alta | Dado un avance que supera el 120 % de la meta, cuando se calcula, entonces el cumplimiento queda en 120 %, también con felicitaciones. | `test_el_tope_por_defecto_es_120`, `test_la_felicitacion_no_supera_el_tope` |
| RF-046 | El sistema deberá registrar felicitaciones y reclamos con respaldo formal, informados por el delegado y aplicados o rechazados por la coordinación. | Reunión de octubre 2026, regla 8 | Alta | Dado un ajuste informado con respaldo, cuando la coordinación lo aplica, entonces una felicitación suma 10 puntos (máximo 3) y un reclamo resta 30, el semáforo se recalcula y la decisión queda en la auditoría. | `DecidirAjusteTests`, `CumplimientoConAjustesTests`, `RecalculoDelSemaforoTests` |
| RF-047 | El delegado deberá ingresar desde el semáforo los días libres, vacaciones, días administrativos, licencias y emergencias de su equipo, para ajustar lo esperado. | Reunión de octubre 2026, regla 9; hoja SEMAFORO de la matriz (tipo «Emergencia») | Alta | Dado un delegado en el semáforo, cuando registra una ausencia, entonces los días se descuentan de lo esperado al día del funcionario y sus indicadores se recalculan. | `AusenciaDesdeSemaforoTests`, `DiasAusenciaTests`, `EsperadoConAusenciasTests`, `test_registrar_y_borrar_una_ausencia_recalcula` |
| RF-048 | El sistema deberá mostrar el resultado del equipo de cada delegación, además del individual. | Reunión de octubre 2026, regla 10 | Media | Dado un período con indicadores, cuando se abre el resumen, entonces se ve el promedio por delegación y el umbral colectivo. | `test_semaforo_y_resumen_comparten_los_resultados` (cubierto por el resumen de RF-021 y RF-029) |
| RF-049 | El sistema deberá cargar los cargos de la matriz con sus ítems, ponderación, meta trimestral y tipo de cálculo, sin nombres de personas. | Matriz SGR trimestral y descriptor de funciones | Alta | Dada la matriz del municipio, cuando se genera el JSON y se carga en un período, entonces se crean los 13 cargos y sus 80 ítems (el de «Pendientes en tubo» se completa desde la hoja SALON) y no se copia ningún nombre de persona. | `GenerarMatrizTests`, `CargarMatrizTests` (test_unit_matriz.py) |
| RF-050 | El sistema deberá calcular el ítem «Soluciones de ingresos al tubo» como porcentaje de tareas realizadas sobre tareas ingresadas con contacto. | Matriz SGR (ítem presente en 12 de 13 cargos) | Alta | Dadas tareas del tubo con contacto en el período, cuando cambia su estado, entonces el cumplimiento es realizadas / ingresadas y el semáforo se recalcula. | `ItemTipoTuboTests`, `test_cambiar_el_estado_de_una_tarea_del_tubo_recalcula` |
| RF-063 | El sistema deberá medir el ítem «Pendientes en tubo menor a 10 %» por tramos sobre todo el tubo de la delegación. | Matriz SGR, hoja SALON (Planificación y control) | Alta | Dadas tareas del tubo con contacto en el período, cuando se calcula, entonces el avance es el % de tareas ingresadas o pendientes y el cumplimiento vale 100 hasta 10 %, 50 hasta 50 % y 0 sobre eso; sin tareas vale 0. Cambiar el estado de cualquier tarea lo recalcula. | `PuntajePorPendientesTests`, `ItemPendientesDelTuboTests`, `MatrizCompletaDesdeSalonTests` (test_unit_matriz_sgr.py) |
| RF-064 | El sistema deberá registrar las fechas de ingreso, visita e informe de cada atención social y mostrar si cumple sus plazos. | Matriz SGR, hojas G SOC y LISTA | Media | Dada una atención social, cuando se registran sus fechas, entonces se valida su orden y se muestra cada tramo como cumplido, en curso o vencido (visita programada ≤ 10 días, visita el día programado, informe ≤ 4 días tras la visita y ≤ 20 desde el ingreso, máximo 2 reingresos); un informe social exige uno de sus tres subtipos. | `AtencionSocialTests` (test_unit_matriz_sgr.py) |
| RF-065 | El sistema deberá importar las hojas TUBO y TUBO CARTAS de la planilla sin duplicar tareas. | Matriz SGR, hojas TUBO y TUBO CARTAS | Media | Dado un CSV de la planilla, cuando se ejecuta `importar_tubo` sin `--aplicar`, entonces solo informa; con `--aplicar` guarda las tareas válidas con su historial, y repetirlo no las duplica. | `ImportarTuboTests` (test_unit_matriz_sgr.py) |

La regla 6 («no deben realizar ingresos solo para generar puntaje») es una política de uso del municipio, no una función del sistema. El SGR la apoya con el tope diario (RF-042), el tope por ítem (RF-045) y la auditoría de cada registro (RF-036), que permiten revisar los patrones de ingreso.

## Requerimientos de la versión 1 que cambian de estado

| Código | Antes (v1) | Ahora (v2) | Evidencia |
| --- | --- | --- | --- |
| RF-015 Registrar atención social | No implementado | Implementado: hasta tres gestiones por usuario, desde el menú del Profesional | `CasoSocialTests`, `AccesosOctubreTests` |
| RF-025 Aplicar incentivos y penalizaciones | No implementado (el ajuste no entraba al cálculo) | Implementado como felicitaciones y reclamos (RF-046) | `CumplimientoConAjustesTests`, `DecidirAjusteTests` |
| RF-035 Facilitar coordinación | No implementado | Implementado: comentarios visibles en el detalle de la actividad | `AccesosOctubreTests` |
| RF-031 Mostrar vista global por cargos | No implementado (postergado) | Implementado: Resultados → Matriz por cargos (`/gestion/matriz/`), con exportación a Excel | `MatrizPorCargosTests`, `MatrizDeAccesosTests` |
| RF-027 Mostrar semáforo | Se recalculaba solo al aprobar actividades | También al decidir ajustes, registrar ausencias y cambiar tareas del tubo | `RecalculoDelSemaforoTests` |

## Requerimientos no funcionales nuevos

| Código | Atributo | Requerimiento | Origen | Prioridad | Criterio de aceptación | Prueba o evidencia |
| --- | --- | --- | --- | --- | --- | --- |
| RNF-019 | Privacidad de los datos del cliente | Los archivos del municipio con datos personales (Excel y Word) no se publican en el repositorio; lo que se versiona sale de ellos sin nombres ni domicilios. | Datos entregados en octubre 2026 (RNF-009 de la v1) | Alta | `data/*.xlsx` y `docs/requerimientos/` están en `.gitignore`; `data/matriz_cargos.json` no contiene alias ni registros de gestiones. | `.gitignore`; `test_no_copia_los_nombres_de_personas_ni_las_gestiones` |
| RNF-020 | Mantenibilidad de las reglas | Los valores de las reglas de octubre (tope, felicitación, máximo de felicitaciones, reclamo, ingresos diarios) son parámetros versionados del período y se cambian sin tocar el código. | Diferencias entre la matriz y el documento de octubre (RNF-015 de la v1) | Alta | Cambiar el parámetro en el mantenedor cambia el cálculo; cargar la matriz no pisa un valor ya definido. | `test_el_valor_del_reclamo_es_un_parametro`, `test_el_limite_diario_se_configura_por_periodo`, `test_deja_los_parametros_de_octubre_sin_pisar_los_existentes` |

## Reglas de negocio nuevas

| Código | Regla |
| --- | --- |
| RN-014 | Una actividad puntúa solo si tiene nombre y teléfono del contacto, no es gestión interna y no es gestión previa (reglas 1, 2 y 5). |
| RN-015 | Máximo de ingresos por autor y día: parámetro `max_ingresos_diarios`, 7 por defecto (regla 3). |
| RN-016 | Desde el martes no se ingresan actividades de la semana anterior; la corrección de una actividad ya registrada no está sujeta al cierre mientras no cambie su día (regla 4). |
| RN-017 | Cumplimiento del ítem = mín(avance / meta × 100, tope) + 10 por felicitación aplicada (máximo 3) − 30 por reclamo aplicado, entre 0 y el tope (reglas 7 y 8). |
| RN-018 | Lo esperado al día descuenta los días de ausencia del funcionario, sin contar dos veces los días que se traslapan (regla 9). |

## Preguntas pendientes para el municipio

Están también en el README.

1. **Tope del cumplimiento.** La matriz usa 150 % y el documento de octubre 120 %. El sistema usa 120 % (parámetro `maximo_cumplimiento`).
2. **Valor del reclamo.** La hoja RECLAMOS y las hojas «Coordinador DISERCO» y «Gestor social 1» restan 20 %; las demás hojas de cargo, 30 %. El sistema usa -30 % (parámetro `valor_reclamo`).
3. **Ponderaciones de «Planificación y control».** Su hoja suma 85 %; el 15 % que falta es el ítem «Pendientes en tubo menor a 10 %» de la hoja SALON, que ahora se carga desde ahí (RF-063). Falta que el municipio lo confirme.
4. **Meta del ítem «Emergencia».** En varias hojas la meta trimestral coincide con el avance (por ejemplo, 304); falta confirmar la meta real.
5. **Felicitaciones al gestor.** La regla 8 dice que las felicitaciones del usuario al gestor por mensaje no son válidas. El sistema permite dirigir un ajuste a cualquier funcionario siempre que tenga respaldo formal y lo informe el delegado; falta confirmar si una felicitación formal a un gestor cuenta.
6. **Organizaciones sin delegación.** 2 organizaciones del territorio «ALFALFARES» y 22 sin territorio quedan para asignar a mano.
