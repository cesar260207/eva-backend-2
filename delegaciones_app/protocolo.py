"""Protocolo de pruebas de la Evaluación 3: casos, defectos, reejecuciones y matriz de trazabilidad.

Cada caso (CP-nn) tiene los campos que pide la guía: identificación (código, nombre, requerimiento, prioridad),
preparación (precondiciones, perfil, datos), ejecución (pasos numerados), resultado (esperado, obtenido, estado) y
seguimiento (responsable, fecha, evidencia, defecto, corrección, reejecución). El resultado obtenido NO se escribe a mano:
el comando `python manage.py protocolo_pruebas` ejecuta las pruebas automáticas que respaldan cada caso y lo completa.
Los casos manuales (revisión visual, correo real) los completa el equipo en RESULTADOS_MANUALES.

Para asignar responsables, editar RESPONSABLE_POR_AREA y volver a generar el protocolo.
"""

E3 = 'delegaciones_app.test_evaluacion3.'
REG = 'delegaciones_app.test_unit_reglas_nuevas.'
SEG = 'delegaciones_app.test_unit_seguridad.'
INT = 'delegaciones_app.test_integracion.'
DEL = 'delegaciones_app.test_unit_delegaciones.'
ACT = 'delegaciones_app.test_unit_actividades.'
AUT = 'delegaciones_app.test_unit_autenticacion.'
MAT = 'delegaciones_app.test_matriz_accesos.MatrizDeAccesosTests.'

POR_ASIGNAR = 'Por asignar'
# Área del caso -> integrante responsable de ejecutarlo y de su seguimiento (lo completa el equipo).
RESPONSABLE_POR_AREA = {
    'Autenticación y seguridad': POR_ASIGNAR,
    'Verificación de actividades': POR_ASIGNAR,
    'Reglas del cliente y metas': POR_ASIGNAR,
    'Tubo': POR_ASIGNAR,
    'Mantenedores y base de datos': POR_ASIGNAR,
    'Dashboard': POR_ASIGNAR,
    'Interfaz': POR_ASIGNAR,
}

# Requerimientos de la guía de la Evaluación 3 (alcance funcional mínimo), con su RF del SGR.
REQUERIMIENTOS = {
    'REQ-01': ('Autenticación, roles y permisos', 'RF-001, RF-002'),
    'REQ-02': ('Contraseña temporal, cambio obligatorio en el primer ingreso y recuperación', 'RF-051'),
    'REQ-03': ('CRUD con validaciones de delegaciones, territorios, usuarios, cargos, roles, vecinos, juntas de vecinos, hitos, tipos y subtipos, metas y trimestres', 'RF-001 a RF-007, RF-055 a RF-058'),
    'REQ-04': ('Actividades, gestiones sociales y evidencias; ingreso opcional al Tubo', 'RF-009, RF-012, RF-015, RF-059'),
    'REQ-05': ('Metas por funcionario y trimestre con cantidad, ponderación y tope de 120 %; solo registros aprobados que ponderan', 'RF-007, RF-023, RF-024, RF-045'),
    'REQ-06': ('Verificación: pendiente, aprobada, rechazada o más antecedentes; lo aprobado no se modifica', 'RF-013, RF-014, RF-052'),
    'REQ-07': ('Tubo de seguimiento y Tubo de cartas; toda la delegación consulta, cada uno modifica lo suyo no cerrado', 'RF-016 a RF-018, RF-053'),
    'REQ-08': ('Dashboard y semáforo por funcionario y delegación, con filtros y gráficos', 'RF-027 a RF-029, RF-060'),
    'REQ-09': ('Fechas y códigos automáticos, autocompletado, búsqueda dinámica por código, RUT o nombre, filtros', 'RF-011, RF-032, RF-054, RF-062'),
    'REQ-10': ('Reglas del cliente: delegado, nombre y teléfono, 7 diarias, cierre semanal, gestión previa, felicitaciones, ausencias', 'RF-040 a RF-047'),
    'REQ-11': ('Seguridad: hash, validación en servidor, autorización por rol y propiedad, sesiones, tokens, acceso a evidencias', 'RNF-004, RF-061'),
    'REQ-12': ('Entorno reproducible: respaldo y recuperación de datos y archivos', 'RNF-012'),
}

# Pantalla y regla de negocio de cada requerimiento, para la matriz de trazabilidad.
PANTALLAS = {
    'REQ-01': ('/login/, /gestion/panel/, /administracion/perfiles/', 'Perfil = permisos (grupo); rol = alcance (delegación)'),
    'REQ-02': ('Administración → Funcionarios y usuarios; /cuenta/cambiar-contrasena/; /recuperar/', 'Toda clave asignada por la administración es temporal y se cambia al ingresar'),
    'REQ-03': ('/administracion/<tabla>/ (17 mantenedores)', 'Unicidad, integridad referencial, ámbito por delegación, baja lógica si hay datos relacionados'),
    'REQ-04': ('/actividad/nueva/, /actividad/<código>/evidencia/, /casos-sociales/', 'Ingresar al Tubo crea una tarea vinculada; gestión social hasta 3 etapas por usuario'),
    'REQ-05': ('Administración → Catálogo de metas y Metas por funcionario; /gestion/mi-ficha/', 'RN-017: mín(avance/meta, 120 %) ± ajustes; solo aprobadas con validación y que puntúan'),
    'REQ-06': ('/actividad/<código>/ (Revisión)', 'RN-009: cada decisión queda en Validacion; aprobada = bloqueada'),
    'REQ-07': ('/agenda/ (Tubo de trabajo) y /agenda/?tubo=carta (Tubo de cartas)', 'Responsable o coordinación modifican; realizada solo la reabre coordinación'),
    'REQ-08': ('/gestion/tablero/, /gestion/semaforo/, /gestion/', 'RN-008: verde ≥ esperado; ámbar ≥ 60 % de lo esperado; rojo bajo eso'),
    'REQ-09': ('/agenda/ (búsqueda al escribir), formularios con RUT o vecino', 'Folio y código generados; RUT normalizado y validado con módulo 11'),
    'REQ-10': ('/actividad/nueva/, /ajustes/nuevo/, /ausencias/nuevo/', 'RN-014 a RN-018'),
    'REQ-11': ('Todas', 'PBKDF2, CSRF, sesión de 30 min, bloqueo por intentos, archivos servidos solo con permiso'),
    'REQ-12': ('python manage.py respaldo; scripts/respaldo.sh (MySQL)', 'El respaldo incluye datos y archivos y se restaura con migrate + loaddata'),
}


def _caso(codigo, nombre, req, prioridad, tipo, area, perfil, precondiciones, datos, pasos, esperado, pruebas=(), manual=False):
    return {
        'codigo': codigo, 'nombre': nombre, 'requerimiento': req, 'prioridad': prioridad, 'tipo': tipo, 'area': area, 'perfil': perfil,
        'precondiciones': precondiciones, 'datos': datos, 'pasos': list(pasos), 'esperado': esperado, 'pruebas': list(pruebas), 'manual': manual,
    }


