"""Pruebas unitarias de las alertas (RF-037): vencimientos, evidencias pendientes, ausencia de registros y avance bajo el umbral."""
from datetime import date, timedelta
from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .alertas import (
    alertas_de, alertas_de_ausencia_de_registros, alertas_de_avance_bajo, alertas_de_evidencias_pendientes, alertas_de_vencimiento,
)
from .models import Actividad, Evidencia, Indicador, Meta
from .pruebas_base import EscenarioBase, crear_funcionario

MITAD_DEL_PERIODO = date(2026, 9, 15)


class AlertasBase(EscenarioBase, TestCase):
    def setUp(self):
        self.crear_escenario()
        self.hoy = timezone.localdate()
        self.coordinador = crear_funcionario('coord-alertas', 'coordinador', cargo=self.cargo)

    def envejecer_registro(self, actividad, dias):
        """La fecha de registro se asigna sola al crear; para simular antigüedad se retrasa con update."""
        Actividad.objects.filter(pk=actividad.pk).update(creada=timezone.now() - timedelta(days=dias))


class AlertasDeVencimientoTests(AlertasBase):
    """CU-14.2 Generar alerta por vencimiento próximo (RF-037, RF-019): motivo, responsable, fecha y enlace."""

    def test_un_compromiso_vencido_genera_una_alerta_urgente(self):
        """CU-14.2 Generar alerta por vencimiento próximo (RF-037). Dice hace cuántos días venció."""
        compromiso = self.nuevo_compromiso(dias=-4, folio='AL-VENC')
        alerta, = alertas_de_vencimiento(self.coordinador, self.hoy)
        self.assertEqual((alerta['tipo'], alerta['nivel'], alerta['responsable'], alerta['fecha']), ('vencimiento', 'danger', 'autor-base', compromiso.fecha_comprometida))
        self.assertIn('AL-VENC vencido hace 4 días', alerta['motivo'])
        self.assertIn('AL-VENC', alerta['url'])

    def test_un_compromiso_proximo_a_vencer_genera_una_advertencia(self):
        """CU-14.2 Generar alerta por vencimiento próximo (RF-037). Hoy y los días de alerta."""
        self.nuevo_compromiso(dias=0, folio='AL-HOY')
        self.nuevo_compromiso(dias=2, folio='AL-DOS')
        motivos = {a['motivo'] for a in alertas_de_vencimiento(self.coordinador, self.hoy)}
        self.assertEqual(motivos, {'Compromiso AL-HOY: vence hoy', 'Compromiso AL-DOS: vence en 2 días'})

    def test_el_singular_se_escribe_bien(self):
        """CU-14.2 Generar alerta por vencimiento próximo (RF-037). Un día, no 1 días."""
        self.nuevo_compromiso(dias=1, folio='AL-UNO')
        self.nuevo_compromiso(dias=-1, folio='AL-AYER')
        motivos = {a['motivo'] for a in alertas_de_vencimiento(self.coordinador, self.hoy)}
        self.assertEqual(motivos, {'Compromiso AL-UNO: vence en 1 día', 'Compromiso AL-AYER vencido hace 1 día'})

    def test_no_alertan_los_realizados_ni_los_lejanos(self):
        """CU-14.2 Generar alerta por vencimiento próximo (RF-037). Solo lo que requiere atención."""
        self.nuevo_compromiso(dias=-9, folio='AL-HECHO', estado='realizado')
        self.nuevo_compromiso(dias=40, folio='AL-LEJOS')
        self.assertEqual(alertas_de_vencimiento(self.coordinador, self.hoy), [])

    def test_solo_alertan_los_compromisos_del_ambito_del_usuario(self):
        """CU-26.1 Denegar acceso por ámbito (RF-037). Un funcionario del Centro no se entera de los de Rural."""
        self.nuevo_compromiso(dias=-2, folio='AL-CENTRO')
        self.nuevo_compromiso(dias=-2, folio='AL-RURAL', delegacion=self.rural)
        folios = [a['motivo'] for a in alertas_de_vencimiento(self.usuario_autor, self.hoy)]
        self.assertEqual(len(folios), 1)
        self.assertIn('AL-CENTRO', folios[0])

    @override_settings(COMPROMISO_DIAS_ALERTA=7)
    def test_los_dias_de_alerta_son_configurables(self):
        """CU-14.2 Generar alerta por vencimiento próximo (RF-037, RNF-015). Con 7 días alerta el que vence en 6."""
        self.nuevo_compromiso(dias=6, folio='AL-SEIS')
        self.assertEqual(len(alertas_de_vencimiento(self.coordinador, self.hoy)), 1)


