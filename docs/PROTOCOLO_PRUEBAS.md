# Protocolo de pruebas del SGR (Evaluación 3)

Generado con `python manage.py protocolo_pruebas` el 24-11-2026. No se edita a mano: los datos de los casos, defectos y responsables están en `delegaciones_app/protocolo.py` y los resultados salen de ejecutar las pruebas automáticas.

## 1. Entorno de ejecución

| Campo | Valor |
|---|---|
| Fecha | 24-11-2026 |
| Python | 3.13.14 |
| Django | 5.2.19 |
| Base de datos de pruebas | sqlite3 (base temporal creada por el runner de Django) |
| Suite completa | 794 pruebas, 0 con falla |

## 2. Indicadores de cobertura y resultados

| Indicador | Cantidad |
|---|---|
| Planificados | 35 |
| Ejecutados | 33 |
| Aprobados | 33 |
| Fallidos | 0 |
| Bloqueados | 0 |
| No ejecutados (manuales pendientes) | 2 |
| Defectos registrados | 8 |
| Defectos corregidos | 8 |
| Casos reejecutados tras corrección | 6 |
| Pruebas automáticas que respaldan casos | 103 |
| Requerimientos de la guía cubiertos | 12 |

### Cobertura por requerimiento de la guía

| Requerimiento | Descripción | RF | Casos | Estado |
|---|---|---|---|---|
| REQ-01 | Autenticación, roles y permisos | RF-001, RF-002 | CP-01, CP-29, CP-35 | Aprobado |
| REQ-02 | Contraseña temporal, cambio obligatorio en el primer ingreso y recuperación | RF-051 | CP-02, CP-03, CP-04, CP-05 | Con pendientes |
| REQ-03 | CRUD con validaciones de delegaciones, territorios, usuarios, cargos, roles, vecinos, juntas de vecinos, hitos, tipos y subtipos, metas y trimestres | RF-001 a RF-007, RF-055 a RF-058 | CP-25, CP-26, CP-27, CP-28 | Aprobado |
| REQ-04 | Actividades, gestiones sociales y evidencias; ingreso opcional al Tubo | RF-009, RF-012, RF-015, RF-059 | CP-23 | Aprobado |
| REQ-05 | Metas por funcionario y trimestre con cantidad, ponderación y tope de 120 %; solo registros aprobados que ponderan | RF-007, RF-023, RF-024, RF-045 | CP-12, CP-13, CP-18 | Aprobado |
| REQ-06 | Verificación: pendiente, aprobada, rechazada o más antecedentes; lo aprobado no se modifica | RF-013, RF-014, RF-052 | CP-09, CP-10, CP-11 | Aprobado |
| REQ-07 | Tubo de seguimiento y Tubo de cartas; toda la delegación consulta, cada uno modifica lo suyo no cerrado | RF-016 a RF-018, RF-053 | CP-20, CP-21 | Aprobado |
| REQ-08 | Dashboard y semáforo por funcionario y delegación, con filtros y gráficos | RF-027 a RF-029, RF-060 | CP-30, CP-31, CP-32 | Con pendientes |
| REQ-09 | Fechas y códigos automáticos, autocompletado, búsqueda dinámica por código, RUT o nombre, filtros | RF-011, RF-032, RF-054, RF-062 | CP-19, CP-22, CP-24, CP-33 | Aprobado |
| REQ-10 | Reglas del cliente: delegado, nombre y teléfono, 7 diarias, cierre semanal, gestión previa, felicitaciones, ausencias | RF-040 a RF-047 | CP-14, CP-15, CP-16, CP-17 | Aprobado |
| REQ-11 | Seguridad: hash, validación en servidor, autorización por rol y propiedad, sesiones, tokens, acceso a evidencias | RNF-004, RF-061 | CP-06, CP-07, CP-08 | Aprobado |
| REQ-12 | Entorno reproducible: respaldo y recuperación de datos y archivos | RNF-012 | CP-34 | Aprobado |

## 3. Resumen de casos

| Código | Nombre | Req. | Prioridad | Tipo | Perfil | Estado | Defecto |
|---|---|---|---|---|---|---|---|
| CP-01 | Ingreso con credenciales válidas e inválidas | REQ-01 | Alta | Funcional positiva y negativa | Cualquiera | Aprobado | - |
| CP-02 | Crear usuario con contraseña temporal | REQ-02 | Alta | Funcional positiva | Administrador | Aprobado | - |
| CP-03 | Cambio obligatorio en el primer ingreso | REQ-02 | Alta | Seguridad | Profesional con contraseña temporal | Aprobado | - |
| CP-04 | Recuperación de contraseña con token que vence | REQ-02 | Alta | Seguridad | Sin sesión | Aprobado | - |
| CP-05 | Envío real del correo de recuperación (SMTP) | REQ-02 | Media | Configuración | Sin sesión | No ejecutado | - |
| CP-06 | Bloqueo de ingreso por intentos fallidos | REQ-11 | Alta | Seguridad | Sin sesión | Aprobado | - |
| CP-07 | Contraseñas con hash, sesión que vence y vistas protegidas | REQ-11 | Alta | Seguridad | Cualquiera | Aprobado | - |
| CP-08 | Autorización por perfil y control de acceso a evidencias | REQ-11 | Alta | Permisos | Profesional y usuario sin sesión | Aprobado | - |
| CP-09 | Solicitar más antecedentes | REQ-06 | Alta | Funcional positiva y negativa | Delegado (revisor) y Profesional (autor) | Aprobado | - |
| CP-10 | Completar antecedentes y aprobar | REQ-06 | Alta | Funcional positiva | Profesional (autor) y Delegado | Aprobado | DEF-07 |
| CP-11 | Bloqueo posterior a la aprobación | REQ-06 | Alta | Funcional negativa | Profesional (autor) y Coordinador | Aprobado | - |
| CP-12 | Tope de cumplimiento de 120 % | REQ-05 | Alta | Cálculo / límite | Sistema | Aprobado | - |
| CP-13 | Solo cuentan registros aprobados que ponderan | REQ-05 | Alta | Cálculo | Sistema | Aprobado | - |
| CP-14 | Límite diario de siete actividades | REQ-10 | Alta | Límite | Profesional | Aprobado | - |
| CP-15 | Cierre semanal | REQ-10 | Alta | Límite | Profesional | Aprobado | - |
| CP-16 | Felicitaciones con respaldo formal | REQ-10 | Alta | Cálculo | Delegado (informa) y Coordinador (decide) | Aprobado | - |
| CP-17 | Ausencias ajustan el semáforo | REQ-10 | Alta | Cálculo | Delegado | Aprobado | - |
| CP-18 | Meta única por funcionario e ítem del trimestre | REQ-05 | Media | Validación | Coordinador | Aprobado | - |
| CP-19 | Búsqueda dinámica por código, RUT o nombre | REQ-09 | Alta | Funcional positiva y negativa | Profesional de la delegación | Aprobado | - |
| CP-20 | Tubo de cartas | REQ-07 | Alta | Funcional positiva | Profesional | Aprobado | DEF-02, DEF-06 |
| CP-21 | Permisos del Tubo | REQ-07 | Alta | Permisos | Profesional compañero, responsable y Coordinador | Aprobado | DEF-04, DEF-05 |
| CP-22 | Filtros del Tubo y RUT válido | REQ-09 | Media | Validación / filtros | Profesional | Aprobado | - |
| CP-23 | Actividad y gestión social ingresan o no al Tubo | REQ-04 | Alta | Funcional positiva | Profesional | Aprobado | DEF-03 |
| CP-24 | Autocompletado desde el registro de vecinos | REQ-09 | Media | Funcional positiva y negativa | Profesional | Aprobado | - |
| CP-25 | Vecinos: RUT, unicidad y ámbito | REQ-03 | Alta | Validación / permisos | Coordinador y Delegado | Aprobado | - |
| CP-26 | Membresía y dirigencia en juntas de vecinos | REQ-03 | Alta | Validación | Coordinador o Delegado | Aprobado | - |
| CP-27 | Hitos con responsables | REQ-03 | Media | Funcional positiva y negativa | Coordinador | Aprobado | - |
| CP-28 | Territorios, tipos y subtipos de atención | REQ-03 | Media | Validación / permisos | Coordinador y Delegado | Aprobado | - |
| CP-29 | Permisos de los perfiles sobre las tablas nuevas | REQ-01 | Alta | Permisos | Todos | Aprobado | - |
| CP-30 | Dashboard con gráficos y tabla de datos | REQ-08 | Alta | Funcional positiva | Coordinador | Aprobado | - |
| CP-31 | Filtros y ámbito del dashboard | REQ-08 | Alta | Filtros / permisos | Delegado y Coordinador | Aprobado | - |
| CP-32 | Interfaz responsiva, legible y con identidad municipal | REQ-08 | Media | Usabilidad | Todos | No ejecutado | - |
| CP-33 | Regresión: formulario del Tubo con calendario | REQ-09 | Baja | Regresión | Profesional | Aprobado | DEF-01 |
| CP-34 | Respaldo y recuperación | REQ-12 | Alta | Recuperación | Administrador del servidor | Aprobado | - |
| CP-35 | Matriz de accesos por perfil | REQ-01 | Alta | Permisos / seguridad | Administrador, Coordinador, Delegado, Profesional, sin sesión, sin perfil y funcionario desactivado | Aprobado | DEF-08 |