CASOS = [
    # Autenticación y seguridad
    _caso('CP-01', 'Ingreso con credenciales válidas e inválidas', 'REQ-01', 'Alta', 'Funcional positiva y negativa', 'Autenticación y seguridad',
          'Cualquiera', 'Usuario activo registrado.', 'Usuario válido / contraseña correcta e incorrecta.',
          ['Abrir /login/.', 'Ingresar usuario y contraseña correctos.', 'Cerrar sesión e ingresar con contraseña incorrecta.'],
          'Con credenciales correctas llega al panel de su perfil; con incorrectas ve un mensaje genérico y no ingresa.',
          [AUT + 'ValidarCredencialesTests.test_login_con_usuario_y_contrasena_validos', AUT + 'ValidarCredencialesTests.test_login_con_contrasena_incorrecta',
           SEG + 'AccesoPorPerfilTests.test_el_login_lleva_al_panel_de_cada_perfil']),
    _caso('CP-02', 'Crear usuario con contraseña temporal', 'REQ-02', 'Alta', 'Funcional positiva', 'Autenticación y seguridad',
          'Administrador', 'Sesión de administrador.', 'Usuario «nuevo.e3», cargo y rol funcionario; contraseña vacía o escrita.',
          ['Ir a Administración → Funcionarios y usuarios → Agregar.', 'Completar los datos dejando la contraseña vacía.', 'Guardar y leer el aviso.', 'Repetir escribiendo una contraseña.'],
          'Se crea la cuenta; el sistema muestra una sola vez la contraseña temporal generada; en ambos casos la cuenta queda marcada para cambiarla; la clave no queda en la auditoría.',
          [E3 + 'ContrasenaTemporalTests.test_crear_sin_contrasena_genera_una_temporal_y_la_muestra_una_vez', E3 + 'ContrasenaTemporalTests.test_una_contrasena_escrita_al_crear_tambien_es_temporal',
           E3 + 'ContrasenaTemporalTests.test_la_contrasena_temporal_es_aleatoria_y_robusta', E3 + 'ContrasenaTemporalTests.test_restablecer_desde_la_edicion_genera_otra_temporal']),
    _caso('CP-03', 'Cambio obligatorio en el primer ingreso', 'REQ-02', 'Alta', 'Seguridad', 'Autenticación y seguridad',
          'Profesional con contraseña temporal', 'Cuenta creada con contraseña temporal.', 'Clave temporal; nueva clave «Personal-Segura-2026» y una débil «123».',
          ['Ingresar con la clave temporal.', 'Intentar abrir Actividades, Tareas y el Dashboard.', 'Intentar una clave débil.', 'Cambiarla por una válida.', 'Abrir Actividades.'],
          'Toda página redirige a «Cambia tu contraseña temporal»; la clave débil se rechaza; tras el cambio el sistema se usa normalmente y el cambio queda auditado; se puede salir sin cambiarla.',
          [E3 + 'ContrasenaTemporalTests.test_el_primer_ingreso_obliga_a_cambiar_la_contrasena', E3 + 'ContrasenaTemporalTests.test_cambiar_la_contrasena_libera_la_cuenta_y_queda_auditado',
           E3 + 'ContrasenaTemporalTests.test_la_nueva_contrasena_debe_cumplir_las_reglas', E3 + 'ContrasenaTemporalTests.test_con_contrasena_temporal_se_puede_cerrar_la_sesion']),
    _caso('CP-04', 'Recuperación de contraseña con token que vence', 'REQ-02', 'Alta', 'Seguridad', 'Autenticación y seguridad',
          'Sin sesión', 'Cuenta activa con correo.', 'Correo registrado y uno desconocido.',
          ['En /login/ elegir «¿Olvidaste tu contraseña?».', 'Ingresar el correo.', 'Abrir el enlace y fijar la nueva clave.', 'Reusar el enlace.', 'Probar un enlace vencido y un correo desconocido.'],
          'Llega un correo con enlace de un solo uso que vence; la respuesta no revela si el correo existe; recuperar quita la marca de clave temporal.',
          [SEG + 'RecuperarContrasenaTests.test_flujo_completo_de_recuperacion', SEG + 'RecuperarContrasenaTests.test_el_enlace_no_sirve_dos_veces',
           SEG + 'RecuperarContrasenaTests.test_el_enlace_vence', SEG + 'RecuperarContrasenaTests.test_un_correo_desconocido_no_envia_nada_ni_lo_revela',
           E3 + 'ContrasenaTemporalTests.test_recuperar_por_correo_quita_la_marca_temporal']),
    _caso('CP-05', 'Envío real del correo de recuperación (SMTP)', 'REQ-02', 'Media', 'Configuración', 'Autenticación y seguridad',
          'Sin sesión', 'Variables EMAIL_* configuradas en el .env del servidor.', 'Correo real de una cuenta demo.',
          ['Ejecutar python manage.py sendtestemail <correo>.', 'Solicitar la recuperación desde /recuperar/.', 'Revisar la bandeja de entrada.'],
          'El correo llega con el enlace y la vigencia; el enlace funciona.', manual=True),
    _caso('CP-06', 'Bloqueo de ingreso por intentos fallidos', 'REQ-11', 'Alta', 'Seguridad', 'Autenticación y seguridad',
          'Sin sesión', 'LOGIN_MAX_INTENTOS = 3 en la prueba (5 por defecto).', 'Usuario existente con clave incorrecta y luego correcta.',
          ['Ingresar tres veces con clave incorrecta.', 'Ingresar con la clave correcta.', 'Ingresar con otra cuenta.'],
          'El cuarto intento se rechaza aunque la clave sea correcta y queda en la auditoría; otra cuenta no se ve afectada; un ingreso correcto reinicia el contador.',
          [E3 + 'BloqueoDeIngresoTests.test_tras_los_intentos_fallidos_se_bloquea_aunque_la_clave_sea_correcta', E3 + 'BloqueoDeIngresoTests.test_el_bloqueo_no_afecta_a_otra_cuenta',
           E3 + 'BloqueoDeIngresoTests.test_un_ingreso_correcto_reinicia_el_contador', E3 + 'CacheCompartidaTests.test_en_el_servidor_la_cache_es_compartida_por_los_procesos']),
    _caso('CP-07', 'Contraseñas con hash, sesión que vence y vistas protegidas', 'REQ-11', 'Alta', 'Seguridad', 'Autenticación y seguridad',
          'Cualquiera', 'Usuarios creados.', 'Usuario de prueba.',
          ['Revisar el campo password del usuario en la base.', 'Dejar la sesión inactiva 30 minutos.', 'Abrir vistas internas sin sesión.', 'Buscar /admin/.'],
          'La clave se guarda como hash con algoritmo y sal; la sesión vence a los 30 min; sin sesión se pide ingresar; Django Admin no está publicado.',
          [E3 + 'ContrasenaTemporalTests.test_la_contrasena_se_guarda_como_hash', SEG + 'CierreDeSesionTests.test_la_sesion_vence_a_los_30_minutos_sin_actividad',
           INT + 'AccesoAutenticadoTests.test_vistas_internas_exigen_inicio_de_sesion', SEG + 'AccesoPorPerfilTests.test_django_admin_no_esta_publicado']),
    _caso('CP-08', 'Autorización por perfil y control de acceso a evidencias', 'REQ-11', 'Alta', 'Permisos', 'Autenticación y seguridad',
          'Profesional y usuario sin sesión', 'Evidencia cargada.', 'Archivo PDF de evidencia; archivo de 6 MB.',
          ['Como Profesional abrir mantenedores críticos, perfiles y auditoría.', 'Abrir el archivo de una evidencia propia.', 'Abrirlo sin sesión.', 'Subir un archivo de más de 5 MB.'],
          'El Profesional no entra a operaciones críticas; el archivo se sirve solo a quien ve la actividad; sin sesión se pide ingresar; el archivo pesado se rechaza.',
          [SEG + 'AccesoPorPerfilTests.test_el_funcionario_no_entra_a_operaciones_criticas', INT + 'EvidenciaArchivoTests.test_el_autor_abre_el_archivo_en_el_navegador',
           INT + 'EvidenciaArchivoTests.test_sin_sesion_se_pide_iniciar_sesion', INT + 'EvidenciaTamanoTests.test_subir_evidencia_rechaza_un_archivo_demasiado_pesado']),

    # Verificación
    _caso('CP-09', 'Solicitar más antecedentes', 'REQ-06', 'Alta', 'Funcional positiva y negativa', 'Verificación de actividades',
          'Delegado (revisor) y Profesional (autor)', 'Actividad pendiente con evidencia, meta de 2 actividades.', 'Detalle vacío y «Falta la foto del lugar intervenido».',
          ['Como delegado abrir la actividad.', 'Pulsar «Solicitar más antecedentes» sin detalle.', 'Repetir con detalle.', 'Revisar el avance de la meta.'],
          'Sin detalle no se registra; con detalle la actividad y la evidencia quedan «más antecedentes», la decisión queda auditada y la actividad no suma.',
          [E3 + 'MasAntecedentesTests.test_solicitar_antecedentes_exige_indicar_que_falta', E3 + 'MasAntecedentesTests.test_la_solicitud_deja_la_actividad_en_espera_y_sin_puntaje',
           E3 + 'MasAntecedentesTests.test_el_boton_de_antecedentes_aparece_para_el_revisor']),
    _caso('CP-10', 'Completar antecedentes y aprobar', 'REQ-06', 'Alta', 'Funcional positiva', 'Verificación de actividades',
          'Profesional (autor) y Delegado', 'Actividad con antecedentes solicitados.', 'Nueva foto PNG; lugar «Plaza de Armas».',
          ['Como autor subir una evidencia nueva (o modificar la actividad).', 'Como delegado aprobar.', 'Revisar el avance.'],
          'La actividad vuelve a «pendiente»; al aprobarla suma 1 al avance de la meta.',
          [E3 + 'MasAntecedentesTests.test_completar_los_antecedentes_vuelve_a_revision_y_al_aprobar_suma', E3 + 'MasAntecedentesTests.test_corregir_la_actividad_la_devuelve_a_revision',
           E3 + 'MasAntecedentesTests.test_el_autor_ve_la_alerta_y_el_estado_en_su_lista']),
    _caso('CP-11', 'Bloqueo posterior a la aprobación', 'REQ-06', 'Alta', 'Funcional negativa', 'Verificación de actividades',
          'Profesional (autor) y Coordinador', 'Actividad aprobada.', 'Actividad aprobada.',
          ['Intentar modificarla.', 'Intentar eliminarla.', 'Intentar subirle evidencia.', 'Intentar cambiar su estado.'],
          'Ninguna operación se permite: la actividad aprobada ya suma al avance y no se modifica.',
          [INT + 'ActividadVistasTests.test_actividad_aprobada_no_se_edita_ni_se_elimina', INT + 'ActividadVistasTests.test_actividad_aprobada_no_admite_nuevas_evidencias',
           ACT + 'ActividadEstadoUnitTests.test_una_actividad_aprobada_no_cambia_de_estado']),

    # Reglas del cliente y metas
    _caso('CP-12', 'Tope de cumplimiento de 120 %', 'REQ-05', 'Alta', 'Cálculo / límite', 'Reglas del cliente y metas',
          'Sistema', 'Meta de 2 actividades, más actividades aprobadas que la meta; felicitaciones aplicadas.', 'Avance 3 de 2 (150 %).',
          ['Aprobar las actividades.', 'Calcular el indicador.', 'Aplicar felicitaciones.'],
          'El cumplimiento queda en 120 %, también con felicitaciones; el ponderado usa el ponderador de la meta.',
          [REG + 'CumplimientoConAjustesTests.test_el_tope_por_defecto_es_120', REG + 'CumplimientoConAjustesTests.test_la_felicitacion_no_supera_el_tope',
           INT + 'MedicionTests.test_rn005_tope_por_defecto_120_y_ponderado']),
    _caso('CP-13', 'Solo cuentan registros aprobados que ponderan', 'REQ-05', 'Alta', 'Cálculo', 'Reglas del cliente y metas',
          'Sistema', 'Actividades aprobadas con y sin contacto, gestión previa e interna.', 'Ver casos.',
          ['Aprobar una actividad sin nombre o teléfono.', 'Aprobar una gestión previa.', 'Aprobar una actividad del delegado (interna).'],
          'Se conservan en el historial pero no suman al avance de la meta.',
          [REG + 'PuntajeDeActividadTests.test_una_actividad_aprobada_sin_contacto_no_suma_al_avance', REG + 'PuntajeDeActividadTests.test_sin_nombre_o_telefono_del_usuario_no_puntua',
           REG + 'PuntajeDeActividadTests.test_la_gestion_previa_conserva_el_historial_sin_puntaje', REG + 'PuntajeDeActividadTests.test_la_actividad_de_una_tarea_interna_es_otra_gestion',
           REG + 'PuntajeDeActividadTests.test_una_actividad_suelta_marcada_como_interna_es_otra_gestion']),
    _caso('CP-14', 'Límite diario de siete actividades', 'REQ-10', 'Alta', 'Límite', 'Reglas del cliente y metas',
          'Profesional', '7 actividades registradas por el mismo autor ese día.', 'Octava actividad del día.',
          ['Registrar la octava actividad del día.', 'Registrar una actividad de otro autor el mismo día.'],
          'La octava se rechaza; el límite es por autor y por día.',
          [REG + 'PuntajeDeActividadTests.test_el_octavo_ingreso_del_dia_se_rechaza', REG + 'PuntajeDeActividadTests.test_el_limite_diario_es_por_autor_y_por_dia']),
    _caso('CP-15', 'Cierre semanal', 'REQ-10', 'Alta', 'Límite', 'Reglas del cliente y metas',
          'Profesional', 'Hoy martes o posterior.', 'Actividad con fecha de la semana anterior.',
          ['El lunes registrar una actividad de la semana anterior.', 'El martes intentar lo mismo.', 'Corregir una actividad rechazada antigua sin cambiar su día.'],
          'El lunes se acepta; desde el martes se rechaza el ingreso tardío; la corrección de una ya registrada se permite.',
          [REG + 'ReglasNuevasTests.test_el_lunes_permite_la_semana_anterior', REG + 'ReglasNuevasTests.test_desde_martes_la_semana_anterior_se_cierra',
           ACT + 'ActividadFormUnitTests.test_no_se_ingresa_una_actividad_de_una_semana_cerrada', ACT + 'ActividadFormUnitTests.test_corregir_una_actividad_rechazada_antigua_la_devuelve_a_pendiente']),
    _caso('CP-16', 'Felicitaciones con respaldo formal', 'REQ-10', 'Alta', 'Cálculo', 'Reglas del cliente y metas',
          'Delegado (informa) y Coordinador (decide)', 'Felicitaciones informadas con respaldo.', 'Cuatro felicitaciones aplicadas.',
          ['Informar felicitaciones con respaldo.', 'Aplicar algunas y dejar otras informadas.', 'Revisar el cumplimiento.'],
          'Solo cuentan las aplicadas; cada una suma 10 con máximo 3.',
          [REG + 'CumplimientoConAjustesTests.test_solo_cuentan_los_ajustes_aplicados', REG + 'CumplimientoConAjustesTests.test_cada_felicitacion_aplicada_suma_10',
           REG + 'CumplimientoConAjustesTests.test_se_aplican_como_maximo_tres_felicitaciones']),
    _caso('CP-17', 'Ausencias ajustan el semáforo', 'REQ-10', 'Alta', 'Cálculo', 'Reglas del cliente y metas',
          'Delegado', 'Funcionario con meta en el período.', 'Ausencia de varios días.',
          ['Registrar la ausencia desde el semáforo.', 'Revisar lo esperado al día.', 'Borrar la ausencia.'],
          'Los días de ausencia se descuentan de lo esperado y el indicador se recalcula; al borrarla vuelve a su valor.',
          [REG + 'EsperadoConAusenciasTests.test_las_ausencias_se_descuentan_de_los_dias_computables', REG + 'RecalculoDelSemaforoTests.test_registrar_y_borrar_una_ausencia_recalcula']),
    _caso('CP-18', 'Meta única por funcionario e ítem del trimestre', 'REQ-05', 'Media', 'Validación', 'Reglas del cliente y metas',
          'Coordinador', 'Meta ya asignada.', 'Mismo ítem y funcionario.',
          ['Asignar otra vez el mismo ítem al mismo funcionario.'],
          'El formulario lo rechaza y la base de datos lo impide con una restricción única.',
          [E3 + 'MembresiasHitosYCatalogosTests.test_la_meta_de_un_funcionario_no_se_duplica']),

    # Tubo
    _caso('CP-19', 'Búsqueda dinámica por código, RUT o nombre', 'REQ-09', 'Alta', 'Funcional positiva y negativa', 'Tubo',
          'Profesional de la delegación', 'Tarea AGR-E3-0001 de «María Pérez», RUT 12.345.678-5.', 'AGR-E3, 12.345.678-5, 123456785, 12345678, maría, 99999999.',
          ['Abrir Tubo.', 'Escribir cada texto en «Buscar mientras escribes».', 'Observar que los resultados cambian sin recargar.'],
          'Cada búsqueda válida encuentra la tarea; el texto sin coincidencias no; la búsqueda al escribir devuelve solo el bloque de resultados.',
          [E3 + 'TuboTests.test_busca_por_codigo_rut_o_nombre', E3 + 'TuboTests.test_la_busqueda_al_escribir_devuelve_solo_los_resultados']),
    _caso('CP-20', 'Tubo de cartas', 'REQ-07', 'Alta', 'Funcional positiva', 'Tubo',
          'Profesional', 'Delegación con una tarea y una carta.', 'Carta «Solicita uso de multicancha».',
          ['Abrir la pestaña Tubo de cartas.', 'Registrar una carta.', 'Volver al Tubo de trabajo.'],
          'La carta recibe un folio CAR- generado, queda con historial y se ve solo en el Tubo de cartas.',
          [E3 + 'TuboTests.test_el_tubo_de_cartas_separa_las_cartas', E3 + 'TuboTests.test_registrar_una_carta_genera_su_folio',
           E3 + 'TuboTests.test_las_cartas_no_cambian_el_item_del_tubo_y_el_informe_las_distingue']),
    _caso('CP-21', 'Permisos del Tubo', 'REQ-07', 'Alta', 'Permisos', 'Tubo',
          'Profesional compañero, responsable y Coordinador', 'Tarea de otro funcionario de la delegación; tarea realizada.', 'Ver casos.',
          ['Como compañero consultar el Tubo e intentar modificar la tarea ajena.', 'Como responsable intentar modificar su tarea realizada.', 'Como coordinación reabrirla.', 'Abrir una tarea de otra delegación.'],
          'Todos consultan; solo el responsable modifica lo suyo no cerrado; la realizada solo la reabre coordinación; otra delegación responde 404.',
          [E3 + 'TuboTests.test_toda_la_delegacion_consulta_pero_solo_el_responsable_modifica', E3 + 'TuboTests.test_una_tarea_realizada_queda_cerrada_para_su_responsable',
           DEL + 'ModificarEnSuPaginaTests.test_cambiar_el_estado_exige_ser_responsable', DEL + 'ModificarEnSuPaginaTests.test_modificar_una_tarea_de_otra_delegacion_responde_404']),
    _caso('CP-22', 'Filtros del Tubo y RUT válido', 'REQ-09', 'Media', 'Validación / filtros', 'Tubo',
          'Profesional', 'Tareas de dos funcionarios.', 'Filtro por funcionario; RUT 12.345.678-9 (inválido).',
          ['Filtrar por funcionario.', 'Ingresar una tarea con RUT inválido.'],
          'El filtro deja solo las tareas del funcionario; el RUT inválido se rechaza y uno válido se guarda sin puntos.',
          [E3 + 'TuboTests.test_filtra_por_funcionario_responsable', E3 + 'TuboTests.test_el_rut_del_solicitante_se_valida_y_se_normaliza']),
    _caso('CP-23', 'Actividad y gestión social ingresan o no al Tubo', 'REQ-04', 'Alta', 'Funcional positiva', 'Tubo',
          'Profesional', 'Período abierto, ítem del cargo.', 'Actividad con «Ingresar al Tubo» y sin marcar; gestión social igual.',
          ['Registrar una actividad marcando «Ingresar al Tubo» con plazo.', 'Registrar otra sin marcar.', 'Repetir con gestiones sociales.'],
          'Marcadas: se crea una tarea vinculada con nombre, teléfono, plazo y responsable; sin marcar no se crea tarea.',
          [E3 + 'IngresoAlTuboTests.test_una_actividad_marcada_ingresa_al_tubo', E3 + 'IngresoAlTuboTests.test_una_actividad_sin_marcar_no_ingresa_al_tubo',
           E3 + 'IngresoAlTuboTests.test_una_gestion_social_puede_ingresar_al_tubo']),
    _caso('CP-24', 'Autocompletado desde el registro de vecinos', 'REQ-09', 'Media', 'Funcional positiva y negativa', 'Tubo',
          'Profesional', 'Vecino 11.111.111-1 registrado.', 'RUT registrado, RUT de otra delegación, RUT incompleto.',
          ['En una tarea escribir el RUT del vecino.', 'Elegir un vecino en la gestión social.', 'Usar un RUT de otra delegación.'],
          'Nombre y teléfono se completan solos; un vecino fuera del ámbito no se entrega; sin permiso responde 403.',
          [E3 + 'VecinosYAutocompletadoTests.test_la_busqueda_por_rut_entrega_los_datos_para_autocompletar', E3 + 'VecinosYAutocompletadoTests.test_elegir_un_vecino_completa_la_tarea',
           E3 + 'IngresoAlTuboTests.test_la_gestion_social_autocompleta_desde_el_vecino', E3 + 'VecinosYAutocompletadoTests.test_la_busqueda_de_vecinos_exige_permiso']),

    # Mantenedores y base de datos
    _caso('CP-25', 'Vecinos: RUT, unicidad y ámbito', 'REQ-03', 'Alta', 'Validación / permisos', 'Mantenedores y base de datos',
          'Coordinador y Delegado', 'Vecinos en Centro y Rural.', 'RUT repetido con otro formato; RUT con dígito erróneo.',
          ['Agregar un vecino con RUT repetido.', 'Agregar uno con dígito verificador erróneo.', 'Como delegado de Centro abrir un vecino de Rural.'],
          'Ambos se rechazan con su mensaje; el vecino de otra delegación responde 404 y queda auditado.',
          [E3 + 'VecinosYAutocompletadoTests.test_el_rut_se_valida_con_modulo_11', E3 + 'VecinosYAutocompletadoTests.test_un_rut_repetido_o_invalido_no_se_guarda',
           E3 + 'VecinosYAutocompletadoTests.test_el_delegado_ve_y_modifica_solo_los_vecinos_de_su_delegacion', E3 + 'VecinosYAutocompletadoTests.test_la_delegacion_del_vecino_es_la_de_su_territorio']),
    _caso('CP-26', 'Membresía y dirigencia en juntas de vecinos', 'REQ-03', 'Alta', 'Validación', 'Mantenedores y base de datos',
          'Coordinador o Delegado', 'Junta con presidenta vigente.', 'Segundo presidente; membresía traslapada; término antes del inicio.',
          ['Inscribir a otro vecino como presidente.', 'Inscribir dos veces al mismo vecino en fechas cruzadas.', 'Guardar un término anterior al inicio.'],
          'Se rechaza el segundo presidente, la membresía traslapada y las fechas inválidas (también por restricción CHECK de la base).',
          [E3 + 'MembresiasHitosYCatalogosTests.test_la_presidencia_es_unica_en_cada_periodo', E3 + 'MembresiasHitosYCatalogosTests.test_un_vecino_no_tiene_dos_membresias_traslapadas',
           E3 + 'MembresiasHitosYCatalogosTests.test_el_termino_no_puede_ser_anterior_al_inicio', E3 + 'MembresiasHitosYCatalogosTests.test_la_organizacion_y_su_territorio_son_de_la_misma_delegacion']),
    _caso('CP-27', 'Hitos con responsables', 'REQ-03', 'Media', 'Funcional positiva y negativa', 'Mantenedores y base de datos',
          'Coordinador', 'Delegación con funcionarios.', 'Responsable principal y apoyo; responsable de otra delegación.',
          ['Crear un hito con principal y apoyo.', 'Crear otro con un responsable de otra delegación.', 'Marcar uno como realizado sin fecha.'],
          'El primero se guarda con sus roles; el segundo y el tercero se rechazan.',
          [E3 + 'MembresiasHitosYCatalogosTests.test_un_hito_se_crea_con_responsable_principal_y_apoyo', E3 + 'MembresiasHitosYCatalogosTests.test_un_responsable_de_otra_delegacion_se_rechaza',
           E3 + 'MembresiasHitosYCatalogosTests.test_un_hito_realizado_exige_su_fecha']),
    _caso('CP-28', 'Territorios, tipos y subtipos de atención', 'REQ-03', 'Media', 'Validación / permisos', 'Mantenedores y base de datos',
          'Coordinador y Delegado', 'Territorio «Casco histórico» en Centro.', 'Nombre repetido con espacios extra; subtipo de otro tipo.',
          ['Crear el mismo territorio en la misma delegación.', 'Como delegado intentar crear un territorio.', 'Elegir en una actividad un subtipo de otro tipo de atención.'],
          'El duplicado se rechaza; el delegado solo consulta; el subtipo ajeno se rechaza.',
          [E3 + 'MembresiasHitosYCatalogosTests.test_el_territorio_es_unico_en_su_delegacion', E3 + 'MembresiasHitosYCatalogosTests.test_el_delegado_no_crea_territorios',
           E3 + 'MembresiasHitosYCatalogosTests.test_el_subtipo_debe_ser_del_tipo_de_atencion_elegido', E3 + 'MembresiasHitosYCatalogosTests.test_un_subtipo_solo_cuelga_de_un_tipo_de_atencion']),
    _caso('CP-29', 'Permisos de los perfiles sobre las tablas nuevas', 'REQ-01', 'Alta', 'Permisos', 'Mantenedores y base de datos',
          'Todos', 'Migraciones aplicadas.', 'Perfiles Administrador, Coordinador, Delegado y Profesional.',
          ['Revisar Administración → Perfiles y permisos.'],
          'Coordinación administra las tablas nuevas; el delegado mantiene vecinos, membresías e hitos; el profesional consulta y registra vecinos sin eliminar.',
          [E3 + 'MembresiasHitosYCatalogosTests.test_los_perfiles_reciben_los_permisos_de_las_tablas_nuevas']),

    # Dashboard
    _caso('CP-30', 'Dashboard con gráficos y tabla de datos', 'REQ-08', 'Alta', 'Funcional positiva', 'Dashboard',
          'Coordinador', 'Período con indicadores, tareas y actividades.', 'Rango septiembre 2026.',
          ['Abrir Resultados → Dashboard con gráficos.', 'Revisar los cinco gráficos.', 'Abrir «Ver datos en tabla».'],
          'Se ven cumplimiento por delegación, semáforo por funcionario, estado de compromisos, carga de trabajo y tendencia, cada uno con su tabla.',
          [E3 + 'DashboardTests.test_el_dashboard_muestra_los_cinco_graficos', E3 + 'DashboardTests.test_estado_de_compromisos_calcula_porcentajes_y_vencidas',
           E3 + 'DashboardTests.test_la_tendencia_cuenta_registradas_y_aprobadas_por_semana']),
    _caso('CP-31', 'Filtros y ámbito del dashboard', 'REQ-08', 'Alta', 'Filtros / permisos', 'Dashboard',
          'Delegado y Coordinador', 'Datos en Centro y Rural.', 'Filtro por funcionario y por delegación ajena.',
          ['Como coordinador filtrar por un funcionario.', 'Como delegado de Centro pedir la delegación Rural por URL.'],
          'El filtro deja solo la carga del funcionario; el delegado sigue viendo solo Centro.',
          [E3 + 'DashboardTests.test_el_filtro_por_funcionario_restringe_la_carga', E3 + 'DashboardTests.test_el_delegado_ve_solo_su_delegacion']),

    # Interfaz
    _caso('CP-32', 'Interfaz responsiva, legible y con identidad municipal', 'REQ-08', 'Media', 'Usabilidad', 'Interfaz',
          'Todos', 'Aplicación desplegada.', 'Anchos de 375 px, 768 px y 1280 px; tema claro y oscuro.',
          ['Abrir el Tubo, el Dashboard y un formulario en cada ancho.', 'Cambiar a tema oscuro y alto contraste.', 'Navegar solo con teclado.'],
          'No hay desplazamiento horizontal; el rojo institucional se usa en acentos; textos y gráficos se leen en ambos temas; el foco es visible.', manual=True),
    _caso('CP-33', 'Regresión: formulario del Tubo con calendario', 'REQ-09', 'Baja', 'Regresión', 'Interfaz',
          'Profesional', 'Ninguna.', 'Formulario de tarea.',
          ['Abrir «Agregar al tubo de trabajo».', 'Revisar el campo de plazo.'],
          'El plazo se elige con un selector de fecha (DEF-01 corregido).',
          [E3 + 'TuboTests.test_el_formulario_del_tubo_usa_selector_de_fecha']),
    _caso('CP-34', 'Respaldo y recuperación', 'REQ-12', 'Alta', 'Recuperación', 'Mantenedores y base de datos',
          'Administrador del servidor', 'Base con datos y archivos de evidencia.', 'Un vecino y su territorio.',
          ['Ejecutar python manage.py respaldo.', 'Borrar el vecino.', 'Restaurar con loaddata desde datos.json del .zip.'],
          'El .zip contiene datos.json y media/; tras restaurar, el vecino vuelve con el mismo RUT.',
          [E3 + 'RespaldoTests.test_el_respaldo_se_restaura_en_una_base_vacia']),
    _caso('CP-35', 'Matriz de accesos por perfil', 'REQ-01', 'Alta', 'Permisos / seguridad', 'Autenticación y seguridad',
          'Administrador, Coordinador, Delegado, Profesional, sin sesión, sin perfil y funcionario desactivado',
          'Un registro de cada tipo en Centro (delegación propia) y otro en Rural.', 'Las 78 rutas de la matriz; 21 acciones POST no permitidas.',
          ['Con cada perfil abrir cada ruta y comparar con la matriz.', 'Revisar que las páginas permitidas no muestren registros de Rural.',
           'Enviar a mano los formularios de acciones no permitidas.', 'Repetir sin sesión, sin perfil y con la ficha desactivada.'],
          'Cada perfil entra solo a lo establecido; las páginas permitidas no muestran datos de otra delegación; ninguna acción no permitida '
          'cambia datos; sin sesión toda ruta interna pide iniciar sesión.',
          [MAT + 'test_cada_perfil_entra_solo_a_lo_establecido', MAT + 'test_sin_sesion_toda_ruta_interna_pide_iniciar_sesion',
           MAT + 'test_un_usuario_sin_perfil_ni_funcionario_no_entra_a_nada_operativo', MAT + 'test_un_funcionario_desactivado_pierde_el_acceso',
           MAT + 'test_las_paginas_permitidas_no_muestran_datos_de_otra_delegacion', MAT + 'test_un_usuario_sin_perfil_no_ve_datos_en_las_paginas_generales',
           MAT + 'test_las_acciones_post_respetan_el_perfil']),
]

