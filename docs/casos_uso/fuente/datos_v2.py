# Casos de uso del SGR, versión 2.
# Fuente: código de proyecto-de-titulo-en-local (commit f4b3515), probado con un usuario de cada perfil.
# Actualizado con la rama feat/requerimientos-octubre de eva-backend-2 (botones de ajustes, accesos del menú,
# comentarios visibles y cierre semanal solo al registrar). delegaciones_app/test_casos_de_uso.py comprueba los actores.
# Los CU-01 a CU-31 (y sus .1, .2, .3) son los códigos que ya usa el software en su catálogo
# (delegaciones_app/plan_pruebas.py) y en las 601 pruebas: se conservan para que todo cuadre.
# Del CU-32 en adelante son casos que el informe no tenía y que el software sí hace.

U, P, D, C, A, MAIL = 'Usuario', 'Profesional', 'Delegado', 'Coordinador', 'Administrador', 'Servidor de correo'

CASOS = {}      # clave -> caso
_ORDEN = []


def caso(clave, tipo, nombre, cu=None, actores=(), proposito='', pre='', post='', flujo='', incluye=(), bases=(),
         condicion='', resultado='', pantalla='', nota='', hu=''):
    """cu = código que ya usa el software (None si es nuevo). bases solo para extensiones."""
    assert clave not in CASOS, clave
    CASOS[clave] = dict(clave=clave, tipo=tipo, nombre=nombre, cu=cu, actores=list(actores), proposito=proposito,
                        pre=pre, post=post, flujo=flujo, incluye=list(incluye), bases=list(bases), condicion=condicion,
                        resultado=resultado, pantalla=pantalla, nota=nota, hu=hu)
    _ORDEN.append(clave)
    return clave


def base(clave, nombre, cu, actores, proposito, pre, post, flujo, incluye=(), pantalla='', nota='', hu=''):
    return caso(clave, 'base', nombre, cu, actores, proposito, pre, post, flujo, incluye, pantalla=pantalla, nota=nota, hu=hu)


def inc(clave, nombre, cu, proposito, pre, post, flujo, nota=''):
    return caso(clave, 'include', nombre, cu, ['Sistema'], proposito, pre, post, flujo, nota=nota)


def ext(clave, nombre, cu, bases, condicion, resultado, nota=''):
    return caso(clave, 'extend', nombre, cu, bases=bases, condicion=condicion, resultado=resultado, nota=nota)


# ---------------------------------------------------------------- casos comunes (se reutilizan)
inc('auditar', 'Registrar en auditoría', None, 'Dejar constancia de quién hizo la operación, cuándo y qué cambió.',
    'Se creó, modificó, eliminó, revisó o exportó un dato.', 'Evento guardado; nadie puede editarlo ni borrarlo.',
    'Guardar usuario, fecha, acción, registro y valores antes y después.')
inc('buscar', 'Buscar y filtrar', 'CU-29', 'Encontrar registros por texto o filtros, solo dentro del ámbito del usuario.',
    'Hay criterios de búsqueda o se abrió una lista.', 'Lista filtrada; Delegado y Profesional ven solo su delegación (CU-29.1).',
    'Aplicar el texto y los filtros sobre los registros autorizados.')
ext('sin_resultados', 'Consulta sin coincidencias', None, ['buscar'], 'Ningún registro cumple el criterio.',
    'Se informa que no hay resultados, sin error.')
ext('error_valid', 'Informar error de validación', None, [], 'Un campo obligatorio está vacío o un dato no cumple una regla.',
    'El formulario vuelve con el error junto al campo y no se guarda nada.')
ext('desactivar', 'Desactivar en vez de eliminar', None, [], 'El registro tiene datos relacionados.',
    'No se borra: queda inactivo para conservar el historial, la confirmación explica por qué y después se puede reactivar.')
ext('protegido', 'Impedir eliminación con datos relacionados', None, [], 'Otros registros dependen de este.',
    'La eliminación se rechaza y se informa qué registros lo impiden.')
ext('periodo_cerrado', 'Restricción por período cerrado', 'CU-28.1', [], 'El período del registro está cerrado.',
    'No se guarda: un período cerrado solo cambia con una reapertura auditada.')
ext('denegar', 'Denegar acceso por ámbito', 'CU-26.1', [], 'El registro o la pantalla está fuera del perfil o de la delegación del usuario.',
    'Se responde «no encontrado» o se vuelve al panel, y el intento queda en la auditoría.')

# ---------------------------------------------------------------- G01 Gestionar acceso al sistema
base('login', 'Iniciar sesión', None, [U], 'Entrar al SGR con su cuenta y llegar al panel de su perfil.',
     'El usuario tiene una cuenta activa.', 'Sesión iniciada y panel del perfil mostrado.',
     'Ingresar usuario y contraseña; el sistema valida y muestra el panel según el perfil.', ['cred'], '/login/', hu='HU-26 (RF-002)')
base('logout', 'Cerrar sesión', None, [U], 'Salir del sistema de forma segura.', 'Sesión iniciada.',
     'Sesión terminada y portada mostrada.', 'Elegir «Cerrar sesión».', [], '/logout/', hu='HU-26 (RF-002)')
base('recuperar', 'Recuperar contraseña', None, [U, MAIL], 'Recibir por correo un enlace para crear una contraseña nueva.',
     'La cuenta tiene correo registrado.', 'Correo enviado con un enlace de un solo uso que vence en 1 hora.',
     'Ingresar el correo; el sistema genera el enlace y lo envía.', ['enviar_enlace'], '/recuperar/', hu='HU-26 (RF-002)')
base('restablecer', 'Restablecer contraseña', None, [U], 'Definir una contraseña nueva con el enlace recibido.',
     'Se recibió el enlace de recuperación.', 'Contraseña cambiada; el enlace deja de servir.',
     'Abrir el enlace, escribir la nueva contraseña dos veces y guardar.', ['validar_enlace'], '/recuperar/<uidb64>/<token>/', hu='HU-26 (RF-002)')
inc('cred', 'Validar credenciales', None, 'Comprobar usuario y contraseña de una cuenta activa.', 'Se ingresaron usuario y contraseña.',
    'Credenciales aceptadas o rechazadas.', 'Comparar la contraseña con su hash PBKDF2 y revisar que la cuenta esté activa.')
inc('enviar_enlace', 'Enviar enlace por correo', None, 'Mandar el enlace de recuperación al correo de la cuenta.',
    'Hay una solicitud de recuperación.', 'Correo entregado al servidor SMTP.', 'Generar el token temporal y enviarlo.')
inc('validar_enlace', 'Validar enlace de recuperación', None, 'Verificar que el enlace sea auténtico, no usado y vigente.',
    'Se abrió un enlace.', 'Enlace aceptado o rechazado.', 'Comprobar el token y su vigencia.')