## 4. Fichas de los casos de prueba

### CP-01 · Ingreso con credenciales válidas e inválidas

| Campo | Detalle |
|---|---|
| Código | CP-01 |
| Nombre | Ingreso con credenciales válidas e inválidas |
| Requerimiento asociado | REQ-01: Autenticación, roles y permisos (RF-001, RF-002) |
| Prioridad | Alta |
| Tipo de prueba | Funcional positiva y negativa (automatizada) |
| Precondiciones | Usuario activo registrado. |
| Perfil de usuario | Cualquiera |
| Datos de prueba | Usuario válido / contraseña correcta e incorrecta. |
| Pasos | 1. Abrir /login/. 2. Ingresar usuario y contraseña correctos. 3. Cerrar sesión e ingresar con contraseña incorrecta. |
| Resultado esperado | Con credenciales correctas llega al panel de su perfil; con incorrectas ve un mensaje genérico y no ingresa. |
| Resultado obtenido | Coincide con lo esperado: 3 de 3 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_unit_autenticacion.ValidarCredencialesTests.test_login_con_usuario_y_contrasena_validos; test_unit_autenticacion.ValidarCredencialesTests.test_login_con_contrasena_incorrecta; test_unit_seguridad.AccesoPorPerfilTests.test_el_login_lleva_al_panel_de_cada_perfil |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-02 · Crear usuario con contraseña temporal

| Campo | Detalle |
|---|---|
| Código | CP-02 |
| Nombre | Crear usuario con contraseña temporal |
| Requerimiento asociado | REQ-02: Contraseña temporal, cambio obligatorio en el primer ingreso y recuperación (RF-051) |
| Prioridad | Alta |
| Tipo de prueba | Funcional positiva (automatizada) |
| Precondiciones | Sesión de administrador. |
| Perfil de usuario | Administrador |
| Datos de prueba | Usuario «nuevo.e3», cargo y rol funcionario; contraseña vacía o escrita. |
| Pasos | 1. Ir a Administración → Funcionarios y usuarios → Agregar. 2. Completar los datos dejando la contraseña vacía. 3. Guardar y leer el aviso. 4. Repetir escribiendo una contraseña. |
| Resultado esperado | Se crea la cuenta; el sistema muestra una sola vez la contraseña temporal generada; en ambos casos la cuenta queda marcada para cambiarla; la clave no queda en la auditoría. |
| Resultado obtenido | Coincide con lo esperado: 4 de 4 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.ContrasenaTemporalTests.test_crear_sin_contrasena_genera_una_temporal_y_la_muestra_una_vez; test_evaluacion3.ContrasenaTemporalTests.test_una_contrasena_escrita_al_crear_tambien_es_temporal; test_evaluacion3.ContrasenaTemporalTests.test_la_contrasena_temporal_es_aleatoria_y_robusta; test_evaluacion3.ContrasenaTemporalTests.test_restablecer_desde_la_edicion_genera_otra_temporal |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-03 · Cambio obligatorio en el primer ingreso

| Campo | Detalle |
|---|---|
| Código | CP-03 |
| Nombre | Cambio obligatorio en el primer ingreso |
| Requerimiento asociado | REQ-02: Contraseña temporal, cambio obligatorio en el primer ingreso y recuperación (RF-051) |
| Prioridad | Alta |
| Tipo de prueba | Seguridad (automatizada) |
| Precondiciones | Cuenta creada con contraseña temporal. |
| Perfil de usuario | Profesional con contraseña temporal |
| Datos de prueba | Clave temporal; nueva clave «Personal-Segura-2026» y una débil «123». |
| Pasos | 1. Ingresar con la clave temporal. 2. Intentar abrir Actividades, Tareas y el Dashboard. 3. Intentar una clave débil. 4. Cambiarla por una válida. 5. Abrir Actividades. |
| Resultado esperado | Toda página redirige a «Cambia tu contraseña temporal»; la clave débil se rechaza; tras el cambio el sistema se usa normalmente y el cambio queda auditado; se puede salir sin cambiarla. |
| Resultado obtenido | Coincide con lo esperado: 4 de 4 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.ContrasenaTemporalTests.test_el_primer_ingreso_obliga_a_cambiar_la_contrasena; test_evaluacion3.ContrasenaTemporalTests.test_cambiar_la_contrasena_libera_la_cuenta_y_queda_auditado; test_evaluacion3.ContrasenaTemporalTests.test_la_nueva_contrasena_debe_cumplir_las_reglas; test_evaluacion3.ContrasenaTemporalTests.test_con_contrasena_temporal_se_puede_cerrar_la_sesion |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-04 · Recuperación de contraseña con token que vence

| Campo | Detalle |
|---|---|
| Código | CP-04 |
| Nombre | Recuperación de contraseña con token que vence |
| Requerimiento asociado | REQ-02: Contraseña temporal, cambio obligatorio en el primer ingreso y recuperación (RF-051) |
| Prioridad | Alta |
| Tipo de prueba | Seguridad (automatizada) |
| Precondiciones | Cuenta activa con correo. |
| Perfil de usuario | Sin sesión |
| Datos de prueba | Correo registrado y uno desconocido. |
| Pasos | 1. En /login/ elegir «¿Olvidaste tu contraseña?». 2. Ingresar el correo. 3. Abrir el enlace y fijar la nueva clave. 4. Reusar el enlace. 5. Probar un enlace vencido y un correo desconocido. |
| Resultado esperado | Llega un correo con enlace de un solo uso que vence; la respuesta no revela si el correo existe; recuperar quita la marca de clave temporal. |
| Resultado obtenido | Coincide con lo esperado: 5 de 5 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_unit_seguridad.RecuperarContrasenaTests.test_flujo_completo_de_recuperacion; test_unit_seguridad.RecuperarContrasenaTests.test_el_enlace_no_sirve_dos_veces; test_unit_seguridad.RecuperarContrasenaTests.test_el_enlace_vence; test_unit_seguridad.RecuperarContrasenaTests.test_un_correo_desconocido_no_envia_nada_ni_lo_revela; test_evaluacion3.ContrasenaTemporalTests.test_recuperar_por_correo_quita_la_marca_temporal |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-05 · Envío real del correo de recuperación (SMTP)

| Campo | Detalle |
|---|---|
| Código | CP-05 |
| Nombre | Envío real del correo de recuperación (SMTP) |
| Requerimiento asociado | REQ-02: Contraseña temporal, cambio obligatorio en el primer ingreso y recuperación (RF-051) |
| Prioridad | Media |
| Tipo de prueba | Configuración (manual) |
| Precondiciones | Variables EMAIL_* configuradas en el .env del servidor. |
| Perfil de usuario | Sin sesión |
| Datos de prueba | Correo real de una cuenta demo. |
| Pasos | 1. Ejecutar python manage.py sendtestemail <correo>. 2. Solicitar la recuperación desde /recuperar/. 3. Revisar la bandeja de entrada. |
| Resultado esperado | El correo llega con el enlace y la vigencia; el enlace funciona. |
| Resultado obtenido | Pendiente: caso manual, lo ejecuta el equipo en el entorno desplegado. |
| Estado final | No ejecutado |
| Responsable | Por asignar |
| Fecha de ejecución | - |
| Evidencia | - |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-06 · Bloqueo de ingreso por intentos fallidos

