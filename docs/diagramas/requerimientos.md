# Diagrama de requerimientos

Reemplaza a las figuras 1 a 12 del informe. Sigue el modelo «Relación entre los artefactos»: cada épica se expresa como
una gestión «Gestionar X» (la misma de los casos de uso de alto nivel) y de ella cuelgan sus requerimientos
(«Debe permitir…»). Los requerimientos de octubre 2026 (RF-039 a RF-050) van en otro color. Generado desde
`docs/casos_uso/fuente/datos_v2.py` y `CATALOGO_RF` (`delegaciones_app/plan_pruebas.py`).

## G02 Gestionar actividades

Épica EP-01: Registro y gestión de actividades.

```mermaid
flowchart LR
    G02["<b>Gestionar actividades</b><br/>G02 · EP-01"]
    G02 --> R9["RF-009<br/>Debe permitir registrar actividades"]
    G02 --> R10["RF-010<br/>Debe permitir validar campos de actividad"]
    G02 --> R11["RF-011<br/>Debe permitir generar código verificador de evidencia"]
    G02 --> R34["RF-034<br/>Debe permitir trabajo simultáneo"]
    G02 --> R35["RF-035<br/>Debe permitir facilitar coordinación"]
    G02 --> R40["RF-040<br/>Debe permitir registrar la gestión interna como otra gestión"]
    class R40 octubre
    G02 --> R41["RF-041<br/>Debe permitir exigir nombre y teléfono del contacto para puntuar"]
    class R41 octubre
    G02 --> R42["RF-042<br/>Debe permitir limitar los ingresos diarios a 7"]
    class R42 octubre
    G02 --> R43["RF-043<br/>Debe permitir cerrar la semana de ingresos"]
    class R43 octubre
    G02 --> R44["RF-044<br/>Debe permitir registrar gestiones previas sin puntaje"]
    class R44 octubre
    classDef octubre fill:#fde8e6,stroke:#8E2B24,stroke-width:2px
```

## G03 Gestionar evidencias

Épica EP-03: Evidencias y verificación.

```mermaid
flowchart LR
    G03["<b>Gestionar evidencias</b><br/>G03 · EP-03"]
    G03 --> R12["RF-012<br/>Debe permitir asociar evidencia"]
    classDef octubre fill:#fde8e6,stroke:#8E2B24,stroke-width:2px
```

## G04 Validar actividades

Épica EP-03: Evidencias y verificación.

```mermaid
flowchart LR
    G04["<b>Validar actividades</b><br/>G04 · EP-03"]
    G04 --> R13["RF-013<br/>Debe permitir validar evidencia"]
    G04 --> R14["RF-014<br/>Debe permitir controlar puntuación por validación"]
    classDef octubre fill:#fde8e6,stroke:#8E2B24,stroke-width:2px
```

## G05 Gestionar tubo de trabajo

Épica EP-04: Agenda colectiva y compromisos.

```mermaid
flowchart LR
    G05["<b>Gestionar tubo de trabajo</b><br/>G05 · EP-04"]
    G05 --> R16["RF-016<br/>Debe permitir crear compromisos en agenda colectiva"]
    G05 --> R17["RF-017<br/>Debe permitir asignar compromiso"]
    G05 --> R18["RF-018<br/>Debe permitir gestionar estados"]
    G05 --> R19["RF-019<br/>Debe permitir controlar plazos"]
    G05 --> R20["RF-020<br/>Debe permitir relacionar agenda y medición"]
    G05 --> R50["RF-050<br/>Debe permitir calcular el ítem del tubo de trabajo"]
    class R50 octubre
    classDef octubre fill:#fde8e6,stroke:#8E2B24,stroke-width:2px
```

## G06 Gestionar ajustes de puntaje

Épica EP-02: Medición y desempeño.

```mermaid
flowchart LR
    G06["<b>Gestionar ajustes de puntaje</b><br/>G06 · EP-02"]
    G06 --> R25["RF-025<br/>Debe permitir aplicar incentivos y penalizaciones"]
    G06 --> R46["RF-046<br/>Debe permitir registrar felicitaciones y reclamos"]
    class R46 octubre
    classDef octubre fill:#fde8e6,stroke:#8E2B24,stroke-width:2px
```

## G07 Gestionar ausencias

Épica EP-02: Medición y desempeño.

```mermaid
flowchart LR
    G07["<b>Gestionar ausencias</b><br/>G07 · EP-02"]
    G07 --> R47["RF-047<br/>Debe permitir registrar ausencias desde el semáforo"]
    class R47 octubre
    classDef octubre fill:#fde8e6,stroke:#8E2B24,stroke-width:2px
```

## G08 Gestionar atenciones sociales

Épica EP-01: Registro y gestión de actividades.

```mermaid
flowchart LR
    G08["<b>Gestionar atenciones sociales</b><br/>G08 · EP-01"]
    G08 --> R15["RF-015<br/>Debe permitir registrar atención social por etapas"]
    classDef octubre fill:#fde8e6,stroke:#8E2B24,stroke-width:2px
```

## G09 Gestionar organizaciones comunitarias

Épica EP-01: Registro y gestión de actividades.

```mermaid
flowchart LR
    G09["<b>Gestionar organizaciones comunitarias</b><br/>G09 · EP-01"]
    G09 --> R39["RF-039<br/>Debe permitir importar organizaciones comunitarias con su delegación y tipo"]
    class R39 octubre
    classDef octubre fill:#fde8e6,stroke:#8E2B24,stroke-width:2px
```