ext('cred_mal', 'Informar credenciales incorrectas', None, ['cred'], 'Usuario o contraseña no coinciden, o la cuenta está inactiva.',
    'Se informa el error sin decir qué dato falló y no se inicia sesión.')
ext('enlace_vencido', 'Informar enlace vencido', None, ['validar_enlace'], 'El enlace ya se usó o pasó 1 hora.',
    'Se informa que no es válido y se ofrece pedir uno nuevo.')

# ---------------------------------------------------------------- G02 Gestionar actividades
base('act_reg', 'Registrar actividad', 'CU-01', [U], 'Registrar una gestión hecha en terreno para que cuente en su meta.',
     'Sesión iniciada, ficha de funcionario y período abierto.',
     'Actividad «pendiente de revisión», con código EVD y su puntaje evaluado.',
     'Completar delegación, ítem, tipo de atención, fecha, solicitud, acción, contacto y organización; el sistema valida, genera el código, evalúa el puntaje y guarda.',
     ['act_valid', 'codigo', 'puntaje', 'auditar'], '/actividad/nueva/', hu='HU-01')
base('act_con', 'Consultar actividades', None, [U], 'Ver las actividades de su ámbito con su estado, evidencias y comentarios.',
     'Sesión iniciada.', 'Lista o detalle mostrado; Delegado y Profesional ven solo su delegación.',
     'Abrir «Actividades», buscar por código o filtrar, y abrir el detalle.', ['act_buscar'], '/actividades/ y /actividad/<código>/', hu='HU-01, HU-29')
base('act_mod', 'Modificar actividad', None, [U], 'Corregir una actividad que todavía no está aprobada.',
     'No aprobada, período abierto, y el usuario es su autor, Coordinador o Administrador.', 'Actividad actualizada.',
     'Buscar la actividad, cambiar los datos y guardar; el sistema valida y vuelve a evaluar el puntaje.',
     ['act_buscar', 'act_valid', 'puntaje', 'auditar'], '/actividad/<código>/editar/', hu='HU-01')
base('act_eli', 'Eliminar actividad', None, [C, A], 'Borrar una actividad registrada por error.',
     'No aprobada y período abierto.', 'Actividad y sus evidencias eliminadas.',
     'Buscar la actividad, revisar la confirmación (indica cuántas evidencias se borran) y confirmar.',
     ['act_buscar', 'auditar'], '/actividad/<código>/eliminar/', hu='HU-01')
base('comentar', 'Comentar actividad', 'CU-24', [P, D, A], 'Dejar una observación sobre la actividad para coordinar con el equipo.',
     'El usuario puede ver la actividad.', 'Comentario guardado y visible en el detalle de la actividad.',
     'Abrir el detalle, elegir «Comentar», escribir el comentario y guardar.', ['act_buscar', 'auditar'], '/actividad/<código>/comentario/', hu='HU-24 (EP-07)')
inc('act_valid', 'Validar campos de actividad', 'CU-01.1', 'Verificar que los datos estén completos y cumplan las reglas.',
    'Hay datos en el formulario.', 'Datos aceptados o rechazados con su error.',
    'Comprobar obligatorios, fecha dentro del período, teléfono válido y organización de la misma delegación.')
inc('codigo', 'Generar código verificador', 'CU-10', 'Dar a la actividad un código único e inmutable.',
    'La actividad se está registrando.', 'Código EVD asignado.', 'Generar el código y asociarlo a la actividad.')
inc('puntaje', 'Evaluar puntaje', None, 'Decidir si la actividad suma al avance según las reglas de octubre.',
    'Los datos ya se validaron.', 'Actividad marcada con o sin puntaje y su motivo.',
    'Revisar si es gestión interna o previa y si tiene nombre y teléfono del contacto.')
inc('act_buscar', 'Buscar actividad por código', 'CU-10.1', 'Localizar la actividad por su código o filtros, dentro del ámbito.',
    'Se eligió o buscó una actividad.', 'Actividad localizada.', 'Buscar por código, delegación, estado, fecha o ítem entre las autorizadas.')
ext('act_error', 'Gestionar error de validación', 'CU-01.2', ['act_valid'], 'Un dato es inválido (por ejemplo, teléfono «abc»).',
    'El formulario vuelve con el error junto al campo y no se guarda.')
ext('cierre_semanal', 'Rechazar por cierre semanal', None, ['act_valid'], 'Al registrar, la fecha es de una semana ya cerrada (cierre el martes) o es futura.',
    'Se informa y no se guarda.')
ext('tope_diario', 'Rechazar por tope diario', None, ['act_valid'], 'Al registrar, ya hay 7 ingresos ese día (parámetro del período).',
    'Se informa el máximo y no se guarda.')
ext('sin_puntaje', 'Registrar sin puntaje', None, ['puntaje'], 'Es gestión interna, gestión previa o falta nombre o teléfono del contacto.',
    'Se guarda para el historial, pero no suma al avance y queda el motivo.')
ext('vincular', 'Vincular tarea del tubo de trabajo', None, ['act_reg', 'act_mod'], 'El usuario elige una tarea del tubo en el formulario (campo opcional).',
    'La actividad queda asociada a esa tarea.')
ext('act_bloqueo', 'Bloquear cambios a la actividad', None, ['act_mod', 'act_eli'], 'La actividad está aprobada, su período cerrado o el usuario no es su autor.',
    'Se informa el motivo y no se cambia nada.')
ext('devolver', 'Devolver a revisión', None, ['act_mod'], 'La actividad estaba rechazada.',
    'Vuelve a «pendiente de revisión», igual que sus evidencias no aprobadas.')
ext('concurrencia', 'Controlar conflicto de concurrencia', 'CU-23.1', ['act_mod'], 'Otro usuario guardó el mismo registro mientras se editaba.',
    'No se pisan sus cambios: se avisa y se pide recargar.')
ext('act_sin', 'Consulta sin coincidencias', 'CU-10.2', ['act_buscar'], 'Ningún código o filtro coincide.', 'Se informa que no hay resultados.')

# ---------------------------------------------------------------- G03 Gestionar evidencias
base('evi_subir', 'Subir evidencia', 'CU-09', [U], 'Respaldar la actividad con una foto o documento.',
     'El usuario es el autor, la actividad no está aprobada y el período está abierto.', 'Evidencia guardada con su código y pendiente de revisión.',
     'Desde el detalle, elegir el archivo y un comentario; el sistema valida el archivo y guarda.',
     ['act_buscar', 'evi_valid', 'auditar'], '/actividad/<código>/evidencia/', hu='HU-09')
