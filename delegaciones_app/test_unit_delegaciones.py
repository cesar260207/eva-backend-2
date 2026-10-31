"""Pruebas de los ajustes de la revisión del equipo: carga de evidencia en su propia pantalla, indicador de
evidencia, revisión aprobar/rechazar, ámbito del delegado, coordinación de delegados y creación de compromisos."""
from datetime import date

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from .models import Auditoria, Funcionario, Indicador, MedicionDelegacion, Meta, Validacion
from .pruebas_base import EscenarioBase, crear_funcionario


class EvidenciaEnListadoYDetalleTests(EscenarioBase, TestCase):
    """Indicador de evidencia en el listado y botón «Subir evidencia» separado de «Modificar»."""

    def setUp(self):
        self.crear_escenario()

    def test_el_listado_indica_si_la_actividad_tiene_evidencia(self):
        """CU-09 Indicar evidencia cargada (RF-012). Con y sin evidencia se distinguen en la lista."""
        sin = self.nueva_actividad(solicitud_problema='Sin respaldo')
        con = self.nueva_actividad(solicitud_problema='Con respaldo')
        self.nueva_evidencia(con)
        self.client.force_login(self.usuario_autor)
        filas = {a.pk: a for a in self.client.get(reverse('actividades')).context['actividades']}
        self.assertEqual((filas[sin.pk].total_evidencias, filas[con.pk].total_evidencias), (0, 1))
        respuesta = self.client.get(reverse('actividades'))
        self.assertContains(respuesta, 'Sin evidencia')
        self.assertContains(respuesta, 'Con evidencia (1)')

    def test_el_indicador_no_hace_una_consulta_por_fila(self):
        """CU-09 Indicar evidencia cargada (RF-012). El total sale de un annotate: más filas no suman consultas."""
        self.client.force_login(self.usuario_autor)

        def consultas_del_listado():
            with CaptureQueriesContext(connection) as consultas:
                self.client.get(reverse('actividades'))
            return len(consultas)

        self.nueva_evidencia(self.nueva_actividad())
        con_una = consultas_del_listado()
        for _ in range(4):
            self.nueva_evidencia(self.nueva_actividad())
        self.assertEqual(consultas_del_listado(), con_una)

    def test_el_autor_ve_el_boton_subir_evidencia(self):
        """CU-09 Subir evidencia (RF-012). Botón propio en la lista y en el detalle."""
        actividad = self.nueva_actividad()
        url = reverse('evidencia_subir', args=[actividad.codigo_verificador])
        self.client.force_login(self.usuario_autor)
        self.assertContains(self.client.get(reverse('actividades')), url)
        self.assertContains(self.client.get(reverse('actividad_detalle', args=[actividad.codigo_verificador])), url)
        self.assertTemplateUsed(self.client.get(url), 'delegaciones_app/evidencia_subir.html')

    def test_subir_evidencia_y_modificar_son_botones_distintos(self):
        """CU-09 Subir evidencia (RF-012). En el detalle, «Subir evidencia» y «Modificar actividad» llevan a pantallas distintas."""
        actividad = self.nueva_actividad()
        self.client.force_login(self.usuario_autor)
        detalle = self.client.get(reverse('actividad_detalle', args=[actividad.codigo_verificador]))
        self.assertContains(detalle, f'href="{reverse("evidencia_subir", args=[actividad.codigo_verificador])}">Subir evidencia</a>', html=False)
        self.assertContains(detalle, f'href="{reverse("actividad_editar", args=[actividad.codigo_verificador])}">Modificar actividad</a>', html=False)

    def test_una_actividad_aprobada_no_ofrece_subir_evidencia(self):
        """CU-09 Subir evidencia (RF-012, RF-013). Aprobada no admite evidencias: el botón no aparece en la lista ni en el detalle."""
        actividad = self.nueva_actividad(estado='aprobada')
        url = reverse('evidencia_subir', args=[actividad.codigo_verificador])
        self.client.force_login(self.usuario_autor)
        self.assertNotContains(self.client.get(reverse('actividades')), url)
        self.assertNotContains(self.client.get(reverse('actividad_detalle', args=[actividad.codigo_verificador])), url)
        self.assertRedirects(self.client.get(url), reverse('actividad_detalle', args=[actividad.codigo_verificador]))

    def test_quien_solo_revisa_no_ve_carga_de_archivos(self):
        """CU-11 Revisión sin elementos de carga (RF-013). El revisor ve la decisión, no el formulario de carga."""
        actividad = self.nueva_actividad()
        self.nueva_evidencia(actividad)
        self.client.force_login(self.usuario_verificador)
        detalle = self.client.get(reverse('actividad_detalle', args=[actividad.codigo_verificador]))
        self.assertNotContains(detalle, 'type="file"')
        self.assertNotContains(detalle, reverse('evidencia_subir', args=[actividad.codigo_verificador]))
        self.assertContains(detalle, reverse('revisar_actividad', args=[actividad.codigo_verificador, 'rechazar']))
        self.assertRedirects(self.client.get(reverse('evidencia_subir', args=[actividad.codigo_verificador])), reverse('actividad_detalle', args=[actividad.codigo_verificador]))

    def test_el_revisor_no_ve_avisos_de_carga(self):
        """CU-11 Revisión sin elementos de carga (RF-013). El aviso «no admite nuevas evidencias» es solo para el autor."""
        actividad = self.nueva_actividad(estado='aprobada')
        self.nueva_evidencia(actividad, estado_revision='aprobada')
        detalle = reverse('actividad_detalle', args=[actividad.codigo_verificador])
        self.client.force_login(self.usuario_verificador)
        self.assertNotContains(self.client.get(detalle), 'no admite nuevas evidencias')
        self.client.force_login(self.usuario_autor)
        self.assertContains(self.client.get(detalle), 'no admite nuevas evidencias')


