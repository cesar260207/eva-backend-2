from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from .models import Ausencia, Periodo
from .pruebas_base import crear_funcionario
from .reglas import dias_ausencia, semana_abierta, validar_fecha_actividad


class ReglasNuevasTests(SimpleTestCase):
    def test_el_lunes_permite_la_semana_anterior(self):
        hoy = timezone.localdate()
        lunes = hoy - timedelta(days=hoy.weekday())
        self.assertTrue(semana_abierta(lunes - timedelta(days=3), lunes))

    def test_desde_martes_la_semana_anterior_se_cierra(self):
        hoy = timezone.localdate()
        martes = hoy - timedelta(days=hoy.weekday()) + timedelta(days=1)
        self.assertFalse(semana_abierta(martes - timedelta(days=4), martes))

    def test_no_permite_fecha_futura(self):
        periodo = type('Periodo', (), {'fecha_inicio': date(2026, 1, 1), 'fecha_termino': date(2026, 12, 31)})()
        with self.assertRaises(ValidationError):
            validar_fecha_actividad(timezone.localdate() + timedelta(days=1), periodo)


class DiasAusenciaTests(TestCase):
    """CU-17.1 Calcular diferencia de avance (RF-026). Regla 9: los días de ausencia se descuentan del avance esperado."""

    def setUp(self):
        self.periodo = Periodo.objects.create(nombre='Trimestre julio-septiembre 2026', fecha_inicio=date(2026, 7, 1), fecha_termino=date(2026, 9, 30), estado='abierto')
        self.funcionario = crear_funcionario('ausente', 'funcionario').funcionario
        self.delegado = crear_funcionario('delegado-ausencias', 'delegado').funcionario

    def _ausencia(self, desde, hasta):
        # objects.create no pasa por clean(): así se prueba también el traslape, que el formulario impide.
        return Ausencia.objects.create(funcionario=self.funcionario, periodo=self.periodo, tipo='licencia', desde=desde, hasta=hasta, registrada_por=self.delegado)

    def test_ausencias_separadas_suman_sus_dias(self):
        """CU-17.1 Calcular diferencia de avance (RF-026). Dos ausencias de 3 días en meses distintos suman 6 días."""
        self._ausencia(date(2026, 8, 10), date(2026, 8, 12))
        self._ausencia(date(2026, 9, 1), date(2026, 9, 3))
        self.assertEqual(dias_ausencia(self.funcionario, self.periodo), 6)

    def test_ausencias_que_se_traslapan_no_duplican_dias(self):
        """CU-17.1 Calcular diferencia de avance (RF-026). Del 10 al 14 y del 12 al 16 de agosto son 7 días, no 10."""
        self._ausencia(date(2026, 8, 10), date(2026, 8, 14))
        self._ausencia(date(2026, 8, 12), date(2026, 8, 16))
        self.assertEqual(dias_ausencia(self.funcionario, self.periodo), 7)

    def test_una_ausencia_que_empieza_antes_del_periodo_cuenta_solo_sus_dias_dentro(self):
        """CU-17.1 Calcular diferencia de avance (RF-026). Del 28 de junio al 2 de julio cuenta el 1 y el 2 de julio."""
        self._ausencia(date(2026, 6, 28), date(2026, 7, 2))
        self.assertEqual(dias_ausencia(self.funcionario, self.periodo), 2)

    def test_hasta_cuenta_solo_los_dias_transcurridos(self):
        """CU-17.1 Calcular diferencia de avance (RF-026). Con «hasta» se cuentan solo los días de ausencia hasta esa fecha."""
        self._ausencia(date(2026, 8, 10), date(2026, 8, 12))
        self._ausencia(date(2026, 9, 1), date(2026, 9, 3))
        self.assertEqual(dias_ausencia(self.funcionario, self.periodo, date(2026, 8, 9)), 0)
        self.assertEqual(dias_ausencia(self.funcionario, self.periodo, date(2026, 8, 11)), 2)
        self.assertEqual(dias_ausencia(self.funcionario, self.periodo, date(2026, 8, 31)), 3)
        self.assertEqual(dias_ausencia(self.funcionario, self.periodo, date(2026, 9, 2)), 5)

    def test_no_cuenta_las_ausencias_de_otro_funcionario(self):
        """CU-17.1 Calcular diferencia de avance (RF-026). Cada funcionario descuenta solo sus propias ausencias."""
        Ausencia.objects.create(funcionario=self.delegado, periodo=self.periodo, tipo='vacaciones', desde=date(2026, 8, 3), hasta=date(2026, 8, 7), registrada_por=self.delegado)
        self.assertEqual(dias_ausencia(self.funcionario, self.periodo), 0)