base('evi_ver', 'Ver evidencia', None, [U], 'Abrir o descargar el archivo que respalda una actividad.',
     'El usuario puede ver la actividad.', 'Archivo mostrado o descargado.',
     'Desde el detalle, elegir el archivo; el sistema verifica el permiso y lo entrega.', ['act_buscar'], '/evidencia/<código>/archivo/', hu='HU-09')
inc('evi_valid', 'Validar archivo de evidencia', 'CU-09.1', 'Aceptar solo archivos permitidos.', 'Se eligió un archivo.',
    'Archivo aceptado o rechazado.', 'Comprobar extensión JPG, PNG o PDF y tamaño máximo de 5 MB.')
ext('evi_invalida', 'Rechazar carga inválida', 'CU-09.2', ['evi_valid'], 'El archivo no es JPG, PNG o PDF, o supera 5 MB.',
    'Se rechaza con su motivo y no se guarda.')
ext('evi_bloqueo', 'Bloquear carga de evidencia', None, ['evi_subir'], 'La actividad está aprobada, su período cerrado o el usuario no es su autor.',
    'Se informa el motivo y no se sube el archivo.')

# ---------------------------------------------------------------- G04 Validar actividades
base('validar', 'Aprobar o rechazar actividad', 'CU-11', [D, C, A], 'Decidir si la actividad y sus evidencias cuentan para el avance.',
     'Actividad de su ámbito, con evidencias pendientes y que no sea propia.', 'Decisión guardada e indicadores recalculados.',
     'Abrir el detalle, revisar el archivo y elegir «Aprobar» o «Rechazar» con su motivo.',
     ['act_buscar', 'trazabilidad', 'recalcular', 'auditar'], '/actividad/<código>/aprobar/ o /rechazar/', hu='HU-11')
base('anular', 'Anular aprobación', None, [D, C, A], 'Quitar la aprobación de una actividad que no debió aprobarse.',
     'La actividad está aprobada y el revisor no es su autor.', 'La actividad deja de sumar y se recalcula hacia abajo.',
     'Abrir el detalle, escribir el motivo y confirmar.', ['act_buscar', 'recalc_anula', 'auditar'], '/actividad/<código>/anular/', hu='HU-11')
inc('trazabilidad', 'Registrar trazabilidad de decisión', 'CU-11.1', 'Guardar quién decidió, cuándo, el resultado y el motivo.',
    'Se tomó una decisión de revisión.', 'Validación guardada por cada evidencia.', 'Crear el registro de validación con revisor, fecha, resultado y motivo.')
inc('recalcular', 'Recalcular indicadores automáticamente', 'CU-06.1', 'Actualizar el avance de las metas tras un cambio.',
    'Cambió una actividad o una meta.', 'Indicadores, ficha y semáforo al día.', 'Volver a calcular el avance de las metas afectadas.')
inc('recalc_anula', 'Recalcular por anulación de registro', 'CU-07.2', 'Restar del avance lo que se había aprobado.',
    'Se anuló una aprobación.', 'Indicadores recalculados hacia abajo; el historial se conserva.', 'Recalcular las metas de la actividad anulada.')
ext('no_suma', 'Bloquear aporte al avance', 'CU-11.2', ['validar'], 'La decisión es «Rechazar».',
    'La actividad no suma; el autor puede corregirla y vuelve a revisión.')
ext('motivo', 'Exigir motivo', None, ['validar', 'anular'], 'Se rechaza o anula sin escribir el motivo.',
    'Se informa que el motivo es obligatorio y no se registra nada.')
ext('propia', 'Impedir revisión propia', None, ['validar', 'anular'], 'El revisor es el autor de la actividad.',
    'Se informa que nadie revisa su propio trabajo.')
ext('sin_pendientes', 'Informar sin evidencias pendientes', None, ['validar'], 'La actividad no tiene evidencias por revisar.',
    'Se informa y no se registra la decisión.')

# ---------------------------------------------------------------- G05 Gestionar tubo de trabajo
base('tarea_reg', 'Registrar compromiso', 'CU-02', [U], 'Agregar una solicitud o compromiso al tubo de trabajo de la delegación.',
     'Sesión iniciada y ficha de funcionario.', 'Tarea creada con folio e historial iniciado.',
     'Completar delegación, descripción, responsable y fecha comprometida; validar y guardar.',
     ['tarea_valid', 'folio', 'historial', 'auditar'], '/agenda/nueva/', hu='HU-02 (EP-01)')
base('tarea_agenda', 'Consultar agenda compartida', 'CU-12', [U], 'Ver las tareas del equipo y su vencimiento.', 'Sesión iniciada.',
     'Tareas mostradas y clasificadas por vencimiento.', 'Abrir «Tubo de trabajo» y filtrar por folio, descripción o delegación.',
     ['tarea_filtrar', 'clasificar'], '/agenda/', hu='HU-12')
base('tarea_seg', 'Seguimiento de compromisos', 'CU-14', [U], 'Ver el total de pendientes, en proceso y en alerta.', 'Sesión iniciada.',
     'Resumen con totales y lista de tareas.', 'Abrir «Solicitudes» y buscar.', ['tarea_filtrar', 'clasificar'], '/solicitudes/', hu='HU-14')
base('tarea_mod', 'Modificar tarea', None, [U], 'Corregir los datos de una tarea.',
     'El usuario es el responsable, Coordinador o Administrador.', 'Tarea actualizada.',
     'Buscar la tarea, cambiar los datos y guardar.', ['tarea_filtrar', 'tarea_valid', 'auditar'], '/agenda/<id>/editar/', hu='HU-12, HU-15')
base('tarea_estado', 'Actualizar estado de la tarea', 'CU-13', [U], 'Avanzar la tarea a pendiente, en proceso o realizada.',
     'El usuario es el responsable, Coordinador o Administrador.', 'Estado cambiado y anotado en el historial.',
     'Elegir el nuevo estado y agregar una observación.', ['tarea_filtrar', 'historial', 'auditar'], '/agenda/<id>/estado/<estado>/', hu='HU-13')
base('tarea_eli', 'Eliminar tarea', None, [C, A], 'Quitar una tarea creada por error.', 'La tarea existe.', 'Tarea eliminada.',
     'Buscar la tarea, revisar la confirmación y confirmar.', ['tarea_filtrar', 'auditar'], '/agenda/<id>/eliminar/', hu='HU-12')
inc('tarea_valid', 'Validar datos de compromiso', 'CU-02.1', 'Verificar los datos críticos de la tarea.', 'Hay datos en el formulario.',
    'Datos aceptados o rechazados.', 'Comprobar delegación, descripción, responsable de esa delegación y fecha comprometida.')
inc('folio', 'Generar folio', None, 'Dar a la tarea un número de seguimiento único.', 'La tarea se está creando.',
    'Folio AGR-fecha-código asignado.', 'Generar el folio con la fecha y un código aleatorio.')
