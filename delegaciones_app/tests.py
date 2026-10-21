import shutil
import tempfile
from datetime import date

from django.contrib.auth.models import AnonymousUser, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import RequestFactory, TestCase, TransactionTestCase, override_settings
from django.urls import reverse

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from django.http import HttpResponse
from django.views import View

from .crud import MANTENEDORES
from .permisos import RolRequeridoMixin, roles_de, rol_requerido, tiene_rol
from .models import (
	Actividad, Auditoria, Cargo, Catalogo, Compromiso, Delegacion, Evidencia, Funcionario, FuncionarioRol,
	HistorialCompromiso, Indicador, ItemMedible, Meta, MetaMedicion, ParametroVersionado, PerfilUsuario, Periodo,
	PeriodoMedicion, Rol, UsuarioMaestro, Validacion,
)
from datetime import datetime
from decimal import Decimal
from django.utils import timezone


class SGRMVPTests(TestCase):
	def setUp(self):
		self.delegacion = Delegacion.objects.create(nombre='Centro', territorio='Centro', enfasis='Atencion territorial')
		self.otra_delegacion = Delegacion.objects.create(nombre='Rural', territorio='Rural', enfasis='Servicios cercanos')
		self.coordinador = User.objects.create_user('coordinador', password='clave-segura')
		PerfilUsuario.objects.create(usuario=self.coordinador, rol='coordinador')
		self.funcionario = User.objects.create_user('funcionario', password='clave-segura')
		PerfilUsuario.objects.create(usuario=self.funcionario, rol='funcionario', delegacion=self.delegacion)

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

class AccesoAutenticadoTests(TestCase):
	"""RNF-004 (acceso con identidad individual) y CU-29.1 (resultados limitados al ámbito)."""

	def setUp(self):
		self.centro = Delegacion.objects.create(nombre='Centro', territorio='Centro', enfasis='Atencion territorial')
		self.rural = Delegacion.objects.create(nombre='Rural', territorio='Rural', enfasis='Servicios cercanos')
		self.coordinador = User.objects.create_user('coordinador-acceso', password='clave-segura')
		PerfilUsuario.objects.create(usuario=self.coordinador, rol='coordinador')
		self.funcionario = User.objects.create_user('funcionario-acceso', password='clave-segura')
		PerfilUsuario.objects.create(usuario=self.funcionario, rol='funcionario', delegacion=self.centro)
		datos = {'responsable': self.coordinador, 'solicitante': 'Junta de vecinos demo', 'territorio': 'Sector demo', 'descripcion': 'Compromiso demo', 'fecha_comprometida': date(2026, 12, 31)}
		Compromiso.objects.create(folio='FOL-CENTRO-1', delegacion=self.centro, **datos)
		Compromiso.objects.create(folio='FOL-RURAL-1', delegacion=self.rural, **datos)

	def test_vistas_internas_exigen_inicio_de_sesion(self):
		urls = (
			reverse('solicitudes'), reverse('agenda'), reverse('delegacion_detalle', args=['Centro']),
			reverse('dashboard'), reverse('semaforo'), reverse('resumen'),
		)
		for url in urls:
			response = self.client.get(url)
			self.assertRedirects(response, f"{reverse('login')}?next={url}")

	def test_portada_y_territorio_siguen_publicos(self):
		self.assertEqual(self.client.get(reverse('inicio')).status_code, 200)
		self.assertEqual(self.client.get(reverse('institucional')).status_code, 200)

	def test_funcionario_solo_ve_compromisos_de_su_delegacion(self):
		self.client.force_login(self.funcionario)
		for url in (reverse('solicitudes'), reverse('agenda')):
			response = self.client.get(url)
			self.assertContains(response, 'FOL-CENTRO-1')
			self.assertNotContains(response, 'FOL-RURAL-1')
		response = self.client.get(reverse('delegacion_detalle', args=['Rural']))
		self.assertNotContains(response, 'FOL-RURAL-1')

	def test_coordinador_ve_compromisos_de_todas_las_delegaciones(self):
		self.client.force_login(self.coordinador)
		response = self.client.get(reverse('solicitudes'))
		self.assertContains(response, 'FOL-CENTRO-1')
		self.assertContains(response, 'FOL-RURAL-1')


class OrganizacionAccesoTests(TestCase):
	"""Etapa 1: métodos de Delegacion, Cargo, Funcionario y Auditoria (se amplían con sus CU en la Etapa 6)."""

	def setUp(self):
		self.centro = Delegacion.objects.create(nombre='Centro', territorio='Centro', enfasis='Atencion territorial')
		self.rural = Delegacion.objects.create(nombre='Rural', territorio='Rural', enfasis='Servicios cercanos')
		self.cargo = Cargo.objects.create(nombre='Profesional territorial')
		self.usuario = User.objects.create_user('func.centro', password='clave-segura')
		self.funcionario = Funcionario.objects.create(usuario=self.usuario, identificador_institucional='func.centro', nombre='Funcionario Centro', cargo=self.cargo, delegacion=self.centro)

	def test_identificadores(self):
		self.assertEqual(self.funcionario.get_identificador(), 'func.centro')
		self.assertEqual(self.centro.get_identificador(), 'Centro')

	def test_delegacion_asigna_funcionario_y_cambia_estado(self):
		self.rural.asignar_funcionario(self.funcionario)
		self.rural.set_estado(False)
		self.funcionario.refresh_from_db()
		self.rural.refresh_from_db()
		self.assertEqual(self.funcionario.delegacion, self.rural)
		self.assertFalse(self.rural.estado)

	def test_reasignar_cargo_exige_cargo_vigente(self):
		vigente = Cargo.objects.create(nombre='Delegado territorial')
		no_vigente = Cargo.objects.create(nombre='Cargo antiguo', vigencia=False)
		self.funcionario.reasignar_cargo(vigente)
		self.assertEqual(Funcionario.objects.get(pk=self.funcionario.pk).cargo, vigente)
		with self.assertRaises(ValidationError):
			self.funcionario.reasignar_cargo(no_vigente)

	def test_rol_no_se_repite_para_el_mismo_funcionario(self):
		# La migración 0010 crea los 6 roles del sistema.
		rol = Rol.objects.get(nombre_rol='funcionario')
		FuncionarioRol.objects.create(funcionario=self.funcionario, rol=rol)
		self.assertQuerySetEqual(self.funcionario.roles.all(), [rol])
		with self.assertRaises(IntegrityError), transaction.atomic():
			FuncionarioRol.objects.create(funcionario=self.funcionario, rol=rol)

	def test_registrar_evento_a_nombre_del_funcionario(self):
		evento = Auditoria.registrar_evento(self.usuario, 'editar', 'Compromiso', 'LS-1', {'estado': 'pendiente'}, {'estado': 'realizado'})
		self.assertEqual(evento.funcionario, self.funcionario)
		self.assertIsNone(evento.usuario_maestro)
		self.assertEqual(evento.evento, 'editar')
		self.assertEqual(evento.identificador_registro, 'LS-1')
		self.assertEqual(evento.valor_nuevo, '{"estado": "realizado"}')

	def test_registrar_evento_a_nombre_del_usuario_maestro(self):
		admin = User.objects.create_superuser('admin.prueba', password='clave-segura')
		maestro = UsuarioMaestro.objects.create(usuario=admin, identificador_maestro='admin.prueba', nombre='Admin', nivel_dominio='total')
		evento = Auditoria.registrar_evento(admin, 'crear', 'Delegacion', 7)
		self.assertEqual(evento.usuario_maestro, maestro)
		self.assertIsNone(evento.funcionario)
		self.assertEqual(evento.identificador_registro, '7')


