# Avance del rediseño de la interfaz

Registro de cada fase del rediseño (rama `feat/interfaz-terracota`). Se agrega al final de cada fase, sin borrar lo anterior.

## Fase 0. Preparación (21-11-2026)

1. **Qué hicimos**
   - Creamos la rama `feat/interfaz-terracota` desde `main` actualizado (1263426; GitHub no tenía cambios nuevos).
   - Revisamos la configuración de Git: nombre y correo están configurados.
   - Medimos la línea base: `check` sin problemas y 681 pruebas aprobadas.
   - Pusimos al día la base local (migraciones 0027 y 0028), cargamos `seed_demo` y guardamos el resultado de `probe.py` (164 combinaciones) para compararlo al final.
   - Listamos dónde aparecen `estado_class`, los colores de Bootstrap, las alertas, `form.as_p` y los mensajes sobre permisos.
   - Registramos las referencias visuales.
2. **Archivos creados:** `docs/interfaz/LINEA_BASE.md`, `docs/interfaz/REFERENCIAS.md` y este archivo.
3. **Pruebas:** 681 en total, 681 aprobadas, 0 fallidas. Es la línea base.
4. **Qué mirar:** nada cambia en pantalla en esta fase.
5. **Límites:** ninguno en riesgo. La base local se respaldó antes de migrarla, fuera del repositorio.
6. **No verificado:** las referencias visuales (no hubo navegador en la sesión; quedan pendientes en `REFERENCIAS.md`) y las capturas «antes» (la lista está en `LINEA_BASE.md`; se pueden sacar desde `main` en cualquier momento).
7. **Commits:** `docs: línea base y referencias del rediseño de la interfaz`.

## Fase 1. Limpieza (21-11-2026)

1. **Qué hicimos**
   - «Administración» muestra solo las tarjetas que el perfil puede abrir (o agregar), sin «No disponible para tu perfil», sin «Sección 01…12» y con un subtítulo de una línea.
   - El encabezado de los paneles quedó con el kicker, el saludo y la delegación como etiqueta pequeña; sin descripción de permisos, sin la insignia oscura y sin «Roles: …».
   - Quitamos el bloque «Restringido para tu perfil» del Profesional y del Delegado; su grilla pasó de 3 a 2 columnas («Tus funciones» o «Tu delegación», y las alertas).
   - El panel del Coordinador lista sus mantenedores solo como enlaces, sin «crear · editar · eliminar» ni la nota de lo reservado.
   - La lista de un mantenedor ya no muestra «Solo lectura para tu perfil»; la ayuda menciona «Agregar» solo cuando se puede agregar.
   - Acortamos las introducciones de «Actividades», «Delegados», «Mantenedores» y «Perfiles».
   - Cambiamos la prueba permitida (regla 17) sin cambiar su nombre y agregamos `test_unit_interfaz.py`.
2. **Archivos cambiados:** `mantenedores.html`, `crud/lista.html`, `crud/perfiles.html`, `actividades.html`, `delegados.html`, `_panel_encabezado.html`, los 4 paneles, `test_integracion.py` (solo `test_indice_deshabilita_los_mantenedores_exclusivos_del_administrador`). **Creado:** `delegaciones_app/test_unit_interfaz.py`.
3. **Pruebas:** 686 en total (681 de la línea base y 5 nuevas), 686 aprobadas, 0 fallidas. Desde esta fase las corremos con `python manage.py test --parallel 6`: tardan 4 minutos en vez de 14 y dan el mismo resultado.
4. **Qué mirar:**
   - Como `funcionario.centro`, «Administración»: una sola tarjeta, «Organizaciones comunitarias», con «Abrir sección».
   - Como `coordinador.demo`, «Administración»: 10 tarjetas, ninguna gris.
   - El panel de cada perfil: el saludo y la delegación, sin textos sobre permisos.
5. **Límites:** todo se ocultó en las plantillas con las variables que ya entregan las vistas (`tarjeta.permitido`, `tarjeta.puede.add`, `puede.add`). No se tocaron vistas ni permisos.
6. **Mensajes de permisos adicionales:** el `grep` del encargo encontró uno más, en el ingreso («Usa tu cuenta para acceder a las funciones autorizadas por tu perfil y delegación.»), que la fase 2 reemplaza por el subtítulo que pide el encargo. Hay tres frases parecidas que no quitamos y quedan a decisión del grupo: «Ves solo los resultados de tu delegación» (`_filtros.html`), «dentro de tu ámbito» (`alertas.html`) y el bloque «Principio de acceso» (`institucional.html`).
7. **No verificado:** el aspecto en el navegador (sin navegador en la sesión).
8. **Commits:** `refactor: la interfaz muestra a cada perfil solo lo que puede hacer`; `test: pruebas de la limpieza de paneles y del índice de mantenedores`; `docs: avance de la fase 1 de la interfaz`.