inc('historial', 'Registrar historial de cambio de estado', 'CU-13.1', 'Guardar cada cambio con quién y cuándo.',
    'La tarea se creó o cambió de estado.', 'Historial actualizado.', 'Guardar estado anterior, nuevo, autor y observación.')
inc('tarea_filtrar', 'Filtrar agenda compartida', 'CU-12.1', 'Encontrar tareas por folio, descripción o delegación, dentro del ámbito.',
    'Hay criterios o se eligió una tarea.', 'Tareas filtradas.', 'Aplicar los filtros sobre las tareas autorizadas.')
inc('clasificar', 'Clasificar compromisos por vencimiento', 'CU-14.1', 'Marcar cada tarea como vigente, por vencer, vencida o realizada.',
    'Se muestran tareas.', 'Tareas clasificadas.', 'Calcular los días que faltan para la fecha comprometida.')
ext('tarea_falta', 'Bloquear guardado por campos faltantes', 'CU-02.2', ['tarea_valid'], 'Falta el responsable, la descripción o la fecha.',
    'Se informa y no se guarda.')
ext('asignar', 'Asignar responsable', None, ['tarea_reg'], 'Quien crea la tarea es Coordinador o Administrador.',
    'Elige al responsable; si la crea un Delegado o Profesional, queda a su cargo.')
ext('reasignar', 'Reasignar responsable', 'CU-15', ['tarea_mod'], 'Un Coordinador o Administrador cambia el responsable (continuidad operativa).',
    'La tarea pasa al nuevo responsable y queda en la auditoría.')
ext('no_responsable', 'Rechazar por no ser responsable', None, ['tarea_mod', 'tarea_estado'], 'El usuario no es el responsable ni Coordinador o Administrador.',
    'No se permite el cambio y el intento queda en la auditoría.')
ext('cierre_tarea', 'Reflejar cierre de compromiso', 'CU-13.2', ['tarea_estado'], 'Se marca «realizada».',
    'Exige la resolución, cierra la tarea y lo deja en el historial.')
ext('vencido', 'Destacar compromiso vencido', 'CU-02.3', ['clasificar'], 'La fecha comprometida ya pasó y no se realizó.',
    'La tarea se muestra en alerta roja.')
ext('conservar', 'Conservar tarea vencida', None, ['tarea_eli'], 'La tarea está vencida y no se realizó.',
    'No se elimina: se conserva como incumplimiento con su historial.')
ext('tarea_sin', 'Consulta sin coincidencias en agenda', 'CU-12.2', ['tarea_filtrar'], 'Ninguna tarea cumple el filtro.', 'Se informa, sin error.')

# ---------------------------------------------------------------- G06 Gestionar ajustes de puntaje (octubre 2026)
base('aj_inf', 'Informar felicitación o reclamo', None, [D, A], 'Registrar una felicitación o un reclamo formal para un funcionario o una delegación.',
     'Existe un respaldo formal (correo, carta o documento).', 'Ajuste «informado», pendiente de decisión.',
     'Elegir «Informar felicitación o reclamo» en el menú del usuario, completar tipo, origen, destinatario, período, fecha y respaldo; validar y guardar.',
     ['aj_valid', 'auditar'], '/ajustes/nuevo/', hu='Requerimientos de octubre')
base('aj_con', 'Consultar ajustes', None, [D, C, A], 'Ver los ajustes informados, aplicados y rechazados.', 'Sesión iniciada.',
     'Lista mostrada; el Delegado ve solo los de su delegación y los que informó.', 'Abrir el mantenedor de ajustes y filtrar.', ['buscar'], '/administracion/ajustes/', hu='Requerimientos de octubre')
base('aj_mod', 'Modificar ajuste', None, [C, A], 'Corregir los datos de un ajuste.', 'El ajuste existe.', 'Ajuste actualizado.',
     'Buscar el ajuste, cambiar los datos y guardar.', ['buscar', 'aj_valid', 'auditar'], '/administracion/ajustes/<id>/editar/', hu='Requerimientos de octubre')
base('aj_dec', 'Aplicar o rechazar ajuste', None, [C, A], 'Decidir si el ajuste informado se aplica al puntaje.',
     'El ajuste está «informado».', 'Ajuste aplicado (cuenta en el puntaje) o rechazado.',
     'Abrir la lista de ajustes, elegir «Aplicar» o «Rechazar» en el ajuste y confirmar.', ['buscar', 'auditar'], '/ajustes/<id>/aplicar/ o /rechazar/',
     hu='Requerimientos de octubre')
inc('aj_valid', 'Validar datos de ajuste', None, 'Verificar que el ajuste esté completo y respaldado.', 'Hay datos en el formulario.',
    'Datos aceptados o rechazados.', 'Respaldo obligatorio, un solo destinatario y emisor si es felicitación; el Delegado solo elige su delegación.')

# ---------------------------------------------------------------- G07 Gestionar ausencias (octubre 2026)
base('au_reg', 'Registrar ausencia', None, [D, A], 'Anotar los días que un funcionario no trabajó para que no le bajen el cumplimiento.',
     'El Delegado solo elige funcionarios de su delegación.', 'Ausencia guardada y descontada del porcentaje esperado.',
     'Elegir «Registrar ausencia» en el semáforo, luego funcionario, período, tipo (licencia, vacaciones, administrativo, compensatorio, día libre o emergencia) y fechas; validar y guardar.',
     ['au_valid', 'auditar'], '/ausencias/nuevo/', hu='Requerimientos de octubre')
base('au_con', 'Consultar ausencias', None, [D, C, A], 'Ver las ausencias registradas.', 'Sesión iniciada.', 'Lista mostrada; el Delegado ve solo las de su equipo.',
     'Abrir el mantenedor de ausencias y filtrar.', ['buscar'], '/administracion/ausencias/', hu='Requerimientos de octubre')
base('au_mod', 'Modificar ausencia', None, [C, A], 'Corregir las fechas o el tipo de una ausencia.', 'La ausencia existe.', 'Ausencia actualizada.',
     'Buscar la ausencia, cambiar los datos y guardar.', ['buscar', 'au_valid', 'auditar'], '/administracion/ausencias/<id>/editar/', hu='Requerimientos de octubre')
inc('au_valid', 'Validar datos de ausencia', None, 'Verificar fechas y funcionario.', 'Hay datos en el formulario.', 'Datos aceptados o rechazados.',
    'Comprobar obligatorios y que el término no sea anterior al inicio.')
ext('superpuesta', 'Rechazar ausencia superpuesta', None, ['au_valid'], 'El funcionario ya tiene una ausencia que se cruza con esas fechas.',
    'Se informa el cruce y no se guarda.')