class MedicionTests(TestCase):
	"""Etapa 2: reglas RN-001 a RN-008 y RN-013 (se amplían con sus CU en la Etapa 6)."""

	def setUp(self):
		self.centro = Delegacion.objects.create(nombre='Centro', territorio='Centro', enfasis='Atencion territorial')
		self.cargo = Cargo.objects.create(nombre='Profesional territorial')
		self.usuario = User.objects.create_user('func.medicion', password='clave-segura')
		self.funcionario = Funcionario.objects.create(usuario=self.usuario, identificador_institucional='func.medicion', nombre='Funcionario Medicion', cargo=self.cargo, delegacion=self.centro)
		self.periodo = Periodo.objects.create(nombre='Septiembre 2026', fecha_inicio=date(2026, 9, 1), fecha_termino=date(2026, 9, 30))

	def _item(self, ponderacion, nombre='Atencion territorial'):
		return ItemMedible.objects.create(cargo=self.cargo, periodo=self.periodo, nombre=nombre, ponderacion=ponderacion)

	def _indicador(self, avance, ponderador=100):
		meta = Meta.objects.create(item=self._item(100), funcionario=self.funcionario, valor_objetivo=10, ponderador=ponderador)
		indicador = Indicador(meta=meta, periodo=self.periodo, avance=avance)
		indicador.calcular_cumplimiento()
		return indicador

	def test_dias_computables_se_calculan_al_guardar(self):
		self.assertEqual(self.periodo.dias_computables, 30)

	def test_periodo_rechaza_termino_anterior(self):
		with self.assertRaises(ValidationError):
			Periodo(nombre='Invalido', fecha_inicio=date(2026, 9, 30), fecha_termino=date(2026, 9, 1)).full_clean()

	def test_rn001_ponderaciones_del_cargo_no_superan_100(self):
		self._item(60)
		with self.assertRaises(ValidationError):
			ItemMedible(cargo=self.cargo, periodo=self.periodo, nombre='Exceso', ponderacion=50).full_clean()
		ItemMedible(cargo=self.cargo, periodo=self.periodo, nombre='Justo', ponderacion=40).full_clean()

	def test_rn001_iniciar_periodo_exige_100_por_cargo(self):
		item = self._item(60)
		with self.assertRaises(ValidationError):
			self.periodo.iniciar_periodo()
		self.cargo.actualizar_ponderaciones(item, 100)
		self.periodo.iniciar_periodo()
		self.assertEqual(Periodo.objects.get(pk=self.periodo.pk).estado, 'abierto')

	def test_rn013_periodo_cerrado_no_se_modifica(self):
		item = self._item(100)
		self.periodo.iniciar_periodo()
		self.periodo.cerrar_periodo()
		self.periodo.nombre = 'Cambio indebido'
		with self.assertRaises(ValidationError):
			self.periodo.save()
		item.nombre = 'Cambio indebido'
		with self.assertRaises(ValidationError):
			item.save()
		with self.assertRaises(ValidationError):
			ParametroVersionado.objects.create(periodo=self.periodo, clave='maximo_cumplimiento', valor='120')

	def test_rn013_reapertura_exige_motivo_y_queda_auditada(self):
		self.periodo.iniciar_periodo()
		self.periodo.cerrar_periodo()
		with self.assertRaises(ValidationError):
			self.periodo.reabrir_periodo('', self.usuario)
		self.periodo.reabrir_periodo('Corrección de datos', self.usuario)
		periodo = Periodo.objects.get(pk=self.periodo.pk)
		self.assertEqual((periodo.estado, periodo.version_parametros), ('abierto', 2))
		self.assertTrue(Auditoria.objects.filter(evento='reabrir_periodo', identificador_registro=str(periodo.pk), funcionario=self.funcionario).exists())

	def test_rn007_porcentaje_esperado_y_dias_restantes(self):
		self.assertEqual(self.periodo.porcentaje_esperado(date(2026, 9, 15)), Decimal('50.00'))
		self.assertEqual(self.periodo.calcular_dias_restantes(date(2026, 9, 15)), 15)
		self.assertEqual(self.periodo.porcentaje_esperado(date(2026, 8, 1)), Decimal('0.00'))
		self.assertEqual(self.periodo.porcentaje_esperado(date(2026, 10, 15)), Decimal('100.00'))

	def test_rn002_valor_objetivo_mayor_que_cero(self):
		meta = Meta(item=self._item(100), funcionario=self.funcionario, valor_objetivo=0)
		with self.assertRaises(ValidationError):
			meta.full_clean()

	def test_rn004_evaluar_progreso_y_actualizar_objetivo(self):
		meta = Meta.objects.create(item=self._item(100), funcionario=self.funcionario, valor_objetivo=8)
		self.assertEqual(meta.evaluar_progreso(2), Decimal('25.00'))
		meta.actualizar_valor_objetivo(4)
		self.assertEqual(Meta.objects.get(pk=meta.pk).valor_objetivo, 4)

	def test_rn005_tope_por_defecto_150_y_ponderado(self):
		indicador = self._indicador(avance=20, ponderador=50)
		self.assertEqual(indicador.cumplimiento, Decimal('150'))
		self.assertEqual(indicador.ponderacion, Decimal('75.00'))

	def test_rn005_tope_configurable_por_parametro(self):
		ParametroVersionado.objects.create(periodo=self.periodo, clave='maximo_cumplimiento', valor='120')
		self.assertEqual(self._indicador(avance=20).cumplimiento, Decimal('120'))

	def test_rn006_umbral_minimo_por_defecto_80(self):
		self.assertTrue(self.periodo.alcanza_umbral(Decimal('80')))
		self.assertFalse(self.periodo.alcanza_umbral(Decimal('79.99')))

	def test_rn008_semaforo(self):
		# El 15 de septiembre lo esperado es 50 %: ámbar desde 30 %.
		casos = [(5, 'verde'), (3, 'ambar'), (2, 'rojo')]
		for avance, color in casos:
			Meta.objects.all().delete()
			indicador = self._indicador(avance)
			self.assertEqual(indicador.actualizar_semaforo(date(2026, 9, 15)), color, avance)

	def test_cumplimiento_global_de_la_delegacion(self):
		self._indicador(avance=10).save()
		self.assertEqual(self.centro.obtener_cumplimiento_global(self.periodo), Decimal('100.00'))

	def test_catalogo_codigo_unico_y_activacion(self):
		elemento = Catalogo.objects.create(codigo='AT-OPER', nombre='Operativo en terreno', tipo='atencion')
		elemento.desactivar()
		self.assertFalse(Catalogo.objects.get(pk=elemento.pk).activo)
		elemento.activar()
		self.assertTrue(Catalogo.objects.get(pk=elemento.pk).activo)
		with self.assertRaises(IntegrityError), transaction.atomic():
			Catalogo.objects.create(codigo='AT-OPER', nombre='Duplicado', tipo='servicio')


