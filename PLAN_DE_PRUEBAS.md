# Plan de pruebas del Sistema de Gestión de Delegaciones

Generado con `python manage.py plan_pruebas` a partir de los docstrings de las pruebas y de su ejecución. No se edita a mano: se vuelve a generar.

## 1. Identificación del documento

| Campo | Información |
|---|---|
| Nombre del proyecto | Sistema de Gestión de Delegaciones |
| Tipo de pruebas | Unitarias y de integración |
| Versión | 1.0 |
| Fecha | 21-10-2026 |
| Ambiente de pruebas | Desarrollo, base de datos de pruebas (sqlite) |
| Tecnología utilizada | Python 3.14.4, Django 5.2.18, unittest de Django |

## 2. Resumen de resultados

| Concepto | Cantidad |
|---|---|
| Pruebas ejecutadas | 442 |
| Unitarias | 250 |
| De integración | 192 |
| Aprobadas | 442 |
| Reprobadas o con error | 0 |

## 3. Cobertura por caso de uso

Los casos de uso son los de la especificación detallada (CU-01 a CU-30). «Cubierto por sus subcasos» indica que el caso base no tiene pruebas propias pero sí sus extensiones.

| CU | Nombre | Unitarias | Integración (por clase) | Situación |
|---|---|---|---|---|
| CU-01 | Registro de actividades | 2 | 31 | Aprobado |
| CU-01.1 | Validar campos de actividad | 7 | 19 | Aprobado |
| CU-01.2 | Gestionar error de validación | 5 | 19 | Aprobado |
| CU-02 | Registro de compromisos ciudadanos | 1 | 6 | Aprobado |
| CU-02.1 | Validar datos de compromiso | 3 | 0 | Aprobado |
| CU-02.2 | Bloquear guardado por campos faltantes | 3 | 0 | Aprobado |
| CU-02.3 | Destacar compromiso vencido | 1 | 13 | Aprobado |
| CU-04 | Administración de funciones por cargo | 1 | 26 | Aprobado |
| CU-04.1 | Validar reglas de configuración | 4 | 0 | Aprobado |
| CU-04.2 | Bloquear guardado por ponderación inválida | 3 | 0 | Aprobado |
| CU-05 | Definición de metas | 1 | 15 | Aprobado |
| CU-05.1 | Validar parámetros de meta | 1 | 0 | Aprobado |
| CU-05.2 | Bloquear guardado por valor inválido | 2 | 0 | Aprobado |
| CU-05.3 | Notificar período cerrado | 1 | 0 | Aprobado |
| CU-06 | Seguimiento de avance | 5 | 12 | Aprobado |
| CU-06.1 | Recalcular indicadores automáticamente | 2 | 15 | Aprobado |
| CU-06.2 | Destacar meta cumplida | 1 | 12 | Aprobado |
| CU-07 | Cálculo automático de cumplimiento | 0 | 15 | Aprobado |
| CU-07.1 | Aplicar fórmulas de medición | 10 | 0 | Aprobado |
| CU-07.2 | Recalcular por anulación de registro | 2 | 8 | Aprobado |
| CU-07.3 | Mostrar detalle en reporte | 3 | 12 | Aprobado |
| CU-09 | Registro de evidencia fotográfica | 3 | 0 | Aprobado |
| CU-09.1 | Validar archivo de evidencia | 2 | 0 | Aprobado |
| CU-09.2 | Rechazar carga inválida | 3 | 5 | Aprobado |
| CU-10 | Generación de códigos verificadores | 3 | 31 | Aprobado |
| CU-10.1 | Buscar actividad por código | 1 | 19 | Aprobado |
| CU-10.2 | Consulta sin coincidencias | 1 | 19 | Aprobado |
| CU-11 | Validación de actividades | 5 | 20 | Aprobado |
| CU-11.1 | Registrar trazabilidad de decisión | 2 | 8 | Aprobado |
| CU-11.2 | Bloquear aporte al avance | 7 | 8 | Aprobado |
| CU-12 | Agenda compartida | 1 | 6 | Aprobado |
| CU-12.1 | Filtrar agenda compartida | 5 | 0 | Aprobado |
| CU-12.2 | Consulta sin coincidencias en agenda | 1 | 0 | Aprobado |
| CU-13 | Actualización de estados | 5 | 19 | Aprobado |
| CU-13.1 | Registrar historial de cambio de estado | 4 | 6 | Aprobado |
| CU-13.2 | Reflejar cierre de compromiso | 3 | 0 | Aprobado |
| CU-14 | Seguimiento de compromisos | 0 | 0 | Cubierto por sus subcasos |
| CU-14.1 | Clasificar compromisos por vencimiento | 3 | 0 | Aprobado |
| CU-14.2 | Generar alerta por vencimiento próximo | 4 | 13 | Aprobado |
| CU-16 | Semáforo de cumplimiento | 1 | 10 | Aprobado |
| CU-16.1 | Calcular estado del semáforo | 2 | 25 | Aprobado |
| CU-17 | Comparación entre avance esperado y real | 0 | 22 | Aprobado |
| CU-17.1 | Calcular diferencia de avance | 3 | 0 | Aprobado |
| CU-17.2 | Destacar desviación significativa | 1 | 12 | Aprobado |
| CU-18 | Resumen ejecutivo | 6 | 10 | Aprobado |
| CU-18.1 | Consolidar datos de delegación | 4 | 10 | Aprobado |
| CU-18.2 | Navegar al detalle de gestión | 1 | 0 | Aprobado |
| CU-20 | Generación de informes | 1 | 15 | Aprobado |
| CU-20.1 | Consolidar datos filtrados | 4 | 15 | Aprobado |
| CU-20.2 | Restringir por ámbito de permisos | 1 | 15 | Aprobado |
| CU-23 | Trabajo colaborativo en línea | 0 | 0 | Cubierto por sus subcasos |
| CU-23.1 | Controlar conflicto de concurrencia | 5 | 18 | Aprobado |
| CU-25 | Modificar parámetros | 5 | 26 | Aprobado |
| CU-26 | Administración de delegaciones, usuarios y roles | 26 | 44 | Aprobado |
| CU-26.1 | Denegar acceso por ámbito | 13 | 26 | Aprobado |
| CU-27 | Administración de catálogos | 4 | 26 | Aprobado |
| CU-27.1 | Restringir elemento duplicado | 2 | 26 | Aprobado |
| CU-28 | Administración de períodos | 12 | 26 | Aprobado |
| CU-28.1 | Restricción por período cerrado | 9 | 15 | Aprobado |
| CU-29 | Búsqueda y filtros | 3 | 15 | Aprobado |
| CU-29.1 | Restricción de búsqueda por ámbito | 4 | 6 | Aprobado |
| CU-30 | Auditoría de cambios | 8 | 22 | Aprobado |
| CU-30.1 | Bloqueo por alteración no autorizada | 3 | 12 | Aprobado |

Casos de uso sin ninguna prueba: ninguno.

## 4. Cobertura por requisito funcional

En las pruebas de integración el CU y los RF se declaran por clase, así que cada prueba de la clase cuenta para todos los que la clase cita.

| RF | Requisito | Unitarias | Integración (por clase) | Situación | Observación |
|---|---|---|---|---|---|
| RF-001 | Administrar delegaciones | 6 | 36 | Aprobado |  |
| RF-002 | Administrar usuarios y roles | 37 | 50 | Aprobado |  |
| RF-003 | Configurar cargos y funciones | 1 | 26 | Aprobado |  |
| RF-004 | Mantener catálogo de actividades y servicios | 6 | 26 | Aprobado |  |
| RF-005 | Configurar períodos de medición | 9 | 41 | Aprobado |  |
| RF-006 | Configurar ponderaciones | 8 | 41 | Aprobado |  |
| RF-007 | Configurar metas y umbrales | 6 | 41 | Aprobado |  |
| RF-008 | Presentar ficha personal | 3 | 12 | Aprobado |  |
| RF-009 | Registrar actividades | 3 | 31 | Aprobado |  |
| RF-010 | Validar campos de actividad | 10 | 19 | Aprobado |  |
| RF-011 | Generar código verificador de evidencia | 3 | 31 | Aprobado |  |
| RF-012 | Asociar evidencia | 7 | 5 | Aprobado |  |
| RF-013 | Validar evidencia | 6 | 20 | Aprobado |  |
| RF-014 | Controlar puntuación por validación | 6 | 20 | Aprobado |  |
| RF-015 | Registrar atención social por etapas | 0 | 0 | Sin prueba | No implementado: no existe el registro de atenciones sociales por etapas. |
| RF-016 | Crear compromisos en agenda colectiva | 1 | 6 | Aprobado |  |
| RF-017 | Asignar compromiso | 9 | 6 | Aprobado |  |
| RF-018 | Gestionar estados | 10 | 19 | Aprobado |  |
| RF-019 | Controlar plazos | 9 | 13 | Aprobado |  |
| RF-020 | Relacionar agenda y medición | 0 | 0 | Sin prueba | No implementado: cerrar un compromiso no alimenta el indicador del ítem; solo cuentan las actividades aprobadas. |
| RF-021 | Generar resumen colectivo | 0 | 0 | Sin prueba | Parcial: la agenda totaliza por estado y plazo, pero no por funcionario ni muestra porcentajes. |
| RF-022 | Calcular avance actual | 13 | 23 | Aprobado |  |
| RF-023 | Calcular porcentaje de cumplimiento | 3 | 23 | Aprobado |  |
| RF-024 | Calcular cumplimiento ponderado | 6 | 15 | Aprobado |  |
| RF-025 | Aplicar incentivos y penalizaciones | 0 | 0 | Sin prueba | No implementado: el campo ajuste del indicador se guarda pero no entra al cálculo. |
| RF-026 | Calcular meta esperada al día | 5 | 25 | Aprobado |  |
| RF-027 | Mostrar semáforo de avance | 3 | 25 | Aprobado |  |
| RF-028 | Mostrar tablero personal | 3 | 22 | Aprobado |  |
| RF-029 | Mostrar tablero de delegación | 9 | 10 | Aprobado |  |
| RF-030 | Medir actividad reciente | 1 | 0 | Aprobado | Parcial: informa fecha del último cálculo y días transcurridos; faltan cantidad de registros y promedio diario. |
| RF-031 | Mostrar vista global por cargos | 0 | 0 | Sin prueba | No implementado: no hay vista global por cargos. |
| RF-032 | Buscar y filtrar información | 17 | 15 | Aprobado |  |
| RF-033 | Generar y exportar informes | 5 | 15 | Aprobado |  |
| RF-034 | Permitir trabajo simultáneo | 5 | 18 | Aprobado |  |
| RF-035 | Facilitar coordinación | 0 | 0 | Sin prueba | No implementado: no hay observaciones o comentarios asociados a registros. |
| RF-036 | Mantener trazabilidad | 13 | 22 | Aprobado |  |
| RF-037 | Emitir alertas | 2 | 0 | Aprobado | Parcial: solo alerta por vencimiento de compromisos; faltan evidencias pendientes, ausencia de registros y avance bajo el umbral. |
| RF-038 | Versionar parámetros | 14 | 0 | Aprobado |  |

Requisitos sin ninguna prueba: RF-015, RF-020, RF-021, RF-025, RF-031, RF-035

## 5. Tabla de casos de prueba

Una fila por prueba. La columna CU lista los casos de uso que verifica y RF los requisitos (RNF y RN cuando aplican). En las pruebas de integración, CU y RF son los de su clase.

