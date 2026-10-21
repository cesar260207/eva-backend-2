"""Pruebas unitarias del cálculo de avance, cumplimiento, semáforo y de las funciones de medicion.py (EP-02 y EP-05)."""
from datetime import date, datetime
from decimal import Decimal
from unittest import mock

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from . import medicion
from .models import (
    Auditoria, Compromiso, Delegacion, Indicador, ItemMedible, Meta, ParametroVersionado, Periodo, Validacion,
)
from .pruebas_base import EscenarioBase, crear_funcionario

MITAD_DEL_PERIODO = date(2026, 9, 15)


class MedicionBase(EscenarioBase, TestCase):
    def setUp(self):
        self.crear_escenario()
        self.meta = Meta.objects.create(item=self.item, funcionario=self.autor, valor_objetivo=4)

    def aprobar(self, actividad, evidencias=1):
        for _ in range(evidencias):
            Validacion(evidencia=self.nueva_evidencia(actividad), funcionario_verificador=self.verificador).aprobar_evidencia()
        actividad.refresh_from_db()
        return actividad


class AvanceUnitTests(MedicionBase):
    """CU-06.1 Recalcular indicadores automáticamente y CU-07 Cálculo automático de cumplimiento (RF-022 a RF-024, RN-003, RN-009)."""

    def test_cuenta_las_actividades_aprobadas_del_item_en_el_periodo(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-022). RN-003: solo aprobadas con validación aprobada."""
        self.aprobar(self.nueva_actividad(solicitud_problema='A'))
        self.aprobar(self.nueva_actividad(solicitud_problema='B'))
        indicador = Indicador(meta=self.meta, periodo=self.periodo)
        self.assertEqual(indicador.calcular_avance(), 2)

    def test_no_cuentan_las_pendientes_rechazadas_ni_en_correccion(self):
        """CU-11.2 Bloquear aporte al avance (RF-022). RN-009: solo lo aprobado aporta."""
        self.nueva_actividad(solicitud_problema='Pendiente')
        rechazada = self.nueva_actividad(solicitud_problema='Rechazada')
        Validacion(evidencia=self.nueva_evidencia(rechazada), funcionario_verificador=self.verificador).rechazar_evidencia('No sirve')
        correccion = self.nueva_actividad(solicitud_problema='Corrección')
        Validacion(evidencia=self.nueva_evidencia(correccion), funcionario_verificador=self.verificador).solicitar_correccion('Falta foto')
        self.assertEqual(Indicador(meta=self.meta, periodo=self.periodo).calcular_avance(), 0)

    def test_no_cuenta_una_actividad_aprobada_sin_validacion_aprobada(self):
        """CU-11 Validación de actividades (RF-022). RN-009: la aprobación exige la validación del verificador."""
        self.nueva_actividad(estado='aprobada', solicitud_problema='Importada sin validación')
        self.assertEqual(Indicador(meta=self.meta, periodo=self.periodo).calcular_avance(), 0)

    def test_no_cuentan_las_actividades_fuera_de_las_fechas_del_periodo(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-022). RN-003: se mide dentro del período."""
        self.aprobar(self.nueva_actividad(fecha=timezone.make_aware(datetime(2026, 10, 1, 0, 0)), solicitud_problema='Octubre'))
        self.aprobar(self.nueva_actividad(fecha=timezone.make_aware(datetime(2026, 8, 31, 23, 59)), solicitud_problema='Agosto'))
        self.aprobar(self.nueva_actividad(fecha=timezone.make_aware(datetime(2026, 9, 30, 23, 59)), solicitud_problema='Último día'))
        self.assertEqual(Indicador(meta=self.meta, periodo=self.periodo).calcular_avance(), 1)

    def test_solo_cuentan_las_actividades_de_la_delegacion_de_la_meta(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-022, RF-029). Una meta de Centro no suma lo de Rural."""
        self.aprobar(self.nueva_actividad(solicitud_problema='Centro'))
        self.aprobar(self.nueva_actividad(delegacion=self.rural, solicitud_problema='Rural'))
        self.assertEqual(Indicador(meta=self.meta, periodo=self.periodo).calcular_avance(), 1)

    def test_una_meta_sin_delegacion_suma_todas_las_delegaciones(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-022). El alcance global cuenta cualquier delegación."""
        coordinador = crear_funcionario('coord-meta', 'coordinador', cargo=self.cargo).funcionario
        meta_global = Meta.objects.create(item=self.item, funcionario=coordinador, valor_objetivo=4)
        self.aprobar(self.nueva_actividad(solicitud_problema='Centro'))
        self.aprobar(self.nueva_actividad(delegacion=self.rural, solicitud_problema='Rural'))
        self.assertEqual(Indicador(meta=meta_global, periodo=self.periodo).calcular_avance(), 2)

    def test_una_actividad_con_dos_evidencias_aprobadas_cuenta_una_vez(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-022). RN-003: se cuentan actividades, no evidencias."""
        self.aprobar(self.nueva_actividad(), evidencias=2)
        self.assertEqual(Indicador(meta=self.meta, periodo=self.periodo).calcular_avance(), 1)

    def test_solo_cuentan_las_actividades_del_item_de_la_meta(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-022). Un ítem distinto no aporta."""
        otro_item = ItemMedible.objects.create(cargo=self.cargo, periodo=self.periodo, nombre='Otro ítem', ponderacion=0)
        self.aprobar(self.nueva_actividad(item=otro_item, solicitud_problema='Otro'))
        self.assertEqual(Indicador(meta=self.meta, periodo=self.periodo).calcular_avance(), 0)


