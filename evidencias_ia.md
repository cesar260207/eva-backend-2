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
