# Guía de estilo de la interfaz del SGR

Como grupo definimos esta guía para que cada pantalla nueva del Sistema de Gestión de Resultados se vea y se comporte igual que las demás. Todo vive en `static/css/sgr.css` (sobre Bootstrap 5.3.3 guardado en `static/bootstrap/`), `static/js/tema.js`, `static/js/sgr.js` y las parciales de `templates/includes/`. La tabla de colores de la sección 2 es la del tema claro; la del tema oscuro está en la sección 10.

## 1. Principios

1. **Cada perfil ve lo que puede hacer.** No mostramos tarjetas bloqueadas ni listas de lo que no está permitido. Ocultar es solo presentación: la protección real sigue en las vistas.
2. **Una idea por bloque y un botón principal por bloque.**
3. **El color nunca va solo.** Todo estado lleva texto y, cuando corresponde, un ícono.
4. **Nada se carga desde internet.** Fuentes, íconos y scripts están en `static/`; así ninguna IP de un funcionario llega a terceros.
5. **El movimiento acompaña y se puede apagar.** Sin JavaScript o con movimiento reducido, la página se ve completa.

## 2. Colores

Contrastes calculados con la fórmula de WCAG 2.1 (luminancia relativa). Si se cambia un valor, se recalcula y se anota aquí.

| Variable | Valor | Uso | Contraste |
| --- | --- | --- | --- |
| `--terracotta` | `#a83224` | Botón principal, enlaces, acentos | 6,67:1 sobre blanco; 6,30:1 sobre `--paper` |
| `--terracotta-dark` | `#762018` | Hover del botón principal, títulos destacados | 10,55:1 sobre blanco |
| `--terracotta-soft` | `#f6e6e1` | Fondo de insignias y de íconos | `--terracotta-dark` encima: 8,71:1 |
| `--clay` | `#c35b3e` | Solo fondos, bordes e ilustraciones | 4,30:1: **no sirve para texto** |
| `--ochre` | `#c48a2a` | Foco del teclado y detalles | Solo decoración |
| `--ink` | `#2f2925` | Texto principal | 13,54:1 sobre `--paper`; 14,34:1 sobre blanco |
| `--muted` | `#766961` | Texto secundario y texto de ejemplo de los campos | 5,30:1 sobre blanco; 5,00:1 sobre `--paper`; 4,60:1 sobre `--paper-2` |
| `--paper` | `#fbf8f4` | Fondo general | |
| `--paper-2` | `#f4eee6` | Secciones alternas | |
| `--panel` | `#ffffff` | Tarjetas y paneles | |
| `--line` | `#e8ddd2` | Bordes suaves de tarjetas | Decorativo |
| `--line-strong` | `#8f7f73` | Borde de campos y botones claros | 3,85:1 sobre blanco (componentes: mínimo 3:1) |
| `--charcoal` | `#302c2a` | Pie y franja superior | Blanco encima: 13,82:1; `#e8ddd2`: 10,34:1; `#d9c8b8`: 8,49:1 |

La paleta azul y roja del Kit de Gobierno Digital no se usa: la marca del SGR es terracota, por los techos de teja de La Serena.

## 3. Semáforo y estados

| Estado | Clase que entrega la vista | Texto | Fondo suave | Ícono | Contraste |
| --- | --- | --- | --- | --- | --- |
| Verde | `success` | `#1d7a46` | `#e7f4ec` | Círculo con visto (`i-visto`) | 5,35:1 sobre blanco; 4,73:1 sobre su fondo |
| Ámbar | `warning` | `#7a4800` sobre su fondo (`#9a5b00` en barras) | `#fff3dc` | Triángulo con exclamación (`i-advertencia`) | 6,94:1 sobre su fondo; barra con texto blanco 5,43:1 |
| Rojo | `danger` | `#9b1035` sobre su fondo (`#b0123b` en barras y bordes) | `#fde8ec` | Círculo con X (`i-equis`) | 7,12:1 sobre su fondo; 7,01:1 sobre blanco |
| Sin cálculo | `secondary` | `#4a4f57` | `#eef0f3` | Círculo con guion (`i-neutro`) | 7,22:1 |
| En proceso | `primary` | `#3d4f7a` | `#e9eef8` | Reloj (`i-reloj`) | 6,95:1 |

