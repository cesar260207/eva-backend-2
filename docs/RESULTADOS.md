# Resultados del SGR

Números medidos (no estimados) el 21 de noviembre de 2026 sobre la rama `feat/requerimientos-octubre`. Los datos para gráficos de la presentación están en [`docs/resultados/`](resultados/), en CSV.

## 1. Pruebas automáticas

| Concepto | Resultado |
| --- | --- |
| Pruebas ejecutadas | 676 |
| Aprobadas | 676 (100 %) |
| Unitarias / de integración | 453 / 223 |
| Antes de esta rama (main después del PR #16) | 601 pruebas, 26 fallaban |
| Casos de uso del catálogo con pruebas y en estado «Aprobado» | Todos (ningún «Reprobado» en [PLAN_DE_PRUEBAS.md](../PLAN_DE_PRUEBAS.md)) |
| Actores de los casos de uso comprobados contra el sistema | 184 de 184 combinaciones de perfil y pantalla |

Pruebas por módulo ([pruebas_por_modulo.csv](resultados/pruebas_por_modulo.csv)):

| Módulo | Pruebas |
| --- | --- |
| test_integracion | 223 |
| test_unit_organizacion | 69 |
| test_unit_compromisos | 54 |
| test_unit_actividades | 51 |
| test_unit_transversal | 50 |
| test_unit_medicion | 49 |
| test_unit_reglas_nuevas | 44 |
| test_unit_delegaciones | 43 |
| test_unit_seguridad | 31 |
| test_unit_alertas | 28 |
| test_unit_plan_pruebas | 16 |
| test_unit_autenticacion | 8 |
| test_unit_matriz | 8 |
| test_casos_de_uso | 2 (una de ellas hace 184 comprobaciones) |

**Cómo se midió:** `python manage.py plan_pruebas` (genera el plan con el resultado de cada prueba).

## 2. Cobertura del código

| Concepto | Resultado |
| --- | --- |
| Cobertura total | **93 %** (3.540 sentencias, 235 sin cubrir) |
| Modelos y reglas (`models.py`, `reglas.py`) | 97 % y 95 % |
| Vistas (`delegaciones_app/views.py`, `gestion_app/views.py`) | 93 % y 99 % |
| Permisos y auditoría | 99 % y 100 % |

Sin cobertura quedan los archivos que no se ejecutan en las pruebas: `wsgi.py` y `asgi.py` (arranque del servidor), y los comandos `plan_pruebas` y `calcular_indicadores`, que se ejecutan a mano. El detalle por archivo está en [cobertura.csv](resultados/cobertura.csv).

**Cómo se midió:** `pip install -r requirements-dev.txt`, `coverage run manage.py test` y `coverage report` (configuración en `.coveragerc`: código de las aplicaciones, sin pruebas ni migraciones).

## 3. Requerimientos

| Grupo | Planificados | Implementados | Pendientes |
| --- | --- | --- | --- |
| RF de la versión 1 (informe de diseño) | 38 | 38 | 0 (RF-031, la vista global por cargos, se implementó en noviembre) |
| RF de la versión 2 (octubre 2026) | 12 | 12 | 0 |
| RNF de la versión 2 | 2 | 2 | 0 |
| RF de la Matriz SGR completa (RF-063 a RF-065) | 3 | 3 | 0 |
| **Total de RF** | **53** | **53 (100 %)** | **0** |

Las 10 reglas de octubre ([reglas_octubre.csv](resultados/reglas_octubre.csv)): 9 implementadas y probadas; la regla 6 («no ingresar solo para generar puntaje») es una política de uso y el sistema la apoya con el tope diario, el tope por ítem y la auditoría.

Historias de usuario terminadas por sprint: [COMPLETAR POR EL GRUPO con el tablero] (el repositorio no registra a qué sprint perteneció cada historia).

## 4. Tamaño del sistema

| Concepto | Cantidad |
| --- | --- |
| Modelos (tablas propias) | 24 |
| Migraciones | 28 |
| Mantenedores | 12 |
| Transacciones | 4 |
| Rutas (URL) | 47 |
| Plantillas HTML | 40 |
| Comandos de administración | 6 |
| Líneas de código (sin pruebas) | 5.636 |
| Líneas de pruebas | 7.037 |
| Casos de uso / gestiones de alto nivel | 171 / 19 |

Hay más líneas de pruebas que de código. Datos en [tamano.csv](resultados/tamano.csv).

## 5. Tiempos de respuesta frente al RNF-002

El RNF-002 del informe pide responder en 2 segundos como máximo en registro y consulta, y en 5 segundos en tableros consolidados.

| Perfil | Página | Promedio (ms) | Máximo (ms) | Límite RNF-002 (ms) | Cumple |
| --- | --- | --- | --- | --- | --- |
| Profesional | Panel del perfil | 45,1 | 50,8 | 5.000 | Sí |
| Profesional | Lista de actividades | 17,9 | 20,7 | 2.000 | Sí |
| Profesional | Formulario de actividad | 20,5 | 21,7 | 2.000 | Sí |
| Profesional | Detalle de actividad | 17,9 | 37,3 | 2.000 | Sí |
| Profesional | Ficha personal | 16,1 | 17,4 | 5.000 | Sí |
| Delegado | Semáforo | 22,9 | 24,1 | 5.000 | Sí |
| Delegado | Tubo de trabajo | 21,6 | 28,4 | 2.000 | Sí |
| Coordinador | Cumplimiento general | 13,7 | 16,4 | 5.000 | Sí |
| Coordinador | Resumen por delegación | 15,9 | 18,5 | 5.000 | Sí |
| Coordinador | Lista de ajustes | 10,2 | 12,7 | 2.000 | Sí |
| Coordinador | Informes | 13,0 | 15,1 | 5.000 | Sí |
| Administrador | Consulta de auditoría | 5,7 | 9,8 | 2.000 | Sí |

**Cómo se midió:** `python scripts/medir_tiempos.py`. Crea una base de prueba en memoria con los datos de `seed_demo`, entra con cada perfil y promedia 20 llamadas por página con el cliente de pruebas de Django ([tiempos_respuesta.csv](resultados/tiempos_respuesta.csv)).

**Límite de la medición:** mide el tiempo de la aplicación en un computador de desarrollo con SQLite, sin la red ni el servidor real (Nginx, Gunicorn y MySQL en EC2). Sirve para comparar páginas y detectar una consulta lenta, no como tiempo que verá el usuario; para eso falta una prueba de carga sobre el servidor (plan de mantención).

## 6. Datos del municipio procesados

| Concepto | Antes | Después |
| --- | --- | --- |
| Organizaciones sin delegación al importar el Excel (2.709) | 1.812 | 24 (2 de ALFALFARES y 22 sin territorio) |
| Organizaciones «sin clasificar» | 1.625 | 0 (lo que no calza con un tipo es «funcional», Ley 19.418) |
| Cargos de la matriz en el sistema | 4 genéricos | 13 cargos y 79 ítems |

## 7. Aportes al repositorio

`git shortlog -sn --all` en los dos repositorios ([aportes_commits.csv](resultados/aportes_commits.csv)):

| Repositorio | Nombre en Git | Commits |
| --- | --- | --- |
| eva-backend-2 | conejobinario | 75 |
| eva-backend-2 | Tu Nombre (firma genérica) | 9 |
| eva-backend-2 | Faride Luna | 8 |
| eva-backend-2 | Vinzenz Lafferte, vinzenz, Vinzenz | 7 |
| eva-backend-2 | kimbo | 4 |
| eva-backend-2 | Dante, DanteObsolette | 2 |
| proyecto-de-titulo-en-local | Tu Nombre (firma genérica) | 2 |
| proyecto-de-titulo-en-local | kimbo | 1 |

Notas para leer la tabla:

- Un integrante puede aparecer con varios nombres en Git; se agruparon por la cuenta de correo de cada commit.
- «conejobinario» corresponde a [COMPLETAR POR EL GRUPO]. Sus commits incluyen los de la rama `feat/requerimientos-octubre`, hechos con apoyo de IA (registrado en `evidencias_ia.md`, prompt 14).
- Los commits con la firma «Tu Nombre» se asignan a su autor en el README, sección «Autoría de los commits».
- El número de commits no mide el aporte: el PR #16 trajo buena parte del trabajo de octubre en solo dos commits, y la documentación y las pruebas también son aporte.
