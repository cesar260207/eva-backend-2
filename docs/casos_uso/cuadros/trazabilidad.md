| Gestión | Caso de uso | Actor | Pantalla | Pruebas |
| --- | --- | --- | --- | --- |
| G01 | CU-32 Iniciar sesión | Usuario | `/login/` | Caso nuevo: sin código propio en el plan de pruebas |
| G01 | CU-33 Cerrar sesión | Usuario | `/logout/` | Caso nuevo: sin código propio en el plan de pruebas |
| G01 | CU-34 Recuperar contraseña | Usuario, Servidor de correo | `/recuperar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G01 | CU-35 Restablecer contraseña | Usuario | `/recuperar/<uidb64>/<token>/` | Caso nuevo: sin código propio en el plan de pruebas |
| G02 | CU-01 Registrar actividad | Usuario | `/actividad/nueva/` | 3 unitarias y 32 de integración (aprobado) |
| G02 | CU-41 Consultar actividades | Usuario | `/actividades/ y /actividad/<código>/` | Caso nuevo: sin código propio en el plan de pruebas |
| G02 | CU-42 Modificar actividad | Usuario | `/actividad/<código>/editar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G02 | CU-43 Eliminar actividad | Coordinador, Administrador | `/actividad/<código>/eliminar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G02 | CU-24 Comentar actividad | Profesional, Delegado, Administrador | `/actividad/<código>/comentario/` | 0 unitarias y 2 de integración (aprobado) |
| G03 | CU-09 Subir evidencia | Usuario | `/actividad/<código>/evidencia/` | 9 unitarias y 4 de integración (aprobado) |
| G03 | CU-52 Ver evidencia | Usuario | `/evidencia/<código>/archivo/` | Caso nuevo: sin código propio en el plan de pruebas |
| G04 | CU-11 Aprobar o rechazar actividad | Delegado, Coordinador, Administrador | `/actividad/<código>/aprobar/ o /rechazar/` | 18 unitarias y 21 de integración (aprobado) |
| G04 | CU-54 Anular aprobación | Delegado, Coordinador, Administrador | `/actividad/<código>/anular/` | Caso nuevo: sin código propio en el plan de pruebas |
| G05 | CU-02 Registrar compromiso | Usuario | `/agenda/nueva/` | 2 unitarias y 6 de integración (aprobado) |
| G05 | CU-12 Consultar agenda compartida | Usuario | `/agenda/` | 8 unitarias y 7 de integración (aprobado) |
| G05 | CU-14 Seguimiento de compromisos | Usuario | `/solicitudes/` | 2 unitarias y 0 de integración (aprobado) |
| G05 | CU-58 Modificar tarea | Usuario | `/agenda/<id>/editar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G05 | CU-13 Actualizar estado de la tarea | Usuario | `/agenda/<id>/estado/<estado>/` | 8 unitarias y 18 de integración (aprobado) |
| G05 | CU-59 Eliminar tarea | Coordinador, Administrador | `/agenda/<id>/eliminar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G06 | CU-64 Informar felicitación o reclamo | Delegado, Administrador | `/ajustes/nuevo/` | 0 unitarias y 1 de integración (aprobado) |
| G06 | CU-65 Consultar ajustes | Delegado, Coordinador, Administrador | `/administracion/ajustes/` | 0 unitarias y 2 de integración (aprobado) |
| G06 | CU-66 Modificar ajuste | Coordinador, Administrador | `/administracion/ajustes/<id>/editar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G06 | CU-67 Aplicar o rechazar ajuste | Coordinador, Administrador | `/ajustes/<id>/aplicar/ o /rechazar/` | 0 unitarias y 6 de integración (aprobado) |
| G07 | CU-71 Registrar ausencia | Delegado, Administrador | `/ausencias/nuevo/` | 0 unitarias y 2 de integración (aprobado) |
| G07 | CU-72 Consultar ausencias | Delegado, Coordinador, Administrador | `/administracion/ausencias/` | 0 unitarias y 1 de integración (aprobado) |
| G07 | CU-73 Modificar ausencia | Coordinador, Administrador | `/administracion/ausencias/<id>/editar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G08 | CU-03 Registrar atención social | Profesional, Administrador | `/casos-sociales/nuevo/` | 3 unitarias y 1 de integración (aprobado) |
| G09 | CU-78 Registrar organización | Administrador | `/administracion/organizaciones/nuevo/` | Caso nuevo: sin código propio en el plan de pruebas |
| G09 | CU-79 Consultar organizaciones | Usuario | `/administracion/organizaciones/` | Caso nuevo: sin código propio en el plan de pruebas |
| G09 | CU-80 Modificar organización | Delegado, Coordinador, Administrador | `/administracion/organizaciones/<id>/editar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G09 | CU-81 Eliminar organización | Administrador | `/administracion/organizaciones/<id>/eliminar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G09 | CU-82 Exportar organizaciones | Usuario | `/administracion/organizaciones/exportar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G09 | CU-83 Importar organizaciones | Administrador | comando importar_organizaciones (servidor) | 4 unitarias y 0 de integración (aprobado) |
| G10 | CU-86 Registrar delegación | Coordinador, Administrador | `/administracion/delegaciones/nuevo/` | Caso nuevo: sin código propio en el plan de pruebas |
| G10 | CU-87 Consultar delegaciones | Coordinador, Administrador | `/administracion/delegaciones/` | Caso nuevo: sin código propio en el plan de pruebas |
| G10 | CU-88 Modificar delegación | Coordinador, Administrador | `/administracion/delegaciones/<id>/editar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G10 | CU-89 Eliminar delegación | Coordinador, Administrador | `/administracion/delegaciones/<id>/eliminar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G10 | CU-90 Asignar delegado | Coordinador, Administrador | `/coordinacion/delegados/` | Caso nuevo: sin código propio en el plan de pruebas |
| G11 | CU-93 Registrar cargo | Coordinador, Administrador | `/administracion/cargos/nuevo/` | Caso nuevo: sin código propio en el plan de pruebas |
| G11 | CU-94 Consultar cargos | Coordinador, Administrador | `/administracion/cargos/` | Caso nuevo: sin código propio en el plan de pruebas |
| G11 | CU-95 Modificar cargo | Coordinador, Administrador | `/administracion/cargos/<id>/editar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G11 | CU-96 Eliminar cargo | Coordinador, Administrador | `/administracion/cargos/<id>/eliminar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G12 | CU-98 Registrar rol | Administrador | `/administracion/roles/nuevo/` | Caso nuevo: sin código propio en el plan de pruebas |
| G12 | CU-99 Consultar roles | Administrador | `/administracion/roles/` | Caso nuevo: sin código propio en el plan de pruebas |
| G12 | CU-100 Modificar rol | Administrador | `/administracion/roles/<id>/editar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G12 | CU-101 Eliminar rol | Administrador | `/administracion/roles/<id>/eliminar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G13 | CU-104 Registrar funcionario | Administrador | `/administracion/funcionarios/nuevo/` | Caso nuevo: sin código propio en el plan de pruebas |
| G13 | CU-105 Consultar funcionarios | Administrador | `/administracion/funcionarios/` | Caso nuevo: sin código propio en el plan de pruebas |
| G13 | CU-106 Modificar funcionario | Administrador | `/administracion/funcionarios/<id>/editar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G13 | CU-107 Eliminar funcionario | Administrador | `/administracion/funcionarios/<id>/eliminar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G14 | CU-112 Registrar elemento de catálogo | Coordinador, Administrador | `/administracion/catalogo/nuevo/` | Caso nuevo: sin código propio en el plan de pruebas |
| G14 | CU-113 Consultar elementos del catálogo | Coordinador, Administrador | `/administracion/catalogo/` | Caso nuevo: sin código propio en el plan de pruebas |
| G14 | CU-114 Modificar elemento de catálogo | Coordinador, Administrador | `/administracion/catalogo/<id>/editar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G14 | CU-115 Eliminar elemento de catálogo | Coordinador, Administrador | `/administracion/catalogo/<id>/eliminar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G15 | CU-117 Registrar período | Coordinador, Administrador | `/administracion/periodos/nuevo/` | Caso nuevo: sin código propio en el plan de pruebas |
| G15 | CU-118 Consultar períodos | Coordinador, Administrador | `/administracion/periodos/` | Caso nuevo: sin código propio en el plan de pruebas |
| G15 | CU-119 Modificar período | Coordinador, Administrador | `/administracion/periodos/<id>/editar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G15 | CU-120 Eliminar período | Coordinador, Administrador | `/administracion/periodos/<id>/eliminar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G15 | CU-28 Abrir, cerrar o reabrir período | Coordinador, Administrador | `/administracion/periodos/<id>/estado/<acción>/` | 12 unitarias y 26 de integración (aprobado) |
| G15 | CU-121 Registrar parámetro | Administrador | `/administracion/parametros/nuevo/` | Caso nuevo: sin código propio en el plan de pruebas |
| G15 | CU-122 Consultar parámetros | Coordinador, Administrador | `/administracion/parametros/` | Caso nuevo: sin código propio en el plan de pruebas |
| G15 | CU-25 Modificar parámetro | Coordinador, Administrador | `/administracion/parametros/<id>/editar/` | 12 unitarias y 26 de integración (aprobado) |
| G15 | CU-123 Eliminar parámetro | Administrador | `/administracion/parametros/<id>/eliminar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G16 | CU-04 Registrar ítem medible | Coordinador, Administrador | `/administracion/items/nuevo/` | 1 unitaria y 26 de integración (aprobado) |
| G16 | CU-128 Consultar ítems medibles | Coordinador, Administrador | `/administracion/items/` | Caso nuevo: sin código propio en el plan de pruebas |
| G16 | CU-129 Modificar ítem medible | Coordinador, Administrador | `/administracion/items/<id>/editar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G16 | CU-130 Eliminar ítem medible | Coordinador, Administrador | `/administracion/items/<id>/eliminar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G16 | CU-131 Cargar matriz de cargos | Administrador | comando cargar_matriz (servidor) | Caso nuevo: sin código propio en el plan de pruebas |
| G16 | CU-05 Registrar meta | Coordinador, Administrador | `/administracion/metas/nuevo/` | 1 unitaria y 15 de integración (aprobado) |
| G16 | CU-132 Consultar metas | Coordinador, Administrador | `/administracion/metas/` | Caso nuevo: sin código propio en el plan de pruebas |
| G16 | CU-133 Modificar meta | Coordinador, Administrador | `/administracion/metas/<id>/editar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G16 | CU-134 Eliminar meta | Coordinador, Administrador | `/administracion/metas/<id>/eliminar/` | Caso nuevo: sin código propio en el plan de pruebas |
| G17 | CU-06 Seguimiento de avance (ficha personal) | Usuario | `/gestion/mi-ficha/` | 19 unitarias y 14 de integración (aprobado) |
| G17 | CU-16 Consultar semáforo de cumplimiento | Usuario | `/gestion/semaforo/` | 4 unitarias y 10 de integración (aprobado) |
| G17 | CU-17 Comparar avance esperado y real | Usuario | `/gestion/` | 0 unitarias y 22 de integración (aprobado) |
| G17 | CU-18 Consultar resumen ejecutivo | Usuario | `/gestion/panel/ y /gestion/resumen/` | 6 unitarias y 10 de integración (aprobado) |
| G17 | CU-136 Consultar territorio y delegación | Usuario | `/territorio/ y /delegacion/<nombre>/` | Caso nuevo: sin código propio en el plan de pruebas |
| G17 | CU-31 Consultar alertas | Usuario | `/gestion/alertas/` | Historia sin pruebas propias en el plan |
| G18 | CU-20 Generar informe | Usuario | `/gestion/informes/` | 1 unitaria y 16 de integración (aprobado) |
| G19 | CU-30 Consultar auditoría de cambios | Administrador | `/administracion/auditoria/` | 8 unitarias y 16 de integración (aprobado) |
| G19 | CU-139 Consultar perfiles y permisos | Administrador | `/administracion/perfiles/` | Caso nuevo: sin código propio en el plan de pruebas |
