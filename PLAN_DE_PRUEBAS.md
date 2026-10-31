# Plan de pruebas del Sistema de Gestión de Delegaciones

Generado con `python manage.py plan_pruebas` a partir de los docstrings de las pruebas y de su ejecución. No se edita a mano: se vuelve a generar.

## 1. Identificación del documento

| Campo | Información |
|---|---|
| Nombre del proyecto | Sistema de Gestión de Delegaciones |
| Tipo de pruebas | Unitarias (las de integración se incluyen como complemento) |
| Versión | 1.0 |
| Fecha | 31-10-2026 |
| Responsable del documento | Por definir |
| Equipo de desarrollo | Dante Fredes, César Aranda, Faride Luna, Vinzenz Lafferte |
| Ambiente de pruebas | Desarrollo, base de datos de pruebas (sqlite) |
| Tecnología utilizada | Python 3.14.4, Django 5.2.18, unittest de Django |

## 2. Resumen de resultados

| Concepto | Cantidad |
|---|---|
| Pruebas ejecutadas | 581 |
| Unitarias | 381 |
| De integración | 200 |
| Aprobadas | 581 |
| Reprobadas o con error | 0 |

## 3. Cobertura por caso de uso

Los casos de uso son los de la especificación detallada (CU-01 a CU-30). «Cubierto por sus subcasos» indica que el caso base no tiene pruebas propias pero sí sus extensiones.

| CU | Nombre | Unitarias | Integración (por clase) | Situación |
|---|---|---|---|---|
| CU-01 | Registro de actividades | 3 | 31 | Aprobado |
| CU-01.1 | Validar campos de actividad | 7 | 19 | Aprobado |
| CU-01.2 | Gestionar error de validación | 5 | 19 | Aprobado |
| CU-02 | Registro de compromisos ciudadanos | 2 | 6 | Aprobado |
| CU-02.1 | Validar datos de compromiso | 4 | 0 | Aprobado |
| CU-02.2 | Bloquear guardado por campos faltantes | 3 | 0 | Aprobado |
| CU-02.3 | Destacar compromiso vencido | 1 | 12 | Aprobado |
| CU-04 | Administración de funciones por cargo | 1 | 26 | Aprobado |
| CU-04.1 | Validar reglas de configuración | 4 | 0 | Aprobado |
| CU-04.2 | Bloquear guardado por ponderación inválida | 3 | 0 | Aprobado |
| CU-05 | Definición de metas | 1 | 15 | Aprobado |
| CU-05.1 | Validar parámetros de meta | 1 | 0 | Aprobado |
| CU-05.2 | Bloquear guardado por valor inválido | 2 | 0 | Aprobado |
| CU-05.3 | Notificar período cerrado | 1 | 0 | Aprobado |
| CU-06 | Seguimiento de avance | 19 | 14 | Aprobado |
| CU-06.1 | Recalcular indicadores automáticamente | 2 | 15 | Aprobado |
| CU-06.2 | Destacar meta cumplida | 1 | 12 | Aprobado |
| CU-07 | Cálculo automático de cumplimiento | 0 | 15 | Aprobado |
| CU-07.1 | Aplicar fórmulas de medición | 10 | 0 | Aprobado |
| CU-07.2 | Recalcular por anulación de registro | 2 | 8 | Aprobado |
| CU-07.3 | Mostrar detalle en reporte | 3 | 12 | Aprobado |
| CU-09 | Registro de evidencia fotográfica | 9 | 4 | Aprobado |
| CU-09.1 | Validar archivo de evidencia | 2 | 0 | Aprobado |
| CU-09.2 | Rechazar carga inválida | 3 | 5 | Aprobado |
| CU-10 | Generación de códigos verificadores | 3 | 31 | Aprobado |
| CU-10.1 | Buscar actividad por código | 2 | 19 | Aprobado |
| CU-10.2 | Consulta sin coincidencias | 1 | 19 | Aprobado |
| CU-11 | Validación de actividades | 18 | 21 | Aprobado |
| CU-11.1 | Registrar trazabilidad de decisión | 7 | 8 | Aprobado |
| CU-11.2 | Bloquear aporte al avance | 6 | 8 | Aprobado |
| CU-12 | Agenda compartida | 8 | 7 | Aprobado |
| CU-12.1 | Filtrar agenda compartida | 8 | 1 | Aprobado |
| CU-12.2 | Consulta sin coincidencias en agenda | 2 | 0 | Aprobado |
| CU-13 | Actualización de estados | 8 | 18 | Aprobado |
| CU-13.1 | Registrar historial de cambio de estado | 4 | 6 | Aprobado |
| CU-13.2 | Reflejar cierre de compromiso | 3 | 0 | Aprobado |
| CU-14 | Seguimiento de compromisos | 2 | 0 | Aprobado |
| CU-14.1 | Clasificar compromisos por vencimiento | 3 | 0 | Aprobado |
| CU-14.2 | Generar alerta por vencimiento próximo | 14 | 12 | Aprobado |
| CU-16 | Semáforo de cumplimiento | 4 | 10 | Aprobado |
| CU-16.1 | Calcular estado del semáforo | 2 | 25 | Aprobado |
| CU-17 | Comparación entre avance esperado y real | 0 | 22 | Aprobado |
| CU-17.1 | Calcular diferencia de avance | 3 | 0 | Aprobado |
| CU-17.2 | Destacar desviación significativa | 1 | 12 | Aprobado |
| CU-18 | Resumen ejecutivo | 6 | 10 | Aprobado |
| CU-18.1 | Consolidar datos de delegación | 9 | 10 | Aprobado |
| CU-18.2 | Navegar al detalle de gestión | 1 | 0 | Aprobado |
| CU-20 | Generación de informes | 1 | 15 | Aprobado |
| CU-20.1 | Consolidar datos filtrados | 6 | 16 | Aprobado |
| CU-20.2 | Restringir por ámbito de permisos | 1 | 16 | Aprobado |
| CU-23 | Trabajo colaborativo en línea | 0 | 0 | Cubierto por sus subcasos |
| CU-23.1 | Controlar conflicto de concurrencia | 5 | 18 | Aprobado |
| CU-25 | Modificar parámetros | 9 | 26 | Aprobado |
| CU-26 | Administración de delegaciones, usuarios y roles | 42 | 40 | Aprobado |
| CU-26.1 | Denegar acceso por ámbito | 34 | 25 | Aprobado |
| CU-27 | Administración de catálogos | 4 | 26 | Aprobado |
| CU-27.1 | Restringir elemento duplicado | 2 | 26 | Aprobado |
| CU-28 | Administración de períodos | 12 | 26 | Aprobado |
| CU-28.1 | Restricción por período cerrado | 9 | 15 | Aprobado |
| CU-29 | Búsqueda y filtros | 3 | 15 | Aprobado |
| CU-29.1 | Restricción de búsqueda por ámbito | 5 | 6 | Aprobado |
| CU-30 | Auditoría de cambios | 8 | 16 | Aprobado |
| CU-30.1 | Bloqueo por alteración no autorizada | 3 | 9 | Aprobado |

Casos de uso sin ninguna prueba: ninguno.

## 4. Cobertura por requisito funcional

En las pruebas de integración el CU y los RF se declaran por clase, así que cada prueba de la clase cuenta para todos los que la clase cita.

| RF | Requisito | Unitarias | Integración (por clase) | Situación | Observación |
|---|---|---|---|---|---|
| RF-001 | Administrar delegaciones | 11 | 32 | Aprobado |  |
| RF-002 | Administrar usuarios y roles | 71 | 46 | Aprobado |  |
| RF-003 | Configurar cargos y funciones | 3 | 26 | Aprobado |  |
| RF-004 | Mantener catálogo de actividades y servicios | 8 | 26 | Aprobado |  |
| RF-005 | Configurar períodos de medición | 9 | 41 | Aprobado |  |
| RF-006 | Configurar ponderaciones | 8 | 41 | Aprobado |  |
| RF-007 | Configurar metas y umbrales | 6 | 41 | Aprobado |  |
| RF-008 | Presentar ficha personal | 3 | 12 | Aprobado |  |
| RF-009 | Registrar actividades | 6 | 31 | Aprobado |  |
| RF-010 | Validar campos de actividad | 10 | 19 | Aprobado |  |
| RF-011 | Generar código verificador de evidencia | 3 | 31 | Aprobado |  |
| RF-012 | Asociar evidencia | 13 | 9 | Aprobado |  |
| RF-013 | Validar evidencia | 21 | 21 | Aprobado |  |
| RF-014 | Controlar puntuación por validación | 7 | 20 | Aprobado |  |
| RF-015 | Registrar atención social por etapas | 0 | 0 | Sin prueba | No implementado: no existe el registro de atenciones sociales por etapas. |
| RF-016 | Crear compromisos en agenda colectiva | 10 | 6 | Aprobado |  |
| RF-017 | Asignar compromiso | 12 | 6 | Aprobado |  |
| RF-018 | Gestionar estados | 14 | 18 | Aprobado |  |
| RF-019 | Controlar plazos | 10 | 12 | Aprobado |  |
| RF-020 | Relacionar agenda y medición | 0 | 0 | Sin prueba | No implementado: cerrar un compromiso no alimenta el indicador del ítem; solo cuentan las actividades aprobadas. |
| RF-021 | Generar resumen colectivo | 8 | 4 | Aprobado |  |
| RF-022 | Calcular avance actual | 13 | 23 | Aprobado |  |
| RF-023 | Calcular porcentaje de cumplimiento | 3 | 23 | Aprobado |  |
| RF-024 | Calcular cumplimiento ponderado | 6 | 15 | Aprobado |  |
| RF-025 | Aplicar incentivos y penalizaciones | 0 | 0 | Sin prueba | No implementado: el campo ajuste del indicador se guarda pero no entra al cálculo. |
| RF-026 | Calcular meta esperada al día | 5 | 25 | Aprobado |  |
| RF-027 | Mostrar semáforo de avance | 3 | 25 | Aprobado |  |
| RF-028 | Mostrar tablero personal | 9 | 22 | Aprobado |  |
| RF-029 | Mostrar tablero de delegación | 21 | 10 | Aprobado |  |
| RF-030 | Medir actividad reciente | 10 | 3 | Aprobado |  |
| RF-031 | Mostrar vista global por cargos | 0 | 0 | Sin prueba | No implementado: no hay vista global por cargos. |
| RF-032 | Buscar y filtrar información | 21 | 15 | Aprobado |  |
| RF-033 | Generar y exportar informes | 8 | 18 | Aprobado |  |
| RF-034 | Permitir trabajo simultáneo | 5 | 18 | Aprobado |  |
| RF-035 | Facilitar coordinación | 0 | 0 | Sin prueba | No implementado: no hay observaciones o comentarios asociados a registros. |
| RF-036 | Mantener trazabilidad | 14 | 16 | Aprobado |  |
| RF-037 | Emitir alertas | 31 | 0 | Aprobado |  |
| RF-038 | Versionar parámetros | 14 | 0 | Aprobado |  |

Requisitos sin ninguna prueba: RF-015, RF-020, RF-025, RF-031, RF-035

## 5. Tabla de casos de prueba

Una fila por prueba. La columna CU lista los casos de uso que verifica y RF los requisitos (RNF y RN cuando aplican). En las pruebas de integración, CU y RF son los de su clase.

