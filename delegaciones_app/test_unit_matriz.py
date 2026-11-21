"""Matriz SGR del municipio: generar_matriz la convierte a JSON sin nombres de personas y cargar_matriz crea los
cargos y sus ítems en un período. Las pruebas arman una planilla con la misma forma que la real."""
import json
import shutil
import tempfile
from datetime import date
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from openpyxl import Workbook

from .management.commands.generar_matriz import leer_hoja
from .models import Cargo, ItemMedible, ParametroVersionado, Periodo


def hoja_de_cargo(libro, titulo, alias, items, reclamo=-0.3):
    """Hoja como las de la matriz: alias de la persona en la fila 1, encabezado en la 2, ítems, totales y ajustes."""
    hoja = libro.create_sheet(titulo)
    hoja.append(['COD', alias, 'NOMBRE DEL CARGO', '(Cumplimiento Minimo 80%)'])
    hoja.append(['', 'ITEM', '', 'PONDERADOR', 'META TRIMESTRE', 'AVANCE ACTUAL META'])
    for nombre, ponderador, meta in items:
        hoja.append(['', nombre, '', ponderador, meta, 0])
    hoja.append(['', 'CUMPLIMIENTO TOTAL PONDERADO', '', 1, 100, 0])
    hoja.append(['', 'FELICITACIONES', 'MAX 3', 0.1, 3, 0])
    hoja.append(['', 'RECLAMOS', '', reclamo, 0, 0])
    hoja.append(['N°', 'FECHA', 'ACTIVIDAD', 'CONTACTO', 'TELEFONO'])
    hoja.append([1, '2026-07-01', 'Atención de prueba', 'Persona de prueba', '912345678'])
    return hoja


class GenerarMatrizTests(TestCase):
    """CU-131 Cargar matriz de cargos (RF-003, RF-006). La matriz se convierte a JSON sin nombres de personas."""

    def setUp(self):
        self.carpeta = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.carpeta, ignore_errors=True)
        libro = Workbook()
        libro.remove(libro.active)
        hoja_de_cargo(libro, 'AP ADM.', 'SUPERHEROE UNO', [('ATENCION DE USUARIO TELEFONO', 0.6, 240), ('SOLUCIONES DE INGRESOS AL TUBO', 0.4, 0.8)])
        hoja_de_cargo(libro, 'PLAN y CON', 'SUPERHEROE DOS', [('REUNION SEMANAL CON EL EQUIPO', 0.5, 12), ('EMERGENCIA', 0.35, 0)], reclamo=-0.2)
        self.excel = self.carpeta / 'matriz.xlsx'
        libro.save(self.excel)
        self.salida = self.carpeta / 'matriz_cargos.json'

    def _generar(self):
        salida = StringIO()
        call_command('generar_matriz', str(self.excel), salida=str(self.salida), stdout=salida)
        return json.loads(self.salida.read_text(encoding='utf-8')), salida.getvalue()

    def test_lee_items_ponderacion_meta_y_tipo_de_calculo(self):
        """CU-131 Cargar matriz de cargos (RF-003, RF-006). Ponderador 0,6 pasa a 60 %; el ítem del tubo es de tipo «tubo»."""
        datos, _ = self._generar()
        cargo = datos['cargos'][0]
        self.assertEqual(cargo['nombre'], 'Apoyo administrativo')
        self.assertEqual(cargo['items'], [
            {'nombre': 'Atencion de usuario telefono', 'ponderacion': 60.0, 'meta_trimestre': 240.0, 'tipo_calculo': 'actividades'},
            {'nombre': 'Soluciones de ingresos al tubo', 'ponderacion': 40.0, 'meta_trimestre': 0.8, 'tipo_calculo': 'tubo'},
        ])
        self.assertEqual((cargo['felicitacion'], cargo['reclamo']), (10.0, -30.0))

    def test_no_copia_los_nombres_de_personas_ni_las_gestiones(self):
        """CU-131 Cargar matriz de cargos (RNF de privacidad). El JSON no lleva el alias de la fila 1 ni los registros de gestiones."""
        _, _ = self._generar()
        texto = self.salida.read_text(encoding='utf-8')
        for dato in ('SUPERHEROE', 'Persona de prueba', '912345678'):
            self.assertNotIn(dato, texto)

    def test_advierte_las_ponderaciones_que_no_suman_100_y_los_reclamos_distintos(self):
        """CU-131 Cargar matriz de cargos (RF-006, RN-001). Las diferencias de la matriz quedan como advertencias."""
        datos, salida = self._generar()
        self.assertIn('«Planificación y control»: las ponderaciones suman 85 %, no 100 %.', datos['advertencias'])
        self.assertIn('El reclamo no vale lo mismo en todas las hojas: -30 %, -20 %.', datos['advertencias'])
        self.assertIn('Falta la hoja «COOR DISERCO» (Coordinador DISERCO).', salida)

    def test_una_hoja_sin_ponderador_es_un_error(self):
        """CU-131 Cargar matriz de cargos (RF-006). Una hoja con otra forma no se interpreta a ciegas."""
        with self.assertRaises(ValueError):
            leer_hoja([['sin', 'encabezado']], 'Cargo de prueba')