| Campo | Detalle |
|---|---|
| Código | CP-06 |
| Nombre | Bloqueo de ingreso por intentos fallidos |
| Requerimiento asociado | REQ-11: Seguridad: hash, validación en servidor, autorización por rol y propiedad, sesiones, tokens, acceso a evidencias (RNF-004, RF-061) |
| Prioridad | Alta |
| Tipo de prueba | Seguridad (automatizada) |
| Precondiciones | LOGIN_MAX_INTENTOS = 3 en la prueba (5 por defecto). |
| Perfil de usuario | Sin sesión |
| Datos de prueba | Usuario existente con clave incorrecta y luego correcta. |
| Pasos | 1. Ingresar tres veces con clave incorrecta. 2. Ingresar con la clave correcta. 3. Ingresar con otra cuenta. |
| Resultado esperado | El cuarto intento se rechaza aunque la clave sea correcta y queda en la auditoría; otra cuenta no se ve afectada; un ingreso correcto reinicia el contador. |
| Resultado obtenido | Coincide con lo esperado: 3 de 3 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.BloqueoDeIngresoTests.test_tras_los_intentos_fallidos_se_bloquea_aunque_la_clave_sea_correcta; test_evaluacion3.BloqueoDeIngresoTests.test_el_bloqueo_no_afecta_a_otra_cuenta; test_evaluacion3.BloqueoDeIngresoTests.test_un_ingreso_correcto_reinicia_el_contador |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-07 · Contraseñas con hash, sesión que vence y vistas protegidas

| Campo | Detalle |
|---|---|
| Código | CP-07 |
| Nombre | Contraseñas con hash, sesión que vence y vistas protegidas |
| Requerimiento asociado | REQ-11: Seguridad: hash, validación en servidor, autorización por rol y propiedad, sesiones, tokens, acceso a evidencias (RNF-004, RF-061) |
| Prioridad | Alta |
| Tipo de prueba | Seguridad (automatizada) |
| Precondiciones | Usuarios creados. |
| Perfil de usuario | Cualquiera |
| Datos de prueba | Usuario de prueba. |
| Pasos | 1. Revisar el campo password del usuario en la base. 2. Dejar la sesión inactiva 30 minutos. 3. Abrir vistas internas sin sesión. 4. Buscar /admin/. |
| Resultado esperado | La clave se guarda como hash con algoritmo y sal; la sesión vence a los 30 min; sin sesión se pide ingresar; Django Admin no está publicado. |
| Resultado obtenido | Coincide con lo esperado: 4 de 4 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.ContrasenaTemporalTests.test_la_contrasena_se_guarda_como_hash; test_unit_seguridad.CierreDeSesionTests.test_la_sesion_vence_a_los_30_minutos_sin_actividad; test_integracion.AccesoAutenticadoTests.test_vistas_internas_exigen_inicio_de_sesion; test_unit_seguridad.AccesoPorPerfilTests.test_django_admin_no_esta_publicado |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-08 · Autorización por perfil y control de acceso a evidencias

| Campo | Detalle |
|---|---|
| Código | CP-08 |
| Nombre | Autorización por perfil y control de acceso a evidencias |
| Requerimiento asociado | REQ-11: Seguridad: hash, validación en servidor, autorización por rol y propiedad, sesiones, tokens, acceso a evidencias (RNF-004, RF-061) |
| Prioridad | Alta |
| Tipo de prueba | Permisos (automatizada) |
| Precondiciones | Evidencia cargada. |
| Perfil de usuario | Profesional y usuario sin sesión |
| Datos de prueba | Archivo PDF de evidencia; archivo de 6 MB. |
| Pasos | 1. Como Profesional abrir mantenedores críticos, perfiles y auditoría. 2. Abrir el archivo de una evidencia propia. 3. Abrirlo sin sesión. 4. Subir un archivo de más de 5 MB. |
| Resultado esperado | El Profesional no entra a operaciones críticas; el archivo se sirve solo a quien ve la actividad; sin sesión se pide ingresar; el archivo pesado se rechaza. |
| Resultado obtenido | Coincide con lo esperado: 4 de 4 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_unit_seguridad.AccesoPorPerfilTests.test_el_funcionario_no_entra_a_operaciones_criticas; test_integracion.EvidenciaArchivoTests.test_el_autor_abre_el_archivo_en_el_navegador; test_integracion.EvidenciaArchivoTests.test_sin_sesion_se_pide_iniciar_sesion; test_integracion.EvidenciaTamanoTests.test_subir_evidencia_rechaza_un_archivo_demasiado_pesado |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-09 · Solicitar más antecedentes

| Campo | Detalle |
|---|---|
| Código | CP-09 |
| Nombre | Solicitar más antecedentes |
| Requerimiento asociado | REQ-06: Verificación: pendiente, aprobada, rechazada o más antecedentes; lo aprobado no se modifica (RF-013, RF-014, RF-052) |
| Prioridad | Alta |
| Tipo de prueba | Funcional positiva y negativa (automatizada) |
| Precondiciones | Actividad pendiente con evidencia, meta de 2 actividades. |
| Perfil de usuario | Delegado (revisor) y Profesional (autor) |
| Datos de prueba | Detalle vacío y «Falta la foto del lugar intervenido». |
| Pasos | 1. Como delegado abrir la actividad. 2. Pulsar «Solicitar más antecedentes» sin detalle. 3. Repetir con detalle. 4. Revisar el avance de la meta. |
| Resultado esperado | Sin detalle no se registra; con detalle la actividad y la evidencia quedan «más antecedentes», la decisión queda auditada y la actividad no suma. |
| Resultado obtenido | Coincide con lo esperado: 3 de 3 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.MasAntecedentesTests.test_solicitar_antecedentes_exige_indicar_que_falta; test_evaluacion3.MasAntecedentesTests.test_la_solicitud_deja_la_actividad_en_espera_y_sin_puntaje; test_evaluacion3.MasAntecedentesTests.test_el_boton_de_antecedentes_aparece_para_el_revisor |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-10 · Completar antecedentes y aprobar

| Campo | Detalle |
|---|---|
| Código | CP-10 |
| Nombre | Completar antecedentes y aprobar |
| Requerimiento asociado | REQ-06: Verificación: pendiente, aprobada, rechazada o más antecedentes; lo aprobado no se modifica (RF-013, RF-014, RF-052) |
| Prioridad | Alta |
| Tipo de prueba | Funcional positiva (automatizada) |
| Precondiciones | Actividad con antecedentes solicitados. |
| Perfil de usuario | Profesional (autor) y Delegado |
| Datos de prueba | Nueva foto PNG; lugar «Plaza de Armas». |
| Pasos | 1. Como autor subir una evidencia nueva (o modificar la actividad). 2. Como delegado aprobar. 3. Revisar el avance. |
| Resultado esperado | La actividad vuelve a «pendiente»; al aprobarla suma 1 al avance de la meta. |
| Resultado obtenido | Coincide con lo esperado: 3 de 3 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.MasAntecedentesTests.test_completar_los_antecedentes_vuelve_a_revision_y_al_aprobar_suma; test_evaluacion3.MasAntecedentesTests.test_corregir_la_actividad_la_devuelve_a_revision; test_evaluacion3.MasAntecedentesTests.test_el_autor_ve_la_alerta_y_el_estado_en_su_lista |
| Defecto asociado | DEF-07 |
| Corrección | actividades.html muestra «Completar antecedentes solicitados» y alertas.py agrega la alerta con el detalle pedido por el verificador. |
| Reejecución | DEF-07: Aprobado |

### CP-11 · Bloqueo posterior a la aprobación

| Campo | Detalle |
|---|---|
| Código | CP-11 |
| Nombre | Bloqueo posterior a la aprobación |
| Requerimiento asociado | REQ-06: Verificación: pendiente, aprobada, rechazada o más antecedentes; lo aprobado no se modifica (RF-013, RF-014, RF-052) |
| Prioridad | Alta |
| Tipo de prueba | Funcional negativa (automatizada) |
| Precondiciones | Actividad aprobada. |
| Perfil de usuario | Profesional (autor) y Coordinador |
| Datos de prueba | Actividad aprobada. |
| Pasos | 1. Intentar modificarla. 2. Intentar eliminarla. 3. Intentar subirle evidencia. 4. Intentar cambiar su estado. |
| Resultado esperado | Ninguna operación se permite: la actividad aprobada ya suma al avance y no se modifica. |
| Resultado obtenido | Coincide con lo esperado: 3 de 3 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_integracion.ActividadVistasTests.test_actividad_aprobada_no_se_edita_ni_se_elimina; test_integracion.ActividadVistasTests.test_actividad_aprobada_no_admite_nuevas_evidencias; test_unit_actividades.ActividadEstadoUnitTests.test_una_actividad_aprobada_no_cambia_de_estado |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-12 · Tope de cumplimiento de 120 %

