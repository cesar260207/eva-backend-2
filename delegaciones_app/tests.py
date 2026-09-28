import shutil
import tempfile
from datetime import date

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from django.core.exceptions import ValidationError

from .forms import EvidenciaMantenedorForm
from .models import Actividad, Auditoria, CatalogoItem, Compromiso, Delegacion, Evidencia, HistorialCompromiso, MetaMedicion, PerfilUsuario, PeriodoMedicion


class SGRMVPTests(TestCase):
	def setUp(self):
		self.delegacion = Delegacion.objects.create(nombre='Centro', territorio='Centro', enfasis='Atencion territorial')
		self.otra_delegacion = Delegacion.objects.create(nombre='Rural', territorio='Rural', enfasis='Servicios cercanos')
		self.coordinador = User.objects.create_user('coordinador', password='clave-segura')
		PerfilUsuario.objects.create(usuario=self.coordinador, rol='coordinador')
		self.funcionario = User.objects.create_user('funcionario', password='clave-segura')
		PerfilUsuario.objects.create(usuario=self.funcionario, rol='funcionario', delegacion=self.delegacion)

	def test_coordinador_puede_administrar_delegaciones(self):
		self.client.force_login(self.coordinador)
		response = self.client.post(reverse('delegacion_nueva'), {'nombre': 'La Antena', 'territorio': 'Oriente', 'enfasis': 'Participacion', 'activa': 'on'})
		self.assertRedirects(response, reverse('delegaciones_crud'))
		self.assertTrue(Delegacion.objects.filter(nombre='La Antena').exists())

	def test_funcionario_no_puede_administrar_delegaciones(self):
		self.client.force_login(self.funcionario)
		response = self.client.get(reverse('delegaciones_crud'))
		self.assertRedirects(response, reverse('inicio'))

	def test_coordinador_visualiza_los_ocho_mantenedores(self):
		self.client.force_login(self.coordinador)
		response = self.client.get(reverse('mantenedores'))
		self.assertContains(response, 'Ocho mantenedores')
		for slug in ('delegaciones', 'perfiles', 'catalogo', 'periodos', 'actividades', 'evidencias', 'compromisos', 'metas'):
			response = self.client.get(reverse('mantenedor_lista', args=[slug]))
			self.assertEqual(response.status_code, 200)
			self.assertContains(response, 'Agregar')
			self.assertContains(response, 'Buscar')

	def test_actividad_genera_codigo_y_auditoria(self):
		self.client.force_login(self.funcionario)
		response = self.client.post(reverse('actividad_nueva'), {'delegacion': self.delegacion.pk, 'fecha': '2026-09-07', 'tipo_atencion': 'Solicitud ciudadana', 'descripcion': 'Consulta vecinal', 'accion': 'Orientacion y derivacion', 'item_medicion': 'Atencion territorial', 'contacto': 'Organizacion demo', 'telefono': ''})
		self.assertEqual(response.status_code, 302)
		actividad = Actividad.objects.get(descripcion='Consulta vecinal')
		self.assertTrue(actividad.codigo.startswith('EVD-'))
		self.assertTrue(Auditoria.objects.filter(entidad='Actividad', identificador=actividad.codigo).exists())

	def test_funcionario_ve_solo_su_delegacion(self):
		Actividad.objects.create(codigo='EVD-TEST-1', funcionario=self.funcionario, delegacion=self.delegacion, fecha=date(2026, 9, 1), tipo_atencion='Solicitud', descripcion='Visible', accion='Accion', item_medicion='Item')
		otro = User.objects.create_user('otro', password='clave-segura')
		Actividad.objects.create(codigo='EVD-TEST-2', funcionario=otro, delegacion=self.otra_delegacion, fecha=date(2026, 9, 1), tipo_atencion='Solicitud', descripcion='No visible', accion='Accion', item_medicion='Item')
		self.client.force_login(self.funcionario)
		response = self.client.get(reverse('actividades'))
		self.assertContains(response, 'EVD-TEST-1')
		self.assertNotContains(response, 'EVD-TEST-2')

	def test_compromiso_persistente_y_cambio_de_estado_auditado(self):
		self.client.force_login(self.funcionario)
		response = self.client.post(reverse('compromiso_nuevo'), {'delegacion': self.delegacion.pk, 'responsable': self.funcionario.pk, 'solicitante': 'Organizacion demo', 'territorio': 'Centro', 'eje': 'Seguridad', 'descripcion': 'Compromiso de prueba', 'fecha_comprometida': '2026-09-30', 'estado': 'pendiente', 'observacion': ''})
		self.assertRedirects(response, reverse('agenda'))
		compromiso = Compromiso.objects.get(descripcion='Compromiso de prueba')
		self.assertContains(self.client.get(reverse('agenda')), compromiso.folio)
		self.client.post(reverse('compromiso_estado', args=[compromiso.pk, 'realizado']))
		compromiso.refresh_from_db()
		self.assertEqual(compromiso.estado, 'realizado')
		self.assertEqual(HistorialCompromiso.objects.filter(compromiso=compromiso).count(), 2)

	def test_meta_cuenta_solo_actividades_aprobadas(self):
		MetaMedicion.objects.create(delegacion=self.delegacion, nombre='Item', objetivo=2, periodo_inicio=date(2026, 9, 1), periodo_termino=date(2026, 9, 30), ponderador=100)
		Actividad.objects.create(codigo='EVD-APPROVED', funcionario=self.funcionario, delegacion=self.delegacion, fecha=date(2026, 9, 2), tipo_atencion='Solicitud', descripcion='Aprobada', accion='Accion', item_medicion='Item', estado='aprobada')
		Actividad.objects.create(codigo='EVD-PENDING', funcionario=self.funcionario, delegacion=self.delegacion, fecha=date(2026, 9, 2), tipo_atencion='Solicitud', descripcion='Pendiente', accion='Accion', item_medicion='Item', estado='pendiente')
		meta = MetaMedicion.objects.get(nombre='Item')
		self.assertEqual(meta.avance_calculado, 1)
		self.assertEqual(meta.cumplimiento, 50)

	def test_periodo_rechaza_termino_anterior(self):
		periodo = PeriodoMedicion(nombre='Inválido', inicio=date(2026, 9, 30), termino=date(2026, 9, 1))
		with self.assertRaises(ValidationError):
			periodo.full_clean()

	def test_logout_invalida_la_sesion(self):
		self.client.force_login(self.funcionario)
		response = self.client.post(reverse('logout'))
		self.assertRedirects(response, reverse('inicio'))
		self.assertFalse('_auth_user_id' in self.client.session)