class AlertasDeEvidenciasTests(AlertasBase):
    """CU-11 Validación de actividades (RF-037): evidencias que esperan revisión."""

    def setUp(self):
        super().setUp()
        self.actividad = self.nueva_actividad()
        self.evidencia = self.nueva_evidencia(self.actividad)

    def test_una_evidencia_pendiente_alerta_al_verificador(self):
        """CU-11 Validación de actividades (RF-037). Con motivo, autor como responsable y enlace a la actividad."""
        alerta, = alertas_de_evidencias_pendientes(self.usuario_verificador, self.hoy)
        self.assertEqual((alerta['tipo'], alerta['responsable'], alerta['fecha']), ('evidencia', 'autor-base', self.hoy))
        self.assertIn(self.actividad.codigo_verificador, alerta['motivo'])
        self.assertEqual(alerta['url'], reverse('actividad_detalle', args=[self.actividad.codigo_verificador]))

    def test_alerta_tambien_a_la_coordinacion_pero_no_al_autor(self):
        """CU-11 Validación de actividades (RF-037). Solo quien puede revisar recibe este aviso."""
        self.assertEqual(len(alertas_de_evidencias_pendientes(self.coordinador, self.hoy)), 1)
        self.assertEqual(alertas_de_evidencias_pendientes(self.usuario_autor, self.hoy), [])

    def test_la_espera_larga_sube_el_nivel_a_urgente(self):
        """CU-11 Validación de actividades (RF-037). Con tres días o más, urgente."""
        self.assertEqual(alertas_de_evidencias_pendientes(self.usuario_verificador, self.hoy)[0]['nivel'], 'warning')
        Evidencia.objects.filter(pk=self.evidencia.pk).update(fecha_carga=timezone.now() - timedelta(days=5))
        alerta, = alertas_de_evidencias_pendientes(self.usuario_verificador, self.hoy)
        self.assertEqual(alerta['nivel'], 'danger')
        self.assertIn('desde hace 5 días', alerta['motivo'])

    def test_una_evidencia_revisada_ya_no_alerta(self):
        """CU-11 Validación de actividades (RF-037). Al aprobarla, la alerta desaparece."""
        Evidencia.objects.filter(pk=self.evidencia.pk).update(estado_revision='aprobada')
        self.assertEqual(alertas_de_evidencias_pendientes(self.usuario_verificador, self.hoy), [])

    def test_una_actividad_con_dos_pendientes_alerta_una_vez(self):
        """CU-11 Validación de actividades (RF-037). Se alerta por actividad, no por archivo."""
        self.nueva_evidencia(self.actividad)
        self.assertEqual(len(alertas_de_evidencias_pendientes(self.usuario_verificador, self.hoy)), 1)


