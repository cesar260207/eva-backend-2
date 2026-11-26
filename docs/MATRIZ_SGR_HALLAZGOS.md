# Matriz SGR: correspondencia con el sistema, hallazgos y decisiones

Revisión de las 25 hojas de la planilla «MATRIZ SGR TRIMESTRE» (exportadas a CSV, con sus fórmulas aparte)
hecha en noviembre de 2026. Los archivos tienen nombres, teléfonos y domicilios reales: se leen desde la
carpeta del usuario y **no se copian al repositorio** (RNF-019). Este documento no reproduce ningún dato personal.

## 1. Dónde quedó cada hoja

| Hoja | Qué contiene | En el sistema |
|---|---|---|
| 01 REGALOS NIÑOS | Datos de la actividad de fin de año | `beneficiarios_app` (inscripción e importación desde Excel) |
| 02, 03, 06 TUBO (por delegación) | Tareas con fecha, solicitante, responsable, compromiso y estatus | Tubo de seguimiento (`Compromiso` tipo `solicitud`). Se importan con `importar_tubo` |
| 04, 19 TUBO CARTAS | Cartas de la oficina de partes y su seguimiento | Tubo de cartas (`Compromiso` tipo `carta`). Se importan con `importar_tubo` |
| Hojas de cargo (APOY ADM, T OO CC 1 a 4, COSERCO, SOCIAL 1 a 5, PLAN y CON, G SEGUR) | Ítems, ponderador, meta trimestral, avance y bitácora | `Cargo`, `ItemMedible` y `Meta` (`generar_matriz` + `cargar_matriz`); la bitácora es el registro de `Actividad` |
| SALON | Vista global de todos los cargos | Pantalla **Resultados → Matriz por cargos** (`/gestion/matriz/`, RF-031) y su exportación a Excel |
| SEMAFORO | Días del período, esperado al día, descuentos por ausencia | `Periodo.porcentaje_esperado`, `Ausencia` y el semáforo (`/gestion/semaforo/`) |
| RECLAMOS | Reclamos y felicitaciones con su efecto | `Ajuste` (informado por el delegado, decidido por la coordinación) |
| G SOC | Tiempos de respuesta de la gestión social | `CasoSocial`: fechas de ingreso, visita e informe, y `plazos()` (pantalla Atención social) |
| LISTA y DATO MENU | Listas desplegables de la planilla | Constantes de `CasoSocial` (grupos, subtipos de informe, forma de entrega) y el catálogo de tipos de atención |

## 2. Lo que se agregó con esta revisión

1. **Ítem «Pendientes en tubo menor a 10 %»** (RF-063). Estaba en SALON para «Planificación y control» pero
   no en su hoja de cargo, por eso ese cargo sumaba 85 %. `generar_matriz` ahora lo completa desde SALON con el
   15 % que faltaba (queda en `data/matriz_cargos.json`: 13 cargos, 80 ítems, todos suman 100 %). Se calcula con
   el nuevo tipo `tubo_pendientes`: porcentaje de tareas sin iniciar (ingresadas o pendientes) en el tubo de la
   delegación, y puntaje por tramos: hasta 10 % → 100; hasta 50 % → 50; sobre 50 % → 0.
2. **Matriz por cargos** (RF-031, antes postergado). Bloques en el orden de SALON, una ficha por funcionario con
   ítem, ponderador, meta, avance, cumplimiento y ponderado; el recuadro de fechas del período y el resumen de
   los tubos por estado. La coordinación ve todo; el delegado, su equipo; el funcionario, solo su fila.
3. **Plazos de la gestión social** (RF-064, hoja G SOC): visita programada hasta 10 días después del ingreso,
   visita el día programado, informe hasta 4 días después de la visita y hasta 20 desde el ingreso, máximo 2
   reingresos del informe. Cada tramo se muestra cumplido, en curso o vencido.
4. **Catálogo de la hoja LISTA**: grupos (Informes sociales, Gestión de subsidios, Derivaciones, Otras gestiones
   sociales), los tres subtipos de informe social con su forma de entrega (dinero, material, documento) y la
   forma de los subsidios (IPS → documento; PGU, SUF, SAP → aporte).
5. **Importación de los tubos** (RF-065): comando `importar_tubo`. Sin `--aplicar` solo revisa; el folio sale
   del contenido (`AGR-IMP-…`, `CAR-IMP-…`), así que repetirlo no duplica tareas.

## 3. Errores encontrados en las fórmulas de la planilla

La planilla es un Google Sheets exportado a Excel. El cálculo de cada área es simple (logro / meta × ponderación),
pero tiene errores de copia. Ninguno pasa al sistema, porque el sistema calcula todo desde los datos con una sola
regla para todos los cargos (RN-017) en vez de copiar celdas entre hojas.