| CP | CU | RF | Método de prueba | Prueba | Unidad probada | Resultado |
|---|---|---|---|---|---|---|
| CP-ACT-025 | CU-01 | RF-009 | Unitaria | El registro válido queda pendiente de revisión con su código. | ActividadUnitTests.test_registrar_actividad_guarda_con_codigo_y_estado_pendiente | Aprobado |
| CP-ACT-027 | CU-01 | RF-009 | Unitaria | Sin delegación indicada se usa la del autor. | ActividadUnitTests.test_registrar_actividad_usa_la_delegacion_del_funcionario_si_falta | Aprobado |
| CP-INT-007 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_actividad_aprobada_no_admite_nuevas_evidencias | Aprobado |
| CP-INT-008 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_actividad_aprobada_no_se_edita_ni_se_elimina | Aprobado |
| CP-INT-009 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_actividad_de_un_periodo_cerrado_no_se_modifica | Aprobado |
| CP-INT-010 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_autor_edita_su_actividad_y_audita | Aprobado |
| CP-INT-011 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_coordinador_puede_modificar_actividad_ajena | Aprobado |
| CP-INT-012 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_edicion_concurrente_se_rechaza_con_la_version_desactualizada | Aprobado |
| CP-INT-013 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_editar_actividad_rechazada_la_devuelve_a_revision_con_sus_evidencias | Aprobado |
| CP-INT-014 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_el_formulario_ofrece_solo_los_items_del_cargo_del_funcionario | Aprobado |
| CP-INT-015 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_eliminar_requiere_confirmacion_post_y_borra_sus_evidencias | Aprobado |
| CP-INT-016 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_evidencia_rechaza_extension_no_permitida | Aprobado |
| CP-INT-017 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_funcionario_de_la_misma_delegacion_que_no_es_autor_no_puede_modificar | Aprobado |
| CP-INT-018 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_funcionario_de_otra_delegacion_no_puede_editar_ni_eliminar | Aprobado |
| CP-INT-019 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_funcionario_ve_solo_su_delegacion | Aprobado |
| CP-INT-020 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_listado_enlaza_modificar_y_eliminar_reales | Aprobado |
| CP-INT-021 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_rechaza_una_fecha_fuera_del_periodo_del_item | Aprobado |
| CP-INT-022 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_registrar_actividad_genera_codigo_y_auditoria | Aprobado |
| CP-INT-023 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_subir_evidencia_la_envia_a_revision_y_audita | Aprobado |
| CP-INT-024 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_usuario_sin_funcionario_no_puede_registrar | Aprobado |
| CP-INT-025 | CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 | RF-009, RF-010, RF-011 | Integración | Registro, consulta, modificación y eliminación de actividades. | ActividadVistasTests.test_verificador_sin_delegacion_ve_todas_las_actividades | Aprobado |
| CP-INT-154 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_actividad_aprobada_no_cambia_de_estado | Aprobado |
| CP-INT-155 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_compromiso_cambios_quedan_en_el_historial | Aprobado |
| CP-INT-156 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_compromiso_version_optimista | Aprobado |
| CP-INT-157 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_indicador_generar_calcula_y_guarda | Aprobado |
| CP-INT-158 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_rechazo_y_correccion_exigen_texto_y_numeran_revisiones | Aprobado |
| CP-INT-159 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_registrar_actividad_fuera_del_periodo_o_con_periodo_cerrado | Aprobado |
| CP-INT-160 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_registrar_actividad_genera_codigo_y_toma_la_delegacion_del_autor | Aprobado |
| CP-INT-161 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_rn009_solo_la_validacion_aprobada_aporta_al_avance | Aprobado |
| CP-INT-162 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_rn010_codigo_verificador_inmutable | Aprobado |
| CP-INT-163 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_subir_evidencia_genera_codigos_y_envia_a_revision | Aprobado |
| CP-INT-164 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_subir_evidencia_rechaza_extension_no_permitida | Aprobado |
| CP-INT-165 | CU-01, CU-10, CU-11, CU-23.1 | RF-009, RF-011, RF-013, RF-014, RF-034 | Integración | RN-009, RN-010, control de versión y métodos de operación. | OperacionTests.test_version_optimista_rechaza_la_edicion_concurrente | Aprobado |
| CP-ACT-010 | CU-01.1 | RF-009 | Unitaria | Los ítems de otro cargo o de períodos cerrados no aparecen. | ActividadFormUnitTests.test_solo_se_ofrecen_items_de_periodos_abiertos_y_del_cargo_del_usuario | Aprobado |
| CP-ACT-012 | CU-01.1 | RF-010 | Unitaria | Con todos los datos obligatorios no hay errores. | ActividadFormUnitTests.test_un_formulario_completo_es_valido | Aprobado |
| CP-ACT-019 | CU-01.1 | RF-010 | Unitaria | Dígitos, espacios, guiones y paréntesis; + o paréntesis inicial opcional. | ActividadUnitTests.test_el_telefono_de_contacto_debe_tener_un_formato_valido | Aprobado |
| CP-ACT-020 | CU-01.1 | RF-010 | Unitaria | Sin teléfono el registro es válido. | ActividadUnitTests.test_el_telefono_es_opcional | Aprobado |
| CP-ACT-021 | CU-01.1 | RF-010 | Unitaria | Una fecha fuera del período se rechaza. | ActividadUnitTests.test_la_fecha_debe_estar_dentro_del_periodo_del_item | Aprobado |
| CP-ACT-023 | CU-01.1 | RF-010 | Unitaria | El primer y el último día del período se aceptan. | ActividadUnitTests.test_los_limites_del_periodo_son_validos | Aprobado |
| CP-ACT-024 | CU-01.1 | RF-038 | Unitaria | RN-013: el ítem de un período cerrado no admite actividades. | ActividadUnitTests.test_no_se_registra_en_un_periodo_cerrado | Aprobado |
| CP-ACT-007 | CU-01.2 | RF-010 | Unitaria | Vacío cada obligatorio, el error apunta a ese campo. | ActividadFormUnitTests.test_cada_campo_obligatorio_se_informa | Aprobado |
| CP-ACT-008 | CU-01.2 | RF-010 | Unitaria | Una fecha mal escrita no se guarda. | ActividadFormUnitTests.test_el_formato_de_fecha_invalido_se_informa | Aprobado |
| CP-ACT-013 | CU-01.2 | RF-010 | Unitaria | El error del teléfono aparece en su campo. | ActividadFormUnitTests.test_un_telefono_invalido_se_informa_en_el_formulario | Aprobado |
| CP-ACT-022 | CU-01.2 | RF-010 | Unitaria | El error nombra cada campo faltante. | ActividadUnitTests.test_los_campos_obligatorios_se_informan_por_nombre | Aprobado |
| CP-ACT-026 | CU-01.2 | RF-010 | Unitaria | Un registro con errores no se guarda. | ActividadUnitTests.test_registrar_actividad_invalida_no_guarda_nada | Aprobado |
| CP-COM-003 | CU-02 | RF-017 | Unitaria | Quien ve todo elige entre los funcionarios activos. | CompromisoFormUnitTests.test_coordinacion_asigna_a_cualquier_funcionario_activo | Aprobado |
| CP-INT-063 | CU-02, CU-12, CU-13, CU-13.1, CU-23.1 | RF-016, RF-017, RF-018, RF-034 | Integración | Agenda de compromisos con responsable, historial y control de versión. | CompromisoVistasTests.test_cambio_de_estado_queda_en_el_historial_y_en_la_auditoria | Aprobado |
| CP-INT-064 | CU-02, CU-12, CU-13, CU-13.1, CU-23.1 | RF-016, RF-017, RF-018, RF-034 | Integración | Agenda de compromisos con responsable, historial y control de versión. | CompromisoVistasTests.test_crear_compromiso_deja_historial_y_auditoria | Aprobado |
| CP-INT-065 | CU-02, CU-12, CU-13, CU-13.1, CU-23.1 | RF-016, RF-017, RF-018, RF-034 | Integración | Agenda de compromisos con responsable, historial y control de versión. | CompromisoVistasTests.test_el_formulario_de_edicion_no_cambia_el_estado_y_rechaza_versiones_viejas | Aprobado |
| CP-INT-066 | CU-02, CU-12, CU-13, CU-13.1, CU-23.1 | RF-016, RF-017, RF-018, RF-034 | Integración | Agenda de compromisos con responsable, historial y control de versión. | CompromisoVistasTests.test_solo_el_responsable_o_la_coordinacion_modifican_un_compromiso | Aprobado |
| CP-INT-067 | CU-02, CU-12, CU-13, CU-13.1, CU-23.1 | RF-016, RF-017, RF-018, RF-034 | Integración | Agenda de compromisos con responsable, historial y control de versión. | CompromisoVistasTests.test_solo_la_coordinacion_elimina_compromisos | Aprobado |
| CP-INT-068 | CU-02, CU-12, CU-13, CU-13.1, CU-23.1 | RF-016, RF-017, RF-018, RF-034 | Integración | Agenda de compromisos con responsable, historial y control de versión. | CompromisoVistasTests.test_un_funcionario_siempre_queda_como_responsable_de_lo_que_crea | Aprobado |
| CP-COM-005 | CU-02.1 | RF-016 | Unitaria | Un eje inventado se rechaza. | CompromisoFormUnitTests.test_el_eje_debe_ser_uno_de_los_definidos | Aprobado |
| CP-COM-010 | CU-02.1 | RF-017 | Unitaria | Con todos los datos críticos no hay errores. | CompromisoFormUnitTests.test_un_compromiso_completo_es_valido | Aprobado |
| CP-COM-011 | CU-02.1 | RF-017 | Unitaria | Una fecha mal escrita no pasa. | CompromisoFormUnitTests.test_una_fecha_con_formato_invalido_se_rechaza | Aprobado |
| CP-COM-002 | CU-02.2 | RF-017 | Unitaria | Solicitante, territorio y descripción también. | CompromisoFormUnitTests.test_cada_campo_obligatorio_se_informa_por_nombre | Aprobado |
| CP-COM-008 | CU-02.2 | RF-017 | Unitaria | La fecha comprometida es obligatoria. | CompromisoFormUnitTests.test_sin_fecha_comprometida_no_se_guarda | Aprobado |
| CP-COM-009 | CU-02.2 | RF-017 | Unitaria | El responsable es obligatorio. | CompromisoFormUnitTests.test_sin_responsable_no_se_guarda | Aprobado |
| CP-COM-037 | CU-02.3 | RF-019 | Unitaria | Pasó la fecha y no está realizado. | PlazoUnitTests.test_vencido_es_fecha_pasada_sin_realizar | Aprobado |
| CP-INT-101 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_acceso_segun_el_rol | Aprobado |
| CP-INT-102 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_administrador_no_puede_desactivarse_ni_quitarse_el_rol | Aprobado |
| CP-INT-103 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_busqueda_filtra_la_lista | Aprobado |
| CP-INT-104 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_cargo_se_desactiva_en_vez_de_eliminarse | Aprobado |
| CP-INT-105 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_catalogo_rechaza_codigo_duplicado | Aprobado |
| CP-INT-106 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_catalogo_se_desactiva_y_activa_sin_borrar_la_fila | Aprobado |
| CP-INT-107 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_crear_y_editar_delegacion_deja_auditoria_con_valores | Aprobado |
| CP-INT-108 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_desactivar_funcionario_tambien_desactiva_su_cuenta | Aprobado |
| CP-INT-109 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_eliminar_meta_avisa_que_borra_sus_indicadores | Aprobado |
| CP-INT-110 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_funcionario_rechaza_usuario_repetido_y_contrasena_distinta | Aprobado |
| CP-INT-111 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_funcionario_se_crea_con_cuenta_roles_y_auditoria_sin_contrasena | Aprobado |
| CP-INT-112 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_indice_deshabilita_los_mantenedores_exclusivos_del_administrador | Aprobado |
| CP-INT-113 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_item_con_metas_no_se_elimina | Aprobado |
| CP-INT-114 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_item_rechaza_ponderaciones_que_superan_100 | Aprobado |
| CP-INT-115 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_las_ocho_listas_tienen_agregar_y_buscar | Aprobado |
| CP-INT-116 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_los_avisos_se_muestran_en_pantalla | Aprobado |
| CP-INT-117 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_los_formularios_de_alta_y_edicion_se_muestran | Aprobado |
| CP-INT-118 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_mantenedor_inexistente_es_404 | Aprobado |
| CP-INT-119 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_meta_rechaza_objetivo_cero_y_al_guardar_genera_su_indicador | Aprobado |
| CP-INT-120 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_periodo_cerrado_no_se_edita_ni_se_elimina | Aprobado |
| CP-INT-121 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_periodo_rechaza_termino_anterior_al_inicio | Aprobado |
| CP-INT-122 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_periodo_se_crea_en_borrador_y_calcula_sus_dias | Aprobado |
| CP-INT-123 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_periodo_se_inicia_se_cierra_y_se_reabre_con_motivo | Aprobado |
| CP-INT-124 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_rol_en_uso_no_se_elimina_y_explica_el_motivo | Aprobado |
| CP-INT-125 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_rol_nuevo_sin_uso_se_elimina_con_auditoria | Aprobado |
| CP-INT-126 | CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 | RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-007 | Integración | CRUD genérico de las ocho tablas maestras. | MantenedoresTests.test_roles_del_sistema_no_se_renombran_ni_se_eliminan | Aprobado |
| CP-ORG-004 | CU-04 | RF-003 | Unitaria | Un cargo retirado no está vigente. | CargoUnitTests.test_verificar_vigencia_refleja_el_estado_del_cargo | Aprobado |
| CP-ORG-002 | CU-04.1 | RF-006 | Unitaria | Una ponderación que respeta el 100 % se guarda. | CargoUnitTests.test_actualizar_ponderaciones_guarda_un_valor_valido | Aprobado |
| CP-ORG-003 | CU-04.1 | RF-006 | Unitaria | El ítem debe pertenecer al cargo. | CargoUnitTests.test_actualizar_ponderaciones_rechaza_un_item_de_otro_cargo | Aprobado |
| CP-ORG-022 | CU-04.1 | RF-006 | Unitaria | Cambiar 60 % a 70 % con otro de 30 % es válido. | ItemMedibleUnitTests.test_al_editar_un_item_no_se_cuenta_a_si_mismo | Aprobado |
| CP-ORG-025 | CU-04.1 | RF-006 | Unitaria | RN-001: 60 % más 40 % suman 100 %. | ItemMedibleUnitTests.test_la_suma_exacta_de_100_es_valida | Aprobado |
| CP-ORG-001 | CU-04.2 | RF-006 | Unitaria | Más de 100 % no se guarda. | CargoUnitTests.test_actualizar_ponderaciones_bloquea_una_suma_superior_a_100 | Aprobado |
| CP-ORG-024 | CU-04.2 | RF-006 | Unitaria | Un porcentaje negativo es inválido. | ItemMedibleUnitTests.test_la_ponderacion_no_puede_ser_negativa | Aprobado |
| CP-ORG-026 | CU-04.2 | RF-006 | Unitaria | RN-001: 60 % más 50 % no se guarda. | ItemMedibleUnitTests.test_una_suma_superior_a_100_se_bloquea | Aprobado |
| CP-INT-127 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_catalogo_codigo_unico_y_activacion | Aprobado |
| CP-INT-128 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_cumplimiento_global_de_la_delegacion | Aprobado |
| CP-INT-129 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_dias_computables_se_calculan_al_guardar | Aprobado |
| CP-INT-130 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_periodo_rechaza_termino_anterior | Aprobado |
| CP-INT-131 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn001_iniciar_periodo_exige_100_por_cargo | Aprobado |
| CP-INT-132 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn001_ponderaciones_del_cargo_no_superan_100 | Aprobado |
| CP-INT-133 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn002_valor_objetivo_mayor_que_cero | Aprobado |
| CP-INT-134 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn004_evaluar_progreso_y_actualizar_objetivo | Aprobado |
| CP-INT-135 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn005_tope_configurable_por_parametro | Aprobado |
| CP-INT-136 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn005_tope_por_defecto_150_y_ponderado | Aprobado |
| CP-INT-137 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn006_umbral_minimo_por_defecto_80 | Aprobado |
| CP-INT-138 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn007_porcentaje_esperado_y_dias_restantes | Aprobado |
| CP-INT-139 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn008_semaforo | Aprobado |
| CP-INT-140 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn013_periodo_cerrado_no_se_modifica | Aprobado |
| CP-INT-141 | CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 | RF-005, RF-006, RF-007, RF-022, RF-023, RF-024, RF-026, RF-027 | Integración | Reglas RN-001 a RN-008 y RN-013 de la medición. | MedicionTests.test_rn013_reapertura_exige_motivo_y_queda_auditada | Aprobado |
| CP-TRA-001 | CU-05 | RF-007 | Unitaria | La advertencia cuenta los indicadores calculados. | AdvertenciaMetaUnitTests.test_eliminar_una_meta_advierte_cuantos_indicadores_se_pierden | Aprobado |
| CP-ORG-031 | CU-05.1 | RF-007 | Unitaria | El mínimo aceptado es 0,01. | MetaUnitTests.test_un_valor_objetivo_positivo_es_valido | Aprobado |
| CP-ORG-027 | CU-05.2 | RF-007 | Unitaria | Un valor inválido no llega a la base. | MetaUnitTests.test_actualizar_valor_objetivo_valida_antes_de_guardar | Aprobado |
| CP-ORG-028 | CU-05.2 | RF-007 | Unitaria | RN-002: cero y negativos se rechazan. | MetaUnitTests.test_el_valor_objetivo_debe_ser_mayor_que_cero | Aprobado |
| CP-ORG-030 | CU-05.3 | RF-038 | Unitaria | RN-013: los períodos cerrados no se modifican. | MetaUnitTests.test_no_se_crea_una_meta_en_un_periodo_cerrado | Aprobado |
| CP-INT-074 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_dashboard_y_resumen_muestran_la_diferencia_y_la_desviacion | Aprobado |
| CP-INT-075 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_el_detalle_explica_la_formula_y_enlaza_las_actividades_que_aportan | Aprobado |
| CP-INT-076 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_el_detalle_informa_cuando_se_aplica_el_tope | Aprobado |
| CP-INT-077 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_el_selector_ignora_un_periodo_ajeno_o_invalido | Aprobado |
| CP-INT-078 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_exige_iniciar_sesion | Aprobado |
| CP-INT-079 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_la_ficha_calcula_la_diferencia_con_lo_esperado | Aprobado |
| CP-INT-080 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_la_ficha_solo_muestra_las_metas_del_funcionario | Aprobado |
| CP-INT-081 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_la_meta_alcanzada_se_destaca_como_cumplida | Aprobado |
| CP-INT-082 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_resumen_de_evidencias_y_compromisos | Aprobado |
| CP-INT-083 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_sin_metas_la_ficha_lo_indica | Aprobado |
| CP-INT-084 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_un_usuario_sin_funcionario_es_redirigido_con_un_mensaje | Aprobado |
| CP-INT-085 | CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 | RF-008, RF-028 | Integración | Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula. | FichaPersonalTests.test_una_meta_sin_calculo_se_informa_sin_formula | Aprobado |
| CP-MED-018 | CU-06 | RF-028 | Unitaria | 1 de 4 con esperado de 50 % es 25 %, 25 puntos bajo lo esperado. | FichaPersonalUnitTests.test_la_fila_trae_avance_cumplimiento_y_diferencia | Aprobado |
| CP-MED-021 | CU-06 | RF-008 | Unitaria | El selector de períodos de la ficha. | FichaPersonalUnitTests.test_periodos_de_lista_solo_donde_hay_metas | Aprobado |
| CP-MED-023 | CU-06 | RF-028 | Unitaria | Cuántas evidencias hay en cada estado de revisión. | FichaPersonalUnitTests.test_resumen_de_evidencias_por_estado | Aprobado |
| CP-MED-024 | CU-06 | RF-008 | Unitaria | La ficha es personal. | FichaPersonalUnitTests.test_solo_aparecen_las_metas_del_funcionario | Aprobado |
| CP-MED-025 | CU-06 | RF-008 | Unitaria | Antes del primer cálculo no hay formula ni diferencia. | FichaPersonalUnitTests.test_una_meta_sin_calculo_se_marca_como_tal | Aprobado |
| CP-ACT-046 | CU-06.1 | RF-022 | Unitaria | Aprobar una actividad deja un indicador nuevo. | ValidacionUnitTests.test_una_aprobacion_recalcula_los_indicadores_de_la_meta | Aprobado |
| CP-MED-013 | CU-06.1 | RF-022 | Unitaria | Cada generación deja un registro. | CumplimientoUnitTests.test_generar_calcula_y_guarda_un_indicador_nuevo | Aprobado |
| CP-MED-019 | CU-06.2 | RF-028 | Unitaria | Con el avance igual al objetivo queda cumplida. | FichaPersonalUnitTests.test_la_meta_alcanzada_se_destaca_como_cumplida | Aprobado |
| CP-MED-001 | CU-07.1 | RF-022 | Unitaria | RN-003: solo aprobadas con validación aprobada. | AvanceUnitTests.test_cuenta_las_actividades_aprobadas_del_item_en_el_periodo | Aprobado |
| CP-MED-003 | CU-07.1 | RF-022 | Unitaria | RN-003: se mide dentro del período. | AvanceUnitTests.test_no_cuentan_las_actividades_fuera_de_las_fechas_del_periodo | Aprobado |
| CP-MED-005 | CU-07.1 | RF-022, RF-029 | Unitaria | Una meta de Centro no suma lo de Rural. | AvanceUnitTests.test_solo_cuentan_las_actividades_de_la_delegacion_de_la_meta | Aprobado |
| CP-MED-006 | CU-07.1 | RF-022 | Unitaria | Un ítem distinto no aporta. | AvanceUnitTests.test_solo_cuentan_las_actividades_del_item_de_la_meta | Aprobado |
| CP-MED-007 | CU-07.1 | RF-022 | Unitaria | RN-003: se cuentan actividades, no evidencias. | AvanceUnitTests.test_una_actividad_con_dos_evidencias_aprobadas_cuenta_una_vez | Aprobado |
| CP-MED-008 | CU-07.1 | RF-022 | Unitaria | El alcance global cuenta cualquier delegación. | AvanceUnitTests.test_una_meta_sin_delegacion_suma_todas_las_delegaciones | Aprobado |
| CP-MED-009 | CU-07.1 | RF-023 | Unitaria | RN-004: 1 de 4 es 25 %. | CumplimientoUnitTests.test_cumplimiento_es_avance_sobre_meta | Aprobado |
| CP-MED-010 | CU-07.1 | RF-024 | Unitaria | RN-005: ponderador 40 % de un 50 % da 20. | CumplimientoUnitTests.test_el_cumplimiento_ponderado_usa_el_ponderador_de_la_meta | Aprobado |
| CP-MED-011 | CU-07.1 | RF-024 | Unitaria | RN-005: no pasa del máximo computable. | CumplimientoUnitTests.test_el_cumplimiento_se_topa_en_150_por_defecto | Aprobado |
| CP-ORG-029 | CU-07.1 | RF-023 | Unitaria | RN-004: 1 de 4 es 25 %, 1 de 3 es 33,33 %. | MetaUnitTests.test_evaluar_progreso_es_avance_sobre_meta_por_100 | Aprobado |
| CP-ACT-001 | CU-07.2 | RF-022 | Unitaria | La anulación explícita sí cambia el estado. | ActividadEstadoUnitTests.test_anulando_si_se_puede_salir_de_aprobada | Aprobado |
| CP-ACT-038 | CU-07.2 | RF-022 | Unitaria | Con motivo, la actividad deja de sumar. | ValidacionUnitTests.test_anular_una_aprobacion_deja_sin_efecto_el_aporte | Aprobado |
| CP-INT-030 | CU-07.2 | RF-022, RF-023, RN-009, RN-013 | Integración | Anular una aprobación exige motivo, recalcula hacia abajo y conserva el historial. | AnularAprobacionTests.test_anular_quita_la_actividad_del_avance_y_recalcula | Aprobado |
| CP-INT-031 | CU-07.2 | RF-022, RF-023, RN-009, RN-013 | Integración | Anular una aprobación exige motivo, recalcula hacia abajo y conserva el historial. | AnularAprobacionTests.test_exige_un_motivo_y_una_actividad_aprobada | Aprobado |
| CP-INT-032 | CU-07.2 | RF-022, RF-023, RN-009, RN-013 | Integración | Anular una aprobación exige motivo, recalcula hacia abajo y conserva el historial. | AnularAprobacionTests.test_get_no_anula_y_el_panel_solo_se_ofrece_a_quien_corresponde | Aprobado |
| CP-INT-033 | CU-07.2 | RF-022, RF-023, RN-009, RN-013 | Integración | Anular una aprobación exige motivo, recalcula hacia abajo y conserva el historial. | AnularAprobacionTests.test_la_validacion_original_se_conserva_como_historial | Aprobado |
| CP-INT-034 | CU-07.2 | RF-022, RF-023, RN-009, RN-013 | Integración | Anular una aprobación exige motivo, recalcula hacia abajo y conserva el historial. | AnularAprobacionTests.test_la_vista_anula_audita_y_muestra_el_resultado | Aprobado |
| CP-INT-035 | CU-07.2 | RF-022, RF-023, RN-009, RN-013 | Integración | Anular una aprobación exige motivo, recalcula hacia abajo y conserva el historial. | AnularAprobacionTests.test_la_vista_rechaza_un_motivo_vacio_sin_cambios | Aprobado |
| CP-INT-036 | CU-07.2 | RF-022, RF-023, RN-009, RN-013 | Integración | Anular una aprobación exige motivo, recalcula hacia abajo y conserva el historial. | AnularAprobacionTests.test_un_funcionario_no_puede_anular_y_queda_registrado | Aprobado |
| CP-INT-037 | CU-07.2 | RF-022, RF-023, RN-009, RN-013 | Integración | Anular una aprobación exige motivo, recalcula hacia abajo y conserva el historial. | AnularAprobacionTests.test_un_periodo_cerrado_no_permite_anular | Aprobado |
| CP-MED-016 | CU-07.3 | RF-024 | Unitaria | Si el bruto supera el máximo, se explica. | FichaPersonalUnitTests.test_el_detalle_avisa_cuando_se_aplica_el_tope | Aprobado |
| CP-MED-017 | CU-07.3 | RF-023 | Unitaria | El cálculo se puede verificar a mano. | FichaPersonalUnitTests.test_el_detalle_muestra_la_formula_y_la_ponderacion | Aprobado |
| CP-MED-020 | CU-07.3 | RF-022 | Unitaria | Cada cifra enlaza a su origen. | FichaPersonalUnitTests.test_lista_las_actividades_que_aportan | Aprobado |
| CP-ACT-028 | CU-09 | RF-012 | Unitaria | Código de la actividad más un correlativo. | EvidenciaUnitTests.test_el_codigo_de_evidencia_deriva_del_de_la_actividad | Aprobado |
| CP-ACT-029 | CU-09 | RF-012 | Unitaria | El código de la evidencia es inmutable. | EvidenciaUnitTests.test_el_codigo_de_evidencia_no_se_puede_modificar | Aprobado |
| CP-ACT-037 | CU-09 | RF-012 | Unitaria | La evidencia queda ligada a la actividad y pendiente. | EvidenciaUnitTests.test_subir_evidencia_vincula_el_archivo_y_envia_a_revision | Aprobado |
| CP-ACT-030 | CU-09.1 | RF-012 | Unitaria | Sin archivo no hay carga. | EvidenciaUnitTests.test_el_formulario_exige_un_archivo | Aprobado |
| CP-ACT-035 | CU-09.1 | RF-012 | Unitaria | JPG, JPEG, PNG y PDF se aceptan, sin importar mayúsculas. | EvidenciaUnitTests.test_formatos_permitidos | Aprobado |
| CP-ACT-031 | CU-09.2 | RF-012 | Unitaria | El motivo exacto del rechazo se informa. | EvidenciaUnitTests.test_el_formulario_rechaza_una_extension_no_permitida | Aprobado |
| CP-ACT-032 | CU-09.2 | RNF-017 | Unitaria | El motivo indica el peso y el máximo permitido. | EvidenciaUnitTests.test_el_limite_de_tamano_es_configurable | Aprobado |
| CP-ACT-034 | CU-09.2 | RF-012 | Unitaria | Ejecutables, documentos y archivos sin extensión no entran. | EvidenciaUnitTests.test_formatos_no_permitidos_se_rechazan | Aprobado |
| CP-INT-069 | CU-09.2 | RF-012, RNF-017 | Integración | Las evidencias que superan el tamaño máximo configurado se rechazan con su motivo. | EvidenciaTamanoTests.test_el_formulario_de_evidencia_informa_el_motivo_del_rechazo | Aprobado |
| CP-INT-070 | CU-09.2 | RF-012, RNF-017 | Integración | Las evidencias que superan el tamaño máximo configurado se rechazan con su motivo. | EvidenciaTamanoTests.test_el_maximo_por_defecto_es_de_5_megabytes | Aprobado |
| CP-INT-071 | CU-09.2 | RF-012, RNF-017 | Integración | Las evidencias que superan el tamaño máximo configurado se rechazan con su motivo. | EvidenciaTamanoTests.test_el_validador_acepta_hasta_el_maximo_y_rechaza_lo_que_lo_supera | Aprobado |
| CP-INT-072 | CU-09.2 | RF-012, RNF-017 | Integración | Las evidencias que superan el tamaño máximo configurado se rechazan con su motivo. | EvidenciaTamanoTests.test_subir_evidencia_rechaza_un_archivo_demasiado_pesado | Aprobado |
| CP-INT-073 | CU-09.2 | RF-012, RNF-017 | Integración | Las evidencias que superan el tamaño máximo configurado se rechazan con su motivo. | EvidenciaTamanoTests.test_un_archivo_guardado_que_falta_en_el_disco_no_se_mide | Aprobado |
| CP-ACT-016 | CU-10 | RF-011 | Unitaria | Los códigos generados son únicos. | ActividadUnitTests.test_dos_actividades_nunca_comparten_codigo | Aprobado |
| CP-ACT-017 | CU-10 | RF-011 | Unitaria | RN-010: el código es inmutable. | ActividadUnitTests.test_el_codigo_verificador_no_se_puede_modificar | Aprobado |
| CP-ACT-018 | CU-10 | RF-011 | Unitaria | RN-010: formato EVD-fecha-sufijo y no se regenera. | ActividadUnitTests.test_el_codigo_verificador_tiene_formato_y_se_asigna_una_vez | Aprobado |
| CP-ACT-014 | CU-10.1 | RF-032 | Unitaria | La búsqueda por código devuelve su actividad. | ActividadUnitTests.test_buscar_por_codigo_encuentra_la_actividad | Aprobado |
| CP-ACT-015 | CU-10.2 | RF-032 | Unitaria | Un código sin registros da un resultado vacío. | ActividadUnitTests.test_buscar_un_codigo_inexistente_no_devuelve_nada | Aprobado |
| CP-ACT-003 | CU-11 | RF-013 | Unitaria | Solo existen los estados definidos. | ActividadEstadoUnitTests.test_cambiar_estado_rechaza_un_estado_inexistente | Aprobado |
| CP-ACT-036 | CU-11 | RF-013 | Unitaria | Un archivo nuevo debe revisarse de nuevo. | EvidenciaUnitTests.test_reemplazar_archivo_vuelve_a_revision | Aprobado |
| CP-ACT-039 | CU-11 | RF-013 | Unitaria | La aprobación se refleja en ambas. | ValidacionUnitTests.test_aprobar_marca_la_evidencia_y_la_actividad | Aprobado |
| CP-INT-180 | CU-11, CU-11.1, CU-11.2 | RF-013, RF-014 | Integración | Revisión de evidencias con Validacion (RN-009). | RevisionTests.test_actividad_corregida_vuelve_a_revision_y_se_puede_aprobar | Aprobado |
| CP-INT-181 | CU-11, CU-11.1, CU-11.2 | RF-013, RF-014 | Integración | Revisión de evidencias con Validacion (RN-009). | RevisionTests.test_actividad_sin_evidencias_pendientes_no_se_revisa | Aprobado |
| CP-INT-182 | CU-11, CU-11.1, CU-11.2 | RF-013, RF-014 | Integración | Revisión de evidencias con Validacion (RN-009). | RevisionTests.test_aprobar_valida_cada_evidencia_pendiente_y_actualiza_el_indicador | Aprobado |
| CP-INT-183 | CU-11, CU-11.1, CU-11.2 | RF-013, RF-014 | Integración | Revisión de evidencias con Validacion (RN-009). | RevisionTests.test_el_detalle_ofrece_la_revision_solo_a_quien_puede_hacerla | Aprobado |
| CP-INT-184 | CU-11, CU-11.1, CU-11.2 | RF-013, RF-014 | Integración | Revisión de evidencias con Validacion (RN-009). | RevisionTests.test_rechazar_y_pedir_correccion_exigen_observacion | Aprobado |
| CP-INT-185 | CU-11, CU-11.1, CU-11.2 | RF-013, RF-014 | Integración | Revisión de evidencias con Validacion (RN-009). | RevisionTests.test_rechazo_sin_observacion_explica_el_motivo | Aprobado |
| CP-INT-186 | CU-11, CU-11.1, CU-11.2 | RF-013, RF-014 | Integración | Revisión de evidencias con Validacion (RN-009). | RevisionTests.test_solo_administracion_coordinacion_y_verificacion_revisan | Aprobado |
| CP-INT-187 | CU-11, CU-11.1, CU-11.2 | RF-013, RF-014 | Integración | Revisión de evidencias con Validacion (RN-009). | RevisionTests.test_superusuario_sin_funcionario_no_puede_revisar | Aprobado |
| CP-MED-002 | CU-11 | RF-022 | Unitaria | RN-009: la aprobación exige la validación del verificador. | AvanceUnitTests.test_no_cuenta_una_actividad_aprobada_sin_validacion_aprobada | Aprobado |
| CP-TRA-010 | CU-11 | RF-013 | Unitaria | Puede revisar actividades de cualquier delegación. | AlcanceUnitTests.test_un_verificador_sin_delegacion_revisa_todas | Aprobado |
| CP-ACT-040 | CU-11.1 | RF-013 | Unitaria | Primera, segunda revisión, y así. | ValidacionUnitTests.test_cada_revision_incrementa_el_numero_de_version | Aprobado |
| CP-ACT-042 | CU-11.1 | RF-013 | Unitaria | Quién, cuándo, qué decidió y por qué. | ValidacionUnitTests.test_la_decision_deja_verificador_fecha_resultado_y_observacion | Aprobado |
| CP-ACT-006 | CU-11.2 | RF-014 | Unitaria | RN-009: lo aprobado ya suma y solo se anula con motivo. | ActividadEstadoUnitTests.test_una_actividad_aprobada_no_cambia_de_estado | Aprobado |
| CP-ACT-033 | CU-11.2 | RF-014 | Unitaria | Lo ya aprobado no vuelve a pendiente. | EvidenciaUnitTests.test_enviar_a_revision_no_reabre_una_actividad_aprobada | Aprobado |
| CP-ACT-043 | CU-11.2 | RF-014 | Unitaria | La solicitud de corrección se explica. | ValidacionUnitTests.test_pedir_correccion_exige_una_observacion | Aprobado |
| CP-ACT-044 | CU-11.2 | RF-014 | Unitaria | Sin motivo no hay rechazo; con él la actividad queda rechazada. | ValidacionUnitTests.test_rechazar_exige_un_motivo_y_no_aporta_al_avance | Aprobado |
| CP-ACT-045 | CU-11.2 | RF-014 | Unitaria | RN-009: rechazada o en corrección no suma. | ValidacionUnitTests.test_solo_las_actividades_aprobadas_cuentan_para_la_meta | Aprobado |
| CP-MED-004 | CU-11.2 | RF-022 | Unitaria | RN-009: solo lo aprobado aporta. | AvanceUnitTests.test_no_cuentan_las_pendientes_rechazadas_ni_en_correccion | Aprobado |
| CP-TRA-003 | CU-11.2 | RF-014 | Unitaria | Aprobada no se modifica ni siquiera por la coordinación. | AlcanceUnitTests.test_bloqueo_de_una_actividad_aprobada | Aprobado |
| CP-COM-029 | CU-12 | RF-032 | Unitaria | Sin criterios se ven todos los compromisos. | FiltrosAgendaUnitTests.test_sin_filtros_trae_todos | Aprobado |
| CP-COM-023 | CU-12.1 | RF-032 | Unitaria | Delegación y estado se combinan. | FiltrosAgendaUnitTests.test_filtra_por_delegacion_y_estado | Aprobado |
| CP-COM-024 | CU-12.1 | RF-019, RF-032 | Unitaria | Vencidos no incluye los realizados. | FiltrosAgendaUnitTests.test_filtra_por_plazo | Aprobado |
| CP-COM-025 | CU-12.1 | RF-032 | Unitaria | Desde y hasta incluyen sus extremos. | FiltrosAgendaUnitTests.test_filtra_por_rango_de_fechas_comprometidas | Aprobado |
| CP-COM-026 | CU-12.1 | RF-032 | Unitaria | La búsqueda de texto recorre los campos visibles. | FiltrosAgendaUnitTests.test_filtra_por_texto_en_folio_descripcion_solicitante_y_delegacion | Aprobado |
| CP-COM-028 | CU-12.1 | RF-032 | Unitaria | Un filtro mal formado no rompe la agenda. | FiltrosAgendaUnitTests.test_los_valores_invalidos_se_ignoran | Aprobado |
| CP-COM-030 | CU-12.2 | RF-032 | Unitaria | Nada que mostrar, sin error. | FiltrosAgendaUnitTests.test_una_consulta_sin_coincidencias_devuelve_vacio | Aprobado |
| CP-COM-001 | CU-13 | RF-018 | Unitaria | El estado cambia solo desde la agenda, con historial. | CompromisoFormUnitTests.test_al_editar_se_oculta_el_estado_y_se_exige_la_version | Aprobado |
| CP-COM-016 | CU-13 | RF-018 | Unitaria | Se avanza y un realizado solo vuelve a «en proceso». | EstadoUnitTests.test_estados_permitidos_avanzan_y_un_realizado_solo_se_reabre_a_en_proceso | Aprobado |
| CP-COM-020 | CU-13 | RF-017 | Unitaria | Lo cerrado no cambia de responsable. | EstadoUnitTests.test_un_compromiso_realizado_no_se_deriva | Aprobado |
| CP-COM-021 | CU-13 | RF-018 | Unitaria | Solo los cuatro estados definidos. | EstadoUnitTests.test_un_estado_inexistente_se_rechaza | Aprobado |
| CP-COM-022 | CU-13 | RF-018 | Unitaria | Retroceder no está permitido y no deja rastro. | EstadoUnitTests.test_una_transicion_no_permitida_se_rechaza_sin_historial | Aprobado |
| CP-INT-050 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_cerrar_un_compromiso_ya_realizado_se_rechaza | Aprobado |
| CP-INT-051 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_el_admin_no_ofrece_eliminar_un_incumplimiento | Aprobado |
| CP-INT-052 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_el_cambio_de_estado_desde_la_vista_guarda_la_observacion_y_rechaza_lo_no_permitido | Aprobado |
| CP-INT-053 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_estados_permitidos_avanzan_y_un_realizado_solo_se_reabre_a_en_proceso | Aprobado |
| CP-INT-054 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_la_agenda_destaca_los_proximos_a_vencer_y_cuenta_cada_grupo | Aprobado |
| CP-INT-055 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_la_agenda_ofrece_solo_las_transiciones_permitidas | Aprobado |
| CP-INT-056 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_la_vista_de_eliminar_explica_por_que_no_se_puede | Aprobado |
| CP-INT-057 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_los_dias_de_alerta_son_configurables | Aprobado |
| CP-INT-058 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_proximo_a_vencer_dentro_de_los_dias_de_alerta | Aprobado |
| CP-INT-059 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_reabrir_un_realizado_guarda_la_observacion_en_el_historial | Aprobado |
| CP-INT-060 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_un_incumplimiento_no_se_elimina_pero_uno_vigente_o_realizado_si | Aprobado |
| CP-INT-061 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_una_transicion_no_permitida_se_rechaza_y_no_deja_historial | Aprobado |
| CP-INT-062 | CU-13, CU-14.2, CU-02.3 | RF-018, RF-019 | Integración | Transiciones controladas, alerta de vencimiento y conservación de incumplimientos. | CompromisoReglasTests.test_vencido_y_proximo_a_vencer_son_excluyentes | Aprobado |
| CP-COM-015 | CU-13.1 | RF-017 | Unitaria | La derivación queda trazada. | EstadoUnitTests.test_derivar_cambia_el_responsable_y_lo_deja_en_el_historial | Aprobado |
| CP-COM-017 | CU-13.1 | RF-018 | Unitaria | La reapertura queda explicada. | EstadoUnitTests.test_reabrir_un_realizado_conserva_la_observacion | Aprobado |
| CP-COM-018 | CU-13.1 | RF-018 | Unitaria | La creación deja su primer registro. | EstadoUnitTests.test_registrar_historial_guarda_el_estado_actual_como_nuevo | Aprobado |
| CP-COM-019 | CU-13.1 | RF-018 | Unitaria | Estado anterior, nuevo, autor y observación. | EstadoUnitTests.test_set_estado_cambia_y_deja_historial | Aprobado |
| CP-COM-012 | CU-13.2 | RF-018 | Unitaria | El cierre se refleja y queda en el historial. | EstadoUnitTests.test_cerrar_deja_el_compromiso_realizado_con_su_resolucion | Aprobado |
| CP-COM-013 | CU-13.2 | RF-018 | Unitaria | Sin resolución no se cierra. | EstadoUnitTests.test_cerrar_exige_una_resolucion | Aprobado |
| CP-COM-014 | CU-13.2 | RF-018 | Unitaria | El cierre solo se hace una vez. | EstadoUnitTests.test_cerrar_uno_ya_realizado_se_rechaza | Aprobado |
| CP-COM-031 | CU-14.1 | RF-019 | Unitaria | Días que faltan, negativos si ya pasó. | PlazoUnitTests.test_dias_para_vencer | Aprobado |
| CP-COM-034 | CU-14.1 | RF-019 | Unitaria | Vencido, próximo a vencer, realizado o estado normal. | PlazoUnitTests.test_situacion_de_plazo_clasifica_cada_compromiso | Aprobado |
| CP-MED-022 | CU-14.1 | RF-019 | Unitaria | Vigentes, por vencer, vencidos y realizados. | FichaPersonalUnitTests.test_resumen_de_compromisos_por_situacion | Aprobado |
| CP-COM-032 | CU-14.2 | RF-019, RF-037 | Unitaria | Con 7 días, vence en 7 sí y en 8 no. | PlazoUnitTests.test_los_dias_de_alerta_son_configurables | Aprobado |
| CP-COM-033 | CU-14.2 | RF-019, RF-037 | Unitaria | Hoy y los 3 días siguientes, por defecto. | PlazoUnitTests.test_proximo_a_vencer_dentro_de_los_dias_de_alerta | Aprobado |
| CP-COM-035 | CU-14.2 | RF-019 | Unitaria | El vencido se conserva con su historial. | PlazoUnitTests.test_un_incumplimiento_no_se_elimina | Aprobado |
| CP-COM-036 | CU-14.2 | RF-019 | Unitaria | Solo el incumplimiento queda protegido. | PlazoUnitTests.test_uno_vigente_o_realizado_si_se_elimina | Aprobado |
| CP-INT-142 | CU-16, CU-16.1, CU-17, CU-18, CU-18.1 | RF-026, RF-027, RF-028, RF-029 | Integración | Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008). | MedicionVistasTests.test_dashboard_muestra_el_cumplimiento_y_el_semaforo_de_cada_delegacion | Aprobado |
| CP-INT-143 | CU-16, CU-16.1, CU-17, CU-18, CU-18.1 | RF-026, RF-027, RF-028, RF-029 | Integración | Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008). | MedicionVistasTests.test_el_cumplimiento_de_la_delegacion_pondera_sus_metas | Aprobado |
| CP-INT-144 | CU-16, CU-16.1, CU-17, CU-18, CU-18.1 | RF-026, RF-027, RF-028, RF-029 | Integración | Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008). | MedicionVistasTests.test_gestionar_metas_solo_para_administracion_y_coordinacion | Aprobado |
| CP-INT-145 | CU-16, CU-16.1, CU-17, CU-18, CU-18.1 | RF-026, RF-027, RF-028, RF-029 | Integración | Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008). | MedicionVistasTests.test_la_portada_usa_el_promedio_de_los_indicadores | Aprobado |
| CP-INT-146 | CU-16, CU-16.1, CU-17, CU-18, CU-18.1 | RF-026, RF-027, RF-028, RF-029 | Integración | Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008). | MedicionVistasTests.test_las_barras_de_progreso_no_usan_coma_decimal | Aprobado |
| CP-INT-147 | CU-16, CU-16.1, CU-17, CU-18, CU-18.1 | RF-026, RF-027, RF-028, RF-029 | Integración | Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008). | MedicionVistasTests.test_selector_de_periodo_y_busqueda_por_delegacion | Aprobado |
| CP-INT-148 | CU-16, CU-16.1, CU-17, CU-18, CU-18.1 | RF-026, RF-027, RF-028, RF-029 | Integración | Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008). | MedicionVistasTests.test_semaforo_segun_lo_esperado_al_dia | Aprobado |
| CP-INT-149 | CU-16, CU-16.1, CU-17, CU-18, CU-18.1 | RF-026, RF-027, RF-028, RF-029 | Integración | Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008). | MedicionVistasTests.test_semaforo_y_resumen_comparten_los_resultados | Aprobado |
| CP-INT-150 | CU-16, CU-16.1, CU-17, CU-18, CU-18.1 | RF-026, RF-027, RF-028, RF-029 | Integración | Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008). | MedicionVistasTests.test_sin_indicadores_se_avisa_y_una_delegacion_sin_calculo_se_marca | Aprobado |
| CP-INT-151 | CU-16, CU-16.1, CU-17, CU-18, CU-18.1 | RF-026, RF-027, RF-028, RF-029 | Integración | Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008). | MedicionVistasTests.test_solo_cuenta_el_ultimo_indicador_de_cada_meta | Aprobado |
| CP-MED-032 | CU-16 | RF-027 | Unitaria | Centro al 100 % es verde y Rural al 25 % es rojo. | ResultadosPorDelegacionUnitTests.test_cumplimiento_y_color_de_cada_delegacion | Aprobado |
| CP-MED-015 | CU-16.1 | RF-027 | Unitaria | RN-008 con esperado de 50 %. | CumplimientoUnitTests.test_semaforo_segun_lo_esperado_al_dia | Aprobado |
| CP-ORG-040 | CU-16.1 | RF-027 | Unitaria | RN-008 con esperado de 50 %. | PeriodoPuroUnitTests.test_semaforo_verde_ambar_y_rojo | Aprobado |
| CP-MED-033 | CU-17.1 | RF-026 | Unitaria | Con esperado de 50 %: +50 para Centro y -25 para Rural. | ResultadosPorDelegacionUnitTests.test_diferencia_con_lo_esperado_y_desviacion | Aprobado |
| CP-ORG-038 | CU-17.1 | RF-026 | Unitaria | Antes del inicio es 0 % y después del término 100 %. | PeriodoPuroUnitTests.test_porcentaje_esperado_no_pasa_de_los_limites | Aprobado |
| CP-ORG-039 | CU-17.1 | RF-026 | Unitaria | RN-007: días transcurridos sobre días totales. | PeriodoPuroUnitTests.test_porcentaje_esperado_segun_los_dias_transcurridos | Aprobado |
| CP-MED-040 | CU-17.2 | RF-026 | Unitaria | RN-008: ámbar y rojo son desviación. | ResultadosPorDelegacionUnitTests.test_una_desviacion_ambar_tambien_se_destaca | Aprobado |
| CP-MED-026 | CU-18 | RF-029 | Unitaria | Con indicadores en ambos, gana el abierto. | PeriodoVigenteUnitTests.test_por_defecto_el_periodo_abierto_mas_reciente | Aprobado |
| CP-MED-028 | CU-18 | RF-029 | Unitaria | Sin períodos abiertos, el más reciente con cálculos. | PeriodoVigenteUnitTests.test_si_ninguno_esta_abierto_se_usa_el_mas_reciente | Aprobado |
| CP-MED-029 | CU-18 | RF-029 | Unitaria | Sin cálculos la pantalla muestra el aviso vacío. | PeriodoVigenteUnitTests.test_sin_indicadores_en_ningun_periodo_no_hay_periodo_vigente | Aprobado |
| CP-MED-030 | CU-18 | RF-029 | Unitaria | Un período sin cálculos no se ofrece. | PeriodoVigenteUnitTests.test_solo_se_ofrecen_los_periodos_con_indicadores | Aprobado |
| CP-MED-038 | CU-18 | RF-029 | Unitaria | Sin período elegido la lista está vacía. | ResultadosPorDelegacionUnitTests.test_sin_periodo_no_hay_resultados | Aprobado |
| CP-ORG-041 | CU-18 | RF-029 | Unitaria | RN-006: el cumplimiento colectivo debe alcanzar el umbral. | PeriodoPuroUnitTests.test_umbral_colectivo | Aprobado |
| CP-MED-035 | CU-18.1 | RF-030 | Unitaria | Fecha del último registro y días desde entonces. | ResultadosPorDelegacionUnitTests.test_informa_el_ultimo_calculo_y_los_dias_transcurridos | Aprobado |
| CP-MED-036 | CU-18.1 | RF-029 | Unitaria | Promedio simple de los cumplimientos. | ResultadosPorDelegacionUnitTests.test_promedio_general | Aprobado |
| CP-ORG-056 | CU-18.1 | RF-024 | Unitaria | 60 % de la meta al 100 % y 40 % al 50 % dan 80 %. | PromedioPonderadoUnitTests.test_pondera_cada_meta_por_su_ponderador | Aprobado |
| CP-ORG-057 | CU-18.1 | RF-024 | Unitaria | Sin indicadores no hay división por cero. | PromedioPonderadoUnitTests.test_sin_indicadores_el_promedio_es_cero | Aprobado |
| CP-MED-034 | CU-18.2 | RF-029 | Unitaria | El detalle explica de dónde sale la cifra. | ResultadosPorDelegacionUnitTests.test_el_detalle_muestra_avance_y_meta_de_cada_item | Aprobado |
| CP-INT-086 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_cambiar_el_estado_de_un_compromiso_conserva_los_filtros_de_la_agenda | Aprobado |
| CP-INT-087 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_el_csv_tiene_bom_separador_y_cabecera_y_queda_auditado | Aprobado |
| CP-INT-088 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_el_detalle_vuelve_a_la_lista_con_los_filtros_usados | Aprobado |
| CP-INT-089 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_el_informe_de_actividades_respeta_el_ambito_del_usuario | Aprobado |
| CP-INT-090 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_el_informe_de_compromisos_marca_la_situacion_del_plazo | Aprobado |
| CP-INT-091 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_el_informe_de_cumplimiento_usa_los_indicadores | Aprobado |
| CP-INT-092 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_el_informe_exige_iniciar_sesion | Aprobado |
| CP-INT-093 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_eliminar_una_actividad_vuelve_a_la_lista_filtrada | Aprobado |
| CP-INT-094 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_filtrar_actividades_por_cada_criterio | Aprobado |
| CP-INT-095 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_filtrar_compromisos_por_plazo_estado_y_periodo | Aprobado |
| CP-INT-096 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_la_agenda_filtra_por_plazo | Aprobado |
| CP-INT-097 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_la_lista_de_actividades_aplica_los_filtros | Aprobado |
| CP-INT-098 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_la_version_para_imprimir_ofrece_imprimir_y_oculta_los_filtros | Aprobado |
| CP-INT-099 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_los_valores_invalidos_se_ignoran_en_vez_de_fallar | Aprobado |
| CP-INT-100 | CU-20, CU-20.1, CU-20.2, CU-29 | RF-032, RF-033 | Integración | Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV. | FiltrosYInformesTests.test_un_tipo_de_informe_desconocido_cae_en_actividades | Aprobado |
| CP-TRA-028 | CU-20 | RF-033 | Unitaria | Abre bien en Excel con tildes. | InformesUnitTests.test_el_csv_tiene_bom_separador_punto_y_coma_y_nombre_de_archivo | Aprobado |
| CP-COM-027 | CU-20.1 | RF-033 | Unitaria | Columnas y valores listos para exportar. | FiltrosAgendaUnitTests.test_las_filas_del_informe_incluyen_responsable_y_situacion_del_plazo | Aprobado |
| CP-TRA-029 | CU-20.1 | RF-033 | Unitaria | Columnas y valores listos para exportar. | InformesUnitTests.test_las_filas_de_actividades_traen_los_datos_del_informe | Aprobado |
| CP-TRA-030 | CU-20.1 | RF-033 | Unitaria | Una fila por delegación con su cumplimiento y estado. | InformesUnitTests.test_las_filas_de_cumplimiento_incluyen_la_diferencia | Aprobado |
| CP-TRA-031 | CU-20.1 | RF-033 | Unitaria | Sin registros no hay error. | InformesUnitTests.test_un_informe_vacio_solo_trae_la_cabecera | Aprobado |
| CP-TRA-006 | CU-20.2 | RF-032 | Unitaria | Un funcionario del Centro no ve lo de Rural. | AlcanceUnitTests.test_quien_tiene_delegacion_solo_ve_la_suya | Aprobado |
| CP-ACT-002 | CU-23.1 | RF-034 | Unitaria | La versión crece con cada edición. | ActividadEstadoUnitTests.test_cada_guardado_sube_la_version_en_uno | Aprobado |
| CP-ACT-004 | CU-23.1 | RF-034 | Unitaria | Gana el primero que guarda; el otro debe recargar. | ActividadEstadoUnitTests.test_dos_ediciones_simultaneas_la_segunda_se_rechaza | Aprobado |
| CP-ACT-005 | CU-23.1 | RF-034 | Unitaria | El campo oculto version detecta datos viejos. | ActividadEstadoUnitTests.test_el_formulario_rechaza_una_version_desactualizada | Aprobado |
| CP-COM-004 | CU-23.1 | RF-034 | Unitaria | El formulario detecta la versión vieja. | CompromisoFormUnitTests.test_dos_ediciones_simultaneas_la_segunda_se_rechaza | Aprobado |
| CP-COM-006 | CU-23.1 | RF-034 | Unitaria | Gana quien guarda primero. | CompromisoFormUnitTests.test_el_modelo_tambien_rechaza_guardar_con_una_version_vieja | Aprobado |
| CP-MED-012 | CU-25 | RF-024, RF-038 | Unitaria | El máximo computable es configurable por período. | CumplimientoUnitTests.test_el_tope_lo_define_el_parametro_del_periodo | Aprobado |
| CP-ORG-032 | CU-25 | RF-038 | Unitaria | Cambiar un período no altera otro. | ParametroUnitTests.test_cada_periodo_conserva_su_propio_valor | Aprobado |
| CP-ORG-033 | CU-25 | RF-007 | Unitaria | Sin parámetro se usa el valor por defecto. | ParametroUnitTests.test_obtener_parametro_devuelve_el_valor_o_el_defecto | Aprobado |
| CP-ORG-034 | CU-25 | RF-038 | Unitaria | RN-013: los resultados cerrados no cambian. | ParametroUnitTests.test_un_periodo_cerrado_conserva_sus_parametros | Aprobado |
| CP-ORG-035 | CU-25 | RF-038 | Unitaria | Cada período tiene su propio valor por clave. | ParametroUnitTests.test_una_clave_no_se_repite_en_el_mismo_periodo | Aprobado |
| CP-INT-026 | CU-26, CU-30 | RF-001, RF-002, RF-036 | Integración | El Django Admin administra los 19 modelos (las 17 clases, FuncionarioRol y MedicionDelegacion). | AdminTests.test_cada_modelo_se_lista_busca_y_se_abre_para_agregar_y_modificar | Aprobado |
| CP-INT-027 | CU-26, CU-30 | RF-001, RF-002, RF-036 | Integración | El Django Admin administra los 19 modelos (las 17 clases, FuncionarioRol y MedicionDelegacion). | AdminTests.test_estan_registrados_los_19_modelos | Aprobado |
| CP-INT-028 | CU-26, CU-30 | RF-001, RF-002, RF-036 | Integración | El Django Admin administra los 19 modelos (las 17 clases, FuncionarioRol y MedicionDelegacion). | AdminTests.test_un_periodo_cerrado_y_lo_que_depende_de_el_no_se_eliminan | Aprobado |
| CP-INT-029 | CU-26, CU-30 | RF-001, RF-002, RF-036 | Integración | El Django Admin administra los 19 modelos (las 17 clases, FuncionarioRol y MedicionDelegacion). | AdminTests.test_un_usuario_staff_sin_permisos_no_agrega_auditoria | Aprobado |
| CP-INT-166 | CU-26, CU-30 | RF-001, RF-002, RF-036 | Integración | Métodos de Delegacion, Cargo, Funcionario y Auditoria con la base de datos. | OrganizacionAccesoTests.test_delegacion_asigna_funcionario_y_cambia_estado | Aprobado |
| CP-INT-167 | CU-26, CU-30 | RF-001, RF-002, RF-036 | Integración | Métodos de Delegacion, Cargo, Funcionario y Auditoria con la base de datos. | OrganizacionAccesoTests.test_identificadores | Aprobado |
| CP-INT-168 | CU-26, CU-30 | RF-001, RF-002, RF-036 | Integración | Métodos de Delegacion, Cargo, Funcionario y Auditoria con la base de datos. | OrganizacionAccesoTests.test_reasignar_cargo_exige_cargo_vigente | Aprobado |
| CP-INT-169 | CU-26, CU-30 | RF-001, RF-002, RF-036 | Integración | Métodos de Delegacion, Cargo, Funcionario y Auditoria con la base de datos. | OrganizacionAccesoTests.test_registrar_evento_a_nombre_del_funcionario | Aprobado |
| CP-INT-170 | CU-26, CU-30 | RF-001, RF-002, RF-036 | Integración | Métodos de Delegacion, Cargo, Funcionario y Auditoria con la base de datos. | OrganizacionAccesoTests.test_registrar_evento_a_nombre_del_usuario_maestro | Aprobado |
| CP-INT-171 | CU-26, CU-30 | RF-001, RF-002, RF-036 | Integración | Métodos de Delegacion, Cargo, Funcionario y Auditoria con la base de datos. | OrganizacionAccesoTests.test_rol_no_se_repite_para_el_mismo_funcionario | Aprobado |
| CP-INT-172 | CU-26, CU-26.1 | RF-002 | Integración | tiene_rol y control de acceso por rol. | PermisosTests.test_cuenta_inactiva_no_tiene_roles | Aprobado |
| CP-INT-173 | CU-26, CU-26.1 | RF-002 | Integración | tiene_rol y control de acceso por rol. | PermisosTests.test_decorador_deja_pasar_al_rol_permitido_y_redirige_a_los_demas | Aprobado |
| CP-INT-174 | CU-26, CU-26.1 | RF-002 | Integración | tiene_rol y control de acceso por rol. | PermisosTests.test_funcionario_con_varios_roles | Aprobado |
| CP-INT-175 | CU-26, CU-26.1 | RF-002 | Integración | tiene_rol y control de acceso por rol. | PermisosTests.test_funcionario_inactivo_no_aporta_roles | Aprobado |
| CP-INT-176 | CU-26, CU-26.1 | RF-002 | Integración | tiene_rol y control de acceso por rol. | PermisosTests.test_mixin_deja_pasar_al_rol_permitido_y_redirige_a_los_demas | Aprobado |
| CP-INT-177 | CU-26, CU-26.1 | RF-002 | Integración | tiene_rol y control de acceso por rol. | PermisosTests.test_superusuario_y_usuario_maestro_cuentan_como_administrador | Aprobado |
| CP-INT-178 | CU-26, CU-26.1 | RF-002 | Integración | tiene_rol y control de acceso por rol. | PermisosTests.test_tiene_rol_segun_los_roles_del_funcionario | Aprobado |
| CP-INT-179 | CU-26, CU-26.1 | RF-002 | Integración | tiene_rol y control de acceso por rol. | PermisosTests.test_usuario_sin_funcionario_ni_sesion_no_tiene_roles | Aprobado |
| CP-MED-039 | CU-26 | RF-001 | Unitaria | Las desactivadas salen de los resultados. | ResultadosPorDelegacionUnitTests.test_una_delegacion_inactiva_no_aparece | Aprobado |
| CP-ORG-009 | CU-26 | RF-002 | Unitaria | Asignar un funcionario actualiza su delegación. | DelegacionUnitTests.test_asignar_funcionario_cambia_su_delegacion | Aprobado |
| CP-ORG-010 | CU-26 | RF-001 | Unitaria | Dos delegaciones no pueden llamarse igual. | DelegacionUnitTests.test_el_nombre_de_la_delegacion_es_unico | Aprobado |
| CP-ORG-011 | CU-26 | RF-001 | Unitaria | Desactivar conserva el registro y su historial. | DelegacionUnitTests.test_set_estado_activa_y_desactiva_sin_borrar | Aprobado |
| CP-ORG-012 | CU-26 | RF-002 | Unitaria | Sin contraseña no hay alta. | FuncionarioFormUnitTests.test_al_crear_la_contrasena_es_obligatoria | Aprobado |
| CP-ORG-014 | CU-26 | RF-002, RNF-004 | Unitaria | La confirmación debe ser igual. | FuncionarioFormUnitTests.test_las_contrasenas_deben_coincidir | Aprobado |
| CP-ORG-015 | CU-26 | RF-002 | Unitaria | Las listas solo muestran opciones vigentes. | FuncionarioFormUnitTests.test_no_se_ofrecen_cargos_retirados_ni_delegaciones_inactivas | Aprobado |
| CP-ORG-016 | CU-26 | RF-002 | Unitaria | El alta crea la cuenta, el funcionario y sus roles. | FuncionarioFormUnitTests.test_un_alta_valida_crea_cuenta_funcionario_y_roles | Aprobado |
| CP-ORG-017 | CU-26 | RF-002 | Unitaria | Sin cuentas duplicadas, sin distinguir mayúsculas. | FuncionarioFormUnitTests.test_un_nombre_de_usuario_repetido_se_rechaza | Aprobado |
| CP-ORG-018 | CU-26 | RF-002, RNF-004 | Unitaria | Se aplican los validadores de contraseña. | FuncionarioFormUnitTests.test_una_contrasena_debil_se_rechaza | Aprobado |
| CP-ORG-019 | CU-26 | RF-002 | Unitaria | Dos funcionarios no comparten identificador. | FuncionarioUnitTests.test_el_identificador_institucional_es_unico | Aprobado |
| CP-ORG-020 | CU-26 | RF-002 | Unitaria | No se reasigna a un cargo retirado. | FuncionarioUnitTests.test_reasignar_a_un_cargo_no_vigente_se_rechaza | Aprobado |
| CP-ORG-021 | CU-26 | RF-002 | Unitaria | Un funcionario puede pasar a un cargo vigente. | FuncionarioUnitTests.test_reasignar_cargo_vigente | Aprobado |
| CP-TRA-022 | CU-26 | RF-002 | Unitaria | Quien tiene el rol entra. | DecoradorRolUnitTests.test_con_el_rol_correcto_ejecuta_la_vista | Aprobado |
| CP-TRA-032 | CU-26 | RF-001 | Unitaria | La consulta se arma sin error. | MantenedoresUnitTests.test_cada_mantenedor_apunta_a_un_modelo_y_un_formulario_coherentes | Aprobado |
| CP-TRA-034 | CU-26 | RF-002 | Unitaria | Sin cuenta activa no inicia sesión. | MantenedoresUnitTests.test_desactivar_un_funcionario_desactiva_tambien_su_cuenta | Aprobado |
| CP-TRA-036 | CU-26 | RF-002 | Unitaria | Los permisos consultan esos nombres. | MantenedoresUnitTests.test_los_roles_del_sistema_no_se_eliminan_pero_uno_propio_si | Aprobado |
| CP-TRA-039 | CU-26 | RF-001 | Unitaria | Las ocho tablas maestras. | MantenedoresUnitTests.test_son_exactamente_ocho_mantenedores | Aprobado |
| CP-TRA-040 | CU-26 | RF-001 | Unitaria | Presentación de las columnas del listado. | MantenedoresUnitTests.test_texto_formatea_booleanos_fechas_y_vacios | Aprobado |
| CP-TRA-041 | CU-26 | RF-002 | Unitaria | El procesador de contexto lo calcula. | RolesUnitTests.test_el_menu_de_administracion_depende_del_rol | Aprobado |
| CP-TRA-042 | CU-26 | RF-002 | Unitaria | Dos formas de tener alcance global. | RolesUnitTests.test_el_superusuario_y_el_usuario_maestro_cuentan_como_administrador | Aprobado |
| CP-TRA-043 | CU-26 | RF-002 | Unitaria | La migración crea los roles que consultan los permisos. | RolesUnitTests.test_existen_los_seis_roles_del_sistema | Aprobado |
| CP-TRA-044 | CU-26 | RF-002 | Unitaria | Y None si no hay sesión o ficha. | RolesUnitTests.test_funcionario_de_devuelve_su_funcionario | Aprobado |
| CP-TRA-045 | CU-26 | RF-002 | Unitaria | Un usuario con dos roles tiene ambos. | RolesUnitTests.test_los_roles_salen_del_funcionario | Aprobado |
| CP-TRA-048 | CU-26 | RF-002 | Unitaria | Desactivar al funcionario quita sus permisos. | RolesUnitTests.test_un_funcionario_inactivo_no_aporta_roles | Aprobado |
| CP-TRA-049 | CU-26 | RF-002 | Unitaria | is_active en falso corta el acceso. | RolesUnitTests.test_una_cuenta_desactivada_no_tiene_roles | Aprobado |
| CP-ACT-009 | CU-26.1 | RF-002 | Unitaria | El formulario no ofrece delegaciones ajenas. | ActividadFormUnitTests.test_quien_tiene_delegacion_solo_registra_en_la_suya | Aprobado |
| CP-COM-007 | CU-26.1 | RF-017 | Unitaria | Un funcionario no asigna a otros ni en otra delegación. | CompromisoFormUnitTests.test_quien_tiene_delegacion_solo_se_asigna_a_si_mismo_en_la_suya | Aprobado |
| CP-INT-001 | CU-26.1, CU-29.1 | RF-002, RNF-004 | Integración | Acceso con identidad individual y resultados limitados al ámbito. | AccesoAutenticadoTests.test_coordinador_ve_compromisos_de_todas_las_delegaciones | Aprobado |
| CP-INT-002 | CU-26.1, CU-29.1 | RF-002, RNF-004 | Integración | Acceso con identidad individual y resultados limitados al ámbito. | AccesoAutenticadoTests.test_funcionario_solo_ve_compromisos_de_su_delegacion | Aprobado |
| CP-INT-003 | CU-26.1, CU-29.1 | RF-002, RNF-004 | Integración | Acceso con identidad individual y resultados limitados al ámbito. | AccesoAutenticadoTests.test_logout_invalida_la_sesion | Aprobado |
| CP-INT-004 | CU-26.1, CU-29.1 | RF-002, RNF-004 | Integración | Acceso con identidad individual y resultados limitados al ámbito. | AccesoAutenticadoTests.test_portada_y_territorio_siguen_publicos | Aprobado |
| CP-INT-005 | CU-26.1, CU-29.1 | RF-002, RNF-004 | Integración | Acceso con identidad individual y resultados limitados al ámbito. | AccesoAutenticadoTests.test_usuario_sin_funcionario_no_ve_compromisos | Aprobado |
| CP-INT-006 | CU-26.1, CU-29.1 | RF-002, RNF-004 | Integración | Acceso con identidad individual y resultados limitados al ámbito. | AccesoAutenticadoTests.test_vistas_internas_exigen_inicio_de_sesion | Aprobado |
| CP-INT-038 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable, accesos denegados y cambios del admin auditados. | AuditoriaTests.test_consultar_un_registro_fuera_del_ambito_da_404_y_queda_registrado | Aprobado |
| CP-INT-039 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable, accesos denegados y cambios del admin auditados. | AuditoriaTests.test_el_cambio_de_un_parametro_desde_el_admin_queda_auditado | Aprobado |
| CP-INT-040 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable, accesos denegados y cambios del admin auditados. | AuditoriaTests.test_el_indice_de_mantenedores_enlaza_la_auditoria_solo_al_administrador | Aprobado |
| CP-INT-041 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable, accesos denegados y cambios del admin auditados. | AuditoriaTests.test_el_superusuario_no_puede_agregar_modificar_ni_eliminar_auditoria_y_el_intento_se_registra | Aprobado |
| CP-INT-042 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable, accesos denegados y cambios del admin auditados. | AuditoriaTests.test_la_consulta_de_auditoria_filtra_y_solo_la_ve_el_administrador | Aprobado |
| CP-INT-043 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable, accesos denegados y cambios del admin auditados. | AuditoriaTests.test_los_cambios_hechos_en_el_admin_quedan_auditados | Aprobado |
| CP-INT-044 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable, accesos denegados y cambios del admin auditados. | AuditoriaTests.test_modificar_lo_de_otro_sin_ser_responsable_ni_autor_queda_registrado | Aprobado |
| CP-INT-045 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable, accesos denegados y cambios del admin auditados. | AuditoriaTests.test_sin_sesion_no_se_registra_acceso_denegado | Aprobado |
| CP-INT-046 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable, accesos denegados y cambios del admin auditados. | AuditoriaTests.test_un_acceso_denegado_por_rol_queda_registrado | Aprobado |
| CP-INT-047 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable, accesos denegados y cambios del admin auditados. | AuditoriaTests.test_un_codigo_inexistente_da_404_sin_registrar_acceso_denegado | Aprobado |
| CP-INT-048 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable, accesos denegados y cambios del admin auditados. | AuditoriaTests.test_un_evento_registrado_no_se_modifica_ni_se_elimina | Aprobado |
| CP-INT-049 | CU-26.1, CU-30, CU-30.1 | RF-036, RNF-008 | Integración | Auditoría inmutable, accesos denegados y cambios del admin auditados. | AuditoriaTests.test_un_rechazo_por_regla_de_negocio_no_cuenta_como_acceso_denegado | Aprobado |
| CP-ORG-013 | CU-26.1 | RF-002 | Unitaria | Evita que el administrador se bloquee a sí mismo. | FuncionarioFormUnitTests.test_el_actor_no_puede_desactivar_su_propia_cuenta | Aprobado |
| CP-TRA-007 | CU-26.1 | RF-002 | Unitaria | Otro funcionario recibe el mensaje de solo autor. | AlcanceUnitTests.test_solo_el_autor_o_la_coordinacion_modifican | Aprobado |
| CP-TRA-009 | CU-26.1 | RF-002 | Unitaria | Una cuenta sin ficha no consulta registros. | AlcanceUnitTests.test_un_usuario_sin_funcionario_no_ve_nada | Aprobado |
| CP-TRA-023 | CU-26.1 | RF-002 | Unitaria | El texto que ve el usuario. | DecoradorRolUnitTests.test_el_mensaje_de_permiso_es_el_definido | Aprobado |
| CP-TRA-024 | CU-26.1 | RF-036 | Unitaria | El intento nombra lo que se quiso ver. | DecoradorRolUnitTests.test_registrar_acceso_denegado_guarda_entidad_e_identificador | Aprobado |
| CP-TRA-025 | CU-26.1 | RF-036 | Unitaria | Sin identidad no hay a quién atribuir el intento. | DecoradorRolUnitTests.test_registrar_acceso_denegado_ignora_al_anonimo | Aprobado |
| CP-TRA-026 | CU-26.1 | RF-036 | Unitaria | Un rol insuficiente queda en la auditoría. | DecoradorRolUnitTests.test_sin_el_rol_redirige_y_registra_el_intento | Aprobado |
| CP-TRA-027 | CU-26.1 | RF-002 | Unitaria | El anónimo va al login y no deja auditoría. | DecoradorRolUnitTests.test_sin_sesion_redirige_al_login | Aprobado |
| CP-TRA-037 | CU-26.1 | RF-002 | Unitaria | Evita el bloqueo de quien administra. | MantenedoresUnitTests.test_nadie_desactiva_su_propia_cuenta | Aprobado |
| CP-TRA-038 | CU-26.1 | RF-002 | Unitaria | La coordinación no administra cuentas ni roles. | MantenedoresUnitTests.test_roles_y_funcionarios_son_solo_de_administracion | Aprobado |
| CP-TRA-047 | CU-26.1 | RF-002 | Unitaria | Sin sesión no hay permisos. | RolesUnitTests.test_un_anonimo_no_tiene_roles | Aprobado |
| CP-ACT-011 | CU-27 | RF-004 | Unitaria | Un tipo desactivado no se puede elegir en registros nuevos. | ActividadFormUnitTests.test_solo_se_ofrecen_tipos_de_atencion_activos | Aprobado |
| CP-ORG-005 | CU-27 | RF-004 | Unitaria | Los registros anteriores conservan el elemento desactivado. | CatalogoUnitTests.test_desactivar_oculta_el_elemento_pero_no_toca_los_registros_historicos | Aprobado |
| CP-ORG-008 | CU-27 | RF-004 | Unitaria | Un tipo inventado no es válido. | CatalogoUnitTests.test_el_tipo_debe_ser_uno_del_catalogo | Aprobado |
| CP-TRA-033 | CU-27 | RF-004 | Unitaria | Desactivar conserva la fila. | MantenedoresUnitTests.test_cambiar_baja_de_delegacion_y_catalogo | Aprobado |
| CP-ORG-006 | CU-27.1 | RF-004 | Unitaria | Un código repetido no se guarda. | CatalogoUnitTests.test_el_codigo_de_un_elemento_es_unico | Aprobado |
| CP-ORG-007 | CU-27.1 | RF-004 | Unitaria | El mantenedor informa el código repetido. | CatalogoUnitTests.test_el_formulario_rechaza_un_codigo_duplicado | Aprobado |
| CP-ORG-036 | CU-28 | RF-026 | Unitaria | Días que faltan para el término. | PeriodoPuroUnitTests.test_dias_restantes | Aprobado |
| CP-ORG-037 | CU-28 | RF-005 | Unitaria | Un rango invertido se rechaza. | PeriodoPuroUnitTests.test_la_fecha_de_termino_no_puede_ser_anterior_al_inicio | Aprobado |
| CP-ORG-042 | CU-28 | RF-005 | Unitaria | Inicio y término el mismo día es válido. | PeriodoPuroUnitTests.test_un_dia_de_duracion_es_valido | Aprobado |
| CP-ORG-043 | CU-28 | RF-005 | Unitaria | Al finalizar el ciclo el período se cierra. | PeriodoUnitTests.test_cerrar_periodo_cambia_el_estado | Aprobado |
| CP-ORG-044 | CU-28 | RF-007 | Unitaria | RN-006: el umbral es un porcentaje. | PeriodoUnitTests.test_el_formulario_exige_un_umbral_entre_0_y_100 | Aprobado |
| CP-ORG-045 | CU-28 | RF-005 | Unitaria | El mantenedor informa la fecha de término anterior. | PeriodoUnitTests.test_el_formulario_rechaza_fechas_invertidas | Aprobado |
| CP-ORG-046 | CU-28 | RF-005 | Unitaria | Septiembre tiene 30 días computables. | PeriodoUnitTests.test_guardar_calcula_los_dias_computables | Aprobado |
| CP-ORG-047 | CU-28 | RF-005 | Unitaria | Con 100 % el período se abre. | PeriodoUnitTests.test_iniciar_periodo_con_100_pasa_a_abierto | Aprobado |
| CP-ORG-048 | CU-28 | RF-006 | Unitaria | RN-001: cada cargo debe sumar exactamente 100 %. | PeriodoUnitTests.test_iniciar_periodo_exige_ponderaciones_que_sumen_100 | Aprobado |
| CP-ORG-051 | CU-28 | RF-005 | Unitaria | Un borrador no se cierra. | PeriodoUnitTests.test_solo_se_cierra_un_periodo_abierto | Aprobado |
| CP-ORG-052 | CU-28 | RF-005 | Unitaria | Un período abierto no se inicia otra vez. | PeriodoUnitTests.test_solo_se_inicia_un_periodo_en_borrador | Aprobado |
| CP-TRA-035 | CU-28 | RF-005 | Unitaria | Borrador se inicia, abierto se cierra, cerrado se reabre con motivo. | MantenedoresUnitTests.test_las_acciones_de_un_periodo_dependen_de_su_estado | Aprobado |
| CP-ACT-041 | CU-28.1 | RF-038 | Unitaria | RN-013: un período cerrado queda congelado. | ValidacionUnitTests.test_con_el_periodo_cerrado_los_indicadores_no_se_recalculan | Aprobado |
| CP-MED-014 | CU-28.1 | RF-038 | Unitaria | RN-013: los resultados cerrados no cambian. | CumplimientoUnitTests.test_no_se_genera_un_indicador_de_un_periodo_cerrado | Aprobado |
| CP-ORG-023 | CU-28.1 | RF-038 | Unitaria | RN-013 alcanza a los ítems del período. | ItemMedibleUnitTests.test_en_un_periodo_cerrado_no_se_crean_ni_modifican_items | Aprobado |
| CP-ORG-049 | CU-28.1 | RF-036, RF-038 | Unitaria | La reapertura es explícita y queda registrada. | PeriodoUnitTests.test_reabrir_deja_auditoria_y_sube_la_version_de_parametros | Aprobado |
| CP-ORG-050 | CU-28.1 | RF-036 | Unitaria | Sin motivo no hay reapertura. | PeriodoUnitTests.test_reabrir_exige_un_motivo | Aprobado |
| CP-ORG-053 | CU-28.1 | RF-038 | Unitaria | Un período abierto no se reabre. | PeriodoUnitTests.test_solo_se_reabre_un_periodo_cerrado | Aprobado |
| CP-ORG-054 | CU-28.1 | RF-038 | Unitaria | RN-013: tampoco se borra. | PeriodoUnitTests.test_un_periodo_cerrado_no_se_elimina | Aprobado |
| CP-ORG-055 | CU-28.1 | RF-038 | Unitaria | RN-013: guardar un cerrado se rechaza. | PeriodoUnitTests.test_un_periodo_cerrado_no_se_modifica | Aprobado |
| CP-TRA-004 | CU-28.1 | RF-038 | Unitaria | RN-013 alcanza a la edición de actividades. | AlcanceUnitTests.test_bloqueo_de_una_actividad_de_periodo_cerrado | Aprobado |
| CP-MED-027 | CU-29 | RF-032 | Unitaria | El período pedido se respeta. | PeriodoVigenteUnitTests.test_se_puede_elegir_otro_periodo_con_indicadores | Aprobado |
| CP-MED-031 | CU-29 | RF-032 | Unitaria | Un id inexistente o con texto no rompe la pantalla. | PeriodoVigenteUnitTests.test_un_valor_invalido_cae_en_el_periodo_por_defecto | Aprobado |
| CP-MED-037 | CU-29 | RF-032 | Unitaria | Buscar «rur» deja solo Rural. | ResultadosPorDelegacionUnitTests.test_se_filtra_por_texto | Aprobado |
| CP-TRA-002 | CU-29.1 | RF-032 | Unitaria | Alcance global. | AlcanceUnitTests.test_administracion_y_coordinacion_ven_todas_las_actividades | Aprobado |
| CP-TRA-005 | CU-29.1 | RF-032 | Unitaria | Alcance global en la agenda. | AlcanceUnitTests.test_los_compromisos_de_administracion_incluyen_todas_las_delegaciones | Aprobado |
| CP-TRA-008 | CU-29.1 | RF-032 | Unitaria | Sin delegación, solo sus propias actividades. | AlcanceUnitTests.test_un_funcionario_sin_delegacion_solo_ve_lo_que_registro | Aprobado |
| CP-TRA-046 | CU-29.1 | RF-032 | Unitaria | El resto queda limitado a su ámbito. | RolesUnitTests.test_solo_administracion_y_coordinacion_ven_todo | Aprobado |
| CP-TRA-011 | CU-30 | RF-036 | Unitaria | Un superusuario con registro maestro se atribuye al maestro. | AuditoriaUnitTests.test_el_usuario_maestro_tiene_prioridad_sobre_el_funcionario | Aprobado |
| CP-TRA-012 | CU-30 | RF-036, RNF-004 | Unitaria | Los campos sensibles se excluyen. | AuditoriaUnitTests.test_las_contrasenas_no_quedan_en_la_auditoria | Aprobado |
| CP-TRA-013 | CU-30 | RF-036 | Unitaria | Al crear solo hay valores nuevos. | AuditoriaUnitTests.test_los_cambios_de_un_formulario_nuevo_no_tienen_valor_anterior | Aprobado |
| CP-TRA-014 | CU-30 | RF-036 | Unitaria | Los campos intactos no ensucian el registro. | AuditoriaUnitTests.test_los_cambios_de_una_edicion_traen_antes_y_despues_solo_de_lo_que_cambio | Aprobado |
| CP-TRA-015 | CU-30 | RF-036 | Unitaria | Antes y después, con tildes sin escapar. | AuditoriaUnitTests.test_los_valores_se_guardan_como_json_legible | Aprobado |
| CP-TRA-016 | CU-30 | RF-036 | Unitaria | Objetos y relaciones se guardan como texto. | AuditoriaUnitTests.test_plano_convierte_valores_a_tipos_guardables | Aprobado |
| CP-TRA-019 | CU-30 | RF-036 | Unitaria | Quién, qué, sobre qué registro y cuándo. | AuditoriaUnitTests.test_un_evento_queda_a_nombre_del_funcionario | Aprobado |
| CP-TRA-021 | CU-30 | RF-036 | Unitaria | Sin doble codificación. | AuditoriaUnitTests.test_un_texto_se_guarda_tal_cual_y_none_queda_vacio | Aprobado |
| CP-TRA-017 | CU-30.1 | RNF-008 | Unitaria | Update y delete de un queryset se rechazan. | AuditoriaUnitTests.test_tampoco_se_modifica_ni_elimina_en_bloque | Aprobado |
| CP-TRA-018 | CU-30.1 | RNF-008 | Unitaria | Ni individualmente. | AuditoriaUnitTests.test_un_evento_no_se_elimina | Aprobado |
| CP-TRA-020 | CU-30.1 | RNF-008 | Unitaria | La auditoría no se reescribe. | AuditoriaUnitTests.test_un_evento_registrado_no_se_puede_guardar_de_nuevo | Aprobado |
| CP-LOGIN-001 | HU-26 | RF-002, RNF-004 | Unitaria | Login con usuario y contraseña válidos | ValidarCredencialesTests.test_login_con_usuario_y_contrasena_validos | Aprobado |
| CP-LOGIN-002 | HU-26 | RF-002, RNF-004 | Unitaria | Login con contraseña incorrecta | ValidarCredencialesTests.test_login_con_contrasena_incorrecta | Aprobado |
| CP-LOGIN-003 | HU-26 | RF-002, RNF-004 | Unitaria | Login con usuario inexistente | ValidarCredencialesTests.test_login_con_usuario_inexistente | Aprobado |
| CP-LOGIN-004 | HU-26 | RF-002, RNF-004 | Unitaria | Login con usuario vacío | ValidarCredencialesTests.test_login_con_usuario_vacio | Aprobado |
| CP-LOGIN-005 | HU-26 | RF-002, RNF-004 | Unitaria | Login con contraseña vacía | ValidarCredencialesTests.test_login_con_contrasena_vacia | Aprobado |
| CP-LOGIN-006 | HU-26 | RF-002, RNF-004 | Unitaria | Login con ambos campos vacíos | ValidarCredencialesTests.test_login_con_usuario_y_contrasena_vacios | Aprobado |
| CP-LOGIN-007 | HU-26 | RF-002, RNF-004 | Unitaria | Login con usuario inactivo | ValidarCredencialesTests.test_login_con_usuario_inactivo | Aprobado |
| CP-LOGIN-008 | HU-26 | RF-002, RNF-004 | Unitaria | Login con formato inválido: solo espacios, texto de inyección y usuario de 151 caracteres | ValidarCredencialesTests.test_login_con_formato_invalido | Aprobado |
| CP-INT-152 | - | - | Integración | Migrar copia y transforma los datos | MigracionDatosTests.test_migrar_copia_y_transforma_los_datos | Aprobado |
| CP-INT-153 | - | - | Integración | Revertir deja los datos como antes | MigracionDatosTests.test_revertir_deja_los_datos_como_antes | Aprobado |
| CP-INT-188 | - | - | Integración | Carga el modelo nuevo con sus datos de demostracion | SeedDemoTests.test_carga_el_modelo_nuevo_con_sus_datos_de_demostracion | Aprobado |
| CP-INT-189 | - | - | Integración | Convive con datos ya migrados sin duplicarlos | SeedDemoTests.test_convive_con_datos_ya_migrados_sin_duplicarlos | Aprobado |
| CP-INT-190 | - | - | Integración | Cuentas demo y delegados inactivos | SeedDemoTests.test_cuentas_demo_y_delegados_inactivos | Aprobado |
| CP-INT-191 | - | - | Integración | La demo se ve en la aplicacion | SeedDemoTests.test_la_demo_se_ve_en_la_aplicacion | Aprobado |
| CP-INT-192 | - | - | Integración | Repetir la carga no duplica nada | SeedDemoTests.test_repetir_la_carga_no_duplica_nada | Aprobado |
| CP-PLAN-001 | - | - | Unitaria | Cobertura distingue prueba propia subcasos y sin prueba | ArmadoDelPlanTests.test_cobertura_distingue_prueba_propia_subcasos_y_sin_prueba | Aprobado |
| CP-PLAN-002 | - | - | Unitaria | Cobertura por rf cuenta unitarias e integracion | ArmadoDelPlanTests.test_cobertura_por_rf_cuenta_unitarias_e_integracion | Aprobado |
| CP-PLAN-003 | - | - | Unitaria | El catalogo tiene los casos de uso y los 38 requisitos | ArmadoDelPlanTests.test_el_catalogo_tiene_los_casos_de_uso_y_los_38_requisitos | Aprobado |
| CP-PLAN-004 | - | - | Unitaria | El documento incluye resumen tabla y fichas de login | ArmadoDelPlanTests.test_el_documento_incluye_resumen_tabla_y_fichas_de_login | Aprobado |
| CP-PLAN-005 | - | - | Unitaria | Hay una ficha por cada caso de login | ArmadoDelPlanTests.test_hay_una_ficha_por_cada_caso_de_login | Aprobado |
| CP-PLAN-006 | - | - | Unitaria | Los cp se asignan por modulo y respetan los declarados | ArmadoDelPlanTests.test_los_cp_se_asignan_por_modulo_y_respetan_los_declarados | Aprobado |
| CP-PLAN-007 | - | - | Unitaria | El docstring de un metodo define cp cu nombre y requisitos | LecturaDeDocstringsTests.test_el_docstring_de_un_metodo_define_cp_cu_nombre_y_requisitos | Aprobado |
| CP-PLAN-008 | - | - | Unitaria | Los cu se ordenan de forma natural | LecturaDeDocstringsTests.test_los_cu_se_ordenan_de_forma_natural | Aprobado |
| CP-PLAN-009 | - | - | Unitaria | Los requisitos se leen y los rangos se expanden | LecturaDeDocstringsTests.test_los_requisitos_se_leen_y_los_rangos_se_expanden | Aprobado |
| CP-PLAN-010 | - | - | Unitaria | Sin docstring de metodo se usa el de la clase | LecturaDeDocstringsTests.test_sin_docstring_de_metodo_se_usa_el_de_la_clase | Aprobado |
| CP-PLAN-011 | - | - | Unitaria | Sin ningun docstring valido la prueba queda sin cu | LecturaDeDocstringsTests.test_sin_ningun_docstring_valido_la_prueba_queda_sin_cu | Aprobado |
| CP-PLAN-012 | - | - | Unitaria | Un metodo sin cp declarado lo deja para asignar | LecturaDeDocstringsTests.test_un_metodo_sin_cp_declarado_lo_deja_para_asignar | Aprobado |
| CP-PLAN-013 | - | - | Unitaria | Un rnf no se confunde con un rf | LecturaDeDocstringsTests.test_un_rnf_no_se_confunde_con_un_rf | Aprobado |

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
| Responsable | _a completar_ |
| Fecha ejecución | 21-10-2026 |
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
| Responsable | _a completar_ |
| Fecha ejecución | 21-10-2026 |
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
| Responsable | _a completar_ |
| Fecha ejecución | 21-10-2026 |
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
| Responsable | _a completar_ |
| Fecha ejecución | 21-10-2026 |
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
| Responsable | _a completar_ |
| Fecha ejecución | 21-10-2026 |
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
| Responsable | _a completar_ |
| Fecha ejecución | 21-10-2026 |
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
| Responsable | _a completar_ |
| Fecha ejecución | 21-10-2026 |
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
| Responsable | _a completar_ |
| Fecha ejecución | 21-10-2026 |
| Observaciones | Prueba `ValidarCredencialesTests.test_login_con_formato_invalido`. |
