"""Mide el tiempo de respuesta de las páginas principales del SGR con el cliente de pruebas de Django.

Crea una base de datos de prueba en memoria (no toca la base real), carga seed_demo, entra con cada perfil y
promedia 20 llamadas por página. Escribe docs/resultados/tiempos_respuesta.csv.
Uso, desde la raíz del proyecto: python scripts/medir_tiempos.py
"""
import csv
import os
import statistics
import sys
import time
from io import StringIO
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_laserena.settings')
os.environ['DB_ENGINE'] = 'sqlite'

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.contrib.auth.models import User  # noqa: E402
from django.core.management import call_command  # noqa: E402
from django.db import connection  # noqa: E402
from django.test import Client  # noqa: E402
from django.test.utils import setup_test_environment  # noqa: E402
from django.urls import reverse  # noqa: E402

LLAMADAS = 20
# RNF-002 del informe: registro y consulta en 2 segundos como máximo; tableros consolidados, 5 segundos.
LIMITE_CONSULTA, LIMITE_TABLERO = 2000, 5000


def paginas():
    from delegaciones_app.models import Actividad

    actividad = Actividad.objects.order_by('pk').first().codigo_verificador
    return [
        ('Profesional', 'funcionario.centro', 'Panel del perfil', reverse('panel'), LIMITE_TABLERO),
        ('Profesional', 'funcionario.centro', 'Lista de actividades', reverse('actividades'), LIMITE_CONSULTA),
        ('Profesional', 'funcionario.centro', 'Formulario de actividad', reverse('actividad_nueva'), LIMITE_CONSULTA),
        ('Profesional', 'funcionario.centro', 'Detalle de actividad', reverse('actividad_detalle', args=[actividad]), LIMITE_CONSULTA),
        ('Profesional', 'funcionario.centro', 'Ficha personal', reverse('ficha_personal'), LIMITE_TABLERO),
        ('Delegado', 'delegado.demo', 'Semáforo', reverse('semaforo'), LIMITE_TABLERO),
        ('Delegado', 'delegado.demo', 'Tubo de trabajo', reverse('agenda'), LIMITE_CONSULTA),
        ('Coordinador', 'coordinador.demo', 'Cumplimiento general', reverse('dashboard'), LIMITE_TABLERO),
        ('Coordinador', 'coordinador.demo', 'Resumen por delegación', reverse('resumen'), LIMITE_TABLERO),
        ('Coordinador', 'coordinador.demo', 'Lista de ajustes', reverse('mantenedor_lista', args=['ajustes']), LIMITE_CONSULTA),
        ('Coordinador', 'coordinador.demo', 'Informes', reverse('informe'), LIMITE_TABLERO),
        ('Administrador', 'admin.demo', 'Consulta de auditoría', reverse('auditoria_consulta'), LIMITE_CONSULTA),
    ]


def main():
    setup_test_environment()
    settings.DEBUG = False
    nombre_original = connection.creation.create_test_db(verbosity=0, autoclobber=True)
    try:
        call_command('seed_demo', password='Clave-de-medicion-2026', stdout=StringIO())
        call_command('calcular_indicadores', stdout=StringIO())
        filas = []
        for perfil, usuario, pagina, url, limite in paginas():
            cliente = Client()
            cliente.force_login(User.objects.get(username=usuario))
            cliente.get(url)  # primera llamada fuera de la medición (carga de plantillas)
            tiempos = []
            for _ in range(LLAMADAS):
                inicio = time.perf_counter()
                respuesta = cliente.get(url)
                tiempos.append((time.perf_counter() - inicio) * 1000)
                assert respuesta.status_code == 200, (url, respuesta.status_code)
            promedio = statistics.mean(tiempos)
            filas.append({
                'perfil': perfil, 'pagina': pagina, 'url': url, 'llamadas': LLAMADAS,
                'promedio_ms': round(promedio, 1), 'maximo_ms': round(max(tiempos), 1), 'limite_rnf002_ms': limite,
                'cumple': 'sí' if promedio <= limite else 'no',
            })
            print(f'{pagina:<28} {promedio:8.1f} ms (máx {max(tiempos):7.1f})')
    finally:
        connection.creation.destroy_test_db(nombre_original, verbosity=0)
    salida = RAIZ / 'docs' / 'resultados' / 'tiempos_respuesta.csv'
    salida.parent.mkdir(parents=True, exist_ok=True)
    with salida.open('w', newline='', encoding='utf-8') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)
    print(f'Escrito {salida}')


if __name__ == '__main__':
    main()
