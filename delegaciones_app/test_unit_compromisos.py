"""Pruebas unitarias de los compromisos de la agenda colectiva: validación, estados, plazos, historial y filtros (EP-04)."""
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from .forms import CompromisoForm
from .informes import filas_de_compromisos, filtrar_compromisos, situacion_de_plazo
from .models import Compromiso, HistorialCompromiso
from .pruebas_base import EscenarioBase, crear_funcionario


class CompromisoBase(EscenarioBase, TestCase):
    def setUp(self):
        self.crear_escenario()
        self.coordinador = crear_funcionario('coord-agenda', 'coordinador', cargo=self.cargo)


class CompromisoFormUnitTests(CompromisoBase):
    """CU-02 Registro de compromisos ciudadanos, CU-02.1 Validar datos y CU-02.2 Bloquear guardado por campos faltantes (RF-016, RF-017)."""

    def _datos(self, **cambios):
        datos = {
            'delegacion': self.centro.pk, 'funcionario_responsable': self.autor.pk, 'origen': 'externo', 'solicitante': 'Junta de vecinos',
            'territorio': 'Centro', 'eje': 'Gestión Social', 'descripcion': 'Poda de árboles', 'fecha_comprometida': '2026-12-15', 'estado': 'ingresado',
        }
        datos.update(cambios)
        return datos

    def test_un_compromiso_completo_es_valido(self):
        """CU-02.1 Validar datos de compromiso (RF-017). Con todos los datos críticos no hay errores."""
        formulario = CompromisoForm(self._datos(), user=self.coordinador)
        self.assertTrue(formulario.is_valid(), formulario.errors)

    def test_sin_responsable_no_se_guarda(self):
        """CU-02.2 Bloquear guardado por campos faltantes (RF-017). El responsable es obligatorio."""
        formulario = CompromisoForm(self._datos(funcionario_responsable=''), user=self.coordinador)
        self.assertFalse(formulario.is_valid())
        self.assertIn('funcionario_responsable', formulario.errors)

    def test_sin_fecha_comprometida_no_se_guarda(self):
        """CU-02.2 Bloquear guardado por campos faltantes (RF-017). La fecha comprometida es obligatoria."""
        formulario = CompromisoForm(self._datos(fecha_comprometida=''), user=self.coordinador)
        self.assertFalse(formulario.is_valid())
        self.assertIn('fecha_comprometida', formulario.errors)

    def test_cada_campo_obligatorio_se_informa_por_nombre(self):
        """CU-02.2 Bloquear guardado por campos faltantes (RF-017). Solicitante, territorio y descripción también."""
        for campo in ('solicitante', 'territorio', 'descripcion', 'origen', 'delegacion'):
            formulario = CompromisoForm(self._datos(**{campo: ''}), user=self.coordinador)
            self.assertFalse(formulario.is_valid(), campo)
            self.assertIn(campo, formulario.errors, campo)

    def test_una_fecha_con_formato_invalido_se_rechaza(self):
        """CU-02.1 Validar datos de compromiso (RF-017). Una fecha mal escrita no pasa."""
        formulario = CompromisoForm(self._datos(fecha_comprometida='31/31/2026'), user=self.coordinador)
        self.assertFalse(formulario.is_valid())
        self.assertIn('fecha_comprometida', formulario.errors)

    def test_el_eje_debe_ser_uno_de_los_definidos(self):
        """CU-02.1 Validar datos de compromiso (RF-016). Un eje inventado se rechaza."""
        formulario = CompromisoForm(self._datos(eje='Inventado'), user=self.coordinador)
        self.assertFalse(formulario.is_valid())
        self.assertIn('eje', formulario.errors)

    def test_quien_tiene_delegacion_solo_se_asigna_a_si_mismo_en_la_suya(self):
        """CU-26.1 Denegar acceso por ámbito (RF-017). Un funcionario no asigna a otros ni en otra delegación."""
        otro = crear_funcionario('otro-agenda', 'funcionario', cargo=self.cargo, delegacion=self.centro).funcionario
        formulario = CompromisoForm(user=self.usuario_autor)
        self.assertEqual(list(formulario.fields['delegacion'].queryset), [self.centro])
        self.assertEqual(list(formulario.fields['funcionario_responsable'].queryset), [self.autor])
        rechazado = CompromisoForm(self._datos(funcionario_responsable=otro.pk), user=self.usuario_autor)
        self.assertFalse(rechazado.is_valid())
        self.assertIn('funcionario_responsable', rechazado.errors)

    def test_coordinacion_asigna_a_cualquier_funcionario_activo(self):
        """CU-02 Registro de compromisos ciudadanos (RF-017). Quien ve todo elige entre los funcionarios activos."""
        formulario = CompromisoForm(user=self.coordinador)
        self.assertIn(self.autor, formulario.fields['funcionario_responsable'].queryset)

    def test_al_editar_se_oculta_el_estado_y_se_exige_la_version(self):
        """CU-13 Actualización de estados (RF-018). El estado cambia solo desde la agenda, con historial."""
        compromiso = self.nuevo_compromiso()
        formulario = CompromisoForm(instance=compromiso, user=self.coordinador)
        self.assertNotIn('estado', formulario.fields)
        self.assertIn('version', formulario.fields)

    def test_dos_ediciones_simultaneas_la_segunda_se_rechaza(self):
        """CU-23.1 Controlar conflicto de concurrencia (RF-034). El formulario detecta la versión vieja."""
        compromiso = self.nuevo_compromiso()
        datos = self._datos(version=compromiso.version)
        del datos['estado']
        Compromiso.objects.filter(pk=compromiso.pk).update(version=compromiso.version + 1)
        formulario = CompromisoForm(datos, instance=Compromiso.objects.get(pk=compromiso.pk), user=self.coordinador)
        self.assertFalse(formulario.is_valid())
        self.assertIn('modificado por otro usuario', str(formulario.errors))

    def test_el_modelo_tambien_rechaza_guardar_con_una_version_vieja(self):
        """CU-23.1 Controlar conflicto de concurrencia (RF-034). Gana quien guarda primero."""
        primera = Compromiso.objects.get(pk=self.nuevo_compromiso().pk)
        segunda = Compromiso.objects.get(pk=primera.pk)
        primera.descripcion = 'A'
        primera.save()
        segunda.descripcion = 'B'
        with self.assertRaises(ValidationError):
            segunda.save()
        self.assertEqual(Compromiso.objects.get(pk=primera.pk).descripcion, 'A')


