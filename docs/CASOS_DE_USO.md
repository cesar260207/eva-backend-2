# Casos de uso del SGR

Los casos de uso siguen el modelo del profesor («Relación entre los artefactos»): cada épica se expresa como una gestión de alto nivel («Gestionar X») y cada gestión se descompone en casos de detalle (registrar, consultar, modificar, eliminar y operaciones propias), con sus casos incluidos (validar, buscar, registrar en auditoría) y sus extensiones (rechazar con motivo, período cerrado, entre otras).

- 19 gestiones de alto nivel, G01 a G19, cada una asociada a una épica (EP-01 a EP-08).
- 171 casos: 81 de detalle, 41 incluidos y 49 extensiones.
- CU-01 a CU-31 son los códigos del catálogo del software (`CATALOGO_CU` en `delegaciones_app/plan_pruebas.py`); CU-32 a CU-139 son los casos agregados en la versión 2.
- Los actores de cada caso coinciden con los permisos reales del sistema: la prueba `delegaciones_app/test_casos_de_uso.py` entra con un usuario de cada perfil y comprueba 184 combinaciones de perfil y pantalla.

## Diagramas

| Diagrama | Archivo |
| --- | --- |
| Alto nivel (16:9, para la presentación) | [alto_nivel_diapositiva.png](casos_uso/imagenes/alto_nivel_diapositiva.png) |
| Alto nivel (vertical, PlantUML) | [alto_nivel_vertical.png](casos_uso/imagenes/alto_nivel_vertical.png) |
| Detalle de cada gestión | [diapositiva_g01.png](casos_uso/imagenes/diapositiva_g01.png) a [diapositiva_g19.png](casos_uso/imagenes/diapositiva_g19.png) |
| Fuentes PlantUML | [plantuml/](casos_uso/plantuml/) |
| Fuentes Graphviz | [dot/](casos_uso/dot/) |

## Gestiones y cuadros

| Gestión | Nombre | Épica | Cuadros |
| --- | --- | --- | --- |
| G01 | Gestionar acceso al sistema | EP-08 | [G01.md](casos_uso/cuadros/G01.md) |
| G02 | Gestionar actividades | EP-01 | [G02.md](casos_uso/cuadros/G02.md) |
| G03 | Gestionar evidencias | EP-03 | [G03.md](casos_uso/cuadros/G03.md) |
| G04 | Validar actividades | EP-03 | [G04.md](casos_uso/cuadros/G04.md) |
| G05 | Gestionar tubo de trabajo | EP-04 | [G05.md](casos_uso/cuadros/G05.md) |
| G06 | Gestionar ajustes de puntaje | EP-02 | [G06.md](casos_uso/cuadros/G06.md) |
| G07 | Gestionar ausencias | EP-02 | [G07.md](casos_uso/cuadros/G07.md) |
| G08 | Gestionar atenciones sociales | EP-01 | [G08.md](casos_uso/cuadros/G08.md) |
| G09 | Gestionar organizaciones comunitarias | EP-01 | [G09.md](casos_uso/cuadros/G09.md) |
| G10 | Gestionar delegaciones | EP-08 | [G10.md](casos_uso/cuadros/G10.md) |
| G11 | Gestionar cargos | EP-08 | [G11.md](casos_uso/cuadros/G11.md) |
| G12 | Gestionar roles | EP-08 | [G12.md](casos_uso/cuadros/G12.md) |
| G13 | Gestionar funcionarios y usuarios | EP-08 | [G13.md](casos_uso/cuadros/G13.md) |
| G14 | Gestionar catálogo | EP-08 | [G14.md](casos_uso/cuadros/G14.md) |
| G15 | Gestionar períodos y parámetros | EP-08 | [G15.md](casos_uso/cuadros/G15.md) |
| G16 | Gestionar ítems medibles y metas | EP-02 | [G16.md](casos_uso/cuadros/G16.md) |
| G17 | Consultar resultados | EP-05 | [G17.md](casos_uso/cuadros/G17.md) |
| G18 | Generar informes | EP-06 | [G18.md](casos_uso/cuadros/G18.md) |
| G19 | Consultar auditoría y perfiles | EP-08 | [G19.md](casos_uso/cuadros/G19.md) |

Los casos que se repiten en varias gestiones (registrar en auditoría, buscar y filtrar, informar error de validación, entre otros) se describen una sola vez en [comunes.md](casos_uso/cuadros/comunes.md).

## Trazabilidad y códigos

- [trazabilidad.md](casos_uso/cuadros/trazabilidad.md): cada caso de detalle con su gestión, actores, pantalla (URL) y pruebas.
- [indice_codigos.md](casos_uso/cuadros/indice_codigos.md): los 171 códigos, con su tipo y gestión.
- [pendientes_software.md](casos_uso/cuadros/pendientes_software.md): diferencias entre los casos y el software, y su estado.
- [plan_de_pruebas_corrida.md](casos_uso/cuadros/plan_de_pruebas_corrida.md): corrida del plan de pruebas de la que salen los conteos de los cuadros.

## Cómo se mantienen

Los cuadros, las fuentes y los diagramas se generan desde `casos_uso/fuente/datos_v2.py`. El procedimiento está en [casos_uso/LEEME.md](casos_uso/LEEME.md). Un código existente no se cambia: la presentación y el informe los citan.
