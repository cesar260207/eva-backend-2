# Plan de mantención del SGR

Define cómo se mantiene el Sistema de Gestión de Resultados (SGR) de la Municipalidad de La Serena una vez en operación: quién lo hace, con qué frecuencia, con qué herramientas y con qué recursos. Se organiza por tipo de mantención (correctiva, preventiva, adaptativa y perfectiva) y termina con el calendario consolidado.

## 1. Sistema que se mantiene

| Componente | Versión o detalle | Dónde está definido |
| --- | --- | --- |
| Servidor | AWS EC2, Amazon Linux 2023, IP elástica 3.225.119.192, usuario `ec2-user` | README, «Despliegue en AWS EC2» |
| Aplicación | Django 5.2 (LTS) con Python 3.14, servida por Gunicorn (systemd) detrás de Nginx | `requirements.txt`, README secciones 7 y 8 |
| Base de datos | MySQL 8.4, base `gestion_laserena`, usuario `gestion_user` | README sección 5 |
| Código | Repositorio `cesar260207/eva-backend-2` en GitHub, rama `main` | |
| Archivos de evidencia | Carpeta `media/` del servidor, entregados solo por la vista con permisos | `delegaciones_app/views.py` (evidencia_archivo) |
| Configuración sensible | Archivo `.env` en el servidor (nunca en GitHub) | `.env.example` |

**Vigencia de Django 5.2.** Es una versión LTS publicada en abril de 2025, con parches de seguridad hasta abril de 2028. El plan anual (sección 7) incluye preparar el paso a la siguiente LTS antes de esa fecha.

## 2. Roles

Los roles están pensados para la Municipalidad; una misma persona puede cumplir más de uno.

| Rol | Quién (propuesta) | Responsabilidades en la mantención |
| --- | --- | --- |
| Administrador del sistema | Técnico o analista de la unidad de informática municipal (jornada parcial) | Servidor, respaldos, actualizaciones del sistema operativo, despliegues, revisión de logs y monitoreo |
| Soporte funcional | Coordinador SGR (perfil Coordinador) | Primer contacto de los usuarios, clasifica los errores, abre y cierra períodos, carga metas y parámetros, prueba las correcciones antes de su paso a producción |
| Desarrollador de mantención | Analista programador interno o contratado por horas | Corrige errores, implementa cambios de reglas, mantiene las pruebas automáticas y las dependencias |
| Administrador funcional | Perfil Administrador del SGR | Usuarios, perfiles, delegaciones y catálogos; revisa la auditoría |
| Usuarios clave | Delegados de las seis delegaciones | Informan errores de su delegación y validan los cambios que les afectan |

## 3. Mantención correctiva

Corrige errores del sistema en operación.

### Cómo se reporta un error

Cada error se registra como un *issue* en GitHub (repositorio del SGR) con esta plantilla. Si el usuario no tiene cuenta de GitHub, lo reporta al Coordinador SGR, que abre el *issue*.

```markdown
**Pantalla o URL:** (por ejemplo /actividad/nueva/)
**Perfil y usuario:** (Profesional, funcionario.centro)
**Qué se hizo:** pasos para repetir el error
**Qué se esperaba / qué pasó:**
**Severidad:** crítica | alta | media | baja
**Captura o mensaje de error:** (sin datos personales de vecinos)
```

### Severidad y tiempos de respuesta

| Severidad | Ejemplo | Primera respuesta | Solución o alternativa |
| --- | --- | --- | --- |
| Crítica | El sistema no responde, no se puede iniciar sesión, pérdida o exposición de datos | 2 horas hábiles | 1 día hábil |
| Alta | No se puede registrar actividades o aprobar evidencias; el puntaje se calcula mal | 1 día hábil | 3 días hábiles |
| Media | Un informe o filtro falla, hay una alternativa manual | 3 días hábiles | Próxima versión (máximo 2 semanas) |
| Baja | Textos, estética, mejoras menores | 5 días hábiles | Se prioriza en el backlog |

### Flujo de una corrección

1. **Rama:** el desarrollador crea `fix/<descripción>` desde `main`.
2. **Prueba primero:** agrega una prueba automática que reproduce el error (falla antes de corregir).
3. **Corrección y pull request:** el pull request enlaza el *issue*. GitHub Actions (`.github/workflows/pruebas.yml`) ejecuta `python manage.py check`, revisa que no falten migraciones y corre todas las pruebas; si algo falla, no se une.
4. **Revisión:** otro integrante o el Coordinador SGR revisa el cambio y lo prueba con los usuarios de demostración.
5. **Despliegue:** respaldo previo (sección 4), `git pull`, `pip install -r requirements.txt`, `python manage.py migrate --plan` y `migrate`, `collectstatic --noinput` y `sudo systemctl restart gunicorn`.
6. **Rollback:** si el sistema falla después del despliegue, se vuelve al commit anterior (`git checkout <commit>`), se restaura el respaldo de la base tomado en el paso 5 si hubo migraciones (`gunzip -c respaldo.sql.gz | mysql gestion_laserena`) y se reinicia Gunicorn. El *issue* queda abierto con lo aprendido.