# ---------------------------------------------------------------- G08 Gestionar atenciones sociales
base('social', 'Registrar atención social', 'CU-03', [P, A], 'Anotar la gestión social hecha a un vecino por etapas.',
     'Ficha de funcionario.', 'Atención guardada a nombre del funcionario.',
     'Elegir «Registrar atención social» en el menú del usuario, completar nombre y teléfono del vecino, etapa, tipo, subtipo y observación; validar y guardar.',
     ['social_valid', 'auditar'], '/casos-sociales/nuevo/',
     nota='Solo existe registrar; no hay lista para consultar ni modificar.', hu='HU-03')
inc('social_valid', 'Validar datos de atención social', None, 'Verificar los datos del vecino y la atención.', 'Hay datos en el formulario.',
    'Datos aceptados o rechazados.', 'Comprobar nombre, teléfono, etapa y tipo.')
ext('tres', 'Rechazar por máximo de tres gestiones', None, ['social'], 'El funcionario ya tiene tres gestiones con el mismo vecino.',
    'Se informa el máximo y no se guarda.')


CASOS['error_valid']['bases'] += ['aj_valid', 'au_valid', 'social_valid']
CASOS['periodo_cerrado']['bases'] += ['aj_inf', 'aj_mod', 'aj_dec', 'au_reg', 'au_mod']


# ---------------------------------------------------------------- mantenedores (patrón del ejemplo «Gestionar Empleados»)
FEM = {'organización', 'delegación', 'meta'}


def g(cosa, m, f):
    return f if cosa in FEM else m


def mantenedor(pref, cosa, plural, ruta, reg, ver, mod, eli, hu, valid_nombre, valid_regla, con_baja=False, con_periodo=False,
               cu_reg=None, cu_mod=None, valid_cu=None, error_cu=None, error_nombre=None, extra_inc_reg=()):
    claves = {}
    vc = valid_nombre
    claves['reg'] = base(f'{pref}_reg', f'Registrar {cosa}', cu_reg, reg, f'Incorporar {g(cosa, "un", "una")} {cosa} {g(cosa, "nuevo", "nueva")}.',
                         'Sesión iniciada con permiso para agregar.', f'{cosa[0].upper() + cosa[1:]} {g(cosa, "guardado", "guardada")}.',
                         'Elegir «Agregar», completar el formulario, validar y guardar.', [f'{pref}_valid', *extra_inc_reg, 'auditar'], f'{ruta}nuevo/', hu=hu)
    claves['con'] = base(f'{pref}_con', f'Consultar {plural}', None, ver, f'Ver {g(cosa, "los", "las")} {plural} y su estado.',
                         'Sesión iniciada con permiso para ver.', 'Lista mostrada.', 'Abrir el mantenedor, buscar o filtrar.', ['buscar'], ruta, hu=hu)
    claves['mod'] = base(f'{pref}_mod', f'Modificar {cosa}', cu_mod, mod, f'Corregir los datos de {g(cosa, "un", "una")} {cosa}.',
                         f'{g(cosa, "El", "La")} {cosa} existe.', 'Información actualizada.', 'Buscar el registro, cambiar los datos y guardar.',
                         ['buscar', f'{pref}_valid', *extra_inc_reg, 'auditar'], f'{ruta}<id>/editar/', hu=hu)
    claves['eli'] = base(f'{pref}_eli', f'Eliminar {cosa}', None, eli, f'Quitar {g(cosa, "un", "una")} {cosa} que ya no corresponde.',
                         f'{g(cosa, "El", "La")} {cosa} existe.', 'Registro eliminado, o desactivado si tiene datos relacionados.' if con_baja else 'Registro eliminado.',
                         'Buscar el registro, revisar la confirmación y confirmar.', ['buscar', 'auditar'], f'{ruta}<id>/eliminar/', hu=hu)
    inc(f'{pref}_valid', vc, valid_cu, 'Verificar que los datos estén completos y cumplan las reglas.', 'Hay datos en el formulario.',
        'Datos aceptados o rechazados.', f'Comprobar {valid_regla}.')
    if error_cu:
        ext(f'{pref}_error', error_nombre, error_cu, [f'{pref}_valid'], 'Un dato no cumple la regla.', 'Se informa y no se guarda.')
    else:
        CASOS['error_valid']['bases'].append(f'{pref}_valid')
    CASOS['desactivar' if con_baja else 'protegido']['bases'].append(f'{pref}_eli')
    if con_periodo:
        CASOS['periodo_cerrado']['bases'] += [f'{pref}_reg', f'{pref}_mod', f'{pref}_eli']
    return claves


# G09 organizaciones
mantenedor('org', 'organización', 'organizaciones', '/administracion/organizaciones/', [A], [U], [D, C, A], [A],
           'Requerimientos de octubre', 'Validar datos de organización', 'nombre, tipo, territorio y delegación', con_baja=True)
base('org_exp', 'Exportar organizaciones', None, [U], 'Descargar la lista de organizaciones visibles.', 'Sesión iniciada.',
     'Archivo CSV descargado con lo que el usuario puede ver.', 'Filtrar la lista y elegir «Exportar».', ['buscar'],
     '/administracion/organizaciones/exportar/', hu='Requerimientos de octubre')
base('org_imp', 'Importar organizaciones', None, [A], 'Cargar la base de juntas de vecinos entregada por el municipio.',
     'El Excel está en el servidor (nunca en GitHub).', 'Organizaciones creadas o actualizadas con su delegación.',
     'Ejecutar el comando, que lee el Excel, asigna la delegación por territorio (CIAS, PAMPA, ANTENA, AV DEL MAR, CENTRO, RURAL), deduce el tipo por el nombre y guarda.', [], 'comando importar_organizaciones (servidor)',
     nota='Sin pantalla. Con el Excel de 2.709 organizaciones quedan 24 sin delegación (ALFALFARES y filas sin territorio), marcadas para asignar a mano.', hu='Requerimientos de octubre')
# G10 delegaciones
mantenedor('del', 'delegación', 'delegaciones', '/administracion/delegaciones/', [C, A], [C, A], [C, A], [C, A],
           'HU-26', 'Validar datos de delegación', 'que el nombre esté y no se repita', con_baja=True)
base('delegado', 'Asignar delegado', None, [C, A], 'Definir qué funcionario es el delegado de cada delegación.',
     'La delegación y el funcionario existen.', 'Delegado asignado o cambiado.', 'Abrir «Delegados», elegir delegación y funcionario y guardar.',
     ['asig_valid', 'auditar'], '/coordinacion/delegados/', hu='HU-26')
inc('asig_valid', 'Validar asignación', None, 'Evitar que un funcionario sea delegado de dos delegaciones.', 'Se eligió delegación y funcionario.',
    'Asignación aceptada o rechazada.', 'Comprobar que no sea ya delegado de otra delegación.')
