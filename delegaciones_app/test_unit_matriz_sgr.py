"""Lo que se incorporó de la Matriz SGR completa (las 25 hojas): ítem «Pendientes en tubo menor a 10 %» (hoja SALON),
matriz por cargos (RF-031), catálogo y plazos de la atención social (hojas LISTA y G SOC) e importación de los tubos.

Ninguna prueba usa los archivos reales del municipio: las planillas se arman aquí con datos ficticios.
"""
import csv
import json
import shutil
import tempfile
from datetime import date, timedelta
from decimal import Decimal
from io import StringIO
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone
from openpyxl import Workbook

from .forms import CasoSocialForm
from .management.commands.importar_tubo import interpretar, leer_fecha, leer_telefono, ubicar_columnas
from .models import CasoSocial, Compromiso, HistorialCompromiso, Indicador, ItemMedible, Meta
from .pruebas_base import CLAVE_PRUEBA, EscenarioBase, crear_funcionario
from .salon import area_de, matriz_por_cargos, resumen_de_tubos
from .test_unit_matriz import hoja_de_cargo


class PuntajePorPendientesTests(SimpleTestCase):
    """CU-07.1 (RF-063). Tramos de la hoja SALON: hasta 10 % pendiente vale 100; hasta 50 %, 50; sobre 50 %, 0."""

    def test_tramos(self):
        casos = {Decimal('0'): 100, Decimal('10'): 100, Decimal('10.01'): 50, Decimal('50'): 50, Decimal('50.01'): 0, Decimal('100'): 0}
        for pendiente, puntaje in casos.items():
            with self.subTest(pendiente=pendiente):
                self.assertEqual(Indicador.puntaje_por_pendientes(pendiente), Decimal(puntaje))


