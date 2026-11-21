# Diagramas actualizados

Revisión de los diagramas del informe de diseño (etapa 2) frente al sistema después de los requerimientos de octubre 2026.

| Diagrama | Figura del informe | ¿Cambia? | Motivo | Versión nueva |
| --- | --- | --- | --- | --- |
| Diagrama de requerimientos | Figuras 1 a 12 | Sí | Se reorganiza como en el modelo del profesor (cada épica como «Gestionar X» con sus requerimientos «Debe permitir…») y se agregan RF-039 a RF-050 de octubre | [requerimientos.md](requerimientos.md) |
| Casos de uso de alto nivel | Figuras 13 a 20 | Sí | El profesor pidió gestiones de alto nivel en vez de un caso por historia; se agregan G06 Ajustes, G07 Ausencias y G08 Atenciones sociales | [../CASOS_DE_USO.md](../CASOS_DE_USO.md) |
| Casos de uso de detalle | Figuras 21 a 28 | Sí | Cada gestión se descompone en sus operaciones con include y extend; los actores se comprueban contra el sistema | [../CASOS_DE_USO.md](../CASOS_DE_USO.md) |
| Diagrama de clases | Figuras 29 a 32 | Sí | Cinco clases nuevas (Organizacion, Ajuste, Ausencia, CasoSocial, Comentario) y campos nuevos en Actividad, Compromiso, ItemMedible e Indicador | [../DIAGRAMA_CLASES.md](../DIAGRAMA_CLASES.md) |
| Entidad-relación, modelo lógico y físico | Figuras 33 a 35 | Sí | Cinco tablas nuevas y columnas nuevas (migraciones 0021 a 0028) | [entidad_relacion.md](entidad_relacion.md) |
| Diagrama de componentes | Figura 36 | No en su estructura | Siguen los mismos componentes (cliente web, Django con autenticación, `delegaciones_app`, `gestion_app`, MySQL y almacenamiento de evidencias). Solo queda desactualizado el texto que dice «17 clases» (ahora 24 tablas) y la mención a HTTPS, que sigue pendiente | Sin versión nueva |
| Diagrama de paquetes | Figura 37 | Sí | Módulo nuevo `reglas.py` y comandos `importar_organizaciones`, `generar_matriz` y `cargar_matriz` | [paquetes.md](paquetes.md) |
| Diagrama de despliegue | Figura 38 | No | El servidor es el mismo: EC2 con Amazon Linux 2023, Nginx, Gunicorn con systemd, MySQL 8.4 y phpMyAdmin con PHP-FPM, código desde GitHub y `.env`. Lo nuevo es operación, no infraestructura: la tarea de cron del respaldo diario (`scripts/respaldo.sh`) y los archivos del municipio copiados por `scp` fuera del repositorio | Sin versión nueva |
| Prototipo, wireframes y trazabilidad | Figuras 39 a 64 y Tabla 38 | Sí | Las pantallas ya existen; los wireframes de CU-04, CU-06, CU-20, CU-23 y CU-30 se reemplazan por las pantallas reales y la trazabilidad llega hasta la URL | [trazabilidad.md](trazabilidad.md) |

Los diagramas están en Mermaid: GitHub los muestra como imagen al abrir el archivo. Para la presentación se pueden exportar con el editor de Mermaid (mermaid.live) o con la extensión de Mermaid de VS Code.