class RevisionPorDelegadoTests(EscenarioBase, TestCase):
    """El delegado revisa las evidencias de su delegación, nunca las propias."""

    def setUp(self):
        self.crear_escenario()
        self.delegado = crear_funcionario('delegado-centro', 'delegado', cargo=self.cargo, delegacion=self.centro)
        self.actividad = self.nueva_actividad()
        self.nueva_evidencia(self.actividad)

    def _revisar(self, usuario, actividad, decision='aprobar', observacion=''):
        self.client.force_login(usuario)
        return self.client.post(reverse('revisar_actividad', args=[actividad.codigo_verificador, decision]), {'observacion': observacion})

    def test_el_delegado_aprueba_una_actividad_de_su_delegacion(self):
        """CU-11 Validación por el delegado (RF-013). Revisa lo registrado en su delegación."""
        self._revisar(self.delegado, self.actividad)
        self.assertEqual(Validacion.objects.get().funcionario_verificador, self.delegado.funcionario)

    def test_el_delegado_no_revisa_otra_delegacion_ni_lo_propio(self):
        """CU-11.1 Restringir revisión (RF-013, RF-036). Otra delegación queda fuera; lo propio no se autoaprueba."""
        de_rural = crear_funcionario('delegado-rural', 'delegado', cargo=self.cargo, delegacion=self.rural)
        self.assertEqual(self._revisar(de_rural, self.actividad).status_code, 404)
        propia = self.nueva_actividad(funcionario_autor=self.delegado.funcionario)
        self.nueva_evidencia(propia)
        respuesta = self._revisar(self.delegado, propia)
        self.assertContains(self.client.get(respuesta.url), 'No puedes revisar una actividad que registraste')
        self.assertFalse(Validacion.objects.exists())

    def test_rechazar_exige_motivo(self):
        """CU-11.1 Rechazar con motivo (RF-013). Sin motivo no se rechaza; con motivo queda rechazada."""
        self._revisar(self.delegado, self.actividad, 'rechazar')
        self.assertFalse(Validacion.objects.exists())
        self._revisar(self.delegado, self.actividad, 'rechazar', 'La foto no corresponde')
        self.actividad.refresh_from_db()
        self.assertEqual(self.actividad.estado, 'rechazada')