class AlertasDeAusenciaTests(AlertasBase):
    """CU-06 Seguimiento de avance (RF-037): funcionarios con metas abiertas que no registran actividades."""

    def setUp(self):
        super().setUp()
        self.meta = Meta.objects.create(item=self.item, funcionario=self.autor, valor_objetivo=3)

    def test_quien_nunca_registro_alerta(self):
        """CU-06 Seguimiento de avance (RF-037). Sin ninguna actividad."""
        alerta, = alertas_de_ausencia_de_registros(self.coordinador, self.hoy)
        self.assertEqual((alerta['tipo'], alerta['responsable'], alerta['fecha']), ('sin_registro', 'autor-base', None))
        self.assertIn('aún no registra actividades', alerta['motivo'])

    def test_un_registro_reciente_no_alerta(self):
        """CU-06 Seguimiento de avance (RF-037). Dentro del plazo no hay aviso."""
        self.nueva_actividad()
        self.assertEqual(alertas_de_ausencia_de_registros(self.coordinador, self.hoy), [])

    def test_un_registro_antiguo_alerta_con_los_dias_transcurridos(self):
        """CU-06 Seguimiento de avance (RF-037). Pasados 7 días sin ingreso."""
        self.envejecer_registro(self.nueva_actividad(), 10)
        alerta, = alertas_de_ausencia_de_registros(self.coordinador, self.hoy)
        self.assertIn('lleva 10 días sin registrar actividades', alerta['motivo'])
        self.assertEqual(alerta['fecha'], self.hoy - timedelta(days=10))

    def test_el_limite_exacto_no_alerta(self):
        """CU-06 Seguimiento de avance (RF-037). Con 7 días justos aún no; con 8 sí."""
        actividad = self.nueva_actividad()
        self.envejecer_registro(actividad, 7)
        self.assertEqual(alertas_de_ausencia_de_registros(self.coordinador, self.hoy), [])
        self.envejecer_registro(actividad, 8)
        self.assertEqual(len(alertas_de_ausencia_de_registros(self.coordinador, self.hoy)), 1)

    @override_settings(ALERTA_DIAS_SIN_REGISTRO=2)
    def test_el_limite_es_configurable(self):
        """CU-06 Seguimiento de avance (RF-037, RNF-015). Con 2 días, tres sin ingreso ya alertan."""
        self.envejecer_registro(self.nueva_actividad(), 3)
        self.assertEqual(len(alertas_de_ausencia_de_registros(self.coordinador, self.hoy)), 1)

    def test_sin_metas_en_un_periodo_abierto_no_se_vigila(self):
        """CU-06 Seguimiento de avance (RF-037). Un período cerrado no genera alertas de ausencia."""
        self.periodo.cerrar_periodo()
        self.assertEqual(alertas_de_ausencia_de_registros(self.coordinador, self.hoy), [])

    def test_cada_usuario_ve_solo_a_quienes_supervisa(self):
        """CU-26.1 Denegar acceso por ámbito (RF-037). Coordinación ve a todos, delegado a su delegación y funcionario a sí mismo."""
        rural = crear_funcionario('rural-ausente', 'funcionario', cargo=self.cargo, delegacion=self.rural)
        Meta.objects.create(item=self.item, funcionario=rural.funcionario, valor_objetivo=3)
        delegado_centro = crear_funcionario('delegado-centro', 'delegado', cargo=self.cargo, delegacion=self.centro)
        Meta.objects.create(item=self.item, funcionario=delegado_centro.funcionario, valor_objetivo=3)

        def responsables(usuario):
            return {a['responsable'] for a in alertas_de_ausencia_de_registros(usuario, self.hoy)}

        self.assertEqual(responsables(self.coordinador), {'autor-base', 'rural-ausente', 'delegado-centro'})
        self.assertEqual(responsables(delegado_centro), {'autor-base', 'delegado-centro'})
        self.assertEqual(responsables(self.usuario_autor), {'autor-base'})
        self.assertEqual(responsables(rural), {'rural-ausente'})


class AlertasDeAvanceTests(AlertasBase):
    """CU-16 Semáforo de cumplimiento (RF-037, RN-008): delegaciones en rojo."""

    def setUp(self):
        super().setUp()
        self.meta = Meta.objects.create(item=self.item, funcionario=self.autor, valor_objetivo=4)
        self.rural_meta = Meta.objects.create(item=self.item, funcionario=crear_funcionario('rural-avance', 'funcionario', cargo=self.cargo, delegacion=self.rural).funcionario, valor_objetivo=4)

    def _alertas(self, usuario):
        with mock.patch('django.utils.timezone.localdate', return_value=MITAD_DEL_PERIODO):
            return alertas_de_avance_bajo(usuario, MITAD_DEL_PERIODO)

    def _indicador(self, meta, avance):
        Indicador.objects.create(meta=meta, periodo=self.periodo, avance=avance, cumplimiento=avance * 25, ponderacion=avance * 25, semaforo='rojo')

    def test_una_delegacion_en_rojo_alerta(self):
        """CU-16 Semáforo de cumplimiento (RF-037). 25 % frente a 50 % esperado."""
        self._indicador(self.meta, 1)
        self._indicador(self.rural_meta, 4)
        alerta, = self._alertas(self.coordinador)
        self.assertEqual((alerta['tipo'], alerta['nivel'], alerta['responsable']), ('avance_bajo', 'danger', 'Delegación Centro'))
        self.assertIn('Cumplimiento de 25.00 % frente a 50.00 % esperado', alerta['motivo'])
        self.assertIn(f'periodo={self.periodo.pk}', alerta['url'])

    def test_verde_y_ambar_no_alertan(self):
        """CU-16 Semáforo de cumplimiento (RF-037). Solo el rojo, que no llega al 60 % de lo esperado."""
        Indicador.objects.create(meta=self.meta, periodo=self.periodo, avance=1, cumplimiento=33.33, ponderacion=33.33, semaforo='ambar')
        Indicador.objects.create(meta=self.rural_meta, periodo=self.periodo, avance=2, cumplimiento=50, ponderacion=50, semaforo='verde')
        self.assertEqual(self._alertas(self.coordinador), [])

    def test_quien_tiene_delegacion_ve_solo_la_suya(self):
        """CU-26.1 Denegar acceso por ámbito (RF-037). Rural no ve el rojo del Centro."""
        self._indicador(self.meta, 1)
        self._indicador(self.rural_meta, 1)
        self.assertEqual([a['responsable'] for a in self._alertas(self.usuario_autor)], ['Delegación Centro'])
        rural = self.rural_meta.funcionario.usuario
        self.assertEqual([a['responsable'] for a in self._alertas(rural)], ['Delegación Rural'])
        self.assertEqual(len(self._alertas(self.coordinador)), 2)

    def test_un_usuario_sin_delegacion_ni_alcance_global_no_recibe_alertas_de_avance(self):
        """CU-26.1 Denegar acceso por ámbito (RF-037). Un verificador sin delegación no las ve."""
        self._indicador(self.meta, 1)
        self.assertEqual(self._alertas(self.usuario_verificador), [])

    def test_sin_indicadores_no_hay_alertas_de_avance(self):
        """CU-16 Semáforo de cumplimiento (RF-037). Sin cálculos no se inventa nada."""
        self.assertEqual(self._alertas(self.coordinador), [])


