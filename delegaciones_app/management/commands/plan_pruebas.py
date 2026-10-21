import platform
import unittest
from io import StringIO
from pathlib import Path

import django
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection
from django.test.runner import DiscoverRunner
from django.utils import timezone

from delegaciones_app.plan_pruebas import construir_markdown, describir


class ResultadoPorPrueba(unittest.TextTestResult):
    """Guarda el resultado de cada prueba por su identificador, incluidas las fallas dentro de subTest."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resultados = {}

    def addSuccess(self, test):
        super().addSuccess(test)
        self.resultados.setdefault(test.id(), 'Aprobado')

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.resultados[test.id()] = 'Reprobado'

    def addError(self, test, err):
        super().addError(test, err)
        self.resultados[test.id()] = 'Error'

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.resultados[test.id()] = 'Omitida'

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            self.resultados[test.id()] = 'Reprobado'


def _pruebas(suite):
    for elemento in suite:
        if isinstance(elemento, unittest.TestSuite):
            yield from _pruebas(elemento)
        else:
            yield elemento


class Command(BaseCommand):
    help = 'Ejecuta las pruebas y genera PLAN_DE_PRUEBAS.md con la tabla CP, CU, RF, método de prueba y resultado.'

    def add_arguments(self, parser):
        parser.add_argument('--salida', default=str(Path(settings.BASE_DIR) / 'PLAN_DE_PRUEBAS.md'), help='Archivo Markdown de salida.')
        parser.add_argument('etiquetas', nargs='*', default=['delegaciones_app', 'gestion_app'], help='Aplicaciones o módulos de prueba a ejecutar.')

    def handle(self, *args, **opciones):
        runner = DiscoverRunner(verbosity=0, interactive=False)
        runner.setup_test_environment()
        suite = runner.build_suite(opciones['etiquetas'])
        pruebas = list(_pruebas(suite))
        self.stdout.write(f'Ejecutando {len(pruebas)} pruebas...')
        bases = runner.setup_databases()
        try:
            resultado = unittest.TextTestRunner(stream=StringIO(), resultclass=ResultadoPorPrueba, verbosity=0).run(suite)
        finally:
            runner.teardown_databases(bases)
            runner.teardown_test_environment()
        registros = []
        for prueba in pruebas:
            clase = type(prueba)
            metodo = prueba._testMethodName
            registro = describir(clase.__module__.rsplit('.', 1)[-1], clase.__name__, metodo, getattr(clase, metodo).__doc__, clase.__doc__)
            registro['resultado'] = resultado.resultados.get(prueba.id(), 'No ejecutada')
            registros.append(registro)
        entorno = {
            'fecha': f'{timezone.localdate():%d-%m-%Y}',
            'ambiente': f"Desarrollo, base de datos de pruebas ({connection.vendor})",
            'tecnologia': f'Python {platform.python_version()}, Django {django.get_version()}, unittest de Django',
        }
        salida = Path(opciones['salida'])
        salida.write_text(construir_markdown(registros, entorno), encoding='utf-8')
        aprobadas = sum(1 for r in registros if r['resultado'] == 'Aprobado')
        self.stdout.write(self.style.SUCCESS(f'{aprobadas} de {len(registros)} pruebas aprobadas. Plan escrito en {salida}.'))
        if aprobadas != len(registros):
            self.stdout.write(self.style.ERROR('Hay pruebas que no pasaron: revisa la sección 2 del plan.'))
