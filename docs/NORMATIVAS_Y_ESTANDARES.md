# Normativas y estándares del SGR

Cada fila indica qué exige la norma o el estándar, cómo lo cumple el SGR (archivo y línea, o evidencia) y su estado: **cumple**, **parcial** o **pendiente**. Se marca «cumple» solo cuando el código o una prueba automática lo respalda. Revisado sobre la rama `feat/requerimientos-octubre` el 21 de noviembre de 2026.

## 1. Protección de datos personales

### Ley 19.628 sobre protección de la vida privada (vigente)

| Exigencia | Cómo la aborda el SGR | Evidencia | Estado |
| --- | --- | --- | --- |
| Tratar datos personales solo para la finalidad autorizada | Se registran solo los datos que exige la Matriz SGR: nombre y teléfono del contacto (regla 2 de octubre, para validar la gestión) y datos de la organización | `delegaciones_app/models.py` (Actividad, CasoSocial, Organizacion) | Cumple |
| Cuidar los datos con diligencia (seguridad) | Acceso con usuario y contraseña, permisos por perfil y por delegación, evidencias servidas solo por una vista con permisos (no por `/media/`) | `delegaciones_app/permisos.py:195`, `delegaciones_app/views.py` (evidencia_archivo), README sección 8 | Cumple |
| No exponer datos de terceros | Los archivos del municipio con datos personales no se suben a GitHub (`data/*.xlsx` y `docs/requerimientos/` en `.gitignore`); la matriz se versiona sin nombres de personas; los usuarios de demostración son ficticios | `.gitignore`, `data/matriz_cargos.json`, prueba `test_no_copia_los_nombres_de_personas_ni_las_gestiones` | Parcial: el Excel de organizaciones sigue en el historial de `main` (commit ffbb5e2); hay que dejar privados los repositorios o limpiar el historial |
| Opción de anonimizar | La importación de organizaciones puede reemplazar los domicilios por un texto neutro | `importar_organizaciones --anonimizar`, prueba `test_repetir_la_importacion_no_duplica_y_anonimiza_domicilios` | Cumple |

### Ley 21.719 de protección de datos personales

Publicada en diciembre de 2024, con vigencia programada para el 1 de diciembre de 2026. A fines de octubre de 2026 el Senado aprobó un proyecto que posterga su entrada en vigencia a 2027. **[CONFIRMAR ESTADO ANTES DE LA EXPOSICIÓN]**

| Exigencia | Cómo la aborda el SGR | Evidencia | Estado |
| --- | --- | --- | --- |
| Principio de minimización y finalidad | Igual que en la Ley 19.628: solo los datos que la matriz necesita | Modelos citados arriba | Cumple |
| Medidas de seguridad apropiadas | Control de acceso por perfil, contraseñas con hash, auditoría de solo lectura; falta cifrar las comunicaciones | Ver OWASP abajo | Parcial: falta HTTPS |
| Registro de las operaciones de tratamiento | La auditoría guarda quién creó, modificó, aprobó, exportó o intentó acceder sin permiso | `delegaciones_app/models.py:1110` (registrar_evento), CU-30 | Cumple |
| Plazos de conservación y eliminación | No hay una política de conservación definida para evidencias y contactos | | Pendiente: definirla con el municipio |
| Notificación de brechas | El plan de mantención define la severidad «crítica» para exposición de datos, pero no el aviso a la autoridad | [PLAN_MANTENCION.md](PLAN_MANTENCION.md) sección 3 | Pendiente |

## 2. OWASP Top 10 (versión 2025)

