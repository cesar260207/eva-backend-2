# Diagrama de clases del SGR

Sacado de los modelos reales (`delegaciones_app/models.py`) después de los cambios de la rama `feat/requerimientos-octubre`. Muestra los atributos principales, los métodos de negocio y las relaciones con su cardinalidad. Las clases marcadas como **nuevas** (en otro color y con el estereotipo `octubre 2026`) son las que agregaron los requerimientos de octubre: Organizacion, Ajuste, Ausencia, CasoSocial y Comentario.

Se omiten los campos técnicos (id, fechas de creación) y la clase `FuncionarioRol`, que es la tabla intermedia de la relación muchos a muchos entre Funcionario y Rol.

```mermaid
classDiagram
    direction LR

    class Delegacion {
        nombre
        estado
        ambito
        enfasis
        set_estado(activa)
        promedio_ponderado(indicadores)
        obtener_cumplimiento_global()
    }
    class Cargo {
        nombre
        vigencia
        actualizar_ponderaciones()
    }
    class Rol {
        nombre_rol
    }
    class Funcionario {
        identificador_institucional
        nombre
        estado
        registrar_actividad(datos)
        subir_evidencia(actividad, archivo)
        reasignar_cargo(cargo)
    }
    class UsuarioMaestro {
        identificador_maestro
        nivel_dominio
        estado
    }
    class Periodo {
        nombre
        fecha_inicio
        fecha_termino
        estado
        umbral_minimo
        version_parametros
        iniciar_periodo()
        cerrar_periodo()
        reabrir_periodo(motivo)
        porcentaje_esperado(fecha)
        calcular_semaforo(cumplimiento, fecha)
        obtener_parametro(clave)
    }
    class ParametroVersionado {
        clave
        valor
        descripcion
    }
    class ItemMedible {
        nombre
        ponderacion
        tipo_calculo
    }
    class Meta {
        valor_objetivo
        unidad
        ponderador
        evaluar_progreso(avance)
        actividades_que_aportan(periodo)
    }
    class Indicador {
        avance
        cumplimiento
        ponderacion
        ajuste
        semaforo
        generar(meta)$
        recalcular(metas)$
        calcular_avance()
        calcular_cumplimiento()
        actualizar_semaforo(fecha)
    }
    class Catalogo {
        codigo
        nombre
        tipo
        activo
    }
    class Actividad {
        codigo_verificador
        fecha
        lugar
        contacto_nombre
        contacto_telefono
        tipo_accion
        gestion_interna
        cuenta_puntaje
        estado
        version
        generar_codigo_verificador()
        cambiar_estado(estado)
        anular_aprobacion(motivo)
        actualizar_indicadores()
    }
    class Evidencia {
        codigo_evidencia
        archivo_vinculo
        estado_revision
        enviar_a_revision()
    }
    class Validacion {
        decision
        observacion
        aprobar_evidencia()
        rechazar_evidencia(motivo)
        anular_evidencia(motivo)
    }
    class Compromiso {
        folio
        origen
        solicitante
        solicitante_telefono
        estado
        fecha_comprometida
        version
        set_estado(estado, autor)
        derivar_compromiso(responsable)
        actualizar_indicadores()
    }
    class HistorialCompromiso {
        estado_anterior
        estado_nuevo
        observacion
    }
    class MedicionDelegacion {
        cumplimiento
        meta
        fecha_datos
    }
    class Auditoria {
        evento
        entidad
        identificador_registro
        valor_anterior
        valor_nuevo
        registrar_evento(usuario, accion, entidad)$
    }
    class Organizacion {
        <<octubre 2026>>
        nombre
        tipo
        territorio
        verificada
        activa
    }
    class Ajuste {
        <<octubre 2026>>
        tipo
        origen
        emisor
        respaldo
        estado
        actualizar_indicadores()
    }
    class Ausencia {
        <<octubre 2026>>
        tipo
        desde
        hasta
        actualizar_indicadores()
    }
    class CasoSocial {
        <<octubre 2026>>
        nombre_usuario
        telefono_usuario
        etapa
        tipo
    }
    class Comentario {
        <<octubre 2026>>
        contenido
    }

    Delegacion "0..1" -- "0..*" Funcionario : pertenece
    Cargo "1" -- "0..*" Funcionario : ocupa
    Funcionario "0..*" -- "1..*" Rol : tiene
    Periodo "1" *-- "0..*" ParametroVersionado : versiona
    Cargo "1" -- "0..*" ItemMedible : mide
    Periodo "1" -- "0..*" ItemMedible : vigente en
    ItemMedible "1" -- "0..*" Meta : define
    Funcionario "1" -- "0..*" Meta : asignada a
    Meta "1" -- "0..*" Indicador : se calcula en
    Funcionario "1" -- "0..*" Actividad : registra
    Delegacion "1" -- "0..*" Actividad : ocurre en
    ItemMedible "1" -- "0..*" Actividad : aporta a
    Catalogo "0..1" -- "0..*" Actividad : clasifica
    Actividad "1" *-- "0..*" Evidencia : respalda
    Evidencia "1" -- "0..*" Validacion : se decide en
    Delegacion "1" -- "0..*" Compromiso : tubo de trabajo
    Funcionario "1" -- "0..*" Compromiso : responsable
    Compromiso "0..1" -- "0..*" Actividad : vincula
    Compromiso "1" *-- "1..*" HistorialCompromiso : registra
    Delegacion "1" -- "0..*" MedicionDelegacion : historico
    Funcionario "0..1" -- "0..*" Auditoria : autor
    UsuarioMaestro "0..1" -- "0..*" Auditoria : autor

    Delegacion "0..1" -- "0..*" Organizacion : agrupa
    Organizacion "0..1" -- "0..*" Actividad : atendida en
    Organizacion "0..1" -- "0..*" Compromiso : solicita
    Funcionario "0..1" -- "0..*" Ajuste : destinatario
    Delegacion "0..1" -- "0..*" Ajuste : destinataria
    Periodo "1" -- "0..*" Ajuste : aplica en
    Funcionario "1" -- "0..*" Ausencia : ausente
    Periodo "1" -- "0..*" Ausencia : descuenta en
    Funcionario "1" -- "0..*" CasoSocial : atiende
    Actividad "0..1" *-- "0..*" Comentario : comentada
    Compromiso "0..1" *-- "0..*" Comentario : comentada
    Funcionario "1" -- "0..*" Comentario : escribe

    classDef nuevo fill:#fde8e6,stroke:#8E2B24,stroke-width:2px
    class Organizacion:::nuevo
    class Ajuste:::nuevo
    class Ausencia:::nuevo
    class CasoSocial:::nuevo
    class Comentario:::nuevo
```