# Resultados de los casos manuales: los completa el equipo después de ejecutarlos (estado: Aprobado, Fallido o Bloqueado).
RESULTADOS_MANUALES = {
    # 'CP-05': {'estado': 'Aprobado', 'obtenido': 'El correo llegó en 10 s con enlace válido.', 'fecha': '27-11-2026', 'evidencia': 'captura_correo.png'},
}

# Defectos encontrados al ejecutar el protocolo (registro real del desarrollo de la Evaluación 3).
DEFECTOS = [
    {
        'codigo': 'DEF-01', 'caso': 'CP-33', 'fecha': '24-11-2026', 'severidad': 'Baja', 'detectado': 'Revisión de código antes de ejecutar el protocolo',
        'descripcion': 'El Meta de CompromisoForm (labels y widgets) estaba pegado por error dentro de ComentarioForm.',
        'causa': 'Bloque de código movido a la clase equivocada en una entrega anterior; el segundo «widgets» reemplazaba al primero.',
        'impacto': 'El plazo de una tarea se escribía como texto libre (sin calendario) y el comentario perdía su etiqueta.',
        'correccion': 'Se movieron labels y widgets a CompromisoForm (fecha con type="date") y ComentarioForm quedó con su propio Meta (forms.py).',
        'reejecucion': [E3 + 'TuboTests.test_el_formulario_del_tubo_usa_selector_de_fecha'],
    },
    {
        'codigo': 'DEF-02', 'caso': 'CP-20', 'fecha': '24-11-2026', 'severidad': 'Alta', 'detectado': 'Ejecución 2 de la suite de regresión (2 pruebas fallidas)',
        'descripcion': 'Al agregar el Tubo de cartas, el campo «tipo» quedó obligatorio y crear una tarea sin indicarlo fallaba.',
        'causa': 'El campo del modelo tiene valor por defecto, pero el ModelForm lo exigía al recibirlo vacío.',
        'impacto': 'No se podían crear tareas desde integraciones o formularios que no enviaban el tipo.',
        'correccion': 'CompromisoForm: «tipo» opcional con valor por defecto «solicitud» y sin cambio posible al editar (clean_tipo).',
        'reejecucion': [INT + 'CompromisoVistasTests.test_crear_compromiso_deja_historial_y_auditoria', 'delegaciones_app.test_unit_compromisos.CompromisoFormUnitTests.test_un_compromiso_completo_es_valido'],
    },
    {
        'codigo': 'DEF-03', 'caso': 'CP-23', 'fecha': '24-11-2026', 'severidad': 'Media', 'detectado': 'Ejecución 2 de la suite de regresión',
        'descripcion': 'Los campos nuevos de la actividad (subtipo, hito, ingresar al Tubo, plazo) aparecían en una sección «Otros datos».',
        'causa': 'La plantilla agrupa los campos por nombre y los nuevos no estaban en ningún grupo.',
        'impacto': 'Formulario desordenado: campos clave lejos de su contexto.',
        'correccion': 'actividad_form.html: subtipo en «Qué se hizo»; hito, ingreso y plazo del Tubo en «Vinculación».',
        'reejecucion': ['delegaciones_app.test_unit_interfaz.FormularioDeActividadTests.test_el_formulario_agrupa_los_campos_sin_perder_ninguno'],
    },
    {
        'codigo': 'DEF-04', 'caso': 'CP-21', 'fecha': '24-11-2026', 'severidad': 'Baja', 'detectado': 'Ejecución 2 de la suite de regresión (2 pruebas fallidas)',
        'descripcion': 'La página del Tubo se renombró «Tubo de seguimiento», contra el término acordado por el equipo («Tubo de trabajo»), sin actualizar sus pruebas.',
        'causa': 'Se tomó el nombre de la guía sin revisar la decisión de interfaz previa ni las pruebas que la verifican.',
        'impacto': 'Inconsistencia de nombres entre pantallas, pruebas y manual.',
        'correccion': 'La página conserva «Tubo de trabajo»; las pestañas distinguen «Tubo de trabajo (seguimiento)» y «Tubo de cartas». '
                      'El nombre del menú se decidió después con el equipo: «Tubo» (ver cambios de requisito).',
        'reejecucion': ['delegaciones_app.test_unit_compromisos.TuboDeTrabajoUnitTests.test_la_pagina_dice_tubo_de_trabajo_y_el_menu_tareas',
                        'delegaciones_app.test_unit_interfaz.EncabezadoPieYAccesibilidadTests.test_el_menu_marca_la_seccion_activa_sin_cambiar_sus_enlaces'],
    },
    {
        'codigo': 'DEF-05', 'caso': 'CP-21', 'fecha': '24-11-2026', 'severidad': 'Media', 'detectado': 'Ejecución 2 de la suite de regresión (2 pruebas fallidas)',
        'descripcion': 'El botón «+ Agregar al tubo de trabajo» dejó de conservar la delegación filtrada con el formato esperado.',
        'causa': 'Se antepuso el parámetro ?tubo= al enlace, también para el Tubo de trabajo.',
        'impacto': 'La coordinación perdía la delegación preseleccionada al agregar una tarea.',
        'correccion': 'agenda.html: el parámetro tubo solo se agrega en el Tubo de cartas.',
        'reejecucion': ['delegaciones_app.test_unit_compromisos.TuboDeTrabajoUnitTests.test_el_boton_conserva_la_delegacion_filtrada',
                        'delegaciones_app.test_unit_compromisos.TuboDeTrabajoUnitTests.test_solo_quien_puede_crear_ve_el_boton_agregar'],
    },
    {
        'codigo': 'DEF-06', 'caso': 'CP-20', 'fecha': '24-11-2026', 'severidad': 'Baja', 'detectado': 'Ejecución 3 de la suite (1 prueba con error)',
        'descripcion': 'Defecto del caso de prueba, no del sistema: los datos de CP-EVA-023 no incluían el estado inicial de la tarea.',
        'causa': 'El formulario de alta exige «estado»; los datos de la prueba lo omitían.',
        'impacto': 'La prueba fallaba aunque la funcionalidad era correcta.',
        'correccion': 'Se completaron los datos de la prueba con estado «ingresado».',
        'reejecucion': [E3 + 'TuboTests.test_registrar_una_carta_genera_su_folio'],
    },
    {
        'codigo': 'DEF-07', 'caso': 'CP-10', 'fecha': '24-11-2026', 'severidad': 'Media', 'detectado': 'Revisión de las pantallas que muestran estados de actividad',
        'descripcion': 'Una actividad con antecedentes solicitados aparecía como «En preparación» en la lista, y su autor no recibía ningún aviso.',
        'causa': 'La plantilla de la lista y las alertas solo conocían los estados anteriores (pendiente, aprobada, rechazada).',
        'impacto': 'El autor podía no enterarse de que debía completar antecedentes y la actividad quedaba sin revisar.',
        'correccion': 'actividades.html muestra «Completar antecedentes solicitados» y alertas.py agrega la alerta con el detalle pedido por el verificador.',
        'reejecucion': [E3 + 'MasAntecedentesTests.test_el_autor_ve_la_alerta_y_el_estado_en_su_lista'],
    },
    {
        'codigo': 'DEF-08', 'caso': 'CP-35', 'fecha': '25-11-2026', 'severidad': 'Baja', 'detectado': 'Auditoría de la matriz de accesos (sin sesión)',
        'descripcion': 'Sin sesión, la exportación de organizaciones respondía 404 en vez de pedir el inicio de sesión.',
        'causa': 'La vista exportar_organizaciones solo verificaba el permiso y no tenía @login_required (defecto anterior a la Evaluación 3).',
        'impacto': 'No exponía datos, pero no era coherente con el resto de las rutas internas.',
        'correccion': 'crud.py: @login_required en exportar_organizaciones.',
        'reejecucion': [MAT + 'test_sin_sesion_toda_ruta_interna_pide_iniciar_sesion'],
    },
    {
        'codigo': 'DEF-09', 'caso': 'CP-06', 'fecha': '25-11-2026', 'severidad': 'Alta', 'detectado': 'Revisión de código del despliegue (Gunicorn con 3 workers)',
        'descripcion': 'El contador de intentos fallidos vivía en la caché en memoria, propia de cada proceso de Gunicorn.',
        'causa': 'Las pruebas corren en un solo proceso, así que no podían mostrar el problema; se detectó al revisar el despliegue.',
        'impacto': 'Con 3 workers un atacante tenía hasta 15 intentos en vez de 5, y el bloqueo dependía del proceso que atendía cada intento.',
        'correccion': 'settings.py: caché en archivos compartida por todos los procesos del servidor (CACHE_DIR, por defecto .cache/).',
        'reejecucion': [E3 + 'CacheCompartidaTests.test_en_el_servidor_la_cache_es_compartida_por_los_procesos'],
    },
    {
        'codigo': 'DEF-10', 'caso': 'CP-20', 'fecha': '25-11-2026', 'severidad': 'Media', 'detectado': 'Revisión de código del cálculo de metas',
        'descripcion': 'El ítem «Soluciones de ingresos al tubo» contaba también las cartas a las que se asignaba ese ítem.',
        'causa': 'Al agregar el Tubo de cartas sobre el mismo modelo, el cálculo del ítem no filtró por tipo.',
        'impacto': 'Las cartas cambiaban el porcentaje de tareas realizadas y el semáforo del funcionario.',
        'correccion': 'models.py (Indicador.calcular_avance): el ítem tipo tubo cuenta solo las tareas del Tubo de trabajo.',
        'reejecucion': [E3 + 'TuboTests.test_las_cartas_no_cambian_el_item_del_tubo_y_el_informe_las_distingue'],
    },
    {
        'codigo': 'DEF-11', 'caso': 'CP-20', 'fecha': '25-11-2026', 'severidad': 'Baja', 'detectado': 'Revisión de los informes exportables',
        'descripcion': 'El informe del Tubo mezclaba tareas y cartas sin una columna que las distinguiera.',
        'causa': 'Las columnas del informe eran anteriores al Tubo de cartas.',
        'impacto': 'El informe exportado no permitía separar tareas de cartas ni ver el RUT del solicitante.',
        'correccion': 'informes.py: columnas «Tubo» (Trabajo o Cartas) y «RUT», al final para no mover las columnas existentes.',
        'reejecucion': [E3 + 'TuboTests.test_las_cartas_no_cambian_el_item_del_tubo_y_el_informe_las_distingue'],
    },
]