class CumplimientoUnitTests(MedicionBase):
    """CU-07 Cálculo automático de cumplimiento, CU-07.1 y CU-16.1 Calcular estado del semáforo (RF-023, RF-024, RF-027, RN-004, RN-005)."""

    def _indicador(self, avance):
        indicador = Indicador(meta=self.meta, periodo=self.periodo, avance=avance)
        indicador.calcular_cumplimiento()
        return indicador

    def test_cumplimiento_es_avance_sobre_meta(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-023). RN-004: 1 de 4 es 25 %."""
        self.assertEqual(self._indicador(1).cumplimiento, Decimal('25.00'))

    def test_el_cumplimiento_se_topa_en_150_por_defecto(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-024). RN-005: no pasa del máximo computable."""
        self.assertEqual(self._indicador(100).cumplimiento, Decimal('150'))

    def test_el_tope_lo_define_el_parametro_del_periodo(self):
        """CU-25 Modificar parámetros (RF-024, RF-038). El máximo computable es configurable por período."""
        ParametroVersionado.objects.create(periodo=self.periodo, clave='maximo_cumplimiento', valor='120')
        self.assertEqual(self._indicador(100).cumplimiento, Decimal('120'))

    def test_el_cumplimiento_ponderado_usa_el_ponderador_de_la_meta(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-024). RN-005: ponderador 40 % de un 50 % da 20."""
        self.meta.ponderador = Decimal('40')
        self.meta.save()
        indicador = self._indicador(2)
        self.assertEqual((indicador.cumplimiento, indicador.ponderacion), (Decimal('50.00'), Decimal('20.00')))

    def test_semaforo_segun_lo_esperado_al_dia(self):
        """CU-16.1 Calcular estado del semáforo (RF-027). RN-008 con esperado de 50 %."""
        indicador = self._indicador(0)
        for cumplimiento, color in ((50, 'verde'), (75, 'verde'), (30, 'ambar'), (49.99, 'ambar'), (29.99, 'rojo'), (0, 'rojo')):
            indicador.cumplimiento = Decimal(str(cumplimiento))
            self.assertEqual(indicador.actualizar_semaforo(MITAD_DEL_PERIODO), color, cumplimiento)
            self.assertEqual(indicador.semaforo, color)

    def test_generar_calcula_y_guarda_un_indicador_nuevo(self):
        """CU-06.1 Recalcular indicadores automáticamente (RF-022). Cada generación deja un registro."""
        self.aprobar(self.nueva_actividad())
        primero = Indicador.generar(self.meta, MITAD_DEL_PERIODO)
        self.aprobar(self.nueva_actividad(solicitud_problema='Otra'))
        segundo = Indicador.generar(self.meta, MITAD_DEL_PERIODO)
        self.assertEqual((primero.avance, segundo.avance), (1, 2))
        self.assertEqual(Indicador.objects.filter(meta=self.meta).count(), 2)
        self.assertEqual(segundo.periodo, self.periodo)

    def test_no_se_genera_un_indicador_de_un_periodo_cerrado(self):
        """CU-28.1 Restricción por período cerrado (RF-038). RN-013: los resultados cerrados no cambian."""
        self.periodo.cerrar_periodo()
        with self.assertRaises(ValidationError):
            Indicador.generar(self.meta)
        self.assertFalse(Indicador.objects.exists())


class ResultadosPorDelegacionUnitTests(MedicionBase):
    """CU-16 Semáforo de cumplimiento, CU-17 Comparación entre avance esperado y real y CU-18 Resumen ejecutivo (RF-026 a RF-029)."""

    def setUp(self):
        super().setUp()
        self.meta_rural = Meta.objects.create(item=self.item, funcionario=crear_funcionario('rural-med', 'funcionario', cargo=self.cargo, delegacion=self.rural).funcionario, valor_objetivo=4)
        self.aprobar(self.nueva_actividad(solicitud_problema='Centro 1'))
        self.aprobar(self.nueva_actividad(solicitud_problema='Centro 2'))
        self.aprobar(self.nueva_actividad(solicitud_problema='Centro 3'))
        self.aprobar(self.nueva_actividad(solicitud_problema='Centro 4'))
        self.aprobar(self.nueva_actividad(delegacion=self.rural, solicitud_problema='Rural 1'))
        for meta in Meta.objects.all():
            Indicador.generar(meta)

    def _filas(self, **argumentos):
        with mock.patch('django.utils.timezone.localdate', return_value=MITAD_DEL_PERIODO):
            return {fila['nombre']: fila for fila in medicion.resultados_por_delegacion(self.periodo, **argumentos)}

    def test_cumplimiento_y_color_de_cada_delegacion(self):
        """CU-16 Semáforo de cumplimiento (RF-027). Centro al 100 % es verde y Rural al 25 % es rojo."""
        filas = self._filas()
        self.assertEqual((filas['Centro']['cumplimiento'], filas['Centro']['estado']), (Decimal('100.00'), 'Verde'))
        self.assertEqual((filas['Rural']['cumplimiento'], filas['Rural']['estado']), (Decimal('25.00'), 'Rojo'))

    def test_diferencia_con_lo_esperado_y_desviacion(self):
        """CU-17.1 Calcular diferencia de avance (RF-026). Con esperado de 50 %: +50 para Centro y -25 para Rural."""
        filas = self._filas()
        self.assertEqual((filas['Centro']['diferencia'], filas['Centro']['desviacion']), (Decimal('50.00'), False))
        self.assertEqual((filas['Rural']['diferencia'], filas['Rural']['desviacion']), (Decimal('-25.00'), True))

    def test_una_desviacion_ambar_tambien_se_destaca(self):
        """CU-17.2 Destacar desviación significativa (RF-026). RN-008: ámbar y rojo son desviación."""
        self.meta_rural.valor_objetivo = 2
        self.meta_rural.save()
        Indicador.generar(self.meta_rural)
        fila = self._filas()['Rural']
        self.assertEqual((fila['cumplimiento'], fila['estado'], fila['desviacion']), (Decimal('50.00'), 'Verde', False))
        self.meta_rural.valor_objetivo = Decimal('3')
        self.meta_rural.save()
        Indicador.generar(self.meta_rural)
        fila = self._filas()['Rural']
        self.assertEqual((fila['cumplimiento'], fila['estado'], fila['desviacion']), (Decimal('33.33'), 'Ámbar', True))

    def test_el_detalle_muestra_avance_y_meta_de_cada_item(self):
        """CU-18.2 Navegar al detalle de gestión (RF-029). El detalle explica de dónde sale la cifra."""
        self.assertEqual(self._filas()['Centro']['detalle'], ['Atención territorial: 4 de 4 actividades'])

    def test_se_filtra_por_texto(self):
        """CU-29 Búsqueda y filtros (RF-032). Buscar «rur» deja solo Rural."""
        self.assertEqual(set(self._filas(texto='rur')), {'Rural'})

    def test_sin_periodo_no_hay_resultados(self):
        """CU-18 Resumen ejecutivo (RF-029). Sin período elegido la lista está vacía."""
        self.assertEqual(medicion.resultados_por_delegacion(None), [])

    def test_una_delegacion_inactiva_no_aparece(self):
        """CU-26 Administración de delegaciones (RF-001). Las desactivadas salen de los resultados."""
        self.rural.set_estado(False)
        self.assertEqual(set(self._filas()), {'Centro'})

    def test_promedio_general(self):
        """CU-18.1 Consolidar datos de delegación (RF-029). Promedio simple de los cumplimientos."""
        self.assertEqual(medicion.promedio_general(list(self._filas().values())), Decimal('62.50'))
        self.assertEqual(medicion.promedio_general([]), Decimal('0.00'))


class PeriodoVigenteUnitTests(MedicionBase):
    """CU-18 Resumen ejecutivo y CU-29 Búsqueda y filtros (RF-029, RF-032): elección del período a mostrar."""

    def setUp(self):
        super().setUp()
        self.agosto = Periodo.objects.create(nombre='Agosto 2026', fecha_inicio=date(2026, 8, 1), fecha_termino=date(2026, 8, 31), estado='abierto')
        item = ItemMedible.objects.create(cargo=self.cargo, periodo=self.agosto, nombre='Atención agosto', ponderacion=100)
        Indicador.generar(Meta.objects.create(item=item, funcionario=self.autor, valor_objetivo=2))
        self.agosto.cerrar_periodo()

    def test_solo_se_ofrecen_los_periodos_con_indicadores(self):
        """CU-18 Resumen ejecutivo (RF-029). Un período sin cálculos no se ofrece."""
        self.assertEqual(list(medicion.periodos_con_indicadores()), [self.agosto])

    def test_sin_indicadores_en_ningun_periodo_no_hay_periodo_vigente(self):
        """CU-18 Resumen ejecutivo (RF-029). Sin cálculos la pantalla muestra el aviso vacío."""
        Indicador.objects.all().delete()
        self.assertIsNone(medicion.periodo_vigente())

    def test_por_defecto_el_periodo_abierto_mas_reciente(self):
        """CU-18 Resumen ejecutivo (RF-029). Con indicadores en ambos, gana el abierto."""
        Indicador.generar(self.meta)
        self.assertEqual(medicion.periodo_vigente(), self.periodo)

    def test_se_puede_elegir_otro_periodo_con_indicadores(self):
        """CU-29 Búsqueda y filtros (RF-032). El período pedido se respeta."""
        Indicador.generar(self.meta)
        self.assertEqual(medicion.periodo_vigente(self.agosto.pk), self.agosto)
        self.assertEqual(medicion.periodo_vigente(str(self.agosto.pk)), self.agosto)

    def test_un_valor_invalido_cae_en_el_periodo_por_defecto(self):
        """CU-29 Búsqueda y filtros (RF-032). Un id inexistente o con texto no rompe la pantalla."""
        Indicador.generar(self.meta)
        for valor in ('abc', '9999', '1;drop table', '-1', ''):
            self.assertEqual(medicion.periodo_vigente(valor), self.periodo, valor)

    def test_si_ninguno_esta_abierto_se_usa_el_mas_reciente(self):
        """CU-18 Resumen ejecutivo (RF-029). Sin períodos abiertos, el más reciente con cálculos."""
        self.assertEqual(medicion.periodo_vigente(), self.agosto)


class FichaPersonalUnitTests(MedicionBase):
    """CU-06 Seguimiento de avance, CU-06.2 Destacar meta cumplida y CU-07.3 Mostrar detalle en reporte (RF-008, RF-028)."""

    def _fila(self):
        with mock.patch('django.utils.timezone.localdate', return_value=MITAD_DEL_PERIODO):
            return medicion.ficha_personal(self.autor, self.periodo)['filas'][0]

    def test_una_meta_sin_calculo_se_marca_como_tal(self):
        """CU-06 Seguimiento de avance (RF-008). Antes del primer cálculo no hay formula ni diferencia."""
        fila = self._fila()
        self.assertEqual((fila['estado'], fila['formula'], fila['diferencia'], fila['cumplida']), ('Sin cálculo', [], None, False))

    def test_la_fila_trae_avance_cumplimiento_y_diferencia(self):
        """CU-06 Seguimiento de avance (RF-028). 1 de 4 con esperado de 50 % es 25 %, 25 puntos bajo lo esperado."""
        self.aprobar(self.nueva_actividad())
        Indicador.generar(self.meta, MITAD_DEL_PERIODO)
        fila = self._fila()
        self.assertEqual((fila['avance'], fila['cumplimiento'], fila['diferencia']), (1, Decimal('25.00'), Decimal('-25.00')))
        self.assertEqual((fila['estado'], fila['desviacion'], fila['cumplida']), ('Rojo', True, False))

    def test_la_meta_alcanzada_se_destaca_como_cumplida(self):
        """CU-06.2 Destacar meta cumplida (RF-028). Con el avance igual al objetivo queda cumplida."""
        self.meta.valor_objetivo = 1
        self.meta.save()
        self.aprobar(self.nueva_actividad())
        Indicador.generar(self.meta, MITAD_DEL_PERIODO)
        self.assertTrue(self._fila()['cumplida'])

    def test_el_detalle_muestra_la_formula_y_la_ponderacion(self):
        """CU-07.3 Mostrar detalle en reporte (RF-023). El cálculo se puede verificar a mano."""
        self.aprobar(self.nueva_actividad())
        Indicador.generar(self.meta, MITAD_DEL_PERIODO)
        formula = self._fila()['formula']
        self.assertIn('1 / 4 × 100 = 25 %', formula[0])
        self.assertIn('Máximo computable: 150 %', formula[1])
        self.assertIn('100 % × 25 % = 25', formula[2])

    def test_el_detalle_avisa_cuando_se_aplica_el_tope(self):
        """CU-07.3 Mostrar detalle en reporte (RF-024). Si el bruto supera el máximo, se explica."""
        self.meta.valor_objetivo = 1
        self.meta.save()
        for numero in range(2):
            self.aprobar(self.nueva_actividad(solicitud_problema=f'Extra {numero}'))
        Indicador.generar(self.meta, MITAD_DEL_PERIODO)
        self.assertIn('se aplica el tope y queda en 150 %', self._fila()['formula'][1])

    def test_lista_las_actividades_que_aportan(self):
        """CU-07.3 Mostrar detalle en reporte (RF-022). Cada cifra enlaza a su origen."""
        actividad = self.aprobar(self.nueva_actividad())
        Indicador.generar(self.meta, MITAD_DEL_PERIODO)
        self.assertEqual(self._fila()['actividades'], [actividad])

    def test_solo_aparecen_las_metas_del_funcionario(self):
        """CU-06 Seguimiento de avance (RF-008). La ficha es personal."""
        otro = crear_funcionario('otro-med', 'funcionario', cargo=self.cargo, delegacion=self.centro).funcionario
        Meta.objects.create(item=self.item, funcionario=otro, valor_objetivo=3)
        with mock.patch('django.utils.timezone.localdate', return_value=MITAD_DEL_PERIODO):
            filas = medicion.ficha_personal(self.autor, self.periodo)['filas']
        self.assertEqual([fila['meta'] for fila in filas], [self.meta])

    def test_periodos_de_lista_solo_donde_hay_metas(self):
        """CU-06 Seguimiento de avance (RF-008). El selector de períodos de la ficha."""
        vacio = Periodo.objects.create(nombre='Julio 2026', fecha_inicio=date(2026, 7, 1), fecha_termino=date(2026, 7, 31), estado='abierto')
        self.assertEqual(list(medicion.periodos_de(self.autor)), [self.periodo])
        self.assertEqual(medicion.periodo_de_ficha(self.autor), self.periodo)
        self.assertEqual(medicion.periodo_de_ficha(self.autor, vacio.pk), self.periodo)

    def test_resumen_de_evidencias_por_estado(self):
        """CU-06 Seguimiento de avance (RF-028). Cuántas evidencias hay en cada estado de revisión."""
        self.aprobar(self.nueva_actividad(solicitud_problema='Aprobada'))
        self.nueva_evidencia(self.nueva_actividad(solicitud_problema='Pendiente'))
        conteo = {fila['estado']: fila['total'] for fila in medicion.resumen_de_evidencias(self.autor, self.periodo)}
        self.assertEqual(conteo, {'pendiente': 1, 'aprobada': 1, 'rechazada': 0, 'correccion': 0})

    def test_resumen_de_compromisos_por_situacion(self):
        """CU-14.1 Clasificar compromisos por vencimiento (RF-019). Vigentes, por vencer, vencidos y realizados."""
        self.nuevo_compromiso(dias=60, folio='C-VIGENTE')
        self.nuevo_compromiso(dias=2, folio='C-POR-VENCER')
        self.nuevo_compromiso(dias=-5, folio='C-VENCIDO')
        self.nuevo_compromiso(dias=-5, folio='C-REALIZADO', estado='realizado')
        resumen = medicion.resumen_de_compromisos(self.autor)
        self.assertEqual(resumen, {'total': 4, 'vencidos': 1, 'por_vencer': 1, 'realizados': 1, 'vigentes': 1})