| Hoja | Problema | Consecuencia |
|---|---|---|
| SALON F928 | `=#REF!` | Origen del #REF! de los CSV |
| SALON G921 a G925 | Vínculos a libros externos (`[2]SEGURIDAD`, `[3]OO CC`, `[4]SOCIAL`) | #N/A o valores viejos si esos archivos no están |
| SALON F9 y F10 | Mezcla filas (`'T OC1'!F5` con `'T OC 2'!F6`) | Suma indicadores distintos |
| SALON E18 | Usa la columna G de G SOC2 y las demás filas la F | Meta mal calculada |
| SALON F16 | Incluye G SOC5 pero E16 no | Logro y meta no comparables |
| SALON / PLAN y CON | El ítem de pendientes del tubo existe solo en SALON | La hoja de cargo suma 85 % |
| AP ADM., COOR DISERCO, T OC | `CONCATENATE(L16:O16)` sobre un rango | #VALUE! en Excel |
| COOR DISERCO I14 | `=H14`, pero el valor está en G14 | Se pierde el componente de RECLAMOS |
| T OC1 desde la fila 30 | `O30 = A32` (desfase de 2 filas) | Claves mal armadas |
| T OC 3 y G SOC3 | Columnas DAY y MONTH invertidas | La clave no coincide con las otras hojas |
| T OC 4 K18 | `=B20` en vez de `=B18` | Fecha equivocada |
| AP ADM. G3 a G6 y casi todas las hojas de área | Los SUMIF llegan a la fila 209 a 248 (231 en AP ADM.), pero hay datos hasta la 450 a 962 | Los registros de más abajo no se suman |
| TUBO COMPAÑIAS / TUBO | Totales hasta la fila 290 a 300, SUMIF solo hasta la 99 o la 191 | Los totales no cuadran con el desglose |
| TUBO ANTENA V19 y U20 | El control compara la fila 14; el % divide por T19 en vez de R19 | El «OK/error» no controla y el % realizado está mal |
| G SOC 1, 3, 4 y 5; PLAN y CON | La meta de una fila es igual al logro (`F7=G7`, `E5=F5`) | Ese indicador sale siempre 100 % |
| G SOC 1 | Faltan los % en H3, H4 y H6; `I9` promedia logros con porcentajes | Filas sin puntaje y un promedio sin sentido |
| G SOC2 | `H7 = L5+R5+R5` (R5 dos veces, falta Y4); `R16 = Q16*Y16` | Logro mal calculado e inflado |
| G SOC3 | `F5` suma `Y2`, pero la columna es X | Se pierde un componente |
| G SOC4 | Falta `G6` y `H6 = G6*D6`; desde AF102 filas corridas | Indicador en 0 y claves mal armadas |
| G SOC5 | Falta la meta `E6` (`G6 = F6/E6`); `F9 = SUM(F4:F7)` deja fuera F3 | #DIV/0! y total incompleto |
| GES SEG | `H6` y `H7` cruzadas, `H8` y `H9` apuntan a filas equivocadas; `I10` deja fuera I8 e I9 | Cuatro % mal calculados y total incompleto |
| RECLAMOS | Fecha de columnas distintas según la fila; un bloque usa `H*V` y el otro `M*V`; solo 10 filas por bloque | Criterios distintos y reclamos sobre 10 no cuentan |
| RECLAMOS y hojas de cargo | El reclamo resta 20 % en unas hojas y 30 % en otras; el tope es 150 % | Distinto del documento de octubre (ver preguntas pendientes en el README) |
| RESUMEN | Columnas J a M desalineadas con B a H; `G14 = SEMAFORO!M14`; `L9` toma la meta | Casi todas las filas mezclan áreas |
| SEMAFORO | GES SEG no aparece | Esa área queda fuera del semáforo |
| DATO MENU y LISTA | Funciones de Google Sheets (`QUERY`, `UNIQUE`) que en Excel quedan como `__xludf.DUMMYFUNCTION`; el rango `DATA` no existe | #N/A y #NAME? en Excel |
| Varias hojas | Fechas imposibles (`09/07/0206`, `25/09//26`, `06--07-2026`), textos en columnas de fecha y correlativos repetidos | El sistema valida fechas, y `importar_tubo` descarta o anota lo ilegible |

## 4. Decisiones tomadas

| Tema | Decisión | Motivo |
|---|---|---|
| Bitácoras de las hojas de cargo | No se importan como actividades | Una actividad necesita evidencia y pasa por verificación, el cierre semanal y el límite diario; el trimestre julio-septiembre ya está cerrado |
| Hoja RECLAMOS | No se importa | Un ajuste exige respaldo formal adjunto y la decisión de la coordinación |
| «Pendiente» en el tubo | Tareas ingresadas o pendientes; «en proceso» no cuenta | Es lo que la planilla separa como trabajo sin iniciar |
| Tubo vacío | El ítem de pendientes vale 0 % | Sin tareas no hay proporción que medir; evita un 100 % sin trabajo |
| Estados de cartas | En proceso y Aprobada → en proceso; Finalizada y No aplica → realizada | «Aprobada» espera la acción comprometida; «No aplica» era solo para conocimiento. El estado original queda en la observación |
| Fecha comprometida ilegible | Se usa la fecha de ingreso y el texto original queda en la observación | El tubo exige una fecha comprometida válida |
| Teléfonos en los tubos | Solo se guarda un teléfono chileno reconocible (8 o 9 dígitos) | Correos u otros textos no son teléfono |
| RUT en la inscripción de beneficiarios | Único por actividad (evento + RUT) | El mismo niño puede estar en Navidad, Día del Niño y Aniversario; la planilla avisaba «RUT ya ingresado» dentro de la misma actividad |
| Valores en duda (tope, reclamo, meta de Emergencia) | Siguen como parámetros del período | Ver «Preguntas pendientes para el municipio» en el README |