class OperacionTests(TestCase):
	"""Etapa 3: RN-009, RN-010, control de versión y métodos de operación (se amplían con sus CU en la Etapa 6)."""

	def setUp(self):
		media = tempfile.mkdtemp()
		self.addCleanup(shutil.rmtree, media, ignore_errors=True)
		ajuste_media = override_settings(MEDIA_ROOT=media)
		ajuste_media.enable()
		self.addCleanup(ajuste_media.disable)

		self.centro = Delegacion.objects.create(nombre='Centro', territorio='Centro', enfasis='Atencion territorial')
		self.cargo = Cargo.objects.create(nombre='Profesional territorial')
		self.autor = self._funcionario('autor.operacion')
		self.verificador = self._funcionario('verificador.operacion')
		self.periodo = Periodo.objects.create(nombre='Septiembre 2026', fecha_inicio=date(2026, 9, 1), fecha_termino=date(2026, 9, 30))
		self.item = ItemMedible.objects.create(cargo=self.cargo, periodo=self.periodo, nombre='Atencion territorial', ponderacion=100)
		self.catalogo = Catalogo.objects.create(codigo='AT-OPER', nombre='Operativo en terreno', tipo='atencion')

	def _funcionario(self, username):
		usuario = User.objects.create_user(username, password='clave-segura')
		return Funcionario.objects.create(usuario=usuario, identificador_institucional=username, nombre=username, cargo=self.cargo, delegacion=self.centro)

	def _actividad(self, dia=10, **cambios):
		datos = {'item': self.item, 'catalogo': self.catalogo, 'fecha_hora': timezone.make_aware(datetime(2026, 9, dia, 10, 0)), 'solicitud_problema': 'Consulta vecinal', 'accion': 'Orientacion'}
		datos.update(cambios)
		return self.autor.registrar_actividad(datos)

	def _archivo(self, nombre='respaldo.pdf'):
		return SimpleUploadedFile(nombre, b'%PDF-1.4 prueba', content_type='application/pdf')

	def _validacion(self, evidencia):
		return Validacion(evidencia=evidencia, funcionario_verificador=self.verificador)

	def test_registrar_actividad_genera_codigo_y_toma_la_delegacion_del_autor(self):
		actividad = self._actividad()
		self.assertTrue(actividad.codigo_verificador.startswith('EVD-'))
		self.assertEqual(actividad.codigo, actividad.codigo_verificador)
		self.assertEqual((actividad.delegacion, actividad.version, actividad.estado), (self.centro, 1, 'pendiente'))

	def test_rn010_codigo_verificador_inmutable(self):
		actividad = self._actividad()
		actividad.codigo_verificador = 'EVD-OTRO'
		with self.assertRaises(ValidationError):
			actividad.save()

	def test_registrar_actividad_fuera_del_periodo_o_con_periodo_cerrado(self):
		with self.assertRaises(ValidationError):
			self._actividad(fecha_hora=timezone.make_aware(datetime(2026, 10, 5, 10, 0)))
		self.periodo.iniciar_periodo()
		self.periodo.cerrar_periodo()
		self.item.refresh_from_db()
		with self.assertRaises(ValidationError):
			self._actividad()

	def test_version_optimista_rechaza_la_edicion_concurrente(self):
		actividad = self._actividad()
		primera = Actividad.objects.get(pk=actividad.pk)
		segunda = Actividad.objects.get(pk=actividad.pk)
		primera.accion = 'Guardada primero'
		primera.save()
		segunda.accion = 'Guardada con version vieja'
		with self.assertRaises(ValidationError):
			segunda.save()
		actividad.refresh_from_db()
		self.assertEqual((actividad.accion, actividad.version), ('Guardada primero', 2))

	def test_subir_evidencia_genera_codigos_y_envia_a_revision(self):
		actividad = self._actividad()
		actividad.cambiar_estado('correccion')
		primera = self.autor.subir_evidencia(actividad, self._archivo(), 'Acta firmada')
		segunda = self.autor.subir_evidencia(actividad, self._archivo('foto.png'))
		self.assertEqual(primera.codigo_evidencia, f'{actividad.codigo_verificador}-01')
		self.assertEqual(segunda.codigo_evidencia, f'{actividad.codigo_verificador}-02')
		self.assertEqual(primera.metadatos, {'comentario': 'Acta firmada'})
		self.assertEqual(primera.estado_revision, 'pendiente')
		self.assertIsNotNone(primera.fecha_carga)
		self.assertTrue(primera.descargar_archivo().endswith('.pdf'))
		self.assertEqual(Actividad.objects.get(pk=actividad.pk).estado, 'pendiente')

	def test_subir_evidencia_rechaza_extension_no_permitida(self):
		archivo = SimpleUploadedFile('script.exe', b'MZ', content_type='application/octet-stream')
		with self.assertRaises(ValidationError):
			self.autor.subir_evidencia(self._actividad(), archivo)

	def test_rn009_solo_la_validacion_aprobada_aporta_al_avance(self):
		validada = self._actividad()
		evidencia = self.autor.subir_evidencia(validada, self._archivo())
		sin_validar = self._actividad(dia=11)
		sin_validar.cambiar_estado('aprobada')
		meta = Meta.objects.create(item=self.item, funcionario=self.autor, valor_objetivo=2)
		self.assertEqual(Indicador(meta=meta, periodo=self.periodo).calcular_avance(), 0)

		self._validacion(evidencia).aprobar_evidencia('Conforme')

		self.assertEqual(Evidencia.objects.get(pk=evidencia.pk).estado_revision, 'aprobada')
		self.assertEqual(Actividad.objects.get(pk=validada.pk).estado, 'aprobada')
		self.assertEqual(Indicador(meta=meta, periodo=self.periodo).calcular_avance(), 1)

	def test_rechazo_y_correccion_exigen_texto_y_numeran_revisiones(self):
		actividad = self._actividad()
		evidencia = self.autor.subir_evidencia(actividad, self._archivo())
		with self.assertRaises(ValidationError):
			self._validacion(evidencia).rechazar_evidencia('')
		correccion = self._validacion(evidencia).solicitar_correccion('Falta la firma')
		self.assertEqual((correccion.version, actividad.estado, evidencia.estado_revision), (1, 'correccion', 'correccion'))

		evidencia.reemplazar_archivo(self._archivo('firmado.pdf'))
		self.assertEqual((evidencia.estado_revision, actividad.estado), ('pendiente', 'pendiente'))

		rechazo = self._validacion(evidencia).rechazar_evidencia('Documento ilegible')
		self.assertEqual((rechazo.version, Actividad.objects.get(pk=actividad.pk).estado), (2, 'rechazada'))

	def test_actividad_aprobada_no_cambia_de_estado(self):
		actividad = self._actividad()
		actividad.cambiar_estado('aprobada')
		with self.assertRaises(ValidationError):
			actividad.cambiar_estado('pendiente')

	def test_indicador_generar_calcula_y_guarda(self):
		evidencia = self.autor.subir_evidencia(self._actividad(), self._archivo())
		self._validacion(evidencia).aprobar_evidencia()
		meta = Meta.objects.create(item=self.item, funcionario=self.autor, valor_objetivo=2)
		indicador = Indicador.generar(meta, fecha=date(2026, 9, 15))
		self.assertEqual((indicador.avance, indicador.cumplimiento, indicador.semaforo), (1, Decimal('50.00'), 'verde'))
		self.assertTrue(Indicador.objects.filter(pk=indicador.pk).exists())

	def _compromiso(self):
		return Compromiso.objects.create(folio='LS-OPER-1', delegacion=self.centro, funcionario_responsable=self.autor, solicitante='Junta de vecinos', territorio='Centro', descripcion='Poda de arboles', fecha_comprometida=date(2026, 9, 30), origen='externo')

	def test_compromiso_cambios_quedan_en_el_historial(self):
		compromiso = self._compromiso()
		compromiso.set_estado('proceso', self.autor)
		compromiso.derivar_compromiso(self.verificador, self.autor)
		with self.assertRaises(ValidationError):
			compromiso.cerrar_compromiso('', self.autor)
		compromiso.cerrar_compromiso('Poda realizada', self.verificador)

		compromiso.refresh_from_db()
		self.assertEqual((compromiso.estado, compromiso.funcionario_responsable, compromiso.observacion), ('realizado', self.verificador, 'Poda realizada'))
		historial = list(compromiso.historial.order_by('pk').values_list('estado_anterior', 'estado_nuevo', 'autor_funcionario'))
		self.assertEqual(historial, [('ingresado', 'proceso', self.autor.pk), ('proceso', 'proceso', self.autor.pk), ('proceso', 'realizado', self.verificador.pk)])
		with self.assertRaises(ValidationError):
			compromiso.derivar_compromiso(self.autor, self.autor)

	def test_compromiso_version_optimista(self):
		compromiso = self._compromiso()
		vieja = Compromiso.objects.get(pk=compromiso.pk)
		compromiso.set_estado('proceso', self.autor)
		with self.assertRaises(ValidationError):
			vieja.set_estado('realizado', self.autor)
		self.assertEqual(HistorialCompromiso.objects.filter(compromiso=compromiso).count(), 1)


