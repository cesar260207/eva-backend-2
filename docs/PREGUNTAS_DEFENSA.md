# Preguntas probables de la defensa

Respuestas cortas, basadas en el código, con el archivo donde se puede mostrar. Cada integrante debe defender su propia contribución: la sección final queda para que cada uno la complete.

## 1. ¿Por qué Django?

Porque trae resuelto lo que el SGR necesita y que sería riesgoso construir desde cero: autenticación con contraseñas cifradas, grupos y permisos (los cuatro perfiles), protección CSRF, un ORM que evita la inyección SQL y migraciones versionadas para cambiar la base de datos sin perder datos, como ocurrió con los requerimientos de octubre. Además, el equipo programa en Python y Django 5.2 es una versión LTS con soporte hasta abril de 2028.
**Dónde mostrarlo:** `gestion_laserena/settings.py`, `delegaciones_app/migrations/`.

## 2. ¿Por qué Scrum y no Cascada?

Por las condiciones del proyecto, no por preferencia: el plazo era de unos cuatro meses y Cascada exige cerrar cada etapa antes de la siguiente; además los requerimientos cambiaron (entrevistas y reunión de octubre), lo que un modelo secuencial no absorbe. Incremental tampoco calzaba, porque planifica entregas largas y el municipio necesitaba ver avances para validar las reglas. Se usó Scrum adaptado (sprints de 3 semanas según el informe) con prácticas de XP: pruebas automáticas, integración por pull request y revisión.
**Dónde mostrarlo:** [DEMO_EXPOSICION.md](DEMO_EXPOSICION.md) sección 5, [BACKLOG_SPRINT.md](BACKLOG_SPRINT.md).

## 3. ¿Por qué ese modelo de datos?

Parte de las 17 clases del diseño, que separan organización (delegación, cargo, funcionario, rol), medición (período, ítem, meta, indicador) y operación (actividad, evidencia, validación, tarea). Las reglas viven en los modelos (`clean`), así valen igual desde las pantallas, los mantenedores y los comandos. Octubre agregó cinco modelos con un motivo cada uno; por ejemplo, Ausencia es una tabla propia y no un campo del usuario porque una persona tiene varias ausencias con fechas y el cálculo necesita los días exactos.
**Dónde mostrarlo:** [MODELO_DATOS.md](../MODELO_DATOS.md), [DIAGRAMA_CLASES.md](DIAGRAMA_CLASES.md).

## 4. ¿Cómo se calcula el puntaje?

1. **Avance:** actividades aprobadas del ítem en el período, con validación aprobada y que puntúan (tienen contacto, no son gestión interna ni previa).
2. **Cumplimiento:** avance / meta × 100, con tope de 120 %, más 10 por felicitación aplicada (máximo 3) y menos 30 por reclamo aplicado, entre 0 y el tope.
3. **Ponderado:** ponderador del ítem × cumplimiento.
4. **Semáforo:** verde si alcanza lo esperado al día (días transcurridos sobre días totales, descontando ausencias), ámbar desde el 60 % de lo esperado, rojo bajo eso.

**Dónde mostrarlo:** `delegaciones_app/models.py` (`Indicador.calcular_avance`, `calcular_cumplimiento`), `delegaciones_app/reglas.py` (`evaluar_puntaje`, `porcentaje_esperado_ajustado`), `delegaciones_app/medicion.py:36` (`_semaforo`).

## 5. ¿Qué pasa si dos usuarios editan lo mismo?

Actividad y Compromiso tienen un campo `version`. Al guardar, si otro usuario guardó antes, la versión no coincide: el segundo recibe un aviso y debe recargar; no se pisan los cambios en silencio (control de concurrencia optimista, CU-23.1).
**Dónde mostrarlo:** `VersionOptimistaMixin` en `delegaciones_app/models.py`; pruebas de CU-23.1 en el plan de pruebas.

## 6. ¿Cómo se protege la contraseña?

Nunca se guarda en texto plano: Django la guarda con hash PBKDF2-SHA256 con sal. Hay validadores de largo, contraseñas comunes y similitud con el usuario. La recuperación usa un enlace de un solo uso que vence en 1 hora. Las claves del servidor están en `.env`, que no se sube a GitHub. Lo pendiente es HTTPS: hoy la contraseña viaja sin cifrar entre el navegador y el servidor.
**Dónde mostrarlo:** `gestion_laserena/settings.py:123` y `:179`; captura del campo `password` (`pbkdf2_sha256$…`).

## 7. ¿Qué pasa si se cae el servidor?

Hay una sola instancia EC2, sin alta disponibilidad. Los datos se protegen con el respaldo diario (`scripts/respaldo.sh`, 7 diarios y 4 semanales; objetivo RPO de 24 horas y RTO de 4 horas). Si se pierde la instancia, se crea otra con la guía del README, se clona el repositorio y se restaura el último respaldo. Si solo se cae Gunicorn, hoy hay que reiniciarlo a mano (`sudo systemctl restart gunicorn`): la unidad de systemd del README no tiene `Restart=on-failure`, y agregarlo está en el plan de mantención.
**Dónde mostrarlo:** [PLAN_MANTENCION.md](PLAN_MANTENCION.md) secciones 3 y 4.

