# Cambios de la interfaz del SGR (rama `feat/interfaz-terracota`)

Como grupo rediseñamos la interfaz del Sistema de Gestión de Resultados para que sea más limpia, moderna y fácil de usar, sin cambiar lo que el sistema hace: no se tocaron vistas, modelos, migraciones, permisos, reglas, cálculos ni URL. Este documento resume qué se quitó, qué cambió en cada pantalla y cómo responde a los requerimientos no funcionales. Las capturas están en [capturas/](capturas/).

## 1. Qué quitamos y por qué

El grupo pidió que cada usuario vea lo que puede hacer, sin listas de lo que no puede hacer: ya lo sabe por su cargo, y las tarjetas grises solo agregaban ruido. Todo se ocultó en las plantillas con las variables que las vistas ya entregaban; la protección sigue en el servidor.

| Pantalla | Se quitó |
| --- | --- |
| «Administración» | Las tarjetas sin permiso y su botón «No disponible para tu perfil» (el Profesional veía 11 bloqueadas y 1 útil), los rótulos «Sección 01…12» y el párrafo largo |
| Encabezado de los 4 paneles | La descripción de permisos («Permisos mínimos…», «Permisos intermedios…», «Acceso total…»), la insignia oscura con el perfil y la línea «Roles: …» (el perfil ya aparece en el menú del usuario) |
| Panel del Profesional y del Delegado | El bloque «Restringido para tu perfil» |
| Panel del Coordinador | La nota de lo reservado al Administrador y los rótulos «crear · editar · eliminar» |
| Lista de cada mantenedor | La insignia «Solo lectura para tu perfil» |
| Ingreso | «Usa tu cuenta para acceder a las funciones autorizadas por tu perfil y delegación.» |
| Actividades, Delegados, Mantenedores, Perfiles | Introducciones largas o sobre permisos, reemplazadas por una línea |

## 2. Qué cambió en cada pantalla

| Pantalla | Cambio | Captura |
| --- | --- | --- |
| Todas | Paleta terracota con contrastes verificados, Roboto y Roboto Slab locales, esquinas suaves, sombras cálidas, encabezado claro con la sección activa marcada, franja superior con «Accesibilidad» y pie en bloques | |
| Portada | Hero con ilustración propia de órbitas (seis delegaciones en torno al SGR), accesos rápidos, cifras que cuentan, «Cómo funciona» en cinco tarjetas unidas por una línea, delegaciones y preguntas frecuentes | `01_portada.png`, `02_portada_375px.png` |
| Ingreso | Tarjeta centrada, campos grandes, mostrar u ocultar contraseña, aviso de credenciales arriba de los campos | `03_ingreso.png`, `04_ingreso_credenciales_incorrectas.png` |
| Paneles | Mosaicos de acceso rápido con el acceso principal en terracota; semáforo con ícono | `05` a `08`, `14_panel_profesional_375px.png` |
| Administración | Solo las secciones que el perfil usa | `09_administracion_profesional.png` |
| Registrar actividad | Cuatro bloques («Dónde y cuándo», «Qué se hizo», «Contacto», «Vinculación»), nota sobre el puntaje en «Contacto», error junto al campo y resumen arriba | `10_registrar_actividad_telefono_abc.png` |
| Subir evidencia | Zona punteada con formatos y tamaño máximo, nombre del archivo elegido | `11_subir_evidencia.png` |
| Detalle de actividad (revisión) | Mismo contenido con el nuevo estilo; «Aprobar» y «Rechazar» en su lugar | `12_revision_delegado.png`, `15_revision_768px.png` |
| Semáforo | Encabezado uniforme (`h1`), insignias carmesí, ámbar y verde con ícono | `13_semaforo.png` |
| Medición, resumen, ficha, alertas, tubo de trabajo, delegados | Insignias del semáforo, barras del color del estado, filas resaltadas sin colores de Bootstrap | |
| Actividades, tubo de trabajo, mantenedores, auditoría | Encabezado de tabla fijo, filtros en tarjeta, estado vacío con ícono | |
| Tarea del tubo, mantenedores, ajuste, ausencia, atención social, comentario | Formularios con el sistema de campos (error junto a cada campo) | |
| Alto contraste y texto grande | Barra de accesibilidad con las clases del Kit de Gobierno Digital | `16_alto_contraste_125.png` |