class MigracionDatosTests(TransactionTestCase):
	"""Etapa 4: la migración 0010 copia los datos antiguos al modelo de 17 clases y se puede revertir."""

	antes = [('delegaciones_app', '0009_ampliar_operacion')]
	despues = [('delegaciones_app', '0010_migrar_datos')]

	def _migrar(self, destino):
		executor = MigrationExecutor(connection)
		executor.migrate(destino)
		return executor.loader.project_state(destino).apps

	def setUp(self):
		viejo = self._migrar(self.antes)
		modelo = lambda nombre: viejo.get_model('delegaciones_app', nombre)
		Usuario = viejo.get_model('auth', 'User')
		centro = modelo('Delegacion').objects.create(nombre='Centro', territorio='Centro historico', enfasis='Atencion')
		rural = modelo('Delegacion').objects.create(nombre='Rural', territorio='Localidades rurales', enfasis='Servicios', activa=False)
		coordinador = Usuario.objects.create(username='coordinador', first_name='Ana', last_name='Rojas')
		funcionario = Usuario.objects.create(username='funcionario')
		admin = Usuario.objects.create(username='admin', is_superuser=True, is_staff=True)
		otro = Usuario.objects.create(username='otro')
		modelo('PerfilUsuario').objects.create(usuario=coordinador, rol='coordinador', cargo='Coordinador territorial')
		modelo('PerfilUsuario').objects.create(usuario=funcionario, rol='funcionario', delegacion=centro)
		modelo('PeriodoMedicion').objects.create(nombre='Trimestre', inicio=date(2026, 7, 1), termino=date(2026, 9, 30), estado='abierto')
		modelo('CatalogoItem').objects.create(categoria='servicio', codigo='DUP', nombre='Servicio')
		modelo('CatalogoItem').objects.create(categoria='atencion', codigo='DUP', nombre='Atencion')
		for delegacion in (centro, rural):
			modelo('MetaMedicion').objects.create(delegacion=delegacion, nombre='Seguridad', objetivo=10, ponderador=100, periodo_inicio=date(2026, 7, 1), periodo_termino=date(2026, 9, 30))
		actividad = modelo('Actividad').objects.create(codigo='EVD-MIG-1', funcionario=funcionario, delegacion=centro, fecha=date(2026, 9, 1), tipo_atencion='Solicitud ciudadana', descripcion='Luminaria', accion='Derivacion', item_medicion='Seguridad', telefono='+56 9 1234 5678 anexo 22', estado='aprobada')
		modelo('Evidencia').objects.create(actividad=actividad, archivo='evidencias/uno.pdf', comentario='Acta', aprobada=True, revisada_por=coordinador)
		modelo('Evidencia').objects.create(actividad=actividad, archivo='evidencias/dos.pdf')
		compromiso = modelo('Compromiso').objects.create(folio='LS-1', delegacion=centro, responsable=otro, solicitante='Junta de vecinos', territorio='Centro', descripcion='Poda', fecha_comprometida=date(2026, 9, 30))
		modelo('HistorialCompromiso').objects.create(compromiso=compromiso, autor=funcionario, estado_anterior='', estado_nuevo='ingresado')
		modelo('Auditoria').objects.create(usuario=admin, accion='cambio_estado', entidad='Compromiso', identificador='LS-1', detalle={'anterior': 'pendiente', 'nuevo': 'realizado'})
		modelo('Auditoria').objects.create(usuario=funcionario, accion='editar', entidad='Actividad', identificador='EVD-MIG-1', detalle={'campos': ['accion']})

	def tearDown(self):
		self._migrar(MigrationExecutor(connection).loader.graph.leaf_nodes())

	def test_migrar_copia_y_transforma_los_datos(self):
		nuevo = self._migrar(self.despues)
		modelo = lambda nombre: nuevo.get_model('delegaciones_app', nombre)
		funcionario = lambda username: modelo('Funcionario').objects.get(usuario__username=username)

		self.assertEqual(modelo('Rol').objects.count(), 6)
		self.assertEqual(funcionario('coordinador').nombre, 'Ana Rojas')
		self.assertEqual(funcionario('coordinador').cargo.nombre, 'Coordinador territorial')
		self.assertEqual(funcionario('funcionario').cargo.nombre, 'Sin cargo asignado')
		self.assertEqual(list(funcionario('otro').roles.values_list('nombre_rol', flat=True)), ['consulta'])
		self.assertFalse(modelo('Funcionario').objects.filter(usuario__username='admin').exists())
		self.assertEqual(modelo('UsuarioMaestro').objects.get().usuario.username, 'admin')
		rural = modelo('Delegacion').objects.get(nombre='Rural')
		self.assertEqual((rural.estado, rural.ambito), (False, 'Localidades rurales'))

		periodo = modelo('Periodo').objects.get(nombre='Trimestre')
		self.assertEqual(periodo.dias_computables, 92)
		self.assertEqual(modelo('ParametroVersionado').objects.get(periodo=periodo).valor, '150.00')
		self.assertEqual(set(modelo('Catalogo').objects.values_list('codigo', flat=True)), {'DUP', 'ATE-DUP', 'ATE-SOLICITUD-CIUDADANA'})

		# P2: Rural no tiene funcionarios y recibe un delegado provisional inactivo. P3: ítem compartido al 100 %.
		item = modelo('ItemMedible').objects.get()
		self.assertEqual((item.nombre, item.ponderacion), ('Seguridad', 100))
		meta_rural = modelo('Meta').objects.get(funcionario__delegacion=rural)
		self.assertFalse(meta_rural.funcionario.usuario.is_active)
		self.assertEqual(list(meta_rural.funcionario.roles.values_list('nombre_rol', flat=True)), ['delegado'])
		self.assertEqual(modelo('Meta').objects.filter(item=item, valor_objetivo=10).count(), 2)

		actividad = modelo('Actividad').objects.get(codigo='EVD-MIG-1')
		self.assertEqual(actividad.codigo_verificador, 'EVD-MIG-1')
		self.assertEqual(actividad.funcionario_autor, funcionario('funcionario'))
		self.assertEqual(timezone.localtime(actividad.fecha_hora).replace(tzinfo=None), datetime(2026, 9, 1, 0, 0))
		self.assertEqual(actividad.contacto_telefono, '+56 9 1234 5678 anex')
		self.assertEqual((actividad.item, actividad.catalogo.codigo), (item, 'ATE-SOLICITUD-CIUDADANA'))

		evidencias = list(modelo('Evidencia').objects.order_by('pk').values_list('codigo_evidencia', 'estado_revision', 'metadatos'))
		self.assertEqual(evidencias, [('EVD-MIG-1-01', 'aprobada', {'comentario': 'Acta'}), ('EVD-MIG-1-02', 'pendiente', None)])
		validacion = modelo('Validacion').objects.get()
		self.assertEqual((validacion.decision, validacion.funcionario_verificador), ('aprobada', funcionario('coordinador')))

		compromiso = modelo('Compromiso').objects.get()
		self.assertEqual((compromiso.funcionario_responsable, compromiso.origen), (funcionario('otro'), 'externo'))
		self.assertEqual(modelo('HistorialCompromiso').objects.get().autor_funcionario, funcionario('funcionario'))

		de_admin = modelo('Auditoria').objects.get(usuario__username='admin')
		self.assertEqual((de_admin.usuario_maestro.identificador_maestro, de_admin.funcionario), ('admin', None))
		self.assertEqual((de_admin.evento, de_admin.valor_anterior, de_admin.valor_nuevo), ('cambio_estado', 'pendiente', 'realizado'))
		del_funcionario = modelo('Auditoria').objects.get(usuario__username='funcionario')
		self.assertEqual((del_funcionario.funcionario, del_funcionario.valor_nuevo), (funcionario('funcionario'), '{"campos": ["accion"]}'))

	def test_revertir_deja_los_datos_como_antes(self):
		self._migrar(self.despues)
		viejo = self._migrar(self.antes)
		modelo = lambda nombre: viejo.get_model('delegaciones_app', nombre)
		for nombre in ('Funcionario', 'Rol', 'Cargo', 'Periodo', 'Catalogo', 'ItemMedible', 'Meta', 'Validacion', 'UsuarioMaestro'):
			self.assertFalse(modelo(nombre).objects.exists(), nombre)
		self.assertFalse(modelo('Actividad').objects.exclude(codigo_verificador=None).exists())
		self.assertFalse(viejo.get_model('auth', 'User').objects.filter(username__startswith='delegado.').exists())
		self.assertEqual(modelo('Evidencia').objects.count(), 2)
		self.assertEqual(modelo('MetaMedicion').objects.count(), 2)