class AlertasConjuntasTests(AlertasBase):
    """CU-14.2 y CU-11 (RF-037): reunión y orden de todas las alertas."""

    def test_las_urgentes_van_primero_y_luego_por_fecha(self):
        """CU-14.2 Generar alerta por vencimiento próximo (RF-037). Orden por gravedad y antigüedad."""
        self.nuevo_compromiso(dias=2, folio='AL-ADV')
        self.nuevo_compromiso(dias=-5, folio='AL-VIEJO')
        self.nuevo_compromiso(dias=-1, folio='AL-RECIENTE')
        niveles = [a['nivel'] for a in alertas_de(self.coordinador, self.hoy)]
        self.assertEqual(niveles, ['danger', 'danger', 'warning'])
        urgentes = [a['motivo'] for a in alertas_de(self.coordinador, self.hoy) if a['nivel'] == 'danger']
        self.assertIn('AL-VIEJO', urgentes[0])

    def test_cada_alerta_trae_motivo_responsable_fecha_y_enlace(self):
        """CU-14.2 Generar alerta por vencimiento próximo (RF-037). Los cuatro datos que pide el requisito."""
        self.nuevo_compromiso(dias=-2)
        self.nueva_evidencia(self.nueva_actividad())
        for alerta in alertas_de(self.coordinador, self.hoy):
            for campo in ('motivo', 'responsable', 'fecha', 'url'):
                self.assertTrue(alerta[campo], (alerta['tipo'], campo))

    def test_sin_nada_pendiente_no_hay_alertas(self):
        """CU-14.2 Generar alerta por vencimiento próximo (RF-037). La lista vacía es válida."""
        self.assertEqual(alertas_de(self.coordinador, self.hoy), [])

    def test_la_pantalla_de_alertas_muestra_conteos_y_exige_sesion(self):
        """CU-14.2 Generar alerta por vencimiento próximo (RF-037). La página resume cuántas son urgentes."""
        self.nuevo_compromiso(dias=-3, folio='AL-PANTALLA')
        self.assertEqual(self.client.get(reverse('alertas')).status_code, 302)
        self.client.force_login(self.coordinador)
        respuesta = self.client.get(reverse('alertas'))
        self.assertContains(respuesta, 'AL-PANTALLA')
        self.assertEqual((respuesta.context['peligro'], respuesta.context['advertencia']), (1, 0))
        self.assertContains(respuesta, 'Alertas')

    def test_la_pantalla_sin_alertas_lo_dice(self):
        """CU-14.2 Generar alerta por vencimiento próximo (RF-037). Mensaje claro cuando no hay nada."""
        self.client.force_login(self.coordinador)
        self.assertContains(self.client.get(reverse('alertas')), 'No hay alertas por ahora')
