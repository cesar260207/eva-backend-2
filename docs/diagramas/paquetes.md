# Diagrama de paquetes

Reemplaza a la figura 37 del informe. Muestra los módulos reales del proyecto y sus dependencias. Los módulos nuevos o que cambiaron de responsabilidad por los requerimientos de octubre 2026 van en otro color: `reglas.py` (reglas 1 a 9 de octubre) y los comandos `importar_organizaciones`, `generar_matriz` y `cargar_matriz`.

```mermaid
flowchart TB
    subgraph proyecto["gestion_laserena (proyecto Django)"]
        settings["settings.py<br/>configuración desde .env"]
        urls_p["urls.py<br/>login, logout, recuperación"]
    end

    subgraph delegaciones["delegaciones_app"]
        vistas["views.py<br/>actividades, evidencias, tubo, ajustes, ausencias, atención social, comentarios"]
        crud["crud.py<br/>12 mantenedores"]
        auditoria_v["auditoria.py<br/>consulta de auditoría"]
        forms["forms.py<br/>formularios y validación"]
        permisos["permisos.py<br/>perfiles, roles y ámbito"]
        backends["backends.py<br/>autenticación por perfil"]
        modelos["models.py<br/>24 modelos y reglas de negocio"]
        reglas["reglas.py<br/>cierre semanal, tope diario, puntaje, ausencias"]
        medicion["medicion.py<br/>semáforo, ficha, resumen"]
        alertas["alertas.py"]
        informes["informes.py"]
        subgraph comandos["management/commands"]
            seed["seed_demo"]
            calcular["calcular_indicadores"]
            importar["importar_organizaciones"]
            generar["generar_matriz"]
            cargar["cargar_matriz"]
            plan["plan_pruebas"]
        end
    end

    subgraph gestion["gestion_app"]
        vistas_g["views.py<br/>panel, dashboard, semáforo, resumen, ficha, informes, alertas"]
    end

    plantillas["templates<br/>Django Templates y Bootstrap"]
    bd[("MySQL 8.4<br/>(SQLite en pruebas)")]
    excel[/"Excel del municipio<br/>(fuera de GitHub)"/]

    urls_p --> vistas
    urls_p --> vistas_g
    vistas --> forms
    vistas --> permisos
    crud --> permisos
    auditoria_v --> permisos
    vistas_g --> medicion
    vistas_g --> alertas
    vistas_g --> informes
    vistas_g --> permisos
    vistas --> plantillas
    vistas_g --> plantillas
    forms --> modelos
    medicion --> reglas
    alertas --> reglas
    modelos --> reglas
    medicion --> modelos
    informes --> modelos
    permisos --> modelos
    backends --> modelos
    seed --> modelos
    seed --> cargar
    seed --> importar
    calcular --> modelos
    importar --> modelos
    cargar --> modelos
    generar --> excel
    importar --> excel
    modelos --> bd
    settings --> bd

    classDef octubre fill:#fde8e6,stroke:#8E2B24,stroke-width:2px
    class reglas,importar,generar,cargar octubre
```

Solo `models.py` (y los comandos, a través de los modelos) accede a la base de datos mediante el ORM. `reglas.py` concentra las reglas de octubre para que las usen por igual el modelo (al guardar), la medición (lo esperado al día) y las alertas.
