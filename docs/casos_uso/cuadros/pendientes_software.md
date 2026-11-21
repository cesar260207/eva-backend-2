# Diferencias que el software debe cerrar

Los casos de uso se escribieron sobre proyecto-de-titulo-en-local (commit f4b3515), igual al main de eva-backend-2 (f910537). Estos 5 puntos eran ajustes al software que los cuadros anotaban. Su estado se revisó contra la rama feat/requerimientos-octubre de eva-backend-2.

| Punto | Casos afectados | Estado | Evidencia | Qué falta |
| --- | --- | --- | --- | --- |
| 1 | CU-67 Aplicar o rechazar ajuste | Resuelto | Commit 3c2aaef: botones «Aplicar» y «Rechazar» con confirmación en la lista de ajustes; pruebas en DecidirAjusteTests | Nada |
| 2 | CU-64, CU-71, CU-03 | Resuelto en parte | Commit 193eed5: el menú del usuario enlaza «Informar felicitación o reclamo» (CU-64) y «Registrar atención social» (CU-03); pruebas en AccesosOctubreTests | CU-71 Registrar ausencia: el botón va en el semáforo (tarea 7 del prompt) |
| 3 | CU-46 Rechazar por cierre semanal | Resuelto | Commit 791b9ac: el cierre semanal se aplica solo al registrar; una actividad rechazada antigua se corrige y vuelve a «pendiente» | Nada |
| 4 | CU-83 Importar organizaciones | Pendiente | Sin cambios | Asignar la delegación por territorio (tarea 10 del prompt) |
| 5 | Todos | Resuelto en parte | Según el grupo, el servidor AWS se actualizó a f910537 el 20 de noviembre de 2026 (migraciones 0021 a 0026, perfil «Profesional») | Desplegar la rama feat/requerimientos-octubre (migración 0027) |

Las notas de los cuadros de los puntos resueltos se quitaron de datos_v2.py. Siguen las de CU-71 Registrar ausencia, CU-83 Importar organizaciones y CU-131 Cargar matriz de cargos, que dependen de las tareas 7, 10 y 11.
