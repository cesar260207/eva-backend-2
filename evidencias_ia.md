# Evidencias de uso de Inteligencia Artificial

## Prompt 1
**Pregunta:** "Necesito un proyecto Django con dos aplicaciones independientes, una para delegaciones y otra para gestión, usando Bootstrap local y JSON para alimentar las pantallas. Diseña la estructura y la lógica para leer solicitudes y metas desde archivos JSON."

**Respuesta de apoyo:** El asistente propuso una arquitectura con:
- proyecto principal `gestion_laserena`
- apps `delegaciones_app` y `gestion_app`
- archivo `base.html` con navbar y pie de página
- lectura de JSON desde una carpeta `data/`
- funciones de procesamiento para estados y semáforos
- plantillas heredadas de Bootstrap

**Implementación realizada:** Se aplicó esa estructura en el proyecto, con vistas, rutas y plantillas compartidas para la administración territorial.



## Prompt 2

Utilizamos La IA del Visual Studio Code para la implementacion de algunos logos e imagenes que estan distribuidos por el proyecto debido a algunos problemas de integracion y de deformaciones que les ocurrian al integrar las imagenes pero gracias a esta logramos insertarla de la mejor manera posible.

## Prompt 3
**Pregunta:** "quiero colocar esa imagen como en la presentacion de la pagina como el landing pages nose si me entiendes".

**Respuesta de apoyo:** Se sugirio transformar el header principal en una portada tipo landing page con fondo rojo, texto grande y la marca institucional centrada.

**Implementación realizada:** Se ajustó la plantilla base para que el hero principal de la página tuviera una presentación visual más impactante y acorde a la referencia enviada.

## Prompt 4
**Pregunta:** "pasame el link para comprobar que se actualizo y enciende el entorno".

**Respuesta de apoyo:** Se indicaron las rutas locales y se ejecutó el proyecto con Django para verificar que la aplicación quedaba levantada correctamente.

**Implementación realizada:** Se validó con `python manage.py check` y se confirmó que la aplicación respondía en `http://localhost:8000`.


## Prompt 5
**Pregunta:** "esa es la url donde esta mi imagen".

**Respuesta de apoyo:** Se utilizó la imagen real enviada por el usuario como recurso local del proyecto para reemplazar la marca provisional.

**Implementación realizada:** Se copió la imagen a `static/images/logo_municipalidad_serena.jpg` y se vinculó al hero principal del landing page.

## Prompt 6
**Pregunta:** "puedes subir los cambios al repositorio de github?".

**Respuesta de apoyo:** Se revisó el estado del repositorio y se procedió a hacer el `commit` y `push` al remoto de GitHub.

**Implementación realizada:** Los cambios del branding del landing page quedaron subidos a GitHub en el repositorio principal del proyecto.

## Prompt 7 - Migracion y administracion relacional (Sumativa 2)

**Solicitud:** Se compartio feedback de revision sobre modelos Django, migraciones, datos JSON, Django Admin, los ocho mantenedores, variables de entorno, archivos estaticos y evidencia de la evaluacion.

**Respuesta de apoyo:** Se priorizaron las correcciones observadas y se propusieron mejoras incrementales a la persistencia relacional, los formularios, la busqueda y el despliegue.

**Implementacion realizada:** Se corrigio la generacion del codigo de actividades desde el modelo; se agregaron representaciones legibles en modelos; se ajustaron la busqueda y desactivacion de delegaciones; se preservo la fecha de ingreso importada; se agrego busqueda a Agenda y una tabla historica basada en `MedicionDelegacion` al Resumen; se incorporaron WhiteNoise y Gunicorn a la configuracion; y se actualizaron los documentos del modelo de datos y la checklist.

## Prompt 8 - Correccion de rutas del CRUD de Catalogo

**Prompt literal del usuario:** "otro feedback:" seguido por el informe de revision que identifica el conflicto entre la ruta de Catalogo y la ruta generica, solicita ordenar las rutas, anota que faltan pruebas del CRUD y recomienda corregir la checklist.

**Respuesta de apoyo:** Se confirmo el conflicto por orden de evaluacion de rutas y se aplicaron las correcciones solicitadas. Se agregaron pruebas para comprobar que la URL canonica usa la plantilla propia, que el alta y validacion de duplicados funcionan, que eliminar exige POST y que un funcionario no accede al mantenedor.

**Implementacion realizada:** Las rutas especificas de Catalogo quedaron antes de la ruta generica `<slug:slug>`, se agrego un comentario preventivo, se ajusto la checklist y se documento la politica de eliminacion del catalogo.