| Campo | Detalle |
|---|---|
| Código | CP-12 |
| Nombre | Tope de cumplimiento de 120 % |
| Requerimiento asociado | REQ-05: Metas por funcionario y trimestre con cantidad, ponderación y tope de 120 %; solo registros aprobados que ponderan (RF-007, RF-023, RF-024, RF-045) |
| Prioridad | Alta |
| Tipo de prueba | Cálculo / límite (automatizada) |
| Precondiciones | Meta de 2 actividades, más actividades aprobadas que la meta; felicitaciones aplicadas. |
| Perfil de usuario | Sistema |
| Datos de prueba | Avance 3 de 2 (150 %). |
| Pasos | 1. Aprobar las actividades. 2. Calcular el indicador. 3. Aplicar felicitaciones. |
| Resultado esperado | El cumplimiento queda en 120 %, también con felicitaciones; el ponderado usa el ponderador de la meta. |
| Resultado obtenido | Coincide con lo esperado: 3 de 3 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_unit_reglas_nuevas.CumplimientoConAjustesTests.test_el_tope_por_defecto_es_120; test_unit_reglas_nuevas.CumplimientoConAjustesTests.test_la_felicitacion_no_supera_el_tope; test_integracion.MedicionTests.test_rn005_tope_por_defecto_120_y_ponderado |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-13 · Solo cuentan registros aprobados que ponderan

| Campo | Detalle |
|---|---|
| Código | CP-13 |
| Nombre | Solo cuentan registros aprobados que ponderan |
| Requerimiento asociado | REQ-05: Metas por funcionario y trimestre con cantidad, ponderación y tope de 120 %; solo registros aprobados que ponderan (RF-007, RF-023, RF-024, RF-045) |
| Prioridad | Alta |
| Tipo de prueba | Cálculo (automatizada) |
| Precondiciones | Actividades aprobadas con y sin contacto, gestión previa e interna. |
| Perfil de usuario | Sistema |
| Datos de prueba | Ver casos. |
| Pasos | 1. Aprobar una actividad sin nombre o teléfono. 2. Aprobar una gestión previa. 3. Aprobar una actividad del delegado (interna). |
| Resultado esperado | Se conservan en el historial pero no suman al avance de la meta. |
| Resultado obtenido | Coincide con lo esperado: 5 de 5 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_unit_reglas_nuevas.PuntajeDeActividadTests.test_una_actividad_aprobada_sin_contacto_no_suma_al_avance; test_unit_reglas_nuevas.PuntajeDeActividadTests.test_sin_nombre_o_telefono_del_usuario_no_puntua; test_unit_reglas_nuevas.PuntajeDeActividadTests.test_la_gestion_previa_conserva_el_historial_sin_puntaje; test_unit_reglas_nuevas.PuntajeDeActividadTests.test_la_actividad_de_una_tarea_interna_es_otra_gestion; test_unit_reglas_nuevas.PuntajeDeActividadTests.test_una_actividad_suelta_marcada_como_interna_es_otra_gestion |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-14 · Límite diario de siete actividades

| Campo | Detalle |
|---|---|
| Código | CP-14 |
| Nombre | Límite diario de siete actividades |
| Requerimiento asociado | REQ-10: Reglas del cliente: delegado, nombre y teléfono, 7 diarias, cierre semanal, gestión previa, felicitaciones, ausencias (RF-040 a RF-047) |
| Prioridad | Alta |
| Tipo de prueba | Límite (automatizada) |
| Precondiciones | 7 actividades registradas por el mismo autor ese día. |
| Perfil de usuario | Profesional |
| Datos de prueba | Octava actividad del día. |
| Pasos | 1. Registrar la octava actividad del día. 2. Registrar una actividad de otro autor el mismo día. |
| Resultado esperado | La octava se rechaza; el límite es por autor y por día. |
| Resultado obtenido | Coincide con lo esperado: 2 de 2 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_unit_reglas_nuevas.PuntajeDeActividadTests.test_el_octavo_ingreso_del_dia_se_rechaza; test_unit_reglas_nuevas.PuntajeDeActividadTests.test_el_limite_diario_es_por_autor_y_por_dia |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-15 · Cierre semanal

| Campo | Detalle |
|---|---|
| Código | CP-15 |
| Nombre | Cierre semanal |
| Requerimiento asociado | REQ-10: Reglas del cliente: delegado, nombre y teléfono, 7 diarias, cierre semanal, gestión previa, felicitaciones, ausencias (RF-040 a RF-047) |
| Prioridad | Alta |
| Tipo de prueba | Límite (automatizada) |
| Precondiciones | Hoy martes o posterior. |
| Perfil de usuario | Profesional |
| Datos de prueba | Actividad con fecha de la semana anterior. |
| Pasos | 1. El lunes registrar una actividad de la semana anterior. 2. El martes intentar lo mismo. 3. Corregir una actividad rechazada antigua sin cambiar su día. |
| Resultado esperado | El lunes se acepta; desde el martes se rechaza el ingreso tardío; la corrección de una ya registrada se permite. |
| Resultado obtenido | Coincide con lo esperado: 4 de 4 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_unit_reglas_nuevas.ReglasNuevasTests.test_el_lunes_permite_la_semana_anterior; test_unit_reglas_nuevas.ReglasNuevasTests.test_desde_martes_la_semana_anterior_se_cierra; test_unit_actividades.ActividadFormUnitTests.test_no_se_ingresa_una_actividad_de_una_semana_cerrada; test_unit_actividades.ActividadFormUnitTests.test_corregir_una_actividad_rechazada_antigua_la_devuelve_a_pendiente |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-16 · Felicitaciones con respaldo formal

| Campo | Detalle |
|---|---|
| Código | CP-16 |
| Nombre | Felicitaciones con respaldo formal |
| Requerimiento asociado | REQ-10: Reglas del cliente: delegado, nombre y teléfono, 7 diarias, cierre semanal, gestión previa, felicitaciones, ausencias (RF-040 a RF-047) |
| Prioridad | Alta |
| Tipo de prueba | Cálculo (automatizada) |
| Precondiciones | Felicitaciones informadas con respaldo. |
| Perfil de usuario | Delegado (informa) y Coordinador (decide) |
| Datos de prueba | Cuatro felicitaciones aplicadas. |
| Pasos | 1. Informar felicitaciones con respaldo. 2. Aplicar algunas y dejar otras informadas. 3. Revisar el cumplimiento. |
| Resultado esperado | Solo cuentan las aplicadas; cada una suma 10 con máximo 3. |
| Resultado obtenido | Coincide con lo esperado: 3 de 3 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_unit_reglas_nuevas.CumplimientoConAjustesTests.test_solo_cuentan_los_ajustes_aplicados; test_unit_reglas_nuevas.CumplimientoConAjustesTests.test_cada_felicitacion_aplicada_suma_10; test_unit_reglas_nuevas.CumplimientoConAjustesTests.test_se_aplican_como_maximo_tres_felicitaciones |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-17 · Ausencias ajustan el semáforo

| Campo | Detalle |
|---|---|
| Código | CP-17 |
| Nombre | Ausencias ajustan el semáforo |
| Requerimiento asociado | REQ-10: Reglas del cliente: delegado, nombre y teléfono, 7 diarias, cierre semanal, gestión previa, felicitaciones, ausencias (RF-040 a RF-047) |
| Prioridad | Alta |
| Tipo de prueba | Cálculo (automatizada) |
| Precondiciones | Funcionario con meta en el período. |
| Perfil de usuario | Delegado |
| Datos de prueba | Ausencia de varios días. |
| Pasos | 1. Registrar la ausencia desde el semáforo. 2. Revisar lo esperado al día. 3. Borrar la ausencia. |
| Resultado esperado | Los días de ausencia se descuentan de lo esperado y el indicador se recalcula; al borrarla vuelve a su valor. |
| Resultado obtenido | Coincide con lo esperado: 2 de 2 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_unit_reglas_nuevas.EsperadoConAusenciasTests.test_las_ausencias_se_descuentan_de_los_dias_computables; test_unit_reglas_nuevas.RecalculoDelSemaforoTests.test_registrar_y_borrar_una_ausencia_recalcula |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-18 · Meta única por funcionario e ítem del trimestre

| Campo | Detalle |
|---|---|
| Código | CP-18 |
| Nombre | Meta única por funcionario e ítem del trimestre |
| Requerimiento asociado | REQ-05: Metas por funcionario y trimestre con cantidad, ponderación y tope de 120 %; solo registros aprobados que ponderan (RF-007, RF-023, RF-024, RF-045) |
| Prioridad | Media |
| Tipo de prueba | Validación (automatizada) |
| Precondiciones | Meta ya asignada. |
| Perfil de usuario | Coordinador |
| Datos de prueba | Mismo ítem y funcionario. |
| Pasos | 1. Asignar otra vez el mismo ítem al mismo funcionario. |
| Resultado esperado | El formulario lo rechaza y la base de datos lo impide con una restricción única. |
| Resultado obtenido | Coincide con lo esperado: 1 de 1 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.MembresiasHitosYCatalogosTests.test_la_meta_de_un_funcionario_no_se_duplica |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-19 · Búsqueda dinámica por código, RUT o nombre