| CP | CU | RF | Método de prueba | Prueba | Unidad probada | Responsable | Resultado |
|---|---|---|---|---|---|---|---|
| CP-ACT-025 | CU-01 | RF-009 | Unitaria | El registro válido queda pendiente de revisión con su código. | ActividadUnitTests.test_registrar_actividad_guarda_con_codigo_y_estado_pendiente | Dante Fredes | Aprobado |
| CP-ACT-027 | CU-01 | RF-009 | Unitaria | Sin delegación indicada se usa la del autor. | ActividadUnitTests.test_registrar_actividad_usa_la_delegacion_del_funcionario_si_falta | Dante Fredes | Aprobado |
| CP-DEL-031 | CU-01 | RF-009 | Unitaria | El autor ve «Modificar actividad» en el detalle; otro funcionario no. | ModificarEnSuPaginaTests.test_el_detalle_ofrece_modificar_actividad_a_su_autor | Dante Fredes | Aprobado |
| CP-INT-007 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_actividad_aprobada_no_admite_nuevas_evidencias | Dante Fredes | Aprobado |
| CP-INT-008 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_actividad_aprobada_no_se_edita_ni_se_elimina | Dante Fredes | Aprobado |
| CP-INT-009 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_actividad_de_un_periodo_cerrado_no_se_modifica | Dante Fredes | Aprobado |
| CP-INT-010 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_autor_edita_su_actividad_y_audita | Dante Fredes | Aprobado |
| CP-INT-011 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_coordinador_puede_modificar_actividad_ajena | Dante Fredes | Aprobado |
| CP-INT-012 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_edicion_concurrente_se_rechaza_con_la_version_desactualizada | Dante Fredes | Aprobado |
| CP-INT-013 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_editar_actividad_rechazada_la_devuelve_a_revision_con_sus_evidencias | Dante Fredes | Aprobado |
| CP-INT-014 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_el_formulario_ofrece_solo_los_items_del_cargo_del_funcionario | Dante Fredes | Aprobado |
| CP-INT-015 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_eliminar_requiere_confirmacion_post_y_borra_sus_evidencias | Dante Fredes | Aprobado |
| CP-INT-016 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_evidencia_rechaza_extension_no_permitida | Dante Fredes | Aprobado |
| CP-INT-017 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_funcionario_de_la_misma_delegacion_que_no_es_autor_no_puede_modificar | Dante Fredes | Aprobado |
| CP-INT-018 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_funcionario_de_otra_delegacion_no_puede_editar_ni_eliminar | Dante Fredes | Aprobado |
| CP-INT-019 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_funcionario_ve_solo_su_delegacion | Dante Fredes | Aprobado |
| CP-INT-020 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_listado_enlaza_modificar_y_eliminar_reales | Dante Fredes | Aprobado |
| CP-INT-021 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_rechaza_una_fecha_fuera_del_periodo_del_item | Dante Fredes | Aprobado |
| CP-INT-022 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_registrar_actividad_genera_codigo_y_auditoria | Dante Fredes | Aprobado |
| CP-INT-023 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_subir_evidencia_la_envia_a_revision_y_audita | Dante Fredes | Aprobado |
| CP-INT-024 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_usuario_sin_funcionario_no_puede_registrar | Dante Fredes | Aprobado |
| CP-INT-025 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_verificador_sin_delegacion_ve_todas_las_actividades | Dante Fredes | Aprobado |
| CP-INT-154 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_actividad_aprobada_no_cambia_de_estado | Dante Fredes | Aprobado |
| CP-INT-155 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_compromiso_cambios_quedan_en_el_historial | Dante Fredes | Aprobado |
| CP-INT-156 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_compromiso_version_optimista | Dante Fredes | Aprobado |
| CP-INT-157 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_el_rechazo_exige_texto_y_numera_revisiones | Dante Fredes | Aprobado |
| CP-INT-158 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_indicador_generar_calcula_y_guarda | Dante Fredes | Aprobado |
| CP-INT-159 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_registrar_actividad_fuera_del_periodo_o_con_periodo_cerrado | Dante Fredes | Aprobado |
| CP-INT-160 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_registrar_actividad_genera_codigo_y_toma_la_delegacion_del_autor | Dante Fredes | Aprobado |
| CP-INT-161 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_rn009_solo_la_validacion_aprobada_aporta_al_avance | Dante Fredes | Aprobado |
| CP-INT-162 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_rn010_codigo_verificador_inmutable | Dante Fredes | Aprobado |
| CP-INT-163 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_subir_evidencia_genera_codigos_y_envia_a_revision | Dante Fredes | Aprobado |
| CP-INT-164 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_subir_evidencia_rechaza_extension_no_permitida | Dante Fredes | Aprobado |
| CP-INT-165 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_version_optimista_rechaza_la_edicion_concurrente | Dante Fredes | Aprobado |
| CP-ACT-010 | CU-01.1 | RF-009 | Unitaria | Los ítems de otro cargo o de períodos cerrados no aparecen. | ActividadFormUnitTests.test_solo_se_ofrecen_items_de_periodos_abiertos_y_del_cargo_del_usuario | Dante Fredes | Aprobado |
| CP-ACT-012 | CU-01.1 | RF-010 | Unitaria | Con todos los datos obligatorios no hay errores. | ActividadFormUnitTests.test_un_formulario_completo_es_valido | Dante Fredes | Aprobado |
| CP-ACT-019 | CU-01.1 | RF-010 | Unitaria | Dígitos, espacios, guiones y paréntesis; + o paréntesis inicial opcional. | ActividadUnitTests.test_el_telefono_de_contacto_debe_tener_un_formato_valido | Dante Fredes | Aprobado |
| CP-ACT-020 | CU-01.1 | RF-010 | Unitaria | Sin teléfono el registro es válido. | ActividadUnitTests.test_el_telefono_es_opcional | Dante Fredes | Aprobado |
| CP-ACT-021 | CU-01.1 | RF-010 | Unitaria | Una fecha fuera del período se rechaza. | ActividadUnitTests.test_la_fecha_debe_estar_dentro_del_periodo_del_item | Dante Fredes | Aprobado |
| CP-ACT-023 | CU-01.1 | RF-010 | Unitaria | El primer y el último día del período se aceptan. | ActividadUnitTests.test_los_limites_del_periodo_son_validos | Dante Fredes | Aprobado |
| CP-ACT-024 | CU-01.1 | RF-038 | Unitaria | RN-013: el ítem de un período cerrado no admite actividades. | ActividadUnitTests.test_no_se_registra_en_un_periodo_cerrado | Dante Fredes | Aprobado |
| CP-ACT-007 | CU-01.2 | RF-010 | Unitaria | Vacío cada obligatorio, el error apunta a ese campo. | ActividadFormUnitTests.test_cada_campo_obligatorio_se_informa | Dante Fredes | Aprobado |
| CP-ACT-008 | CU-01.2 | RF-010 | Unitaria | Una fecha mal escrita no se guarda. | ActividadFormUnitTests.test_el_formato_de_fecha_invalido_se_informa | Dante Fredes | Aprobado |
| CP-ACT-013 | CU-01.2 | RF-010 | Unitaria | El error del teléfono aparece en su campo. | ActividadFormUnitTests.test_un_telefono_invalido_se_informa_en_el_formulario | Dante Fredes | Aprobado |
| CP-ACT-022 | CU-01.2 | RF-010 | Unitaria | El error nombra cada campo faltante. | ActividadUnitTests.test_los_campos_obligatorios_se_informan_por_nombre | Dante Fredes | Aprobado |
| CP-ACT-026 | CU-01.2 | RF-010 | Unitaria | Un registro con errores no se guarda. | ActividadUnitTests.test_registrar_actividad_invalida_no_guarda_nada | Dante Fredes | Aprobado |
| CP-COM-003 | CU-02 | RF-017 | Unitaria | Quien ve todo elige entre los funcionarios activos. | CompromisoFormUnitTests.test_coordinacion_asigna_a_cualquier_funcionario_activo | Faride Luna | Aprobado |
| CP-COM-051 | CU-02 | RF-016 | Unitaria | Administración, coordinación, delegados y funcionarios ven | TuboDeTrabajoUnitTests.test_solo_quien_puede_crear_ve_el_boton_agregar | Faride Luna | Aprobado |
| CP-INT-055 | CU-02, CU-12, CU-13, CU-13.1, CU-23.1 | RF-016, RF-017, RF-018, RF-034 | Integración | Agenda de compromisos con responsable, historial y control de versión. | CompromisoVistasTests.test_cambio_de_estado_queda_en_el_historial_y_en_la_auditoria | Faride Luna | Aprobado |
| CP-INT-056 | CU-02, CU-12, CU-13, CU-13.1, CU-23.1 | RF-016, RF-017, RF-018, RF-034 | Integración | Agenda de compromisos con responsable, historial y control de versión. | CompromisoVistasTests.test_crear_compromiso_deja_historial_y_auditoria | Faride Luna | Aprobado |
| CP-INT-057 | CU-02, CU-12, CU-13, CU-13.1, CU-23.1 | RF-016, RF-017, RF-018, RF-034 | Integración | Agenda de compromisos con responsable, historial y control de versión. | CompromisoVistasTests.test_el_formulario_de_edicion_no_cambia_el_estado_y_rechaza_versiones_viejas | Faride Luna | Aprobado |
| CP-INT-058 | CU-02, CU-12, CU-13, CU-13.1, CU-23.1 | RF-016, RF-017, RF-018, RF-034 | Integración | Agenda de compromisos con responsable, historial y control de versión. | CompromisoVistasTests.test_solo_el_responsable_o_la_coordinacion_modifican_un_compromiso | Faride Luna | Aprobado |
| CP-INT-059 | CU-02, CU-12, CU-13, CU-13.1, CU-23.1 | RF-016, RF-017, RF-018, RF-034 | Integración | Agenda de compromisos con responsable, historial y control de versión. | CompromisoVistasTests.test_solo_la_coordinacion_elimina_compromisos | Faride Luna | Aprobado |
| CP-INT-060 | CU-02, CU-12, CU-13, CU-13.1, CU-23.1 | RF-016, RF-017, RF-018, RF-034 | Integración | Agenda de compromisos con responsable, historial y control de versión. | CompromisoVistasTests.test_un_funcionario_siempre_queda_como_responsable_de_lo_que_crea | Faride Luna | Aprobado |
| CP-COM-005 | CU-02.1 | RF-016 | Unitaria | Un eje inventado se rechaza. | CompromisoFormUnitTests.test_el_eje_debe_ser_uno_de_los_definidos | Faride Luna | Aprobado |
| CP-COM-010 | CU-02.1 | RF-017 | Unitaria | Con todos los datos críticos no hay errores. | CompromisoFormUnitTests.test_un_compromiso_completo_es_valido | Faride Luna | Aprobado |
| CP-COM-011 | CU-02.1 | RF-017 | Unitaria | Una fecha mal escrita no pasa. | CompromisoFormUnitTests.test_una_fecha_con_formato_invalido_se_rechaza | Faride Luna | Aprobado |
| CP-DEL-010 | CU-02.1 | RF-016, RF-017 | Unitaria | El responsable debe ser de la delegación elegida. | CoordinacionDeDelegadosTests.test_el_coordinador_asigna_compromisos_a_delegados_de_la_delegacion | Faride Luna | Aprobado |
| CP-COM-002 | CU-02.2 | RF-017 | Unitaria | Solicitante, territorio y descripción también. | CompromisoFormUnitTests.test_cada_campo_obligatorio_se_informa_por_nombre | Faride Luna | Aprobado |
| CP-COM-008 | CU-02.2 | RF-017 | Unitaria | La fecha comprometida es obligatoria. | CompromisoFormUnitTests.test_sin_fecha_comprometida_no_se_guarda | Faride Luna | Aprobado |
| CP-COM-009 | CU-02.2 | RF-017 | Unitaria | El responsable es obligatorio. | CompromisoFormUnitTests.test_sin_responsable_no_se_guarda | Faride Luna | Aprobado |
| CP-COM-037 | CU-02.3 | RF-019 | Unitaria | Pasó la fecha y no está realizado. | PlazoUnitTests.test_vencido_es_fecha_pasada_sin_realizar | Faride Luna | Aprobado |
| CP-INT-099 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_acceso_segun_el_rol | Por definir | Aprobado |
| CP-INT-100 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_administrador_no_puede_desactivarse_ni_quitarse_el_rol | Por definir | Aprobado |
| CP-INT-101 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_busqueda_filtra_la_lista | Por definir | Aprobado |
| CP-INT-102 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_cargo_se_desactiva_en_vez_de_eliminarse | Por definir | Aprobado |
| CP-INT-103 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_catalogo_rechaza_codigo_duplicado | Por definir | Aprobado |
| CP-INT-104 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_catalogo_sin_uso_se_elimina_y_uno_inactivo_se_activa | Por definir | Aprobado |
| CP-INT-105 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_crear_y_editar_delegacion_deja_auditoria_con_valores | Por definir | Aprobado |
| CP-INT-106 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_desactivar_funcionario_tambien_desactiva_su_cuenta | Por definir | Aprobado |
| CP-INT-107 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_eliminar_meta_avisa_que_borra_sus_indicadores | Por definir | Aprobado |
| CP-INT-108 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_funcionario_rechaza_usuario_repetido_y_contrasena_distinta | Por definir | Aprobado |
| CP-INT-109 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_funcionario_se_crea_con_cuenta_roles_y_auditoria_sin_contrasena | Por definir | Aprobado |
| CP-INT-110 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_indice_deshabilita_los_mantenedores_exclusivos_del_administrador | Por definir | Aprobado |
| CP-INT-111 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_item_con_metas_no_se_elimina | Por definir | Aprobado |
| CP-INT-112 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_item_rechaza_ponderaciones_que_superan_100 | Por definir | Aprobado |
| CP-INT-113 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_las_ocho_listas_tienen_agregar_y_buscar | Por definir | Aprobado |
| CP-INT-114 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_los_avisos_se_muestran_en_pantalla | Por definir | Aprobado |
| CP-INT-115 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_los_formularios_de_alta_y_edicion_se_muestran | Por definir | Aprobado |
| CP-INT-116 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_mantenedor_inexistente_es_404 | Por definir | Aprobado |
| CP-INT-117 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_meta_rechaza_objetivo_cero_y_al_guardar_genera_su_indicador | Por definir | Aprobado |
| CP-INT-118 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_periodo_cerrado_no_se_edita_ni_se_elimina | Por definir | Aprobado |
| CP-INT-119 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_periodo_rechaza_termino_anterior_al_inicio | Por definir | Aprobado |
| CP-INT-120 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_periodo_se_crea_en_borrador_y_calcula_sus_dias | Por definir | Aprobado |
| CP-INT-121 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_periodo_se_inicia_se_cierra_y_se_reabre_con_motivo | Por definir | Aprobado |
| CP-INT-122 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_rol_en_uso_no_se_elimina_y_explica_el_motivo | Por definir | Aprobado |
| CP-INT-123 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_rol_nuevo_sin_uso_se_elimina_con_auditoria | Por definir | Aprobado |
| CP-INT-124 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_roles_del_sistema_no_se_renombran_ni_se_eliminan | Por definir | Aprobado |
| CP-ORG-004 | CU-04 | RF-003 | Unitaria | Un cargo retirado no está vigente. | CargoUnitTests.test_verificar_vigencia_refleja_el_estado_del_cargo | Por definir | Aprobado |
| CP-ORG-002 | CU-04.1 | RF-006 | Unitaria | Una ponderación que respeta el 100 % se guarda. | CargoUnitTests.test_actualizar_ponderaciones_guarda_un_valor_valido | Por definir | Aprobado |
| CP-ORG-003 | CU-04.1 | RF-006 | Unitaria | El ítem debe pertenecer al cargo. | CargoUnitTests.test_actualizar_ponderaciones_rechaza_un_item_de_otro_cargo | Por definir | Aprobado |
| CP-ORG-028 | CU-04.1 | RF-006 | Unitaria | Cambiar 60 % a 70 % con otro de 30 % es válido. | ItemMedibleUnitTests.test_al_editar_un_item_no_se_cuenta_a_si_mismo | Por definir | Aprobado |
| CP-ORG-031 | CU-04.1 | RF-006 | Unitaria | RN-001: 60 % más 40 % suman 100 %. | ItemMedibleUnitTests.test_la_suma_exacta_de_100_es_valida | Por definir | Aprobado |
| CP-ORG-001 | CU-04.2 | RF-006 | Unitaria | Más de 100 % no se guarda. | CargoUnitTests.test_actualizar_ponderaciones_bloquea_una_suma_superior_a_100 | Por definir | Aprobado |
| CP-ORG-030 | CU-04.2 | RF-006 | Unitaria | Un porcentaje negativo es inválido. | ItemMedibleUnitTests.test_la_ponderacion_no_puede_ser_negativa | Por definir | Aprobado |
| CP-ORG-032 | CU-04.2 | RF-006 | Unitaria | RN-001: 60 % más 50 % no se guarda. | ItemMedibleUnitTests.test_una_suma_superior_a_100_se_bloquea | Por definir | Aprobado |
| CP-INT-125 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_catalogo_codigo_unico_y_activacion | Faride Luna | Aprobado |
| CP-INT-126 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_cumplimiento_global_de_la_delegacion | Faride Luna | Aprobado |
| CP-INT-127 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_dias_computables_se_calculan_al_guardar | Faride Luna | Aprobado |
| CP-INT-128 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_periodo_rechaza_termino_anterior | Faride Luna | Aprobado |
| CP-INT-129 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn001_iniciar_periodo_exige_100_por_cargo | Faride Luna | Aprobado |
| CP-INT-130 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn001_ponderaciones_del_cargo_no_superan_100 | Faride Luna | Aprobado |
| CP-INT-131 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn002_valor_objetivo_mayor_que_cero | Faride Luna | Aprobado |
| CP-INT-132 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn004_evaluar_progreso_y_actualizar_objetivo | Faride Luna | Aprobado |
| CP-INT-133 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn005_tope_configurable_por_parametro | Faride Luna | Aprobado |
| CP-INT-134 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn005_tope_por_defecto_150_y_ponderado | Faride Luna | Aprobado |
| CP-INT-135 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn006_umbral_minimo_por_defecto_80 | Faride Luna | Aprobado |
| CP-INT-136 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn007_porcentaje_esperado_y_dias_restantes | Faride Luna | Aprobado |
| CP-INT-137 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn008_semaforo | Faride Luna | Aprobado |
| CP-INT-138 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn013_periodo_cerrado_no_se_modifica | Faride Luna | Aprobado |
| CP-INT-139 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn013_reapertura_exige_motivo_y_queda_auditada | Faride Luna | Aprobado |
| CP-TRA-001 | CU-05 | RF-007 | Unitaria | La advertencia cuenta los indicadores calculados. | AdvertenciaMetaUnitTests.test_eliminar_una_meta_advierte_cuantos_indicadores_se_pierden | Faride Luna | Aprobado |
| CP-ORG-037 | CU-05.1 | RF-007 | Unitaria | El mínimo aceptado es 0,01. | MetaUnitTests.test_un_valor_objetivo_positivo_es_valido | Faride Luna | Aprobado |
| CP-ORG-033 | CU-05.2 | RF-007 | Unitaria | Un valor inválido no llega a la base. | MetaUnitTests.test_actualizar_valor_objetivo_valida_antes_de_guardar | Faride Luna | Aprobado |
| CP-ORG-034 | CU-05.2 | RF-007 | Unitaria | RN-002: cero y negativos se rechazan. | MetaUnitTests.test_el_valor_objetivo_debe_ser_mayor_que_cero | Faride Luna | Aprobado |
| CP-ORG-036 | CU-05.3 | RF-038 | Unitaria | RN-013: los períodos cerrados no se modifican. | MetaUnitTests.test_no_se_crea_una_meta_en_un_periodo_cerrado | Faride Luna | Aprobado |
| CP-ALE-007 | CU-06 | RF-037, RNF-015 | Unitaria | Con 2 días, tres sin ingreso ya alertan. | AlertasDeAusenciaTests.test_el_limite_es_configurable | Por definir | Aprobado |
| CP-ALE-008 | CU-06 | RF-037 | Unitaria | Con 7 días justos aún no; con 8 sí. | AlertasDeAusenciaTests.test_el_limite_exacto_no_alerta | Por definir | Aprobado |
| CP-ALE-009 | CU-06 | RF-037 | Unitaria | Sin ninguna actividad. | AlertasDeAusenciaTests.test_quien_nunca_registro_alerta | Por definir | Aprobado |
| CP-ALE-010 | CU-06 | RF-037 | Unitaria | Un período cerrado no genera alertas de ausencia. | AlertasDeAusenciaTests.test_sin_metas_en_un_periodo_abierto_no_se_vigila | Por definir | Aprobado |
| CP-ALE-011 | CU-06 | RF-037 | Unitaria | Pasados 7 días sin ingreso. | AlertasDeAusenciaTests.test_un_registro_antiguo_alerta_con_los_dias_transcurridos | Por definir | Aprobado |
| CP-ALE-012 | CU-06 | RF-037 | Unitaria | Dentro del plazo no hay aviso. | AlertasDeAusenciaTests.test_un_registro_reciente_no_alerta | Por definir | Aprobado |
| CP-INT-072 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_dashboard_y_resumen_muestran_la_diferencia_y_la_desviacion | Por definir | Aprobado |
| CP-INT-073 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_el_detalle_explica_la_formula_y_enlaza_las_actividades_que_aportan | Por definir | Aprobado |
| CP-INT-074 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_el_detalle_informa_cuando_se_aplica_el_tope | Por definir | Aprobado |
| CP-INT-075 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_el_selector_ignora_un_periodo_ajeno_o_invalido | Por definir | Aprobado |
| CP-INT-076 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_exige_iniciar_sesion | Por definir | Aprobado |
| CP-INT-077 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_la_ficha_calcula_la_diferencia_con_lo_esperado | Por definir | Aprobado |
| CP-INT-078 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_la_ficha_solo_muestra_las_metas_del_funcionario | Por definir | Aprobado |
| CP-INT-079 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_la_meta_alcanzada_se_destaca_como_cumplida | Por definir | Aprobado |
| CP-INT-080 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_resumen_de_evidencias_y_compromisos | Por definir | Aprobado |
| CP-INT-081 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_sin_metas_la_ficha_lo_indica | Por definir | Aprobado |
| CP-INT-082 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_un_usuario_sin_funcionario_es_redirigido_con_un_mensaje | Por definir | Aprobado |
| CP-INT-083 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_una_meta_sin_calculo_se_informa_sin_formula | Por definir | Aprobado |
| CP-INT-185 | CU-06 | RF-030 | Integración | Último ingreso, días sin ingreso, registros y promedio diario. | ResumenYActividadRecienteVistasTests.test_la_ficha_muestra_la_actividad_reciente_propia | Por definir | Aprobado |
| CP-INT-186 | CU-06 | RF-030 | Integración | Sin registros no hay cifras inventadas. | ResumenYActividadRecienteVistasTests.test_la_ficha_sin_actividades_lo_dice | Por definir | Aprobado |
| CP-MED-001 | CU-06 | RF-030 | Unitaria | Una fila por funcionario con su cantidad. | ActividadRecienteUnitTests.test_cuenta_los_registros_de_cada_funcionario | Por definir | Aprobado |
| CP-MED-002 | CU-06 | RF-030 | Unitaria | 5 registros en 10 días son 0,50 por día. | ActividadRecienteUnitTests.test_el_promedio_diario_usa_los_dias_transcurridos_del_periodo | Por definir | Aprobado |
| CP-MED-003 | CU-06 | RF-030 | Unitaria | Antes de empezar se cuenta al menos un día. | ActividadRecienteUnitTests.test_el_promedio_no_divide_por_cero_antes_del_inicio_del_periodo | Por definir | Aprobado |
| CP-MED-004 | CU-06 | RF-030 | Unitaria | El último ingreso es la fecha de registro, no la de la actividad. | ActividadRecienteUnitTests.test_informa_la_fecha_del_ultimo_ingreso_y_los_dias_sin_ingreso | Por definir | Aprobado |
| CP-MED-006 | CU-06 | RF-030 | Unitaria | Quien no tiene delegación figura con alcance global. | ActividadRecienteUnitTests.test_nombra_la_delegacion_o_el_alcance_global | Por definir | Aprobado |
| CP-MED-007 | CU-06 | RF-030 | Unitaria | Un funcionario sin registros no aparece. | ActividadRecienteUnitTests.test_sin_actividades_no_hay_filas | Por definir | Aprobado |
| CP-MED-008 | CU-06 | RF-030 | Unitaria | El promedio necesita un período de referencia. | ActividadRecienteUnitTests.test_sin_periodo_no_hay_promedio | Por definir | Aprobado |
| CP-MED-009 | CU-06 | RF-030 | Unitaria | Un ítem de otro período no suma. | ActividadRecienteUnitTests.test_solo_cuentan_las_actividades_del_periodo | Por definir | Aprobado |
| CP-MED-027 | CU-06 | RF-028 | Unitaria | 1 de 4 con esperado de 50 % es 25 %, 25 puntos bajo lo esperado. | FichaPersonalUnitTests.test_la_fila_trae_avance_cumplimiento_y_diferencia | Por definir | Aprobado |
| CP-MED-030 | CU-06 | RF-008 | Unitaria | El selector de períodos de la ficha. | FichaPersonalUnitTests.test_periodos_de_lista_solo_donde_hay_metas | Por definir | Aprobado |
| CP-MED-032 | CU-06 | RF-028 | Unitaria | Cuántas evidencias hay en cada estado de revisión. | FichaPersonalUnitTests.test_resumen_de_evidencias_por_estado | Por definir | Aprobado |
| CP-MED-033 | CU-06 | RF-008 | Unitaria | La ficha es personal. | FichaPersonalUnitTests.test_solo_aparecen_las_metas_del_funcionario | Por definir | Aprobado |
| CP-MED-034 | CU-06 | RF-008 | Unitaria | Antes del primer cálculo no hay formula ni diferencia. | FichaPersonalUnitTests.test_una_meta_sin_calculo_se_marca_como_tal | Por definir | Aprobado |
| CP-ACT-046 | CU-06.1 | RF-022 | Unitaria | Aprobar una actividad deja un indicador nuevo. | ValidacionUnitTests.test_una_aprobacion_recalcula_los_indicadores_de_la_meta | Por definir | Aprobado |
| CP-MED-022 | CU-06.1 | RF-022 | Unitaria | Cada generación deja un registro. | CumplimientoUnitTests.test_generar_calcula_y_guarda_un_indicador_nuevo | Por definir | Aprobado |
| CP-MED-028 | CU-06.2 | RF-028 | Unitaria | Con el avance igual al objetivo queda cumplida. | FichaPersonalUnitTests.test_la_meta_alcanzada_se_destaca_como_cumplida | Por definir | Aprobado |
| CP-MED-010 | CU-07.1 | RF-022 | Unitaria | RN-003: solo aprobadas con validación aprobada. | AvanceUnitTests.test_cuenta_las_actividades_aprobadas_del_item_en_el_periodo | Por definir | Aprobado |
| CP-MED-012 | CU-07.1 | RF-022 | Unitaria | RN-003: se mide dentro del período. | AvanceUnitTests.test_no_cuentan_las_actividades_fuera_de_las_fechas_del_periodo | Por definir | Aprobado |
| CP-MED-014 | CU-07.1 | RF-022, RF-029 | Unitaria | Una meta de Centro no suma lo de Rural. | AvanceUnitTests.test_solo_cuentan_las_actividades_de_la_delegacion_de_la_meta | Por definir | Aprobado |
| CP-MED-015 | CU-07.1 | RF-022 | Unitaria | Un ítem distinto no aporta. | AvanceUnitTests.test_solo_cuentan_las_actividades_del_item_de_la_meta | Por definir | Aprobado |
| CP-MED-016 | CU-07.1 | RF-022 | Unitaria | RN-003: se cuentan actividades, no evidencias. | AvanceUnitTests.test_una_actividad_con_dos_evidencias_aprobadas_cuenta_una_vez | Por definir | Aprobado |
| CP-MED-017 | CU-07.1 | RF-022 | Unitaria | El alcance global cuenta cualquier delegación. | AvanceUnitTests.test_una_meta_sin_delegacion_suma_todas_las_delegaciones | Por definir | Aprobado |
| CP-MED-018 | CU-07.1 | RF-023 | Unitaria | RN-004: 1 de 4 es 25 %. | CumplimientoUnitTests.test_cumplimiento_es_avance_sobre_meta | Por definir | Aprobado |
| CP-MED-019 | CU-07.1 | RF-024 | Unitaria | RN-005: ponderador 40 % de un 50 % da 20. | CumplimientoUnitTests.test_el_cumplimiento_ponderado_usa_el_ponderador_de_la_meta | Por definir | Aprobado |
| CP-MED-020 | CU-07.1 | RF-024 | Unitaria | RN-005: no pasa del máximo computable. | CumplimientoUnitTests.test_el_cumplimiento_se_topa_en_150_por_defecto | Por definir | Aprobado |
| CP-ORG-035 | CU-07.1 | RF-023 | Unitaria | RN-004: 1 de 4 es 25 %, 1 de 3 es 33,33 %. | MetaUnitTests.test_evaluar_progreso_es_avance_sobre_meta_por_100 | Por definir | Aprobado |
| CP-ACT-001 | CU-07.2 | RF-022 | Unitaria | La anulación explícita sí cambia el estado. | ActividadEstadoUnitTests.test_anulando_si_se_puede_salir_de_aprobada | Por definir | Aprobado |
| CP-ACT-038 | CU-07.2 | RF-022 | Unitaria | Con motivo, la actividad deja de sumar. | ValidacionUnitTests.test_anular_una_aprobacion_deja_sin_efecto_el_aporte | Por definir | Aprobado |
| CP-INT-026 | CU-07.2 | RF-022, RF-023, RN-009, RN-013 | Integración | Anular una aprobación exige motivo, recalcula hacia abajo y conserva el historial. | AnularAprobacionTests.test_anular_quita_la_actividad_del_avance_y_recalcula | Por definir | Aprobado |
| CP-INT-027 | CU-07.2 | RF-022, RF-023, RN-009, RN-013 | Integración | Anular una aprobación exige motivo, recalcula hacia abajo y conserva el historial. | AnularAprobacionTests.test_exige_un_motivo_y_una_actividad_aprobada | Por definir | Aprobado |
| CP-INT-028 | CU-07.2 | RF-022, RF-023, RN-009, RN-013 | Integración | Anular una aprobación exige motivo, recalcula hacia abajo y conserva el historial. | AnularAprobacionTests.test_get_no_anula_y_el_panel_solo_se_ofrece_a_quien_corresponde | Por definir | Aprobado |
| CP-INT-029 | CU-07.2 | RF-022, RF-023, RN-009, RN-013 | Integración | Anular una aprobación exige motivo, recalcula hacia abajo y conserva el historial. | AnularAprobacionTests.test_la_validacion_original_se_conserva_como_historial | Por definir | Aprobado |
| CP-INT-030 | CU-07.2 | RF-022, RF-023, RN-009, RN-013 | Integración | Anular una aprobación exige motivo, recalcula hacia abajo y conserva el historial. | AnularAprobacionTests.test_la_vista_anula_audita_y_muestra_el_resultado | Por definir | Aprobado |
| CP-INT-031 | CU-07.2 | RF-022, RF-023, RN-009, RN-013 | Integración | Anular una aprobación exige motivo, recalcula hacia abajo y conserva el historial. | AnularAprobacionTests.test_la_vista_rechaza_un_motivo_vacio_sin_cambios | Por definir | Aprobado |
| CP-INT-032 | CU-07.2 | RF-022, RF-023, RN-009, RN-013 | Integración | Anular una aprobación exige motivo, recalcula hacia abajo y conserva el historial. | AnularAprobacionTests.test_un_funcionario_no_puede_anular_y_queda_registrado | Por definir | Aprobado |
| CP-INT-033 | CU-07.2 | RF-022, RF-023, RN-009, RN-013 | Integración | Anular una aprobación exige motivo, recalcula hacia abajo y conserva el historial. | AnularAprobacionTests.test_un_periodo_cerrado_no_permite_anular | Por definir | Aprobado |
| CP-MED-025 | CU-07.3 | RF-024 | Unitaria | Si el bruto supera el máximo, se explica. | FichaPersonalUnitTests.test_el_detalle_avisa_cuando_se_aplica_el_tope | Por definir | Aprobado |
| CP-MED-026 | CU-07.3 | RF-023 | Unitaria | El cálculo se puede verificar a mano. | FichaPersonalUnitTests.test_el_detalle_muestra_la_formula_y_la_ponderacion | Por definir | Aprobado |
| CP-MED-029 | CU-07.3 | RF-022 | Unitaria | Cada cifra enlaza a su origen. | FichaPersonalUnitTests.test_lista_las_actividades_que_aportan | Por definir | Aprobado |
| CP-ACT-028 | CU-09 | RF-012 | Unitaria | Código de la actividad más un correlativo. | EvidenciaUnitTests.test_el_codigo_de_evidencia_deriva_del_de_la_actividad | Dante Fredes | Aprobado |
| CP-ACT-029 | CU-09 | RF-012 | Unitaria | El código de la evidencia es inmutable. | EvidenciaUnitTests.test_el_codigo_de_evidencia_no_se_puede_modificar | Dante Fredes | Aprobado |
| CP-ACT-037 | CU-09 | RF-012 | Unitaria | La evidencia queda ligada a la actividad y pendiente. | EvidenciaUnitTests.test_subir_evidencia_vincula_el_archivo_y_envia_a_revision | Dante Fredes | Aprobado |
| CP-DEL-012 | CU-09 | RF-012 | Unitaria | La coordinación revisa, pero la evidencia la sube quien registró la actividad. | CoordinacionDeDelegadosTests.test_el_coordinador_no_sube_evidencias_en_nombre_de_otro | Dante Fredes | Aprobado |
| CP-DEL-021 | CU-09 | RF-012 | Unitaria | Botón propio en la lista y en el detalle. | EvidenciaEnListadoYDetalleTests.test_el_autor_ve_el_boton_subir_evidencia | Dante Fredes | Aprobado |
| CP-DEL-022 | CU-09 | RF-012 | Unitaria | El total sale de un annotate: más filas no suman consultas. | EvidenciaEnListadoYDetalleTests.test_el_indicador_no_hace_una_consulta_por_fila | Dante Fredes | Aprobado |
| CP-DEL-023 | CU-09 | RF-012 | Unitaria | Con y sin evidencia se distinguen en la lista. | EvidenciaEnListadoYDetalleTests.test_el_listado_indica_si_la_actividad_tiene_evidencia | Dante Fredes | Aprobado |
| CP-DEL-026 | CU-09 | RF-012 | Unitaria | En el detalle, «Subir evidencia» y «Modificar actividad» llevan a pantallas distintas. | EvidenciaEnListadoYDetalleTests.test_subir_evidencia_y_modificar_son_botones_distintos | Dante Fredes | Aprobado |
| CP-DEL-027 | CU-09 | RF-012, RF-013 | Unitaria | Aprobada no admite evidencias: el botón no aparece en la lista ni en el detalle. | EvidenciaEnListadoYDetalleTests.test_una_actividad_aprobada_no_ofrece_subir_evidencia | Dante Fredes | Aprobado |
| CP-INT-061 | CU-09 | RF-012 | Integración | Quien puede ver la actividad abre su archivo. | EvidenciaArchivoTests.test_el_autor_abre_el_archivo_en_el_navegador | Dante Fredes | Aprobado |
| CP-INT-062 | CU-09 | RF-012 | Integración | El detalle ofrece abrir y descargar cada archivo. | EvidenciaArchivoTests.test_el_detalle_de_la_actividad_enlaza_ver_y_descargar | Dante Fredes | Aprobado |
| CP-INT-064 | CU-09 | RNF-004 | Integración | Sin sesión no se entrega ningún archivo. | EvidenciaArchivoTests.test_sin_sesion_se_pide_iniciar_sesion | Dante Fredes | Aprobado |
| CP-INT-065 | CU-09 | RF-012 | Integración | Si el archivo ya no está, se informa sin error del sistema. | EvidenciaArchivoTests.test_un_archivo_que_falta_en_el_disco_responde_404 | Dante Fredes | Aprobado |
| CP-ACT-030 | CU-09.1 | RF-012 | Unitaria | Sin archivo no hay carga. | EvidenciaUnitTests.test_el_formulario_exige_un_archivo | Dante Fredes | Aprobado |
| CP-ACT-035 | CU-09.1 | RF-012 | Unitaria | JPG, JPEG, PNG y PDF se aceptan, sin importar mayúsculas. | EvidenciaUnitTests.test_formatos_permitidos | Dante Fredes | Aprobado |
| CP-ACT-031 | CU-09.2 | RF-012 | Unitaria | El motivo exacto del rechazo se informa. | EvidenciaUnitTests.test_el_formulario_rechaza_una_extension_no_permitida | Dante Fredes | Aprobado |
| CP-ACT-032 | CU-09.2 | RNF-017 | Unitaria | El motivo indica el peso y el máximo permitido. | EvidenciaUnitTests.test_el_limite_de_tamano_es_configurable | Dante Fredes | Aprobado |
| CP-ACT-034 | CU-09.2 | RF-012 | Unitaria | Ejecutables, documentos y archivos sin extensión no entran. | EvidenciaUnitTests.test_formatos_no_permitidos_se_rechazan | Dante Fredes | Aprobado |
| CP-INT-067 | CU-09.2 | RF-012, RNF-017 | Integración | Las evidencias que superan el tamaño máximo configurado se rechazan con su motivo. | EvidenciaTamanoTests.test_el_formulario_de_evidencia_informa_el_motivo_del_rechazo | Dante Fredes | Aprobado |
| CP-INT-068 | CU-09.2 | RF-012, RNF-017 | Integración | Las evidencias que superan el tamaño máximo configurado se rechazan con su motivo. | EvidenciaTamanoTests.test_el_maximo_por_defecto_es_de_5_megabytes | Dante Fredes | Aprobado |
| CP-INT-069 | CU-09.2 | RF-012, RNF-017 | Integración | Las evidencias que superan el tamaño máximo configurado se rechazan con su motivo. | EvidenciaTamanoTests.test_el_validador_acepta_hasta_el_maximo_y_rechaza_lo_que_lo_supera | Dante Fredes | Aprobado |
| CP-INT-070 | CU-09.2 | RF-012, RNF-017 | Integración | Las evidencias que superan el tamaño máximo configurado se rechazan con su motivo. | EvidenciaTamanoTests.test_subir_evidencia_rechaza_un_archivo_demasiado_pesado | Dante Fredes | Aprobado |
| CP-INT-071 | CU-09.2 | RF-012, RNF-017 | Integración | Las evidencias que superan el tamaño máximo configurado se rechazan con su motivo. | EvidenciaTamanoTests.test_un_archivo_guardado_que_falta_en_el_disco_no_se_mide | Dante Fredes | Aprobado |
| CP-ACT-016 | CU-10 | RF-011 | Unitaria | Los códigos generados son únicos. | ActividadUnitTests.test_dos_actividades_nunca_comparten_codigo | Dante Fredes | Aprobado |
| CP-ACT-017 | CU-10 | RF-011 | Unitaria | RN-010: el código es inmutable. | ActividadUnitTests.test_el_codigo_verificador_no_se_puede_modificar | Dante Fredes | Aprobado |
| CP-ACT-018 | CU-10 | RF-011 | Unitaria | RN-010: formato EVD-fecha-sufijo y no se regenera. | ActividadUnitTests.test_el_codigo_verificador_tiene_formato_y_se_asigna_una_vez | Dante Fredes | Aprobado |
| CP-ACT-014 | CU-10.1 | RF-032 | Unitaria | La búsqueda por código devuelve su actividad. | ActividadUnitTests.test_buscar_por_codigo_encuentra_la_actividad | Dante Fredes | Aprobado |
| CP-DEL-033 | CU-10.1 | RF-032 | Unitaria | Quien no puede modificar no ve Modificar ni Eliminar en la fila. | ModificarEnSuPaginaTests.test_la_lista_no_muestra_botones_desactivados | Dante Fredes | Aprobado |
| CP-ACT-015 | CU-10.2 | RF-032 | Unitaria | Un código sin registros da un resultado vacío. | ActividadUnitTests.test_buscar_un_codigo_inexistente_no_devuelve_nada | Dante Fredes | Aprobado |
| CP-ACT-003 | CU-11 | RF-013 | Unitaria | Solo existen los estados definidos. | ActividadEstadoUnitTests.test_cambiar_estado_rechaza_un_estado_inexistente | Dante Fredes | Aprobado |
| CP-ACT-036 | CU-11 | RF-013 | Unitaria | Un archivo nuevo debe revisarse de nuevo. | EvidenciaUnitTests.test_reemplazar_archivo_vuelve_a_revision | Dante Fredes | Aprobado |
| CP-ACT-039 | CU-11 | RF-013 | Unitaria | La aprobación se refleja en ambas. | ValidacionUnitTests.test_aprobar_marca_la_evidencia_y_la_actividad | Dante Fredes | Aprobado |
| CP-ACT-043 | CU-11 | RF-013 | Unitaria | Ya no existe «Solicitar corrección»: solo aprobar o rechazar. | ValidacionUnitTests.test_la_revision_solo_aprueba_o_rechaza | Dante Fredes | Aprobado |
| CP-ALE-018 | CU-11 | RF-037 | Unitaria | Solo quien puede revisar recibe este aviso. | AlertasDeEvidenciasTests.test_alerta_tambien_a_la_coordinacion_pero_no_al_autor | Dante Fredes | Aprobado |
| CP-ALE-019 | CU-11 | RF-037 | Unitaria | Con tres días o más, urgente. | AlertasDeEvidenciasTests.test_la_espera_larga_sube_el_nivel_a_urgente | Dante Fredes | Aprobado |
| CP-ALE-020 | CU-11 | RF-037 | Unitaria | Se alerta por actividad, no por archivo. | AlertasDeEvidenciasTests.test_una_actividad_con_dos_pendientes_alerta_una_vez | Dante Fredes | Aprobado |
| CP-ALE-021 | CU-11 | RF-037 | Unitaria | Con motivo, autor como responsable y enlace a la actividad. | AlertasDeEvidenciasTests.test_una_evidencia_pendiente_alerta_al_verificador | Dante Fredes | Aprobado |
| CP-ALE-022 | CU-11 | RF-037 | Unitaria | Al aprobarla, la alerta desaparece. | AlertasDeEvidenciasTests.test_una_evidencia_revisada_ya_no_alerta | Dante Fredes | Aprobado |
| CP-DEL-013 | CU-11 | RF-013 | Unitaria | La coordinación aprueba evidencias de cualquier delegación. | CoordinacionDeDelegadosTests.test_el_coordinador_revisa_en_todas_las_delegaciones | Dante Fredes | Aprobado |
| CP-DEL-024 | CU-11 | RF-013 | Unitaria | El aviso «no admite nuevas evidencias» es solo para el autor. | EvidenciaEnListadoYDetalleTests.test_el_revisor_no_ve_avisos_de_carga | Dante Fredes | Aprobado |
| CP-DEL-025 | CU-11 | RF-013 | Unitaria | El revisor ve la decisión, no el formulario de carga. | EvidenciaEnListadoYDetalleTests.test_quien_solo_revisa_no_ve_carga_de_archivos | Dante Fredes | Aprobado |
| CP-DEL-035 | CU-11 | RF-013 | Unitaria | Aprobada ya suma al avance: ni el detalle ni la lista ofrecen modificarla. | ModificarEnSuPaginaTests.test_una_actividad_aprobada_no_ofrece_modificar | Dante Fredes | Aprobado |
| CP-DEL-036 | CU-11 | RF-013 | Unitaria | Aprobar con o sin observación es válido. | RevisionFormTests.test_aprobar_no_exige_motivo | Dante Fredes | Aprobado |
| CP-DEL-040 | CU-11 | RF-013 | Unitaria | «Solicitar corrección» ya no existe: otra decisión no es válida. | RevisionFormTests.test_solo_se_acepta_aprobar_o_rechazar | Dante Fredes | Aprobado |
| CP-DEL-041 | CU-11 | RF-013 | Unitaria | Revisa lo registrado en su delegación. | RevisionPorDelegadoTests.test_el_delegado_aprueba_una_actividad_de_su_delegacion | Dante Fredes | Aprobado |
| CP-INT-063 | CU-11 | RF-013 | Integración | El verificador descarga la evidencia que revisa. | EvidenciaArchivoTests.test_el_verificador_descarga_el_archivo | Dante Fredes | Aprobado |
| CP-INT-188 | CU-11, CU-11.1, CU-11.2 | RF-013, RF-014 | Integración | Revisión de evidencias con Validacion (RN-009). | RevisionTests.test_actividad_rechazada_se_corrige_vuelve_a_revision_y_se_puede_aprobar | Dante Fredes | Aprobado |
| CP-INT-189 | CU-11, CU-11.1, CU-11.2 | RF-013, RF-014 | Integración | Revisión de evidencias con Validacion (RN-009). | RevisionTests.test_actividad_sin_evidencias_pendientes_no_se_revisa | Dante Fredes | Aprobado |
| CP-INT-190 | CU-11, CU-11.1, CU-11.2 | RF-013, RF-014 | Integración | Revisión de evidencias con Validacion (RN-009). | RevisionTests.test_aprobar_valida_cada_evidencia_pendiente_y_actualiza_el_indicador | Dante Fredes | Aprobado |
| CP-INT-191 | CU-11, CU-11.1, CU-11.2 | RF-013, RF-014 | Integración | Revisión de evidencias con Validacion (RN-009). | RevisionTests.test_el_detalle_ofrece_la_revision_solo_a_quien_puede_hacerla | Dante Fredes | Aprobado |
| CP-INT-192 | CU-11, CU-11.1, CU-11.2 | RF-013, RF-014 | Integración | Revisión de evidencias con Validacion (RN-009). | RevisionTests.test_rechazar_exige_motivo_y_ya_no_se_pide_correccion | Dante Fredes | Aprobado |
| CP-INT-193 | CU-11, CU-11.1, CU-11.2 | RF-013, RF-014 | Integración | Revisión de evidencias con Validacion (RN-009). | RevisionTests.test_rechazo_sin_observacion_explica_el_motivo | Dante Fredes | Aprobado |
| CP-INT-194 | CU-11, CU-11.1, CU-11.2 | RF-013, RF-014 | Integración | Revisión de evidencias con Validacion (RN-009). | RevisionTests.test_solo_administracion_coordinacion_y_verificacion_revisan | Dante Fredes | Aprobado |
| CP-INT-195 | CU-11, CU-11.1, CU-11.2 | RF-013, RF-014 | Integración | Revisión de evidencias con Validacion (RN-009). | RevisionTests.test_superusuario_sin_funcionario_no_puede_revisar | Dante Fredes | Aprobado |
| CP-MED-011 | CU-11 | RF-022 | Unitaria | RN-009: la aprobación exige la validación del verificador. | AvanceUnitTests.test_no_cuenta_una_actividad_aprobada_sin_validacion_aprobada | Dante Fredes | Aprobado |
| CP-TRA-010 | CU-11 | RF-013 | Unitaria | Puede revisar actividades de cualquier delegación. | AlcanceUnitTests.test_un_verificador_sin_delegacion_revisa_todas | Dante Fredes | Aprobado |
| CP-ACT-040 | CU-11.1 | RF-013 | Unitaria | Primera, segunda revisión, y así. | ValidacionUnitTests.test_cada_revision_incrementa_el_numero_de_version | Dante Fredes | Aprobado |
| CP-ACT-042 | CU-11.1 | RF-013 | Unitaria | Quién, cuándo, qué decidió y por qué. | ValidacionUnitTests.test_la_decision_deja_verificador_fecha_resultado_y_observacion | Dante Fredes | Aprobado |
| CP-DEL-037 | CU-11.1 | RF-014 | Unitaria | El motivo admite hasta 1000 caracteres. | RevisionFormTests.test_el_motivo_tiene_un_largo_maximo | Dante Fredes | Aprobado |
| CP-DEL-038 | CU-11.1 | RF-013 | Unitaria | Sin motivo no se crea ninguna validación y se explica por qué. | RevisionFormTests.test_la_vista_usa_el_formulario_y_no_registra_un_rechazo_sin_motivo | Dante Fredes | Aprobado |
| CP-DEL-039 | CU-11.1 | RF-013, RF-014 | Unitaria | Rechazar sin motivo, o solo con espacios, no es válido. | RevisionFormTests.test_rechazar_exige_motivo_aunque_venga_en_blanco | Dante Fredes | Aprobado |
| CP-DEL-042 | CU-11.1 | RF-013, RF-036 | Unitaria | Otra delegación queda fuera; lo propio no se autoaprueba. | RevisionPorDelegadoTests.test_el_delegado_no_revisa_otra_delegacion_ni_lo_propio | Dante Fredes | Aprobado |
| CP-DEL-043 | CU-11.1 | RF-013 | Unitaria | Sin motivo no se rechaza; con motivo queda rechazada. | RevisionPorDelegadoTests.test_rechazar_exige_motivo | Dante Fredes | Aprobado |
| CP-ACT-006 | CU-11.2 | RF-014 | Unitaria | RN-009: lo aprobado ya suma y solo se anula con motivo. | ActividadEstadoUnitTests.test_una_actividad_aprobada_no_cambia_de_estado | Dante Fredes | Aprobado |
| CP-ACT-033 | CU-11.2 | RF-014 | Unitaria | Lo ya aprobado no vuelve a pendiente. | EvidenciaUnitTests.test_enviar_a_revision_no_reabre_una_actividad_aprobada | Dante Fredes | Aprobado |
| CP-ACT-044 | CU-11.2 | RF-014 | Unitaria | Sin motivo no hay rechazo; con él la actividad queda rechazada. | ValidacionUnitTests.test_rechazar_exige_un_motivo_y_no_aporta_al_avance | Dante Fredes | Aprobado |
| CP-ACT-045 | CU-11.2 | RF-014 | Unitaria | RN-009: rechazada no suma. | ValidacionUnitTests.test_solo_las_actividades_aprobadas_cuentan_para_la_meta | Dante Fredes | Aprobado |
| CP-MED-013 | CU-11.2 | RF-022 | Unitaria | RN-009: solo lo aprobado aporta. | AvanceUnitTests.test_no_cuentan_las_pendientes_ni_las_rechazadas | Dante Fredes | Aprobado |
| CP-TRA-003 | CU-11.2 | RF-014 | Unitaria | Aprobada no se modifica ni siquiera por la coordinación. | AlcanceUnitTests.test_bloqueo_de_una_actividad_aprobada | Dante Fredes | Aprobado |
| CP-COM-029 | CU-12 | RF-032 | Unitaria | Sin criterios se ven todos los compromisos. | FiltrosAgendaUnitTests.test_sin_filtros_trae_todos | Faride Luna | Aprobado |
| CP-COM-040 | CU-12 | RF-021 | Unitaria | Los totales coinciden con el detalle. | ResumenColectivoUnitTests.test_la_fila_total_suma_a_todos_los_responsables | Faride Luna | Aprobado |
| CP-COM-042 | CU-12 | RF-021 | Unitaria | Orden estable por nombre. | ResumenColectivoUnitTests.test_los_responsables_salen_en_orden_alfabetico | Faride Luna | Aprobado |
| CP-COM-045 | CU-12 | RF-021 | Unitaria | Una fila por responsable con la cantidad en cada estado. | ResumenColectivoUnitTests.test_totaliza_por_responsable_y_estado | Faride Luna | Aprobado |
| CP-COM-046 | CU-12 | RF-016, RF-018 | Unitaria | Cada registro del tubo es una «tarea» y sus estados van en femenino. | TuboDeTrabajoUnitTests.test_cada_registro_se_llama_tarea | Faride Luna | Aprobado |
| CP-COM-049 | CU-12 | RF-016 | Unitaria | Paneles, delegados y la delegación llevan al tubo y no crean tareas. | TuboDeTrabajoUnitTests.test_el_boton_esta_solo_en_la_pagina_del_tubo | Faride Luna | Aprobado |
| CP-COM-050 | CU-12 | RF-016 | Unitaria | El menú, el título y la pestaña usan el término de la Municipalidad. | TuboDeTrabajoUnitTests.test_la_pagina_y_el_menu_dicen_tubo_de_trabajo | Faride Luna | Aprobado |
| CP-DEL-017 | CU-12 | RF-016 | Unitaria | La agenda dice quién crea y quién elimina. | CoordinacionDeDelegadosTests.test_la_agenda_explica_quien_crea_compromisos | Faride Luna | Aprobado |
| CP-INT-184 | CU-12 | RF-021 | Integración | El panel totaliza lo que se ve en la agenda. | ResumenYActividadRecienteVistasTests.test_la_agenda_muestra_el_resumen_por_responsable | Faride Luna | Aprobado |
| CP-COM-023 | CU-12.1 | RF-032 | Unitaria | Delegación y estado se combinan. | FiltrosAgendaUnitTests.test_filtra_por_delegacion_y_estado | Faride Luna | Aprobado |
| CP-COM-024 | CU-12.1 | RF-019, RF-032 | Unitaria | Vencidos no incluye los realizados. | FiltrosAgendaUnitTests.test_filtra_por_plazo | Faride Luna | Aprobado |
| CP-COM-025 | CU-12.1 | RF-032 | Unitaria | Desde y hasta incluyen sus extremos. | FiltrosAgendaUnitTests.test_filtra_por_rango_de_fechas_comprometidas | Faride Luna | Aprobado |
| CP-COM-026 | CU-12.1 | RF-032 | Unitaria | La búsqueda de texto recorre los campos visibles. | FiltrosAgendaUnitTests.test_filtra_por_texto_en_folio_descripcion_solicitante_y_delegacion | Faride Luna | Aprobado |
| CP-COM-028 | CU-12.1 | RF-032 | Unitaria | Un filtro mal formado no rompe la agenda. | FiltrosAgendaUnitTests.test_los_valores_invalidos_se_ignoran | Faride Luna | Aprobado |
| CP-COM-039 | CU-12.1 | RF-021 | Unitaria | Los totales coinciden con el detalle filtrado. | ResumenColectivoUnitTests.test_el_resumen_respeta_el_filtro_aplicado | Faride Luna | Aprobado |
| CP-COM-048 | CU-12.1 | RF-016 | Unitaria | Al filtrar por una delegación, la tarea nueva parte en ella. | TuboDeTrabajoUnitTests.test_el_boton_conserva_la_delegacion_filtrada | Faride Luna | Aprobado |
| CP-DEL-028 | CU-12.1 | RF-032 | Unitaria | El buscador de la delegación filtra por folio o descripción. | ListasSinBotonesFalsosTests.test_el_buscador_de_la_delegacion_filtra | Faride Luna | Aprobado |
| CP-INT-183 | CU-12.1 | RF-021 | Integración | Al filtrar por delegación los totales cambian con el detalle. | ResumenYActividadRecienteVistasTests.test_el_resumen_sigue_el_filtro_de_la_agenda | Faride Luna | Aprobado |
| CP-COM-030 | CU-12.2 | RF-032 | Unitaria | Nada que mostrar, sin error. | FiltrosAgendaUnitTests.test_una_consulta_sin_coincidencias_devuelve_vacio | Faride Luna | Aprobado |
| CP-COM-044 | CU-12.2 | RF-021 | Unitaria | Sin datos no hay división por cero. | ResumenColectivoUnitTests.test_sin_compromisos_los_porcentajes_son_cero | Faride Luna | Aprobado |
| CP-COM-001 | CU-13 | RF-018 | Unitaria | El estado cambia solo desde la agenda, con historial. | CompromisoFormUnitTests.test_al_editar_se_oculta_el_estado_y_se_exige_la_version | Faride Luna | Aprobado |
| CP-COM-016 | CU-13 | RF-018 | Unitaria | Se avanza y un realizado solo vuelve a «en proceso». | EstadoUnitTests.test_estados_permitidos_avanzan_y_un_realizado_solo_se_reabre_a_en_proceso | Faride Luna | Aprobado |
| CP-COM-020 | CU-13 | RF-017 | Unitaria | Lo cerrado no cambia de responsable. | EstadoUnitTests.test_un_compromiso_realizado_no_se_deriva | Faride Luna | Aprobado |
| CP-COM-021 | CU-13 | RF-018 | Unitaria | Solo los cuatro estados definidos. | EstadoUnitTests.test_un_estado_inexistente_se_rechaza | Faride Luna | Aprobado |
| CP-COM-022 | CU-13 | RF-018 | Unitaria | Retroceder no está permitido y no deja rastro. | EstadoUnitTests.test_una_transicion_no_permitida_se_rechaza_sin_historial | Faride Luna | Aprobado |
| CP-DEL-029 | CU-13 | RF-018 | Unitaria | Modificar está solo en la fila del tubo, para quien puede. | ListasSinBotonesFalsosTests.test_no_hay_botones_modificar_ni_eliminar_sin_destino | Faride Luna | Aprobado |
| CP-DEL-030 | CU-13 | RF-018 | Unitaria | Quien no es responsable no cambia el estado aunque envíe el formulario. | ModificarEnSuPaginaTests.test_cambiar_el_estado_exige_ser_responsable | Faride Luna | Aprobado |
| CP-DEL-032 | CU-13 | RF-018 | Unitaria | El responsable y la coordinación ven Modificar y los estados; otro funcionario no. | ModificarEnSuPaginaTests.test_la_fila_del_tubo_ofrece_modificar_solo_a_quien_puede | Faride Luna | Aprobado |
| CP-INT-043 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_cerrar_un_compromiso_ya_realizado_se_rechaza | Faride Luna | Aprobado |
| CP-INT-044 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_el_cambio_de_estado_desde_la_vista_guarda_la_observacion_y_rechaza_lo_no_permitido | Faride Luna | Aprobado |
| CP-INT-045 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_estados_permitidos_avanzan_y_un_realizado_solo_se_reabre_a_en_proceso | Faride Luna | Aprobado |
| CP-INT-046 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_la_agenda_destaca_los_proximos_a_vencer_y_cuenta_cada_grupo | Faride Luna | Aprobado |
| CP-INT-047 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_la_agenda_ofrece_solo_las_transiciones_permitidas | Faride Luna | Aprobado |
| CP-INT-048 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_la_vista_de_eliminar_explica_por_que_no_se_puede | Faride Luna | Aprobado |
| CP-INT-049 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_los_dias_de_alerta_son_configurables | Faride Luna | Aprobado |
| CP-INT-050 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_proximo_a_vencer_dentro_de_los_dias_de_alerta | Faride Luna | Aprobado |
| CP-INT-051 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_reabrir_un_realizado_guarda_la_observacion_en_el_historial | Faride Luna | Aprobado |
| CP-INT-052 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_un_incumplimiento_no_se_elimina_pero_uno_vigente_o_realizado_si | Faride Luna | Aprobado |
| CP-INT-053 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_una_transicion_no_permitida_se_rechaza_y_no_deja_historial | Faride Luna | Aprobado |
| CP-INT-054 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_vencido_y_proximo_a_vencer_son_excluyentes | Faride Luna | Aprobado |
| CP-COM-015 | CU-13.1 | RF-017 | Unitaria | La derivación queda trazada. | EstadoUnitTests.test_derivar_cambia_el_responsable_y_lo_deja_en_el_historial | Faride Luna | Aprobado |
| CP-COM-017 | CU-13.1 | RF-018 | Unitaria | La reapertura queda explicada. | EstadoUnitTests.test_reabrir_un_realizado_conserva_la_observacion | Faride Luna | Aprobado |
| CP-COM-018 | CU-13.1 | RF-018 | Unitaria | La creación deja su primer registro. | EstadoUnitTests.test_registrar_historial_guarda_el_estado_actual_como_nuevo | Faride Luna | Aprobado |
| CP-COM-019 | CU-13.1 | RF-018 | Unitaria | Estado anterior, nuevo, autor y observación. | EstadoUnitTests.test_set_estado_cambia_y_deja_historial | Faride Luna | Aprobado |
| CP-COM-012 | CU-13.2 | RF-018 | Unitaria | El cierre se refleja y queda en el historial. | EstadoUnitTests.test_cerrar_deja_el_compromiso_realizado_con_su_resolucion | Faride Luna | Aprobado |
| CP-COM-013 | CU-13.2 | RF-018 | Unitaria | Sin resolución no se cierra. | EstadoUnitTests.test_cerrar_exige_una_resolucion | Faride Luna | Aprobado |
| CP-COM-014 | CU-13.2 | RF-018 | Unitaria | El cierre solo se hace una vez. | EstadoUnitTests.test_cerrar_uno_ya_realizado_se_rechaza | Faride Luna | Aprobado |
| CP-COM-038 | CU-14 | RF-019, RF-021 | Unitaria | El vencido sin realizar se destaca. | ResumenColectivoUnitTests.test_cuenta_los_vencidos_de_cada_responsable | Faride Luna | Aprobado |
| CP-COM-043 | CU-14 | RF-021 | Unitaria | El pendiente es todo lo que aún no está realizado. | ResumenColectivoUnitTests.test_porcentaje_realizado_y_pendiente | Faride Luna | Aprobado |
| CP-COM-031 | CU-14.1 | RF-019 | Unitaria | Días que faltan, negativos si ya pasó. | PlazoUnitTests.test_dias_para_vencer | Faride Luna | Aprobado |
| CP-COM-034 | CU-14.1 | RF-019 | Unitaria | Vencido, próximo a vencer, realizado o estado normal. | PlazoUnitTests.test_situacion_de_plazo_clasifica_cada_compromiso | Faride Luna | Aprobado |
| CP-MED-031 | CU-14.1 | RF-019 | Unitaria | Vigentes, por vencer, vencidos y realizados. | FichaPersonalUnitTests.test_resumen_de_compromisos_por_situacion | Faride Luna | Aprobado |
| CP-ALE-001 | CU-14.2 | RF-037 | Unitaria | Los cuatro datos que pide el requisito. | AlertasConjuntasTests.test_cada_alerta_trae_motivo_responsable_fecha_y_enlace | Faride Luna | Aprobado |
| CP-ALE-002 | CU-14.2 | RF-037 | Unitaria | La página resume cuántas son urgentes. | AlertasConjuntasTests.test_la_pantalla_de_alertas_muestra_conteos_y_exige_sesion | Faride Luna | Aprobado |
| CP-ALE-003 | CU-14.2 | RF-037 | Unitaria | Mensaje claro cuando no hay nada. | AlertasConjuntasTests.test_la_pantalla_sin_alertas_lo_dice | Faride Luna | Aprobado |
| CP-ALE-004 | CU-14.2 | RF-037 | Unitaria | Orden por gravedad y antigüedad. | AlertasConjuntasTests.test_las_urgentes_van_primero_y_luego_por_fecha | Faride Luna | Aprobado |
| CP-ALE-005 | CU-14.2 | RF-037 | Unitaria | La lista vacía es válida. | AlertasConjuntasTests.test_sin_nada_pendiente_no_hay_alertas | Faride Luna | Aprobado |
| CP-ALE-023 | CU-14.2 | RF-037 | Unitaria | Un día, no 1 días. | AlertasDeVencimientoTests.test_el_singular_se_escribe_bien | Faride Luna | Aprobado |
| CP-ALE-024 | CU-14.2 | RF-037, RNF-015 | Unitaria | Con 7 días alerta el que vence en 6. | AlertasDeVencimientoTests.test_los_dias_de_alerta_son_configurables | Faride Luna | Aprobado |
| CP-ALE-025 | CU-14.2 | RF-037 | Unitaria | Solo lo que requiere atención. | AlertasDeVencimientoTests.test_no_alertan_los_realizados_ni_los_lejanos | Faride Luna | Aprobado |
| CP-ALE-027 | CU-14.2 | RF-037 | Unitaria | Hoy y los días de alerta. | AlertasDeVencimientoTests.test_un_compromiso_proximo_a_vencer_genera_una_advertencia | Faride Luna | Aprobado |
| CP-ALE-028 | CU-14.2 | RF-037 | Unitaria | Dice hace cuántos días venció. | AlertasDeVencimientoTests.test_un_compromiso_vencido_genera_una_alerta_urgente | Faride Luna | Aprobado |
| CP-COM-032 | CU-14.2 | RF-019, RF-037 | Unitaria | Con 7 días, vence en 7 sí y en 8 no. | PlazoUnitTests.test_los_dias_de_alerta_son_configurables | Faride Luna | Aprobado |
| CP-COM-033 | CU-14.2 | RF-019, RF-037 | Unitaria | Hoy y los 3 días siguientes, por defecto. | PlazoUnitTests.test_proximo_a_vencer_dentro_de_los_dias_de_alerta | Faride Luna | Aprobado |
| CP-COM-035 | CU-14.2 | RF-019 | Unitaria | El vencido se conserva con su historial. | PlazoUnitTests.test_un_incumplimiento_no_se_elimina | Faride Luna | Aprobado |
| CP-COM-036 | CU-14.2 | RF-019 | Unitaria | Solo el incumplimiento queda protegido. | PlazoUnitTests.test_uno_vigente_o_realizado_si_se_elimina | Faride Luna | Aprobado |
| CP-ALE-014 | CU-16 | RF-037 | Unitaria | Sin cálculos no se inventa nada. | AlertasDeAvanceTests.test_sin_indicadores_no_hay_alertas_de_avance | Por definir | Aprobado |
| CP-ALE-016 | CU-16 | RF-037 | Unitaria | 25 % frente a 50 % esperado. | AlertasDeAvanceTests.test_una_delegacion_en_rojo_alerta | Por definir | Aprobado |
| CP-ALE-017 | CU-16 | RF-037 | Unitaria | Solo el rojo, que no llega al 60 % de lo esperado. | AlertasDeAvanceTests.test_verde_y_ambar_no_alertan | Por definir | Aprobado |
| CP-INT-140 | CU-16, CU-16.1, CU-17, CU-18, CU-18.1 | RF-026, RF-027, RF-028, RF-029 | Integración | Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008). | MedicionVistasTests.test_dashboard_muestra_el_cumplimiento_y_el_semaforo_de_cada_delegacion | Por definir | Aprobado |
| CP-INT-141 | CU-16, CU-16.1, CU-17, CU-18, CU-18.1 | RF-026, RF-027, RF-028, RF-029 | Integración | Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008). | MedicionVistasTests.test_el_cumplimiento_de_la_delegacion_pondera_sus_metas | Por definir | Aprobado |
| CP-INT-142 | CU-16, CU-16.1, CU-17, CU-18, CU-18.1 | RF-026, RF-027, RF-028, RF-029 | Integración | Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008). | MedicionVistasTests.test_gestionar_metas_solo_para_administracion_y_coordinacion | Por definir | Aprobado |
| CP-INT-143 | CU-16, CU-16.1, CU-17, CU-18, CU-18.1 | RF-026, RF-027, RF-028, RF-029 | Integración | Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008). | MedicionVistasTests.test_la_portada_usa_el_promedio_de_los_indicadores | Por definir | Aprobado |
| CP-INT-144 | CU-16, CU-16.1, CU-17, CU-18, CU-18.1 | RF-026, RF-027, RF-028, RF-029 | Integración | Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008). | MedicionVistasTests.test_las_barras_de_progreso_no_usan_coma_decimal | Por definir | Aprobado |
| CP-INT-145 | CU-16, CU-16.1, CU-17, CU-18, CU-18.1 | RF-026, RF-027, RF-028, RF-029 | Integración | Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008). | MedicionVistasTests.test_selector_de_periodo_y_busqueda_por_delegacion | Por definir | Aprobado |
| CP-INT-146 | CU-16, CU-16.1, CU-17, CU-18, CU-18.1 | RF-026, RF-027, RF-028, RF-029 | Integración | Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008). | MedicionVistasTests.test_semaforo_segun_lo_esperado_al_dia | Por definir | Aprobado |
| CP-INT-147 | CU-16, CU-16.1, CU-17, CU-18, CU-18.1 | RF-026, RF-027, RF-028, RF-029 | Integración | Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008). | MedicionVistasTests.test_semaforo_y_resumen_comparten_los_resultados | Por definir | Aprobado |
| CP-INT-148 | CU-16, CU-16.1, CU-17, CU-18, CU-18.1 | RF-026, RF-027, RF-028, RF-029 | Integración | Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008). | MedicionVistasTests.test_sin_indicadores_se_avisa_y_una_delegacion_sin_calculo_se_marca | Por definir | Aprobado |
| CP-INT-149 | CU-16, CU-16.1, CU-17, CU-18, CU-18.1 | RF-026, RF-027, RF-028, RF-029 | Integración | Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008). | MedicionVistasTests.test_solo_cuenta_el_ultimo_indicador_de_cada_meta | Por definir | Aprobado |
| CP-MED-041 | CU-16 | RF-027 | Unitaria | Centro al 100 % es verde y Rural al 25 % es rojo. | ResultadosPorDelegacionUnitTests.test_cumplimiento_y_color_de_cada_delegacion | Por definir | Aprobado |
| CP-MED-024 | CU-16.1 | RF-027 | Unitaria | RN-008 con esperado de 50 %. | CumplimientoUnitTests.test_semaforo_segun_lo_esperado_al_dia | Por definir | Aprobado |
| CP-ORG-046 | CU-16.1 | RF-027 | Unitaria | RN-008 con esperado de 50 %. | PeriodoPuroUnitTests.test_semaforo_verde_ambar_y_rojo | Por definir | Aprobado |
| CP-MED-042 | CU-17.1 | RF-026 | Unitaria | Con esperado de 50 %: +50 para Centro y -25 para Rural. | ResultadosPorDelegacionUnitTests.test_diferencia_con_lo_esperado_y_desviacion | Por definir | Aprobado |
| CP-ORG-044 | CU-17.1 | RF-026 | Unitaria | Antes del inicio es 0 % y después del término 100 %. | PeriodoPuroUnitTests.test_porcentaje_esperado_no_pasa_de_los_limites | Por definir | Aprobado |
| CP-ORG-045 | CU-17.1 | RF-026 | Unitaria | RN-007: días transcurridos sobre días totales. | PeriodoPuroUnitTests.test_porcentaje_esperado_segun_los_dias_transcurridos | Por definir | Aprobado |
| CP-MED-049 | CU-17.2 | RF-026 | Unitaria | RN-008: ámbar y rojo son desviación. | ResultadosPorDelegacionUnitTests.test_una_desviacion_ambar_tambien_se_destaca | Por definir | Aprobado |
| CP-MED-035 | CU-18 | RF-029 | Unitaria | Con indicadores en ambos, gana el abierto. | PeriodoVigenteUnitTests.test_por_defecto_el_periodo_abierto_mas_reciente | Por definir | Aprobado |
| CP-MED-037 | CU-18 | RF-029 | Unitaria | Sin períodos abiertos, el más reciente con cálculos. | PeriodoVigenteUnitTests.test_si_ninguno_esta_abierto_se_usa_el_mas_reciente | Por definir | Aprobado |
| CP-MED-038 | CU-18 | RF-029 | Unitaria | Sin cálculos la pantalla muestra el aviso vacío. | PeriodoVigenteUnitTests.test_sin_indicadores_en_ningun_periodo_no_hay_periodo_vigente | Por definir | Aprobado |
| CP-MED-039 | CU-18 | RF-029 | Unitaria | Un período sin cálculos no se ofrece. | PeriodoVigenteUnitTests.test_solo_se_ofrecen_los_periodos_con_indicadores | Por definir | Aprobado |
| CP-MED-047 | CU-18 | RF-029 | Unitaria | Sin período elegido la lista está vacía. | ResultadosPorDelegacionUnitTests.test_sin_periodo_no_hay_resultados | Por definir | Aprobado |
| CP-ORG-047 | CU-18 | RF-029 | Unitaria | RN-006: el cumplimiento colectivo debe alcanzar el umbral. | PeriodoPuroUnitTests.test_umbral_colectivo | Por definir | Aprobado |
| CP-DEL-002 | CU-18.1 | RF-028, RF-029 | Unitaria | El panel muestra su cumplimiento y el acceso a su delegación. | AmbitoDelDelegadoTests.test_el_panel_del_delegado_muestra_su_delegacion | Por definir | Aprobado |
| CP-DEL-003 | CU-18.1 | RF-028, RF-029 | Unitaria | Mediciones históricas y cifras del panel, solo de Centro. | AmbitoDelDelegadoTests.test_el_resumen_y_el_panel_no_mezclan_otras_delegaciones | Por definir | Aprobado |
| CP-DEL-004 | CU-18.1 | RF-028, RF-029 | Unitaria | Con sesión, la portada cuenta solo su delegación. | AmbitoDelDelegadoTests.test_la_portada_del_delegado_muestra_solo_sus_cifras | Por definir | Aprobado |
| CP-DEL-015 | CU-18.1 | RF-028, RF-029 | Unitaria | El coordinador ve cada delegación con su avance y su delegado. | CoordinacionDeDelegadosTests.test_el_panel_del_coordinador_muestra_todas_las_delegaciones_y_su_delegado | Por definir | Aprobado |
| CP-DEL-016 | CU-18.1 | RF-028, RF-029 | Unitaria | Lo que espera su revisión y el tubo, solo de su delegación. | CoordinacionDeDelegadosTests.test_el_panel_del_delegado_se_centra_en_su_delegacion | Por definir | Aprobado |
| CP-MED-044 | CU-18.1 | RF-030 | Unitaria | Fecha del último registro y días desde entonces. | ResultadosPorDelegacionUnitTests.test_informa_el_ultimo_calculo_y_los_dias_transcurridos | Por definir | Aprobado |
| CP-MED-045 | CU-18.1 | RF-029 | Unitaria | Promedio simple de los cumplimientos. | ResultadosPorDelegacionUnitTests.test_promedio_general | Por definir | Aprobado |
| CP-ORG-062 | CU-18.1 | RF-024 | Unitaria | 60 % de la meta al 100 % y 40 % al 50 % dan 80 %. | PromedioPonderadoUnitTests.test_pondera_cada_meta_por_su_ponderador | Por definir | Aprobado |
| CP-ORG-063 | CU-18.1 | RF-024 | Unitaria | Sin indicadores no hay división por cero. | PromedioPonderadoUnitTests.test_sin_indicadores_el_promedio_es_cero | Por definir | Aprobado |
| CP-MED-043 | CU-18.2 | RF-029 | Unitaria | El detalle explica de dónde sale la cifra. | ResultadosPorDelegacionUnitTests.test_el_detalle_muestra_avance_y_meta_de_cada_item | Por definir | Aprobado |
| CP-INT-084 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_cambiar_el_estado_de_un_compromiso_conserva_los_filtros_de_la_agenda | Por definir | Aprobado |
| CP-INT-085 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_el_csv_tiene_bom_separador_y_cabecera_y_queda_auditado | Por definir | Aprobado |
| CP-INT-086 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_el_detalle_vuelve_a_la_lista_con_los_filtros_usados | Por definir | Aprobado |
| CP-INT-087 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_el_informe_de_actividades_respeta_el_ambito_del_usuario | Por definir | Aprobado |
| CP-INT-088 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_el_informe_de_compromisos_marca_la_situacion_del_plazo | Por definir | Aprobado |
| CP-INT-089 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_el_informe_de_cumplimiento_usa_los_indicadores | Por definir | Aprobado |
| CP-INT-090 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_el_informe_exige_iniciar_sesion | Por definir | Aprobado |
| CP-INT-091 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_eliminar_una_actividad_vuelve_a_la_lista_filtrada | Por definir | Aprobado |
| CP-INT-092 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_filtrar_actividades_por_cada_criterio | Por definir | Aprobado |
| CP-INT-093 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_filtrar_compromisos_por_plazo_estado_y_periodo | Por definir | Aprobado |
| CP-INT-094 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_la_agenda_filtra_por_plazo | Por definir | Aprobado |
| CP-INT-095 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_la_lista_de_actividades_aplica_los_filtros | Por definir | Aprobado |
| CP-INT-096 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_la_version_para_imprimir_ofrece_imprimir_y_oculta_los_filtros | Por definir | Aprobado |
| CP-INT-097 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_los_valores_invalidos_se_ignoran_en_vez_de_fallar | Por definir | Aprobado |
| CP-INT-098 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_un_tipo_de_informe_desconocido_cae_en_actividades | Por definir | Aprobado |
| CP-TRA-028 | CU-20 | RF-033 | Unitaria | Abre bien en Excel con tildes. | InformesUnitTests.test_el_csv_tiene_bom_separador_punto_y_coma_y_nombre_de_archivo | Por definir | Aprobado |
| CP-COM-027 | CU-20.1 | RF-033 | Unitaria | Columnas y valores listos para exportar. | FiltrosAgendaUnitTests.test_las_filas_del_informe_incluyen_responsable_y_situacion_del_plazo | Por definir | Aprobado |
| CP-COM-041 | CU-20.1 | RF-021, RF-033 | Unitaria | Columnas y filas listas para exportar. | ResumenColectivoUnitTests.test_las_filas_del_informe_terminan_con_el_total | Por definir | Aprobado |
| CP-INT-182 | CU-20.1 | RF-021, RF-033 | Integración | El informe repite el resumen de la agenda. | ResumenYActividadRecienteVistasTests.test_el_informe_de_resumen_trae_el_total | Por definir | Aprobado |
| CP-MED-005 | CU-20.1 | RF-030, RF-033 | Unitaria | Fecha legible y promedio con dos decimales. | ActividadRecienteUnitTests.test_las_filas_del_informe_traen_los_datos_formateados | Por definir | Aprobado |
| CP-TRA-029 | CU-20.1 | RF-033 | Unitaria | Columnas y valores listos para exportar. | InformesUnitTests.test_las_filas_de_actividades_traen_los_datos_del_informe | Por definir | Aprobado |
| CP-TRA-030 | CU-20.1 | RF-033 | Unitaria | Una fila por delegación con su cumplimiento y estado. | InformesUnitTests.test_las_filas_de_cumplimiento_incluyen_la_diferencia | Por definir | Aprobado |
| CP-TRA-031 | CU-20.1 | RF-033 | Unitaria | Sin registros no hay error. | InformesUnitTests.test_un_informe_vacio_solo_trae_la_cabecera | Por definir | Aprobado |
| CP-INT-181 | CU-20.2 | RF-030, RF-033 | Integración | Un funcionario ve solo su delegación. | ResumenYActividadRecienteVistasTests.test_el_informe_de_actividad_reciente_respeta_el_ambito | Por definir | Aprobado |
| CP-TRA-006 | CU-20.2 | RF-032 | Unitaria | Un funcionario del Centro no ve lo de Rural. | AlcanceUnitTests.test_quien_tiene_delegacion_solo_ve_la_suya | Por definir | Aprobado |
| CP-ACT-002 | CU-23.1 | RF-034 | Unitaria | La versión crece con cada edición. | ActividadEstadoUnitTests.test_cada_guardado_sube_la_version_en_uno | Por definir | Aprobado |
| CP-ACT-004 | CU-23.1 | RF-034 | Unitaria | Gana el primero que guarda; el otro debe recargar. | ActividadEstadoUnitTests.test_dos_ediciones_simultaneas_la_segunda_se_rechaza | Por definir | Aprobado |
| CP-ACT-005 | CU-23.1 | RF-034 | Unitaria | El campo oculto version detecta datos viejos. | ActividadEstadoUnitTests.test_el_formulario_rechaza_una_version_desactualizada | Por definir | Aprobado |
| CP-COM-004 | CU-23.1 | RF-034 | Unitaria | El formulario detecta la versión vieja. | CompromisoFormUnitTests.test_dos_ediciones_simultaneas_la_segunda_se_rechaza | Por definir | Aprobado |
| CP-COM-006 | CU-23.1 | RF-034 | Unitaria | Gana quien guarda primero. | CompromisoFormUnitTests.test_el_modelo_tambien_rechaza_guardar_con_una_version_vieja | Por definir | Aprobado |
| CP-MED-021 | CU-25 | RF-024, RF-038 | Unitaria | El máximo computable es configurable por período. | CumplimientoUnitTests.test_el_tope_lo_define_el_parametro_del_periodo | Vinzenz Lafferte | Aprobado |
| CP-ORG-012 | CU-25 | RF-001, RF-003, RF-004 | Unitaria | Con datos relacionados no se elimina: se desactiva y se dice por qué. | EliminarEnMantenedoresTests.test_con_datos_relacionados_se_desactiva_y_explica_la_razon | Vinzenz Lafferte | Aprobado |
| CP-ORG-015 | CU-25 | RF-001 | Unitaria | La fila activa dice «Eliminar» y la inactiva «Activar». | EliminarEnMantenedoresTests.test_la_lista_ofrece_eliminar_en_activos_y_activar_en_inactivos | Vinzenz Lafferte | Aprobado |
| CP-ORG-016 | CU-25 | RF-002 | Unitaria | Los roles asignados se borran con el funcionario: no impiden eliminarlo. | EliminarEnMantenedoresTests.test_los_datos_relacionados_no_cuentan_lo_que_se_borra_junto | Vinzenz Lafferte | Aprobado |
| CP-ORG-017 | CU-25 | RF-001, RF-003, RF-004 | Unitaria | Delegación, cargo y catálogo sin uso se eliminan. | EliminarEnMantenedoresTests.test_sin_datos_relacionados_se_elimina_con_auditoria | Vinzenz Lafferte | Aprobado |
| CP-ORG-038 | CU-25 | RF-038 | Unitaria | Cambiar un período no altera otro. | ParametroUnitTests.test_cada_periodo_conserva_su_propio_valor | Vinzenz Lafferte | Aprobado |
| CP-ORG-039 | CU-25 | RF-007 | Unitaria | Sin parámetro se usa el valor por defecto. | ParametroUnitTests.test_obtener_parametro_devuelve_el_valor_o_el_defecto | Vinzenz Lafferte | Aprobado |
| CP-ORG-040 | CU-25 | RF-038 | Unitaria | RN-013: los resultados cerrados no cambian. | ParametroUnitTests.test_un_periodo_cerrado_conserva_sus_parametros | Vinzenz Lafferte | Aprobado |
| CP-ORG-041 | CU-25 | RF-038 | Unitaria | Cada período tiene su propio valor por clave. | ParametroUnitTests.test_una_clave_no_se_repite_en_el_mismo_periodo | Vinzenz Lafferte | Aprobado |
| CP-DEL-009 | CU-26 | RF-001, RF-017 | Unitaria | Solo delegados activos, delegaciones activas y sin repetir la asignación. | CoordinacionDeDelegadosTests.test_asignar_delegado_valida_el_formulario | César Aranda | Aprobado |
| CP-DEL-011 | CU-26 | RF-001, RF-017 | Unitaria | Queda en la delegación y en la auditoría. | CoordinacionDeDelegadosTests.test_el_coordinador_asigna_un_delegado_a_una_delegacion | César Aranda | Aprobado |
| CP-INT-166 | CU-26, CU-30 | RF-001, RF-002, RF-036 | Integración | Métodos de Delegacion, Cargo, Funcionario y Auditoria con la base de datos. | OrganizacionAccesoTests.test_delegacion_asigna_funcionario_y_cambia_estado | César Aranda | Aprobado |
| CP-INT-167 | CU-26, CU-30 | RF-001, RF-002, RF-036 | Integración | Métodos de Delegacion, Cargo, Funcionario y Auditoria con la base de datos. | OrganizacionAccesoTests.test_identificadores | César Aranda | Aprobado |
| CP-INT-168 | CU-26, CU-30 | RF-001, RF-002, RF-036 | Integración | Métodos de Delegacion, Cargo, Funcionario y Auditoria con la base de datos. | OrganizacionAccesoTests.test_reasignar_cargo_exige_cargo_vigente | César Aranda | Aprobado |
| CP-INT-169 | CU-26, CU-30 | RF-001, RF-002, RF-036 | Integración | Métodos de Delegacion, Cargo, Funcionario y Auditoria con la base de datos. | OrganizacionAccesoTests.test_registrar_evento_a_nombre_del_funcionario | César Aranda | Aprobado |
| CP-INT-170 | CU-26, CU-30 | RF-001, RF-002, RF-036 | Integración | Métodos de Delegacion, Cargo, Funcionario y Auditoria con la base de datos. | OrganizacionAccesoTests.test_registrar_evento_a_nombre_del_usuario_maestro | César Aranda | Aprobado |
| CP-INT-171 | CU-26, CU-30 | RF-001, RF-002, RF-036 | Integración | Métodos de Delegacion, Cargo, Funcionario y Auditoria con la base de datos. | OrganizacionAccesoTests.test_rol_no_se_repite_para_el_mismo_funcionario | César Aranda | Aprobado |
| CP-INT-172 | CU-26, CU-26.1 | RF-002 | Integración | tiene_rol y control de acceso por rol. | PermisosTests.test_cuenta_inactiva_no_tiene_roles | César Aranda | Aprobado |
| CP-INT-173 | CU-26, CU-26.1 | RF-002 | Integración | tiene_rol y control de acceso por rol. | PermisosTests.test_decorador_deja_pasar_al_rol_permitido_y_redirige_a_los_demas | César Aranda | Aprobado |
| CP-INT-174 | CU-26, CU-26.1 | RF-002 | Integración | tiene_rol y control de acceso por rol. | PermisosTests.test_funcionario_con_varios_roles | César Aranda | Aprobado |
| CP-INT-175 | CU-26, CU-26.1 | RF-002 | Integración | tiene_rol y control de acceso por rol. | PermisosTests.test_funcionario_inactivo_no_aporta_roles | César Aranda | Aprobado |
| CP-INT-176 | CU-26, CU-26.1 | RF-002 | Integración | tiene_rol y control de acceso por rol. | PermisosTests.test_mixin_deja_pasar_al_rol_permitido_y_redirige_a_los_demas | César Aranda | Aprobado |
| CP-INT-177 | CU-26, CU-26.1 | RF-002 | Integración | tiene_rol y control de acceso por rol. | PermisosTests.test_superusuario_y_usuario_maestro_cuentan_como_administrador | César Aranda | Aprobado |
| CP-INT-178 | CU-26, CU-26.1 | RF-002 | Integración | tiene_rol y control de acceso por rol. | PermisosTests.test_tiene_rol_segun_los_roles_del_funcionario | César Aranda | Aprobado |
| CP-INT-179 | CU-26, CU-26.1 | RF-002 | Integración | tiene_rol y control de acceso por rol. | PermisosTests.test_usuario_sin_funcionario_ni_sesion_no_tiene_roles | César Aranda | Aprobado |
| CP-MED-048 | CU-26 | RF-001 | Unitaria | Las desactivadas salen de los resultados. | ResultadosPorDelegacionUnitTests.test_una_delegacion_inactiva_no_aparece | César Aranda | Aprobado |
| CP-ORG-009 | CU-26 | RF-002 | Unitaria | Asignar un funcionario actualiza su delegación. | DelegacionUnitTests.test_asignar_funcionario_cambia_su_delegacion | César Aranda | Aprobado |
| CP-ORG-010 | CU-26 | RF-001 | Unitaria | Dos delegaciones no pueden llamarse igual. | DelegacionUnitTests.test_el_nombre_de_la_delegacion_es_unico | César Aranda | Aprobado |
| CP-ORG-011 | CU-26 | RF-001 | Unitaria | Desactivar conserva el registro y su historial. | DelegacionUnitTests.test_set_estado_activa_y_desactiva_sin_borrar | César Aranda | Aprobado |
| CP-ORG-013 | CU-26 | RF-002 | Unitaria | Quien registró actividades se desactiva con su cuenta: su trabajo se conserva. | EliminarEnMantenedoresTests.test_funcionario_que_trabajo_en_el_sistema_se_desactiva | César Aranda | Aprobado |
| CP-ORG-014 | CU-26 | RF-002 | Unitaria | Sin datos relacionados se eliminan el funcionario, su cuenta y sus roles. | EliminarEnMantenedoresTests.test_funcionario_sin_datos_se_elimina_con_su_cuenta | César Aranda | Aprobado |
| CP-ORG-018 | CU-26 | RF-002 | Unitaria | Sin contraseña no hay alta. | FuncionarioFormUnitTests.test_al_crear_la_contrasena_es_obligatoria | César Aranda | Aprobado |
| CP-ORG-020 | CU-26 | RF-002, RNF-004 | Unitaria | La confirmación debe ser igual. | FuncionarioFormUnitTests.test_las_contrasenas_deben_coincidir | César Aranda | Aprobado |
| CP-ORG-021 | CU-26 | RF-002 | Unitaria | Las listas solo muestran opciones vigentes. | FuncionarioFormUnitTests.test_no_se_ofrecen_cargos_retirados_ni_delegaciones_inactivas | César Aranda | Aprobado |
| CP-ORG-022 | CU-26 | RF-002 | Unitaria | El alta crea la cuenta, el funcionario y sus roles. | FuncionarioFormUnitTests.test_un_alta_valida_crea_cuenta_funcionario_y_roles | César Aranda | Aprobado |
| CP-ORG-023 | CU-26 | RF-002 | Unitaria | Sin cuentas duplicadas, sin distinguir mayúsculas. | FuncionarioFormUnitTests.test_un_nombre_de_usuario_repetido_se_rechaza | César Aranda | Aprobado |
| CP-ORG-024 | CU-26 | RF-002, RNF-004 | Unitaria | Se aplican los validadores de contraseña. | FuncionarioFormUnitTests.test_una_contrasena_debil_se_rechaza | César Aranda | Aprobado |
| CP-ORG-025 | CU-26 | RF-002 | Unitaria | Dos funcionarios no comparten identificador. | FuncionarioUnitTests.test_el_identificador_institucional_es_unico | César Aranda | Aprobado |
| CP-ORG-026 | CU-26 | RF-002 | Unitaria | No se reasigna a un cargo retirado. | FuncionarioUnitTests.test_reasignar_a_un_cargo_no_vigente_se_rechaza | César Aranda | Aprobado |
| CP-ORG-027 | CU-26 | RF-002 | Unitaria | Un funcionario puede pasar a un cargo vigente. | FuncionarioUnitTests.test_reasignar_cargo_vigente | César Aranda | Aprobado |
| CP-SEG-001 | CU-26 | RF-002 | Unitaria | La ruta /admin/ no existe. | AccesoPorPerfilTests.test_django_admin_no_esta_publicado | César Aranda | Aprobado |
| CP-SEG-005 | CU-26 | RF-002, RF-029 | Unitaria | Usuarios, perfiles y los ocho mantenedores. | AccesoPorPerfilTests.test_el_panel_administrador_muestra_gestion_de_usuarios_y_todos_los_mantenedores | César Aranda | Aprobado |
| CP-SEG-007 | CU-26 | RF-002 | Unitaria | Solo lectura para el administrador. | AccesoPorPerfilTests.test_la_pagina_de_perfiles_lista_permisos_y_usuarios | César Aranda | Aprobado |
| CP-SEG-008 | CU-26 | RF-002 | Unitaria | Un usuario queda en un solo perfil. | GestionDeUsuariosTests.test_cambiar_el_perfil_reemplaza_el_grupo_anterior | César Aranda | Aprobado |
| CP-SEG-009 | CU-26 | RF-002 | Unitaria | El perfil elegido queda como grupo de la cuenta. | GestionDeUsuariosTests.test_crear_usuario_con_perfil_elegido | César Aranda | Aprobado |
| CP-SEG-011 | CU-26 | RF-002 | Unitaria | Sin perfil, un funcionario queda como Funcionario. | GestionDeUsuariosTests.test_sin_perfil_elegido_se_deduce_de_los_roles | César Aranda | Aprobado |
| CP-SEG-013 | CU-26 | RF-002 | Unitaria | Un Coordinador sin rol coordinador ve todas las delegaciones. | PerfilesTests.test_el_perfil_coordinador_aporta_el_alcance_de_su_rol | César Aranda | Aprobado |
| CP-SEG-014 | CU-26 | RF-002 | Unitaria | El Delegado revisa, pero su alcance sigue siendo su delegación. | PerfilesTests.test_el_perfil_delegado_no_da_alcance_global | César Aranda | Aprobado |
| CP-SEG-016 | CU-26 | RF-002 | Unitaria | Administrador, coordinador, delegado o verificador, y los demás. | PerfilesTests.test_el_perfil_se_deduce_de_los_roles | César Aranda | Aprobado |
| CP-SEG-017 | CU-26 | RF-002 | Unitaria | Cada perfil tiene más permisos que el siguiente. | PerfilesTests.test_las_migraciones_crean_los_cuatro_perfiles_con_permisos_diferenciados | César Aranda | Aprobado |
| CP-SEG-019 | CU-26 | RF-002 | Unitaria | Aunque la cuenta siga activa, su ficha inactiva corta los permisos. | PerfilesTests.test_un_funcionario_desactivado_pierde_los_permisos_de_su_perfil | César Aranda | Aprobado |
| CP-TRA-022 | CU-26 | RF-002 | Unitaria | Quien tiene el rol entra. | DecoradorRolUnitTests.test_con_el_rol_correcto_ejecuta_la_vista | César Aranda | Aprobado |
| CP-TRA-032 | CU-26 | RF-001 | Unitaria | La consulta se arma sin error. | MantenedoresUnitTests.test_cada_mantenedor_apunta_a_un_modelo_y_un_formulario_coherentes | César Aranda | Aprobado |
| CP-TRA-034 | CU-26 | RF-002 | Unitaria | Sin cuenta activa no inicia sesión. | MantenedoresUnitTests.test_desactivar_un_funcionario_desactiva_tambien_su_cuenta | César Aranda | Aprobado |
| CP-TRA-036 | CU-26 | RF-002 | Unitaria | Los permisos consultan esos nombres. | MantenedoresUnitTests.test_los_roles_del_sistema_no_se_eliminan_pero_uno_propio_si | César Aranda | Aprobado |
| CP-TRA-039 | CU-26 | RF-001 | Unitaria | Las ocho tablas maestras. | MantenedoresUnitTests.test_son_exactamente_ocho_mantenedores | César Aranda | Aprobado |
| CP-TRA-040 | CU-26 | RF-001 | Unitaria | Presentación de las columnas del listado. | MantenedoresUnitTests.test_texto_formatea_booleanos_fechas_y_vacios | César Aranda | Aprobado |
| CP-TRA-041 | CU-26 | RF-002 | Unitaria | El procesador de contexto lo calcula. | RolesUnitTests.test_el_menu_de_administracion_depende_del_rol | César Aranda | Aprobado |
| CP-TRA-042 | CU-26 | RF-002 | Unitaria | Dos formas de tener alcance global. | RolesUnitTests.test_el_superusuario_y_el_usuario_maestro_cuentan_como_administrador | César Aranda | Aprobado |
| CP-TRA-043 | CU-26 | RF-002 | Unitaria | La migración crea los roles que consultan los permisos. | RolesUnitTests.test_existen_los_seis_roles_del_sistema | César Aranda | Aprobado |
| CP-TRA-044 | CU-26 | RF-002 | Unitaria | Y None si no hay sesión o ficha. | RolesUnitTests.test_funcionario_de_devuelve_su_funcionario | César Aranda | Aprobado |
| CP-TRA-045 | CU-26 | RF-002 | Unitaria | Un usuario con dos roles tiene ambos. | RolesUnitTests.test_los_roles_salen_del_funcionario | César Aranda | Aprobado |
| CP-TRA-048 | CU-26 | RF-002 | Unitaria | Desactivar al funcionario quita sus permisos. | RolesUnitTests.test_un_funcionario_inactivo_no_aporta_roles | César Aranda | Aprobado |
| CP-TRA-049 | CU-26 | RF-002 | Unitaria | is_active en falso corta el acceso. | RolesUnitTests.test_una_cuenta_desactivada_no_tiene_roles | César Aranda | Aprobado |
| CP-TRA-050 | CU-26 | RNF-004 | Unitaria | Textos para el usuario, no para el equipo de desarrollo. | SinTextosDeDesarrolloTests.test_ninguna_pantalla_muestra_codigos_internos | César Aranda | Aprobado |
| CP-ACT-009 | CU-26.1 | RF-002 | Unitaria | El formulario no ofrece delegaciones ajenas. | ActividadFormUnitTests.test_quien_tiene_delegacion_solo_registra_en_la_suya | César Aranda | Aprobado |
| CP-ALE-006 | CU-26.1 | RF-037 | Unitaria | Coordinación ve a todos, delegado a su delegación y funcionario a sí mismo. | AlertasDeAusenciaTests.test_cada_usuario_ve_solo_a_quienes_supervisa | César Aranda | Aprobado |
| CP-ALE-013 | CU-26.1 | RF-037 | Unitaria | Rural no ve el rojo del Centro. | AlertasDeAvanceTests.test_quien_tiene_delegacion_ve_solo_la_suya | César Aranda | Aprobado |
| CP-ALE-015 | CU-26.1 | RF-037 | Unitaria | Un verificador sin delegación no las ve. | AlertasDeAvanceTests.test_un_usuario_sin_delegacion_ni_alcance_global_no_recibe_alertas_de_avance | César Aranda | Aprobado |
| CP-ALE-026 | CU-26.1 | RF-037 | Unitaria | Un funcionario del Centro no se entera de los de Rural. | AlertasDeVencimientoTests.test_solo_alertan_los_compromisos_del_ambito_del_usuario | César Aranda | Aprobado |
| CP-COM-007 | CU-26.1 | RF-017 | Unitaria | Un funcionario no asigna a otros ni en otra delegación. | CompromisoFormUnitTests.test_quien_tiene_delegacion_solo_se_asigna_a_si_mismo_en_la_suya | César Aranda | Aprobado |
| CP-COM-047 | CU-26.1 | RF-016 | Unitaria | Aunque escriba la URL, una cuenta de consulta no agrega tareas. | TuboDeTrabajoUnitTests.test_consulta_no_puede_agregar_tareas | César Aranda | Aprobado |
| CP-DEL-001 | CU-26.1 | RF-029 | Unitaria | La delegación ajena no existe para él (404). | AmbitoDelDelegadoTests.test_el_delegado_no_abre_otra_delegacion | César Aranda | Aprobado |
| CP-DEL-005 | CU-26.1 | RF-029, RF-037 | Unitaria | Ninguna alerta menciona otra delegación. | AmbitoDelDelegadoTests.test_las_alertas_del_delegado_son_solo_de_su_delegacion | César Aranda | Aprobado |
| CP-DEL-007 | CU-26.1 | RF-029, RF-033 | Unitaria | Los cinco informes, en pantalla y en CSV, solo traen su delegación. | AmbitoDelDelegadoTests.test_los_informes_del_delegado_son_solo_de_su_delegacion | César Aranda | Aprobado |
| CP-DEL-008 | CU-26.1 | RF-029 | Unitaria | Actividad, evidencia, tarea y delegación ajenas no existen para él. | AmbitoDelDelegadoTests.test_los_registros_de_otra_delegacion_responden_404 | César Aranda | Aprobado |
| CP-DEL-014 | CU-26.1 | RF-002 | Unitaria | La gestión de delegados es de la coordinación. | CoordinacionDeDelegadosTests.test_el_delegado_no_entra_a_la_coordinacion | César Aranda | Aprobado |
| CP-DEL-018 | CU-26.1 | RF-002, RF-009 | Unitaria | Con el permiso, se confirma y la actividad se elimina. | EliminarActividadSoloCoordinacionTests.test_coordinador_y_administrador_eliminan_tras_confirmar | César Aranda | Aprobado |
| CP-DEL-019 | CU-26.1 | RF-002, RF-009 | Unitaria | Sin el permiso, el autor no elimina: el intento se audita. | EliminarActividadSoloCoordinacionTests.test_el_autor_funcionario_o_delegado_no_elimina_su_actividad | César Aranda | Aprobado |
| CP-DEL-020 | CU-26.1 | RF-002, RF-032 | Unitaria | La lista ofrece Eliminar solo a quien puede eliminar. | EliminarActividadSoloCoordinacionTests.test_el_boton_eliminar_solo_aparece_con_el_permiso | César Aranda | Aprobado |
| CP-DEL-034 | CU-26.1 | RF-016 | Unitaria | Una tarea de otra delegación no existe para el usuario. | ModificarEnSuPaginaTests.test_modificar_una_tarea_de_otra_delegacion_responde_404 | César Aranda | Aprobado |
| CP-INT-001 | CU-26.1, CU-29.1 | RF-002, RNF-004 | Integración | Acceso con identidad individual y resultados limitados al ámbito. | AccesoAutenticadoTests.test_coordinador_ve_compromisos_de_todas_las_delegaciones | César Aranda | Aprobado |
| CP-INT-002 | CU-26.1, CU-29.1 | RF-002, RNF-004 | Integración | Acceso con identidad individual y resultados limitados al ámbito. | AccesoAutenticadoTests.test_funcionario_solo_ve_compromisos_de_su_delegacion | César Aranda | Aprobado |
| CP-INT-003 | CU-26.1, CU-29.1 | RF-002, RNF-004 | Integración | Acceso con identidad individual y resultados limitados al ámbito. | AccesoAutenticadoTests.test_logout_invalida_la_sesion | César Aranda | Aprobado |
| CP-INT-004 | CU-26.1, CU-29.1 | RF-002, RNF-004 | Integración | Acceso con identidad individual y resultados limitados al ámbito. | AccesoAutenticadoTests.test_portada_y_territorio_siguen_publicos | César Aranda | Aprobado |
| CP-INT-005 | CU-26.1, CU-29.1 | RF-002, RNF-004 | Integración | Acceso con identidad individual y resultados limitados al ámbito. | AccesoAutenticadoTests.test_usuario_sin_funcionario_no_ve_compromisos | César Aranda | Aprobado |
| CP-INT-006 | CU-26.1, CU-29.1 | RF-002, RNF-004 | Integración | Acceso con identidad individual y resultados limitados al ámbito. | AccesoAutenticadoTests.test_vistas_internas_exigen_inicio_de_sesion | César Aranda | Aprobado |
| CP-INT-034 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable y accesos denegados auditados. | AuditoriaTests.test_consultar_un_registro_fuera_del_ambito_da_404_y_queda_registrado | César Aranda | Aprobado |
| CP-INT-035 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable y accesos denegados auditados. | AuditoriaTests.test_el_indice_de_mantenedores_enlaza_la_auditoria_solo_al_administrador | César Aranda | Aprobado |
| CP-INT-036 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable y accesos denegados auditados. | AuditoriaTests.test_la_consulta_de_auditoria_filtra_y_solo_la_ve_el_administrador | César Aranda | Aprobado |
| CP-INT-037 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable y accesos denegados auditados. | AuditoriaTests.test_modificar_lo_de_otro_sin_ser_responsable_ni_autor_queda_registrado | César Aranda | Aprobado |
| CP-INT-038 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable y accesos denegados auditados. | AuditoriaTests.test_sin_sesion_no_se_registra_acceso_denegado | César Aranda | Aprobado |
| CP-INT-039 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable y accesos denegados auditados. | AuditoriaTests.test_un_acceso_denegado_por_rol_queda_registrado | César Aranda | Aprobado |
| CP-INT-040 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable y accesos denegados auditados. | AuditoriaTests.test_un_codigo_inexistente_da_404_sin_registrar_acceso_denegado | César Aranda | Aprobado |
| CP-INT-041 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable y accesos denegados auditados. | AuditoriaTests.test_un_evento_registrado_no_se_modifica_ni_se_elimina | César Aranda | Aprobado |
| CP-INT-042 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable y accesos denegados auditados. | AuditoriaTests.test_un_rechazo_por_regla_de_negocio_no_cuenta_como_acceso_denegado | César Aranda | Aprobado |
| CP-INT-066 | CU-26.1 | RF-012, RNF-005 | Integración | El archivo de otra delegación no se entrega. | EvidenciaArchivoTests.test_un_funcionario_de_otra_delegacion_no_accede_y_queda_auditado | César Aranda | Aprobado |
| CP-INT-187 | CU-26.1 | RF-021 | Integración | El resumen no incluye otras delegaciones. | ResumenYActividadRecienteVistasTests.test_quien_tiene_delegacion_solo_ve_su_resumen | César Aranda | Aprobado |
| CP-ORG-019 | CU-26.1 | RF-002 | Unitaria | Evita que el administrador se bloquee a sí mismo. | FuncionarioFormUnitTests.test_el_actor_no_puede_desactivar_su_propia_cuenta | César Aranda | Aprobado |
| CP-SEG-002 | CU-26.1 | RF-002 | Unitaria | Permisos intermedios. | AccesoPorPerfilTests.test_el_coordinador_no_gestiona_usuarios_ni_perfiles | César Aranda | Aprobado |
| CP-SEG-003 | CU-26.1 | RF-002, RNF-004 | Unitaria | Sin mantenedores, perfiles ni auditoría. | AccesoPorPerfilTests.test_el_funcionario_no_entra_a_operaciones_criticas | César Aranda | Aprobado |
| CP-SEG-006 | CU-26.1 | RF-002, RF-029 | Unitaria | Seis mantenedores; sin usuarios ni auditoría. | AccesoPorPerfilTests.test_el_panel_coordinador_muestra_solo_los_mantenedores_autorizados | César Aranda | Aprobado |
| CP-SEG-010 | CU-26.1 | RF-002, RF-013 | Unitaria | Un delegado con perfil Funcionario no podría revisar: se rechaza. | GestionDeUsuariosTests.test_el_rol_delegado_exige_un_perfil_que_revise | César Aranda | Aprobado |
| CP-SEG-012 | CU-26.1 | RF-002 | Unitaria | El rol administrador exige el perfil Administrador. | GestionDeUsuariosTests.test_un_perfil_menor_que_el_rol_se_rechaza | César Aranda | Aprobado |
| CP-SEG-015 | CU-26.1 | RF-002, RF-013 | Unitaria | Sin el permiso del perfil, el rol no basta. | PerfilesTests.test_el_perfil_funcionario_no_revisa_aunque_tenga_rol_revisor | César Aranda | Aprobado |
| CP-SEG-018 | CU-26.1 | RF-002 | Unitaria | La migración 0019 da delete_actividad al Coordinador; Delegado y Funcionario no lo tienen. | PerfilesTests.test_solo_coordinador_y_administrador_tienen_permiso_de_eliminar_actividades | César Aranda | Aprobado |
| CP-TRA-007 | CU-26.1 | RF-002 | Unitaria | Otro funcionario recibe el mensaje de solo autor. | AlcanceUnitTests.test_solo_el_autor_o_la_coordinacion_modifican | César Aranda | Aprobado |
| CP-TRA-009 | CU-26.1 | RF-002 | Unitaria | Una cuenta sin ficha no consulta registros. | AlcanceUnitTests.test_un_usuario_sin_funcionario_no_ve_nada | César Aranda | Aprobado |
| CP-TRA-023 | CU-26.1 | RF-002 | Unitaria | El texto que ve el usuario. | DecoradorRolUnitTests.test_el_mensaje_de_permiso_es_el_definido | César Aranda | Aprobado |
| CP-TRA-024 | CU-26.1 | RF-036 | Unitaria | El intento nombra lo que se quiso ver. | DecoradorRolUnitTests.test_registrar_acceso_denegado_guarda_entidad_e_identificador | César Aranda | Aprobado |
| CP-TRA-025 | CU-26.1 | RF-036 | Unitaria | Sin identidad no hay a quién atribuir el intento. | DecoradorRolUnitTests.test_registrar_acceso_denegado_ignora_al_anonimo | César Aranda | Aprobado |
| CP-TRA-026 | CU-26.1 | RF-036 | Unitaria | Un rol insuficiente queda en la auditoría. | DecoradorRolUnitTests.test_sin_el_rol_redirige_y_registra_el_intento | César Aranda | Aprobado |
| CP-TRA-027 | CU-26.1 | RF-002 | Unitaria | El anónimo va al login y no deja auditoría. | DecoradorRolUnitTests.test_sin_sesion_redirige_al_login | César Aranda | Aprobado |
| CP-TRA-037 | CU-26.1 | RF-002 | Unitaria | Evita el bloqueo de quien administra. | MantenedoresUnitTests.test_nadie_desactiva_su_propia_cuenta | César Aranda | Aprobado |
| CP-TRA-038 | CU-26.1 | RF-002 | Unitaria | El perfil Coordinador no administra cuentas ni roles. | MantenedoresUnitTests.test_roles_y_funcionarios_son_solo_de_administracion | César Aranda | Aprobado |
| CP-TRA-047 | CU-26.1 | RF-002 | Unitaria | Sin sesión no hay permisos. | RolesUnitTests.test_un_anonimo_no_tiene_roles | César Aranda | Aprobado |
| CP-ACT-011 | CU-27 | RF-004 | Unitaria | Un tipo desactivado no se puede elegir en registros nuevos. | ActividadFormUnitTests.test_solo_se_ofrecen_tipos_de_atencion_activos | Por definir | Aprobado |
| CP-ORG-005 | CU-27 | RF-004 | Unitaria | Los registros anteriores conservan el elemento desactivado. | CatalogoUnitTests.test_desactivar_oculta_el_elemento_pero_no_toca_los_registros_historicos | Por definir | Aprobado |
| CP-ORG-008 | CU-27 | RF-004 | Unitaria | Un tipo inventado no es válido. | CatalogoUnitTests.test_el_tipo_debe_ser_uno_del_catalogo | Por definir | Aprobado |
| CP-TRA-033 | CU-27 | RF-004 | Unitaria | Desactivar conserva la fila. | MantenedoresUnitTests.test_cambiar_baja_de_delegacion_y_catalogo | Por definir | Aprobado |
| CP-ORG-006 | CU-27.1 | RF-004 | Unitaria | Un código repetido no se guarda. | CatalogoUnitTests.test_el_codigo_de_un_elemento_es_unico | Por definir | Aprobado |
| CP-ORG-007 | CU-27.1 | RF-004 | Unitaria | El mantenedor informa el código repetido. | CatalogoUnitTests.test_el_formulario_rechaza_un_codigo_duplicado | Por definir | Aprobado |
| CP-ORG-042 | CU-28 | RF-026 | Unitaria | Días que faltan para el término. | PeriodoPuroUnitTests.test_dias_restantes | Vinzenz Lafferte | Aprobado |
| CP-ORG-043 | CU-28 | RF-005 | Unitaria | Un rango invertido se rechaza. | PeriodoPuroUnitTests.test_la_fecha_de_termino_no_puede_ser_anterior_al_inicio | Vinzenz Lafferte | Aprobado |
| CP-ORG-048 | CU-28 | RF-005 | Unitaria | Inicio y término el mismo día es válido. | PeriodoPuroUnitTests.test_un_dia_de_duracion_es_valido | Vinzenz Lafferte | Aprobado |
| CP-ORG-049 | CU-28 | RF-005 | Unitaria | Al finalizar el ciclo el período se cierra. | PeriodoUnitTests.test_cerrar_periodo_cambia_el_estado | Vinzenz Lafferte | Aprobado |
| CP-ORG-050 | CU-28 | RF-007 | Unitaria | RN-006: el umbral es un porcentaje. | PeriodoUnitTests.test_el_formulario_exige_un_umbral_entre_0_y_100 | Vinzenz Lafferte | Aprobado |
| CP-ORG-051 | CU-28 | RF-005 | Unitaria | El mantenedor informa la fecha de término anterior. | PeriodoUnitTests.test_el_formulario_rechaza_fechas_invertidas | Vinzenz Lafferte | Aprobado |
| CP-ORG-052 | CU-28 | RF-005 | Unitaria | Septiembre tiene 30 días computables. | PeriodoUnitTests.test_guardar_calcula_los_dias_computables | Vinzenz Lafferte | Aprobado |
| CP-ORG-053 | CU-28 | RF-005 | Unitaria | Con 100 % el período se abre. | PeriodoUnitTests.test_iniciar_periodo_con_100_pasa_a_abierto | Vinzenz Lafferte | Aprobado |
| CP-ORG-054 | CU-28 | RF-006 | Unitaria | RN-001: cada cargo debe sumar exactamente 100 %. | PeriodoUnitTests.test_iniciar_periodo_exige_ponderaciones_que_sumen_100 | Vinzenz Lafferte | Aprobado |
| CP-ORG-057 | CU-28 | RF-005 | Unitaria | Un borrador no se cierra. | PeriodoUnitTests.test_solo_se_cierra_un_periodo_abierto | Vinzenz Lafferte | Aprobado |
| CP-ORG-058 | CU-28 | RF-005 | Unitaria | Un período abierto no se inicia otra vez. | PeriodoUnitTests.test_solo_se_inicia_un_periodo_en_borrador | Vinzenz Lafferte | Aprobado |
| CP-TRA-035 | CU-28 | RF-005 | Unitaria | Borrador se inicia, abierto se cierra, cerrado se reabre con motivo. | MantenedoresUnitTests.test_las_acciones_de_un_periodo_dependen_de_su_estado | Vinzenz Lafferte | Aprobado |
| CP-ACT-041 | CU-28.1 | RF-038 | Unitaria | RN-013: un período cerrado queda congelado. | ValidacionUnitTests.test_con_el_periodo_cerrado_los_indicadores_no_se_recalculan | Vinzenz Lafferte | Aprobado |
| CP-MED-023 | CU-28.1 | RF-038 | Unitaria | RN-013: los resultados cerrados no cambian. | CumplimientoUnitTests.test_no_se_genera_un_indicador_de_un_periodo_cerrado | Vinzenz Lafferte | Aprobado |
| CP-ORG-029 | CU-28.1 | RF-038 | Unitaria | RN-013 alcanza a los ítems del período. | ItemMedibleUnitTests.test_en_un_periodo_cerrado_no_se_crean_ni_modifican_items | Vinzenz Lafferte | Aprobado |
| CP-ORG-055 | CU-28.1 | RF-036, RF-038 | Unitaria | La reapertura es explícita y queda registrada. | PeriodoUnitTests.test_reabrir_deja_auditoria_y_sube_la_version_de_parametros | Vinzenz Lafferte | Aprobado |
| CP-ORG-056 | CU-28.1 | RF-036 | Unitaria | Sin motivo no hay reapertura. | PeriodoUnitTests.test_reabrir_exige_un_motivo | Vinzenz Lafferte | Aprobado |
| CP-ORG-059 | CU-28.1 | RF-038 | Unitaria | Un período abierto no se reabre. | PeriodoUnitTests.test_solo_se_reabre_un_periodo_cerrado | Vinzenz Lafferte | Aprobado |
| CP-ORG-060 | CU-28.1 | RF-038 | Unitaria | RN-013: tampoco se borra. | PeriodoUnitTests.test_un_periodo_cerrado_no_se_elimina | Vinzenz Lafferte | Aprobado |
| CP-ORG-061 | CU-28.1 | RF-038 | Unitaria | RN-013: guardar un cerrado se rechaza. | PeriodoUnitTests.test_un_periodo_cerrado_no_se_modifica | Vinzenz Lafferte | Aprobado |
| CP-TRA-004 | CU-28.1 | RF-038 | Unitaria | RN-013 alcanza a la edición de actividades. | AlcanceUnitTests.test_bloqueo_de_una_actividad_de_periodo_cerrado | Vinzenz Lafferte | Aprobado |
| CP-MED-036 | CU-29 | RF-032 | Unitaria | El período pedido se respeta. | PeriodoVigenteUnitTests.test_se_puede_elegir_otro_periodo_con_indicadores | Por definir | Aprobado |
| CP-MED-040 | CU-29 | RF-032 | Unitaria | Un id inexistente o con texto no rompe la pantalla. | PeriodoVigenteUnitTests.test_un_valor_invalido_cae_en_el_periodo_por_defecto | Por definir | Aprobado |
| CP-MED-046 | CU-29 | RF-032 | Unitaria | Buscar «rur» deja solo Rural. | ResultadosPorDelegacionUnitTests.test_se_filtra_por_texto | Por definir | Aprobado |
| CP-DEL-006 | CU-29.1 | RF-029, RF-032 | Unitaria | Medición, semáforo y resumen solo muestran su delegación. | AmbitoDelDelegadoTests.test_las_metricas_del_delegado_son_solo_de_su_delegacion | Por definir | Aprobado |
| CP-TRA-002 | CU-29.1 | RF-032 | Unitaria | Alcance global. | AlcanceUnitTests.test_administracion_y_coordinacion_ven_todas_las_actividades | Por definir | Aprobado |
| CP-TRA-005 | CU-29.1 | RF-032 | Unitaria | Alcance global en la agenda. | AlcanceUnitTests.test_los_compromisos_de_administracion_incluyen_todas_las_delegaciones | Por definir | Aprobado |
| CP-TRA-008 | CU-29.1 | RF-032 | Unitaria | Sin delegación, solo sus propias actividades. | AlcanceUnitTests.test_un_funcionario_sin_delegacion_solo_ve_lo_que_registro | Por definir | Aprobado |
| CP-TRA-046 | CU-29.1 | RF-032 | Unitaria | El resto queda limitado a su ámbito. | RolesUnitTests.test_solo_administracion_y_coordinacion_ven_todo | Por definir | Aprobado |
| CP-INT-180 | CU-30 | RF-033, RF-036 | Integración | La exportación deja su registro. | ResumenYActividadRecienteVistasTests.test_el_informe_de_actividad_reciente_exporta_csv_y_queda_auditado | Por definir | Aprobado |
| CP-TRA-011 | CU-30 | RF-036 | Unitaria | Un superusuario con registro maestro se atribuye al maestro. | AuditoriaUnitTests.test_el_usuario_maestro_tiene_prioridad_sobre_el_funcionario | Por definir | Aprobado |
| CP-TRA-012 | CU-30 | RF-036, RNF-004 | Unitaria | Los campos sensibles se excluyen. | AuditoriaUnitTests.test_las_contrasenas_no_quedan_en_la_auditoria | Por definir | Aprobado |
| CP-TRA-013 | CU-30 | RF-036 | Unitaria | Al crear solo hay valores nuevos. | AuditoriaUnitTests.test_los_cambios_de_un_formulario_nuevo_no_tienen_valor_anterior | Por definir | Aprobado |
| CP-TRA-014 | CU-30 | RF-036 | Unitaria | Los campos intactos no ensucian el registro. | AuditoriaUnitTests.test_los_cambios_de_una_edicion_traen_antes_y_despues_solo_de_lo_que_cambio | Por definir | Aprobado |
| CP-TRA-015 | CU-30 | RF-036 | Unitaria | Antes y después, con tildes sin escapar. | AuditoriaUnitTests.test_los_valores_se_guardan_como_json_legible | Por definir | Aprobado |
| CP-TRA-016 | CU-30 | RF-036 | Unitaria | Objetos y relaciones se guardan como texto. | AuditoriaUnitTests.test_plano_convierte_valores_a_tipos_guardables | Por definir | Aprobado |
| CP-TRA-019 | CU-30 | RF-036 | Unitaria | Quién, qué, sobre qué registro y cuándo. | AuditoriaUnitTests.test_un_evento_queda_a_nombre_del_funcionario | Por definir | Aprobado |
| CP-TRA-021 | CU-30 | RF-036 | Unitaria | Sin doble codificación. | AuditoriaUnitTests.test_un_texto_se_guarda_tal_cual_y_none_queda_vacio | Por definir | Aprobado |
| CP-TRA-017 | CU-30.1 | RNF-008 | Unitaria | Update y delete de un queryset se rechazan. | AuditoriaUnitTests.test_tampoco_se_modifica_ni_elimina_en_bloque | Por definir | Aprobado |
| CP-TRA-018 | CU-30.1 | RNF-008 | Unitaria | Ni individualmente. | AuditoriaUnitTests.test_un_evento_no_se_elimina | Por definir | Aprobado |
| CP-TRA-020 | CU-30.1 | RNF-008 | Unitaria | La auditoría no se reescribe. | AuditoriaUnitTests.test_un_evento_registrado_no_se_puede_guardar_de_nuevo | Por definir | Aprobado |
| CP-LOGIN-001 | HU-26 | RF-002, RNF-004 | Unitaria | Login con usuario y contraseña válidos | ValidarCredencialesTests.test_login_con_usuario_y_contrasena_validos | Por definir | Aprobado |
| CP-LOGIN-002 | HU-26 | RF-002, RNF-004 | Unitaria | Login con contraseña incorrecta | ValidarCredencialesTests.test_login_con_contrasena_incorrecta | Por definir | Aprobado |
| CP-LOGIN-003 | HU-26 | RF-002, RNF-004 | Unitaria | Login con usuario inexistente | ValidarCredencialesTests.test_login_con_usuario_inexistente | Por definir | Aprobado |
| CP-LOGIN-004 | HU-26 | RF-002, RNF-004 | Unitaria | Login con usuario vacío | ValidarCredencialesTests.test_login_con_usuario_vacio | Por definir | Aprobado |
| CP-LOGIN-005 | HU-26 | RF-002, RNF-004 | Unitaria | Login con contraseña vacía | ValidarCredencialesTests.test_login_con_contrasena_vacia | Por definir | Aprobado |
| CP-LOGIN-006 | HU-26 | RF-002, RNF-004 | Unitaria | Login con ambos campos vacíos | ValidarCredencialesTests.test_login_con_usuario_y_contrasena_vacios | Por definir | Aprobado |
| CP-LOGIN-007 | HU-26 | RF-002, RNF-004 | Unitaria | Login con usuario inactivo | ValidarCredencialesTests.test_login_con_usuario_inactivo | Por definir | Aprobado |
| CP-LOGIN-008 | HU-26 | RF-002, RNF-004 | Unitaria | Login con formato inválido: solo espacios, texto de inyección y usuario de 151 caracteres | ValidarCredencialesTests.test_login_con_formato_invalido | Por definir | Aprobado |
| CP-SEG-004 | HU-26 | RF-002, RF-028 | Unitaria | Cada perfil ve su propio panel. | AccesoPorPerfilTests.test_el_login_lleva_al_panel_de_cada_perfil | Por definir | Aprobado |
| CP-SEG-020 | HU-26 | RF-002 | Unitaria | El mensaje trae el enlace con el token y cuánto dura. | RecuperarContrasenaTests.test_el_correo_lleva_el_enlace_y_la_vigencia | Por definir | Aprobado |
| CP-SEG-021 | HU-26 | RF-002, RNF-004 | Unitaria | Tras usarlo, el token deja de ser válido. | RecuperarContrasenaTests.test_el_enlace_no_sirve_dos_veces | Por definir | Aprobado |
| CP-SEG-022 | HU-26 | RF-002, RNF-004 | Unitaria | Pasado PASSWORD_RESET_TIMEOUT el enlace ya no sirve. | RecuperarContrasenaTests.test_el_enlace_vence | Por definir | Aprobado |
| CP-SEG-023 | HU-26 | RF-002 | Unitaria | El enlace está en la pantalla de ingreso. | RecuperarContrasenaTests.test_el_login_ofrece_recuperar_la_contrasena | Por definir | Aprobado |
| CP-SEG-024 | HU-26 | RF-002, RNF-004 | Unitaria | Solicitud, correo, enlace, cambio y acceso. | RecuperarContrasenaTests.test_flujo_completo_de_recuperacion | Por definir | Aprobado |
| CP-SEG-025 | HU-26 | RF-002, RNF-004 | Unitaria | La respuesta es la misma exista o no la cuenta. | RecuperarContrasenaTests.test_un_correo_desconocido_no_envia_nada_ni_lo_revela | Por definir | Aprobado |
| CP-SEG-026 | HU-26 | RF-002, RNF-004 | Unitaria | Un token inventado no permite cambiar la contraseña. | RecuperarContrasenaTests.test_un_token_alterado_se_rechaza | Por definir | Aprobado |
| CP-SEG-027 | HU-26 | RF-002, RNF-004 | Unitaria | Desactivar la cuenta también corta la recuperación. | RecuperarContrasenaTests.test_una_cuenta_inactiva_no_recibe_enlace | Por definir | Aprobado |
| CP-INT-150 | - | - | Integración | Migrar copia y transforma los datos | MigracionDatosTests.test_migrar_copia_y_transforma_los_datos | Por definir | Aprobado |
| CP-INT-151 | - | - | Integración | Revertir deja los datos como antes | MigracionDatosTests.test_revertir_deja_los_datos_como_antes | Por definir | Aprobado |
| CP-INT-152 | - | - | Integración | Renombra crea el delegado y mueve a los revisores | MigracionPerfilesPorJerarquiaTests.test_renombra_crea_el_delegado_y_mueve_a_los_revisores | Por definir | Aprobado |
| CP-INT-153 | - | - | Integración | Correccion pasa a rechazada conservando la observacion | MigracionSinCorreccionTests.test_correccion_pasa_a_rechazada_conservando_la_observacion | Por definir | Aprobado |
| CP-INT-196 | - | - | Integración | Carga el modelo nuevo con sus datos de demostracion | SeedDemoTests.test_carga_el_modelo_nuevo_con_sus_datos_de_demostracion | Por definir | Aprobado |
| CP-INT-197 | - | - | Integración | Convive con datos ya migrados sin duplicarlos | SeedDemoTests.test_convive_con_datos_ya_migrados_sin_duplicarlos | Por definir | Aprobado |
| CP-INT-198 | - | - | Integración | Cuentas demo y delegados inactivos | SeedDemoTests.test_cuentas_demo_y_delegados_inactivos | Por definir | Aprobado |
| CP-INT-199 | - | - | Integración | La demo se ve en la aplicacion | SeedDemoTests.test_la_demo_se_ve_en_la_aplicacion | Por definir | Aprobado |
| CP-INT-200 | - | - | Integración | Repetir la carga no duplica nada | SeedDemoTests.test_repetir_la_carga_no_duplica_nada | Por definir | Aprobado |
| CP-PLAN-001 | - | - | Unitaria | Cobertura distingue prueba propia subcasos y sin prueba | ArmadoDelPlanTests.test_cobertura_distingue_prueba_propia_subcasos_y_sin_prueba | Por definir | Aprobado |
| CP-PLAN-002 | - | - | Unitaria | Cobertura por rf cuenta unitarias e integracion | ArmadoDelPlanTests.test_cobertura_por_rf_cuenta_unitarias_e_integracion | Por definir | Aprobado |
| CP-PLAN-003 | - | - | Unitaria | El catalogo tiene los casos de uso y los 38 requisitos | ArmadoDelPlanTests.test_el_catalogo_tiene_los_casos_de_uso_y_los_38_requisitos | Por definir | Aprobado |
| CP-PLAN-004 | - | - | Unitaria | El documento incluye resumen tabla y fichas de login | ArmadoDelPlanTests.test_el_documento_incluye_resumen_tabla_y_fichas_de_login | Por definir | Aprobado |
| CP-PLAN-005 | - | - | Unitaria | Hay una ficha por cada caso de login | ArmadoDelPlanTests.test_hay_una_ficha_por_cada_caso_de_login | Por definir | Aprobado |
| CP-PLAN-006 | - | - | Unitaria | Los cp se asignan por modulo y respetan los declarados | ArmadoDelPlanTests.test_los_cp_se_asignan_por_modulo_y_respetan_los_declarados | Por definir | Aprobado |
| CP-PLAN-007 | - | - | Unitaria | El docstring de un metodo define cp cu nombre y requisitos | LecturaDeDocstringsTests.test_el_docstring_de_un_metodo_define_cp_cu_nombre_y_requisitos | Por definir | Aprobado |
| CP-PLAN-008 | - | - | Unitaria | Los cu se ordenan de forma natural | LecturaDeDocstringsTests.test_los_cu_se_ordenan_de_forma_natural | Por definir | Aprobado |
| CP-PLAN-009 | - | - | Unitaria | Los requisitos se leen y los rangos se expanden | LecturaDeDocstringsTests.test_los_requisitos_se_leen_y_los_rangos_se_expanden | Por definir | Aprobado |
| CP-PLAN-010 | - | - | Unitaria | Sin docstring de metodo se usa el de la clase | LecturaDeDocstringsTests.test_sin_docstring_de_metodo_se_usa_el_de_la_clase | Por definir | Aprobado |
| CP-PLAN-011 | - | - | Unitaria | Sin ningun docstring valido la prueba queda sin cu | LecturaDeDocstringsTests.test_sin_ningun_docstring_valido_la_prueba_queda_sin_cu | Por definir | Aprobado |
| CP-PLAN-012 | - | - | Unitaria | Un metodo sin cp declarado lo deja para asignar | LecturaDeDocstringsTests.test_un_metodo_sin_cp_declarado_lo_deja_para_asignar | Por definir | Aprobado |
| CP-PLAN-013 | - | - | Unitaria | Un rnf no se confunde con un rf | LecturaDeDocstringsTests.test_un_rnf_no_se_confunde_con_un_rf | Por definir | Aprobado |
| CP-PLAN-014 | - | - | Unitaria | El responsable sale de la familia del primer caso de uso | ResponsablesTests.test_el_responsable_sale_de_la_familia_del_primer_caso_de_uso | Por definir | Aprobado |
| CP-PLAN-015 | - | - | Unitaria | Las fichas de login ya no dicen a completar | ResponsablesTests.test_las_fichas_de_login_ya_no_dicen_a_completar | Por definir | Aprobado |
| CP-PLAN-016 | - | - | Unitaria | Sin asignacion queda por definir | ResponsablesTests.test_sin_asignacion_queda_por_definir | Por definir | Aprobado |

