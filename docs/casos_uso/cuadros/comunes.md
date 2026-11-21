## Casos comunes

Se usan en varias gestiones; se describen una vez.

**Incluidos comunes**

| Identificador | Nombre | Propósito | Precondiciones | Postcondiciones | Flujo principal | Casos extendidos | Pruebas |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CU-06.1 | Recalcular indicadores automáticamente | Actualizar el avance de las metas tras un cambio. | Cambió una actividad o una meta. | Indicadores, ficha y semáforo al día. | Volver a calcular el avance de las metas afectadas. | Ninguno | 10 unitarias y 15 de integración (aprobado) |
| CU-10.1 | Buscar actividad por código | Localizar la actividad por su código o filtros, dentro del ámbito. | Se eligió o buscó una actividad. | Actividad localizada. | Buscar por código, delegación, estado, fecha o ítem entre las autorizadas. | CU-26.1 Denegar acceso por ámbito; CU-10.2 Consulta sin coincidencias | 2 unitarias y 19 de integración (aprobado) |
| CU-29 | Buscar y filtrar | Encontrar registros por texto o filtros, solo dentro del ámbito del usuario. | Hay criterios de búsqueda o se abrió una lista. | Lista filtrada; Delegado y Profesional ven solo su delegación (CU-29.1). | Aplicar el texto y los filtros sobre los registros autorizados. | CU-70 Consulta sin coincidencias | 3 unitarias y 16 de integración (aprobado) |
| CU-45 | Registrar en auditoría | Dejar constancia de quién hizo la operación, cuándo y qué cambió. | Se creó, modificó, eliminó, revisó o exportó un dato. | Evento guardado; nadie puede editarlo ni borrarlo. | Guardar usuario, fecha, acción, registro y valores antes y después. | Ninguno | Caso nuevo: sin código propio en el plan de pruebas |

**Extensiones comunes**

| Identificador | Nombre | Caso base | Condición | Resultado | Pruebas |
| --- | --- | --- | --- | --- | --- |
| CU-127 | Impedir eliminación con datos relacionados | CU-120 Eliminar período; CU-130 Eliminar ítem medible | Otros registros dependen de este. | La eliminación se rechaza y se informa qué registros lo impiden. | Caso nuevo: sin código propio en el plan de pruebas |
| CU-26.1 | Denegar acceso por ámbito | CU-10.1 Buscar actividad por código; CU-29.1 Restricción de búsqueda por ámbito; CU-30 Consultar auditoría de cambios | El registro o la pantalla está fuera del perfil o de la delegación del usuario (por ejemplo, un Profesional abre la auditoría). | Se responde «no encontrado» o se vuelve al panel, y el intento queda en la auditoría. | 44 unitarias y 25 de integración (aprobado) |
| CU-28.1 | Restricción por período cerrado | CU-64 Informar felicitación o reclamo; CU-66 Modificar ajuste; CU-67 Aplicar o rechazar ajuste; CU-71 Registrar ausencia; CU-73 Modificar ausencia; CU-119 Modificar período; CU-121 Registrar parámetro; CU-25 Modificar parámetro; CU-123 Eliminar parámetro; CU-04 Registrar ítem medible; CU-129 Modificar ítem medible; CU-130 Eliminar ítem medible | El período del registro está cerrado. | No se guarda: un período cerrado solo cambia con una reapertura auditada. | 10 unitarias y 15 de integración (aprobado) |
| CU-69 | Informar error de validación | CU-68 Validar datos de ajuste; CU-74 Validar datos de ausencia; CU-76 Validar datos de atención social; CU-84 Validar datos de organización; CU-91 Validar datos de delegación; CU-97 Validar datos de cargo; CU-102 Validar datos de rol; CU-108 Validar datos de funcionario; CU-124 Validar datos de período; CU-125 Validar datos de parámetro | Un campo obligatorio está vacío o un dato no cumple una regla. | El formulario vuelve con el error junto al campo y no se guarda nada. | Caso nuevo: sin código propio en el plan de pruebas |
| CU-70 | Consulta sin coincidencias | CU-29 Buscar y filtrar; CU-20.1 Consolidar datos filtrados | Ningún registro cumple el criterio. | Se informa que no hay resultados, sin error. | Caso nuevo: sin código propio en el plan de pruebas |
| CU-85 | Desactivar en vez de eliminar | CU-81 Eliminar organización; CU-89 Eliminar delegación; CU-96 Eliminar cargo; CU-107 Eliminar funcionario; CU-115 Eliminar elemento de catálogo | El registro tiene datos relacionados. | No se borra: queda inactivo para conservar el historial, la confirmación explica por qué y después se puede reactivar. | Caso nuevo: sin código propio en el plan de pruebas |