| Campo | Detalle |
|---|---|
| Código | CP-19 |
| Nombre | Búsqueda dinámica por código, RUT o nombre |
| Requerimiento asociado | REQ-09: Fechas y códigos automáticos, autocompletado, búsqueda dinámica por código, RUT o nombre, filtros (RF-011, RF-032, RF-054, RF-062) |
| Prioridad | Alta |
| Tipo de prueba | Funcional positiva y negativa (automatizada) |
| Precondiciones | Tarea AGR-E3-0001 de «María Pérez», RUT 12.345.678-5. |
| Perfil de usuario | Profesional de la delegación |
| Datos de prueba | AGR-E3, 12.345.678-5, 123456785, 12345678, maría, 99999999. |
| Pasos | 1. Abrir Tubo. 2. Escribir cada texto en «Buscar mientras escribes». 3. Observar que los resultados cambian sin recargar. |
| Resultado esperado | Cada búsqueda válida encuentra la tarea; el texto sin coincidencias no; la búsqueda al escribir devuelve solo el bloque de resultados. |
| Resultado obtenido | Coincide con lo esperado: 2 de 2 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.TuboTests.test_busca_por_codigo_rut_o_nombre; test_evaluacion3.TuboTests.test_la_busqueda_al_escribir_devuelve_solo_los_resultados |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-20 · Tubo de cartas

| Campo | Detalle |
|---|---|
| Código | CP-20 |
| Nombre | Tubo de cartas |
| Requerimiento asociado | REQ-07: Tubo de seguimiento y Tubo de cartas; toda la delegación consulta, cada uno modifica lo suyo no cerrado (RF-016 a RF-018, RF-053) |
| Prioridad | Alta |
| Tipo de prueba | Funcional positiva (automatizada) |
| Precondiciones | Delegación con una tarea y una carta. |
| Perfil de usuario | Profesional |
| Datos de prueba | Carta «Solicita uso de multicancha». |
| Pasos | 1. Abrir la pestaña Tubo de cartas. 2. Registrar una carta. 3. Volver al Tubo de trabajo. |
| Resultado esperado | La carta recibe un folio CAR- generado, queda con historial y se ve solo en el Tubo de cartas. |
| Resultado obtenido | Coincide con lo esperado: 2 de 2 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.TuboTests.test_el_tubo_de_cartas_separa_las_cartas; test_evaluacion3.TuboTests.test_registrar_una_carta_genera_su_folio |
| Defecto asociado | DEF-02, DEF-06 |
| Corrección | CompromisoForm: «tipo» opcional con valor por defecto «solicitud» y sin cambio posible al editar (clean_tipo).; Se completaron los datos de la prueba con estado «ingresado». |
| Reejecución | DEF-02: Aprobado; DEF-06: Aprobado |

### CP-21 · Permisos del Tubo

| Campo | Detalle |
|---|---|
| Código | CP-21 |
| Nombre | Permisos del Tubo |
| Requerimiento asociado | REQ-07: Tubo de seguimiento y Tubo de cartas; toda la delegación consulta, cada uno modifica lo suyo no cerrado (RF-016 a RF-018, RF-053) |
| Prioridad | Alta |
| Tipo de prueba | Permisos (automatizada) |
| Precondiciones | Tarea de otro funcionario de la delegación; tarea realizada. |
| Perfil de usuario | Profesional compañero, responsable y Coordinador |
| Datos de prueba | Ver casos. |
| Pasos | 1. Como compañero consultar el Tubo e intentar modificar la tarea ajena. 2. Como responsable intentar modificar su tarea realizada. 3. Como coordinación reabrirla. 4. Abrir una tarea de otra delegación. |
| Resultado esperado | Todos consultan; solo el responsable modifica lo suyo no cerrado; la realizada solo la reabre coordinación; otra delegación responde 404. |
| Resultado obtenido | Coincide con lo esperado: 4 de 4 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.TuboTests.test_toda_la_delegacion_consulta_pero_solo_el_responsable_modifica; test_evaluacion3.TuboTests.test_una_tarea_realizada_queda_cerrada_para_su_responsable; test_unit_delegaciones.ModificarEnSuPaginaTests.test_cambiar_el_estado_exige_ser_responsable; test_unit_delegaciones.ModificarEnSuPaginaTests.test_modificar_una_tarea_de_otra_delegacion_responde_404 |
| Defecto asociado | DEF-04, DEF-05 |
| Corrección | La página conserva «Tubo de trabajo»; las pestañas distinguen «Tubo de trabajo (seguimiento)» y «Tubo de cartas». El nombre del menú se decidió después con el equipo: «Tubo» (ver cambios de requisito).; agenda.html: el parámetro tubo solo se agrega en el Tubo de cartas. |
| Reejecución | DEF-04: Aprobado; DEF-05: Aprobado |

### CP-22 · Filtros del Tubo y RUT válido

| Campo | Detalle |
|---|---|
| Código | CP-22 |
| Nombre | Filtros del Tubo y RUT válido |
| Requerimiento asociado | REQ-09: Fechas y códigos automáticos, autocompletado, búsqueda dinámica por código, RUT o nombre, filtros (RF-011, RF-032, RF-054, RF-062) |
| Prioridad | Media |
| Tipo de prueba | Validación / filtros (automatizada) |
| Precondiciones | Tareas de dos funcionarios. |
| Perfil de usuario | Profesional |
| Datos de prueba | Filtro por funcionario; RUT 12.345.678-9 (inválido). |
| Pasos | 1. Filtrar por funcionario. 2. Ingresar una tarea con RUT inválido. |
| Resultado esperado | El filtro deja solo las tareas del funcionario; el RUT inválido se rechaza y uno válido se guarda sin puntos. |
| Resultado obtenido | Coincide con lo esperado: 2 de 2 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.TuboTests.test_filtra_por_funcionario_responsable; test_evaluacion3.TuboTests.test_el_rut_del_solicitante_se_valida_y_se_normaliza |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-23 · Actividad y gestión social ingresan o no al Tubo

| Campo | Detalle |
|---|---|
| Código | CP-23 |
| Nombre | Actividad y gestión social ingresan o no al Tubo |
| Requerimiento asociado | REQ-04: Actividades, gestiones sociales y evidencias; ingreso opcional al Tubo (RF-009, RF-012, RF-015, RF-059) |
| Prioridad | Alta |
| Tipo de prueba | Funcional positiva (automatizada) |
| Precondiciones | Período abierto, ítem del cargo. |
| Perfil de usuario | Profesional |
| Datos de prueba | Actividad con «Ingresar al Tubo» y sin marcar; gestión social igual. |
| Pasos | 1. Registrar una actividad marcando «Ingresar al Tubo» con plazo. 2. Registrar otra sin marcar. 3. Repetir con gestiones sociales. |
| Resultado esperado | Marcadas: se crea una tarea vinculada con nombre, teléfono, plazo y responsable; sin marcar no se crea tarea. |
| Resultado obtenido | Coincide con lo esperado: 3 de 3 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.IngresoAlTuboTests.test_una_actividad_marcada_ingresa_al_tubo; test_evaluacion3.IngresoAlTuboTests.test_una_actividad_sin_marcar_no_ingresa_al_tubo; test_evaluacion3.IngresoAlTuboTests.test_una_gestion_social_puede_ingresar_al_tubo |
| Defecto asociado | DEF-03 |
| Corrección | actividad_form.html: subtipo en «Qué se hizo»; hito, ingreso y plazo del Tubo en «Vinculación». |
| Reejecución | DEF-03: Aprobado |

### CP-24 · Autocompletado desde el registro de vecinos