class CatalogoCRUDTests(TestCase):
	def setUp(self):
		self.delegacion = Delegacion.objects.create(nombre='Centro', territorio='Centro', enfasis='Atencion territorial')
		self.coordinador = User.objects.create_user('coordinador-catalogo', password='clave-segura')
		PerfilUsuario.objects.create(usuario=self.coordinador, rol='coordinador')
		self.funcionario = User.objects.create_user('funcionario-catalogo', password='clave-segura')
		PerfilUsuario.objects.create(usuario=self.funcionario, rol='funcionario', delegacion=self.delegacion)
		self.client.force_login(self.coordinador)

	def test_ruta_catalogo_muestra_su_lista_y_busca(self):
		CatalogoItem.objects.create(categoria='servicio', codigo='SRV-01', nombre='Orientacion vecinal')
		CatalogoItem.objects.create(categoria='actividad', codigo='ACT-02', nombre='Operativo rural')

		response = self.client.get(reverse('mantenedor_lista', args=['catalogo']), {'q': 'SRV-01'})

		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'delegaciones_app/catalogo_lista.html')
		self.assertContains(response, 'Orientacion vecinal')
		self.assertNotContains(response, 'Operativo rural')

	def test_crear_item_y_registrar_auditoria(self):
		response = self.client.post(reverse('catalogo_nuevo'), {
			'categoria': 'servicio', 'codigo': 'SRV-NUEVO', 'nombre': 'Atencion comunitaria',
			'area': 'Territorio', 'activo': 'on',
		})

		self.assertRedirects(response, reverse('catalogo_lista'))
		item = CatalogoItem.objects.get(categoria='servicio', codigo='SRV-NUEVO')
		self.assertTrue(Auditoria.objects.filter(entidad='CatalogoItem', identificador=str(item.pk), accion='crear').exists())

	def test_formulario_rechaza_categoria_y_codigo_duplicados(self):
		CatalogoItem.objects.create(categoria='servicio', codigo='SRV-DUP', nombre='Existente')

		response = self.client.post(reverse('catalogo_nuevo'), {
			'categoria': 'servicio', 'codigo': 'SRV-DUP', 'nombre': 'Duplicado',
			'area': '', 'activo': 'on',
		})

		self.assertEqual(response.status_code, 200)
		self.assertFalse(response.context['form'].is_valid())
		self.assertTrue(response.context['form'].errors)
		self.assertEqual(CatalogoItem.objects.filter(categoria='servicio', codigo='SRV-DUP').count(), 1)

	def test_eliminar_requiere_confirmacion_post_y_audita(self):
		item = CatalogoItem.objects.create(categoria='servicio', codigo='SRV-BORRAR', nombre='Temporal')

		response = self.client.get(reverse('catalogo_eliminar', args=[item.pk]))
		self.assertEqual(response.status_code, 200)
		self.assertTrue(CatalogoItem.objects.filter(pk=item.pk).exists())

		response = self.client.post(reverse('catalogo_eliminar', args=[item.pk]))
		self.assertRedirects(response, reverse('catalogo_lista'))
		self.assertFalse(CatalogoItem.objects.filter(pk=item.pk).exists())
		self.assertTrue(Auditoria.objects.filter(entidad='CatalogoItem', identificador=str(item.pk), accion='eliminar').exists())

	def test_funcionario_no_puede_entrar_al_mantenedor(self):
		self.client.force_login(self.funcionario)

		response = self.client.get(reverse('catalogo_lista'))

		self.assertRedirects(response, reverse('inicio'))