class PlazoUnitTests(CompromisoBase):
    """CU-02.3 Destacar compromiso vencido, CU-14 Seguimiento de compromisos, CU-14.1 y CU-14.2 (RF-019)."""

    def test_vencido_es_fecha_pasada_sin_realizar(self):
        """CU-02.3 Destacar compromiso vencido (RF-019). Pasó la fecha y no está realizado."""
        self.assertTrue(self.nuevo_compromiso(dias=-1, folio='V1').vencido)
        self.assertFalse(self.nuevo_compromiso(dias=0, folio='V2').vencido)
        self.assertFalse(self.nuevo_compromiso(dias=-10, estado='realizado', folio='V3').vencido)

    def test_dias_para_vencer(self):
        """CU-14.1 Clasificar compromisos por vencimiento (RF-019). Días que faltan, negativos si ya pasó."""
        self.assertEqual(self.nuevo_compromiso(dias=5, folio='D1').dias_para_vencer, 5)
        self.assertEqual(self.nuevo_compromiso(dias=-2, folio='D2').dias_para_vencer, -2)

    def test_proximo_a_vencer_dentro_de_los_dias_de_alerta(self):
        """CU-14.2 Generar alerta por vencimiento próximo (RF-019). Hoy y los 3 días siguientes, por defecto."""
        casos = [(0, 'pendiente', True), (3, 'pendiente', True), (4, 'pendiente', False), (-1, 'pendiente', False), (2, 'realizado', False)]
        for dias, estado, esperado in casos:
            compromiso = self.nuevo_compromiso(dias=dias, estado=estado, folio=f'P{dias}{estado}')
            self.assertEqual(compromiso.proximo_a_vencer, esperado, (dias, estado))

    @override_settings(COMPROMISO_DIAS_ALERTA=7)
    def test_los_dias_de_alerta_son_configurables(self):
        """CU-14.2 Generar alerta por vencimiento próximo (RF-019). Con 7 días, vence en 7 sí y en 8 no."""
        self.assertTrue(self.nuevo_compromiso(dias=7, folio='A7').proximo_a_vencer)
        self.assertFalse(self.nuevo_compromiso(dias=8, folio='A8').proximo_a_vencer)

    def test_situacion_de_plazo_clasifica_cada_compromiso(self):
        """CU-14.1 Clasificar compromisos por vencimiento (RF-019). Vencido, próximo a vencer, realizado o estado normal."""
        casos = [
            (self.nuevo_compromiso(dias=-3, folio='S1'), ('Vencido', 'danger')),
            (self.nuevo_compromiso(dias=2, folio='S2'), ('Próximo a vencer', 'warning')),
            (self.nuevo_compromiso(dias=40, estado='proceso', folio='S3'), ('En proceso', 'warning')),
            (self.nuevo_compromiso(dias=-3, estado='realizado', folio='S4'), ('Realizado', 'success')),
        ]
        for compromiso, esperado in casos:
            self.assertEqual(situacion_de_plazo(compromiso), esperado, compromiso.folio)

    def test_un_incumplimiento_no_se_elimina(self):
        """CU-14.2 Generar alerta por vencimiento próximo (RF-019). El vencido se conserva con su historial."""
        vencido = self.nuevo_compromiso(dias=-5)
        self.assertIn('se conserva con su historial', vencido.motivo_no_eliminable())
        with self.assertRaises(ValidationError):
            vencido.delete()
        self.assertTrue(Compromiso.objects.filter(pk=vencido.pk).exists())

    def test_uno_vigente_o_realizado_si_se_elimina(self):
        """CU-14.2 Generar alerta por vencimiento próximo (RF-019). Solo el incumplimiento queda protegido."""
        vigente = self.nuevo_compromiso(dias=30, folio='E1')
        realizado = self.nuevo_compromiso(dias=-5, estado='realizado', folio='E2')
        self.assertIsNone(vigente.motivo_no_eliminable())
        vigente.delete()
        realizado.delete()
        self.assertFalse(Compromiso.objects.exists())