## Prompt 9 - CRUD propio de Actividades y Evidencias

**Solicitud (resumida):** Completar el CRUD propio de los mantenedores Actividades y Evidencias con el mismo patrón de Delegaciones y Catálogo. En Actividades, agregar edición y eliminación reales al listado existente `/actividades/` sin crear un segundo listado, evaluar si conviene bloquear la edición de actividades aprobadas o rechazadas, advertir que eliminar una actividad borra sus evidencias y enlazar la tarjeta del índice de mantenedores a ese listado. En Evidencias, construir en `/administracion/evidencias/` una lista con búsqueda, un formulario de alta y edición con selector de actividad y una eliminación con confirmación, declarando sus rutas antes de la ruta genérica. Registrar cada acción en `Auditoria`, agregar pruebas por CRUD, ejecutar `check`, `makemigrations --check --dry-run` y `test`, y actualizar la checklist, el modelo de datos y este archivo, sin tocar Perfiles ni Períodos.

**Respuesta de apoyo:** Se revisaron primero las vistas, formularios, rutas y plantillas de Catálogo y Delegaciones para replicar su estilo. Se propuso bloquear la edición y eliminación de actividades aprobadas, porque ya suman al avance de las metas, y permitir corregir las rechazadas devolviéndolas a revisión. También se detectó que las rutas nuevas `actividad/<codigo>/editar/` y `actividad/<codigo>/eliminar/` debían declararse antes de `actividad/<codigo>/<decision>/`, que de lo contrario las capturaba como una decisión de revisión.

**Implementación realizada:** Vistas `actividad_editar` y `actividad_eliminar`, restringidas al autor o a administración y coordinación, con confirmación por GET, borrado por POST y auditoría; botones Modificar y Eliminar reales en `actividades.html` y la tarjeta de Actividades enlazada a `/actividades/`. Vistas `evidencia_lista`, `evidencia_form` y `evidencia_eliminar` con el formulario `EvidenciaMantenedorForm` y tres plantillas nuevas al estilo de Catálogo. Clases de prueba `ActividadCRUDTests` y `EvidenciaCRUDTests`, y las decisiones documentadas en `MODELO_DATOS.md`.

---

# Evaluación Sumativa 3 — Autenticación, perfiles, recuperación de contraseña y salida de Django Admin

Herramienta usada: **Claude Code** (asistente de IA dentro de VS Code), trabajando directamente sobre el repositorio.

## Prompt 10 — Diagnóstico contra la rúbrica

**Prompt literal:** "Necesito que revises este directorio de trabajo y esta rubrica adjuntada. Dinos, qué nos falta. Y QUÉ Tenemos listo. Directo al grano." (con el PDF de la pauta adjunto).

**Qué respondió la IA:** Leyó el código y comparó cada criterio de la rúbrica. Nos dijo que ya teníamos login y logout, los 8 mantenedores, las transacciones, la base de datos y EC2, y que nos faltaban cuatro cosas que valían 40 puntos:
- No existía la recuperación de contraseña.
- Los perfiles no usaban los grupos de Django.
- Todos los perfiles veían el mismo dashboard.
- El README seguía presentando Django Admin como la forma de administrar.

**Cómo lo usamos:** Esa lista fue nuestro plan de trabajo, ordenado por puntaje.

## Prompt 11 — Implementación

**Prompt literal:** "Haz todo, MENOS el documento técnico de PDF/Word. Indícame qué cambiaste, CÓMO implementaste cada punto, y en dónde. En evidencias IA dime cómo ayudó la IA, con un lenguaje humano y directo al grano."

**Cómo ayudó la IA, punto por punto:**

1. **Perfiles con grupos de Django.**
   - **Qué propuso:** No borrar nuestros roles (delegado, verificador, etc.), porque todo el flujo de actividades depende de ellos, y montar encima tres grupos de Django: Administrador, Supervisor y Administrativo, cada uno con permisos reales (`view`, `add`, `change` y `delete` por tabla).
   - **Qué hizo:** Escribió la migración `0015_perfiles_de_acceso`, que crea los grupos y además asigna perfil a los usuarios que ya estaban en la base de EC2, para no tener que hacerlo a mano.
2. **Mantenedores protegidos por permisos.**
   - **Qué hizo:** Cambió el control de acceso para que cada pantalla (listar, crear, editar, eliminar) pida su permiso de Django, y los botones se muestran u ocultan según esos permisos.
   - **Qué encontró:** Al correr las pruebas, detectó un caso que no habíamos pensado: un funcionario desactivado seguía teniendo los permisos de su grupo. Lo corrigió con un backend de autenticación propio (`backends.py`).