## 6. Fichas de los casos de login

Siguen el formato del plan de pruebas del curso. La unidad probada es el formulario de autenticación `AuthenticationForm`, que usa `LoginView`.

### CP-LOGIN-001

| Campo | Detalle |
|---|---|
| ID Caso de Prueba | CP-LOGIN-001 |
| Módulo | Autenticación |
| Unidad a probar | AuthenticationForm (validación de credenciales) |
| Nombre | Login con usuario y contraseña válidos |
| Objetivo | Verificar que se autentique a un usuario registrado y activo. |
| Precondiciones | El usuario de prueba está registrado (activo salvo en el caso 007). |
| Datos de entrada | Usuario: usuario.prueba / Contraseña: la registrada |
| Pasos | 1. Construir el formulario con los datos. 2. Validarlo. 3. Revisar errores y usuario obtenido. |
| Resultado esperado | El formulario es válido y entrega el usuario autenticado. |
| Resultado obtenido | Coincide con lo esperado. |
| Estado | ☒ Aprobado ☐ Reprobado ☐ No ejecutado |
| Responsable | Por definir |
| Fecha ejecución | 31-10-2026 |
| Observaciones | Prueba `ValidarCredencialesTests.test_login_con_usuario_y_contrasena_validos`. |

### CP-LOGIN-002