class PermisosTests(TestCase):
	"""Etapa 5a: tiene_rol y control de acceso por rol (se amplía con sus CU en la Etapa 6)."""

	def setUp(self):
		self.cargo = Cargo.objects.create(nombre='Profesional territorial')
		self.factory = RequestFactory()

	def _usuario(self, username, *roles, estado=True):
		usuario = User.objects.create_user(username, password='clave-segura')
		funcionario = Funcionario.objects.create(usuario=usuario, identificador_institucional=username, nombre=username, cargo=self.cargo, estado=estado)
		for rol in roles:
			FuncionarioRol.objects.create(funcionario=funcionario, rol=Rol.objects.get(nombre_rol=rol))
		return usuario

	def _llamar(self, vista, usuario, ruta='/prueba/'):
		request = self.factory.get(ruta)
		request.user = usuario
		return vista(request)

	def test_tiene_rol_segun_los_roles_del_funcionario(self):
		coordinador = self._usuario('coord', 'coordinador')
		self.assertTrue(tiene_rol(coordinador, 'administrador', 'coordinador'))
		self.assertFalse(tiene_rol(coordinador, 'administrador'))
		self.assertFalse(tiene_rol(coordinador))

	def test_funcionario_con_varios_roles(self):
		usuario = self._usuario('doble', 'funcionario', 'verificador')
		self.assertEqual(roles_de(usuario), {'funcionario', 'verificador'})

	def test_funcionario_inactivo_no_aporta_roles(self):
		self.assertEqual(roles_de(self._usuario('baja', 'coordinador', estado=False)), frozenset())

	def test_usuario_sin_funcionario_ni_sesion_no_tiene_roles(self):
		self.assertEqual(roles_de(User.objects.create_user('sin.perfil', password='clave-segura')), frozenset())
		self.assertFalse(tiene_rol(AnonymousUser(), 'administrador'))

	def test_superusuario_y_usuario_maestro_cuentan_como_administrador(self):
		self.assertTrue(tiene_rol(User.objects.create_superuser('super', password='clave-segura'), 'administrador'))
		usuario = User.objects.create_user('maestro', password='clave-segura')
		maestro = UsuarioMaestro.objects.create(usuario=usuario, identificador_maestro='maestro', nombre='Maestro', nivel_dominio='total')
		self.assertTrue(tiene_rol(usuario, 'administrador'))
		maestro.estado = False
		maestro.save()
		self.assertFalse(tiene_rol(usuario, 'administrador'))

	def test_cuenta_inactiva_no_tiene_roles(self):
		usuario = self._usuario('inactivo', 'administrador')
		usuario.is_active = False
		self.assertEqual(roles_de(usuario), frozenset())

	def test_mixin_deja_pasar_al_rol_permitido_y_redirige_a_los_demas(self):
		class VistaDePrueba(RolRequeridoMixin, View):
			roles_permitidos = ('administrador', 'coordinador')

			def get(self, request):
				return HttpResponse('ok')

		vista = VistaDePrueba.as_view()
		self.assertEqual(self._llamar(vista, self._usuario('coord2', 'coordinador')).status_code, 200)
		sin_permiso = self._llamar(vista, self._usuario('func2', 'funcionario'))
		self.assertEqual((sin_permiso.status_code, sin_permiso.url), (302, reverse('inicio')))
		anonimo = self._llamar(vista, AnonymousUser())
		self.assertEqual((anonimo.status_code, anonimo.url), (302, f"{reverse('login')}?next=/prueba/"))

	def test_decorador_deja_pasar_al_rol_permitido_y_redirige_a_los_demas(self):
		@rol_requerido('verificador')
		def vista(request):
			return HttpResponse('ok')

		self.assertEqual(self._llamar(vista, self._usuario('verif', 'verificador')).status_code, 200)
		sin_permiso = self._llamar(vista, self._usuario('func3', 'funcionario'))
		self.assertEqual((sin_permiso.status_code, sin_permiso.url), (302, reverse('inicio')))
		anonimo = self._llamar(vista, AnonymousUser())
		self.assertEqual((anonimo.status_code, anonimo.url), (302, f"{reverse('login')}?next=/prueba/"))