| Campo | Detalle |
|---|---|
| Código | CP-24 |
| Nombre | Autocompletado desde el registro de vecinos |
| Requerimiento asociado | REQ-09: Fechas y códigos automáticos, autocompletado, búsqueda dinámica por código, RUT o nombre, filtros (RF-011, RF-032, RF-054, RF-062) |
| Prioridad | Media |
| Tipo de prueba | Funcional positiva y negativa (automatizada) |
| Precondiciones | Vecino 11.111.111-1 registrado. |
| Perfil de usuario | Profesional |
| Datos de prueba | RUT registrado, RUT de otra delegación, RUT incompleto. |
| Pasos | 1. En una tarea escribir el RUT del vecino. 2. Elegir un vecino en la gestión social. 3. Usar un RUT de otra delegación. |
| Resultado esperado | Nombre y teléfono se completan solos; un vecino fuera del ámbito no se entrega; sin permiso responde 403. |
| Resultado obtenido | Coincide con lo esperado: 4 de 4 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.VecinosYAutocompletadoTests.test_la_busqueda_por_rut_entrega_los_datos_para_autocompletar; test_evaluacion3.VecinosYAutocompletadoTests.test_elegir_un_vecino_completa_la_tarea; test_evaluacion3.IngresoAlTuboTests.test_la_gestion_social_autocompleta_desde_el_vecino; test_evaluacion3.VecinosYAutocompletadoTests.test_la_busqueda_de_vecinos_exige_permiso |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-25 · Vecinos: RUT, unicidad y ámbito

| Campo | Detalle |
|---|---|
| Código | CP-25 |
| Nombre | Vecinos: RUT, unicidad y ámbito |
| Requerimiento asociado | REQ-03: CRUD con validaciones de delegaciones, territorios, usuarios, cargos, roles, vecinos, juntas de vecinos, hitos, tipos y subtipos, metas y trimestres (RF-001 a RF-007, RF-055 a RF-058) |
| Prioridad | Alta |
| Tipo de prueba | Validación / permisos (automatizada) |
| Precondiciones | Vecinos en Centro y Rural. |
| Perfil de usuario | Coordinador y Delegado |
| Datos de prueba | RUT repetido con otro formato; RUT con dígito erróneo. |
| Pasos | 1. Agregar un vecino con RUT repetido. 2. Agregar uno con dígito verificador erróneo. 3. Como delegado de Centro abrir un vecino de Rural. |
| Resultado esperado | Ambos se rechazan con su mensaje; el vecino de otra delegación responde 404 y queda auditado. |
| Resultado obtenido | Coincide con lo esperado: 4 de 4 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.VecinosYAutocompletadoTests.test_el_rut_se_valida_con_modulo_11; test_evaluacion3.VecinosYAutocompletadoTests.test_un_rut_repetido_o_invalido_no_se_guarda; test_evaluacion3.VecinosYAutocompletadoTests.test_el_delegado_ve_y_modifica_solo_los_vecinos_de_su_delegacion; test_evaluacion3.VecinosYAutocompletadoTests.test_la_delegacion_del_vecino_es_la_de_su_territorio |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-26 · Membresía y dirigencia en juntas de vecinos

| Campo | Detalle |
|---|---|
| Código | CP-26 |
| Nombre | Membresía y dirigencia en juntas de vecinos |
| Requerimiento asociado | REQ-03: CRUD con validaciones de delegaciones, territorios, usuarios, cargos, roles, vecinos, juntas de vecinos, hitos, tipos y subtipos, metas y trimestres (RF-001 a RF-007, RF-055 a RF-058) |
| Prioridad | Alta |
| Tipo de prueba | Validación (automatizada) |
| Precondiciones | Junta con presidenta vigente. |
| Perfil de usuario | Coordinador o Delegado |
| Datos de prueba | Segundo presidente; membresía traslapada; término antes del inicio. |
| Pasos | 1. Inscribir a otro vecino como presidente. 2. Inscribir dos veces al mismo vecino en fechas cruzadas. 3. Guardar un término anterior al inicio. |
| Resultado esperado | Se rechaza el segundo presidente, la membresía traslapada y las fechas inválidas (también por restricción CHECK de la base). |
| Resultado obtenido | Coincide con lo esperado: 4 de 4 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.MembresiasHitosYCatalogosTests.test_la_presidencia_es_unica_en_cada_periodo; test_evaluacion3.MembresiasHitosYCatalogosTests.test_un_vecino_no_tiene_dos_membresias_traslapadas; test_evaluacion3.MembresiasHitosYCatalogosTests.test_el_termino_no_puede_ser_anterior_al_inicio; test_evaluacion3.MembresiasHitosYCatalogosTests.test_la_organizacion_y_su_territorio_son_de_la_misma_delegacion |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-27 · Hitos con responsables

| Campo | Detalle |
|---|---|
| Código | CP-27 |
| Nombre | Hitos con responsables |
| Requerimiento asociado | REQ-03: CRUD con validaciones de delegaciones, territorios, usuarios, cargos, roles, vecinos, juntas de vecinos, hitos, tipos y subtipos, metas y trimestres (RF-001 a RF-007, RF-055 a RF-058) |
| Prioridad | Media |
| Tipo de prueba | Funcional positiva y negativa (automatizada) |
| Precondiciones | Delegación con funcionarios. |
| Perfil de usuario | Coordinador |
| Datos de prueba | Responsable principal y apoyo; responsable de otra delegación. |
| Pasos | 1. Crear un hito con principal y apoyo. 2. Crear otro con un responsable de otra delegación. 3. Marcar uno como realizado sin fecha. |
| Resultado esperado | El primero se guarda con sus roles; el segundo y el tercero se rechazan. |
| Resultado obtenido | Coincide con lo esperado: 3 de 3 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.MembresiasHitosYCatalogosTests.test_un_hito_se_crea_con_responsable_principal_y_apoyo; test_evaluacion3.MembresiasHitosYCatalogosTests.test_un_responsable_de_otra_delegacion_se_rechaza; test_evaluacion3.MembresiasHitosYCatalogosTests.test_un_hito_realizado_exige_su_fecha |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-28 · Territorios, tipos y subtipos de atención

| Campo | Detalle |
|---|---|
| Código | CP-28 |
| Nombre | Territorios, tipos y subtipos de atención |
| Requerimiento asociado | REQ-03: CRUD con validaciones de delegaciones, territorios, usuarios, cargos, roles, vecinos, juntas de vecinos, hitos, tipos y subtipos, metas y trimestres (RF-001 a RF-007, RF-055 a RF-058) |
| Prioridad | Media |
| Tipo de prueba | Validación / permisos (automatizada) |
| Precondiciones | Territorio «Casco histórico» en Centro. |
| Perfil de usuario | Coordinador y Delegado |
| Datos de prueba | Nombre repetido con espacios extra; subtipo de otro tipo. |
| Pasos | 1. Crear el mismo territorio en la misma delegación. 2. Como delegado intentar crear un territorio. 3. Elegir en una actividad un subtipo de otro tipo de atención. |
| Resultado esperado | El duplicado se rechaza; el delegado solo consulta; el subtipo ajeno se rechaza. |
| Resultado obtenido | Coincide con lo esperado: 4 de 4 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.MembresiasHitosYCatalogosTests.test_el_territorio_es_unico_en_su_delegacion; test_evaluacion3.MembresiasHitosYCatalogosTests.test_el_delegado_no_crea_territorios; test_evaluacion3.MembresiasHitosYCatalogosTests.test_el_subtipo_debe_ser_del_tipo_de_atencion_elegido; test_evaluacion3.MembresiasHitosYCatalogosTests.test_un_subtipo_solo_cuelga_de_un_tipo_de_atencion |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-29 · Permisos de los perfiles sobre las tablas nuevas

| Campo | Detalle |
|---|---|
| Código | CP-29 |
| Nombre | Permisos de los perfiles sobre las tablas nuevas |
| Requerimiento asociado | REQ-01: Autenticación, roles y permisos (RF-001, RF-002) |
| Prioridad | Alta |
| Tipo de prueba | Permisos (automatizada) |
| Precondiciones | Migraciones aplicadas. |
| Perfil de usuario | Todos |
| Datos de prueba | Perfiles Administrador, Coordinador, Delegado y Profesional. |
| Pasos | 1. Revisar Administración → Perfiles y permisos. |
| Resultado esperado | Coordinación administra las tablas nuevas; el delegado mantiene vecinos, membresías e hitos; el profesional consulta y registra vecinos sin eliminar. |
| Resultado obtenido | Coincide con lo esperado: 1 de 1 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.MembresiasHitosYCatalogosTests.test_los_perfiles_reciben_los_permisos_de_las_tablas_nuevas |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-30 · Dashboard con gráficos y tabla de datos