# Pruebas existentes actualizadas porque la guía de la Evaluación 3 cambió el requisito (no son defectos).
CAMBIOS_DE_REQUISITO = [
    ('test_unit_actividades.ValidacionUnitTests.test_la_revision_solo_aprueba_o_rechaza', 'La revisión agrega «solicitar más antecedentes».'),
    ('test_unit_organizacion.FuncionarioFormUnitTests.test_al_crear_la_contrasena_es_obligatoria', 'Sin contraseña escrita se genera una temporal.'),
    ('test_unit_medicion.FichaPersonalUnitTests.test_resumen_de_evidencias_por_estado', 'Nuevo estado de evidencia «más antecedentes».'),
    ('test_integracion.MantenedoresTests (2 pruebas), test_unit_seguridad.AccesoPorPerfilTests (2), test_unit_transversal.MantenedoresUnitTests, test_unit_interfaz.IndiceDeMantenedoresTests',
     'De 12 a 17 mantenedores (territorios, vecinos, membresías, hitos y subtipos).'),
    ('test_integracion.SeedDemoTests.test_carga_el_modelo_nuevo_con_sus_datos_de_demostracion', 'Los datos demo incluyen una carta y las tablas nuevas.'),
    ('test_unit_plan_pruebas.ArmadoDelPlanTests.test_el_catalogo_tiene_los_casos_de_uso_y_los_38_requisitos', 'El catálogo de requisitos suma RF-051 a RF-062.'),
    ('test_unit_compromisos.TuboDeTrabajoUnitTests.test_la_pagina_dice_tubo_de_trabajo_y_el_menu_tareas, test_unit_interfaz.EncabezadoPieYAccesibilidadTests.test_el_menu_marca_la_seccion_activa_sin_cambiar_sus_enlaces',
     'Revisión del equipo (25-11-2026): el menú pasa de «Tareas» a «Tubo», porque ahora reúne el Tubo de trabajo y el Tubo de cartas (una carta no es una tarea).'),
]

