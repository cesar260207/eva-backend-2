from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from django.utils import timezone

from .reglas import semana_abierta, validar_fecha_actividad


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