Las capturas son de Chrome sin ventana sobre la base local de demostración (`seed_demo`, datos ficticios). La 04 y la 10 se generaron desde un archivo local, por eso no muestran los íconos del sprite (el navegador bloquea ese recurso desde `file://`); en el servidor sí se ven. En la 01 las cifras aparecen a mitad del conteo animado.

**Capturas «antes»:** quedan pendientes. Como `main` no cambia hasta unir la rama, se pueden sacar desde `main` con la lista de `LINEA_BASE.md`.

## 3. Requerimientos no funcionales

Los nombres vienen del encargo del rediseño; el texto completo de RNF-011 a RNF-013 está en el informe de diseño (etapa 2), que no forma parte del repositorio.

| Requerimiento | Cómo responde la interfaz | Evidencia |
| --- | --- | --- |
| **RNF-011 Usabilidad** | Cada perfil ve solo lo que usa; accesos rápidos con textos de acción; el acceso principal de cada perfil destacado; formularios agrupados con el error junto al campo y el foco en el primer error; sección activa marcada en el menú; estados vacíos que dicen qué hacer | `LimpiezaDePanelesTests`, `IndiceDeMantenedoresTests`, `FormularioDeActividadTests`, `EncabezadoPieYAccesibilidadTests` en `delegaciones_app/test_unit_interfaz.py` |
| **RNF-012 Accesibilidad** | Contraste de 4,5:1 o más en texto normal (también en alto contraste); color con ícono y texto en el semáforo; `is-invalid`, `aria-invalid` y `aria-describedby` en errores; barra con tamaño de texto, alto contraste y enlaces subrayados (clases `a11y-font-*` y `a11y-contrast` del kit); foco visible; un `h1` por pantalla; etiquetas en todos los campos; movimiento que se apaga con `prefers-reduced-motion`; la portada se ve completa sin JavaScript | `SemaforoTests`, `PortadaTests`, `FiltrosDeInterfazTests` y la tabla de contrastes de `GUIA_DE_ESTILO.md` |
| **RNF-013 Compatibilidad** | Bootstrap 5.3.3 local, sin jQuery ni librerías nuevas; JavaScript propio que revisa si cada función existe (`IntersectionObserver`, `localStorage` en `try/catch`); revisado a 375, 768 y 1280 px; ningún recurso desde internet | `RecursosLocalesTests`; capturas 02, 14 y 15 |

## 4. Verificación

- Pruebas: 681 en la línea base y todas siguen aprobadas; se agregaron 22 pruebas de interfaz (703 en total). La única prueba existente modificada es `test_indice_deshabilita_los_mantenedores_exclusivos_del_administrador`, con el mismo nombre.
- `python manage.py check`: sin problemas. `python manage.py makemigrations --check --dry-run`: «No changes detected».
- `probe.py` con la base de demostración: 200 de 200 combinaciones de perfil y pantalla iguales antes y después (el script actual recorre 50 pantallas con 4 perfiles; el encargo mencionaba 164 de una versión anterior del script).
- Textos de la demo (`docs/DEMO_EXPOSICION.md`): «Registrar actividad con evidencia», «Actividades», «+ Nueva actividad», «Guardar actividad», «Subir evidencia», «Rechazar», «Aprobar», «Anular aprobación», «Resultados», «Semáforo de avance», «Mi ficha», «Administración», «Consultar auditoría», «Informar felicitación o reclamo», «Ingresar al SGR», «Ingresar», «¿Olvidaste tu contraseña?», «Abrir sección», «Solo lectura» y «De la necesidad territorial al resultado verificable.» siguen en su lugar. Lo revisamos sobre la base local y recorrimos el flujo 1 completo en una copia que luego restauramos.

## 5. Para desplegar

Hay archivos estáticos nuevos (fuentes, íconos y JavaScript) y el CSS cambió. En el servidor, después de `git pull`, hay que correr:

```
python manage.py collectstatic --noinput
```

y luego seguir los pasos habituales del despliegue del grupo. Sin `collectstatic`, el servidor no encuentra `static/js/sgr.js`, `static/fonts/` ni `static/icons/` y la página se verá sin fuentes, sin íconos y sin la barra de accesibilidad. No hay migraciones ni dependencias nuevas. El parámetro `?v=interfaz-20261121` del CSS obliga a los navegadores a descargar la hoja nueva.