class AmbitoDelDelegadoTests(EscenarioBase, TestCase):
    """Un delegado ve solo la información y las métricas de su delegación."""

    def setUp(self):
        self.crear_escenario()
        for funcionario in (self.autor, crear_funcionario('func-rural', 'funcionario', cargo=self.cargo, delegacion=self.rural).funcionario):
            Indicador.generar(Meta.objects.create(item=self.item, funcionario=funcionario, valor_objetivo=10))
        self.delegado = crear_funcionario('delegado-ambito', 'delegado', cargo=self.cargo, delegacion=self.centro)
        self.coordinador = crear_funcionario('coord-ambito', 'coordinador', cargo=self.cargo)

    def test_las_metricas_del_delegado_son_solo_de_su_delegacion(self):
        """CU-29.1 Restricción por ámbito (RF-029, RF-032). Medición, semáforo y resumen solo muestran su delegación."""
        self.client.force_login(self.delegado)
        for nombre in ('dashboard', 'semaforo', 'resumen'):
            respuesta = self.client.get(reverse(nombre))
            self.assertEqual({fila['nombre'] for fila in respuesta.context['delegaciones']}, {'Centro'}, nombre)
        self.client.force_login(self.coordinador)
        self.assertEqual({fila['nombre'] for fila in self.client.get(reverse('dashboard')).context['delegaciones']}, {'Centro', 'Rural'})

    def test_el_panel_del_delegado_muestra_su_delegacion(self):
        """CU-18.1 Consolidar datos de delegación (RF-028, RF-029). El panel muestra su cumplimiento y el acceso a su delegación."""
        self.client.force_login(self.delegado)
        respuesta = self.client.get(reverse('panel'))
        self.assertEqual([fila['nombre'] for fila in respuesta.context['resultado_delegacion']], ['Centro'])
        self.assertContains(respuesta, reverse('delegacion_detalle', args=['Centro']))

    def test_el_delegado_no_abre_otra_delegacion(self):
        """CU-26.1 Denegar acceso por ámbito (RF-029). La delegación ajena no existe para él (404)."""
        self.client.force_login(self.delegado)
        self.assertEqual(self.client.get(reverse('delegacion_detalle', args=['Rural'])).status_code, 404)
        self.assertEqual([d.nombre for d in self.client.get(reverse('actividades')).context['delegaciones_filtro']], ['Centro'])

    def _datos_de_rural(self):
        """Actividad, tarea vencida y medición histórica en Rural, junto a las equivalentes de Centro."""
        rural = Funcionario.objects.get(identificador_institucional='func-rural')
        self.actividad_centro = self.nueva_actividad(solicitud_problema='Actividad de Centro')
        self.actividad_rural = self.nueva_actividad(funcionario_autor=rural, delegacion=self.rural, solicitud_problema='Actividad de Rural')
        self.tarea_centro = self.nuevo_compromiso(dias=-2, folio='AMB-CENTRO')
        self.tarea_rural = self.nuevo_compromiso(dias=-2, folio='AMB-RURAL', delegacion=self.rural, funcionario_responsable=rural)
        for delegacion in (self.centro, self.rural):
            MedicionDelegacion.objects.create(delegacion=delegacion, cumplimiento=50, meta=100, fecha_datos=date(2026, 8, 31), estado_reportado='rojo')
        self.client.force_login(self.delegado)

    def test_los_informes_del_delegado_son_solo_de_su_delegacion(self):
        """CU-26.1 Denegar acceso por ámbito (RF-029, RF-033). Los cinco informes, en pantalla y en CSV, solo traen su delegación."""
        self._datos_de_rural()
        informe = lambda **filtros: self.client.get(reverse('informe'), filtros)
        self.assertEqual([fila[0] for fila in informe(tipo='actividades').context['filas']], [self.actividad_centro.codigo_verificador])
        self.assertEqual([fila[0] for fila in informe(tipo='compromisos').context['filas']], ['AMB-CENTRO'])
        self.assertNotIn('func-rural', [fila[0] for fila in informe(tipo='resumen').context['filas']])
        self.assertEqual({fila[1] for fila in informe(tipo='reciente').context['filas']}, {'Centro'})
        self.assertEqual([fila[0] for fila in informe(tipo='cumplimiento').context['filas']], ['Centro'])
        self.assertEqual(informe(tipo='cumplimiento', delegacion=self.rural.pk).context['filas'], [])
        csv = informe(tipo='compromisos', formato='csv').content.decode('utf-8')
        self.assertIn('AMB-CENTRO', csv)
        self.assertNotIn('AMB-RURAL', csv)

    def test_las_alertas_del_delegado_son_solo_de_su_delegacion(self):
        """CU-26.1 Denegar acceso por ámbito (RF-029, RF-037). Ninguna alerta menciona otra delegación."""
        self._datos_de_rural()
        motivos = ' '.join(alerta['motivo'] for alerta in self.client.get(reverse('alertas')).context['alertas'])
        self.assertIn('AMB-CENTRO', motivos)
        self.assertNotIn('AMB-RURAL', motivos)
        self.assertNotIn('func-rural', motivos)

    def test_el_resumen_y_el_panel_no_mezclan_otras_delegaciones(self):
        """CU-18.1 Consolidar datos de delegación (RF-028, RF-029). Mediciones históricas y cifras del panel, solo de Centro."""
        self._datos_de_rural()
        historicas = self.client.get(reverse('resumen')).context['mediciones_historicas']
        self.assertEqual({medicion.delegacion.nombre for medicion in historicas}, {'Centro'})
        panel = self.client.get(reverse('panel')).context
        self.assertEqual((panel['actividades_total'], panel['compromisos_abiertos'], panel['compromisos_vencidos']), (1, 1, 1))

    def test_la_portada_del_delegado_muestra_solo_sus_cifras(self):
        """CU-18.1 Consolidar datos de delegación (RF-028, RF-029). Con sesión, la portada cuenta solo su delegación."""
        self._datos_de_rural()
        self.assertEqual(self.client.get(reverse('inicio')).context['total_solicitudes'], 1)
        self.client.logout()
        self.assertEqual(self.client.get(reverse('inicio')).context['total_solicitudes'], 2)

    def test_los_registros_de_otra_delegacion_responden_404(self):
        """CU-26.1 Denegar acceso por ámbito (RF-029). Actividad, evidencia, tarea y delegación ajenas no existen para él."""
        self._datos_de_rural()
        evidencia = self.nueva_evidencia(self.actividad_rural)
        codigo = self.actividad_rural.codigo_verificador
        urls = [
            reverse('actividad_detalle', args=[codigo]), reverse('evidencia_subir', args=[codigo]),
            reverse('evidencia_archivo', args=[evidencia.codigo_evidencia]), reverse('compromiso_editar', args=[self.tarea_rural.pk]),
            reverse('delegacion_detalle', args=['Rural']),
        ]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 404, url)
        for url in (reverse('revisar_actividad', args=[codigo, 'aprobar']), reverse('compromiso_estado', args=[self.tarea_rural.pk, 'proceso'])):
            self.assertEqual(self.client.post(url).status_code, 404, url)
        self.assertFalse(Validacion.objects.exists())