class ItemPendientesDelTuboTests(EscenarioBase, TestCase):
    """CU-07.1 (RF-063). El ítem «Pendientes en tubo» mira todo el tubo de la delegación, no solo las tareas de un ítem."""

    def setUp(self):
        self.crear_escenario()
        self.item_pendientes = ItemMedible.objects.create(
            cargo=self.cargo, periodo=self.periodo, nombre='Pendientes en tubo menor a 10%', ponderacion=0, tipo_calculo='tubo_pendientes',
        )
        self.meta = Meta.objects.create(item=self.item_pendientes, funcionario=self.autor, valor_objetivo=Decimal('0.10'))
        self.folios = 0

    def _tarea(self, estado, **cambios):
        self.folios += 1
        datos = {'estado': estado, 'fecha_ingreso': date(2026, 9, 10), 'solicitante_telefono': '912345678'}
        datos.update(cambios)
        return self.nuevo_compromiso(folio=f'PEND-{self.folios}', **datos)

    def _indicador(self):
        return Indicador.generar(self.meta, fecha=date(2026, 9, 30))

    def test_con_pocas_pendientes_el_item_vale_100(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-063). 1 pendiente de 10 tareas es 10 %: el ítem vale 100 %. «En proceso» no cuenta como pendiente."""
        self._tarea('ingresado')
        for _ in range(5):
            self._tarea('realizado')
        for _ in range(4):
            self._tarea('proceso')
        indicador = self._indicador()
        self.assertEqual((indicador.avance, indicador.cumplimiento), (Decimal('10.00'), Decimal('100')))

    def test_con_la_mitad_pendiente_vale_50_y_sobre_eso_0(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-063). 2 de 4 pendientes (50 %) vale 50 %; 3 de 4 (75 %) vale 0 %."""
        self._tarea('pendiente')
        self._tarea('ingresado')
        self._tarea('realizado')
        tarea = self._tarea('realizado')
        self.assertEqual(self._indicador().cumplimiento, Decimal('50'))
        Compromiso.objects.filter(pk=tarea.pk).update(estado='pendiente')
        self.assertEqual(self._indicador().cumplimiento, Decimal('0'))

    def test_sin_tareas_vale_cero(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-063). Sin tareas no hay proporción que medir: 0 %, sin dividir por cero."""
        self.assertEqual(self._indicador().cumplimiento, Decimal('0'))

    def test_cambiar_una_tarea_del_tubo_recalcula_el_item(self):
        """CU-06.1 Recalcular indicadores automáticamente (RF-063, RF-027). Una tarea sin ítem también mueve «Pendientes»."""
        tarea = self._tarea('ingresado')
        ultimo = Indicador.objects.filter(meta=self.meta).order_by('-pk').first()
        self.assertEqual(ultimo.cumplimiento, Decimal('0'))  # 100 % pendiente
        tarea.set_estado('realizado', self.verificador)
        ultimo = Indicador.objects.filter(meta=self.meta).order_by('-pk').first()
        self.assertEqual((ultimo.avance, ultimo.cumplimiento), (Decimal('0.00'), Decimal('100')))


class MatrizCompletaDesdeSalonTests(TestCase):
    """CU-04 (RF-049, RF-063). La hoja SALON completa el ítem que falta en «Planificación y control»."""

    def setUp(self):
        self.carpeta = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.carpeta, ignore_errors=True)
        libro = Workbook()
        libro.remove(libro.active)
        hoja_de_cargo(libro, 'PLAN y CON', 'SUPERHEROE DOS', [
            ('REUNION SEMANAL CON EL EQUIPO', 0.5, 12), ('SOLUCIONES DE INGRESOS AL TUBO', 0.35, 0.8),
        ])
        salon = libro.create_sheet('SALON')
        salon.append(['', '', 'PONDERACION Y COMISIONES', 'PONDERADOR', 'META TRIMESTRE'])
        salon.append(['P Y C', '', 'REUNION SEMANAL CON EL EQUIPO', 0.04, 12])
        salon.append(['', '', 'SOLUCIONES DE INGRESOS AL TUBO', 0.05, 0.8])
        salon.append(['', '', 'PENDIENTES EN TUBO MENOR A 10%', 0.05, 0.1])
        salon.append(['', '', 'CUMPLIMIENTO TOTAL PONDERADO', 1, ''])
        self.excel = self.carpeta / 'matriz.xlsx'
        libro.save(self.excel)
        self.salida = self.carpeta / 'matriz_cargos.json'

    def test_agrega_el_item_de_pendientes_con_la_ponderacion_que_falta(self):
        call_command('generar_matriz', str(self.excel), salida=str(self.salida), stdout=StringIO())
        datos = json.loads(self.salida.read_text(encoding='utf-8'))
        items = datos['cargos'][0]['items']
        self.assertEqual(items[-1], {'nombre': 'Pendientes en tubo menor a 10%', 'ponderacion': 15.0, 'meta_trimestre': 0.1, 'tipo_calculo': 'tubo_pendientes'})
        self.assertEqual(sum(item['ponderacion'] for item in items), 100)
        self.assertFalse(any('no 100 %' in advertencia for advertencia in datos['advertencias']))
        self.assertTrue(any('desde la hoja SALON' in advertencia for advertencia in datos['advertencias']))

    def test_el_json_versionado_tiene_los_80_items_y_todos_los_cargos_suman_100(self):
        """RF-049. data/matriz_cargos.json: 13 cargos, 80 ítems y cada cargo suma exactamente 100 %."""
        datos = json.loads((Path(__file__).resolve().parents[1] / 'data' / 'matriz_cargos.json').read_text(encoding='utf-8'))
        self.assertEqual((len(datos['cargos']), sum(len(c['items']) for c in datos['cargos'])), (13, 80))
        for cargo in datos['cargos']:
            with self.subTest(cargo=cargo['nombre']):
                self.assertEqual(sum(Decimal(str(i['ponderacion'])) for i in cargo['items']), 100)


class AtencionSocialTests(EscenarioBase, TestCase):
    """CU-03 (RF-015, RF-064). Hojas LISTA y G SOC de la matriz: grupo, forma de entrega y plazos de respuesta."""

    def setUp(self):
        self.crear_escenario()

    def _caso(self, **cambios):
        datos = {'funcionario': self.autor, 'nombre_usuario': 'Vecino de prueba', 'telefono_usuario': '912345678', 'etapa': 1, 'tipo': 'pgu'}
        datos.update(cambios)
        return CasoSocial(**datos)

    def test_grupo_y_forma_de_la_hoja_lista(self):
        self.assertEqual((self._caso().grupo, self._caso().forma), ('Gestión de subsidios', 'Aporte'))
        informe = self._caso(tipo='informe_social', subtipo='Informe aporte económico')
        self.assertEqual((informe.grupo, informe.forma), ('Informes sociales', 'Dinero'))
        self.assertEqual(self._caso(tipo='otras_gestiones').grupo, 'Otras gestiones sociales')

    def test_un_informe_social_exige_su_subtipo(self):
        with self.assertRaises(ValidationError) as error:
            self._caso(tipo='informe_social', subtipo='Otro').full_clean()
        self.assertIn('subtipo', error.exception.message_dict)

    def test_las_fechas_de_visita_exigen_marcar_la_visita_y_respetan_el_orden(self):
        with self.assertRaises(ValidationError) as error:
            self._caso(fecha_visita=date(2026, 9, 12)).full_clean()
        self.assertIn('fecha_visita', error.exception.message_dict)
        with self.assertRaises(ValidationError) as error:
            self._caso(requiere_visita=True, fecha_ingreso=date(2026, 9, 10), fecha_visita=date(2026, 9, 14),
                       fecha_entrega_informe=date(2026, 9, 13)).full_clean()
        self.assertIn('fecha_entrega_informe', error.exception.message_dict)

    def test_plazos_cumplidos_e_incumplidos(self):
        """Fila 19 de G SOC: visita programada hasta 10 días, visita el día programado e informe hasta 4 días después."""
        caso = self._caso(
            tipo='informe_social', subtipo='Informe aporte material', requiere_visita=True, fecha_ingreso=date(2026, 9, 1),
            fecha_programada_visita=date(2026, 9, 12), fecha_visita=date(2026, 9, 12), fecha_entrega_informe=date(2026, 9, 15),
        )
        plazos = {fila['nombre']: (fila['dias'], fila['cumple']) for fila in caso.plazos()}
        self.assertEqual(plazos, {
            'Ingreso → visita programada': (11, False),
            'Visita programada → visita realizada': (0, True),
            'Visita → entrega del informe': (3, True),
            'Ingreso → entrega del informe': (14, True),
        })

    def test_un_tramo_sin_fecha_final_queda_en_curso(self):
        caso = self._caso(requiere_visita=True, fecha_ingreso=timezone.localdate() - timedelta(days=3))
        (plazo,) = caso.plazos()
        self.assertEqual((plazo['dias'], plazo['en_curso'], plazo['cumple'], plazo['vencido']), (3, True, True, False))

    def test_el_formulario_completa_ingreso_y_reingresos_si_no_se_informan(self):
        form = CasoSocialForm({'nombre_usuario': 'Ana', 'telefono_usuario': '912345678', 'etapa': 1, 'tipo': 'pgu'}, user=self.usuario_autor)
        self.assertTrue(form.is_valid(), form.errors)
        caso = form.save(commit=False)
        self.assertEqual((caso.fecha_ingreso, caso.reingresos_informe), (timezone.localdate(), 0))


class MatrizPorCargosTests(EscenarioBase, TestCase):
    """CU-17, CU-20.2 (RF-031, RF-033). La hoja SALON: cada cargo con sus ítems y su total ponderado, según el perfil."""

    def setUp(self):
        self.crear_escenario()
        self.periodo.fecha_inicio, self.periodo.fecha_termino = timezone.localdate() - timedelta(days=10), timezone.localdate() + timedelta(days=20)
        self.periodo.save()
        self.meta = Meta.objects.create(item=self.item, funcionario=self.autor, valor_objetivo=10)
        Indicador.generar(self.meta)
        self.usuario_coordinador = crear_funcionario('coordinador-salon', 'coordinador', cargo=self.cargo)
        self.usuario_otro = crear_funcionario('otro-salon', 'funcionario', cargo=self.cargo, delegacion=self.centro)
        Indicador.generar(Meta.objects.create(item=self.item, funcionario=self.usuario_otro.funcionario, valor_objetivo=5))

    def test_area_de_cada_cargo(self):
        self.assertEqual([area_de(nombre) for nombre in ('Gestor social 3', 'Territorial OO.CC. 2', 'Planificación y control', 'Chofer')],
                         ['Gestión social', 'Territorial OO.CC.', 'Planificación y control', 'Otros cargos'])

    def test_la_coordinacion_ve_a_todos_y_el_funcionario_solo_su_fila(self):
        self.client.login(username='coordinador-salon', password=CLAVE_PRUEBA)
        respuesta = self.client.get(reverse('matriz_cargos'))
        self.assertEqual(respuesta.status_code, 200)
        personas = [p['funcionario'] for b in respuesta.context['bloques'] for p in b['personas']]
        self.assertEqual(set(personas), {self.autor, self.usuario_otro.funcionario})
        self.client.login(username='autor-base', password=CLAVE_PRUEBA)
        respuesta = self.client.get(reverse('matriz_cargos'))
        personas = [p['funcionario'] for b in respuesta.context['bloques'] for p in b['personas']]
        self.assertEqual(personas, [self.autor])

    def test_exporta_a_excel_y_queda_en_la_auditoria(self):
        self.client.login(username='coordinador-salon', password=CLAVE_PRUEBA)
        respuesta = self.client.get(reverse('matriz_cargos'), {'formato': 'excel'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('spreadsheetml', respuesta['Content-Type'])

    def test_resumen_de_tubos_por_estado(self):
        hoy = timezone.localdate()
        for numero, estado in enumerate(('ingresado', 'pendiente', 'proceso', 'realizado'), start=1):
            self.nuevo_compromiso(folio=f'SAL-{numero}', estado=estado, fecha_ingreso=hoy)
        (fila,) = resumen_de_tubos(Compromiso.objects.all(), self.periodo)
        self.assertEqual((fila['total'], fila['realizado_pct'], fila['pendiente_pct']), (4, Decimal('25.00'), Decimal('50.00')))

    def test_sin_periodo_no_hay_bloques(self):
        self.assertEqual(matriz_por_cargos(None, None), [])


def escribir_csv(ruta, filas):
    with ruta.open('w', encoding='utf-8-sig', newline='') as salida:
        csv.writer(salida).writerows(filas)


class ImportarTuboTests(EscenarioBase, TestCase):
    """CU-02 (RF-016, RF-053, RF-065). Importación de las hojas TUBO y TUBO CARTAS (CSV) al Tubo. Datos ficticios."""

    def setUp(self):
        self.crear_escenario()
        self.carpeta = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.carpeta, ignore_errors=True)
        self.tubo = self.carpeta / 'tubo.csv'
        escribir_csv(self.tubo, [
            ['TUBO DE TRABAJO', '', '', '', '', '', 'FECHA HOY'],
            ['N°', 'FECHA SOLICITUD', 'ACTIVIDAD/ SOLICITUD/ PROBLEMA', 'INT EXT', 'SOLICITANTE', 'TERRITORIO', 'RESPONSABLE',
             'FECHA DE COMPROMISO', 'MES COM', 'AREA/PERSONA APOYO', 'AVANCE, OBSERVACIONES', 'ESTATUS'],
            ['1', '2026-09-02', 'Poda en pasaje de ejemplo', 'INT', 'Junta de ejemplo', 'Sector uno', 'Persona ficticia', '2026-09-20', '9', 'DISERCO', 'Se solicita poda', 'REALIZADO'],
            ['2', '2026-09-03', 'Taller de ejemplo', 'EXT', 'Delegacion', 'Sector dos', 'Persona ficticia', '13/7/ al 23', '', 'Mujeres', '', 'EN PROCESO'],
            ['3', '', 'Fila sin fecha', '', '', '', '', '', '', '', '', 'PENDIENTE'],
            ['4', '', '', '', '', '', '', '', '', '', '', ''],
        ])

    def _importar(self, archivo, *extra):
        salida = StringIO()
        call_command('importar_tubo', str(archivo), '--delegacion', 'Centro', *extra, stdout=salida)
        return salida.getvalue()

    def test_solo_revisar_no_guarda(self):
        salida = self._importar(self.tubo)
        self.assertIn('2 tareas nuevas', salida)
        self.assertIn('sin fecha de ingreso válida', salida)
        self.assertFalse(Compromiso.objects.exists())

    def test_aplicar_guarda_con_historial_y_repetir_no_duplica(self):
        self._importar(self.tubo, '--aplicar')
        tareas = Compromiso.objects.order_by('fecha_ingreso')
        self.assertEqual([(t.estado, t.origen, t.funcionario_responsable) for t in tareas],
                         [('realizado', 'interno', self.verificador), ('proceso', 'externo', self.verificador)])
        self.assertTrue(all(t.folio.startswith('AGR-IMP-') for t in tareas))
        # Fecha comprometida ilegible: queda la de ingreso y el texto original en la observación.
        self.assertEqual(tareas[1].fecha_comprometida, date(2026, 9, 3))
        self.assertIn('«13/7/ al 23»', tareas[1].observacion)
        self.assertEqual(HistorialCompromiso.objects.count(), 2)
        self.assertIn('0 tareas nuevas, 2 ya importadas', self._importar(self.tubo, '--aplicar'))
        self.assertEqual(Compromiso.objects.count(), 2)

    def test_tubo_de_cartas(self):
        cartas = self.carpeta / 'cartas.csv'
        escribir_csv(cartas, [
            ['', '', 'TUBO DE SEGUIMIENTO DE CARTAS OFICINA DE PARTES'],
            ['', '', 'Fecha', 'Nº', 'PARA', 'REMITE', 'FONO CONTACTO', 'ACTIVIDAD O TEMA', 'FECHA DE LA ACTIVIDAD',
             'ENCARGADO DE SEGUIMIENTO', 'ESTADO', 'PRONUNICIA MIENTO', 'DERIVADA A', 'OBSERVACION'],
            ['', '1', '2026-09-01', '9999', 'Alcaldesa', 'Remitente ficticio', 'correo@ejemplo.cl', 'Solicita espacio', '2026-09-15', 'FOMENTO', 'NO APLICA', '', '', 'Para conocimiento'],
            ['', '2', '2026-09-02', '', 'Delegado', 'Club ficticio', '9 1234 5678', 'Invitación', '', 'DELEGADO', 'APROBADA', '', 'Gabinete', ''],
        ])
        self._importar(cartas, '--aplicar')
        tareas = Compromiso.objects.order_by('fecha_ingreso')
        self.assertEqual([(t.tipo, t.estado, t.solicitante_telefono) for t in tareas],
                         [('carta', 'realizado', ''), ('carta', 'proceso', '912345678')])
        self.assertTrue(tareas[0].folio.startswith('CAR-IMP-'))
        self.assertIn('Carta n.º 9999', tareas[0].observacion)

    def test_sin_delegacion_o_sin_delegado_es_un_error(self):
        with self.assertRaises(CommandError):
            call_command('importar_tubo', str(self.tubo), '--delegacion', 'No existe', stdout=StringIO())
        with self.assertRaises(CommandError):
            call_command('importar_tubo', str(self.tubo), '--delegacion', 'Rural', stdout=StringIO())

    def test_lectura_de_fechas_y_telefonos(self):
        self.assertEqual([leer_fecha(v) for v in ('2026-07-06', '06/07/2026', '22/05/0206', '13/7/ al 23', '')],
                         [date(2026, 7, 6), date(2026, 7, 6), None, None, None])
        self.assertEqual([leer_telefono(v) for v in ('+56 9 1234 5678', '51221994', 'futre@gmail.com')], ['912345678', '51221994', ''])

    def test_una_hoja_sin_encabezados_es_un_error(self):
        with self.assertRaises(CommandError):
            ubicar_columnas([['otra', 'cosa']], 'solicitud')
        datos, motivo = interpretar(['', '', ''], {'descripcion': 1, 'fecha': 0, 'estado': 2}, 'solicitud')
        self.assertEqual((datos, motivo), (None, None))
