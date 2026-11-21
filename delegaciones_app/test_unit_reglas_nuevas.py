from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from .models import Ajuste, Ausencia, CasoSocial, Indicador, ItemMedible, Meta, ParametroVersionado, Periodo, Validacion
from .pruebas_base import EscenarioBase, crear_funcionario, fijar_hoy
from .reglas import dias_ausencia, porcentaje_esperado_ajustado, semana_abierta, validar_fecha_actividad


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


class PuntajeDeActividadTests(EscenarioBase, TestCase):
    """CU-01.1 Validar campos de actividad y CU-07.1 Aplicar fórmulas de medición (RF-010, RF-022). Reglas 1, 2 y 5 de octubre y máximo diario."""

    def setUp(self):
        self.crear_escenario()
        # La fecha válida es el jueves 10 de septiembre: el viernes 11 su semana sigue abierta (regla 4).
        fijar_hoy(self, date(2026, 9, 11))
        self.meta = Meta.objects.create(item=self.item, funcionario=self.autor, valor_objetivo=10)

    def _registrar(self, autor=None, fecha=None, **cambios):
        datos = {
            'item': self.item, 'catalogo': self.catalogo, 'fecha': fecha or self.fecha_valida, 'solicitud_problema': 'Consulta',
            'accion': 'Orientación', 'contacto_nombre': 'Vecina de prueba', 'contacto_telefono': '912345678',
        }
        datos.update(cambios)
        return (autor or self.autor).registrar_actividad(datos)

    def _aprobar(self, actividad):
        Validacion(evidencia=self.nueva_evidencia(actividad), funcionario_verificador=self.verificador).aprobar_evidencia()

    def test_el_octavo_ingreso_del_dia_se_rechaza(self):
        """CU-01.1 Validar campos de actividad (RF-010). Máximo de 7 ingresos diarios por autor (parámetro max_ingresos_diarios)."""
        for numero in range(7):
            self._registrar(solicitud_problema=f'Ingreso {numero + 1}')
        with self.assertRaises(ValidationError) as error:
            self._registrar(solicitud_problema='Ingreso 8')
        self.assertIn('máximo de ingresos', str(error.exception.message_dict['fecha']))
        self.assertEqual(self.autor.actividades.count(), 7)

    def test_el_limite_diario_es_por_autor_y_por_dia(self):
        """CU-01.1 Validar campos de actividad (RF-010). Otro autor u otro día no cuentan para el máximo diario."""
        for numero in range(7):
            self._registrar(solicitud_problema=f'Ingreso {numero + 1}')
        self._registrar(fecha=self.fecha_valida - timedelta(days=1), solicitud_problema='Otro día')
        self._registrar(autor=self.verificador, solicitud_problema='Otro autor')
        self.assertEqual(self.autor.actividades.count(), 8)

    def test_el_limite_diario_se_configura_por_periodo(self):
        """CU-25 Modificar parámetros (RF-010). El máximo diario se lee del parámetro versionado del período."""
        ParametroVersionado.objects.create(periodo=self.periodo, clave='max_ingresos_diarios', valor='2')
        self._registrar()
        self._registrar()
        with self.assertRaises(ValidationError):
            self._registrar()

    def test_sin_nombre_o_telefono_del_usuario_no_puntua(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-022). Regla 2: sin nombre y teléfono del usuario la actividad se guarda, pero no puntúa."""
        for vacio in ({'contacto_nombre': ''}, {'contacto_telefono': ''}, {'contacto_nombre': None, 'contacto_telefono': None}):
            actividad = self._registrar(solicitud_problema=f'Sin contacto {vacio}', **vacio)
            self.assertFalse(actividad.cuenta_puntaje, vacio)
            self.assertEqual(actividad.motivo_sin_puntaje, 'Falta el nombre y teléfono del usuario.')
        self.assertTrue(self._registrar(solicitud_problema='Con contacto').cuenta_puntaje)

    def test_una_actividad_aprobada_sin_contacto_no_suma_al_avance(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-022). Regla 2: aunque se apruebe, sin contacto no aporta al avance."""
        self._aprobar(self._registrar(contacto_telefono=''))
        con_contacto = self._registrar(solicitud_problema='Con contacto')
        self._aprobar(con_contacto)
        self.assertEqual(list(self.meta.actividades_que_aportan()), [con_contacto])

    def test_la_gestion_previa_conserva_el_historial_sin_puntaje(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-022). Regla 5: la gestión previa se guarda y se puede aprobar, pero no puntúa."""
        previa = self._registrar(tipo_accion='gestion_previa')
        self._aprobar(previa)
        previa.refresh_from_db()
        self.assertEqual((previa.estado, previa.cuenta_puntaje), ('aprobada', False))
        self.assertIn('Gestión previa', previa.motivo_sin_puntaje)
        self.assertEqual(self.meta.actividades_que_aportan().count(), 0)

    def test_la_actividad_de_una_tarea_interna_es_otra_gestion(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-022). Regla 1: la actividad de una tarea de origen interno no puntúa."""
        interna = self.nuevo_compromiso(folio='INT-1', origen='interno', gestion_interna=True)
        actividad = self._registrar(compromiso=interna)
        self.assertTrue(actividad.gestion_interna)
        self.assertFalse(actividad.cuenta_puntaje)
        self.assertIn('Otra gestión', actividad.motivo_sin_puntaje)