class EstadoUnitTests(CompromisoBase):
    """CU-13 Actualización de estados, CU-13.1 Registrar historial de cambio de estado y CU-13.2 Reflejar cierre de compromiso (RF-018)."""

    def test_estados_permitidos_avanzan_y_un_realizado_solo_se_reabre_a_en_proceso(self):
        """CU-13 Actualización de estados (RF-018). Se avanza y un realizado solo vuelve a «en proceso»."""
        esperado = {
            'ingresado': ['pendiente', 'proceso', 'realizado'], 'pendiente': ['proceso', 'realizado'],
            'proceso': ['realizado'], 'realizado': ['proceso'],
        }
        for estado, permitidos in esperado.items():
            compromiso = self.nuevo_compromiso(estado=estado, folio=f'T-{estado}')
            self.assertEqual([valor for valor, _ in compromiso.estados_permitidos()], permitidos, estado)

    def test_set_estado_cambia_y_deja_historial(self):
        """CU-13.1 Registrar historial de cambio de estado (RF-018). Estado anterior, nuevo, autor y observación."""
        compromiso = self.nuevo_compromiso()
        compromiso.set_estado('proceso', self.coordinador.funcionario, 'Se inició la poda')
        registro = compromiso.historial.get()
        self.assertEqual((registro.estado_anterior, registro.estado_nuevo, registro.autor, registro.observacion), ('ingresado', 'proceso', self.coordinador.funcionario, 'Se inició la poda'))
        self.assertEqual(Compromiso.objects.get(pk=compromiso.pk).estado, 'proceso')

    def test_una_transicion_no_permitida_se_rechaza_sin_historial(self):
        """CU-13 Actualización de estados (RF-018). Retroceder no está permitido y no deja rastro."""
        compromiso = self.nuevo_compromiso(estado='proceso')
        with self.assertRaises(ValidationError) as error:
            compromiso.set_estado('pendiente', self.coordinador.funcionario)
        self.assertIn('Transición no permitida', error.exception.messages[0])
        self.assertEqual(Compromiso.objects.get(pk=compromiso.pk).estado, 'proceso')
        self.assertFalse(compromiso.historial.exists())

    def test_un_estado_inexistente_se_rechaza(self):
        """CU-13 Actualización de estados (RF-018). Solo los cuatro estados definidos."""
        with self.assertRaises(ValidationError):
            self.nuevo_compromiso().set_estado('inventado', self.coordinador.funcionario)

    def test_reabrir_un_realizado_conserva_la_observacion(self):
        """CU-13.1 Registrar historial de cambio de estado (RF-018). La reapertura queda explicada."""
        compromiso = self.nuevo_compromiso(estado='realizado')
        compromiso.set_estado('proceso', self.coordinador.funcionario, 'Se detectó un error en el cierre')
        self.assertEqual(compromiso.historial.get().observacion, 'Se detectó un error en el cierre')

    def test_cerrar_exige_una_resolucion(self):
        """CU-13.2 Reflejar cierre de compromiso (RF-018). Sin resolución no se cierra."""
        compromiso = self.nuevo_compromiso()
        for vacia in (None, '', '   '):
            with self.assertRaises(ValidationError):
                compromiso.cerrar_compromiso(vacia, self.coordinador.funcionario)
        self.assertEqual(Compromiso.objects.get(pk=compromiso.pk).estado, 'ingresado')

    def test_cerrar_deja_el_compromiso_realizado_con_su_resolucion(self):
        """CU-13.2 Reflejar cierre de compromiso (RF-020). El cierre se refleja y queda en el historial."""
        compromiso = self.nuevo_compromiso(estado='proceso')
        compromiso.cerrar_compromiso('Poda realizada', self.coordinador.funcionario)
        compromiso.refresh_from_db()
        self.assertEqual((compromiso.estado, compromiso.observacion), ('realizado', 'Poda realizada'))
        self.assertEqual(compromiso.historial.get().estado_nuevo, 'realizado')

    def test_cerrar_uno_ya_realizado_se_rechaza(self):
        """CU-13.2 Reflejar cierre de compromiso (RF-020). El cierre solo se hace una vez."""
        with self.assertRaises(ValidationError):
            self.nuevo_compromiso(estado='realizado').cerrar_compromiso('Otra resolución', self.coordinador.funcionario)

    def test_derivar_cambia_el_responsable_y_lo_deja_en_el_historial(self):
        """CU-13.1 Registrar historial de cambio de estado (RF-017). La derivación queda trazada."""
        otro = crear_funcionario('derivado', 'funcionario', cargo=self.cargo, delegacion=self.centro).funcionario
        compromiso = self.nuevo_compromiso()
        compromiso.derivar_compromiso(otro, self.coordinador.funcionario)
        compromiso.refresh_from_db()
        self.assertEqual(compromiso.funcionario_responsable, otro)
        self.assertIn('Derivado de autor-base a derivado', compromiso.historial.get().observacion)

    def test_un_compromiso_realizado_no_se_deriva(self):
        """CU-13 Actualización de estados (RF-017). Lo cerrado no cambia de responsable."""
        otro = crear_funcionario('derivado2', 'funcionario', cargo=self.cargo, delegacion=self.centro).funcionario
        with self.assertRaises(ValidationError):
            self.nuevo_compromiso(estado='realizado').derivar_compromiso(otro, self.coordinador.funcionario)

    def test_registrar_historial_guarda_el_estado_actual_como_nuevo(self):
        """CU-13.1 Registrar historial de cambio de estado (RF-018). La creación deja su primer registro."""
        compromiso = self.nuevo_compromiso()
        compromiso.registrar_historial(self.coordinador.funcionario, '', 'Creación del compromiso')
        registro = HistorialCompromiso.objects.get()
        self.assertEqual((registro.estado_anterior, registro.estado_nuevo, registro.compromiso), ('', 'ingresado', compromiso))