class CoordinacionDeDelegadosTests(EscenarioBase, TestCase):
    """El coordinador gestiona y asigna delegados; el delegado trabaja su delegación."""

    def setUp(self):
        self.crear_escenario()
        self.coordinador = crear_funcionario('coord-del', 'coordinador', cargo=self.cargo)
        self.delegado = crear_funcionario('delegado-sin', 'delegado', cargo=self.cargo)

    def test_el_coordinador_asigna_un_delegado_a_una_delegacion(self):
        """CU-26 Asignar delegado (RF-001, RF-017). Queda en la delegación y en la auditoría."""
        self.client.force_login(self.coordinador)
        self.assertEqual(self.client.get(reverse('delegados')).status_code, 200)
        self.client.post(reverse('delegados'), {'funcionario': self.delegado.funcionario.pk, 'delegacion': self.rural.pk})
        self.delegado.funcionario.refresh_from_db()
        self.assertEqual(self.delegado.funcionario.delegacion, self.rural)
        self.assertTrue(Auditoria.objects.filter(evento='asignar_delegado').exists())

    def test_el_delegado_no_entra_a_la_coordinacion(self):
        """CU-26.1 Separar coordinador y delegado (RF-002). La gestión de delegados es de la coordinación."""
        self.client.force_login(crear_funcionario('delegado-centro2', 'delegado', cargo=self.cargo, delegacion=self.centro))
        self.assertRedirects(self.client.get(reverse('delegados')), reverse('inicio'))

    def test_asignar_delegado_valida_el_formulario(self):
        """CU-26 Asignar delegado (RF-001, RF-017). Solo delegados activos, delegaciones activas y sin repetir la asignación."""
        self.client.force_login(self.coordinador)
        respuesta = self.client.post(reverse('delegados'), {'funcionario': self.autor.pk, 'delegacion': self.rural.pk})
        self.assertIn('funcionario', respuesta.context['form'].errors)
        self.rural.set_estado(False)
        respuesta = self.client.post(reverse('delegados'), {'funcionario': self.delegado.funcionario.pk, 'delegacion': self.rural.pk})
        self.assertIn('delegacion', respuesta.context['form'].errors)
        self.client.post(reverse('delegados'), {'funcionario': self.delegado.funcionario.pk, 'delegacion': self.centro.pk})
        respuesta = self.client.post(reverse('delegados'), {'funcionario': self.delegado.funcionario.pk, 'delegacion': self.centro.pk})
        self.assertContains(respuesta, 'ya es delegado de Centro')
        self.assertEqual(Auditoria.objects.filter(evento='asignar_delegado').count(), 1)

    def test_el_coordinador_no_sube_evidencias_en_nombre_de_otro(self):
        """CU-09 Subir evidencia (RF-012). La coordinación revisa, pero la evidencia la sube quien registró la actividad."""
        actividad = self.nueva_actividad()
        url = reverse('evidencia_subir', args=[actividad.codigo_verificador])
        self.client.force_login(self.coordinador)
        self.assertNotContains(self.client.get(reverse('actividades')), url)
        self.assertRedirects(self.client.get(url), reverse('actividad_detalle', args=[actividad.codigo_verificador]))
        self.client.post(url, {'comentario': 'En nombre del autor'})
        self.assertFalse(actividad.evidencias.exists())

    def test_el_coordinador_revisa_en_todas_las_delegaciones(self):
        """CU-11 Validación de actividades (RF-013). La coordinación aprueba evidencias de cualquier delegación."""
        actividad = self.nueva_actividad()
        self.nueva_evidencia(actividad)
        self.client.force_login(self.coordinador)
        self.client.post(reverse('revisar_actividad', args=[actividad.codigo_verificador, 'aprobar']))
        actividad.refresh_from_db()
        self.assertEqual(actividad.estado, 'aprobada')

    def test_el_panel_del_coordinador_muestra_todas_las_delegaciones_y_su_delegado(self):
        """CU-18.1 Consolidar datos de delegación (RF-028, RF-029). El coordinador ve cada delegación con su avance y su delegado."""
        for funcionario in (self.autor, crear_funcionario('func-rural-p', 'funcionario', cargo=self.cargo, delegacion=self.rural).funcionario):
            Indicador.generar(Meta.objects.create(item=self.item, funcionario=funcionario, valor_objetivo=10))
        self.delegado.funcionario.delegacion = self.centro
        self.delegado.funcionario.save()
        self.client.force_login(self.coordinador)
        respuesta = self.client.get(reverse('panel'))
        self.assertTemplateUsed(respuesta, 'gestion_app/panel_coordinador.html')
        filas = {fila['nombre']: fila['delegados'] for fila in respuesta.context['delegaciones']}
        self.assertEqual(filas, {'Centro': 'delegado-sin', 'Rural': ''})
        self.assertContains(respuesta, reverse('delegados'))
        self.assertNotContains(respuesta, reverse('actividad_nueva'))

    def test_el_panel_del_delegado_se_centra_en_su_delegacion(self):
        """CU-18.1 Consolidar datos de delegación (RF-028, RF-029). Lo que espera su revisión y el tubo, solo de su delegación."""
        delegado = crear_funcionario('delegado-panel', 'delegado', cargo=self.cargo, delegacion=self.centro)
        rural = crear_funcionario('func-rural-d', 'funcionario', cargo=self.cargo, delegacion=self.rural).funcionario
        de_centro = self.nueva_actividad()
        self.nueva_evidencia(de_centro)
        self.nueva_evidencia(self.nueva_actividad(funcionario_autor=rural, delegacion=self.rural))
        self.nuevo_compromiso(folio='PAN-CENTRO')
        self.nuevo_compromiso(folio='PAN-RURAL', delegacion=self.rural, funcionario_responsable=rural)
        self.client.force_login(delegado)
        respuesta = self.client.get(reverse('panel'))
        self.assertTemplateUsed(respuesta, 'gestion_app/panel_delegado.html')
        self.assertEqual(respuesta.context['por_revisar'], [de_centro])
        self.assertEqual([c.folio for c in respuesta.context['tareas_abiertas']], ['PAN-CENTRO'])
        self.assertNotContains(respuesta, reverse('delegados'))

    def test_el_coordinador_asigna_compromisos_a_delegados_de_la_delegacion(self):
        """CU-02.1 Validar datos de compromiso (RF-016, RF-017). El responsable debe ser de la delegación elegida."""
        self.client.force_login(self.coordinador)
        datos = {
            'delegacion': self.rural.pk, 'funcionario_responsable': self.autor.pk, 'origen': 'externo', 'solicitante': 'Junta',
            'territorio': 'Rural', 'eje': 'Seguridad', 'descripcion': 'Compromiso cruzado', 'fecha_comprometida': '2026-12-30', 'estado': 'pendiente',
        }
        respuesta = self.client.post(reverse('compromiso_nuevo'), datos)
        self.assertIn('funcionario_responsable', respuesta.context['form'].errors)
        self.assertContains(self.client.get(reverse('compromiso_nuevo')), 'Delegado responsable')

    def test_la_agenda_explica_quien_crea_compromisos(self):
        """CU-12 Agenda compartida (RF-016). La agenda dice quién crea y quién elimina."""
        self.client.force_login(self.coordinador)
        self.assertContains(self.client.get(reverse('agenda')), '+ Agregar al tubo de trabajo')
        self.nuevo_compromiso()
        self.client.force_login(self.usuario_autor)
        agenda = self.client.get(reverse('agenda'))
        self.assertContains(agenda, '¿Quién agrega tareas al tubo de trabajo?')
        self.assertContains(agenda, '+ Agregar al tubo de trabajo')
        self.assertNotContains(agenda, 'Eliminar</a>')