class ActividadCRUDTests(TestCase):
	def setUp(self):
		self.centro = Delegacion.objects.create(nombre='Centro', territorio='Centro', enfasis='Atencion territorial')
		self.rural = Delegacion.objects.create(nombre='Rural', territorio='Rural', enfasis='Servicios cercanos')
		self.coordinador = User.objects.create_user('coordinador-actividad', password='clave-segura')
		PerfilUsuario.objects.create(usuario=self.coordinador, rol='coordinador')
		self.funcionario = User.objects.create_user('funcionario-actividad', password='clave-segura')
		PerfilUsuario.objects.create(usuario=self.funcionario, rol='funcionario', delegacion=self.centro)
		self.actividad = self._crear_actividad('EVD-CRUD-1')
		self.client.force_login(self.funcionario)

	def _crear_actividad(self, codigo, estado='pendiente'):
		return Actividad.objects.create(codigo=codigo, funcionario=self.funcionario, delegacion=self.centro, fecha=date(2026, 9, 1), tipo_atencion='Solicitud', descripcion='Descripcion original', accion='Accion', item_medicion='Item', estado=estado)

	def _datos(self, **cambios):
		datos = {'delegacion': self.centro.pk, 'fecha': '2026-09-01', 'tipo_atencion': 'Solicitud', 'descripcion': 'Descripcion corregida', 'accion': 'Accion', 'item_medicion': 'Item', 'contacto': '', 'telefono': ''}
		datos.update(cambios)
		return datos

	def test_listado_enlaza_modificar_y_eliminar_reales(self):
		response = self.client.get(reverse('actividades'))

		self.assertContains(response, reverse('actividad_editar', args=[self.actividad.codigo]))
		self.assertContains(response, reverse('actividad_eliminar', args=[self.actividad.codigo]))
		self.assertNotContains(response, 'href="#"')

	def test_autor_edita_su_actividad_y_audita(self):
		url = reverse('actividad_editar', args=[self.actividad.codigo])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'delegaciones_app/actividad_form.html')

		response = self.client.post(url, self._datos())

		self.assertRedirects(response, reverse('actividad_detalle', args=[self.actividad.codigo]))
		self.actividad.refresh_from_db()
		self.assertEqual(self.actividad.descripcion, 'Descripcion corregida')
		self.assertEqual(self.actividad.funcionario, self.funcionario)
		self.assertEqual(self.actividad.estado, 'pendiente')
		self.assertTrue(Auditoria.objects.filter(entidad='Actividad', identificador=self.actividad.codigo, accion='editar').exists())

	def test_editar_actividad_rechazada_la_devuelve_a_revision(self):
		self.actividad.estado = 'rechazada'
		self.actividad.save()

		self.client.post(reverse('actividad_editar', args=[self.actividad.codigo]), self._datos())

		self.actividad.refresh_from_db()
		self.assertEqual(self.actividad.estado, 'pendiente')

	def test_actividad_aprobada_no_se_edita_ni_se_elimina(self):
		aprobada = self._crear_actividad('EVD-CRUD-OK', estado='aprobada')
		self.client.force_login(self.coordinador)
		detalle = reverse('actividad_detalle', args=[aprobada.codigo])

		self.assertNotContains(self.client.get(reverse('actividades')), reverse('actividad_editar', args=[aprobada.codigo]))
		response = self.client.post(reverse('actividad_editar', args=[aprobada.codigo]), self._datos())
		self.assertRedirects(response, detalle)
		response = self.client.post(reverse('actividad_eliminar', args=[aprobada.codigo]))
		self.assertRedirects(response, detalle)

		aprobada.refresh_from_db()
		self.assertEqual(aprobada.descripcion, 'Descripcion original')
		self.assertFalse(Auditoria.objects.filter(identificador=aprobada.codigo).exists())

	def test_eliminar_requiere_confirmacion_post_y_borra_sus_evidencias(self):
		Evidencia.objects.create(actividad=self.actividad, archivo='evidencias/2026/09/respaldo.pdf')
		url = reverse('actividad_eliminar', args=[self.actividad.codigo])

		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['total_evidencias'], 1)
		self.assertContains(response, 'también se eliminan sus evidencias')
		self.assertTrue(Actividad.objects.filter(pk=self.actividad.pk).exists())

		response = self.client.post(url)
		self.assertRedirects(response, reverse('actividades'))
		self.assertFalse(Actividad.objects.filter(pk=self.actividad.pk).exists())
		self.assertFalse(Evidencia.objects.filter(actividad_id=self.actividad.pk).exists())
		self.assertTrue(Auditoria.objects.filter(entidad='Actividad', identificador=self.actividad.codigo, accion='eliminar').exists())

	def test_funcionario_de_otra_delegacion_no_puede_editar_ni_eliminar(self):
		intruso = User.objects.create_user('funcionario-rural', password='clave-segura')
		PerfilUsuario.objects.create(usuario=intruso, rol='funcionario', delegacion=self.rural)
		self.client.force_login(intruso)
		codigo = self.actividad.codigo

		self.assertEqual(self.client.get(reverse('actividad_editar', args=[codigo])).status_code, 404)
		self.assertEqual(self.client.post(reverse('actividad_editar', args=[codigo]), self._datos()).status_code, 404)
		self.assertEqual(self.client.post(reverse('actividad_eliminar', args=[codigo])).status_code, 404)

		self.actividad.refresh_from_db()
		self.assertEqual(self.actividad.descripcion, 'Descripcion original')
		self.assertFalse(Auditoria.objects.filter(identificador=codigo).exists())

	def test_funcionario_de_la_misma_delegacion_que_no_es_autor_no_puede_modificar(self):
		companero = User.objects.create_user('funcionario-centro-2', password='clave-segura')
		PerfilUsuario.objects.create(usuario=companero, rol='funcionario', delegacion=self.centro)
		self.client.force_login(companero)
		detalle = reverse('actividad_detalle', args=[self.actividad.codigo])

		self.assertRedirects(self.client.get(reverse('actividad_editar', args=[self.actividad.codigo])), detalle)
		self.assertRedirects(self.client.post(reverse('actividad_eliminar', args=[self.actividad.codigo])), detalle)
		self.assertTrue(Actividad.objects.filter(pk=self.actividad.pk).exists())

	def test_coordinador_puede_modificar_actividad_ajena(self):
		self.client.force_login(self.coordinador)

		response = self.client.post(reverse('actividad_editar', args=[self.actividad.codigo]), self._datos(descripcion='Ajustada por coordinacion'))

		self.assertRedirects(response, reverse('actividad_detalle', args=[self.actividad.codigo]))
		self.actividad.refresh_from_db()
		self.assertEqual(self.actividad.descripcion, 'Ajustada por coordinacion')
		self.assertEqual(self.actividad.funcionario, self.funcionario)

	def test_tarjeta_de_mantenedores_enlaza_al_listado_de_actividades(self):
		self.client.force_login(self.coordinador)

		response = self.client.get(reverse('mantenedores'))

		self.assertContains(response, f'href="{reverse("actividades")}"')
		self.assertNotContains(response, f'href="{reverse("mantenedor_lista", args=["actividades"])}"')