## Fase 2. Base visual, formularios, ingreso y semáforo (21-11-2026)

1. **Qué hicimos**
   - Reescribimos `sgr.css` como sistema de diseño: variables de color con su contraste calculado, Roboto y Roboto Slab guardadas en `static/fonts/`, esquinas de 12 px en tarjetas y 8 px en botones y campos, sombras cálidas, insignias en píldora y alertas suaves. El parámetro de versión del CSS pasó a `?v=interfaz-20261121`.
   - El encabezado del sitio quedó claro, con la marca terracota y la sección activa marcada (`aria-current="page"`). El menú mantiene su orden, sus textos y sus condiciones.
   - Creamos las parciales `_campo.html`, `_formulario.html`, `_errores_formulario.html`, `_semaforo_insignia.html`, `_icono.html`, `_encabezado_pagina.html` y `_estado_vacio.html`, más el filtro de presentación `campo_sgr` (agrega «is-invalid»; Django 5.2 ya pone `aria-invalid` y `aria-describedby`).
   - «Registrar actividad» quedó en cuatro bloques («Dónde y cuándo», «Qué se hizo», «Contacto» y «Vinculación»); un quinto bloque «Otros datos» aparece solo si algún campo quedara fuera, así no se pierde ninguno. El panel «Reglas del registro» conserva su texto.
   - Nueva pantalla de ingreso: tarjeta centrada de 420 px, campos de 48 px, botón para mostrar u ocultar la contraseña y el aviso de credenciales arriba de los campos.
   - «Subir evidencia» con zona punteada, el tamaño máximo desde `tamano_maximo` y el nombre del archivo elegido.
   - El semáforo usa colores propios (verde `#1d7a46`, ámbar `#9a5b00`, carmesí `#b0123b`) con ícono y el mismo texto («Verde», «Ámbar», «Rojo», «Sin cálculo») en paneles, medición, resumen, ficha, semáforo, tubo de trabajo, delegados y alertas. `medicion.py` sigue entregando `success`, `warning` y `danger`.
   - «Tarea del tubo de trabajo», los mantenedores y los formularios de ajuste, ausencia, atención social y comentario usan `_formulario.html`.
2. **Archivos cambiados:** `base.html`, `sgr.css`, `actividad_form.html`, `compromiso_form.html`, `mantenedor_form.html`, `formulario_nuevo.html`, `evidencia_subir.html`, `registration/login.html`, `semaforo.html`, `dashboard.html`, `resumen.html`, `ficha.html`, `alertas.html`, `_panel_alertas.html`, los 4 paneles, `agenda.html`, `solicitudes.html`, `delegacion_detalle.html`, `delegados.html`, `crud/lista.html`, `crud/auditoria.html`. **Creados:** `static/fonts/` (5 fuentes, licencias y `LEEME.md`), `static/icons/sgr-iconos.svg`, `static/js/sgr.js`, `templates/includes/` (7 parciales), `delegaciones_app/templatetags/sgr_interfaz.py`.
3. **Pruebas:** 696 en total, 696 aprobadas, 0 fallidas (línea base 681; se agregaron 10).
4. **Qué mirar:**
   - `/login/` sin sesión, y con una contraseña errada: el aviso aparece arriba de los campos.
   - Como `funcionario.centro`, «Registrar actividad» con el teléfono `abc`: el campo queda marcado en carmesí con el mensaje debajo, arriba aparece «Revisa los campos marcados.» y el foco va al teléfono.
   - Como `delegado.demo`, «Resultados» > «Semáforo de avance»: Centro en «Rojo» con ícono de círculo con X.
5. **Límites:** no tocamos `forms.py`; las etiquetas «Delegacion», «Tipo accion» y «Organizacion» se ven sin tilde porque vienen del modelo y la regla 10 no permite cambiarlas. El formulario de mantenedores conserva su `<form>` sin `enctype` (agregarlo habría cambiado su comportamiento).
6. **No verificado en navegador real:** revisamos con capturas de Chrome sin ventana sobre un servidor local (ingreso, panel del Profesional, registrar actividad con error y semáforo). El editor marca dos avisos de contraste en `sgr.css` que son falsos positivos: texto blanco sobre un velo blanco translúcido encima de fondos oscuros (calculado: unos 10:1 y 5:1).
7. **Commits:** `feat: sistema de diseño terracota con fuentes, íconos y JavaScript propios`; `feat: formularios con el error junto a cada campo`; `feat: nueva pantalla de ingreso con mostrar u ocultar contraseña`; `feat: subir evidencia con zona de archivo y nombre del archivo elegido`; `feat: semáforo con colores propios, ícono y texto en todas las pantallas`; `test: pruebas de formularios, ingreso, semáforo y recursos locales`; `docs: avance de la fase 2 de la interfaz`.