class ModificarEnSuPaginaTests(EscenarioBase, TestCase):
    """«Modificar» está en la página de cada registro (detalle o fila) y solo lo ve quien puede modificar."""

    def setUp(self):
        self.crear_escenario()
        self.companero = crear_funcionario('companero-mod', 'funcionario', cargo=self.cargo, delegacion=self.centro)
        self.coordinador = crear_funcionario('coord-mod', 'coordinador', cargo=self.cargo)

    def test_el_detalle_ofrece_modificar_actividad_a_su_autor(self):
        """CU-01 Registro de actividades (RF-009). El autor ve «Modificar actividad» en el detalle; otro funcionario no."""
        actividad = self.nueva_actividad()
        detalle, editar = reverse('actividad_detalle', args=[actividad.codigo_verificador]), reverse('actividad_editar', args=[actividad.codigo_verificador])
        self.client.force_login(self.usuario_autor)
        self.assertContains(self.client.get(detalle), f'href="{editar}">Modificar actividad</a>', html=False)
        self.client.force_login(self.companero)
        self.assertNotContains(self.client.get(detalle), editar)

    def test_una_actividad_aprobada_no_ofrece_modificar(self):
        """CU-11 Validación de actividades (RF-013). Aprobada ya suma al avance: ni el detalle ni la lista ofrecen modificarla."""
        actividad = self.nueva_actividad(estado='aprobada')
        editar = reverse('actividad_editar', args=[actividad.codigo_verificador])
        self.client.force_login(self.usuario_autor)
        self.assertNotContains(self.client.get(reverse('actividad_detalle', args=[actividad.codigo_verificador])), editar)
        self.assertNotContains(self.client.get(reverse('actividades')), editar)

    def test_la_lista_no_muestra_botones_desactivados(self):
        """CU-10.1 Buscar actividad por código (RF-032). Quien no puede modificar no ve Modificar ni Eliminar en la fila."""
        actividad = self.nueva_actividad()
        self.client.force_login(self.companero)
        lista = self.client.get(reverse('actividades'))
        self.assertNotContains(lista, 'disabled')
        self.assertNotContains(lista, reverse('actividad_editar', args=[actividad.codigo_verificador]))
        self.client.force_login(self.usuario_autor)
        self.assertContains(self.client.get(reverse('actividades')), reverse('actividad_editar', args=[actividad.codigo_verificador]))

    def test_la_fila_del_tubo_ofrece_modificar_solo_a_quien_puede(self):
        """CU-13 Actualización de estados (RF-018). El responsable y la coordinación ven Modificar y los estados; otro funcionario no."""
        compromiso = self.nuevo_compromiso()
        editar, estado = reverse('compromiso_editar', args=[compromiso.pk]), reverse('compromiso_estado', args=[compromiso.pk, 'proceso'])
        for usuario in (self.usuario_autor, self.coordinador):
            self.client.force_login(usuario)
            respuesta = self.client.get(reverse('agenda'))
            self.assertContains(respuesta, editar, msg_prefix=usuario.username)
            self.assertContains(respuesta, estado, msg_prefix=usuario.username)
        self.client.force_login(self.companero)
        respuesta = self.client.get(reverse('agenda'))
        self.assertNotContains(respuesta, editar)
        self.assertNotContains(respuesta, estado)
        self.assertContains(respuesta, 'Solo lectura')

    def test_cambiar_el_estado_exige_ser_responsable(self):
        """CU-13 Actualización de estados (RF-018). Quien no es responsable no cambia el estado aunque envíe el formulario."""
        compromiso = self.nuevo_compromiso()
        self.client.force_login(self.companero)
        self.client.post(reverse('compromiso_estado', args=[compromiso.pk, 'proceso']))
        compromiso.refresh_from_db()
        self.assertEqual(compromiso.estado, 'ingresado')
        self.assertFalse(compromiso.historial.exists())
        self.assertTrue(Auditoria.objects.filter(evento='acceso_denegado', identificador_registro=compromiso.folio).exists())

    def test_modificar_una_tarea_de_otra_delegacion_responde_404(self):
        """CU-26.1 Denegar acceso por ámbito (RF-016). Una tarea de otra delegación no existe para el usuario."""
        compromiso = self.nuevo_compromiso()
        self.client.force_login(crear_funcionario('rural-mod', 'funcionario', cargo=self.cargo, delegacion=self.rural))
        self.assertEqual(self.client.get(reverse('compromiso_editar', args=[compromiso.pk])).status_code, 404)