| Campo | Detalle |
|---|---|
| ID Caso de Prueba | CP-LOGIN-002 |
| Módulo | Autenticación |
| Unidad a probar | AuthenticationForm (validación de credenciales) |
| Nombre | Login con contraseña incorrecta |
| Objetivo | Verificar que se rechace una contraseña incorrecta para un usuario existente. |
| Precondiciones | El usuario de prueba está registrado (activo salvo en el caso 007). |
| Datos de entrada | Usuario: usuario.prueba / Contraseña: otra-clave |
| Pasos | 1. Construir el formulario con los datos. 2. Validarlo. 3. Revisar errores y usuario obtenido. |
| Resultado esperado | El formulario es inválido, informa credenciales inválidas y no entrega usuario. |
| Resultado obtenido | Coincide con lo esperado. |
| Estado | ☒ Aprobado ☐ Reprobado ☐ No ejecutado |
| Responsable | Por definir |
| Fecha ejecución | 31-10-2026 |
| Observaciones | Prueba `ValidarCredencialesTests.test_login_con_contrasena_incorrecta`. |

### CP-LOGIN-003

| Campo | Detalle |
|---|---|
| ID Caso de Prueba | CP-LOGIN-003 |
| Módulo | Autenticación |
| Unidad a probar | AuthenticationForm (validación de credenciales) |
| Nombre | Login con usuario inexistente |
| Objetivo | Verificar que se rechace un usuario que no está registrado. |
| Precondiciones | El usuario de prueba está registrado (activo salvo en el caso 007). |
| Datos de entrada | Usuario: no.existe / Contraseña: cualquiera |
| Pasos | 1. Construir el formulario con los datos. 2. Validarlo. 3. Revisar errores y usuario obtenido. |
| Resultado esperado | El formulario es inválido, con el mismo mensaje genérico de credenciales inválidas. |
| Resultado obtenido | Coincide con lo esperado. |
| Estado | ☒ Aprobado ☐ Reprobado ☐ No ejecutado |
| Responsable | Por definir |
| Fecha ejecución | 31-10-2026 |
| Observaciones | Prueba `ValidarCredencialesTests.test_login_con_usuario_inexistente`. |

