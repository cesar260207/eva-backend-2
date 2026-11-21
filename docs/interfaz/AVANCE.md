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