class CargarMatrizTests(TestCase):
    """CU-131 Cargar matriz de cargos (RF-003, RF-006, RF-038). cargar_matriz crea cargos e ítems y no pisa parámetros."""

    def setUp(self):
        self.carpeta = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.carpeta, ignore_errors=True)
        self.periodo = Periodo.objects.create(nombre='Trimestre de prueba', fecha_inicio=date(2026, 10, 1), fecha_termino=date(2026, 12, 31))
        self.archivo = self.carpeta / 'matriz_cargos.json'
        self.archivo.write_text(json.dumps({'cargos': [{'nombre': 'Gestor social 1', 'reclamo': -20.0, 'items': [
            {'nombre': 'Visita terreno', 'ponderacion': 60.0, 'meta_trimestre': 12.0, 'tipo_calculo': 'actividades'},
            {'nombre': 'Soluciones de ingresos al tubo', 'ponderacion': 40.0, 'meta_trimestre': 0.8, 'tipo_calculo': 'tubo'},
        ]}]}), encoding='utf-8')

    def _cargar(self):
        call_command('cargar_matriz', str(self.archivo), periodo='Trimestre de prueba', stdout=StringIO())

    def test_crea_el_cargo_y_sus_items_en_el_periodo(self):
        """CU-131 Cargar matriz de cargos (RF-003, RF-006). Los ítems quedan con su ponderación y tipo de cálculo."""
        self._cargar()
        items = ItemMedible.objects.filter(cargo__nombre='Gestor social 1', periodo=self.periodo).order_by('nombre')
        self.assertEqual([(i.nombre, i.ponderacion, i.tipo_calculo) for i in items], [
            ('Soluciones de ingresos al tubo', 40, 'tubo'), ('Visita terreno', 60, 'actividades'),
        ])

    def test_repetir_la_carga_no_duplica(self):
        """CU-131 Cargar matriz de cargos (RF-003). La carga se puede repetir sin duplicar cargos ni ítems."""
        self._cargar()
        self._cargar()
        self.assertEqual((Cargo.objects.filter(nombre='Gestor social 1').count(), ItemMedible.objects.count()), (1, 2))

    def test_deja_los_parametros_de_octubre_sin_pisar_los_existentes(self):
        """CU-25 Modificar parámetros (RF-038). Tope 120 % y reclamo -30 % por defecto; un valor ya definido se respeta."""
        ParametroVersionado.objects.create(periodo=self.periodo, clave='maximo_cumplimiento', valor='150')
        self._cargar()
        parametros = dict(ParametroVersionado.objects.filter(periodo=self.periodo).values_list('clave', 'valor'))
        self.assertEqual(parametros['maximo_cumplimiento'], '150')
        self.assertEqual((parametros['valor_reclamo'], parametros['valor_felicitacion'], parametros['max_felicitaciones']), ('-30', '10', '3'))

    def test_un_periodo_inexistente_es_un_error(self):
        """CU-131 Cargar matriz de cargos (RF-005). Sin el período de destino no se carga nada."""
        with self.assertRaises(CommandError):
            call_command('cargar_matriz', str(self.archivo), periodo='No existe', stdout=StringIO())
        self.assertFalse(ItemMedible.objects.exists())