# Ejecuciones de la suite completa durante el desarrollo (registro real; la última la agrega el comando).
EJECUCIONES = [
    {'numero': 1, 'fecha': '24-11-2026', 'pruebas': 727, 'fallidas': 0, 'nota': 'Línea base antes de los cambios de la Evaluación 3 (todas aprobadas).'},
    {'numero': 2, 'fecha': '24-11-2026', 'pruebas': 727, 'fallidas': 18,
     'nota': '7 fallas por 4 defectos reales (DEF-02 a DEF-05) y 11 por requisitos que la guía cambió (pruebas actualizadas, ver sección 6).'},
    {'numero': 3, 'fecha': '24-11-2026', 'pruebas': 784, 'fallidas': 1, 'nota': 'Defecto del caso de prueba DEF-06.'},
    {'numero': 4, 'fecha': '24-11-2026', 'pruebas': 74, 'fallidas': 1,
     'nota': 'Ejecución parcial (protocolo y plan): 1 falla por el catálogo de requisitos ampliado (cambio de requisito, sección 6).'},
    {'numero': 5, 'fecha': '25-11-2026', 'pruebas': 796, 'fallidas': 1,
     'nota': 'La corrección de DEF-11 agregó la columna «Tubo» al inicio del informe y movió las existentes; se trasladó al final.'},
]