## Qué cambió en el diseño por los requerimientos de octubre

| Clase | Qué agrega | Regla de octubre |
| --- | --- | --- |
| Organizacion | Las organizaciones comunitarias con su tipo y delegación; la actividad y la tarea pueden indicar a cuál atendieron | Tipos de organización |
| Ajuste | Felicitaciones y reclamos con respaldo, informados por el delegado y aplicados por la coordinación | Regla 8 |
| Ausencia | Días que no se trabajaron, descontados de lo esperado al día | Regla 9 |
| CasoSocial | Atención social por etapas, hasta tres gestiones por usuario | Área social (RF-015) |
| Comentario | Observaciones sobre una actividad o una tarea | RF-035 |

También cambiaron clases existentes:

- **Actividad:** `tipo_accion` (gestión previa), `gestion_interna` y `cuenta_puntaje` con `motivo_sin_puntaje` (reglas 1, 2 y 5).
- **ItemMedible:** `tipo_calculo` («actividades» o «tubo»).
- **Compromiso:** `item`, `solicitante_telefono`, `organizacion` y `gestion_interna` (regla 1 e ítem del tubo).
- **Indicador:** `ajuste` y el método `recalcular`, que usan Ajuste, Ausencia y Compromiso para mantener el semáforo al día.
- **ParametroVersionado:** guarda las claves de las reglas: `maximo_cumplimiento`, `max_ingresos_diarios`, `valor_felicitacion`, `max_felicitaciones` y `valor_reclamo`.

La justificación de cada clase nueva está en [MODELO_DATOS.md](../MODELO_DATOS.md).