# G11 cargos
mantenedor('car', 'cargo', 'cargos', '/administracion/cargos/', [C, A], [C, A], [C, A], [C, A], 'HU-26', 'Validar datos de cargo',
           'nombre y vigencia', con_baja=True)
# G12 roles
mantenedor('rol', 'rol', 'roles', '/administracion/roles/', [A], [A], [A], [A], 'HU-26', 'Validar datos de rol',
           'que el nombre esté, no se repita y no sea un rol retirado')
ext('rol_sistema', 'Impedir eliminar rol del sistema', None, ['rol_eli'], 'Es un rol que usa el sistema o está reservado.', 'No se elimina y se explica por qué.')
CASOS['protegido']['bases'].remove('rol_eli')
# G13 funcionarios y usuarios
mantenedor('fun', 'funcionario', 'funcionarios', '/administracion/funcionarios/', [A], [A], [A], [A], 'HU-26',
           'Validar datos de funcionario', 'usuario único, correo, cargo y delegación', con_baja=True, extra_inc_reg=['perfil'])
inc('perfil', 'Asignar perfil de acceso', None, 'Dejar la cuenta en uno de los cuatro perfiles.', 'Se guarda un funcionario con su usuario.',
    'Usuario con un solo perfil y sus permisos.', 'Asignar el grupo que corresponde y quitar los demás.')
ext('usuario_dup', 'Informar usuario duplicado', None, ['fun_valid'], 'Ya existe una cuenta con ese usuario.', 'Se informa y no se guarda.')
ext('propia_cuenta', 'Impedir desactivar la propia cuenta', None, ['fun_eli'], 'El Administrador intenta eliminar o desactivar su propia cuenta.',
    'No se permite y se explica por qué.')
# G14 catálogo
mantenedor('cat', 'elemento de catálogo', 'elementos del catálogo', '/administracion/catalogo/', [C, A], [C, A], [C, A], [C, A], 'HU-27',
           'Validar datos de catálogo', 'código y nombre', con_baja=True, error_cu='CU-27.1', error_nombre='Restringir elemento duplicado')
CASOS['cat_error']['condicion'] = 'El código ya existe.'
CASOS['cat_error']['resultado'] = 'Se informa que está repetido y no se guarda.'
# G15 períodos y parámetros
mantenedor('per', 'período', 'períodos', '/administracion/periodos/', [C, A], [C, A], [C, A], [C, A], 'HU-28',
           'Validar datos de período', 'fechas de inicio y término y umbral entre 0 y 100 %')
CASOS['periodo_cerrado']['bases'].append('per_mod')
base('per_estado', 'Abrir, cerrar o reabrir período', 'CU-28', [C, A], 'Controlar el ciclo del período de medición.',
     'El período está en el estado que permite la acción.', 'Período abierto, cerrado o reabierto con nueva versión de parámetros.',
     'Buscar el período y elegir «Iniciar», «Cerrar» o «Reabrir».', ['buscar', 'auditar'], '/administracion/periodos/<id>/estado/<acción>/', hu='HU-28')
ext('reabrir', 'Exigir motivo de reapertura', None, ['per_estado'], 'Se elige «Reabrir».', 'Sin motivo no se reabre.')
mantenedor('par', 'parámetro', 'parámetros', '/administracion/parametros/', [A], [C, A], [C, A], [A], 'HU-25 (EP-07)',
           'Validar datos de parámetro', 'período, clave y valor', con_periodo=True, cu_mod='CU-25')
CASOS['protegido']['bases'].remove('par_eli')
# G16 ítems medibles y metas
mantenedor('item', 'ítem medible', 'ítems medibles', '/administracion/items/', [C, A], [C, A], [C, A], [C, A], 'HU-04 (EP-01)',
           'Validar reglas de configuración', 'que el ítem sea del cargo y que las ponderaciones no pasen de 100 %', con_periodo=True,
           cu_reg='CU-04', valid_cu='CU-04.1', error_cu='CU-04.2', error_nombre='Bloquear guardado por ponderación inválida')
base('matriz', 'Cargar matriz de cargos', None, [A], 'Crear los ítems de los 13 cargos desde la matriz del municipio.',
     'data/matriz_cargos.json, generado desde el Excel con generar_matriz (sin nombres de personas).', 'Ítems medibles creados por cargo y período.', 'Ejecutar el comando con el período de destino; crea los 13 cargos y sus ítems sin pisar los parámetros ya definidos.',
     [], 'comando cargar_matriz (servidor)', nota='Sin pantalla. La matriz trae un cargo cuyas ponderaciones suman 85 %: se informa como advertencia.', hu='Requerimientos de octubre')
mantenedor('meta', 'meta', 'metas', '/administracion/metas/', [C, A], [C, A], [C, A], [C, A], 'HU-05 (EP-02)',
           'Validar parámetros de meta', 'ítem, funcionario y valor objetivo mayor que 0', cu_reg='CU-05', valid_cu='CU-05.1',
           error_cu='CU-05.2', error_nombre='Bloquear guardado por valor inválido', extra_inc_reg=['recalcular'])
ext('meta_cerrado', 'Notificar período cerrado', 'CU-05.3', ['meta_reg', 'meta_mod', 'meta_eli'], 'El período de la meta está cerrado.',
    'Se informa y no se guarda.')
CASOS['protegido']['bases'].remove('meta_eli')
ext('meta_ind', 'Advertir indicadores asociados', None, ['meta_eli'], 'La meta ya tiene indicadores.', 'La confirmación avisa cuántos se borran con ella.')

# ---------------------------------------------------------------- G17 Consultar resultados
base('ficha', 'Seguimiento de avance (ficha personal)', 'CU-06', [U], 'Ver sus metas, avance, evidencias y tareas.', 'Ficha de funcionario.',
     'Ficha mostrada con el detalle del cálculo.', 'Abrir «Mi ficha» y elegir el período.', ['calculo', 'ambito'], '/gestion/mi-ficha/', hu='HU-06')
base('semaforo', 'Consultar semáforo de cumplimiento', 'CU-16', [U], 'Ver el cumplimiento en verde, amarillo o rojo.', 'Sesión iniciada.',
     'Semáforo mostrado.', 'Abrir «Semáforo» y elegir el período.', ['estado_sem', 'ambito'], '/gestion/semaforo/', hu='HU-16')
base('comparar', 'Comparar avance esperado y real', 'CU-17', [U], 'Ver la diferencia entre lo logrado y lo esperado al día.', 'Sesión iniciada.',
     'Diferencias mostradas.', 'Abrir «Dashboard» y elegir el período.', ['diferencia', 'ambito'], '/gestion/', hu='HU-17')
