# Avance del rediseño de la interfaz

Registro de cada fase del rediseño (rama `feat/interfaz-terracota`). Se agrega al final de cada fase, sin borrar lo anterior.

## Fase 0. Preparación (21-11-2026)

1. **Qué hicimos**
   - Creamos la rama `feat/interfaz-terracota` desde `main` actualizado (1263426; GitHub no tenía cambios nuevos).
   - Revisamos la configuración de Git: nombre y correo están configurados.
   - Medimos la línea base: `check` sin problemas y 681 pruebas aprobadas.
   - Pusimos al día la base local (migraciones 0027 y 0028), cargamos `seed_demo` y guardamos el resultado de `probe.py` (164 combinaciones) para compararlo al final.
   - Listamos dónde aparecen `estado_class`, los colores de Bootstrap, las alertas, `form.as_p` y los mensajes sobre permisos.
   - Registramos las referencias visuales.
2. **Archivos creados:** `docs/interfaz/LINEA_BASE.md`, `docs/interfaz/REFERENCIAS.md` y este archivo.
3. **Pruebas:** 681 en total, 681 aprobadas, 0 fallidas. Es la línea base.
4. **Qué mirar:** nada cambia en pantalla en esta fase.
5. **Límites:** ninguno en riesgo. La base local se respaldó antes de migrarla, fuera del repositorio.
6. **No verificado:** las referencias visuales (no hubo navegador en la sesión; quedan pendientes en `REFERENCIAS.md`) y las capturas «antes» (la lista está en `LINEA_BASE.md`; se pueden sacar desde `main` en cualquier momento).
7. **Commits:** `docs: línea base y referencias del rediseño de la interfaz`.

## Fase 1. Limpieza (21-11-2026)

1. **Qué hicimos**
   - «Administración» muestra solo las tarjetas que el perfil puede abrir (o agregar), sin «No disponible para tu perfil», sin «Sección 01…12» y con un subtítulo de una línea.
   - El encabezado de los paneles quedó con el kicker, el saludo y la delegación como etiqueta pequeña; sin descripción de permisos, sin la insignia oscura y sin «Roles: …».
   - Quitamos el bloque «Restringido para tu perfil» del Profesional y del Delegado; su grilla pasó de 3 a 2 columnas («Tus funciones» o «Tu delegación», y las alertas).
   - El panel del Coordinador lista sus mantenedores solo como enlaces, sin «crear · editar · eliminar» ni la nota de lo reservado.
   - La lista de un mantenedor ya no muestra «Solo lectura para tu perfil»; la ayuda menciona «Agregar» solo cuando se puede agregar.
   - Acortamos las introducciones de «Actividades», «Delegados», «Mantenedores» y «Perfiles».
   - Cambiamos la prueba permitida (regla 17) sin cambiar su nombre y agregamos `test_unit_interfaz.py`.
2. **Archivos cambiados:** `mantenedores.html`, `crud/lista.html`, `crud/perfiles.html`, `actividades.html`, `delegados.html`, `_panel_encabezado.html`, los 4 paneles, `test_integracion.py` (solo `test_indice_deshabilita_los_mantenedores_exclusivos_del_administrador`). **Creado:** `delegaciones_app/test_unit_interfaz.py`.
3. **Pruebas:** 686 en total (681 de la línea base y 5 nuevas), 686 aprobadas, 0 fallidas. Desde esta fase las corremos con `python manage.py test --parallel 6`: tardan 4 minutos en vez de 14 y dan el mismo resultado.
4. **Qué mirar:**
   - Como `funcionario.centro`, «Administración»: una sola tarjeta, «Organizaciones comunitarias», con «Abrir sección».
   - Como `coordinador.demo`, «Administración»: 10 tarjetas, ninguna gris.
   - El panel de cada perfil: el saludo y la delegación, sin textos sobre permisos.
5. **Límites:** todo se ocultó en las plantillas con las variables que ya entregan las vistas (`tarjeta.permitido`, `tarjeta.puede.add`, `puede.add`). No se tocaron vistas ni permisos.
6. **Mensajes de permisos adicionales:** el `grep` del encargo encontró uno más, en el ingreso («Usa tu cuenta para acceder a las funciones autorizadas por tu perfil y delegación.»), que la fase 2 reemplaza por el subtítulo que pide el encargo. Hay tres frases parecidas que no quitamos y quedan a decisión del grupo: «Ves solo los resultados de tu delegación» (`_filtros.html`), «dentro de tu ámbito» (`alertas.html`) y el bloque «Principio de acceso» (`institucional.html`).
7. **No verificado:** el aspecto en el navegador (sin navegador en la sesión).
8. **Commits:** `refactor: la interfaz muestra a cada perfil solo lo que puede hacer`; `test: pruebas de la limpieza de paneles y del índice de mantenedores`; `docs: avance de la fase 1 de la interfaz`.