## Fase 3. Portada y movimiento (21-11-2026)

1. **Qué hicimos**
   - Reescribimos `index.html` en varias líneas, con las mismas variables de la vista (`total_solicitudes`, `alertas`, `promedio`, `ejes`, `delegaciones`).
   - Hero en dos columnas: el título y el párrafo actuales; con sesión «Registrar actividad» y «Ver medición», sin sesión «Ingresar» y «Territorio». A la derecha, una ilustración SVG propia: el SGR al centro, seis puntos que orbitan (uno por delegación, 40 s por vuelta) y formas de teja y arco que flotan.
   - Accesos rápidos con ícono y texto de acción. Sin sesión: «Ingresar», «Territorio», «Cómo funciona», «Delegaciones» y «Preguntas frecuentes». Con sesión: los destinos del menú con sus mismas condiciones.
   - Cifras que cuentan de 0 a su valor (900 ms); el valor final está en el HTML y el lector de pantalla lee solo ese.
   - «Cómo funciona»: los cinco pasos actuales como tarjetas con motivo geométrico propio (círculo, cuadrícula, hexágono, triángulo y semáforo), unidas por una línea que se completa al bajar.
   - Las seis delegaciones con su enlace actual y los ejes de gestión como etiquetas.
   - Seis preguntas frecuentes en acordeón (collapse de Bootstrap). Sin JavaScript las respuestas se ven abiertas.
   - `sgr.js` reúne: aparición al bajar, conteo, llenado de barras, encabezado compacto, foco en el primer error, nombre del archivo elegido, mostrar u ocultar contraseña, acordeón y barra de accesibilidad.
2. **De dónde sale cada respuesta**

   | Pregunta | Fuente |
   | --- | --- |
   | ¿Quién registra las actividades? | `templates/delegaciones_app/actividad_form.html` (texto «El registro quedará asociado a tu usuario y a la delegación seleccionada.» y «Se genera un código único.»); `delegaciones_app/views.py:223` (`actividad_nueva`) |
   | ¿Cuándo suma una actividad al avance? | `delegaciones_app/models.py:858-866` (solo actividades `aprobada`, con `cuenta_puntaje` y evidencia aprobada); `docs/REQUERIMIENTOS_V2.md:62` (RN-014: nombre y teléfono, sin gestión interna ni previa) |
   | ¿Quién revisa la evidencia? | `delegaciones_app/views.py:31` (`MENSAJE_REVISION_PROPIA`); `delegaciones_app/permisos.py:126` (`puede_revisar`); motivo obligatorio del rechazo en `docs/DEMO_EXPOSICION.md`, flujo 2 |
   | ¿Qué evidencia se acepta? | `delegaciones_app/models.py:356` (`EXTENSIONES_EVIDENCIA`: jpg, jpeg, png y pdf); el tamaño máximo no se escribe a mano: lo muestra «Subir evidencia» desde `gestion_laserena/settings.py:192` |
   | ¿Cómo se calcula el semáforo? | `delegaciones_app/medicion.py:36-41` (`_semaforo`) |
   | ¿Hasta cuándo puedo registrar una actividad? | `delegaciones_app/reglas.py:14-22` (`semana_abierta`) y `:25-29` (fechas futuras); `docs/REQUERIMIENTOS_V2.md:64` (RN-016) |

3. **Archivos cambiados:** `templates/delegaciones_app/index.html`, `static/css/sgr.css`, `static/js/sgr.js`, `delegaciones_app/test_unit_interfaz.py`.
4. **Pruebas:** 699 en total, 699 aprobadas, 0 fallidas (línea base 681).
5. **Qué mirar:** la portada sin sesión y como `funcionario.centro`; bajar despacio para ver las apariciones y la línea de los pasos; abrir y cerrar las preguntas.
6. **Comprobado:** con capturas de Chrome sin ventana a 1280 px y en un marco de 375 px (Chrome sin ventana no baja de 504 px de ancho, así que usamos un marco), y con la portada guardada sin sus `<script>` para simular un navegador sin JavaScript: todo el contenido queda visible. En el celular los accesos rápidos van en dos columnas.
7. **No verificado:** el movimiento en sí (las capturas son imágenes fijas) y el modo de movimiento reducido del sistema operativo; ambos están cubiertos en el CSS (`@media (prefers-reduced-motion: reduce)`) y en `sgr.js`.
8. **Límites:** no se cambió la vista `index`. Las respuestas no muestran códigos internos (RN, RF, CU), porque una prueba existente lo impide en las pantallas.
9. **Commits:** `feat: portada con hero de órbitas, accesos rápidos y preguntas frecuentes`; `test: pruebas de la portada con y sin sesión`; `docs: avance de la fase 3 de la interfaz`.