base('resumen', 'Consultar resumen ejecutivo', 'CU-18', [U], 'Ver el panel resumen de la delegación.', 'Sesión iniciada.',
     'Resumen mostrado.', 'Abrir «Mi panel» o «Resumen».', ['consolidar', 'ambito'], '/gestion/panel/ y /gestion/resumen/', hu='HU-18')
base('tablero', 'Consultar territorio y delegación', None, [U], 'Ver las delegaciones y las tareas de cada una.', 'Sesión iniciada.',
     'Tablero mostrado; Delegado y Profesional solo el de su delegación.', 'Abrir «Territorio» y elegir la delegación.', ['ambito'],
     '/territorio/ y /delegacion/<nombre>/', hu='HU-08 (parcial)')
base('alertas', 'Consultar alertas', 'CU-31', [U], 'Ver vencimientos, evidencias pendientes y avance bajo el umbral.', 'Sesión iniciada.',
     'Alertas mostradas con su enlace.', 'Abrir «Alertas».', ['alerta', 'ambito'], '/gestion/alertas/', hu='HU-31')
inc('ambito', 'Restricción de búsqueda por ámbito', 'CU-29.1', 'Mostrar solo los datos de la delegación del usuario.',
    'Se pidió una consulta.', 'Datos limitados a su ámbito.', 'Filtrar por la delegación del usuario, salvo Coordinador y Administrador.')
inc('calculo', 'Cálculo automático de cumplimiento', 'CU-07', 'Calcular avance, cumplimiento y ponderado.', 'Hay metas y actividades.',
    'Porcentajes calculados con tope de 120 %.', 'Aplicar las fórmulas de medición (CU-07.1) sobre lo aprobado.')
inc('estado_sem', 'Calcular estado del semáforo', 'CU-16.1', 'Clasificar el avance frente a lo esperado.', 'Hay indicadores.',
    'Color asignado.', 'Comparar avance y meta esperada al día, descontando ausencias.')
inc('diferencia', 'Calcular diferencia de avance', 'CU-17.1', 'Restar lo esperado de lo logrado.', 'Hay indicadores.', 'Diferencia calculada.',
    'Esperado = días transcurridos sobre días totales.')
inc('consolidar', 'Consolidar datos de delegación', 'CU-18.1', 'Reunir responsables, avance, semáforo y promedio.', 'Hay datos del período.',
    'Resumen armado.', 'Agrupar los indicadores por delegación.')
inc('alerta', 'Generar alerta por vencimiento próximo', 'CU-14.2', 'Avisar antes de que algo venza.', 'Hay tareas o evidencias pendientes.',
    'Alerta con motivo, responsable, fecha y enlace.', 'Revisar plazos, evidencias pendientes y umbral.')
ext('cumplida', 'Destacar meta cumplida', 'CU-06.2', ['ficha'], 'El avance alcanza el objetivo.', 'La meta se marca como cumplida.')
ext('detalle_formula', 'Mostrar detalle en reporte', 'CU-07.3', ['calculo'], 'El usuario abre el detalle del cálculo.', 'Se muestra la fórmula para verificarla a mano.')
ext('desviacion', 'Destacar desviación significativa', 'CU-17.2', ['diferencia'], 'La diferencia deja al funcionario en ámbar o rojo.', 'Queda destacada.')
ext('navegar', 'Navegar al detalle de gestión', 'CU-18.2', ['resumen'], 'El usuario hace clic en una cifra.', 'Se abre el detalle que explica la cifra.')
CASOS['denegar']['bases'] += ['act_buscar', 'ambito']

# ---------------------------------------------------------------- G18 Generar informes
base('informe', 'Generar informe', 'CU-20', [U], 'Obtener un informe de actividades, tareas o cumplimiento.', 'Sesión iniciada.',
     'Informe en pantalla con lo que el usuario puede ver.', 'Abrir «Informes», elegir el tipo y los filtros.', ['inf_cons', 'inf_ambito'],
     '/gestion/informes/', hu='HU-20')
inc('inf_cons', 'Consolidar datos filtrados', 'CU-20.1', 'Reunir las filas del informe según los filtros.', 'Se eligió tipo y filtros.',
    'Filas calculadas.', 'Filtrar actividades o tareas por los criterios.')
inc('inf_ambito', 'Restringir por ámbito de permisos', 'CU-20.2', 'No mostrar nada fuera del ámbito del usuario.', 'Hay filas.',
    'Filas autorizadas.', 'Limitar a la delegación del usuario.')
ext('imprimir', 'Imprimir informe', None, ['informe'], 'El usuario elige «Imprimir».', 'Se muestra la versión para imprimir.')
ext('exportar', 'Exportar informe', None, ['informe'], 'El usuario elige CSV o Excel.', 'Se descarga el archivo y queda en la auditoría.')
CASOS['sin_resultados']['bases'].append('inf_cons')

# ---------------------------------------------------------------- G19 Consultar auditoría y perfiles
base('auditoria', 'Consultar auditoría de cambios', 'CU-30', [A], 'Revisar quién hizo cada operación crítica y cuándo.',
     'Sesión iniciada como Administrador.', 'Eventos mostrados; no se pueden editar ni borrar.',
     'Abrir «Auditoría» y filtrar por usuario, acción, fecha o registro.', ['buscar'], '/administracion/auditoria/', hu='HU-30')
base('perfiles', 'Consultar perfiles y permisos', None, [A], 'Ver qué puede hacer cada perfil y sus usuarios.', 'Sesión iniciada como Administrador.',
     'Perfiles, permisos y usuarios mostrados.', 'Abrir «Perfiles».', [], '/administracion/perfiles/', hu='HU-26')
ext('inmutable', 'Bloqueo por alteración no autorizada', 'CU-30.1', ['auditoria'], 'Alguien intenta modificar o borrar un evento de auditoría.',
    'Se rechaza: la auditoría no se reescribe.')
CASOS['denegar']['bases'].append('auditoria')
CASOS['denegar']['condicion'] = ('El registro o la pantalla está fuera del perfil o de la delegación del usuario '
                                 '(por ejemplo, un Profesional abre la auditoría).')