## 8. ¿Cómo se adaptaron a los requerimientos de octubre?

Sin alargar el sprint: se agruparon las reglas, se formalizaron como RF y RNF con su prueba, se ajustaron los casos de uso y el diagrama de clases, se crearon las tareas y se repriorizó el backlog por valor para el municipio (primero lo que cambia el puntaje). Lo que no cabía (HTTPS, vista global por cargos) se postergó.
**Dónde mostrarlo:** [REQUERIMIENTOS_V2.md](REQUERIMIENTOS_V2.md), [BACKLOG_SPRINT.md](BACKLOG_SPRINT.md), historial de commits de la rama `feat/requerimientos-octubre`.

## 9. ¿Qué falta?

HTTPS con dominio municipal, alarmas de monitoreo, copia de respaldos fuera del servidor, límite de intentos de inicio de sesión y las respuestas del municipio a las preguntas pendientes (tope 150 % o 120 %, reclamo -20 % o -30 %, confirmar el ítem «Pendientes en tubo» que completa «Planificación y control»).
**Dónde mostrarlo:** README, «Preguntas pendientes para el municipio»; [PLAN_MANTENCION.md](PLAN_MANTENCION.md) sección 6.

## 10. ¿Cómo evitan que un funcionario vea datos de otra delegación?

Cada vista exige sesión y el permiso de su perfil, y las consultas se filtran por la delegación del usuario salvo para Coordinador y Administrador. Un acceso fuera del ámbito responde «no encontrado» y queda en la auditoría. Una prueba automática entra con los cuatro perfiles a 46 pantallas y comprueba que solo responden a los actores de cada caso de uso (184 de 184).
**Dónde mostrarlo:** `delegaciones_app/permisos.py`, `delegaciones_app/test_casos_de_uso.py`.

## 11. ¿Cómo saben que el sistema funciona?

Con más de 670 pruebas automáticas unitarias y de integración. Cada prueba declara en su docstring el caso de uso y el requerimiento que verifica, y `python manage.py plan_pruebas` genera el plan con el resultado de cada una. GitHub Actions las ejecuta en cada pull request. La cobertura medida está en [RESULTADOS.md](RESULTADOS.md).
**Dónde mostrarlo:** [PLAN_DE_PRUEBAS.md](../PLAN_DE_PRUEBAS.md), `.github/workflows/pruebas.yml`.

## 12. ¿Por qué el cierre semanal se aplica solo al registrar?

La regla 4 habla de «ingresos»: no se pueden ingresar gestiones de la semana pasada. Si también se aplicara al editar, una actividad rechazada hace dos semanas no se podría corregir ni volver a revisión, y quedaría perdida. Ese error existía y se corrigió con una prueba que lo demuestra.
**Dónde mostrarlo:** `delegaciones_app/reglas.py:25`, `delegaciones_app/models.py:290`, commit 791b9ac.

## 13. ¿Cómo se asegura que la evidencia respalde la gestión?

La evidencia solo la sube el autor; la revisa otra persona (nadie revisa su propio trabajo); rechazar exige motivo; solo lo aprobado suma; los archivos son JPG, PNG o PDF de hasta 5 MB y se entregan solo por una vista que revisa permisos, no por una carpeta pública.
**Dónde mostrarlo:** `delegaciones_app/forms.py:387`, `delegaciones_app/views.py` (`revisar_actividad`, `evidencia_archivo`).

## 14. ¿Qué hicieron con los datos personales que entregó el municipio?

Los Excel y Word del cliente están en `.gitignore` y no se suben; la matriz se convierte a JSON sin nombres de personas, y una prueba lo verifica. Un Excel con domicilios llegó al historial con el pull request #16; se sacó de las versiones nuevas, pero sigue en el historial de dos repositorios que hoy son públicos. Como grupo identificamos esta falencia y la corregimos dejando los repositorios privados o limpiando el historial [COMPLETAR POR EL GRUPO: acción tomada y fecha].
**Dónde mostrarlo:** `.gitignore`, `delegaciones_app/test_unit_matriz.py`, [NORMATIVAS_Y_ESTANDARES.md](NORMATIVAS_Y_ESTANDARES.md).

## 15. ¿Cómo se despliega una versión nueva sin perder datos?

Respaldo previo (`mysqldump --no-tablespaces`), `git pull`, `pip install -r requirements.txt`, `migrate --plan` para ver qué migraciones se aplicarán, `migrate`, `collectstatic` y reinicio de Gunicorn. Las migraciones que tocan datos se documentan (qué filas cambian) y las nuevas se pueden revertir. Si algo falla, se vuelve al commit anterior y se restaura el respaldo.
**Dónde mostrarlo:** README, «Despliegue en AWS EC2»; [PLAN_MANTENCION.md](PLAN_MANTENCION.md) sección 3.

## Contribución de cada integrante

Cada integrante anota qué hizo, con al menos un commit, pull request o documento que lo respalde, y prepara la respuesta a «¿qué parte del sistema hiciste tú y cómo funciona?».

### Dante Fredes

[COMPLETAR POR EL GRUPO]

### César Aranda

[COMPLETAR POR EL GRUPO]

### Faride Luna

[COMPLETAR POR EL GRUPO]

### Vinzenz Lafferte

[COMPLETAR POR EL GRUPO]