## 4. Mantención preventiva

Evita que los problemas ocurran.

### Respaldo de la base de datos

- **Script:** [`scripts/respaldo.sh`](../scripts/respaldo.sh). Ejecuta `mysqldump --no-tablespaces --single-transaction` (sin `--no-tablespaces` falla por permisos del usuario de la aplicación), comprime el resultado y verifica que termine en «Dump completed».
- **Credenciales:** el script no guarda contraseñas; las lee de `~/.my.cnf` del usuario `ec2-user`, creado con `chmod 600`.
- **Frecuencia:** diaria, a las 02:30, con cron: `30 2 * * * /var/www/eva-backend-2/scripts/respaldo.sh >> /home/ec2-user/respaldos/respaldo.log 2>&1`.
- **Retención:** 7 respaldos diarios y 4 semanales (copia del domingo). Con la base actual, cada respaldo comprimido pesa pocos megabytes.
- **Copia fuera del servidor:** semanal, a un bucket S3 privado o al almacenamiento institucional, para no perder los respaldos si se pierde la instancia (pendiente de habilitar; sección 6).
- **Prueba de restauración:** mensual. Se restaura el último respaldo en una base de prueba (`gestion_laserena_prueba`) y se revisa que el conteo de actividades y usuarios coincida con producción. Se registra el resultado en el *issue* mensual de mantención.
- **Objetivo:** RPO de 24 horas y RTO de 4 horas (RNF-010 del informe).

### Actualizaciones de seguridad

| Qué | Cómo | Frecuencia |
| --- | --- | --- |
| Sistema operativo y paquetes (Nginx, MySQL, PHP-FPM de phpMyAdmin) | `sudo dnf upgrade --security` y luego `sudo dnf upgrade`, como se hizo con PHP-FPM; reiniciar los servicios afectados | Mensual, o el mismo día ante un aviso crítico |
| Dependencias de Python | `pip list --outdated` y `pip-audit` (en el entorno virtual) | Mensual |
| Parches de Django 5.2 | Actualizar a la última 5.2.x dentro del rango de `requirements.txt` y correr las pruebas | Al publicarse un parche de seguridad |

### Revisión de operación

| Qué | Comando o herramienta | Frecuencia |
| --- | --- | --- |
| Errores de la aplicación | `sudo journalctl -u gunicorn --since "1 day ago"` | Diaria (5 minutos) |
| Errores de Nginx | `sudo tail -n 200 /var/log/nginx/error.log` | Semanal |
| Espacio en disco | `df -h` y `du -sh /var/www/eva-backend-2/media ~/respaldos` (alerta sobre 80 %) | Semanal |
| Respaldos | `tail ~/respaldos/respaldo.log` (debe decir «OK» cada día) | Semanal |
| Servicios | `systemctl status gunicorn nginx mysqld` | Semanal |
| Sesiones vencidas | `python manage.py clearsessions` (borra de la base las sesiones ya vencidas); en cron: `0 3 * * 0 cd /var/www/eva-backend-2 && venv/bin/python manage.py clearsessions` | Semanal |
| Reinicio automático de Gunicorn | Agregar `Restart=on-failure` y `RestartSec=5` en la sección `[Service]` de `/etc/systemd/system/gunicorn.service` (la unidad del README no lo tiene), luego `sudo systemctl daemon-reload` | Una vez, en el próximo despliegue |
| Accesos denegados | Consulta de auditoría filtrando «acceso_denegado» en el SGR | Mensual |

## 5. Mantención adaptativa

Adapta el sistema a cambios del entorno, en especial a cambios de reglas del municipio como los de octubre de 2026.

1. **Parámetros sin tocar código.** El tope de cumplimiento, el valor de felicitaciones y reclamos, el máximo de felicitaciones y el máximo de ingresos diarios son parámetros versionados de cada período (mantenedor «Parámetros del período»). Si el municipio confirma, por ejemplo, un tope de 150 % o un reclamo de -20 %, el Coordinador lo cambia sin desplegar código.
2. **Cambios de reglas que sí requieren código.** Se sigue el proceso aplicado con los requerimientos de octubre: nueva versión del documento de requerimientos ([REQUERIMIENTOS_V2.md](REQUERIMIENTOS_V2.md)), casos de uso ajustados, repriorización del backlog ([BACKLOG_SPRINT.md](BACKLOG_SPRINT.md)), pruebas de cada regla y despliegue con el flujo de la sección 3.
3. **Migraciones con respaldo previo.** Antes de cada `migrate` se ejecuta `scripts/respaldo.sh` a mano y se revisa `migrate --plan`. Las migraciones que tocan datos se documentan en el README (qué filas cambian).
4. **Cierre y apertura de períodos trimestrales.** Al final de cada trimestre el Coordinador: (a) revisa que no queden evidencias pendientes; (b) cierra el período (los indicadores quedan congelados); (c) crea el período siguiente; (d) carga la matriz de cargos con `python manage.py cargar_matriz data/matriz_cargos.json --periodo "<nombre>"`; (e) ingresa las metas de cada funcionario; (f) inicia el período, que exige que las ponderaciones de cada cargo sumen 100 %.
5. **Datos nuevos del municipio.** La base de organizaciones se actualiza con `importar_organizaciones` desde un Excel copiado al servidor por `scp` (nunca por GitHub); las que quedan sin delegación se asignan a mano en el mantenedor.