### CP-LOGIN-004

| Campo | Detalle |
|---|---|
| ID Caso de Prueba | CP-LOGIN-004 |
| Módulo | Autenticación |
| Unidad a probar | AuthenticationForm (validación de credenciales) |
| Nombre | Login con usuario vacío |
| Objetivo | Verificar que el usuario sea obligatorio. |
| Precondiciones | El usuario de prueba está registrado (activo salvo en el caso 007). |
| Datos de entrada | Usuario: (vacío) / Contraseña: válida |
| Pasos | 1. Construir el formulario con los datos. 2. Validarlo. 3. Revisar errores y usuario obtenido. |
| Resultado esperado | El formulario es inválido y señala solo el campo usuario como obligatorio. |
| Resultado obtenido | Coincide con lo esperado. |
| Estado | ☒ Aprobado ☐ Reprobado ☐ No ejecutado |
| Responsable | Por definir |
| Fecha ejecución | 31-10-2026 |
| Observaciones | Prueba `ValidarCredencialesTests.test_login_con_usuario_vacio`. |

### CP-LOGIN-005

| Campo | Detalle |
|---|---|
| ID Caso de Prueba | CP-LOGIN-005 |
| Módulo | Autenticación |
| Unidad a probar | AuthenticationForm (validación de credenciales) |
| Nombre | Login con contraseña vacía |
| Objetivo | Verificar que la contraseña sea obligatoria. |
| Precondiciones | El usuario de prueba está registrado (activo salvo en el caso 007). |
| Datos de entrada | Usuario: usuario.prueba / Contraseña: (vacía) |
| Pasos | 1. Construir el formulario con los datos. 2. Validarlo. 3. Revisar errores y usuario obtenido. |
| Resultado esperado | El formulario es inválido y señala solo el campo contraseña como obligatorio. |
| Resultado obtenido | Coincide con lo esperado. |
| Estado | ☒ Aprobado ☐ Reprobado ☐ No ejecutado |
| Responsable | Por definir |
| Fecha ejecución | 31-10-2026 |
| Observaciones | Prueba `ValidarCredencialesTests.test_login_con_contrasena_vacia`. |

