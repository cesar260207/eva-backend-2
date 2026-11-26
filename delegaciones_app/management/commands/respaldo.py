"""Respaldo portable de la base de datos y de los archivos subidos (evidencias y respaldos de ajustes).

Funciona igual con MySQL y con SQLite, en Linux (EC2) y en Windows:

    python manage.py respaldo                      -> respaldos/sgr_AAAAMMDD_HHMMSS.zip
    python manage.py respaldo --destino /ruta      -> en otra carpeta
    python manage.py respaldo --conservar 7        -> borra los respaldos más antiguos y deja los 7 últimos

El .zip contiene datos.json (dumpdata de todas las tablas, sin tipos de contenido ni permisos, que recrea migrate) y la
carpeta media/. Para restaurar en una base vacía:

    python manage.py migrate
    python manage.py loaddata datos.json           (extraído del .zip)
    y copiar media/ dentro de MEDIA_ROOT.

Para MySQL en producción también existe scripts/respaldo.sh (mysqldump), que conserva el esquema exacto.
"""
import zipfile
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Genera un .zip con los datos (dumpdata) y los archivos subidos (media) para respaldo y recuperación.'

    def add_arguments(self, parser):
        parser.add_argument('--destino', default=str(Path(settings.BASE_DIR) / 'respaldos'), help='Carpeta donde se guarda el respaldo.')
        parser.add_argument('--conservar', type=int, default=0, help='Cantidad de respaldos a conservar (0 = todos).')

    def handle(self, *args, **opciones):
        destino = Path(opciones['destino'])
        destino.mkdir(parents=True, exist_ok=True)
        datos = StringIO()
        call_command('dumpdata', '--natural-foreign', '--natural-primary', '--indent', '1',
                     '--exclude', 'contenttypes', '--exclude', 'auth.permission', '--exclude', 'sessions', stdout=datos)
        archivo = destino / f'sgr_{timezone.localtime():%Y%m%d_%H%M%S}.zip'
        media = Path(settings.MEDIA_ROOT)
        total_archivos = 0
        with zipfile.ZipFile(archivo, 'w', compression=zipfile.ZIP_DEFLATED) as zip_respaldo:
            zip_respaldo.writestr('datos.json', datos.getvalue())
            if media.exists():
                for ruta in media.rglob('*'):
                    if ruta.is_file():
                        zip_respaldo.write(ruta, Path('media') / ruta.relative_to(media))
                        total_archivos += 1
        if opciones['conservar'] > 0:
            for antiguo in sorted(destino.glob('sgr_*.zip'))[:-opciones['conservar']]:
                antiguo.unlink()
        self.stdout.write(self.style.SUCCESS(f'Respaldo creado: {archivo} ({archivo.stat().st_size // 1024} KB, {total_archivos} archivo/s de media).'))