- El rojo del semáforo es carmesí (tono frío) para no confundirse con el terracota (tono anaranjado).
- `delegaciones_app/medicion.py` sigue entregando `success`, `warning` y `danger`; el cambio de color está solo en CSS y en las plantillas.
- Se dibuja con `{% include 'includes/_semaforo_insignia.html' with estado=fila.estado estado_class=fila.estado_class %}`. Acepta `sufijo` (por ejemplo `' %'`).
- Barras de avance: `progress-bar barra-{{ estado_class }}`. Filas resaltadas: `fila-{{ estado_class }}`. Tarjetas con borde superior: `borde-{{ estado_class }}`. Recuadro del semáforo: `semaforo-caja semaforo-caja-{{ estado_class }}`.

## 4. Tipografía

- **Roboto** (400, 500 y 700) para el texto y **Roboto Slab** (600 y 700) para los títulos, como indica el Kit de Gobierno Digital. Archivos `woff2` del subconjunto latino en `static/fonts/`, con `font-display: swap` y su licencia (Apache 2.0, ver `static/fonts/LEEME.md`).
- Si las fuentes no cargan, el sistema usa `"Segoe UI", "Helvetica Neue", Arial, sans-serif` para el texto y `Georgia` para los títulos.
- Tamaños en `rem`, para que la barra de accesibilidad los escale: cuerpo 1 rem con línea 1,55; títulos de pantalla 1,875 rem (1,5 en el celular); título de la portada `clamp(2.5rem, 5vw, 3.5rem)`.
- Kicker (`.page-kicker`): mayúsculas pequeñas, terracota, con espaciado de letras.

## 5. Forma, sombra y espacio

- Esquinas: 12 px en tarjetas y paneles (`--radio-tarjeta`), 8 px en botones y campos (`--radio-control`), 16 px en la tarjeta del ingreso, insignias en píldora.
- **Decisión:** reemplazamos la regla anterior de «bordes rectos» de 2 px. Las esquinas suaves hacen la interfaz más amable y separan mejor los bloques; los botones siguen siendo rectangulares (el redondeado completo queda solo para insignias y el botón «Accesibilidad»).
- Sombras cálidas en capas: `--sombra` (`0 1px 2px` y `0 8px 24px`, carbón al 6 %) y `--sombra-alta` para el hover.
- Espaciado en una escala de 4 px: `--e1` 4, `--e2` 8, `--e3` 12, `--e4` 16, `--e6` 24, `--e8` 32, `--e12` 48 y `--e16` 64. Secciones de la portada separadas por 72 px.
- Ancho máximo: 1560 px en pantallas de trabajo; 1200 px en la portada.
- Puntos de quiebre: los de Bootstrap (576, 768, 992 y 1200 px), los mismos del kit.

## 6. Componentes