### CP-LOGIN-006

| Campo | Detalle |
|---|---|
| ID Caso de Prueba | CP-LOGIN-006 |
| Módulo | Autenticación |
| Unidad a probar | AuthenticationForm (validación de credenciales) |
| Nombre | Login con ambos campos vacíos |
| Objetivo | Verificar que ambos campos sean obligatorios. |
| Precondiciones | El usuario de prueba está registrado (activo salvo en el caso 007). |
| Datos de entrada | Usuario: (vacío) / Contraseña: (vacía) |
| Pasos | 1. Construir el formulario con los datos. 2. Validarlo. 3. Revisar errores y usuario obtenido. |
| Resultado esperado | El formulario es inválido y señala los dos campos. |
| Resultado obtenido | Coincide con lo esperado. |
| Estado | ☒ Aprobado ☐ Reprobado ☐ No ejecutado |
| Responsable | Por definir |
| Fecha ejecución | 31-10-2026 |
| Observaciones | Prueba `ValidarCredencialesTests.test_login_con_usuario_y_contrasena_vacios`. |

### CP-LOGIN-007

| Campo | Detalle |
|---|---|
| ID Caso de Prueba | CP-LOGIN-007 |
| Módulo | Autenticación |
| Unidad a probar | AuthenticationForm (validación de credenciales) |
| Nombre | Login con usuario inactivo |
| Objetivo | Verificar que una cuenta desactivada no pueda iniciar sesión. |
| Precondiciones | El usuario de prueba está registrado (activo salvo en el caso 007). |
| Datos de entrada | Usuario: usuario.prueba con is_active falso / Contraseña: válida |
| Pasos | 1. Construir el formulario con los datos. 2. Validarlo. 3. Revisar errores y usuario obtenido. |
| Resultado esperado | El formulario es inválido y authenticate() no devuelve usuario. |
| Resultado obtenido | Coincide con lo esperado. |
| Estado | ☒ Aprobado ☐ Reprobado ☐ No ejecutado |
| Responsable | Por definir |
| Fecha ejecución | 31-10-2026 |
| Observaciones | Prueba `ValidarCredencialesTests.test_login_con_usuario_inactivo`. |

### CP-LOGIN-008

| Campo | Detalle |
|---|---|
| ID Caso de Prueba | CP-LOGIN-008 |
| Módulo | Autenticación |
| Unidad a probar | AuthenticationForm (validación de credenciales) |
| Nombre | Login con formato inválido |
| Objetivo | Verificar el rechazo de entradas con formato inválido. |
| Precondiciones | El usuario de prueba está registrado (activo salvo en el caso 007). |
| Datos de entrada | Usuarios: «' OR '1'='1», 151 caracteres, «<script>…</script>» y solo espacios |
| Pasos | 1. Construir el formulario con los datos. 2. Validarlo. 3. Revisar errores y usuario obtenido. |
| Resultado esperado | Todos se rechazan sin error del sistema y sin entregar usuario; los espacios señalan el campo usuario. |
| Resultado obtenido | Coincide con lo esperado. |
| Estado | ☒ Aprobado ☐ Reprobado ☐ No ejecutado |
| Responsable | Por definir |
| Fecha ejecución | 31-10-2026 |
| Observaciones | Prueba `ValidarCredencialesTests.test_login_con_formato_invalido`. |