class EvidenciaCRUDTests(TestCase):
	def setUp(self):
		media = tempfile.mkdtemp()
		self.addCleanup(shutil.rmtree, media, ignore_errors=True)
		ajuste_media = override_settings(MEDIA_ROOT=media)
		ajuste_media.enable()
		self.addCleanup(ajuste_media.disable)

		self.delegacion = Delegacion.objects.create(nombre='Centro', territorio='Centro', enfasis='Atencion territorial')
		self.coordinador = User.objects.create_user('coordinador-evidencia', password='clave-segura')
		PerfilUsuario.objects.create(usuario=self.coordinador, rol='coordinador')
		self.funcionario = User.objects.create_user('funcionario-evidencia', password='clave-segura')
		PerfilUsuario.objects.create(usuario=self.funcionario, rol='funcionario', delegacion=self.delegacion)
		self.actividad = Actividad.objects.create(codigo='EVD-EVID-1', funcionario=self.funcionario, delegacion=self.delegacion, fecha=date(2026, 9, 1), tipo_atencion='Solicitud', descripcion='Primera', accion='Accion', item_medicion='Item')
		self.aprobada = Actividad.objects.create(codigo='EVD-EVID-2', funcionario=self.funcionario, delegacion=self.delegacion, fecha=date(2026, 9, 2), tipo_atencion='Solicitud', descripcion='Segunda', accion='Accion', item_medicion='Item', estado='aprobada')
		self.client.force_login(self.coordinador)

	def _archivo(self, nombre='respaldo.pdf'):
		return SimpleUploadedFile(nombre, b'%PDF-1.4 prueba', content_type='application/pdf')

	def test_ruta_evidencias_muestra_su_lista_y_busca_por_codigo_y_comentario(self):
		evidencia = Evidencia.objects.create(actividad=self.actividad, archivo='evidencias/uno.pdf', comentario='Acta de reunion vecinal')
		Evidencia.objects.create(actividad=self.aprobada, archivo='evidencias/dos.pdf', comentario='Fotografia de operativo')

		response = self.client.get(reverse('mantenedor_lista', args=['evidencias']), {'q': 'EVD-EVID-1'})

		self.assertTemplateUsed(response, 'delegaciones_app/evidencia_lista.html')
		self.assertContains(response, 'Acta de reunion vecinal')
		self.assertNotContains(response, 'Fotografia de operativo')
		for url in (reverse('evidencia_nueva'), reverse('evidencia_editar', args=[evidencia.pk]), reverse('evidencia_eliminar', args=[evidencia.pk])):
			self.assertContains(response, url)

		response = self.client.get(reverse('evidencia_lista'), {'q': 'operativo'})
		self.assertContains(response, 'Fotografia de operativo')
		self.assertNotContains(response, 'Acta de reunion vecinal')

	def test_crear_evidencia_sube_archivo_y_audita_sin_cambiar_la_actividad(self):
		response = self.client.post(reverse('evidencia_nueva'), {'actividad': self.aprobada.pk, 'archivo': self._archivo(), 'comentario': 'Respaldo inicial', 'aprobada': 'unknown'})

		self.assertRedirects(response, reverse('evidencia_lista'))
		evidencia = Evidencia.objects.get(comentario='Respaldo inicial')
		self.assertEqual(evidencia.actividad, self.aprobada)
		self.assertTrue(evidencia.archivo.name.endswith('.pdf'))
		self.assertIsNone(evidencia.aprobada)
		self.assertIsNone(evidencia.revisada_por)
		self.assertTrue(Auditoria.objects.filter(entidad='Evidencia', identificador=str(evidencia.pk), accion='crear').exists())
		self.aprobada.refresh_from_db()
		self.assertEqual(self.aprobada.estado, 'aprobada')

	def test_rechaza_extension_no_permitida(self):
		archivo = SimpleUploadedFile('script.exe', b'MZ', content_type='application/octet-stream')

		response = self.client.post(reverse('evidencia_nueva'), {'actividad': self.actividad.pk, 'archivo': archivo, 'comentario': '', 'aprobada': 'unknown'})

		self.assertEqual(response.status_code, 200)
		self.assertIn('archivo', response.context['form'].errors)
		self.assertFalse(Evidencia.objects.exists())

	def test_editar_sin_archivo_nuevo_conserva_el_actual(self):
		evidencia = Evidencia.objects.create(actividad=self.actividad, archivo=self._archivo('original.pdf'), comentario='Antes')
		archivo_original = evidencia.archivo.name
		url = reverse('evidencia_editar', args=[evidencia.pk])
		self.assertContains(self.client.get(url), 'enctype="multipart/form-data"')

		response = self.client.post(url, {'actividad': self.actividad.pk, 'comentario': 'Despues', 'aprobada': 'unknown'})

		self.assertRedirects(response, reverse('evidencia_lista'))
		evidencia.refresh_from_db()
		self.assertEqual(evidencia.archivo.name, archivo_original)
		self.assertEqual(evidencia.comentario, 'Despues')
		self.assertTrue(Auditoria.objects.filter(entidad='Evidencia', identificador=str(evidencia.pk), accion='editar').exists())

	def test_validador_marca_revision_y_queda_como_revisor(self):
		evidencia = Evidencia.objects.create(actividad=self.actividad, archivo='evidencias/revision.pdf')

		self.client.post(reverse('evidencia_editar', args=[evidencia.pk]), {'actividad': self.actividad.pk, 'comentario': '', 'aprobada': 'true'})

		evidencia.refresh_from_db()
		self.assertTrue(evidencia.aprobada)
		self.assertEqual(evidencia.revisada_por, self.coordinador)

	def test_revision_solo_se_ofrece_a_quien_puede_validar(self):
		self.assertIn('aprobada', EvidenciaMantenedorForm(puede_validar=True).fields)
		self.assertNotIn('aprobada', EvidenciaMantenedorForm(puede_validar=False).fields)

	def test_eliminar_requiere_confirmacion_post_y_audita(self):
		evidencia = Evidencia.objects.create(actividad=self.actividad, archivo='evidencias/borrar.pdf')
		url = reverse('evidencia_eliminar', args=[evidencia.pk])

		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertTrue(Evidencia.objects.filter(pk=evidencia.pk).exists())

		response = self.client.post(url)
		self.assertRedirects(response, reverse('evidencia_lista'))
		self.assertFalse(Evidencia.objects.filter(pk=evidencia.pk).exists())
		self.assertTrue(Actividad.objects.filter(pk=self.actividad.pk).exists())
		self.assertTrue(Auditoria.objects.filter(entidad='Evidencia', identificador=str(evidencia.pk), accion='eliminar').exists())

	def test_funcionario_y_verificador_no_pueden_usar_el_mantenedor(self):
		evidencia = Evidencia.objects.create(actividad=self.actividad, archivo='evidencias/protegida.pdf', comentario='Original')
		verificador = User.objects.create_user('verificador-evidencia', password='clave-segura')
		PerfilUsuario.objects.create(usuario=verificador, rol='verificador')
		urls = (reverse('evidencia_lista'), reverse('evidencia_nueva'), reverse('evidencia_editar', args=[evidencia.pk]), reverse('evidencia_eliminar', args=[evidencia.pk]))

		for usuario in (self.funcionario, verificador):
			self.client.force_login(usuario)
			for url in urls:
				self.assertRedirects(self.client.get(url), reverse('inicio'))
			self.assertRedirects(self.client.post(reverse('evidencia_eliminar', args=[evidencia.pk])), reverse('inicio'))

		self.assertTrue(Evidencia.objects.filter(pk=evidencia.pk, comentario='Original').exists())