| Componente | Clase o parcial | Notas |
| --- | --- | --- |
| Encabezado de página | `.page-header` o `includes/_encabezado_pagina.html` | Kicker, un solo `h1.page-title`, una línea de introducción y acciones a la derecha |
| Botón principal | `.btn-sgr` | Uno por bloque; hover `--terracotta-dark`; al presionar `scale(.98)` |
| Botón secundario | `.btn-outline-sgr`, `.btn-light` | `.btn-light` para «Cancelar» |
| Campo | `includes/_campo.html` | Etiqueta arriba, `*` de obligatorio, ayuda con `id="<id>_helptext"`, error con `id="<id>_error"`, `is-invalid` |
| Formulario completo | `includes/_formulario.html` | Errores generales y «Revisa los campos marcados.» arriba; `novalidate` en el `<form>` |
| Formulario agrupado a mano | `form|campos:"a b"` y `form|campos_restantes:"…"` | `campos_restantes` asegura que ningún campo quede fuera |
| Mosaico de acceso rápido | `.mosaico`, `.mosaico-principal`, dentro de `.mosaicos` | Ícono, texto de acción y flecha; el principal en terracota |
| Lista de enlaces | `.lista-enlaces` | Enlaces con flecha y separadores |
| Métrica | `.metric` (`.coral`, `.amber`, `.navy`) | Acento a la izquierda con `box-shadow` interior |
| Tabla larga | `.table-responsive.tabla-fija` | Encabezado fijo dentro de la tabla |
| Filtros | `.filtros` o `.filtros-caja` | Tarjeta clara; los nombres de los parámetros no cambian |
| Estado vacío | `includes/_estado_vacio.html` | Ícono, título y texto opcional |
| Íconos | `includes/_icono.html` con `nombre` | Sprite propio `static/icons/sgr-iconos.svg`, siempre `aria-hidden="true"` |

## 7. Movimiento

- Duraciones: 200 ms en botones, campos y menús; 500 ms en apariciones; 700 ms en barras; 900 ms en cifras; bucles decorativos de 40 a 60 s y flotación de 5,5 a 7 s.
- Curva `cubic-bezier(.2, .8, .2, 1)`. Solo se animan `transform` y `opacity`.
- Aparición al bajar: `sgr.js` agrega `.reveal-pendiente` solo a los elementos `.reveal` que todavía no están a la vista, con 70 ms de desfase entre hermanos. Sin JavaScript nada queda oculto.
- Encabezado: al bajar más de 8 px gana sombra y se compacta.
- Cifras de la portada: el valor final está en el HTML y en un texto oculto para lectores de pantalla; si el navegador pausa la animación, a los 1,2 s queda el valor final.
- **Todo se apaga con `@media (prefers-reduced-motion: reduce)`**, y `sgr.js` no inicia apariciones, conteos ni barras en ese caso.
- En formularios y tablas de trabajo solo hay movimiento de foco y hover.

## 8. Accesibilidad

- Enlace «Ir al contenido principal», foco visible ocre de 3 px y orden `header`, `main`, `footer` con los scripts al final.
- Barra de accesibilidad (botón «Accesibilidad» arriba a la derecha y en el pie): «Aumentar texto», «Achicar texto», «Alto contraste», «Links subrayados» y «Reiniciar». Usa las clases del kit en `<html>`: `a11y-font-0` (16 px), `a11y-font-1` (20 px), `a11y-font-2` (24 px) y `a11y-contrast`, más la propia `a11y-subrayar`. Los botones de alternar llevan `aria-pressed`; la preferencia se guarda en `localStorage` dentro de `try/catch`.
- Alto contraste: fondo blanco, texto negro (21:1), secundario `#2b2b2b` (14,16:1), terracota `#6e1a12` (11,54:1), estados `#0f5a31` (7,34:1), `#6b3f00` (8,18:1) y `#8a0c2e` (8,25:1) sobre sus fondos, bordes negros de 2 px y enlaces subrayados.
- Con el texto aumentado, el menú baja a una segunda fila en vez de apretarse.
- Errores de formulario: `is-invalid`, `aria-invalid="true"` y `aria-describedby` (Django 5.2 agrega estos dos últimos); el foco va al primer campo con error.
- Áreas de toque de 44 px en el menú del celular, botones y casillas.
- Cada campo tiene etiqueta visible o `aria-label`; cada pantalla tiene un solo `h1`.

## 9. Decisiones y su porqué

