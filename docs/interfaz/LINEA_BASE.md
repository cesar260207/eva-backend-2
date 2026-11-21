# Línea base antes del rediseño de la interfaz

Registro del estado del SGR el 21-11-2026, antes de tocar la interfaz. Sirve para comparar cada fase del rediseño (rama `feat/interfaz-terracota`, creada desde `main` en el commit 1263426).

## 1. Repositorio

- `main` en GitHub coincide con el local: 1263426 (PR #19, cierre de sesión por inactividad). No hubo cambios nuevos.
- Configuración de Git del equipo: nombre y correo configurados (no son los valores de ejemplo).

## 2. Pruebas

- `python manage.py check`: sin problemas («System check identified no issues»).
- `python manage.py test`: **681 pruebas, todas aprobadas** («Ran 681 tests in 866.346s», «OK»): unos 14 minutos en este equipo. Ninguna falla.

## 3. Combinaciones de perfil y pantalla (`probe.py`)

La base local estaba atrasada: le faltaban las migraciones 0027 y 0028. Antes de medir, respaldamos `db.sqlite3` fuera del repositorio, aplicamos las migraciones y corrimos `python manage.py seed_demo` (solo en local). Luego `python docs/casos_uso/fuente/probe.py .` recorrió 41 pantallas con los 4 perfiles demo: **164 combinaciones**. El resultado queda guardado fuera del repositorio para compararlo al final (fase 5).

## 4. Dónde aparecen las clases que cambian

| Búsqueda | Archivos |
| --- | --- |
| `estado_class` | `agenda.html`, `delegacion_detalle.html`, `delegados.html`, `solicitudes.html`, `dashboard.html` (4), `ficha.html` (2), `panel_administrador.html`, `panel_coordinador.html`, `panel_delegado.html`, `panel_funcionario.html`, `resumen.html` (2), `semaforo.html` (3) |
| `bg-{{ … }}` (color desde la vista) | `delegacion_detalle.html`, `delegados.html`, `solicitudes.html`, `_panel_alertas.html`, `alertas.html`, `dashboard.html`, `ficha.html` (2), los 4 paneles, `resumen.html`, `semaforo.html` (2) |
| `bg-danger`, `bg-success`, `bg-secondary`, `bg-dark` fijos | `crud/lista.html`, `dashboard.html`, `ficha.html`, `panel_delegado.html`, `panel_funcionario.html`, `_panel_encabezado.html` |
| `alert-danger`, `alert-warning`, `alert-info`, `alert-secondary` | `actividad_confirmar_eliminar.html`, `agenda.html`, `compromiso_confirmar_eliminar.html`, `delegacion_detalle.html`, `delegados.html`, `evidencia_subir.html`, `mantenedor_confirmar_eliminar.html` (2), `mantenedor_form.html`, `solicitudes.html`, `_filtros.html` (2), `ficha.html`, `semaforo.html` (`alert-{{ estado_class }}`) |
| `form.as_p` | `actividad_form.html`, `compromiso_form.html`, `registration/login.html` |

## 5. Mensajes sobre permisos

Los que el encargo ya identificó (punto 5):

| Archivo | Texto |
| --- | --- |
| `mantenedores.html` | «No disponible para tu perfil» en las tarjetas sin permiso |
| `_panel_encabezado.html` y los 4 paneles | «Permisos mínimos…», «Permisos intermedios…» y «Acceso total…» (parámetro `descripcion=`) |
| `panel_funcionario.html` y `panel_delegado.html` | Bloque «Restringido para tu perfil» |
| `panel_coordinador.html` | «Usuarios, roles, perfiles y auditoría quedan reservados al perfil Administrador.» |
| `crud/lista.html` | «Solo lectura para tu perfil» |

Encontrados además con `grep -ri "tu perfil\|restringid\|reservad\|permisos m\|permisos inter\|acceso total\|no disponible"`:

| Archivo | Texto | Qué hicimos |
| --- | --- | --- |
| `registration/login.html` | «Usa tu cuenta para acceder a las funciones autorizadas por tu perfil y delegación.» | Se reemplaza en la fase 2 por el subtítulo de una línea que pide el encargo («Municipalidad de La Serena») |

Otras frases parecidas que no calzan con el `grep` pero hablan del alcance del usuario, y que **no** quitamos sin confirmación del grupo: «Ves solo los resultados de tu delegación» (`_filtros.html`, aviso útil del filtro), «dentro de tu ámbito» (`alertas.html`) y «Principio de acceso» (`institucional.html`, contenido institucional).

## 6. Capturas antes del cambio

La sesión no tenía navegador. Como `main` no cambia hasta que el grupo una la rama, las capturas «antes» se pueden sacar en cualquier momento desde `main`:

1. Portada sin sesión.
2. Ingreso (`/login/`) y el ingreso con una contraseña incorrecta.
3. Panel de cada perfil: `admin.demo`, `coordinador.demo`, `delegado.demo` y `funcionario.centro`.
4. «Administración» como `funcionario.centro` y como `coordinador.demo`.
5. «Registrar actividad» con el teléfono `abc` (error).
6. «Subir evidencia» de una actividad.
7. «Resultados» > «Semáforo de avance».
