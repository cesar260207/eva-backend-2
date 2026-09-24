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