## 6. Mantención perfectiva o evolutiva

Mejoras pendientes, ordenadas por prioridad.

| Mejora | Por qué | Esfuerzo estimado | Prioridad |
| --- | --- | --- | --- |
| HTTPS con dominio municipal y certificado (Let's Encrypt con certbot en Nginx) | Hoy el acceso es por http: las contraseñas viajan sin cifrar (RNF-006, OWASP A04) | 4 horas más el trámite del dominio | Alta |
| Pruebas automáticas en cada pull request | Ya está el workflow `.github/workflows/pruebas.yml`; falta exigirlo como regla de protección de `main` en GitHub | 1 hora | Alta |
| Copia de respaldos fuera del servidor (S3) | Un respaldo dentro de la misma instancia se pierde con ella | 3 horas | Alta |
| Monitoreo con alarmas de CloudWatch | Avisar por correo si la CPU supera 80 %, si la instancia falla su revisión de estado o si el disco se llena (RNF-018) | 3 horas | Media |
| Escalar: instancia más grande o base de datos en Amazon RDS | Si crecen los usuarios o el volumen de evidencias; RDS agrega respaldos automáticos | 1 día | Baja (cuando haga falta) |
| Funcionalidades postergadas del backlog | Vista global por cargos (RF-031), actividad reciente por funcionario (RF-030) | Según el backlog | Según el valor para el municipio |

## 7. Recursos

### Costo mensual aproximado de AWS

Valores de referencia de la región us-east-1, con precios de lista; el tipo de instancia exacto se confirma en la consola de AWS ([CONFIRMAR POR EL GRUPO]).

| Recurso | Supuesto | Costo aproximado (USD/mes) |
| --- | --- | --- |
| Instancia EC2 | 2 vCPU y 2 GB de RAM (t3.small, el mínimo del informe), encendida todo el mes | 15 |
| Disco EBS | 20 GB gp3 | 2 |
| IP pública elástica | Cobro por dirección IPv4 pública | 4 |
| Copia de respaldos en S3 (pendiente) | Menos de 5 GB | Menos de 1 |
| CloudWatch (pendiente) | Métricas básicas y 3 alarmas | Menos de 1 |
| **Total** | | **Unos 22** |

### Horas de trabajo

| Tarea | Rol | Horas al mes |
| --- | --- | --- |
| Revisión diaria y semanal de operación | Administrador del sistema | 4 |
| Actualizaciones de seguridad y dependencias | Administrador del sistema y desarrollador | 3 |
| Prueba de restauración del respaldo | Administrador del sistema | 1 |
| Soporte funcional a usuarios | Coordinador SGR | 4 |
| Correcciones y cambios menores | Desarrollador de mantención | 8 (variable) |
| **Total mensual estimado** | | **20** |

En los meses de cierre de trimestre se suman unas 4 horas del Coordinador SGR para el cierre y la apertura de períodos.

### Herramientas

GitHub (código, *issues*, pull requests y Actions), AWS (EC2, y en el futuro S3 y CloudWatch), cron, `mysqldump`, `pip-audit`, `journalctl` y el propio SGR (auditoría y mantenedores).

## 8. Calendario

| Frecuencia | Actividad | Responsable |
| --- | --- | --- |
| Diaria | Respaldo automático a las 02:30 (cron) | Automático |
| Diaria | Revisar errores de Gunicorn (5 minutos) | Administrador del sistema |
| Semanal | Revisar log de respaldos, espacio en disco, estado de servicios y errores de Nginx | Administrador del sistema |
| Semanal | Copia del respaldo semanal fuera del servidor (cuando esté habilitada) | Administrador del sistema |
| Mensual | `dnf upgrade --security`, `pip list --outdated` y `pip-audit` | Administrador del sistema y desarrollador |
| Mensual | Prueba de restauración del respaldo en una base de prueba | Administrador del sistema |
| Mensual | Revisar accesos denegados en la auditoría | Administrador funcional |
| Trimestral | Cerrar el período, abrir el siguiente, cargar la matriz y las metas | Coordinador SGR |
| Trimestral | Revisar con el municipio los parámetros (tope, reclamos, felicitaciones) y las reglas nuevas | Coordinador SGR y desarrollador |
| Anual | Revisar la vigencia de Django y Python, y planificar el paso a la siguiente LTS antes de abril de 2028 | Desarrollador |
| Anual | Revisar roles, usuarios inactivos y permisos de cada perfil | Administrador funcional |
| Anual | Revisar costos de AWS y el tamaño de la instancia | Administrador del sistema |