## G10 Gestionar delegaciones

Épica EP-08: Administración, seguridad y trazabilidad.

```mermaid
flowchart LR
    G10["<b>Gestionar delegaciones</b><br/>G10 · EP-08"]
    G10 --> R1["RF-001<br/>Debe permitir administrar delegaciones"]
    classDef octubre fill:#fde8e6,stroke:#8E2B24,stroke-width:2px
```

## G11 Gestionar cargos

Épica EP-08: Administración, seguridad y trazabilidad.

```mermaid
flowchart LR
    G11["<b>Gestionar cargos</b><br/>G11 · EP-08"]
    G11 --> R3["RF-003<br/>Debe permitir configurar cargos y funciones"]
    classDef octubre fill:#fde8e6,stroke:#8E2B24,stroke-width:2px
```

## G13 Gestionar funcionarios y usuarios

Épica EP-08: Administración, seguridad y trazabilidad.

```mermaid
flowchart LR
    G13["<b>Gestionar funcionarios y usuarios</b><br/>G13 · EP-08"]
    G13 --> R2["RF-002<br/>Debe permitir administrar usuarios y roles"]
    classDef octubre fill:#fde8e6,stroke:#8E2B24,stroke-width:2px
```

## G14 Gestionar catálogo

Épica EP-08: Administración, seguridad y trazabilidad.

```mermaid
flowchart LR
    G14["<b>Gestionar catálogo</b><br/>G14 · EP-08"]
    G14 --> R4["RF-004<br/>Debe permitir mantener catálogo de actividades y servicios"]
    classDef octubre fill:#fde8e6,stroke:#8E2B24,stroke-width:2px
```

## G15 Gestionar períodos y parámetros

Épica EP-08: Administración, seguridad y trazabilidad.

```mermaid
flowchart LR
    G15["<b>Gestionar períodos y parámetros</b><br/>G15 · EP-08"]
    G15 --> R5["RF-005<br/>Debe permitir configurar períodos de medición"]
    G15 --> R38["RF-038<br/>Debe permitir versionar parámetros"]
    G15 --> R45["RF-045<br/>Debe permitir limitar el cumplimiento de cada ítem a 120 %"]
    class R45 octubre
    classDef octubre fill:#fde8e6,stroke:#8E2B24,stroke-width:2px
```

## G16 Gestionar ítems medibles y metas

Épica EP-02: Medición y desempeño.

```mermaid
flowchart LR
    G16["<b>Gestionar ítems medibles y metas</b><br/>G16 · EP-02"]
    G16 --> R6["RF-006<br/>Debe permitir configurar ponderaciones"]
    G16 --> R7["RF-007<br/>Debe permitir configurar metas y umbrales"]
    G16 --> R49["RF-049<br/>Debe permitir cargar la matriz de cargos"]
    class R49 octubre
    classDef octubre fill:#fde8e6,stroke:#8E2B24,stroke-width:2px
```

## G17 Consultar resultados

Épica EP-05: Monitoreo y control de gestión.

```mermaid
flowchart LR
    G17["<b>Consultar resultados</b><br/>G17 · EP-05"]
    G17 --> R8["RF-008<br/>Debe permitir presentar ficha personal"]
    G17 --> R21["RF-021<br/>Debe permitir generar resumen colectivo"]
    G17 --> R22["RF-022<br/>Debe permitir calcular avance actual"]
    G17 --> R23["RF-023<br/>Debe permitir calcular porcentaje de cumplimiento"]
    G17 --> R24["RF-024<br/>Debe permitir calcular cumplimiento ponderado"]
    G17 --> R26["RF-026<br/>Debe permitir calcular meta esperada al día"]
    G17 --> R27["RF-027<br/>Debe permitir mostrar semáforo de avance"]
    G17 --> R28["RF-028<br/>Debe permitir mostrar tablero personal"]
    G17 --> R29["RF-029<br/>Debe permitir mostrar tablero de delegación"]
    G17 --> R31["RF-031<br/>Debe permitir mostrar vista global por cargos"]
    G17 --> R37["RF-037<br/>Debe permitir emitir alertas"]
    G17 --> R48["RF-048<br/>Debe permitir mostrar el resultado del equipo"]
    class R48 octubre
    classDef octubre fill:#fde8e6,stroke:#8E2B24,stroke-width:2px
```

## G18 Generar informes

Épica EP-06: Reportabilidad y toma de decisiones.

```mermaid
flowchart LR
    G18["<b>Generar informes</b><br/>G18 · EP-06"]
    G18 --> R30["RF-030<br/>Debe permitir medir actividad reciente"]
    G18 --> R32["RF-032<br/>Debe permitir buscar y filtrar información"]
    G18 --> R33["RF-033<br/>Debe permitir generar y exportar informes"]
    classDef octubre fill:#fde8e6,stroke:#8E2B24,stroke-width:2px
```

## G19 Consultar auditoría y perfiles

Épica EP-08: Administración, seguridad y trazabilidad.

```mermaid
flowchart LR
    G19["<b>Consultar auditoría y perfiles</b><br/>G19 · EP-08"]
    G19 --> R36["RF-036<br/>Debe permitir mantener trazabilidad"]
    classDef octubre fill:#fde8e6,stroke:#8E2B24,stroke-width:2px
```
