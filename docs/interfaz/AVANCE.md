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

# Segunda ronda: Territorio, modo oscuro y ajustes

Rama `feat/interfaz-ronda-2`, creada desde `main` en caf02d6 (PR #20). Mismo formato de informe que la primera ronda.

## Ronda 2, fase 0. Preparación (21-11-2026)

1. **Qué hicimos**
   - Actualizamos `main` (sin cambios nuevos desde caf02d6) y creamos la rama `feat/interfaz-ronda-2`.
   - Revisamos la configuración de Git: nombre y correo están configurados.
   - Línea base: `check` sin problemas y 703 pruebas aprobadas.
   - Leímos la guía de estilo, `base.html`, `sgr.css`, `sgr.js`, la portada, Territorio, la vista `institucional` y `test_unit_interfaz.py`.
   - Contamos los colores escritos a mano en `sgr.css`: 141 apariciones en formato `#…` (58 valores distintos) y 20 en `rgba(…)`. El plan para el modo oscuro: los que son fondo, borde o texto pasan a variables con su valor oscuro; los que van sobre fondos que no cambian (texto blanco sobre terracota, el pie oscuro) quedan como están o pasan a variables propias del pie.
   - Buscamos en las pruebas y en `docs/DEMO_EXPOSICION.md` los textos de Territorio y de la portada que vamos a cambiar («Principio de acceso», «Información institucional de referencia», «Las delegaciones hoy», «Ver contexto», etc.): ninguno aparece.
2. **Archivos:** solo este informe.
3. **Pruebas:** 703 en total, 703 aprobadas, 0 fallidas. Es la línea base de esta ronda.
4. **Qué mirar:** nada cambia en pantalla en esta fase.
5. **Límites:** ninguno en riesgo.
6. **No verificado:** nada pendiente en esta fase.
7. **Commits:** `docs: línea base de la segunda ronda de la interfaz`.

## Ronda 2, fase 1. Territorio (21-11-2026)

1. **Qué hicimos**
   - Corregimos las cifras de población en la vista `institucional` (única excepción permitida en `views.py`): 88,0 % urbana y 12,0 % rural según el Censo de Población y Vivienda 2024 del INE, y agregamos al contexto `fuente_poblacion`. El total 250.141 no cambió.
   - Reescribimos `institucional.html` en varias líneas con los componentes de la portada:
     - hero en dos columnas con kicker «Territorio», el mismo título, una línea de introducción y dos botones (sin sesión «Ingresar» y «Ver delegaciones»; con sesión «Ir a mi panel» y «Ver delegaciones»);
     - a la derecha, un esquema propio de la comuna en SVG: franja de mar al oeste con olas que se mueven muy lento, zona urbana punteada, la zona rural difusa al oriente, líneas desde Centro y el norte arriba. Los 6 nodos laten suavemente y desfasados. Debajo dice «Esquema referencial, no a escala»;
     - cuatro cifras con el conteo animado (250.141, 88,0 %, 12,0 % y 6 delegaciones municipales), una barra urbana y rural que se llena al aparecer y la línea «Fuente: Censo de Población y Vivienda 2024, INE»;
     - las seis delegaciones con una fila de 6 botones, tarjetas con su motivo geométrico propio, aparición escalonada y movimiento al pasar el mouse. Cada tarjeta tiene un `id` estable (`delegacion-las-companias`, etc.);
     - al pasar el mouse o enfocar un nodo o un botón se resalta su tarjeta, y al revés; al hacer clic, la página baja a la tarjeta y la marca como seleccionada;
     - con sesión, «Ver seguimiento» solo en la tarjeta de la propia delegación, o en las seis para la coordinación (la misma condición del menú y de la vista). Sin sesión, ninguna tarjeta enlaza a pantallas privadas;
     - cierre con una banda terracota: «¿Trabajas en una delegación?» con «Ingresar», o «Ir a mi panel» con sesión.
   - Quitamos las insignias «Territorio» e «Información institucional de referencia» y el bloque «Principio de acceso».
   - Sin JavaScript, los nodos y los botones son enlaces normales a cada tarjeta, todas las tarjetas se ven completas y el esquema queda como imagen con su texto alternativo.
   - Accesibilidad: el dibujo tiene `role="img"` y un `aria-label` que nombra las 6 delegaciones; los nodos son enlaces que se enfocan con teclado y su nombre es el texto visible; un solo `h1`. El movimiento se apaga con `prefers-reduced-motion`.
2. **Archivos cambiados:** `delegaciones_app/views.py` (solo los textos de `urbano` y `rural` y la clave `fuente_poblacion`), `delegaciones_app/templatetags/sgr_interfaz.py` (filtro `partes_cifra`, que separa «88,0 %» en número, decimales y sufijo para el conteo), `templates/delegaciones_app/institucional.html`, `static/css/sgr.css`, `static/js/sgr.js`, `delegaciones_app/test_unit_interfaz.py`. **Creado:** `templates/includes/_motivo_delegacion.html`.
3. **Pruebas:** 709 en total, 709 aprobadas, 0 fallidas (línea base 703). Seis pruebas nuevas: el censo con su fuente; sin «Principio de acceso» ni insignias; sin sesión ningún enlace al seguimiento; el Profesional de Centro ve solo Centro y el Coordinador las seis; `id` de cada tarjeta, esquema accesible y un solo `h1`; y el filtro `partes_cifra`. No ajustamos ninguna prueba existente.
4. **Qué mirar:** «Territorio» sin sesión, con `funcionario.centro` (solo Centro tiene «Ver seguimiento») y con `coordinador.demo` (las seis lo tienen). Pasar el mouse por los nodos del esquema y hacer clic en uno.
5. **Comprobado con capturas:** a 1280 px sin sesión y como Profesional, y a 375 px. En 375 px la etiqueta del mar quedaba tapada por «Avenida del Mar»; la subimos a la parte norte del mar.
6. **Límites:** en `views.py` cambiamos solo lo que permite la regla 8. Las cifras para el conteo salen del filtro y no se escriben dos veces en la plantilla; la cantidad de delegaciones es el largo de la lista de la vista.
7. **No verificado:** el movimiento en un navegador real (las capturas son imágenes fijas; en ellas las cifras y la barra aparecen a mitad de la animación).
8. **Commits:** `fix: población urbana y rural según el Censo 2024 del INE, con su fuente`; `feat: Territorio con esquema interactivo, cifras animadas y delegaciones enlazadas`; `test: pruebas de Territorio (censo, enlaces por perfil, ids y esquema)`; `docs: avance de la fase 1 de la segunda ronda`.

## Ronda 2, fase 2. Portada y pie (21-11-2026)

1. **Qué hicimos**
   - Tarjetas de delegaciones de la portada: cada una lleva a su tarjeta en Territorio (`/territorio/#delegacion-…`). Con sesión, la tarjeta de la propia delegación (o todas, para la coordinación) agrega el enlace «Seguimiento territorial» a `delegacion_detalle`, con la misma condición del menú. Antes las seis enlazaban siempre al seguimiento: sin sesión llevaban al ingreso y, para un Profesional o Delegado, las otras cinco respondían 404 y quedaban en la auditoría como acceso denegado.
   - Cifras: sin sesión, la portada ya no muestra cifras internas (tareas en el tubo de trabajo, tareas que requieren atención y cumplimiento promedio). En su lugar muestra 250.141 habitantes, la cantidad de delegaciones municipales activas y 12,0 % de población rural, con «Fuente: Censo de Población y Vivienda 2024, INE». Con sesión se ven las cifras internas como antes. En ambos casos hay 3 cifras con `data-contar`, así que la prueba existente no cambió.
   - Menos repetición:
     - sin sesión, los accesos rápidos son «Cómo funciona», «Delegaciones» y «Preguntas frecuentes» («Ingresar» y «Territorio» ya están en el hero y en el menú);
     - con sesión quitamos el acceso «Ver resultados», que repetía el botón «Ver medición» del hero (los dos van a la misma pantalla);
     - quitamos el botón «Ver contexto» de la sección de delegaciones, porque ahora cada tarjeta lleva a Territorio;
     - en el pie, «Territorio» aparece una sola vez: sin sesión en «Secciones» y con sesión en «Ayuda».
2. **Archivos cambiados:** `templates/delegaciones_app/index.html`, `templates/base.html` (solo el pie), `static/css/sgr.css` (tarjeta de delegación con dos enlaces: la tarjeta entera lleva a Territorio y el seguimiento va encima), `delegaciones_app/test_unit_interfaz.py`.
3. **Pruebas:** 714 en total, 714 aprobadas, 0 fallidas (línea base 703). Cinco pruebas nuevas: sin sesión no hay cifras internas y sí la fuente; las cifras públicas de la portada son las mismas que entrega la vista de Territorio (así no se desalinean si cambian); ninguna tarjeta enlaza al seguimiento de una delegación ajena; los accesos rápidos sin sesión no repiten el hero; en el pie cada destino aparece una sola vez. No ajustamos ninguna prueba existente.
4. **Qué mirar:** la portada sin sesión (cifras públicas y fuente), con `funcionario.centro` (solo Centro tiene «Seguimiento territorial») y con `coordinador.demo` (las seis lo tienen). Hacer clic en una tarjeta: abre Territorio con esa delegación marcada.
5. **Límites:** la vista `index` no cambió. La población y la ruralidad de la portada quedan escritas una vez en la plantilla, porque la regla 8 solo permite cambiar la vista `institucional`; una prueba compara esos valores con los de Territorio.
6. **Revisión general (punto 5.4), para que el grupo decida; no quitamos nada de esta lista:**

   | Pantalla y archivo | Texto | Propuesta |
   | --- | --- | --- |
   | Panel del Coordinador (`panel_coordinador.html`) | Títulos «Mantenedores autorizados» y «Transacciones autorizadas» | Dejar «Mantenedores» y «Transacciones» |
   | Auditoría (`crud/auditoria.html`) | «Los registros son de solo lectura: no se pueden modificar ni eliminar.» | Dejar solo «Historial de operaciones críticas.» |
   | Alertas del panel (`_panel_alertas.html`) | «Revisa estas situaciones para saber qué requiere atención en tu ámbito.» (segunda línea bajo «Alertas en tu ámbito») | Quitar la frase; el título ya explica el filtro |
   | Ficha personal (`ficha.html`) | «Un coordinador puede asignarlas desde Administración.» | Se puede dejar: dice a quién pedir las metas |
   | Panel del Profesional (`panel_funcionario.html`) | «Actividades en tu ámbito» y «en tu ámbito» | Se quedan: explican el filtro, como «dentro de tu ámbito» de alertas |
   | Territorio con sesión | «Ir a mi panel» en el hero y en la banda de cierre (además de «Mi panel» en el menú) | Lo pide el encargo; se puede dejar solo en la banda |

   Las introducciones largas que quedan explican un cálculo o una regla (semáforo, medición, editar actividad) y ocupan una o dos líneas; no encontramos botones repetidos en una misma pantalla fuera de los ya corregidos.
7. **No verificado:** nada pendiente de esta fase; la revisamos con capturas a 1280 px con y sin sesión.
8. **Commits:** `feat: portada con cifras públicas sin sesión y delegaciones enlazadas a Territorio`; `fix: el pie muestra Territorio una sola vez`; `test: pruebas de la portada sin cifras internas y del pie sin enlaces repetidos`; `docs: avance de la fase 2 de la segunda ronda`.

## Ronda 2, fase 3. Modo claro y oscuro (21-11-2026)

1. **Qué hicimos**
   - Tres opciones de tema: «Claro», «Oscuro» y «Automático» (sigue al computador o al teléfono). Por defecto, «Automático».
   - El selector está en dos lugares: un botón «Tema» junto a «Accesibilidad» en la barra superior (ícono de sol, luna o automático; abre un menú con las tres opciones) y un grupo de tres botones dentro del panel de accesibilidad. Los botones llevan `aria-pressed`; el botón de la barra se llama «Tema: claro», «Tema: oscuro» o «Tema: automático», y el menú y el grupo se llaman «Tema».
   - La elección se guarda en `localStorage` (clave `sgr-tema`) dentro de `try/catch`; si el navegador no deja guardar, el tema funciona igual mientras la página siga abierta.
   - En «Automático», si el sistema cambia de claro a oscuro con la página abierta, la página cambia sola (`matchMedia` con su evento `change`).
   - El alto contraste manda: con «Alto contraste» activo la página queda en claro con alto contraste, aunque el tema elegido sea «Oscuro».
   - Sin parpadeo: el archivo nuevo `static/js/tema.js` se carga en el `<head>`, sin `defer` y antes del CSS. Pone `data-bs-theme` en `<html>` y aplica las preferencias de accesibilidad guardadas antes de que se dibuje la página. La etiqueta `<html lang="es" class="a11y-font-0">` no cambió: el atributo lo pone JavaScript. Agregamos `<meta name="color-scheme" content="light dark">`.
   - `sgr.css`: pasamos los colores escritos a mano a variables (`--acento`, `--texto-2`, `--fondo-campo`, `--thead-fondo`, `--pie-fondo`, `--mar`, etc.) y definimos los valores oscuros en un solo bloque `[data-bs-theme="dark"]`, sin duplicar reglas. Fuera de los bloques de variables solo quedan transparencias blancas sobre superficies que no cambian de color (el terracota de la banda y del hero de las pantallas internas) y los brillos decorativos del ingreso.
   - La variable interna de las tarjetas `.metric` se llamaba `--acento`; pasó a `--metrica-acento` para no chocar con la nueva variable global.
   - Paleta oscura (contrastes WCAG 2.1, todos de 4,5:1 o más para texto): fondo `#161311`, tarjetas `#201c19`, texto `#f3ece6` (14,46:1), texto secundario `#b9ada3` (7,71:1), acento `#ee8a72` (6,86:1), acento fuerte `#f6b3a2` (9,58:1), verde `#6fd39a` sobre `#16301f` (7,76:1), ámbar `#f2b860` sobre `#33270f` (8,21:1), rojo `#ff8fa3` sobre `#3a1520` (7,42:1). El borde de los campos (`#8a7d73`) queda en 4,24:1 sobre las tarjetas. El botón principal sigue en `#a83224` con texto blanco (6,67:1).
   - En oscuro las sombras se reemplazan por bordes suaves; el pie queda más oscuro que el fondo (`#0e0c0b`) y conserva el borde terracota; el ícono de error de los campos cambia a rosado para que se vea.
   - Dos clases de Bootstrap que se perdían en oscuro (`text-dark` en las alertas del panel y en el panel del Administrador, y `text-danger` en Delegados) se corrigen desde el CSS, solo en oscuro.
   - Escudo y logos: el SGR no usa imágenes; la marca «SGR» es un cuadro terracota con texto blanco y se lee igual en ambos temas.
2. **Archivos cambiados:** `templates/base.html`, `static/css/sgr.css`, `static/js/sgr.js`, `static/icons/sgr-iconos.svg` (íconos `i-sol`, `i-luna`, `i-tema-auto`), `templates/delegaciones_app/institucional.html` (olas del esquema), `delegaciones_app/test_unit_interfaz.py`. **Creado:** `static/js/tema.js`.
3. **Pruebas:** 717 en total, 717 aprobadas, 0 fallidas (línea base 703). Tres pruebas nuevas: `tema.js` en el `<head>` sin `defer` y antes del CSS, con el `meta color-scheme`; el selector con sus tres opciones en la barra y en el panel, con nombre accesible; la etiqueta `<html>` intacta y ningún `<script>` en línea. No ajustamos ninguna prueba existente.
4. **Qué mirar:** con cualquier usuario, el botón «Tema» de la barra superior: elegir «Oscuro», recargar (se mantiene) y recorrer ingreso, panel, «Registrar actividad» con un error, tablas, menús desplegables, alertas, preguntas frecuentes, «Subir evidencia» y la barra de accesibilidad. Después activar «Alto contraste» con el tema en «Oscuro»: debe verse el alto contraste claro.
5. **Comprobado con capturas** en oscuro: portada sin sesión, panel del Profesional, semáforo, ingreso, «Registrar actividad» con el teléfono «abc» y Territorio. En claro, el panel del Profesional se ve igual que antes. Una captura sin forzar el tema salió en oscuro porque Windows está en modo oscuro: así comprobamos «Automático».
6. **Límites:** no tocamos vistas ni ajustes. El encargo dice que el hero terracota de la portada se mantiene en ambos temas, pero el hero de la portada es claro desde la primera ronda (fondo crema con la ilustración de órbitas). Por eso en oscuro pasa a fondo oscuro con un brillo cálido. Los bloques que sí son terracota (la banda de Territorio y el hero de las pantallas internas) se mantienen igual en ambos temas.
7. **No verificado:** los clics reales en el selector, el cambio del sistema con la página abierta y la combinación de alto contraste con oscuro (las capturas son imágenes fijas sin interacción); quedan cubiertos por el código de `tema.js` y `sgr.js`.
8. **Commits:** `feat: modo claro, oscuro y automático con colores en variables y selector de tema`; `fix: olas del esquema de Territorio sin tapar la etiqueta del mar`; `test: pruebas del tema (carga en el head, selector accesible y etiqueta html intacta)`; `docs: avance de la fase 3 de la segunda ronda`.

## Ronda 2, fase 4. Verificación y documentación (21-11-2026)

1. **Qué hicimos**
   - `check` sin problemas; `makemigrations --check --dry-run`: «No changes detected»; 717 pruebas aprobadas.
   - `probe.py` con la base local de demostración: 200 de 200 combinaciones iguales a la línea base (50 pantallas con 4 perfiles; el encargo menciona 164, de una versión anterior del script).
   - Recorrimos los textos de los 3 flujos de `docs/DEMO_EXPOSICION.md`: los 28 que revisa nuestro script siguen en su lugar. Para el flujo 1 completo (registrar, subir evidencia, revisar) respaldamos la base local, hicimos el flujo, revisamos y sacamos capturas, y después restauramos el respaldo y borramos el archivo subido. El HTML es el mismo en claro y en oscuro; el aspecto en oscuro lo revisamos con capturas de ingreso, panel, «Registrar actividad» con error, «Subir evidencia», la revisión del Delegado, semáforo, portada y Territorio.
   - Guardamos 10 capturas nuevas en `docs/interfaz/capturas/` (17 a 26): Territorio en escritorio, a 375 px y en oscuro; portada sin sesión en claro y en oscuro; panel del Profesional, ingreso, «Registrar actividad» con el teléfono «abc», semáforo y revisión del Delegado en oscuro.
   - Actualizamos `GUIA_DE_ESTILO.md` (sección 10: tema claro y oscuro con la paleta y sus contrastes; sección 11: Territorio y su esquema; tres decisiones nuevas) y `CAMBIOS_INTERFAZ.md` (sección 6: qué cambió, la corrección del censo con su fuente, los enlaces de delegaciones, RNF-011 a RNF-013 y la verificación; «Para desplegar» con `tema.js`).
2. **Archivos:** `docs/interfaz/GUIA_DE_ESTILO.md`, `docs/interfaz/CAMBIOS_INTERFAZ.md`, `docs/interfaz/capturas/` (10 PNG nuevos) y este archivo.
3. **Pruebas:** 717 en total, 717 aprobadas, 0 fallidas (línea base 703). No ajustamos ninguna prueba existente.
4. **Qué mirar:** las capturas 17 a 26 y, en local, el botón «Tema» en cada pantalla.
5. **Para desplegar:** después del `git pull`, correr `python manage.py collectstatic --noinput` y reiniciar Gunicorn (hay un estático nuevo, `tema.js`). No lo ejecutamos.
6. **No verificado:** el movimiento y los clics del selector de tema en un navegador real; el modo de movimiento reducido del sistema operativo; la combinación de alto contraste con el tema oscuro (cubierta por el código, sin captura).
7. **Commits:** `docs: guía de estilo con el tema oscuro y el esquema del territorio`; `docs: cambios de la segunda ronda con capturas, censo corregido y pasos para desplegar`; `docs: avance de la fase 4 de la segunda ronda`.
