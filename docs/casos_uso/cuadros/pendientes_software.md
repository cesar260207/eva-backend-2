# Diferencias que el software debe cerrar

Los casos de uso se escribieron sobre proyecto-de-titulo-en-local (commit f4b3515), igual al main de eva-backend-2 (f910537). Estos 5 puntos eran ajustes al software que los cuadros anotaban. Su estado se revisó contra la rama feat/requerimientos-octubre de eva-backend-2.

| Punto | Casos afectados | Estado | Evidencia | Qué falta |
| --- | --- | --- | --- | --- |
| 1 | CU-67 Aplicar o rechazar ajuste | Resuelto | Commit 3c2aaef: botones «Aplicar» y «Rechazar» con confirmación en la lista de ajustes; pruebas en DecidirAjusteTests | Nada |
| 2 | CU-64, CU-71, CU-03 | Resuelto | Commit 193eed5: el menú del usuario enlaza «Informar felicitación o reclamo» (CU-64) y «Registrar atención social» (CU-03); el semáforo muestra «Registrar ausencia» (CU-71) al Delegado; pruebas en AccesosOctubreTests y AusenciaDesdeSemaforoTests | Nada |
| 3 | CU-46 Rechazar por cierre semanal | Resuelto | Commit 791b9ac: el cierre semanal se aplica solo al registrar; una actividad rechazada antigua se corrige y vuelve a «pendiente» | Nada |
| 4 | CU-83 Importar organizaciones | Resuelto | Mapeo de territorios y clasificación por tipo: de 1.812 sin delegación a 24 (ALFALFARES y filas sin territorio, para asignar a mano); pruebas en ImportarOrganizacionesTests | Nada |
| 5 | Todos | Resuelto en parte | Según el grupo, el servidor AWS se actualizó a f910537 el 20 de noviembre de 2026 (migraciones 0021 a 0026, perfil «Profesional») | Desplegar la rama feat/requerimientos-octubre (migraciones 0027 y 0028) |

Las notas de los cuadros de los puntos resueltos se quitaron de datos_v2.py. CU-83 y CU-131 conservan una nota informativa (no son pantallas y reportan advertencias de los datos del municipio).
