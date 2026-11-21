#!/usr/bin/env bash
# Respaldo diario de la base de datos del SGR (plan de mantención, mantención preventiva).
#
# Las credenciales NO van en este script: mysqldump las lee de ~/.my.cnf, que se crea una vez con
# chmod 600 y este contenido (la contraseña la escribe a mano el administrador del sistema):
#
#   [mysqldump]
#   user=gestion_user
#   password=<contraseña de la base>
#
# Retención: 7 respaldos diarios y 4 semanales (copia del domingo).
# Cron de ejemplo (crontab -e del usuario ec2-user), todos los días a las 02:30:
#
#   30 2 * * * /var/www/eva-backend-2/scripts/respaldo.sh >> /home/ec2-user/respaldos/respaldo.log 2>&1
#
# Restaurar (prueba mensual en una base de ensayo, nunca sobre la base en uso sin respaldo previo):
#   gunzip -c ARCHIVO.sql.gz | mysql gestion_laserena_prueba
set -euo pipefail

BASE="${SGR_BASE:-gestion_laserena}"
DESTINO="${SGR_RESPALDOS:-$HOME/respaldos}"
DIARIOS=7
SEMANALES=4

umask 077
mkdir -p "$DESTINO/diarios" "$DESTINO/semanales"
archivo="$DESTINO/diarios/${BASE}_$(date +%F).sql.gz"
temporal="$archivo.parcial"

# --no-tablespaces: el usuario de la aplicación no tiene el privilegio PROCESS y sin esta opción mysqldump falla.
# --single-transaction: copia consistente de las tablas InnoDB sin bloquear el sistema.
mysqldump --no-tablespaces --single-transaction --routines "$BASE" | gzip > "$temporal"

# mysqldump termina el archivo con «-- Dump completed»; si no está, el respaldo quedó incompleto.
if ! gunzip -c "$temporal" | tail -n 1 | grep -q 'Dump completed'; then
    rm -f "$temporal"
    echo "$(date '+%F %T') ERROR: el respaldo de $BASE quedó incompleto" >&2
    exit 1
fi
mv "$temporal" "$archivo"

if [ "$(date +%u)" = "7" ]; then
    cp "$archivo" "$DESTINO/semanales/"
fi

# Borra lo que excede la retención (los más antiguos primero).
ls -1t "$DESTINO"/diarios/*.sql.gz 2>/dev/null | tail -n +$((DIARIOS + 1)) | xargs -r rm -- || true
ls -1t "$DESTINO"/semanales/*.sql.gz 2>/dev/null | tail -n +$((SEMANALES + 1)) | xargs -r rm -- || true

echo "$(date '+%F %T') OK: $archivo ($(du -h "$archivo" | cut -f1))"