class MantenedoresTests(TestCase):
	"""Etapa 5b: CRUD genérico de las ocho tablas maestras (se amplía con sus CU en la Etapa 6)."""

	def setUp(self):
		self.cargo = Cargo.objects.create(nombre='Profesional territorial')
		self.centro = Delegacion.objects.create(nombre='Centro', ambito='Centro historico', enfasis='Atencion territorial')
		self.admin = self._usuario('admin.crud', 'administrador')
		self.coordinador = self._usuario('coord.crud', 'coordinador')
		self.funcionario = self._usuario('func.crud', 'funcionario')
		self.client.force_login(self.admin)

	def _usuario(self, username, *roles):
		usuario = User.objects.create_user(username, password='clave-segura')
		funcionario = Funcionario.objects.create(usuario=usuario, identificador_institucional=username, nombre=username, cargo=self.cargo)
		for rol in roles:
			FuncionarioRol.objects.create(funcionario=funcionario, rol=Rol.objects.get(nombre_rol=rol))
		return usuario

	def _url(self, nombre, slug, *args):
		return reverse(nombre, args=[slug, *args])

	def _auditoria(self, evento, entidad):
		return Auditoria.objects.filter(evento=evento, entidad=entidad)

	def _periodo_con_item(self, ponderacion=100):
		periodo = Periodo.objects.create(nombre='Septiembre 2026', fecha_inicio=date(2026, 9, 1), fecha_termino=date(2026, 9, 30))
		return periodo, ItemMedible.objects.create(cargo=self.cargo, periodo=periodo, nombre='Atencion territorial', ponderacion=ponderacion)

	def test_indice_deshabilita_los_mantenedores_exclusivos_del_administrador(self):
		respuesta = self.client.get(reverse('mantenedores'))
		self.assertContains(respuesta, 'Ver registros', count=8)
		self.assertNotContains(respuesta, 'Disponible para administradores')
		self.client.force_login(self.coordinador)
		respuesta = self.client.get(reverse('mantenedores'))
		self.assertContains(respuesta, 'Ver registros', count=6)
		self.assertContains(respuesta, 'Disponible para administradores', count=2)

	def test_las_ocho_listas_tienen_agregar_y_buscar(self):
		self.assertEqual(len(MANTENEDORES), 8)
		for slug in MANTENEDORES:
			respuesta = self.client.get(reverse('mantenedor_lista', args=[slug]))
			self.assertEqual(respuesta.status_code, 200, slug)
			self.assertContains(respuesta, 'Agregar')
			self.assertContains(respuesta, 'Buscar')

	def test_acceso_segun_el_rol(self):
		for slug in ('funcionarios', 'roles'):
			self.client.force_login(self.coordinador)
			self.assertRedirects(self.client.get(reverse('mantenedor_lista', args=[slug])), reverse('inicio'))
		self.assertEqual(self.client.get(reverse('mantenedor_lista', args=['delegaciones'])).status_code, 200)
		self.client.force_login(self.funcionario)
		self.assertRedirects(self.client.get(reverse('mantenedores')), reverse('inicio'))
		self.assertRedirects(self.client.get(reverse('mantenedor_lista', args=['catalogo'])), reverse('inicio'))
		self.client.logout()
		url = reverse('mantenedor_lista', args=['catalogo'])
		self.assertRedirects(self.client.get(url), f"{reverse('login')}?next={url}")

	def test_mantenedor_inexistente_es_404(self):
		self.assertEqual(self.client.get('/administracion/inexistente/').status_code, 404)

	def test_crear_y_editar_delegacion_deja_auditoria_con_valores(self):
		self.client.post(self._url('mantenedor_nuevo', 'delegaciones'), {'nombre': 'Rural', 'ambito': 'Localidades rurales', 'enfasis': '', 'estado': 'on'})
		rural = Delegacion.objects.get(nombre='Rural')
		self.assertEqual(self._auditoria('crear', 'Delegacion').get().funcionario.usuario, self.admin)

		self.client.post(self._url('mantenedor_editar', 'delegaciones', rural.pk), {'nombre': 'Rural', 'ambito': 'Sector rural', 'enfasis': '', 'estado': 'on'})
		edicion = self._auditoria('editar', 'Delegacion').get()
		self.assertEqual((edicion.valor_anterior, edicion.valor_nuevo), ('{"ambito": "Localidades rurales"}', '{"ambito": "Sector rural"}'))

	def test_busqueda_filtra_la_lista(self):
		Catalogo.objects.create(codigo='SRV-01', nombre='Orientacion vecinal', tipo='servicio')
		Catalogo.objects.create(codigo='ACT-02', nombre='Operativo rural', tipo='actividad')
		respuesta = self.client.get(reverse('mantenedor_lista', args=['catalogo']), {'q': 'SRV-01'})
		self.assertContains(respuesta, 'Orientacion vecinal')
		self.assertNotContains(respuesta, 'Operativo rural')

	def test_catalogo_rechaza_codigo_duplicado(self):
		Catalogo.objects.create(codigo='DUP', nombre='Existente', tipo='servicio')
		respuesta = self.client.post(self._url('mantenedor_nuevo', 'catalogo'), {'codigo': 'DUP', 'nombre': 'Otro', 'tipo': 'atencion', 'activo': 'on'})
		self.assertEqual(respuesta.status_code, 200)
		self.assertIn('codigo', respuesta.context['form'].errors)
		self.assertEqual(Catalogo.objects.filter(codigo='DUP').count(), 1)

	def test_catalogo_se_desactiva_y_activa_sin_borrar_la_fila(self):
		elemento = Catalogo.objects.create(codigo='SRV-BAJA', nombre='Servicio', tipo='servicio')
		url = self._url('mantenedor_eliminar', 'catalogo', elemento.pk)
		self.assertContains(self.client.get(url), 'Confirmar desactivación')
		self.assertTrue(Catalogo.objects.get(pk=elemento.pk).activo)

		self.assertRedirects(self.client.post(url), reverse('mantenedor_lista', args=['catalogo']))
		self.assertFalse(Catalogo.objects.get(pk=elemento.pk).activo)
		self.assertTrue(self._auditoria('desactivar', 'Catalogo').exists())

		self.assertContains(self.client.get(url), 'Confirmar activación')
		self.client.post(url)
		self.assertTrue(Catalogo.objects.get(pk=elemento.pk).activo)

	def test_roles_del_sistema_no_se_renombran_ni_se_eliminan(self):
		consulta = Rol.objects.get(nombre_rol='consulta')
		self.assertContains(self.client.get(self._url('mantenedor_eliminar', 'roles', consulta.pk)), 'rol del sistema')
		self.client.post(self._url('mantenedor_eliminar', 'roles', consulta.pk))
		self.client.post(self._url('mantenedor_editar', 'roles', consulta.pk), {'nombre_rol': 'otro'})
		self.assertTrue(Rol.objects.filter(nombre_rol='consulta').exists())
		self.assertFalse(Rol.objects.filter(nombre_rol='otro').exists())

	def test_rol_nuevo_sin_uso_se_elimina_con_auditoria(self):
		rol = Rol.objects.create(nombre_rol='pasante')
		self.client.post(self._url('mantenedor_eliminar', 'roles', rol.pk))
		self.assertFalse(Rol.objects.filter(pk=rol.pk).exists())
		self.assertTrue(self._auditoria('eliminar', 'Rol').exists())

	def test_rol_en_uso_no_se_elimina_y_explica_el_motivo(self):
		rol = Rol.objects.create(nombre_rol='pasante')
		FuncionarioRol.objects.create(funcionario=self.funcionario.funcionario, rol=rol)
		respuesta = self.client.post(self._url('mantenedor_eliminar', 'roles', rol.pk), follow=True)
		self.assertTrue(Rol.objects.filter(pk=rol.pk).exists())
		self.assertContains(respuesta, 'No se puede eliminar')
		self.assertFalse(self._auditoria('eliminar', 'Rol').exists())

	def test_cargo_se_desactiva_en_vez_de_eliminarse(self):
		self.client.post(self._url('mantenedor_eliminar', 'cargos', self.cargo.pk))
		self.assertFalse(Cargo.objects.get(pk=self.cargo.pk).vigencia)

	def test_funcionario_se_crea_con_cuenta_roles_y_auditoria_sin_contrasena(self):
		datos = {'username': 'nuevo.func', 'nombre': 'Nuevo Funcionario', 'email': 'nuevo@laserena.cl', 'cargo': self.cargo.pk, 'delegacion': self.centro.pk, 'roles': [Rol.objects.get(nombre_rol='funcionario').pk], 'estado': 'on', 'password': 'Clave-segura-2026', 'password_confirm': 'Clave-segura-2026'}
		self.client.post(self._url('mantenedor_nuevo', 'funcionarios'), datos)
		funcionario = Funcionario.objects.get(identificador_institucional='nuevo.func')
		self.assertTrue(funcionario.usuario.check_password('Clave-segura-2026'))
		self.assertEqual((funcionario.delegacion, list(funcionario.roles.values_list('nombre_rol', flat=True))), (self.centro, ['funcionario']))
		self.assertNotIn('Clave-segura-2026', self._auditoria('crear', 'Funcionario').get().valor_nuevo)

	def test_funcionario_rechaza_usuario_repetido_y_contrasena_distinta(self):
		datos = {'username': 'func.crud', 'nombre': 'Repetido', 'cargo': self.cargo.pk, 'roles': [Rol.objects.get(nombre_rol='consulta').pk], 'estado': 'on', 'password': 'Clave-segura-2026', 'password_confirm': 'Otra-clave-2026'}
		formulario = self.client.post(self._url('mantenedor_nuevo', 'funcionarios'), datos).context['form']
		self.assertIn('username', formulario.errors)
		self.assertIn('password_confirm', formulario.errors)

	def test_desactivar_funcionario_tambien_desactiva_su_cuenta(self):
		funcionario = self.funcionario.funcionario
		self.client.post(self._url('mantenedor_eliminar', 'funcionarios', funcionario.pk))
		funcionario.refresh_from_db()
		self.assertFalse(funcionario.estado)
		self.assertFalse(User.objects.get(pk=self.funcionario.pk).is_active)

	def test_administrador_no_puede_desactivarse_ni_quitarse_el_rol(self):
		propio = self.admin.funcionario
		self.client.post(self._url('mantenedor_eliminar', 'funcionarios', propio.pk))
		self.assertTrue(Funcionario.objects.get(pk=propio.pk).estado)
		datos = {'username': 'admin.crud', 'nombre': 'admin.crud', 'cargo': self.cargo.pk, 'roles': [Rol.objects.get(nombre_rol='consulta').pk], 'estado': 'on'}
		formulario = self.client.post(self._url('mantenedor_editar', 'funcionarios', propio.pk), datos).context['form']
		self.assertIn('roles', formulario.errors)
		self.assertTrue(propio.roles.filter(nombre_rol='administrador').exists())

	def test_periodo_se_crea_en_borrador_y_calcula_sus_dias(self):
		self.client.post(self._url('mantenedor_nuevo', 'periodos'), {'nombre': 'Octubre 2026', 'fecha_inicio': '2026-10-01', 'fecha_termino': '2026-10-31', 'umbral_minimo': '80'})
		periodo = Periodo.objects.get(nombre='Octubre 2026')
		self.assertEqual((periodo.estado, periodo.dias_computables), ('borrador', 31))

	def test_periodo_rechaza_termino_anterior_al_inicio(self):
		formulario = self.client.post(self._url('mantenedor_nuevo', 'periodos'), {'nombre': 'Invalido', 'fecha_inicio': '2026-10-31', 'fecha_termino': '2026-10-01', 'umbral_minimo': '80'}).context['form']
		self.assertTrue(formulario.non_field_errors())

	def test_periodo_se_inicia_se_cierra_y_se_reabre_con_motivo(self):
		periodo, item = self._periodo_con_item(ponderacion=60)
		url = lambda accion: reverse('periodo_accion', args=[periodo.pk, accion])
		self.assertContains(self.client.post(url('iniciar'), follow=True), 'deben sumar 100')
		self.assertEqual(Periodo.objects.get(pk=periodo.pk).estado, 'borrador')

		item.ponderacion = 100
		item.save()
		self.client.post(url('iniciar'))
		self.client.post(url('cerrar'))
		self.assertEqual(Periodo.objects.get(pk=periodo.pk).estado, 'cerrado')

		self.assertContains(self.client.post(url('reabrir'), {'motivo': ''}, follow=True), 'exige un motivo')
		self.client.post(url('reabrir'), {'motivo': 'Correccion de datos'})
		self.assertEqual(Periodo.objects.get(pk=periodo.pk).estado, 'abierto')
		for evento in ('iniciar_periodo', 'cerrar_periodo', 'reabrir_periodo'):
			self.assertTrue(self._auditoria(evento, 'Periodo').exists(), evento)

	def test_periodo_cerrado_no_se_edita_ni_se_elimina(self):
		periodo, _ = self._periodo_con_item()
		periodo.iniciar_periodo()
		periodo.cerrar_periodo()
		datos = {'nombre': 'Cambio', 'fecha_inicio': '2026-09-01', 'fecha_termino': '2026-09-30', 'umbral_minimo': '80'}
		self.assertTrue(self.client.post(self._url('mantenedor_editar', 'periodos', periodo.pk), datos).context['form'].non_field_errors())
		self.client.post(self._url('mantenedor_eliminar', 'periodos', periodo.pk))
		self.assertTrue(Periodo.objects.filter(pk=periodo.pk, nombre='Septiembre 2026').exists())

	def test_item_rechaza_ponderaciones_que_superan_100(self):
		periodo, _ = self._periodo_con_item(ponderacion=70)
		datos = {'cargo': self.cargo.pk, 'periodo': periodo.pk, 'nombre': 'Otro item', 'ponderacion': '40'}
		formulario = self.client.post(self._url('mantenedor_nuevo', 'items'), datos).context['form']
		self.assertIn('ponderacion', formulario.errors)

	def test_item_con_metas_no_se_elimina(self):
		_, item = self._periodo_con_item()
		Meta.objects.create(item=item, funcionario=self.funcionario.funcionario, valor_objetivo=10)
		respuesta = self.client.post(self._url('mantenedor_eliminar', 'items', item.pk), follow=True)
		self.assertTrue(ItemMedible.objects.filter(pk=item.pk).exists())
		self.assertContains(respuesta, 'No se puede eliminar')

	def test_meta_rechaza_objetivo_cero_y_al_guardar_genera_su_indicador(self):
		_, item = self._periodo_con_item()
		datos = {'item': item.pk, 'funcionario': self.funcionario.funcionario.pk, 'valor_objetivo': '0', 'unidad': 'actividades', 'ponderador': '100'}
		self.assertIn('valor_objetivo', self.client.post(self._url('mantenedor_nuevo', 'metas'), datos).context['form'].errors)
		datos['valor_objetivo'] = '10'
		self.client.post(self._url('mantenedor_nuevo', 'metas'), datos)
		meta = Meta.objects.get()
		self.assertEqual(Indicador.objects.filter(meta=meta).count(), 1)

	def test_eliminar_meta_avisa_que_borra_sus_indicadores(self):
		_, item = self._periodo_con_item()
		meta = Meta.objects.create(item=item, funcionario=self.funcionario.funcionario, valor_objetivo=10)
		Indicador.generar(meta)
		self.assertContains(self.client.get(self._url('mantenedor_eliminar', 'metas', meta.pk)), '1 indicador(es)')
		self.client.post(self._url('mantenedor_eliminar', 'metas', meta.pk))
		self.assertFalse(Meta.objects.filter(pk=meta.pk).exists())
		self.assertFalse(Indicador.objects.exists())

	def test_los_formularios_de_alta_y_edicion_se_muestran(self):
		periodo, item = self._periodo_con_item()
		meta = Meta.objects.create(item=item, funcionario=self.funcionario.funcionario, valor_objetivo=10)
		existentes = {
			'delegaciones': self.centro, 'cargos': self.cargo, 'roles': Rol.objects.get(nombre_rol='consulta'),
			'funcionarios': self.funcionario.funcionario, 'catalogo': Catalogo.objects.create(codigo='C-1', nombre='Elemento', tipo='servicio'),
			'periodos': periodo, 'items': item, 'metas': meta,
		}
		for slug, objeto in existentes.items():
			self.assertEqual(self.client.get(self._url('mantenedor_nuevo', slug)).status_code, 200, slug)
			self.assertEqual(self.client.get(self._url('mantenedor_editar', slug, objeto.pk)).status_code, 200, slug)
			self.assertEqual(self.client.get(self._url('mantenedor_eliminar', slug, objeto.pk)).status_code, 200, slug)

	def test_los_avisos_se_muestran_en_pantalla(self):
		respuesta = self.client.post(self._url('mantenedor_nuevo', 'cargos'), {'nombre': 'Cargo con aviso', 'vigencia': 'on'}, follow=True)
		self.assertContains(respuesta, 'Se guardó: Cargo con aviso.')