class CumplimientoConAjustesTests(EscenarioBase, TestCase):
    """CU-07.1 Aplicar fórmulas de medición (RF-022, RF-024, RN-005). Reglas 7 y 8 de octubre: tope, felicitaciones y reclamos."""

    def setUp(self):
        self.crear_escenario()
        self.meta = Meta.objects.create(item=self.item, funcionario=self.autor, valor_objetivo=10)

    def _cumplimiento(self, avance, meta=None):
        indicador = Indicador(meta=meta or self.meta, periodo=self.periodo)
        indicador.avance = avance
        return indicador.calcular_cumplimiento()

    def _ajuste(self, tipo, estado='aplicado', **destino):
        destino = destino or {'funcionario': self.autor}
        return Ajuste.objects.create(tipo=tipo, emisor='Junta de vecinos', periodo=self.periodo, estado=estado, informado_por=self.verificador, **destino)

    def test_el_tope_por_defecto_es_120(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-024, RN-005). Regla 7: el cumplimiento no supera 120 %."""
        self.assertEqual(self._cumplimiento(11), Decimal('110'))
        self.assertEqual(self._cumplimiento(15), Decimal('120'))

    def test_cada_felicitacion_aplicada_suma_10(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-022). Regla 8: una felicitación aplicada suma 10 puntos al cumplimiento."""
        self._ajuste('felicitacion')
        self.assertEqual(self._cumplimiento(5), Decimal('60'))

    def test_se_aplican_como_maximo_tres_felicitaciones(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-022). Regla 8: de cuatro felicitaciones solo cuentan tres."""
        for _ in range(4):
            self._ajuste('felicitacion')
        self.assertEqual(self._cumplimiento(5), Decimal('80'))

    def test_la_felicitacion_no_supera_el_tope(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-024, RN-005). Reglas 7 y 8: con felicitaciones el cumplimiento sigue topado en 120 %."""
        for _ in range(3):
            self._ajuste('felicitacion')
        self.assertEqual(self._cumplimiento(11), Decimal('120'))

    def test_cada_reclamo_aplicado_resta_30_sin_bajar_de_cero(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-022). Regla 8: un reclamo resta 30 puntos y el cumplimiento no queda negativo."""
        self._ajuste('reclamo')
        self.assertEqual(self._cumplimiento(5), Decimal('20'))
        self._ajuste('reclamo')
        self.assertEqual(self._cumplimiento(5), Decimal('0'))

    def test_el_valor_del_reclamo_es_un_parametro(self):
        """CU-25 Modificar parámetros (RF-022). El valor del reclamo se lee del parámetro versionado (la matriz también trae -20 %)."""
        ParametroVersionado.objects.create(periodo=self.periodo, clave='valor_reclamo', valor='-20')
        self._ajuste('reclamo')
        self.assertEqual(self._cumplimiento(5), Decimal('30'))

    def test_solo_cuentan_los_ajustes_aplicados(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-022). Regla 8: un ajuste informado o rechazado no cambia el cumplimiento."""
        self._ajuste('felicitacion', estado='informado')
        self._ajuste('reclamo', estado='rechazado')
        self.assertEqual(self._cumplimiento(5), Decimal('50'))

    def test_el_ajuste_a_la_delegacion_alcanza_a_sus_funcionarios(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-022). Regla 8: la felicitación a la delegación cuenta para quienes pertenecen a ella."""
        self._ajuste('felicitacion', delegacion=self.centro)
        self.assertEqual(self._cumplimiento(5), Decimal('60'))
        self._ajuste('reclamo', delegacion=self.rural)
        self.assertEqual(self._cumplimiento(5), Decimal('60'))

    def test_el_ajuste_de_otro_funcionario_no_cuenta(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-022). Regla 8: cada funcionario recibe solo sus ajustes y los de su delegación."""
        self._ajuste('felicitacion', funcionario=self.verificador)
        self.assertEqual(self._cumplimiento(5), Decimal('50'))

    def test_sin_delegacion_no_recibe_los_ajustes_de_otros(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-022). Regla 8: quien no tiene delegación no recibe los ajustes dirigidos a otras personas."""
        coordinador = crear_funcionario('coordinador-ajustes', 'coordinador', cargo=self.cargo).funcionario
        meta = Meta.objects.create(item=self.item, funcionario=coordinador, valor_objetivo=10)
        self._ajuste('felicitacion', funcionario=self.autor)
        self.assertEqual(self._cumplimiento(5, meta), Decimal('50'))


class ItemTipoTuboTests(EscenarioBase, TestCase):
    """CU-07.1 Aplicar fórmulas de medición (RF-022). Ítem «% del tubo realizado»: tareas realizadas sobre tareas ingresadas con contacto."""

    def setUp(self):
        self.crear_escenario()
        self.tubo = ItemMedible.objects.create(cargo=self.cargo, periodo=self.periodo, nombre='Tubo de trabajo', ponderacion=0, tipo_calculo='tubo')
        self.meta = Meta.objects.create(item=self.tubo, funcionario=self.autor, valor_objetivo=1)
        self.folios = 0

    def _tarea(self, estado='ingresado', **cambios):
        self.folios += 1
        datos = {'item': self.tubo, 'estado': estado, 'fecha_ingreso': date(2026, 9, 10), 'solicitante_telefono': '912345678'}
        datos.update(cambios)
        return self.nuevo_compromiso(folio=f'TUBO-{self.folios}', **datos)

    def test_el_cumplimiento_es_el_porcentaje_de_tareas_realizadas(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-022). Dos realizadas de tres ingresadas dan 66,67 %."""
        self._tarea('realizado')
        self._tarea('realizado')
        self._tarea('proceso')
        indicador = Indicador.generar(self.meta, fecha=date(2026, 9, 30))
        indicador.refresh_from_db()
        self.assertEqual((indicador.avance, indicador.cumplimiento), (Decimal('2'), Decimal('66.67')))

    def test_solo_cuentan_las_tareas_con_contacto_de_la_delegacion_y_del_periodo(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-022). Regla 2: sin teléfono, de otra delegación o fuera del período, la tarea no cuenta."""
        self._tarea('realizado')
        self._tarea('realizado', solicitante_telefono='')
        self._tarea('realizado', delegacion=self.rural)
        self._tarea('realizado', fecha_ingreso=date(2026, 8, 31))
        self._tarea('ingresado')
        indicador = Indicador.generar(self.meta, fecha=date(2026, 9, 30))
        self.assertEqual((indicador.avance, indicador.cumplimiento), (1, Decimal('50')))

    def test_sin_tareas_el_cumplimiento_es_cero(self):
        """CU-07.1 Aplicar fórmulas de medición (RF-022). Un tubo vacío da 0 % y no divide por cero."""
        self.assertEqual(Indicador.generar(self.meta, fecha=date(2026, 9, 30)).cumplimiento, Decimal('0'))


class RecalculoDelSemaforoTests(EscenarioBase, TestCase):
    """CU-06.1 Recalcular indicadores automáticamente (RF-022, RF-027). Ajustes, ausencias y tareas del tubo actualizan el semáforo."""

    def setUp(self):
        self.crear_escenario()
        self.meta = Meta.objects.create(item=self.item, funcionario=self.autor, valor_objetivo=10)

    def _ultimo(self, meta=None):
        return Indicador.objects.filter(meta=meta or self.meta).order_by('fecha_calculo', 'pk').last()

    def _ajuste(self, **cambios):
        datos = {'tipo': 'felicitacion', 'emisor': 'Junta de vecinos', 'periodo': self.periodo, 'informado_por': self.verificador, 'funcionario': self.autor}
        datos.update(cambios)
        return Ajuste.objects.create(**datos)

    def test_un_ajuste_informado_no_recalcula(self):
        """CU-06.1 Recalcular indicadores automáticamente (RF-022). Regla 8: informar no cambia el puntaje hasta que se decide."""
        self._ajuste()
        self.assertIsNone(self._ultimo())

    def test_aplicar_una_felicitacion_recalcula_el_cumplimiento(self):
        """CU-06.1 Recalcular indicadores automáticamente (RF-022, RF-025). Regla 8: al aplicarla, el cumplimiento sube 10 puntos sin correr un comando."""
        ajuste = self._ajuste()
        ajuste.estado = 'aplicado'
        ajuste.save()
        self.assertEqual(self._ultimo().cumplimiento, Decimal('10'))

    def test_rechazar_deja_un_calculo_nuevo_sin_cambio(self):
        """CU-06.1 Recalcular indicadores automáticamente (RF-025). Regla 8: el ajuste rechazado no suma."""
        ajuste = self._ajuste()
        ajuste.estado = 'rechazado'
        ajuste.save()
        self.assertEqual(self._ultimo().cumplimiento, Decimal('0'))

    def test_borrar_un_ajuste_aplicado_lo_quita_del_cumplimiento(self):
        """CU-06.1 Recalcular indicadores automáticamente (RF-025). Al eliminar el ajuste aplicado, el cumplimiento vuelve atrás."""
        ajuste = self._ajuste(estado='aplicado')
        self.assertEqual(self._ultimo().cumplimiento, Decimal('10'))
        ajuste.delete()
        self.assertEqual(self._ultimo().cumplimiento, Decimal('0'))

    def test_el_ajuste_a_la_delegacion_recalcula_solo_a_sus_funcionarios(self):
        """CU-06.1 Recalcular indicadores automáticamente (RF-025). Regla 8: la felicitación a Centro no toca las metas de Rural."""
        rural = crear_funcionario('rural-recalculo', 'funcionario', cargo=self.cargo, delegacion=self.rural).funcionario
        meta_rural = Meta.objects.create(item=self.item, funcionario=rural, valor_objetivo=10)
        self._ajuste(funcionario=None, delegacion=self.centro, estado='aplicado')
        self.assertEqual(self._ultimo().cumplimiento, Decimal('10'))
        self.assertIsNone(self._ultimo(meta_rural))

    def test_registrar_y_borrar_una_ausencia_recalcula(self):
        """CU-06.1 Recalcular indicadores automáticamente (RF-026, RF-027). Regla 9: la ausencia renueva el cálculo de las metas del funcionario."""
        ausencia = Ausencia.objects.create(funcionario=self.autor, periodo=self.periodo, tipo='licencia', desde=date(2026, 9, 1), hasta=date(2026, 9, 5), registrada_por=self.verificador)
        primero = self._ultimo()
        self.assertIsNotNone(primero)
        ausencia.delete()
        self.assertGreater(self._ultimo().pk, primero.pk)

    def test_cambiar_el_estado_de_una_tarea_del_tubo_recalcula(self):
        """CU-06.1 Recalcular indicadores automáticamente (RF-020, RF-022). Al marcar «realizada» la tarea, sube el porcentaje del tubo."""
        tubo = ItemMedible.objects.create(cargo=self.cargo, periodo=self.periodo, nombre='Tubo de trabajo', ponderacion=0, tipo_calculo='tubo')
        meta = Meta.objects.create(item=tubo, funcionario=self.autor, valor_objetivo=1)
        tarea = self.nuevo_compromiso(item=tubo, fecha_ingreso=date(2026, 9, 10), solicitante_telefono='912345678')
        self.assertEqual(self._ultimo(meta).cumplimiento, Decimal('0'))
        tarea.set_estado('realizado', self.autor, 'Poda realizada')
        self.assertEqual((self._ultimo(meta).avance, self._ultimo(meta).cumplimiento), (Decimal('1'), Decimal('100')))

    def test_una_tarea_sin_item_tubo_no_recalcula(self):
        """CU-06.1 Recalcular indicadores automáticamente (RF-020). Las tareas que no son de un ítem tipo tubo no generan cálculos."""
        self.nuevo_compromiso()
        self.assertFalse(Indicador.objects.exists())

    def test_un_periodo_cerrado_no_se_recalcula(self):
        """CU-28.1 Restricción por período cerrado (RF-022, RN-013). Los indicadores de un período cerrado quedan congelados."""
        Periodo.objects.filter(pk=self.periodo.pk).update(estado='cerrado')
        self.assertEqual(Indicador.recalcular(Meta.objects.filter(pk=self.meta.pk)), [])
        self.assertFalse(Indicador.objects.exists())


class EsperadoConAusenciasTests(EscenarioBase, TestCase):
    """CU-17.1 Calcular diferencia de avance (RF-026). Regla 9: las ausencias se descuentan de lo esperado al día."""

    def setUp(self):
        self.crear_escenario()

    def test_sin_ausencias_lo_esperado_es_proporcional_a_los_dias(self):
        """CU-17.1 Calcular diferencia de avance (RF-026). Al día 15 de 30 se espera el 50 %."""
        self.assertEqual(porcentaje_esperado_ajustado(self.autor, self.periodo, date(2026, 9, 15)), Decimal('50.00'))

    def test_las_ausencias_se_descuentan_de_los_dias_computables(self):
        """CU-17.1 Calcular diferencia de avance (RF-026). Con 5 días de ausencia, al día 15 se esperan 10 de 25 días computables: 40 %."""
        Ausencia.objects.create(funcionario=self.autor, periodo=self.periodo, tipo='licencia', desde=date(2026, 9, 1), hasta=date(2026, 9, 5), registrada_por=self.verificador)
        self.assertEqual(porcentaje_esperado_ajustado(self.autor, self.periodo, date(2026, 9, 15)), Decimal('40.00'))


class CasoSocialTests(TestCase):
    """CU-03 Registrar atención social (requerimientos de octubre 2026). Un caso social tiene como máximo tres gestiones."""

    def setUp(self):
        self.funcionario = crear_funcionario('profesional-social', 'funcionario').funcionario

    def _caso(self, etapa):
        return CasoSocial(funcionario=self.funcionario, nombre_usuario='Vecino de prueba', telefono_usuario='912345678', etapa=etapa, tipo='informe_social')

    def test_se_aceptan_las_gestiones_uno_a_tres(self):
        """CU-03 Registrar atención social (requerimientos de octubre 2026). Las etapas 1, 2 y 3 son válidas."""
        for etapa in (1, 2, 3):
            self._caso(etapa).full_clean()

    def test_no_se_acepta_una_cuarta_gestion(self):
        """CU-03 Registrar atención social (requerimientos de octubre 2026). La etapa 4 supera el máximo de tres gestiones."""
        with self.assertRaises(ValidationError) as error:
            self._caso(4).full_clean()
        self.assertIn('máximo tres gestiones', str(error.exception.message_dict['etapa']))

    def test_la_etapa_minima_es_uno(self):
        """CU-03 Registrar atención social (requerimientos de octubre 2026). La etapa 0 no es válida."""
        with self.assertRaises(ValidationError):
            self._caso(0).full_clean()