| Riesgo | Cómo lo aborda el SGR | Evidencia | Estado |
| --- | --- | --- | --- |
| A01 Control de acceso roto | Cada vista exige sesión y permiso del perfil; el Delegado y el Profesional ven solo su delegación; los intentos denegados responden 404 o vuelven al inicio y quedan en la auditoría | `delegaciones_app/permisos.py:175` y `:195`, `delegaciones_app/crud.py` (MantenedorMixin.dispatch); prueba `test_casos_de_uso.py`: 184 de 184 combinaciones de perfil y pantalla | Cumple |
| A02 Configuración de seguridad incorrecta | `DEBUG` falso por defecto, secretos en `.env`, cabeceras nosniff, referrer y X-Frame-Options; sin Django Admin publicado | `gestion_laserena/settings.py:34`, `:65` a `:67` | Parcial: sin HTTPS no se activan HSTS ni cookies `Secure` (`settings.py:64`) |
| A03 Fallas en la cadena de suministro de software | Dependencias con rango de versiones en `requirements.txt`; pruebas en GitHub Actions en cada pull request; revisión mensual con `pip-audit` | `requirements.txt`, `.github/workflows/pruebas.yml`, [PLAN_MANTENCION.md](PLAN_MANTENCION.md) sección 4 | Parcial: `pip-audit` todavía no se ejecuta de forma automática |
| A04 Fallas criptográficas | Contraseñas con hash PBKDF2-SHA256 de Django (nunca en texto plano); enlace de recuperación de un solo uso que vence en 1 hora | Hasher por defecto (no se cambia `PASSWORD_HASHERS`), `gestion_laserena/settings.py:179` | Parcial: sin HTTPS la contraseña viaja sin cifrar entre el navegador y el servidor |
| A05 Inyección | Todas las consultas usan el ORM de Django (no hay SQL escrito a mano en las aplicaciones); las plantillas escapan el HTML por defecto | Búsqueda de `raw(`, `execute(` y `extra(` en `delegaciones_app` y `gestion_app`: sin resultados | Cumple |
| A06 Diseño inseguro | Las reglas de negocio se validan en el modelo (`clean`), no solo en el formulario; nadie revisa su propio trabajo; el rechazo exige motivo | `delegaciones_app/models.py:270` (Actividad.clean), `delegaciones_app/forms.py:387` | Cumple |
| A07 Fallas de autenticación | Validadores de contraseña de Django; un funcionario desactivado pierde sus permisos; recuperación por correo con token | `gestion_laserena/settings.py:123`, `delegaciones_app/backends.py:7` | Parcial: no hay límite de intentos fallidos ni segundo factor |
| A08 Fallas de integridad de datos | Auditoría de solo inserción; control de concurrencia optimista (versión) en actividades y tareas; evidencias limitadas a JPG, PNG o PDF de hasta 5 MB | `delegaciones_app/models.py:1064` a `:1100`, VersionOptimistaMixin, `validar_tamano_evidencia` | Cumple |
| A09 Fallas en el registro y las alertas | Los eventos críticos y los accesos denegados quedan en la auditoría | CU-30, `registrar_acceso_denegado` en `delegaciones_app/permisos.py:150` | Parcial: no hay alertas automáticas (CloudWatch, pendiente en el plan de mantención) |
| A10 Mal manejo de condiciones excepcionales | Los errores de negocio (período cerrado, transición no permitida) se informan con un mensaje y no con un error 500 | `delegaciones_app/views.py` (ajuste_decidir, revisar_actividad, anular_actividad) | Parcial: no hay páginas propias para los errores 404 y 500 |

**HTTPS** queda como pendiente transversal: es la primera mejora del plan de mantención perfectiva ([PLAN_MANTENCION.md](PLAN_MANTENCION.md) sección 6).

## 3. ISO/IEC 25010 (modelo de calidad del producto)

| Característica | Evidencia en el SGR | Estado |
| --- | --- | --- |
| Adecuación funcional | Las 10 reglas de octubre implementadas o justificadas en [REQUERIMIENTOS_V2.md](REQUERIMIENTOS_V2.md); cada regla tiene su prueba automática | Cumple |
| Seguridad (confidencialidad, integridad, trazabilidad) | Perfiles y permisos, auditoría de solo lectura, contraseñas con hash; ver OWASP | Parcial: falta HTTPS |
| Usabilidad | Mensajes de error junto al campo, botones que solo aparecen a quien puede usarlos, confirmación antes de decidir un ajuste, nombres del dominio del municipio («tubo de trabajo», «tarea») | Cumple |
| Fiabilidad | Transacciones atómicas en las operaciones que tocan varias tablas, control de concurrencia, respaldo diario con verificación (`scripts/respaldo.sh`) | Parcial: el respaldo automático se activa en el servidor en el despliegue; falta la copia fuera del servidor |
| Mantenibilidad | Más de 650 pruebas automáticas, reglas de octubre como parámetros versionados, migraciones para cada cambio de base de datos, casos de uso comprobados por una prueba | Cumple |
| Eficiencia de desempeño | Tiempos de respuesta medidos frente al RNF-002 en [RESULTADOS.md](RESULTADOS.md) | Ver resultados |
| Portabilidad | Funciona con MySQL (servidor) y SQLite (pruebas y CI) con la misma configuración por `.env` | Cumple |

## 4. Estándares de modelado, código y accesibilidad

| Estándar | Qué exige | Cómo se aplica | Estado |
| --- | --- | --- | --- |
| UML 2.5 | Notación estándar de los diagramas | Casos de uso con actores, `<<include>>` y `<<extend>>` ([CASOS_DE_USO.md](CASOS_DE_USO.md)); diagrama de clases con multiplicidades ([DIAGRAMA_CLASES.md](DIAGRAMA_CLASES.md)) | Cumple |
| PEP 8 | Estilo de código Python (sangría de 4 espacios, nombres en minúscula con guion bajo) | Nombres y estructura siguen PEP 8; `models.py`, `reglas.py` y `test_integracion.py` usan tabuladores para la sangría | Parcial: falta unificar la sangría con espacios |
| Convenciones de Django | Aplicaciones, modelos, migraciones, plantillas y comandos en su lugar | Dos aplicaciones (`delegaciones_app`, `gestion_app`), comandos en `management/commands`, migraciones numeradas | Cumple |
| WCAG 2.1 (nivel básico) | Idioma de la página, enlace para saltar al contenido, etiquetas en formularios, contraste | `templates/base.html:3` (`lang="es"`), `:12` (enlace «Ir al contenido principal»), etiquetas `<label>` generadas por los formularios de Django, `aria-label` en el menú | Parcial: el contraste de colores no se ha medido con una herramienta |