class ListasSinBotonesFalsosTests(EscenarioBase, TestCase):
    """Las listas de solicitudes y de la delegación no muestran botones sin función: llevan a la fila del tubo."""

    def setUp(self):
        self.crear_escenario()
        self.nuevo_compromiso(folio='LST-1', descripcion='Poda de árboles')
        self.nuevo_compromiso(folio='LST-2', descripcion='Luminaria apagada')

    def test_no_hay_botones_modificar_ni_eliminar_sin_destino(self):
        """CU-13 Actualización de estados (RF-018). Modificar está solo en la fila del tubo, para quien puede."""
        self.client.force_login(self.usuario_autor)
        for url in (reverse('solicitudes'), reverse('delegacion_detalle', args=['Centro'])):
            respuesta = self.client.get(url)
            self.assertNotContains(respuesta, 'href="#"', msg_prefix=url)
            self.assertContains(respuesta, f'{reverse("agenda")}?q=LST-1', msg_prefix=url)

    def test_el_buscador_de_la_delegacion_filtra(self):
        """CU-12.1 Filtrar agenda compartida (RF-032). El buscador de la delegación filtra por folio o descripción."""
        self.client.force_login(self.usuario_autor)
        respuesta = self.client.get(reverse('delegacion_detalle', args=['Centro']), {'q': 'luminaria'})
        self.assertEqual([c.folio for c in respuesta.context['solicitudes']], ['LST-2'])
