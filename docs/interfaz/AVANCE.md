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

## Fase 4. Paneles, encabezado, pie, tablas y accesibilidad (21-11-2026)

1. **Qué hicimos**
   - Paneles: «Tus funciones», «Tu delegación», «Coordinación de delegados», «Transacciones autorizadas», «Gestión de usuarios» y «Transacciones» pasaron de botones a mosaicos con ícono, texto de acción y movimiento al pasar el mouse. Mismos textos, mismos enlaces y mismas condiciones. El acceso principal va en terracota: «Registrar actividad con evidencia» (Profesional), «Revisar evidencias pendientes» (Delegado), «Delegados y asignaciones» (Coordinador) y «Crear usuario» (Administrador). Los mantenedores del Coordinador quedan como lista de enlaces con flecha.
   - Encabezado: franja superior con «Municipalidad de La Serena · Departamento de Gestión Territorial» y el botón «Accesibilidad»; menú claro con desenfoque que se compacta al bajar. En el celular, el menú se abre en un panel con áreas de toque de 44 px. Con el texto aumentado, el menú baja a una segunda fila.
   - Pie (`footer` > `div.container`, fondo carbón y borde terracota de 4 px): marca y descripción del SGR; «Secciones» con las mismas condiciones del menú; «Ayuda» con «¿Olvidaste tu contraseña?» (sin sesión), «Territorio» y el botón de accesibilidad; franja «Sistema de Gestión de Resultados · Prototipo académico INACAP 2026». Sin teléfonos, direcciones, redes ni páginas inventadas.
   - Tablas de actividades, tubo de trabajo, mantenedores y auditoría: encabezado fijo dentro de la tabla, filas más aireadas, filtros en una tarjeta clara y estado vacío con ícono. Los nombres de los parámetros de búsqueda no cambiaron.
   - Barra de accesibilidad: «Aumentar texto», «Achicar texto», «Alto contraste», «Links subrayados» y «Reiniciar», con las clases del kit (`a11y-font-0`, `a11y-font-1`, `a11y-font-2`, `a11y-contrast`) y una propia (`a11y-subrayar`). Los botones de alternar llevan `aria-pressed`; la preferencia se guarda en `localStorage` dentro de `try/catch`. Sin JavaScript, el botón no aparece.
   - Revisión: agregamos `aria-label` a cinco campos que solo tenían texto de ejemplo (búsquedas de mantenedores, auditoría y medición, y los motivos de anulación y de acción). No hay etiquetas `img` en las plantillas. Una prueba nueva revisa que las pantallas principales tengan un solo `h1`.
2. **Archivos cambiados:** `base.html`, `sgr.css`, los 4 paneles, `actividades.html`, `agenda.html`, `solicitudes.html`, `mantenedores.html`, `crud/lista.html`, `crud/auditoria.html`, `actividad_detalle.html`, `_filtros.html`, `test_unit_interfaz.py`.
3. **Pruebas:** 703 en total, 703 aprobadas, 0 fallidas (línea base 681).
4. **Qué mirar:**
   - El panel de cada perfil: mosaicos con el acceso principal en terracota.
   - «Accesibilidad» arriba a la derecha: probar cada botón y recargar la página (la preferencia se mantiene).
   - El pie con y sin sesión.
   - «Actividades» con muchos registros: al bajar dentro de la tabla, el encabezado queda fijo.
5. **Comprobado con capturas:** los 4 paneles, «Actividades» y «Administración» como Profesional a 1280 px; el panel del Delegado en alto contraste con texto al 125 % y al 150 %.
6. **Límites:** las condiciones de cada mosaico y de cada enlace del pie son las mismas del menú o del panel original. No se tocó ninguna vista.
7. **Commits:** `feat: paneles con mosaicos de acceso rápido`; `feat: pie en bloques y barra de accesibilidad con las clases del kit`; `feat: tablas con encabezado fijo, filtros en tarjeta y estados vacíos`; `test: pruebas del pie, la barra de accesibilidad y el menú activo`; `docs: avance de la fase 4 de la interfaz`.

## Fase 5. Verificación y documentación (21-11-2026)

1. **Qué hicimos**
   - `check` sin problemas; `makemigrations --check --dry-run`: «No changes detected»; 703 pruebas aprobadas.
   - `probe.py` con la base local de demostración: 200 de 200 combinaciones iguales a la línea base (el script actual recorre 50 pantallas con 4 perfiles; el encargo mencionaba 164).
   - Recorrimos los textos de los 3 flujos de `docs/DEMO_EXPOSICION.md` en la base local. Para ver «Subir evidencia» y la revisión con «Aprobar» y «Rechazar», hicimos el flujo 1 en la base local, sacamos las capturas y después restauramos el respaldo de la base y borramos el archivo subido.
   - Revisamos 375, 768 y 1280 px con capturas (para 375 y 768 usamos un marco, porque Chrome sin ventana no baja de 504 px).
   - Ajustes finales: el texto de ejemplo de los campos subió de 3,99:1 a 5,30:1, y las cifras de la portada muestran su valor final aunque el navegador pause la animación.
   - Escribimos `GUIA_DE_ESTILO.md` y `CAMBIOS_INTERFAZ.md` (con la sección «Para desplegar») y guardamos 16 capturas en `docs/interfaz/capturas/`.
2. **Archivos:** `static/js/sgr.js`, `static/css/sgr.css`, `docs/interfaz/GUIA_DE_ESTILO.md`, `docs/interfaz/CAMBIOS_INTERFAZ.md`, `docs/interfaz/capturas/` (16 PNG).
3. **Pruebas:** 703 en total, 703 aprobadas, 0 fallidas (línea base 681).
4. **Qué mirar:** las capturas de `docs/interfaz/capturas/` y, en local, los 3 flujos de la demo.
5. **Para desplegar:** correr `python manage.py collectstatic --noinput` en el servidor después del `git pull` (detalle en `CAMBIOS_INTERFAZ.md`). No lo ejecutamos.
6. **No verificado:** capturas «antes» (se sacan desde `main`); el movimiento en un navegador real y el modo de movimiento reducido del sistema operativo; la revisión de las páginas de referencia con navegador.
7. **Commits:** `fix: cifras de la portada con respaldo y texto de ejemplo con contraste suficiente`; `docs: guía de estilo de la interfaz`; `docs: cambios de la interfaz con capturas y pasos para desplegar`; `docs: avance de la fase 5 de la interfaz`.