3. **Asignación de grupo al crear usuarios.**
   - **Qué hizo:** Agregó el campo "Perfil de acceso" al formulario de funcionarios.
   - **Qué validó:** Que un perfil no quede por debajo del rol (por ejemplo, un rol administrador con perfil Administrativo se rechaza).
4. **Paneles por perfil.**
   - **Qué hizo:** Creó una vista `panel` y tres plantillas distintas. Al iniciar sesión, cada usuario llega al panel de su perfil:
     - Administrador: visión global y gestión de usuarios.
     - Supervisor: información operacional y los mantenedores autorizados.
     - Administrativo: solo sus funciones y la lista de lo que tiene restringido.
5. **Recuperación de contraseña.**
   - **Qué recomendó:** Usar las vistas que Django ya trae (generan un token firmado, de un solo uso y con vencimiento) en vez de programar el token a mano, porque son más seguras. Hizo nuestras las plantillas y el correo, y dejó el cambio registrado en la auditoría.
   - **Qué nos avisó:** Que AWS bloquea el puerto 25, y que por eso hay que usar Gmail por el 587 con una "contraseña de aplicación".
6. **Fuera Django Admin.**
   - **Qué hizo:** Quitó la ruta `/admin/` y la app del proyecto.
   - **Qué reemplazó:** Las pruebas que dependían del Admin las cambió por pruebas de que `/admin/` responde 404.
7. **Pruebas.**
   - **Qué escribió:** El archivo nuevo `test_unit_seguridad.py`, con 21 pruebas: perfiles, permisos, paneles, creación de usuarios con grupo y el flujo completo de recuperación (el correo se envía, el enlace funciona una sola vez, un token falso se rechaza y se ingresa con la clave nueva).
   - **Qué corrigió de paso:** Errores que nosotros no habríamos visto a simple vista, como un `initial` que debía ser la clave del grupo y no el objeto.

**Verificación:** La IA corrió `python manage.py test` (517 pruebas en verde) y recorrió con las cuentas demo los tres paneles y el flujo de recuperación, usando un correo de prueba. A nosotros nos tocó revisar cada cambio y probar el envío con un correo real (Gmail) desde EC2.

**Lo que la IA no hizo:** No escribió el documento técnico en PDF/Word, no levantó la instancia EC2 ni configuró la cuenta de Gmail. Eso lo hicimos nosotros.

## Prompt 12 — Ajustes pedidos en la revisión del equipo

**Prompt literal:** Pegamos la lista de pendientes de nuestra reunión ("Creación de compromisos… Botón para subir evidencia… Indicador de evidencia… Limpieza de plantilla… Estados de revisión… Restricción de vista del Delegado… Separación de roles… Diseño de interfaz") y pedimos "dinos qué cambiaste".

**Cómo ayudó la IA:**

- **Compromisos.** Nos propuso una regla clara y la dejó escrita en la agenda: la coordinación crea y asigna a un delegado; el delegado o funcionario registra los de su delegación.
- **Evidencias.** Separó "Subir evidencia" en una pantalla propia, agregó la columna "Evidencia" (cargada o sin evidencia) en el listado y sacó el formulario de carga de la vista de revisión.
- **Revisión.** Quitó "Solicitar corrección": ahora solo se aprueba, o se rechaza con un motivo obligatorio.
- **Ámbito del delegado.** Encontró todos los lugares donde un delegado veía otras delegaciones (medición, semáforo, resumen, informes, filtros y la página de delegación) y los limitó a la suya.
- **Coordinador y delegado.** Creó la pantalla "Delegados" para la coordinación.
- **Diseño.** Reorganizó el menú y aplicó el estilo "más cuadrado".

**Dónde la corregimos nosotros:** Al principio la IA convirtió la cuenta `funcionario.centro` en delegado. Le respondimos: "¿por qué funcionario pasa a ser delegado y no verificador? El verificador es el que debe cumplir las funciones de delegado". La IA lo corrigió:
- `verificador.demo` es ahora el delegado de Centro.
- El rol delegado puede aprobar o rechazar las evidencias de su delegación.
- Nadie puede revisar una actividad que registró él mismo.

**Qué detectó la IA al probar:** Recorrió las pantallas con cada cuenta demo y encontró que el panel del delegado se caía porque una variable de la vista pisaba la del menú. Lo arregló y agregó una prueba para ese caso.
