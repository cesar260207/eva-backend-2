# Referencias visuales de la interfaz

Como grupo tomamos tres sitios como inspiración para el rediseño del SGR. De ellos tomamos ideas de orden, movimiento y accesibilidad; no copiamos colores, logos, textos, ilustraciones ni código.

## Cómo se revisaron

La sesión de trabajo que hizo el rediseño no tenía un navegador disponible, así que no pudo ver las páginas ni su movimiento. Lo que sigue se basa en la lectura del texto de cada sitio que hizo quien preparó el encargo. **Queda pendiente** que una persona del grupo abra cada página, observe el movimiento, el ingreso y el pie, y complete la columna «Observado en el navegador».

## 1. Spaceship (https://www.spaceship.com/)

| Elemento | Lo que se sabe por el texto | Lo que tomamos para el SGR | Observado en el navegador |
| --- | --- | --- | --- |
| Hero | Frase corta y un único llamado a la acción | Hero con el título actual del SGR y un botón principal destacado | Pendiente |
| Bloques de funciones | Título, explicación breve e ilustración animada de formas geométricas que orbitan o flotan | Ilustración propia de órbitas: el SGR al centro y seis puntos, uno por delegación | Pendiente |
| «Core products» | Tres tarjetas, cada una con su motivo geométrico y un solo enlace | Las cinco tarjetas de «Cómo funciona», cada una con un motivo geométrico propio | Pendiente |
| «Key features» | Grilla de funciones | Grilla de accesos rápidos y de delegaciones | Pendiente |
| Preguntas frecuentes | Al final de la portada | Acordeón con preguntas cuyas respuestas salen del código | Pendiente |
| Ingreso (https://www.spaceship.com/auth/) | No se pudo abrir | Página despejada, tarjeta centrada, campos grandes y botón a todo el ancho | Pendiente |

## 2. Municipalidad de Las Condes (https://www.lascondes.cl/)

| Elemento | Lo que se sabe por el texto | Lo que tomamos para el SGR | Observado en el navegador |
| --- | --- | --- | --- |
| Menú | Ordenado por necesidad, con submenús en bloques de 3 o 4 enlaces | Conservamos el menú actual del SGR (las pruebas y la demo dependen de él) y marcamos la sección activa | Pendiente |
| Accesos rápidos | Fila sin título, con textos cortos de acción | Mosaicos con ícono y texto de acción en la portada y en los paneles | Pendiente |
| Barra de accesibilidad | «Aumentar texto», «Achicar texto», «Alto contraste», «Links subrayados», «Reiniciar», entre otras | Barra con «Aumentar texto», «Achicar texto», «Alto contraste», «Links subrayados» y «Reiniciar» | Pendiente |
| Pie | Logo, «Contacto», «Síguenos» y enlaces de apoyo | Pie en bloques: marca, «Secciones» y «Ayuda»; sin contacto ni redes porque el SGR no tiene datos propios que mostrar | Pendiente |

## 3. Kit de Gobierno Digital (https://framework.digital.gob.cl/)

No lo instalamos: usa Bootstrap 4, jQuery y Popper, y el SGR usa Bootstrap 5.3.3 sin jQuery. Tomamos sus criterios:

- Roboto para el texto y Roboto Slab para los títulos, guardadas en `static/fonts/`.
- Orden `header`, `main`, `footer` y los scripts al final del `body`.
- Los mismos puntos de quiebre de Bootstrap (576, 768, 992 y 1200 px).
- Las clases de accesibilidad `a11y-font-0`, `a11y-font-1`, `a11y-font-2` y `a11y-contrast` en la etiqueta `html`.
- Un `footer` con un `div.container`, la marca y bloques de enlaces agrupados.
- Un único estilo de botón principal; el botón redondeado solo como excepción.
- Su paleta azul y roja no se usa: la marca del SGR es terracota.