| Decisión | Por qué |
| --- | --- |
| No instalar el Kit de Gobierno Digital | Usa Bootstrap 4, jQuery y Popper; el SGR usa Bootstrap 5.3.3 sin jQuery. Tomamos sus criterios (tipografía, clases de accesibilidad, orden del pie). |
| Fuentes e íconos propios en `static/` | Cargar Google Fonts o un CDN envía la IP de cada funcionario a un tercero; el proyecto declara cumplir la normativa de datos personales. |
| Carmesí para el rojo del semáforo | El terracota es la marca; un rojo anaranjado confundiría «marca» con «alerta». |
| Esquinas de 12 y 8 px en vez de 2 px | Más amable y moderno, y separa mejor los bloques. |
| Ocultar en vez de deshabilitar | Cada usuario ya sabe lo que puede hacer; las tarjetas grises solo agregaban ruido. La protección sigue en el servidor. |
| Respuestas de la portada abiertas sin JavaScript | La portada debe verse completa aunque el script no cargue. |
| Filtro `campo_sgr` en `templatetags` | Es la única forma de agregar `is-invalid` al widget sin tocar `forms.py`; no tiene lógica de negocio y tiene pruebas propias. |
| Tema con `data-bs-theme` puesto por JavaScript | Bootstrap 5.3 ya cambia sus componentes con ese atributo. Lo pone `tema.js` en el `<head>` para que no parpadee, y el servidor no escribe atributos nuevos en `<html>` (una prueba busca la etiqueta exacta). |
| Variables en vez de reglas duplicadas para el oscuro | Un solo bloque `[data-bs-theme="dark"]` cambia los valores; las reglas son las mismas en ambos temas, así que un componente nuevo funciona en oscuro si usa las variables. |
| Esquema propio del territorio en vez de un mapa | Un mapa externo (Google Maps, OpenStreetMap) envía la IP del funcionario a un tercero y agrega dependencias. El esquema es referencial y lo dice. |

## 10. Tema claro y oscuro

- Opciones: «Claro», «Oscuro» y «Automático» (por defecto; sigue a `prefers-color-scheme`). Se eligen en el botón «Tema» de la franja superior o en el grupo «Tema» del panel de accesibilidad. La elección se guarda en `localStorage` con la clave `sgr-tema` dentro de `try/catch`.
- `static/js/tema.js` se carga en el `<head>`, sin `defer` y antes del CSS: aplica el tema y las preferencias de accesibilidad guardadas antes de dibujar la página. Expone `window.sgrTema` (`leer`, `guardar`, `aplicar`, `sistema`), que usa `sgr.js` para los botones y para el evento `change` del sistema.
- El alto contraste manda: con `a11y-contrast` activo, el tema efectivo es claro.
- **Regla para componentes nuevos:** usar las variables, nunca colores escritos a mano. Para texto o trazos terracota se usa `--acento` (o `--acento-fuerte` para hover y texto destacado); `--terracotta` queda para fondos con texto blanco (botón principal, mosaico principal, selección), que no cambian en oscuro.
- En oscuro, `--sombra` no dibuja nada y `--sombra-alta` es un borde de 1 px: las tarjetas se separan por sus bordes.