# Incidencias de configuración del entorno resueltas (Actividad 3).
INCIDENCIAS = [
    ('La suite completa tardaba más de 10 minutos.', 'Cada prueba crea usuarios y PBKDF2 (1.000.000 de iteraciones) es lento a propósito.',
     'Solo al ejecutar pruebas se usa un hasher rápido (settings.EJECUTANDO_PRUEBAS); producción sigue con PBKDF2. La suite bajó a menos de 1 minuto.'),
    ('Los acentos de los mensajes de migración se ven mal en la consola de Windows.', 'La consola usa la página de códigos cp1252.',
     'Ejecutar con la variable PYTHONIOENCODING=utf-8 o en Windows Terminal; no afecta los datos (la base usa utf8mb4).'),
    ('Riesgo detectado al diseñar el bloqueo de ingreso: sus intentos fallidos podían bloquear el login en otras pruebas.', 'La caché en memoria dura todo el proceso de pruebas.',
     'En pruebas el máximo de intentos es muy alto y las pruebas del bloqueo fijan el suyo con override_settings y limpian la caché.'),
    ('La migración 0030 fallaría si ya existieran metas duplicadas.', 'Se agregó una restricción única (ítem, funcionario).',
     'La migración verifica antes y, si hay duplicados, se detiene con la lista de filas a corregir en vez de dejar la base a medias.'),
    ('Advertencia de WhiteNoise «No directory at: staticfiles» al ejecutar pruebas o runserver.', 'En desarrollo no se ejecuta collectstatic, así que la carpeta no existe.',
     'Es inofensiva en desarrollo; en el servidor se ejecuta python manage.py collectstatic --noinput (paso 6 del despliegue) y desaparece.'),
]
