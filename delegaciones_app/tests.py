from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from django.core.exceptions import ValidationError

from .models import Actividad, Auditoria, Compromiso, Delegacion, HistorialCompromiso, MetaMedicion, PerfilUsuario, PeriodoMedicion


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