| Variable | Claro | Oscuro | Contraste en oscuro |
| --- | --- | --- | --- |
| `--paper` (fondo) | `#fbf8f4` | `#161311` | |
| `--panel` (tarjetas) | `#ffffff` | `#201c19` | |
| `--paper-2` (secciones alternas) | `#f4eee6` | `#2a2522` | |
| `--line` (bordes suaves) | `#e8ddd2` | `#3b342f` | Decorativo |
| `--line-strong` (borde de campos) | `#8f7f73` | `#8a7d73` | 4,24:1 sobre tarjeta; 4,63:1 sobre el campo |
| `--ink` (texto) | `#2f2925` | `#f3ece6` | 14,46:1 sobre tarjeta; 15,81:1 sobre fondo |
| `--muted` (texto secundario) | `#766961` | `#b9ada3` | 7,71:1 sobre tarjeta; 6,90:1 sobre `--paper-2` |
| `--texto-2` (texto de apoyo) | `#5c524b` | `#d6cbc2` | 10,62:1 sobre tarjeta |
| `--acento` (enlaces y texto terracota) | `#a83224` | `#ee8a72` | 6,86:1 sobre tarjeta; 7,50:1 sobre fondo; 6,14:1 sobre `--paper-2` |
| `--acento-fuerte` (hover y texto destacado) | `#762018` | `#f6b3a2` | 9,58:1 sobre tarjeta; 8,18:1 sobre `--terracotta-soft` |
| `--terracotta-soft` | `#f6e6e1` | `#3a2420` | |
| Botón principal (`--terracotta`) | `#a83224` | `#a83224` | Texto blanco 6,67:1 |
| Verde (texto sobre su fondo) | `#1d7a46` sobre `#e7f4ec` | `#6fd39a` sobre `#16301f` | 7,76:1 |
| Ámbar (texto sobre su fondo) | `#7a4800` sobre `#fff3dc` | `#f2b860` sobre `#33270f` | 8,21:1 |
| Rojo (texto sobre su fondo) | `#9b1035` sobre `#fde8ec` | `#ff8fa3` sobre `#3a1520` | 7,42:1 |
| Rojo de bordes y error de campo (`--rojo-borde`) | `#b0123b` | `#ff8fa3` | 8,55:1 sobre el campo |
| Sin cálculo | `#4a4f57` sobre `#eef0f3` | `#c6cbd3` sobre `#262a30` | 8,85:1 |
| En proceso | `#3d4f7a` sobre `#e9eef8` | `#a9bdf0` sobre `#1c2333` | 8,39:1 |
| Pie y franja superior | `#302c2a` | `#0e0c0b` | `#e8ddd2` encima: 14,59:1 |
| Foco del teclado (`--ochre`) | `#c48a2a` | `#c48a2a` | 5,65:1 sobre tarjeta |

- El hero terracota de las pantallas internas (`.hero-sgr`) y la banda de cierre de Territorio no cambian: texto blanco sobre el degradado terracota en ambos temas. El hero de la portada y de Territorio es claro en el tema claro y pasa a fondo oscuro con un brillo cálido en el oscuro.
- El ícono de error dentro de los campos cambia a `#ff8fa3` en oscuro. Las clases de Bootstrap `text-dark` y `text-danger` se corrigen solo en oscuro.

## 11. Territorio y su esquema

- El esquema de `institucional.html` es un SVG propio: mar al oeste con olas que se mueven muy lento (14 s), zona urbana punteada, zona rural difusa al oriente, líneas desde Centro y la flecha del norte. Debajo dice «Esquema referencial, no a escala».
- Los nodos son enlaces HTML encima del dibujo (`.esquema-nodo.nodo-<slug>`, posición en porcentaje en el CSS). Cada uno lleva a `#delegacion-<slug>` y funciona sin JavaScript. Laten de 1 a 1,08 cada 3 a 4 s, desfasados. Si se agrega una delegación nueva, hay que darle su posición en el CSS.
- El dibujo tiene `role="img"` y un `aria-label` que nombra las delegaciones; el nombre de cada nodo es su texto visible.
- `data-delegacion="<slug>"` une el nodo, el botón de la fila y la tarjeta: `sgr.js` resalta los tres al pasar el mouse o enfocar y, al hacer clic, baja a la tarjeta y la marca (`.is-seleccionada`, `aria-current` en el nodo y el botón). Sin JavaScript, `:target` marca la tarjeta.
- Cifras: `{% with c=valor|partes_cifra %}` separa «88,0 %» en `c.plano` («88.0», para `data-contar`), `c.decimales`, `c.texto` y `c.sufijo`. Cada cifra pública lleva su fuente visible («Fuente: Censo de Población y Vivienda 2024, INE»).
- Motivo de cada delegación: `includes/_motivo_delegacion.html` con `slug`; dibujos de trazo con el mismo estilo que los pasos de la portada (`.delegacion-motivo`).