# ---------------------------------------------------------------- gestiones (alto nivel)
GESTIONES = [
    dict(id='G01', nombre='Gestionar acceso al sistema', epica='EP-08', actores=[U, MAIL],
         casos=['login', 'logout', 'recuperar', 'restablecer', 'cred', 'enviar_enlace', 'validar_enlace', 'cred_mal', 'enlace_vencido']),
    dict(id='G02', nombre='Gestionar actividades', epica='EP-01', actores=[U],
         casos=['act_reg', 'act_con', 'act_mod', 'act_eli', 'comentar', 'act_valid', 'codigo', 'puntaje', 'act_buscar', 'auditar',
                'act_error', 'cierre_semanal', 'tope_diario', 'sin_puntaje', 'vincular', 'act_bloqueo', 'devolver', 'concurrencia',
                'act_sin', 'denegar']),
    dict(id='G03', nombre='Gestionar evidencias', epica='EP-03', actores=[U],
         casos=['evi_subir', 'evi_ver', 'act_buscar', 'evi_valid', 'auditar', 'evi_invalida', 'evi_bloqueo']),
    dict(id='G04', nombre='Validar actividades', epica='EP-03', actores=[D, C, A],
         casos=['validar', 'anular', 'act_buscar', 'trazabilidad', 'recalcular', 'recalc_anula', 'auditar', 'no_suma', 'motivo', 'propia',
                'sin_pendientes']),
    dict(id='G05', nombre='Gestionar tubo de trabajo', epica='EP-04', actores=[U],
         casos=['tarea_reg', 'tarea_agenda', 'tarea_seg', 'tarea_mod', 'tarea_estado', 'tarea_eli', 'tarea_valid', 'folio', 'historial',
                'tarea_filtrar', 'clasificar', 'auditar', 'tarea_falta', 'asignar', 'reasignar', 'no_responsable', 'cierre_tarea', 'vencido',
                'conservar', 'tarea_sin']),
    dict(id='G06', nombre='Gestionar ajustes de puntaje', epica='EP-02', actores=[D, C, A],
         casos=['aj_inf', 'aj_con', 'aj_mod', 'aj_dec', 'aj_valid', 'buscar', 'auditar', 'error_valid', 'periodo_cerrado', 'sin_resultados']),
    dict(id='G07', nombre='Gestionar ausencias', epica='EP-02', actores=[D, C, A],
         casos=['au_reg', 'au_con', 'au_mod', 'au_valid', 'buscar', 'auditar', 'error_valid', 'superpuesta', 'periodo_cerrado', 'sin_resultados']),
    dict(id='G08', nombre='Gestionar atenciones sociales', epica='EP-01', actores=[P, A],
         casos=['social', 'social_valid', 'auditar', 'error_valid', 'tres']),
    dict(id='G09', nombre='Gestionar organizaciones comunitarias', epica='EP-01', actores=[U],
         casos=['org_reg', 'org_con', 'org_mod', 'org_eli', 'org_exp', 'org_imp', 'org_valid', 'buscar', 'auditar', 'error_valid',
                'desactivar', 'sin_resultados']),
    dict(id='G10', nombre='Gestionar delegaciones', epica='EP-08', actores=[C, A],
         casos=['del_reg', 'del_con', 'del_mod', 'del_eli', 'delegado', 'del_valid', 'asig_valid', 'buscar', 'auditar', 'error_valid',
                'desactivar', 'sin_resultados']),
    dict(id='G11', nombre='Gestionar cargos', epica='EP-08', actores=[C, A],
         casos=['car_reg', 'car_con', 'car_mod', 'car_eli', 'car_valid', 'buscar', 'auditar', 'error_valid', 'desactivar', 'sin_resultados']),
    dict(id='G12', nombre='Gestionar roles', epica='EP-08', actores=[A],
         casos=['rol_reg', 'rol_con', 'rol_mod', 'rol_eli', 'rol_valid', 'buscar', 'auditar', 'error_valid', 'rol_sistema', 'sin_resultados']),
    dict(id='G13', nombre='Gestionar funcionarios y usuarios', epica='EP-08', actores=[A],
         casos=['fun_reg', 'fun_con', 'fun_mod', 'fun_eli', 'fun_valid', 'perfil', 'buscar', 'auditar', 'error_valid', 'usuario_dup',
                'propia_cuenta', 'desactivar', 'sin_resultados']),
    dict(id='G14', nombre='Gestionar catálogo', epica='EP-08', actores=[C, A],
         casos=['cat_reg', 'cat_con', 'cat_mod', 'cat_eli', 'cat_valid', 'buscar', 'auditar', 'cat_error', 'desactivar', 'sin_resultados']),
    dict(id='G15', nombre='Gestionar períodos y parámetros', epica='EP-08', actores=[C, A],
         casos=['per_reg', 'per_con', 'per_mod', 'per_eli', 'per_estado', 'par_reg', 'par_con', 'par_mod', 'par_eli', 'per_valid', 'par_valid',
                'buscar', 'auditar', 'error_valid', 'reabrir', 'periodo_cerrado', 'protegido', 'sin_resultados']),
    dict(id='G16', nombre='Gestionar ítems medibles y metas', epica='EP-02', actores=[C, A],
         casos=['item_reg', 'item_con', 'item_mod', 'item_eli', 'matriz', 'meta_reg', 'meta_con', 'meta_mod', 'meta_eli', 'item_valid',
                'meta_valid', 'recalcular', 'buscar', 'auditar', 'item_error', 'meta_error', 'periodo_cerrado', 'meta_cerrado', 'protegido',
                'meta_ind', 'sin_resultados']),
    dict(id='G17', nombre='Consultar resultados', epica='EP-05', actores=[U],
         casos=['ficha', 'semaforo', 'comparar', 'resumen', 'tablero', 'alertas', 'ambito', 'calculo', 'estado_sem', 'diferencia', 'consolidar',
                'alerta', 'cumplida', 'detalle_formula', 'desviacion', 'navegar', 'denegar']),
    dict(id='G18', nombre='Generar informes', epica='EP-06', actores=[U],
         casos=['informe', 'inf_cons', 'inf_ambito', 'imprimir', 'exportar', 'sin_resultados']),
    dict(id='G19', nombre='Consultar auditoría y perfiles', epica='EP-08', actores=[A],
         casos=['auditoria', 'perfiles', 'buscar', 'inmutable', 'denegar']),
]

EPICAS = {'EP-01': 'Registro y gestión de actividades', 'EP-02': 'Medición y desempeño', 'EP-03': 'Evidencias y verificación',
          'EP-04': 'Agenda colectiva y compromisos', 'EP-05': 'Monitoreo y control de gestión', 'EP-06': 'Reportabilidad y toma de decisiones',
          'EP-07': 'Plataforma colaborativa', 'EP-08': 'Administración, seguridad y trazabilidad'}

# ---------------------------------------------------------------- numeración de los casos nuevos (CU-32 en adelante)
# Se numeran siguiendo el orden de las gestiones (G01 a G19): primero sus casos de detalle, luego incluidos y extensiones.
_n = 32
_orden_tipo = {'base': 0, 'include': 1, 'extend': 2}
for _g in GESTIONES:
    for _k in sorted(_g['casos'], key=lambda k: _orden_tipo[CASOS[k]['tipo']]):
        if CASOS[_k]['cu'] is None:
            CASOS[_k]['cu'] = f'CU-{_n}'
            _n += 1
for _k in _ORDEN:
    assert CASOS[_k]['cu'] is not None, _k
ULTIMO = _n - 1