| Campo | Detalle |
|---|---|
| Código | CP-30 |
| Nombre | Dashboard con gráficos y tabla de datos |
| Requerimiento asociado | REQ-08: Dashboard y semáforo por funcionario y delegación, con filtros y gráficos (RF-027 a RF-029, RF-060) |
| Prioridad | Alta |
| Tipo de prueba | Funcional positiva (automatizada) |
| Precondiciones | Período con indicadores, tareas y actividades. |
| Perfil de usuario | Coordinador |
| Datos de prueba | Rango septiembre 2026. |
| Pasos | 1. Abrir Resultados → Dashboard con gráficos. 2. Revisar los cinco gráficos. 3. Abrir «Ver datos en tabla». |
| Resultado esperado | Se ven cumplimiento por delegación, semáforo por funcionario, estado de compromisos, carga de trabajo y tendencia, cada uno con su tabla. |
| Resultado obtenido | Coincide con lo esperado: 3 de 3 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.DashboardTests.test_el_dashboard_muestra_los_cinco_graficos; test_evaluacion3.DashboardTests.test_estado_de_compromisos_calcula_porcentajes_y_vencidas; test_evaluacion3.DashboardTests.test_la_tendencia_cuenta_registradas_y_aprobadas_por_semana |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-31 · Filtros y ámbito del dashboard

| Campo | Detalle |
|---|---|
| Código | CP-31 |
| Nombre | Filtros y ámbito del dashboard |
| Requerimiento asociado | REQ-08: Dashboard y semáforo por funcionario y delegación, con filtros y gráficos (RF-027 a RF-029, RF-060) |
| Prioridad | Alta |
| Tipo de prueba | Filtros / permisos (automatizada) |
| Precondiciones | Datos en Centro y Rural. |
| Perfil de usuario | Delegado y Coordinador |
| Datos de prueba | Filtro por funcionario y por delegación ajena. |
| Pasos | 1. Como coordinador filtrar por un funcionario. 2. Como delegado de Centro pedir la delegación Rural por URL. |
| Resultado esperado | El filtro deja solo la carga del funcionario; el delegado sigue viendo solo Centro. |
| Resultado obtenido | Coincide con lo esperado: 2 de 2 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.DashboardTests.test_el_filtro_por_funcionario_restringe_la_carga; test_evaluacion3.DashboardTests.test_el_delegado_ve_solo_su_delegacion |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-32 · Interfaz responsiva, legible y con identidad municipal

| Campo | Detalle |
|---|---|
| Código | CP-32 |
| Nombre | Interfaz responsiva, legible y con identidad municipal |
| Requerimiento asociado | REQ-08: Dashboard y semáforo por funcionario y delegación, con filtros y gráficos (RF-027 a RF-029, RF-060) |
| Prioridad | Media |
| Tipo de prueba | Usabilidad (manual) |
| Precondiciones | Aplicación desplegada. |
| Perfil de usuario | Todos |
| Datos de prueba | Anchos de 375 px, 768 px y 1280 px; tema claro y oscuro. |
| Pasos | 1. Abrir el Tubo, el Dashboard y un formulario en cada ancho. 2. Cambiar a tema oscuro y alto contraste. 3. Navegar solo con teclado. |
| Resultado esperado | No hay desplazamiento horizontal; el rojo institucional se usa en acentos; textos y gráficos se leen en ambos temas; el foco es visible. |
| Resultado obtenido | Pendiente: caso manual, lo ejecuta el equipo en el entorno desplegado. |
| Estado final | No ejecutado |
| Responsable | Por asignar |
| Fecha de ejecución | - |
| Evidencia | - |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-33 · Regresión: formulario del Tubo con calendario

| Campo | Detalle |
|---|---|
| Código | CP-33 |
| Nombre | Regresión: formulario del Tubo con calendario |
| Requerimiento asociado | REQ-09: Fechas y códigos automáticos, autocompletado, búsqueda dinámica por código, RUT o nombre, filtros (RF-011, RF-032, RF-054, RF-062) |
| Prioridad | Baja |
| Tipo de prueba | Regresión (automatizada) |
| Precondiciones | Ninguna. |
| Perfil de usuario | Profesional |
| Datos de prueba | Formulario de tarea. |
| Pasos | 1. Abrir «Agregar al tubo de trabajo». 2. Revisar el campo de plazo. |
| Resultado esperado | El plazo se elige con un selector de fecha (DEF-01 corregido). |
| Resultado obtenido | Coincide con lo esperado: 1 de 1 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.TuboTests.test_el_formulario_del_tubo_usa_selector_de_fecha |
| Defecto asociado | DEF-01 |
| Corrección | Se movieron labels y widgets a CompromisoForm (fecha con type="date") y ComentarioForm quedó con su propio Meta (forms.py). |
| Reejecución | DEF-01: Aprobado |

### CP-34 · Respaldo y recuperación

| Campo | Detalle |
|---|---|
| Código | CP-34 |
| Nombre | Respaldo y recuperación |
| Requerimiento asociado | REQ-12: Entorno reproducible: respaldo y recuperación de datos y archivos (RNF-012) |
| Prioridad | Alta |
| Tipo de prueba | Recuperación (automatizada) |
| Precondiciones | Base con datos y archivos de evidencia. |
| Perfil de usuario | Administrador del servidor |
| Datos de prueba | Un vecino y su territorio. |
| Pasos | 1. Ejecutar python manage.py respaldo. 2. Borrar el vecino. 3. Restaurar con loaddata desde datos.json del .zip. |
| Resultado esperado | El .zip contiene datos.json y media/; tras restaurar, el vecino vuelve con el mismo RUT. |
| Resultado obtenido | Coincide con lo esperado: 1 de 1 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_evaluacion3.RespaldoTests.test_el_respaldo_se_restaura_en_una_base_vacia |
| Defecto asociado | Ninguno |
| Corrección | - |
| Reejecución | - |

### CP-35 · Matriz de accesos por perfil

| Campo | Detalle |
|---|---|
| Código | CP-35 |
| Nombre | Matriz de accesos por perfil |
| Requerimiento asociado | REQ-01: Autenticación, roles y permisos (RF-001, RF-002) |
| Prioridad | Alta |
| Tipo de prueba | Permisos / seguridad (automatizada) |
| Precondiciones | Un registro de cada tipo en Centro (delegación propia) y otro en Rural. |
| Perfil de usuario | Administrador, Coordinador, Delegado, Profesional, sin sesión, sin perfil y funcionario desactivado |
| Datos de prueba | Las 78 rutas de la matriz; 21 acciones POST no permitidas. |
| Pasos | 1. Con cada perfil abrir cada ruta y comparar con la matriz. 2. Revisar que las páginas permitidas no muestren registros de Rural. 3. Enviar a mano los formularios de acciones no permitidas. 4. Repetir sin sesión, sin perfil y con la ficha desactivada. |
| Resultado esperado | Cada perfil entra solo a lo establecido; las páginas permitidas no muestran datos de otra delegación; ninguna acción no permitida cambia datos; sin sesión toda ruta interna pide iniciar sesión. |
| Resultado obtenido | Coincide con lo esperado: 7 de 7 pruebas automáticas aprobadas. |
| Estado final | Aprobado |
| Responsable | Por asignar |
| Fecha de ejecución | 24-11-2026 |
| Evidencia | test_matriz_accesos.MatrizDeAccesosTests.test_cada_perfil_entra_solo_a_lo_establecido; test_matriz_accesos.MatrizDeAccesosTests.test_sin_sesion_toda_ruta_interna_pide_iniciar_sesion; test_matriz_accesos.MatrizDeAccesosTests.test_un_usuario_sin_perfil_ni_funcionario_no_entra_a_nada_operativo; test_matriz_accesos.MatrizDeAccesosTests.test_un_funcionario_desactivado_pierde_el_acceso; test_matriz_accesos.MatrizDeAccesosTests.test_las_paginas_permitidas_no_muestran_datos_de_otra_delegacion; test_matriz_accesos.MatrizDeAccesosTests.test_un_usuario_sin_perfil_no_ve_datos_en_las_paginas_generales; test_matriz_accesos.MatrizDeAccesosTests.test_las_acciones_post_respetan_el_perfil |
| Defecto asociado | DEF-08 |
| Corrección | crud.py: @login_required en exportar_organizaciones. |
| Reejecución | DEF-08: Aprobado |

## 5. Registro de defectos

