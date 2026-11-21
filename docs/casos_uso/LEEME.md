# Casos de uso del SGR, versión 2

Reemplaza a casos_uso_sgr.zip (versión 1). La diferencia principal: los códigos son los mismos del catálogo del software (CU-01 a CU-31 en plan_pruebas.py y en las pruebas). Los casos nuevos siguen desde CU-32 hasta CU-139.

- 19 gestiones de alto nivel (G01 a G19), cada una con su épica (EP-01 a EP-08).
- 171 casos: 81 de detalle, 41 incluidos y 49 extensiones.
- Verificado contra el sistema: 184 de 184 combinaciones de perfil y pantalla coinciden con los actores de los cuadros. Lo comprueba la prueba automática delegaciones_app/test_casos_de_uso.py, que reemplaza a fuente/probe.py (la primera revisión, a mano, dio 164 de 164).

## Carpetas

- imagenes/: alto_nivel_diapositiva.png (16:9, para la diapositiva 4), diapositiva_g01.png a diapositiva_g19.png (detalle de cada gestión) y alto_nivel_vertical.png (versión PlantUML).
- cuadros/: un archivo por gestión (G01.md a G19.md) con los cuadros del formato del profesor, comunes.md, trazabilidad.md (caso, actor, pantalla, pruebas), indice_codigos.md (los 171 códigos), pendientes_software.md y la corrida del plan de pruebas.
- plantuml/ y dot/: fuentes de los diagramas.
- fuente/: datos_v2.py (todos los casos), gen_v2.py (genera cuadros y PlantUML), detalle_dot.py (diagramas de detalle con Graphviz), alto_ppt.py (alto nivel 16:9 con matplotlib) y probe.py (comprueba los actores entrando con cada perfil).

## Regenerar

    python fuente/gen_v2.py salida cuadros/plan_de_pruebas_corrida.md
    python fuente/detalle_dot.py salida/dot G01 G02 G03 G04 G05 G06 G07 G08 G09 G10 G11 G12 G13 G14 G15 G16 G17 G18 G19
    python fuente/alto_ppt.py salida/dot/alto_nivel_diapositiva.png

Necesita matplotlib y Graphviz (dot). Para comprobar actores, desde la raíz del proyecto: `python manage.py test delegaciones_app.test_casos_de_uso`. Si cambia un actor en datos_v2.py o un permiso en el código, esa prueba falla e indica el caso, el perfil y la pantalla.

Los códigos de los casos nuevos se numeran solos según su posición en GESTIONES (datos_v2.py). Un caso nuevo debe llevar su código explícito (desde CU-140) para no correr los códigos que ya usan la presentación y el informe.