class FiltrosAgendaUnitTests(CompromisoBase):
    """CU-12 Agenda compartida, CU-12.1 Filtrar agenda y CU-12.2 Consulta sin coincidencias (RF-032)."""

    def setUp(self):
        super().setUp()
        self.vencido = self.nuevo_compromiso(dias=-4, folio='AG-1', descripcion='Reparar luminaria')
        self.por_vencer = self.nuevo_compromiso(dias=2, folio='AG-2', descripcion='Poda de árboles', delegacion=self.rural, estado='proceso')
        self.lejano = self.nuevo_compromiso(dias=90, folio='AG-3', descripcion='Limpieza de canal', solicitante='Comité de agua')
        self.hecho = self.nuevo_compromiso(dias=-9, folio='AG-4', estado='realizado')

    def _folios(self, **filtros):
        return set(filtrar_compromisos(Compromiso.objects.all(), filtros).values_list('folio', flat=True))

    def test_sin_filtros_trae_todos(self):
        """CU-12 Agenda compartida (RF-032). Sin criterios se ven todos los compromisos."""
        self.assertEqual(self._folios(), {'AG-1', 'AG-2', 'AG-3', 'AG-4'})

    def test_filtra_por_delegacion_y_estado(self):
        """CU-12.1 Filtrar agenda compartida (RF-032). Delegación y estado se combinan."""
        self.assertEqual(self._folios(delegacion=str(self.rural.pk)), {'AG-2'})
        self.assertEqual(self._folios(estado='realizado'), {'AG-4'})
        self.assertEqual(self._folios(delegacion=str(self.centro.pk), estado='proceso'), set())

    def test_filtra_por_plazo(self):
        """CU-12.1 Filtrar agenda compartida (RF-019, RF-032). Vencidos no incluye los realizados."""
        self.assertEqual(self._folios(plazo='vencidos'), {'AG-1'})
        self.assertEqual(self._folios(plazo='por_vencer'), {'AG-2'})

    def test_filtra_por_texto_en_folio_descripcion_solicitante_y_delegacion(self):
        """CU-12.1 Filtrar agenda compartida (RF-032). La búsqueda de texto recorre los campos visibles."""
        self.assertEqual(self._folios(q='AG-3'), {'AG-3'})
        self.assertEqual(self._folios(q='luminaria'), {'AG-1'})
        self.assertEqual(self._folios(q='comité'), {'AG-3'})
        self.assertEqual(self._folios(q='rural'), {'AG-2'})

    def test_filtra_por_rango_de_fechas_comprometidas(self):
        """CU-12.1 Filtrar agenda compartida (RF-032). Desde y hasta incluyen sus extremos."""
        hoy = timezone.localdate()
        self.assertEqual(self._folios(desde=str(hoy), hasta=str(hoy + timedelta(days=2))), {'AG-2'})
        self.assertEqual(self._folios(desde=str(hoy - timedelta(days=4)), hasta=str(hoy - timedelta(days=4))), {'AG-1'})

    def test_una_consulta_sin_coincidencias_devuelve_vacio(self):
        """CU-12.2 Consulta sin coincidencias en agenda (RF-032). Nada que mostrar, sin error."""
        self.assertEqual(self._folios(q='no existe este texto'), set())

    def test_los_valores_invalidos_se_ignoran(self):
        """CU-12.1 Filtrar agenda compartida (RF-032). Un filtro mal formado no rompe la agenda."""
        self.assertEqual(self._folios(estado='inventado', plazo='nunca', delegacion='x', desde='mañana', hasta='32-13-2026'), {'AG-1', 'AG-2', 'AG-3', 'AG-4'})

    def test_las_filas_del_informe_incluyen_responsable_y_situacion_del_plazo(self):
        """CU-20.1 Consolidar datos filtrados (RF-033). Columnas y valores listos para exportar."""
        columnas, filas = filas_de_compromisos(Compromiso.objects.filter(folio='AG-1'))
        self.assertEqual(columnas[0], 'Folio')
        self.assertIn('Situación del plazo', columnas)
        fila = dict(zip(columnas, filas[0]))
        self.assertEqual((fila['Folio'], fila['Responsable'], fila['Situación del plazo'], fila['Estado']), ('AG-1', 'autor-base', 'Vencido', 'Ingresado'))