| Código | Caso | Fecha | Severidad | Detectado en | Descripción | Causa | Impacto | Corrección | Reejecución | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| DEF-01 | CP-33 | 24-11-2026 | Baja | Revisión de código antes de ejecutar el protocolo | El Meta de CompromisoForm (labels y widgets) estaba pegado por error dentro de ComentarioForm. | Bloque de código movido a la clase equivocada en una entrega anterior; el segundo «widgets» reemplazaba al primero. | El plazo de una tarea se escribía como texto libre (sin calendario) y el comentario perdía su etiqueta. | Se movieron labels y widgets a CompromisoForm (fecha con type="date") y ComentarioForm quedó con su propio Meta (forms.py). | Aprobado (1 prueba/s) | Corregido y verificado |
| DEF-02 | CP-20 | 24-11-2026 | Alta | Ejecución 2 de la suite de regresión (2 pruebas fallidas) | Al agregar el Tubo de cartas, el campo «tipo» quedó obligatorio y crear una tarea sin indicarlo fallaba. | El campo del modelo tiene valor por defecto, pero el ModelForm lo exigía al recibirlo vacío. | No se podían crear tareas desde integraciones o formularios que no enviaban el tipo. | CompromisoForm: «tipo» opcional con valor por defecto «solicitud» y sin cambio posible al editar (clean_tipo). | Aprobado (2 prueba/s) | Corregido y verificado |
| DEF-03 | CP-23 | 24-11-2026 | Media | Ejecución 2 de la suite de regresión | Los campos nuevos de la actividad (subtipo, hito, ingresar al Tubo, plazo) aparecían en una sección «Otros datos». | La plantilla agrupa los campos por nombre y los nuevos no estaban en ningún grupo. | Formulario desordenado: campos clave lejos de su contexto. | actividad_form.html: subtipo en «Qué se hizo»; hito, ingreso y plazo del Tubo en «Vinculación». | Aprobado (1 prueba/s) | Corregido y verificado |
| DEF-04 | CP-21 | 24-11-2026 | Baja | Ejecución 2 de la suite de regresión (2 pruebas fallidas) | La página del Tubo se renombró «Tubo de seguimiento», contra el término acordado por el equipo («Tubo de trabajo»), sin actualizar sus pruebas. | Se tomó el nombre de la guía sin revisar la decisión de interfaz previa ni las pruebas que la verifican. | Inconsistencia de nombres entre pantallas, pruebas y manual. | La página conserva «Tubo de trabajo»; las pestañas distinguen «Tubo de trabajo (seguimiento)» y «Tubo de cartas». El nombre del menú se decidió después con el equipo: «Tubo» (ver cambios de requisito). | Aprobado (2 prueba/s) | Corregido y verificado |
| DEF-05 | CP-21 | 24-11-2026 | Media | Ejecución 2 de la suite de regresión (2 pruebas fallidas) | El botón «+ Agregar al tubo de trabajo» dejó de conservar la delegación filtrada con el formato esperado. | Se antepuso el parámetro ?tubo= al enlace, también para el Tubo de trabajo. | La coordinación perdía la delegación preseleccionada al agregar una tarea. | agenda.html: el parámetro tubo solo se agrega en el Tubo de cartas. | Aprobado (2 prueba/s) | Corregido y verificado |
| DEF-06 | CP-20 | 24-11-2026 | Baja | Ejecución 3 de la suite (1 prueba con error) | Defecto del caso de prueba, no del sistema: los datos de CP-EVA-023 no incluían el estado inicial de la tarea. | El formulario de alta exige «estado»; los datos de la prueba lo omitían. | La prueba fallaba aunque la funcionalidad era correcta. | Se completaron los datos de la prueba con estado «ingresado». | Aprobado (1 prueba/s) | Corregido y verificado |
| DEF-07 | CP-10 | 24-11-2026 | Media | Revisión de las pantallas que muestran estados de actividad | Una actividad con antecedentes solicitados aparecía como «En preparación» en la lista, y su autor no recibía ningún aviso. | La plantilla de la lista y las alertas solo conocían los estados anteriores (pendiente, aprobada, rechazada). | El autor podía no enterarse de que debía completar antecedentes y la actividad quedaba sin revisar. | actividades.html muestra «Completar antecedentes solicitados» y alertas.py agrega la alerta con el detalle pedido por el verificador. | Aprobado (1 prueba/s) | Corregido y verificado |
| DEF-08 | CP-35 | 25-11-2026 | Baja | Auditoría de la matriz de accesos (sin sesión) | Sin sesión, la exportación de organizaciones respondía 404 en vez de pedir el inicio de sesión. | La vista exportar_organizaciones solo verificaba el permiso y no tenía @login_required (defecto anterior a la Evaluación 3). | No exponía datos, pero no era coherente con el resto de las rutas internas. | crud.py: @login_required en exportar_organizaciones. | Aprobado (1 prueba/s) | Corregido y verificado |

## 6. Pruebas actualizadas por cambio de requisito

No son defectos: la guía de la Evaluación 3 cambió el comportamiento esperado y estas pruebas existentes se ajustaron para verificar el nuevo.

| Prueba | Cambio de requisito |
|---|---|
| test_unit_actividades.ValidacionUnitTests.test_la_revision_solo_aprueba_o_rechaza | La revisión agrega «solicitar más antecedentes». |
| test_unit_organizacion.FuncionarioFormUnitTests.test_al_crear_la_contrasena_es_obligatoria | Sin contraseña escrita se genera una temporal. |
| test_unit_medicion.FichaPersonalUnitTests.test_resumen_de_evidencias_por_estado | Nuevo estado de evidencia «más antecedentes». |
| test_integracion.MantenedoresTests (2 pruebas), test_unit_seguridad.AccesoPorPerfilTests (2), test_unit_transversal.MantenedoresUnitTests, test_unit_interfaz.IndiceDeMantenedoresTests | De 12 a 17 mantenedores (territorios, vecinos, membresías, hitos y subtipos). |
| test_integracion.SeedDemoTests.test_carga_el_modelo_nuevo_con_sus_datos_de_demostracion | Los datos demo incluyen una carta y las tablas nuevas. |
| test_unit_plan_pruebas.ArmadoDelPlanTests.test_el_catalogo_tiene_los_casos_de_uso_y_los_38_requisitos | El catálogo de requisitos suma RF-051 a RF-062. |
| test_unit_compromisos.TuboDeTrabajoUnitTests.test_la_pagina_dice_tubo_de_trabajo_y_el_menu_tareas, test_unit_interfaz.EncabezadoPieYAccesibilidadTests.test_el_menu_marca_la_seccion_activa_sin_cambiar_sus_enlaces | Revisión del equipo (25-11-2026): el menú pasa de «Tareas» a «Tubo», porque ahora reúne el Tubo de trabajo y el Tubo de cartas (una carta no es una tarea). |

## 7. Historial de ejecuciones de la suite completa

| N.º | Fecha | Pruebas | Con falla | Observación |
|---|---|---|---|---|
| 1 | 24-11-2026 | 727 | 0 | Línea base antes de los cambios de la Evaluación 3 (todas aprobadas). |
| 2 | 24-11-2026 | 727 | 18 | 7 fallas por 4 defectos reales (DEF-02 a DEF-05) y 11 por requisitos que la guía cambió (pruebas actualizadas, ver sección 6). |
| 3 | 24-11-2026 | 784 | 1 | Defecto del caso de prueba DEF-06. |
| 4 | 24-11-2026 | 74 | 1 | Ejecución parcial (protocolo y plan): 1 falla por el catálogo de requisitos ampliado (cambio de requisito, sección 6). |
| 5 | 24-11-2026 | 794 | 0 | Ejecución que generó este protocolo (89 s). |

## 8. Incidencias de configuración resueltas

| Incidencia | Causa | Solución |
|---|---|---|
| La suite completa tardaba más de 10 minutos. | Cada prueba crea usuarios y PBKDF2 (1.000.000 de iteraciones) es lento a propósito. | Solo al ejecutar pruebas se usa un hasher rápido (settings.EJECUTANDO_PRUEBAS); producción sigue con PBKDF2. La suite bajó a menos de 1 minuto. |
| Los acentos de los mensajes de migración se ven mal en la consola de Windows. | La consola usa la página de códigos cp1252. | Ejecutar con la variable PYTHONIOENCODING=utf-8 o en Windows Terminal; no afecta los datos (la base usa utf8mb4). |
| Riesgo detectado al diseñar el bloqueo de ingreso: sus intentos fallidos podían bloquear el login en otras pruebas. | La caché en memoria dura todo el proceso de pruebas. | En pruebas el máximo de intentos es muy alto y las pruebas del bloqueo fijan el suyo con override_settings y limpian la caché. |
| La migración 0030 fallaría si ya existieran metas duplicadas. | Se agregó una restricción única (ítem, funcionario). | La migración verifica antes y, si hay duplicados, se detiene con la lista de filas a corregir en vez de dejar la base a medias. |
| Advertencia de WhiteNoise «No directory at: staticfiles» al ejecutar pruebas o runserver. | En desarrollo no se ejecuta collectstatic, así que la carpeta no existe. | Es inofensiva en desarrollo; en el servidor se ejecuta python manage.py collectstatic --noinput (paso 6 del despliegue) y desaparece. |
