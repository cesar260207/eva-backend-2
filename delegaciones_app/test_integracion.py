import json
import shutil
import tempfile
from io import StringIO
from datetime import date

from django.apps import apps
from django.contrib import admin
from django.contrib.auth.models import AnonymousUser, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import RequestFactory, TestCase, TransactionTestCase, override_settings
from django.urls import reverse

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from django.http import HttpResponse
from django.views import View

from .crud import MANTENEDORES
from .informes import filtrar_actividades, filtrar_compromisos
from .models import validar_tamano_evidencia
from .permisos import RolRequeridoMixin, roles_de, rol_requerido, tiene_rol
from .models import (
	Actividad, Auditoria, Cargo, Catalogo, Compromiso, Delegacion, Evidencia, Funcionario, FuncionarioRol,
	HistorialCompromiso, Indicador, ItemMedible, MedicionDelegacion, Meta, ParametroVersionado, Periodo,
	Rol, UsuarioMaestro, Validacion,
)
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone


def crear_funcionario(username, *roles, cargo=None, delegacion=None):
	"""Usuario de Django con su Funcionario y roles (la migración 0010 crea los seis roles del sistema)."""
	usuario = User.objects.create_user(username, password='clave-segura')
	cargo = cargo or Cargo.objects.get_or_create(nombre='Profesional territorial')[0]
	funcionario = Funcionario.objects.create(usuario=usuario, identificador_institucional=username, nombre=username, cargo=cargo, delegacion=delegacion)
	for rol in roles:
		FuncionarioRol.objects.create(funcionario=funcionario, rol=Rol.objects.get(nombre_rol=rol))
	return usuario


class OrganizacionAccesoTests(TestCase):
	"""CU-26, CU-30 (RF-001, RF-002, RF-036). Métodos de Delegacion, Cargo, Funcionario y Auditoria con la base de datos."""

	def setUp(self):
		self.centro = Delegacion.objects.create(nombre='Centro', ambito='Centro', enfasis='Atencion territorial')
		self.rural = Delegacion.objects.create(nombre='Rural', ambito='Rural', enfasis='Servicios cercanos')
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
	"""CU-05, CU-06.1, CU-07, CU-16.1, CU-28.1 (RF-005 a RF-007, RF-022 a RF-027). Reglas RN-001 a RN-008 y RN-013 de la medición."""

	def setUp(self):
		self.centro = Delegacion.objects.create(nombre='Centro', ambito='Centro', enfasis='Atencion territorial')
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
	"""CU-01, CU-10, CU-11, CU-23.1 (RF-009, RF-011, RF-013, RF-014, RF-034). RN-009, RN-010, control de versión y métodos de operación."""

	def setUp(self):
		media = tempfile.mkdtemp()
		self.addCleanup(shutil.rmtree, media, ignore_errors=True)
		ajuste_media = override_settings(MEDIA_ROOT=media)
		ajuste_media.enable()
		self.addCleanup(ajuste_media.disable)

		self.centro = Delegacion.objects.create(nombre='Centro', ambito='Centro', enfasis='Atencion territorial')
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
		datos = {'item': self.item, 'catalogo': self.catalogo, 'fecha': timezone.make_aware(datetime(2026, 9, dia, 10, 0)), 'solicitud_problema': 'Consulta vecinal', 'accion': 'Orientacion'}
		datos.update(cambios)
		return self.autor.registrar_actividad(datos)

	def _archivo(self, nombre='respaldo.pdf'):
		return SimpleUploadedFile(nombre, b'%PDF-1.4 prueba', content_type='application/pdf')

	def _validacion(self, evidencia):
		return Validacion(evidencia=evidencia, funcionario_verificador=self.verificador)

	def test_registrar_actividad_genera_codigo_y_toma_la_delegacion_del_autor(self):
		actividad = self._actividad()
		self.assertTrue(actividad.codigo_verificador.startswith('EVD-'))
		self.assertEqual((actividad.delegacion, actividad.version, actividad.estado), (self.centro, 1, 'pendiente'))

	def test_rn010_codigo_verificador_inmutable(self):
		actividad = self._actividad()
		actividad.codigo_verificador = 'EVD-OTRO'
		with self.assertRaises(ValidationError):
			actividad.save()

	def test_registrar_actividad_fuera_del_periodo_o_con_periodo_cerrado(self):
		with self.assertRaises(ValidationError):
			self._actividad(fecha=timezone.make_aware(datetime(2026, 10, 5, 10, 0)))
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
		historial = list(compromiso.historial.order_by('pk').values_list('estado_anterior', 'estado_nuevo', 'autor'))
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
	"""Sin CU (migración de datos). La migración 0010 copia los datos antiguos al modelo de 17 clases y se puede revertir."""

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
	"""CU-26, CU-26.1 (RF-002). tiene_rol y control de acceso por rol."""

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
	"""CU-04, CU-25, CU-26, CU-27, CU-27.1, CU-28 (RF-001 a RF-007). CRUD genérico de las ocho tablas maestras."""

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


class BaseOperacion(TestCase):
	"""Datos comunes de las pruebas de actividades, evidencias y compromisos."""

	def setUp(self):
		media = tempfile.mkdtemp()
		self.addCleanup(shutil.rmtree, media, ignore_errors=True)
		ajuste_media = override_settings(MEDIA_ROOT=media)
		ajuste_media.enable()
		self.addCleanup(ajuste_media.disable)

		self.cargo = Cargo.objects.create(nombre='Profesional territorial')
		self.centro = Delegacion.objects.create(nombre='Centro', ambito='Centro historico', enfasis='Atencion territorial')
		self.rural = Delegacion.objects.create(nombre='Rural', ambito='Rural', enfasis='Servicios cercanos')
		self.periodo = Periodo.objects.create(nombre='Septiembre 2026', fecha_inicio=date(2026, 9, 1), fecha_termino=date(2026, 9, 30), estado='abierto')
		self.item = ItemMedible.objects.create(cargo=self.cargo, periodo=self.periodo, nombre='Atencion territorial', ponderacion=100)
		self.catalogo = Catalogo.objects.create(codigo='AT-OPER', nombre='Operativo en terreno', tipo='atencion')
		# Los atributos son usuarios de Django; su Funcionario es usuario.funcionario.
		self.coordinador = crear_funcionario('coordinador-op', 'coordinador', cargo=self.cargo)
		self.verificador = crear_funcionario('verificador-op', 'verificador', cargo=self.cargo)
		self.funcionario = crear_funcionario('funcionario-op', 'funcionario', cargo=self.cargo, delegacion=self.centro)

	def _actividad(self, autor=None, delegacion=None, estado='pendiente', **cambios):
		datos = {
			'funcionario_autor': (autor or self.funcionario).funcionario, 'delegacion': delegacion or self.centro,
			'item': self.item, 'catalogo': self.catalogo, 'fecha': timezone.make_aware(datetime(2026, 9, 1, 10, 0)),
			'solicitud_problema': 'Solicitud original', 'accion': 'Accion', 'estado': estado,
		}
		datos.update(cambios)
		return Actividad.objects.create(**datos)

	def _datos_actividad(self, **cambios):
		datos = {
			'delegacion': self.centro.pk, 'item': self.item.pk, 'catalogo': self.catalogo.pk, 'fecha': '2026-09-01T10:00',
			'solicitud_problema': 'Solicitud corregida', 'accion': 'Accion', 'contacto_nombre': '', 'contacto_telefono': '',
		}
		datos.update(cambios)
		return datos

	def _archivo(self, nombre='respaldo.pdf'):
		return SimpleUploadedFile(nombre, b'%PDF-1.4 prueba', content_type='application/pdf')

	def _evidencia(self, actividad, **cambios):
		return Evidencia.objects.create(actividad=actividad, funcionario_autor=actividad.funcionario_autor, archivo_vinculo='evidencias/2026/09/respaldo.pdf', **cambios)

	def _compromiso(self, responsable=None, delegacion=None, folio='LS-OP-1'):
		return Compromiso.objects.create(
			folio=folio, delegacion=delegacion or self.centro, funcionario_responsable=(responsable or self.funcionario).funcionario,
			solicitante='Junta de vecinos', territorio='Centro', descripcion='Poda de arboles', fecha_comprometida=timezone.localdate() + timedelta(days=60), origen='externo',
		)


class ActividadVistasTests(BaseOperacion):
	"""CU-01, CU-01.1, CU-01.2, CU-10, CU-10.1, CU-10.2 (RF-009 a RF-011). Registro, consulta, modificación y eliminación de actividades."""

	def test_registrar_actividad_genera_codigo_y_auditoria(self):
		self.client.force_login(self.funcionario)
		respuesta = self.client.post(reverse('actividad_nueva'), self._datos_actividad(solicitud_problema='Consulta vecinal', contacto_nombre='Organizacion demo'))
		actividad = Actividad.objects.get(solicitud_problema='Consulta vecinal')
		self.assertRedirects(respuesta, reverse('actividad_detalle', args=[actividad.codigo_verificador]))
		self.assertTrue(actividad.codigo_verificador.startswith('EVD-'))
		self.assertEqual((actividad.funcionario_autor, actividad.estado, actividad.version), (self.funcionario.funcionario, 'pendiente', 1))
		self.assertTrue(Auditoria.objects.filter(entidad='Actividad', identificador_registro=actividad.codigo_verificador, evento='crear').exists())

	def test_el_formulario_ofrece_solo_los_items_del_cargo_del_funcionario(self):
		ajeno = ItemMedible.objects.create(cargo=Cargo.objects.create(nombre='Otro cargo'), periodo=self.periodo, nombre='Item ajeno', ponderacion=100)
		self.client.force_login(self.funcionario)
		self.assertQuerySetEqual(self.client.get(reverse('actividad_nueva')).context['form'].fields['item'].queryset, [self.item])
		self.client.force_login(self.coordinador)
		self.assertEqual(set(self.client.get(reverse('actividad_nueva')).context['form'].fields['item'].queryset), {self.item, ajeno})

	def test_rechaza_una_fecha_fuera_del_periodo_del_item(self):
		self.client.force_login(self.funcionario)
		respuesta = self.client.post(reverse('actividad_nueva'), self._datos_actividad(fecha='2026-10-05T10:00'))
		self.assertIn('fecha', respuesta.context['form'].errors)
		self.assertFalse(Actividad.objects.exists())

	def test_usuario_sin_funcionario_no_puede_registrar(self):
		self.client.force_login(User.objects.create_user('suelto', password='clave-segura'))
		respuesta = self.client.get(reverse('actividad_nueva'), follow=True)
		self.assertRedirects(respuesta, reverse('inicio'))
		self.assertContains(respuesta, 'no tiene un funcionario asociado')

	def test_funcionario_ve_solo_su_delegacion(self):
		visible = self._actividad()
		otro = crear_funcionario('otro-op', 'funcionario', cargo=self.cargo, delegacion=self.rural)
		oculta = self._actividad(autor=otro, delegacion=self.rural)
		self.client.force_login(self.funcionario)
		respuesta = self.client.get(reverse('actividades'))
		self.assertContains(respuesta, visible.codigo_verificador)
		self.assertNotContains(respuesta, oculta.codigo_verificador)

	def test_verificador_sin_delegacion_ve_todas_las_actividades(self):
		actividad = self._actividad()
		self.client.force_login(self.verificador)
		self.assertContains(self.client.get(reverse('actividades')), actividad.codigo_verificador)
		self.assertEqual(self.client.get(reverse('actividad_detalle', args=[actividad.codigo_verificador])).status_code, 200)

	def test_listado_enlaza_modificar_y_eliminar_reales(self):
		actividad = self._actividad()
		self.client.force_login(self.funcionario)
		respuesta = self.client.get(reverse('actividades'))
		self.assertContains(respuesta, reverse('actividad_editar', args=[actividad.codigo_verificador]))
		self.assertContains(respuesta, reverse('actividad_eliminar', args=[actividad.codigo_verificador]))
		self.assertNotContains(respuesta, 'href="#"')

	def test_autor_edita_su_actividad_y_audita(self):
		actividad = self._actividad()
		url = reverse('actividad_editar', args=[actividad.codigo_verificador])
		self.client.force_login(self.funcionario)
		respuesta = self.client.get(url)
		self.assertTemplateUsed(respuesta, 'delegaciones_app/actividad_form.html')
		self.assertContains(respuesta, 'name="version"')

		respuesta = self.client.post(url, self._datos_actividad(version=actividad.version))

		self.assertRedirects(respuesta, reverse('actividad_detalle', args=[actividad.codigo_verificador]))
		actividad.refresh_from_db()
		self.assertEqual((actividad.solicitud_problema, actividad.funcionario_autor, actividad.estado, actividad.version), ('Solicitud corregida', self.funcionario.funcionario, 'pendiente', 2))
		self.assertTrue(Auditoria.objects.filter(entidad='Actividad', identificador_registro=actividad.codigo_verificador, evento='editar').exists())

	def test_editar_actividad_rechazada_la_devuelve_a_revision_con_sus_evidencias(self):
		actividad = self._actividad(estado='rechazada')
		evidencia = self._evidencia(actividad, estado_revision='rechazada')
		self.client.force_login(self.funcionario)
		self.client.post(reverse('actividad_editar', args=[actividad.codigo_verificador]), self._datos_actividad(version=actividad.version))
		self.assertEqual(Actividad.objects.get(pk=actividad.pk).estado, 'pendiente')
		self.assertEqual(Evidencia.objects.get(pk=evidencia.pk).estado_revision, 'pendiente')

	def test_edicion_concurrente_se_rechaza_con_la_version_desactualizada(self):
		actividad = self._actividad()
		url = reverse('actividad_editar', args=[actividad.codigo_verificador])
		self.client.force_login(self.funcionario)
		self.client.post(url, self._datos_actividad(solicitud_problema='Guardada primero', version=1))
		respuesta = self.client.post(url, self._datos_actividad(solicitud_problema='Con version vieja', version=1))
		self.assertEqual(respuesta.status_code, 200)
		self.assertContains(respuesta, 'modificado por otro usuario')
		actividad.refresh_from_db()
		self.assertEqual((actividad.solicitud_problema, actividad.version), ('Guardada primero', 2))

	def test_actividad_aprobada_no_se_edita_ni_se_elimina(self):
		aprobada = self._actividad(estado='aprobada')
		self.client.force_login(self.coordinador)
		detalle = reverse('actividad_detalle', args=[aprobada.codigo_verificador])

		self.assertNotContains(self.client.get(reverse('actividades')), reverse('actividad_editar', args=[aprobada.codigo_verificador]))
		self.assertRedirects(self.client.post(reverse('actividad_editar', args=[aprobada.codigo_verificador]), self._datos_actividad(version=1)), detalle)
		self.assertRedirects(self.client.post(reverse('actividad_eliminar', args=[aprobada.codigo_verificador])), detalle)

		aprobada.refresh_from_db()
		self.assertEqual(aprobada.solicitud_problema, 'Solicitud original')
		self.assertFalse(Auditoria.objects.filter(identificador_registro=aprobada.codigo_verificador).exists())

	def test_actividad_de_un_periodo_cerrado_no_se_modifica(self):
		actividad = self._actividad()
		Periodo.objects.filter(pk=self.periodo.pk).update(estado='cerrado')
		self.client.force_login(self.coordinador)
		detalle = reverse('actividad_detalle', args=[actividad.codigo_verificador])
		self.assertRedirects(self.client.get(reverse('actividad_editar', args=[actividad.codigo_verificador])), detalle)
		self.assertRedirects(self.client.post(reverse('actividad_eliminar', args=[actividad.codigo_verificador])), detalle)
		self.assertTrue(Actividad.objects.filter(pk=actividad.pk).exists())

	def test_eliminar_requiere_confirmacion_post_y_borra_sus_evidencias(self):
		actividad = self._actividad()
		self._evidencia(actividad)
		url = reverse('actividad_eliminar', args=[actividad.codigo_verificador])
		self.client.force_login(self.funcionario)

		respuesta = self.client.get(url)
		self.assertEqual(respuesta.context['total_evidencias'], 1)
		self.assertContains(respuesta, 'también se eliminan sus evidencias')
		self.assertTrue(Actividad.objects.filter(pk=actividad.pk).exists())

		self.assertRedirects(self.client.post(url), reverse('actividades'))
		self.assertFalse(Actividad.objects.filter(pk=actividad.pk).exists())
		self.assertFalse(Evidencia.objects.filter(actividad_id=actividad.pk).exists())
		self.assertTrue(Auditoria.objects.filter(entidad='Actividad', identificador_registro=actividad.codigo_verificador, evento='eliminar').exists())

	def test_funcionario_de_otra_delegacion_no_puede_editar_ni_eliminar(self):
		actividad = self._actividad()
		self.client.force_login(crear_funcionario('intruso-op', 'funcionario', cargo=self.cargo, delegacion=self.rural))
		codigo = actividad.codigo_verificador
		self.assertEqual(self.client.get(reverse('actividad_editar', args=[codigo])).status_code, 404)
		self.assertEqual(self.client.post(reverse('actividad_editar', args=[codigo]), self._datos_actividad(version=1)).status_code, 404)
		self.assertEqual(self.client.post(reverse('actividad_eliminar', args=[codigo])).status_code, 404)
		self.assertEqual(Actividad.objects.get(pk=actividad.pk).solicitud_problema, 'Solicitud original')

	def test_funcionario_de_la_misma_delegacion_que_no_es_autor_no_puede_modificar(self):
		actividad = self._actividad()
		self.client.force_login(crear_funcionario('companero-op', 'funcionario', cargo=self.cargo, delegacion=self.centro))
		detalle = reverse('actividad_detalle', args=[actividad.codigo_verificador])
		self.assertRedirects(self.client.get(reverse('actividad_editar', args=[actividad.codigo_verificador])), detalle)
		self.assertRedirects(self.client.post(reverse('actividad_eliminar', args=[actividad.codigo_verificador])), detalle)
		self.assertTrue(Actividad.objects.filter(pk=actividad.pk).exists())

	def test_coordinador_puede_modificar_actividad_ajena(self):
		actividad = self._actividad()
		self.client.force_login(self.coordinador)
		respuesta = self.client.post(reverse('actividad_editar', args=[actividad.codigo_verificador]), self._datos_actividad(solicitud_problema='Ajustada por coordinacion', version=1))
		self.assertRedirects(respuesta, reverse('actividad_detalle', args=[actividad.codigo_verificador]))
		actividad.refresh_from_db()
		self.assertEqual((actividad.solicitud_problema, actividad.funcionario_autor), ('Ajustada por coordinacion', self.funcionario.funcionario))

	def test_subir_evidencia_la_envia_a_revision_y_audita(self):
		actividad = self._actividad(estado='correccion')
		self.client.force_login(self.funcionario)
		respuesta = self.client.post(reverse('actividad_detalle', args=[actividad.codigo_verificador]), {'archivo_vinculo': self._archivo(), 'comentario': 'Acta firmada'})
		self.assertRedirects(respuesta, reverse('actividad_detalle', args=[actividad.codigo_verificador]))
		evidencia = Evidencia.objects.get()
		self.assertEqual((evidencia.codigo_evidencia, evidencia.metadatos, evidencia.estado_revision), (f'{actividad.codigo_verificador}-01', {'comentario': 'Acta firmada'}, 'pendiente'))
		self.assertEqual(Actividad.objects.get(pk=actividad.pk).estado, 'pendiente')
		self.assertTrue(Auditoria.objects.filter(evento='cargar_evidencia', identificador_registro=actividad.codigo_verificador).exists())

	def test_evidencia_rechaza_extension_no_permitida(self):
		actividad = self._actividad()
		self.client.force_login(self.funcionario)
		archivo = SimpleUploadedFile('script.exe', b'MZ', content_type='application/octet-stream')
		respuesta = self.client.post(reverse('actividad_detalle', args=[actividad.codigo_verificador]), {'archivo_vinculo': archivo, 'comentario': ''})
		self.assertIn('archivo_vinculo', respuesta.context['evidencia_form'].errors)
		self.assertFalse(Evidencia.objects.exists())

	def test_actividad_aprobada_no_admite_nuevas_evidencias(self):
		actividad = self._actividad(estado='aprobada')
		self.client.force_login(self.funcionario)
		self.client.post(reverse('actividad_detalle', args=[actividad.codigo_verificador]), {'archivo_vinculo': self._archivo(), 'comentario': ''})
		self.assertFalse(Evidencia.objects.exists())
		self.assertContains(self.client.get(reverse('actividad_detalle', args=[actividad.codigo_verificador])), 'ya no admite nuevas evidencias')


class RevisionTests(BaseOperacion):
	"""CU-11, CU-11.1, CU-11.2 (RF-013, RF-014). Revisión de evidencias con Validacion (RN-009)."""

	def setUp(self):
		super().setUp()
		self.meta = Meta.objects.create(item=self.item, funcionario=self.funcionario.funcionario, valor_objetivo=10)
		self.actividad = self._actividad()
		self.evidencias = [self._evidencia(self.actividad), self._evidencia(self.actividad)]
		self.codigo = self.actividad.codigo_verificador

	def _revisar(self, decision, usuario=None, observacion=''):
		self.client.force_login(usuario or self.verificador)
		return self.client.post(reverse('revisar_actividad', args=[self.codigo, decision]), {'observacion': observacion})

	def test_aprobar_valida_cada_evidencia_pendiente_y_actualiza_el_indicador(self):
		self.assertRedirects(self._revisar('aprobar', observacion='Conforme'), reverse('actividad_detalle', args=[self.codigo]))
		self.assertEqual(Actividad.objects.get(pk=self.actividad.pk).estado, 'aprobada')
		self.assertEqual(set(Evidencia.objects.values_list('estado_revision', flat=True)), {'aprobada'})
		validaciones = Validacion.objects.all()
		self.assertEqual((validaciones.count(), {v.decision for v in validaciones}, {v.funcionario_verificador for v in validaciones}), (2, {'aprobada'}, {self.verificador.funcionario}))
		indicador = Indicador.objects.get(meta=self.meta)
		self.assertEqual((indicador.avance, indicador.cumplimiento), (1, Decimal('10.00')))
		self.assertTrue(Auditoria.objects.filter(evento='aprobar', identificador_registro=self.codigo).exists())

	def test_rechazar_y_pedir_correccion_exigen_observacion(self):
		for decision in ('rechazar', 'corregir'):
			self._revisar(decision, observacion='')
			self.assertEqual(Actividad.objects.get(pk=self.actividad.pk).estado, 'pendiente', decision)
			self.assertFalse(Validacion.objects.exists(), decision)
		self._revisar('corregir', observacion='Falta la firma')
		self.assertEqual(Actividad.objects.get(pk=self.actividad.pk).estado, 'correccion')
		self.assertEqual(set(Evidencia.objects.values_list('estado_revision', flat=True)), {'correccion'})

	def test_rechazo_sin_observacion_explica_el_motivo(self):
		respuesta = self._revisar('rechazar', observacion='')
		self.assertContains(self.client.get(respuesta.url), 'exige un motivo')

	def test_actividad_corregida_vuelve_a_revision_y_se_puede_aprobar(self):
		self._revisar('corregir', observacion='Falta la firma')
		self.client.force_login(self.funcionario)
		actividad = Actividad.objects.get(pk=self.actividad.pk)
		self.client.post(reverse('actividad_editar', args=[self.codigo]), self._datos_actividad(version=actividad.version))
		self.assertEqual(Actividad.objects.get(pk=self.actividad.pk).estado, 'pendiente')
		self._revisar('aprobar')
		self.assertEqual(Actividad.objects.get(pk=self.actividad.pk).estado, 'aprobada')
		self.assertEqual(Validacion.objects.filter(evidencia=self.evidencias[0]).count(), 2)

	def test_actividad_sin_evidencias_pendientes_no_se_revisa(self):
		sin_evidencias = self._actividad(solicitud_problema='Sin respaldo')
		self.client.force_login(self.verificador)
		respuesta = self.client.post(reverse('revisar_actividad', args=[sin_evidencias.codigo_verificador, 'aprobar']), follow=True)
		self.assertContains(respuesta, 'no tiene evidencias pendientes')
		self.assertEqual(Actividad.objects.get(pk=sin_evidencias.pk).estado, 'pendiente')

	def test_solo_administracion_coordinacion_y_verificacion_revisan(self):
		self._revisar('aprobar', usuario=self.funcionario)
		self.assertFalse(Validacion.objects.exists())
		self._revisar('aprobar', usuario=self.coordinador)
		self.assertEqual(Validacion.objects.count(), 2)

	def test_superusuario_sin_funcionario_no_puede_revisar(self):
		respuesta = self._revisar('aprobar', usuario=User.objects.create_superuser('super-op', password='clave-segura'))
		self.assertContains(self.client.get(respuesta.url), 'no tiene un funcionario asociado')
		self.assertFalse(Validacion.objects.exists())

	def test_el_detalle_ofrece_la_revision_solo_a_quien_puede_hacerla(self):
		url = reverse('actividad_detalle', args=[self.codigo])
		self.client.force_login(self.verificador)
		self.assertContains(self.client.get(url), 'Solicitar corrección')
		self.client.force_login(self.funcionario)
		self.assertNotContains(self.client.get(url), 'Solicitar corrección')


class CompromisoVistasTests(BaseOperacion):
	"""CU-02, CU-12, CU-13, CU-13.1, CU-23.1 (RF-016 a RF-018, RF-034). Agenda de compromisos con responsable, historial y control de versión."""

	def _datos(self, **cambios):
		datos = {
			'delegacion': self.centro.pk, 'funcionario_responsable': self.funcionario.funcionario.pk, 'origen': 'externo',
			'solicitante': 'Organizacion demo', 'territorio': 'Centro', 'eje': 'Seguridad', 'descripcion': 'Compromiso de prueba',
			'fecha_comprometida': '2026-09-30', 'area_apoyo': '', 'item': '', 'estado': 'pendiente', 'observacion': '',
		}
		datos.update(cambios)
		return datos

	def test_crear_compromiso_deja_historial_y_auditoria(self):
		self.client.force_login(self.funcionario)
		self.assertRedirects(self.client.post(reverse('compromiso_nuevo'), self._datos()), reverse('agenda'))
		compromiso = Compromiso.objects.get(descripcion='Compromiso de prueba')
		self.assertTrue(compromiso.folio.startswith('AGR-'))
		self.assertEqual((compromiso.funcionario_responsable, compromiso.version), (self.funcionario.funcionario, 1))
		registro = compromiso.historial.get()
		self.assertEqual((registro.estado_anterior, registro.estado_nuevo, registro.autor), ('', 'pendiente', self.funcionario.funcionario))
		self.assertTrue(Auditoria.objects.filter(evento='crear', entidad='Compromiso', identificador_registro=compromiso.folio).exists())
		self.assertContains(self.client.get(reverse('agenda')), compromiso.folio)

	def test_un_funcionario_siempre_queda_como_responsable_de_lo_que_crea(self):
		otro = crear_funcionario('otro-resp', 'funcionario', cargo=self.cargo, delegacion=self.centro)
		self.client.force_login(self.funcionario)
		respuesta = self.client.post(reverse('compromiso_nuevo'), self._datos(funcionario_responsable=otro.funcionario.pk))
		self.assertIn('funcionario_responsable', respuesta.context['form'].errors)

	def test_cambio_de_estado_queda_en_el_historial_y_en_la_auditoria(self):
		compromiso = self._compromiso()
		self.client.force_login(self.funcionario)
		self.client.post(reverse('compromiso_estado', args=[compromiso.pk, 'realizado']))
		compromiso.refresh_from_db()
		self.assertEqual(compromiso.estado, 'realizado')
		registro = compromiso.historial.get()
		self.assertEqual((registro.estado_anterior, registro.estado_nuevo), ('ingresado', 'realizado'))
		auditoria = Auditoria.objects.get(evento='cambio_estado', identificador_registro=compromiso.folio)
		self.assertEqual((auditoria.valor_anterior, auditoria.valor_nuevo), ('ingresado', 'realizado'))

	def test_solo_el_responsable_o_la_coordinacion_modifican_un_compromiso(self):
		compromiso = self._compromiso()
		url = reverse('compromiso_editar', args=[compromiso.pk])
		self.client.force_login(crear_funcionario('companero-comp', 'funcionario', cargo=self.cargo, delegacion=self.centro))
		self.assertRedirects(self.client.post(url, self._datos(descripcion='Intento ajeno', version=1)), reverse('agenda'))
		self.assertEqual(Compromiso.objects.get(pk=compromiso.pk).descripcion, 'Poda de arboles')

		self.client.force_login(self.funcionario)
		self.assertRedirects(self.client.post(url, self._datos(descripcion='Corregido por el responsable', version=1)), reverse('agenda'))
		self.client.force_login(self.coordinador)
		self.assertRedirects(self.client.post(url, self._datos(descripcion='Ajustado por coordinacion', version=2)), reverse('agenda'))
		compromiso.refresh_from_db()
		self.assertEqual((compromiso.descripcion, compromiso.version), ('Ajustado por coordinacion', 3))

	def test_el_formulario_de_edicion_no_cambia_el_estado_y_rechaza_versiones_viejas(self):
		compromiso = self._compromiso()
		url = reverse('compromiso_editar', args=[compromiso.pk])
		self.client.force_login(self.coordinador)
		self.assertNotIn('estado', self.client.get(url).context['form'].fields)
		self.client.post(url, self._datos(descripcion='Guardado primero', version=1))
		respuesta = self.client.post(url, self._datos(descripcion='Con version vieja', version=1))
		self.assertContains(respuesta, 'modificado por otro usuario')
		self.assertEqual(Compromiso.objects.get(pk=compromiso.pk).descripcion, 'Guardado primero')

	def test_solo_la_coordinacion_elimina_compromisos(self):
		compromiso = self._compromiso()
		compromiso.set_estado('proceso', self.funcionario.funcionario)
		self.client.force_login(self.funcionario)
		self.client.post(reverse('compromiso_eliminar', args=[compromiso.pk]))
		self.assertTrue(Compromiso.objects.filter(pk=compromiso.pk).exists())
		self.client.force_login(self.coordinador)
		self.client.post(reverse('compromiso_eliminar', args=[compromiso.pk]))
		self.assertFalse(Compromiso.objects.filter(pk=compromiso.pk).exists())
		self.assertFalse(HistorialCompromiso.objects.exists())


class AccesoAutenticadoTests(BaseOperacion):
	"""CU-26.1, CU-29.1 (RNF-004, RF-002). Acceso con identidad individual y resultados limitados al ámbito."""

	def setUp(self):
		super().setUp()
		self._compromiso(responsable=self.coordinador, delegacion=self.centro, folio='FOL-CENTRO-1')
		self._compromiso(responsable=self.coordinador, delegacion=self.rural, folio='FOL-RURAL-1')

	def test_vistas_internas_exigen_inicio_de_sesion(self):
		urls = (
			reverse('solicitudes'), reverse('agenda'), reverse('delegacion_detalle', args=['Centro']),
			reverse('dashboard'), reverse('semaforo'), reverse('resumen'),
		)
		for url in urls:
			self.assertRedirects(self.client.get(url), f"{reverse('login')}?next={url}")

	def test_portada_y_territorio_siguen_publicos(self):
		self.assertEqual(self.client.get(reverse('inicio')).status_code, 200)
		self.assertEqual(self.client.get(reverse('institucional')).status_code, 200)

	def test_funcionario_solo_ve_compromisos_de_su_delegacion(self):
		self.client.force_login(self.funcionario)
		for url in (reverse('solicitudes'), reverse('agenda')):
			respuesta = self.client.get(url)
			self.assertContains(respuesta, 'FOL-CENTRO-1')
			self.assertNotContains(respuesta, 'FOL-RURAL-1')
		self.assertNotContains(self.client.get(reverse('delegacion_detalle', args=['Rural'])), 'FOL-RURAL-1')

	def test_coordinador_ve_compromisos_de_todas_las_delegaciones(self):
		self.client.force_login(self.coordinador)
		respuesta = self.client.get(reverse('solicitudes'))
		self.assertContains(respuesta, 'FOL-CENTRO-1')
		self.assertContains(respuesta, 'FOL-RURAL-1')

	def test_logout_invalida_la_sesion(self):
		self.client.force_login(self.funcionario)
		self.assertRedirects(self.client.post(reverse('logout')), reverse('inicio'))
		self.assertNotIn('_auth_user_id', self.client.session)

	def test_usuario_sin_funcionario_no_ve_compromisos(self):
		self.client.force_login(User.objects.create_user('suelto-acceso', password='clave-segura'))
		self.assertNotContains(self.client.get(reverse('agenda')), 'FOL-CENTRO-1')


class MedicionVistasTests(BaseOperacion):
	"""CU-16, CU-16.1, CU-17, CU-18, CU-18.1 (RF-026 a RF-029). Portada, dashboard, semáforo y resumen leen los Indicador (RN-005, RN-006, RN-008)."""

	def setUp(self):
		super().setUp()
		self.rural_user = crear_funcionario('rural-op', 'funcionario', cargo=self.cargo, delegacion=self.rural)
		self.meta_centro = Meta.objects.create(item=self.item, funcionario=self.funcionario.funcionario, valor_objetivo=1)
		self.meta_rural = Meta.objects.create(item=self.item, funcionario=self.rural_user.funcionario, valor_objetivo=4)
		self._aprobar(self._actividad())
		self._aprobar(self._actividad(autor=self.rural_user, delegacion=self.rural))
		self._calcular()

	def _aprobar(self, actividad):
		Validacion(evidencia=self._evidencia(actividad), funcionario_verificador=self.verificador.funcionario).aprobar_evidencia()

	def _calcular(self):
		Indicador.objects.all().delete()
		for meta in Meta.objects.all():
			Indicador.generar(meta)

	def _filas(self, url='dashboard', usuario=None, **parametros):
		self.client.force_login(usuario or self.coordinador)
		respuesta = self.client.get(reverse(url), parametros)
		return respuesta, {fila['nombre']: fila for fila in respuesta.context['delegaciones']}

	def test_dashboard_muestra_el_cumplimiento_y_el_semaforo_de_cada_delegacion(self):
		respuesta, filas = self._filas()
		self.assertEqual(set(filas), {'Centro', 'Rural'})
		self.assertEqual((filas['Centro']['cumplimiento'], filas['Centro']['estado']), (Decimal('100.00'), 'Verde'))
		self.assertEqual((filas['Rural']['cumplimiento'], filas['Rural']['estado']), (Decimal('25.00'), 'Rojo'))
		self.assertEqual(respuesta.context['periodo'], self.periodo)
		self.assertContains(respuesta, 'Septiembre 2026')
		self.assertContains(respuesta, 'Tope: 150 %')
		self.assertEqual(filas['Centro']['detalle'], ['Atencion territorial: 1 de 1 actividades'])

	def test_las_barras_de_progreso_no_usan_coma_decimal(self):
		self.meta_rural.valor_objetivo = 3
		self.meta_rural.save()
		self._calcular()
		respuesta, filas = self._filas()
		self.assertEqual(filas['Rural']['cumplimiento'], Decimal('33.33'))
		self.assertContains(respuesta, 'width: 33.33%')
		self.assertNotContains(respuesta, 'width: 33,33%')

	def test_el_cumplimiento_de_la_delegacion_pondera_sus_metas(self):
		otro = crear_funcionario('otro-centro', 'funcionario', cargo=self.cargo, delegacion=self.centro)
		self.meta_centro.ponderador = 60
		self.meta_centro.save()
		meta = Meta.objects.create(item=self.item, funcionario=otro.funcionario, valor_objetivo=10, ponderador=40)
		indicador = Indicador(meta=meta, periodo=self.periodo, avance=5)
		indicador.calcular_cumplimiento()
		indicador.save()
		self._calcular_solo(self.meta_centro)
		# 60 % de la meta al 100 % y 40 % de la meta al 50 % dan un 80 % ponderado.
		self.assertEqual(self.centro.obtener_cumplimiento_global(self.periodo), Decimal('80.00'))

	def _calcular_solo(self, meta):
		Indicador.objects.filter(meta=meta).delete()
		Indicador.generar(meta)

	def test_solo_cuenta_el_ultimo_indicador_de_cada_meta(self):
		self.meta_rural.valor_objetivo = 2
		self.meta_rural.save()
		Indicador.generar(self.meta_rural)
		self.assertEqual(self.rural.obtener_cumplimiento_global(self.periodo), Decimal('50.00'))
		self.assertEqual(Indicador.objects.filter(meta=self.meta_rural).count(), 2)

	def test_semaforo_segun_lo_esperado_al_dia(self):
		mitad = date(2026, 9, 15)
		self.assertEqual(self.periodo.porcentaje_esperado(mitad), Decimal('50.00'))
		self.assertEqual([self.periodo.calcular_semaforo(Decimal(valor), mitad) for valor in ('50', '30', '29.99')], ['verde', 'ambar', 'rojo'])

	def test_selector_de_periodo_y_busqueda_por_delegacion(self):
		octubre = Periodo.objects.create(nombre='Octubre 2026', fecha_inicio=date(2026, 10, 1), fecha_termino=date(2026, 10, 31), estado='abierto')
		item = ItemMedible.objects.create(cargo=self.cargo, periodo=octubre, nombre='Atencion de octubre', ponderacion=100)
		Indicador.generar(Meta.objects.create(item=item, funcionario=self.funcionario.funcionario, valor_objetivo=5))

		respuesta, filas = self._filas()
		self.assertEqual((respuesta.context['periodo'], set(filas)), (octubre, {'Centro'}))
		respuesta, filas = self._filas(periodo=self.periodo.pk)
		self.assertEqual((respuesta.context['periodo'], set(filas)), (self.periodo, {'Centro', 'Rural'}))
		self.assertEqual(self._filas(periodo='no-es-un-numero')[0].context['periodo'], octubre)
		self.assertEqual(set(self._filas(periodo=self.periodo.pk, q='rur')[1]), {'Rural'})

	def test_sin_indicadores_se_avisa_y_una_delegacion_sin_calculo_se_marca(self):
		Indicador.objects.filter(meta=self.meta_rural).delete()
		self.assertEqual(self._filas()[1]['Rural']['estado'], 'Sin cálculo')
		Indicador.objects.all().delete()
		respuesta, filas = self._filas()
		self.assertEqual(filas, {})
		self.assertContains(respuesta, 'Todavía no hay indicadores calculados')

	def test_semaforo_y_resumen_comparten_los_resultados(self):
		respuesta, filas = self._filas('semaforo')
		self.assertEqual(filas['Centro']['estado'], 'Verde')
		self.assertContains(respuesta, 'ámbar desde el 60 %')
		MedicionDelegacion.objects.create(delegacion=self.centro, cumplimiento=88, meta=92, fecha_datos=date(2026, 8, 24), estado_reportado='verde', observacion='Dato historico importado')
		respuesta, _ = self._filas('resumen')
		contexto = respuesta.context
		self.assertEqual((contexto['promedio'], contexto['mejor']['nombre'], contexto['critico']['nombre']), (Decimal('62.50'), 'Centro', 'Rural'))
		self.assertFalse(contexto['alcanza_umbral'])
		self.assertContains(respuesta, 'No alcanza el umbral colectivo de 80')
		self.assertContains(respuesta, 'Dato historico importado')

	def test_la_portada_usa_el_promedio_de_los_indicadores(self):
		self.assertEqual(self.client.get(reverse('inicio')).context['promedio'], Decimal('62.50'))
		Indicador.objects.all().delete()
		self.assertEqual(self.client.get(reverse('inicio')).context['promedio'], Decimal('0.00'))

	def test_gestionar_metas_solo_para_administracion_y_coordinacion(self):
		respuesta, _ = self._filas()
		self.assertContains(respuesta, 'Gestionar metas')
		self.assertContains(respuesta, '+ Agregar meta')
		respuesta, _ = self._filas(usuario=self.funcionario)
		self.assertNotContains(respuesta, 'Gestionar metas')
		self.assertNotContains(respuesta, '+ Agregar meta')


CLAVE_DEMO = 'Clave-segura-2026'


def cargar_demo():
	call_command('seed_demo', password=CLAVE_DEMO, stdout=StringIO())


def contar_filas():
	"""Número de filas de cada modelo de la aplicación, para comprobar que repetir la carga no duplica."""
	return {modelo.__name__: modelo.objects.count() for modelo in apps.get_app_config('delegaciones_app').get_models()}


class SeedDemoTests(TestCase):
	"""Sin CU (datos de demostración). seed_demo crea los datos en el modelo de 17 clases y se puede repetir."""

	def test_carga_el_modelo_nuevo_con_sus_datos_de_demostracion(self):
		cargar_demo()
		filas = contar_filas()
		esperadas = {
			'Delegacion': 6, 'Funcionario': 9, 'FuncionarioRol': 9, 'UsuarioMaestro': 1, 'Periodo': 1, 'ParametroVersionado': 1,
			'ItemMedible': 1, 'Meta': 6, 'Catalogo': 5, 'Indicador': 6, 'Compromiso': 8, 'HistorialCompromiso': 8,
			'Actividad': 1, 'Evidencia': 1, 'Validacion': 1, 'MedicionDelegacion': 6,
		}
		for modelo, total in esperadas.items():
			self.assertEqual(filas[modelo], total, modelo)

	def test_cuentas_demo_y_delegados_inactivos(self):
		cargar_demo()
		administrador = User.objects.get(username='admin.demo')
		self.assertTrue(administrador.check_password(CLAVE_DEMO))
		self.assertTrue(administrador.is_superuser and administrador.usuario_maestro.estado)
		self.assertEqual(roles_de(administrador), {'administrador'})
		centro = User.objects.get(username='funcionario.centro')
		self.assertEqual((roles_de(centro), centro.funcionario.delegacion.nombre), ({'funcionario'}, 'Centro'))
		delegado = User.objects.get(username='delegado.las-companias')
		self.assertFalse(delegado.is_active)
		self.assertFalse(delegado.has_usable_password())
		self.assertEqual(delegado.funcionario.delegacion.nombre, 'Las Compañías')

	def test_repetir_la_carga_no_duplica_nada(self):
		cargar_demo()
		antes = contar_filas()
		cargar_demo()
		self.assertEqual(contar_filas(), antes)

	def test_la_demo_se_ve_en_la_aplicacion(self):
		cargar_demo()
		self.assertTrue(self.client.login(username='coordinador.demo', password=CLAVE_DEMO))
		respuesta = self.client.get(reverse('dashboard'))
		filas = {fila['nombre']: fila for fila in respuesta.context['delegaciones']}
		self.assertEqual(len(filas), 6)
		self.assertEqual((filas['Centro']['cumplimiento'], filas['Rural']['cumplimiento']), (Decimal('10.00'), Decimal('0.00')))
		self.assertContains(self.client.get(reverse('agenda')), 'LS-2026-014')
		self.assertEqual(self.client.get(reverse('actividades')).status_code, 200)

	def test_convive_con_datos_ya_migrados_sin_duplicarlos(self):
		cargo = Cargo.objects.create(nombre='Sin cargo asignado')
		centro = Delegacion.objects.create(nombre='Centro', ambito='Centro historico', enfasis='Atencion')
		usuario = User.objects.create_user('funcionario.centro', password='clave-previa')
		migrado = Funcionario.objects.create(usuario=usuario, identificador_institucional='funcionario.centro', nombre='Funcionario Centro', cargo=cargo, delegacion=centro)
		FuncionarioRol.objects.create(funcionario=migrado, rol=Rol.objects.get(nombre_rol='funcionario'))
		periodo = Periodo.objects.create(nombre='Trimestre julio-septiembre 2026', fecha_inicio=date(2026, 7, 1), fecha_termino=date(2026, 9, 30), estado='abierto')
		item = ItemMedible.objects.create(nombre='Seguridad y prevencion', cargo=cargo, periodo=periodo, ponderacion=100)
		Meta.objects.create(item=item, funcionario=migrado, valor_objetivo=10)

		cargar_demo()

		self.assertEqual(Funcionario.objects.get(pk=migrado.pk).cargo, cargo)
		self.assertTrue(User.objects.get(pk=usuario.pk).check_password('clave-previa'))
		self.assertEqual(Meta.objects.filter(funcionario=migrado).count(), 1)
		self.assertEqual(ItemMedible.objects.filter(cargo=cargo).count(), 1)
		self.assertEqual((Funcionario.objects.count(), Meta.objects.count(), Periodo.objects.count()), (9, 6, 1))


class AdminTests(TestCase):
	"""CU-26, CU-30 (RF-001, RF-002, RF-036). El Django Admin administra los 19 modelos (las 17 clases, FuncionarioRol y MedicionDelegacion)."""

	@classmethod
	def setUpTestData(cls):
		cargar_demo()

	def setUp(self):
		self.assertTrue(self.client.login(username='admin.demo', password=CLAVE_DEMO))

	def _modelos(self):
		return [modelo for modelo in admin.site._registry if modelo._meta.app_label == 'delegaciones_app']

	def _url(self, modelo, accion, *args):
		return reverse(f'admin:delegaciones_app_{modelo._meta.model_name}_{accion}', args=args)

	def test_estan_registrados_los_19_modelos(self):
		self.assertEqual(len(self._modelos()), 19)
		todos = {modelo.__name__ for modelo in apps.get_app_config('delegaciones_app').get_models()}
		self.assertEqual(todos - {modelo.__name__ for modelo in self._modelos()}, set())

	def test_cada_modelo_se_lista_busca_y_se_abre_para_agregar_y_modificar(self):
		for modelo in self._modelos():
			nombre = modelo.__name__
			self.assertEqual(self.client.get(self._url(modelo, 'changelist')).status_code, 200, nombre)
			self.assertEqual(self.client.get(self._url(modelo, 'changelist'), {'q': 'demo'}).status_code, 200, nombre)
			# La auditoría es de solo lectura: ni el superusuario puede agregar (CU-30.1).
			self.assertEqual(self.client.get(self._url(modelo, 'add')).status_code, 403 if modelo is Auditoria else 200, nombre)
			objeto = modelo.objects.first()
			if objeto is not None:
				self.assertEqual(self.client.get(self._url(modelo, 'change', objeto.pk)).status_code, 200, nombre)

	def test_un_periodo_cerrado_y_lo_que_depende_de_el_no_se_eliminan(self):
		periodo = Periodo.objects.get()
		Periodo.objects.filter(pk=periodo.pk).update(estado='cerrado')
		for modelo, objeto in ((Periodo, periodo), (ItemMedible, ItemMedible.objects.first()), (Meta, Meta.objects.first()), (Indicador, Indicador.objects.first())):
			self.assertEqual(self.client.get(self._url(modelo, 'delete', objeto.pk)).status_code, 403, modelo.__name__)
		Periodo.objects.filter(pk=periodo.pk).update(estado='abierto')
		self.assertEqual(self.client.get(self._url(Periodo, 'delete', periodo.pk)).status_code, 200)

	def test_un_usuario_staff_sin_permisos_no_agrega_auditoria(self):
		empleado = User.objects.create_user('staff-sin-permisos', password=CLAVE_DEMO, is_staff=True)
		self.client.force_login(empleado)
		self.assertEqual(self.client.get(self._url(Auditoria, 'add')).status_code, 403)


class AuditoriaTests(BaseOperacion):
	"""CU-26.1, CU-30, CU-30.1 (RF-036, RNF-008). Auditoría inmutable, accesos denegados y cambios del admin auditados."""

	def _evento(self, evento, entidad=None):
		eventos = Auditoria.objects.filter(evento=evento)
		return eventos.filter(entidad=entidad) if entidad else eventos

	def _superusuario(self):
		cargar_demo()
		self.assertTrue(self.client.login(username='admin.demo', password=CLAVE_DEMO))

	def test_un_evento_registrado_no_se_modifica_ni_se_elimina(self):
		evento = Auditoria.registrar_evento(self.coordinador, 'crear', 'Cargo', 1)
		evento.evento = 'otro'
		with self.assertRaises(ValidationError):
			evento.save()
		with self.assertRaises(ValidationError):
			evento.delete()
		with self.assertRaises(ValidationError):
			Auditoria.objects.all().update(evento='otro')
		with self.assertRaises(ValidationError):
			Auditoria.objects.all().delete()
		self.assertEqual(Auditoria.objects.get(pk=evento.pk).evento, 'crear')

	def test_el_superusuario_no_puede_agregar_modificar_ni_eliminar_auditoria_y_el_intento_se_registra(self):
		self._superusuario()
		evento = Auditoria.registrar_evento(self.coordinador, 'crear', 'Cargo', 1)
		self.assertEqual(self.client.get(reverse('admin:delegaciones_app_auditoria_add')).status_code, 403)
		self.assertEqual(self.client.post(reverse('admin:delegaciones_app_auditoria_change', args=[evento.pk]), {'evento': 'otro'}).status_code, 403)
		self.assertEqual(self.client.post(reverse('admin:delegaciones_app_auditoria_delete', args=[evento.pk]), {'post': 'yes'}).status_code, 403)
		self.assertEqual(Auditoria.objects.get(pk=evento.pk).evento, 'crear')
		acciones = [json.loads(e.valor_nuevo)['accion'] for e in self._evento('intento_alteracion', 'Auditoria').order_by('pk')]
		self.assertEqual(acciones, ['agregar', 'modificar', 'eliminar'])
		# Ver sigue permitido y no ofrece acciones de borrado masivo.
		self.assertEqual(self.client.get(reverse('admin:delegaciones_app_auditoria_changelist')).status_code, 200)
		self.assertEqual(self.client.get(reverse('admin:delegaciones_app_auditoria_change', args=[evento.pk])).status_code, 200)

	def test_los_cambios_hechos_en_el_admin_quedan_auditados(self):
		self._superusuario()
		self.client.post(reverse('admin:delegaciones_app_cargo_add'), {'nombre': 'Cargo del admin', 'vigencia': 'on'})
		cargo = Cargo.objects.get(nombre='Cargo del admin')
		self.assertEqual(self._evento('admin_crear', 'Cargo').get().identificador_registro, str(cargo.pk))

		self.client.post(reverse('admin:delegaciones_app_cargo_change', args=[cargo.pk]), {'nombre': 'Cargo renombrado', 'vigencia': 'on'})
		edicion = self._evento('admin_editar', 'Cargo').get()
		self.assertEqual((edicion.valor_anterior, edicion.valor_nuevo), ('{"nombre": "Cargo del admin"}', '{"nombre": "Cargo renombrado"}'))

		self.client.post(reverse('admin:delegaciones_app_cargo_delete', args=[cargo.pk]), {'post': 'yes'})
		self.assertFalse(Cargo.objects.filter(pk=cargo.pk).exists())
		self.assertEqual(json.loads(self._evento('admin_eliminar', 'Cargo').get().valor_anterior), {'descripcion': 'Cargo renombrado'})

	def test_el_cambio_de_un_parametro_desde_el_admin_queda_auditado(self):
		self._superusuario()
		parametro = ParametroVersionado.objects.get(clave='maximo_cumplimiento')
		self.client.post(reverse('admin:delegaciones_app_parametroversionado_change', args=[parametro.pk]), {'periodo': parametro.periodo.pk, 'clave': 'maximo_cumplimiento', 'valor': '120', 'descripcion': parametro.descripcion})
		self.assertEqual(ParametroVersionado.objects.get(pk=parametro.pk).valor, '120')
		cambio = self._evento('admin_editar', 'ParametroVersionado').get()
		self.assertEqual((cambio.valor_anterior, cambio.valor_nuevo), ('{"valor": "150"}', '{"valor": "120"}'))

	def test_un_acceso_denegado_por_rol_queda_registrado(self):
		self.client.force_login(self.funcionario)
		self.client.get(reverse('mantenedor_lista', args=['catalogo']))
		evento = self._evento('acceso_denegado', 'Acceso').get()
		self.assertEqual(evento.funcionario, self.funcionario.funcionario)
		self.assertEqual(json.loads(evento.valor_nuevo)['motivo'], 'rol insuficiente')

	def test_sin_sesion_no_se_registra_acceso_denegado(self):
		self.client.get(reverse('mantenedor_lista', args=['catalogo']))
		self.assertFalse(self._evento('acceso_denegado').exists())

	def test_consultar_un_registro_fuera_del_ambito_da_404_y_queda_registrado(self):
		actividad = self._actividad()
		self.client.force_login(crear_funcionario('intruso-aud', 'funcionario', cargo=self.cargo, delegacion=self.rural))
		self.assertEqual(self.client.get(reverse('actividad_detalle', args=[actividad.codigo_verificador])).status_code, 404)
		evento = self._evento('acceso_denegado', 'Actividad').get()
		self.assertEqual((evento.identificador_registro, json.loads(evento.valor_nuevo)['motivo']), (actividad.codigo_verificador, 'fuera del ámbito'))

	def test_un_codigo_inexistente_da_404_sin_registrar_acceso_denegado(self):
		self.client.force_login(self.funcionario)
		self.assertEqual(self.client.get(reverse('actividad_detalle', args=['EVD-NO-EXISTE'])).status_code, 404)
		self.assertFalse(self._evento('acceso_denegado').exists())

	def test_modificar_lo_de_otro_sin_ser_responsable_ni_autor_queda_registrado(self):
		compromiso = self._compromiso()
		actividad = self._actividad()
		self.client.force_login(crear_funcionario('companero-aud', 'funcionario', cargo=self.cargo, delegacion=self.centro))
		self.client.get(reverse('compromiso_editar', args=[compromiso.pk]))
		self.client.get(reverse('actividad_editar', args=[actividad.codigo_verificador]))
		motivos = sorted(json.loads(e.valor_nuevo)['motivo'] for e in self._evento('acceso_denegado'))
		self.assertEqual(motivos, ['no es el autor', 'no es el responsable'])

	def test_un_rechazo_por_regla_de_negocio_no_cuenta_como_acceso_denegado(self):
		aprobada = self._actividad(estado='aprobada')
		self.client.force_login(self.coordinador)
		self.client.get(reverse('actividad_editar', args=[aprobada.codigo_verificador]))
		self.assertFalse(self._evento('acceso_denegado').exists())

	def test_la_consulta_de_auditoria_filtra_y_solo_la_ve_el_administrador(self):
		administrador = crear_funcionario('admin-aud', 'administrador', cargo=self.cargo)
		Auditoria.registrar_evento(self.coordinador, 'crear', 'Cargo', 'C-1', None, {'nombre': 'Uno'})
		Auditoria.registrar_evento(self.coordinador, 'editar', 'Delegacion', 'D-1')
		self.client.force_login(administrador)
		url = reverse('auditoria_consulta')
		respuesta = self.client.get(url)
		self.assertContains(respuesta, 'Auditoría de cambios')
		self.assertContains(respuesta, 'C-1')
		self.assertContains(self.client.get(url, {'entidad': 'Cargo'}), 'C-1')
		self.assertNotContains(self.client.get(url, {'entidad': 'Cargo'}), 'D-1')
		self.assertNotContains(self.client.get(url, {'evento': 'editar'}), 'C-1')
		self.assertContains(self.client.get(url, {'q': 'D-1'}), 'D-1')
		hoy = timezone.localdate().isoformat()
		self.assertContains(self.client.get(url, {'desde': hoy, 'hasta': hoy}), 'C-1')
		self.assertNotContains(self.client.get(url, {'desde': '2999-01-01'}), 'C-1')
		# Solo lectura: no hay formularios ni acciones de modificación.
		self.assertNotContains(respuesta, 'Eliminar')
		contenido = respuesta.content.decode().split('<main', 1)[1]
		self.assertNotIn('method="post"', contenido)
		self.client.force_login(self.coordinador)
		self.assertRedirects(self.client.get(url), reverse('inicio'))
		self.assertTrue(self._evento('acceso_denegado').exists())

	def test_el_indice_de_mantenedores_enlaza_la_auditoria_solo_al_administrador(self):
		self.client.force_login(self.coordinador)
		self.assertNotContains(self.client.get(reverse('mantenedores')), reverse('auditoria_consulta'))
		self.client.force_login(crear_funcionario('admin-aud2', 'administrador', cargo=self.cargo))
		self.assertContains(self.client.get(reverse('mantenedores')), reverse('auditoria_consulta'))


class EvidenciaTamanoTests(BaseOperacion):
	"""CU-09.2 (RF-012, RNF-017). Las evidencias que superan el tamaño máximo configurado se rechazan con su motivo."""

	def _pdf(self, megabytes):
		return SimpleUploadedFile('respaldo.pdf', b'0' * int(megabytes * 1024 * 1024), content_type='application/pdf')

	@override_settings(EVIDENCIA_TAMANO_MAXIMO_MB=1)
	def test_el_validador_acepta_hasta_el_maximo_y_rechaza_lo_que_lo_supera(self):
		validar_tamano_evidencia(self._pdf(1))
		with self.assertRaises(ValidationError) as error:
			validar_tamano_evidencia(self._pdf(1.5))
		self.assertIn('1.5 MB', error.exception.messages[0])
		self.assertIn('máximo permitido es 1 MB', error.exception.messages[0])

	def test_el_maximo_por_defecto_es_de_5_megabytes(self):
		validar_tamano_evidencia(self._pdf(5))
		with self.assertRaises(ValidationError):
			validar_tamano_evidencia(self._pdf(5.5))

	def test_un_archivo_guardado_que_falta_en_el_disco_no_se_mide(self):
		actividad = self._actividad()
		evidencia = self._evidencia(actividad)
		self.assertIsNone(validar_tamano_evidencia(evidencia.archivo_vinculo))

	@override_settings(EVIDENCIA_TAMANO_MAXIMO_MB=1)
	def test_el_formulario_de_evidencia_informa_el_motivo_del_rechazo(self):
		actividad = self._actividad()
		self.client.force_login(self.funcionario)
		respuesta = self.client.post(reverse('actividad_detalle', args=[actividad.codigo_verificador]), {'archivo_vinculo': self._pdf(1.5), 'comentario': ''})
		self.assertIn('archivo_vinculo', respuesta.context['evidencia_form'].errors)
		self.assertContains(respuesta, 'máximo permitido es 1 MB')
		self.assertFalse(Evidencia.objects.exists())

	@override_settings(EVIDENCIA_TAMANO_MAXIMO_MB=1)
	def test_subir_evidencia_rechaza_un_archivo_demasiado_pesado(self):
		with self.assertRaises(ValidationError):
			self.funcionario.funcionario.subir_evidencia(self._actividad(), self._pdf(1.5))


class CompromisoReglasTests(BaseOperacion):
	"""CU-13, CU-14.2, CU-02.3 (RF-018, RF-019). Transiciones controladas, alerta de vencimiento y conservación de incumplimientos."""

	def _con_plazo(self, dias, estado='pendiente', folio=None):
		compromiso = self._compromiso(folio=folio or f'PLAZO-{dias}-{estado}')
		compromiso.fecha_comprometida = timezone.localdate() + timedelta(days=dias)
		compromiso.estado = estado
		compromiso.save()
		return compromiso

	def test_proximo_a_vencer_dentro_de_los_dias_de_alerta(self):
		casos = [(0, 'pendiente', True), (3, 'pendiente', True), (4, 'pendiente', False), (-1, 'pendiente', False), (2, 'realizado', False)]
		for dias, estado, esperado in casos:
			compromiso = self._con_plazo(dias, estado)
			self.assertEqual(compromiso.proximo_a_vencer, esperado, (dias, estado))

	@override_settings(COMPROMISO_DIAS_ALERTA=7)
	def test_los_dias_de_alerta_son_configurables(self):
		self.assertTrue(self._con_plazo(7).proximo_a_vencer)
		self.assertFalse(self._con_plazo(8).proximo_a_vencer)

	def test_vencido_y_proximo_a_vencer_son_excluyentes(self):
		vencido = self._con_plazo(-2)
		self.assertTrue(vencido.vencido)
		self.assertFalse(vencido.proximo_a_vencer)
		self.assertFalse(self._con_plazo(1).vencido)

	def test_estados_permitidos_avanzan_y_un_realizado_solo_se_reabre_a_en_proceso(self):
		esperado = {
			'ingresado': ['pendiente', 'proceso', 'realizado'], 'pendiente': ['proceso', 'realizado'],
			'proceso': ['realizado'], 'realizado': ['proceso'],
		}
		for estado, permitidos in esperado.items():
			compromiso = self._con_plazo(30, estado, folio=f'TR-{estado}')
			self.assertEqual([valor for valor, _ in compromiso.estados_permitidos()], permitidos, estado)

	def test_una_transicion_no_permitida_se_rechaza_y_no_deja_historial(self):
		compromiso = self._con_plazo(30, 'proceso')
		with self.assertRaises(ValidationError) as error:
			compromiso.set_estado('pendiente', self.funcionario.funcionario)
		self.assertIn('Transición no permitida', error.exception.messages[0])
		with self.assertRaises(ValidationError):
			compromiso.set_estado('inexistente', self.funcionario.funcionario)
		self.assertEqual(Compromiso.objects.get(pk=compromiso.pk).estado, 'proceso')
		self.assertFalse(compromiso.historial.exists())

	def test_reabrir_un_realizado_guarda_la_observacion_en_el_historial(self):
		compromiso = self._con_plazo(30, 'realizado')
		compromiso.set_estado('proceso', self.funcionario.funcionario, 'Se detectó un error en el cierre')
		registro = compromiso.historial.get()
		self.assertEqual((registro.estado_anterior, registro.estado_nuevo, registro.observacion), ('realizado', 'proceso', 'Se detectó un error en el cierre'))

	def test_cerrar_un_compromiso_ya_realizado_se_rechaza(self):
		with self.assertRaises(ValidationError):
			self._con_plazo(30, 'realizado').cerrar_compromiso('Otra resolución', self.funcionario.funcionario)

	def test_un_incumplimiento_no_se_elimina_pero_uno_vigente_o_realizado_si(self):
		vencido = self._con_plazo(-5)
		self.assertIn('se conserva con su historial', vencido.motivo_no_eliminable())
		with self.assertRaises(ValidationError):
			vencido.delete()
		self.assertTrue(Compromiso.objects.filter(pk=vencido.pk).exists())
		vigente, realizado = self._con_plazo(30), self._con_plazo(-5, 'realizado', folio='REALIZADO-VENCIDO')
		self.assertIsNone(vigente.motivo_no_eliminable())
		vigente.delete()
		realizado.delete()
		self.assertFalse(Compromiso.objects.filter(pk__in=[vigente.pk, realizado.pk]).exists())

	def test_la_vista_de_eliminar_explica_por_que_no_se_puede(self):
		vencido = self._con_plazo(-5)
		self.client.force_login(self.coordinador)
		self.assertContains(self.client.get(reverse('compromiso_eliminar', args=[vencido.pk])), 'se conserva con su historial')
		respuesta = self.client.post(reverse('compromiso_eliminar', args=[vencido.pk]), follow=True)
		self.assertContains(respuesta, 'se conserva con su historial')
		self.assertTrue(Compromiso.objects.filter(pk=vencido.pk).exists())
		self.assertFalse(Auditoria.objects.filter(evento='eliminar', entidad='Compromiso').exists())

	def test_la_agenda_destaca_los_proximos_a_vencer_y_cuenta_cada_grupo(self):
		self._con_plazo(2, folio='POR-VENCER')
		self._con_plazo(-3, folio='YA-VENCIDO')
		self._con_plazo(40, 'realizado', folio='YA-REALIZADO')
		self.client.force_login(self.coordinador)
		respuesta = self.client.get(reverse('agenda'))
		self.assertContains(respuesta, '1 compromiso próximo a vencer')
		self.assertContains(respuesta, 'Próximo a vencer')
		contexto = respuesta.context
		self.assertEqual((contexto['por_vencer'], contexto['vencidos'], contexto['realizados'], contexto['proximos']), (1, 1, 1, 1))
		estados = {c.folio: c.estado_display for c in contexto['compromisos']}
		self.assertEqual(estados, {'POR-VENCER': 'Próximo a vencer', 'YA-VENCIDO': 'Vencido', 'YA-REALIZADO': 'Realizado'})

	def test_la_agenda_ofrece_solo_las_transiciones_permitidas(self):
		compromiso = self._con_plazo(30, 'proceso')
		self.client.force_login(self.coordinador)
		respuesta = self.client.get(reverse('agenda'))
		self.assertContains(respuesta, reverse('compromiso_estado', args=[compromiso.pk, 'realizado']))
		self.assertNotContains(respuesta, reverse('compromiso_estado', args=[compromiso.pk, 'pendiente']))

	def test_el_cambio_de_estado_desde_la_vista_guarda_la_observacion_y_rechaza_lo_no_permitido(self):
		compromiso = self._con_plazo(30, 'proceso')
		self.client.force_login(self.coordinador)
		self.client.post(reverse('compromiso_estado', args=[compromiso.pk, 'realizado']), {'observacion': 'Entregado a la junta de vecinos'})
		compromiso.refresh_from_db()
		self.assertEqual(compromiso.estado, 'realizado')
		self.assertEqual(compromiso.historial.get().observacion, 'Entregado a la junta de vecinos')
		auditoria = Auditoria.objects.get(evento='cambio_estado', identificador_registro=compromiso.folio)
		self.assertEqual(json.loads(auditoria.valor_nuevo), {'estado': 'realizado', 'observacion': 'Entregado a la junta de vecinos'})

		respuesta = self.client.post(reverse('compromiso_estado', args=[compromiso.pk, 'pendiente']), follow=True)
		self.assertContains(respuesta, 'Transición no permitida')
		self.assertEqual(Compromiso.objects.get(pk=compromiso.pk).estado, 'realizado')

	def test_el_admin_no_ofrece_eliminar_un_incumplimiento(self):
		cargar_demo()
		self.assertTrue(self.client.login(username='admin.demo', password=CLAVE_DEMO))
		vencido = Compromiso.objects.filter(estado='pendiente').first()
		realizado = Compromiso.objects.filter(estado='realizado').first()
		self.assertTrue(vencido.vencido)
		self.assertEqual(self.client.get(reverse('admin:delegaciones_app_compromiso_delete', args=[vencido.pk])).status_code, 403)
		self.assertEqual(self.client.get(reverse('admin:delegaciones_app_compromiso_delete', args=[realizado.pk])).status_code, 200)


class FichaPersonalTests(BaseOperacion):
	"""CU-06, CU-06.2, CU-07.3, CU-17, CU-17.2 (RF-008, RF-028). Ficha personal, diferencia con lo esperado, meta cumplida y detalle de la fórmula."""

	def setUp(self):
		super().setUp()
		self.otro = crear_funcionario('otro-centro', 'funcionario', cargo=self.cargo, delegacion=self.centro)
		self.meta = Meta.objects.create(item=self.item, funcionario=self.funcionario.funcionario, valor_objetivo=2)
		self.meta_otro = Meta.objects.create(item=self.item, funcionario=self.otro.funcionario, valor_objetivo=5)
		self.actividad = self._actividad()
		Validacion(evidencia=self._evidencia(self.actividad), funcionario_verificador=self.verificador.funcionario).aprobar_evidencia()
		for meta in Meta.objects.all():
			Indicador.generar(meta)

	def _ficha(self, usuario=None, **parametros):
		self.client.force_login(usuario or self.funcionario)
		return self.client.get(reverse('ficha_personal'), parametros)

	def test_la_ficha_solo_muestra_las_metas_del_funcionario(self):
		respuesta = self._ficha()
		self.assertEqual(respuesta.status_code, 200)
		self.assertEqual([fila['meta'] for fila in respuesta.context['filas']], [self.meta])
		self.assertEqual(respuesta.context['periodo'], self.periodo)
		fila = respuesta.context['filas'][0]
		self.assertEqual((fila['avance'], fila['cumplimiento'], fila['estado']), (1, Decimal('50.00'), 'Rojo'))
		self.assertEqual(respuesta.context['cumplimiento_total'], Decimal('50.00'))

	def test_la_ficha_calcula_la_diferencia_con_lo_esperado(self):
		esperado = self.periodo.porcentaje_esperado()
		fila = self._ficha().context['filas'][0]
		self.assertEqual(fila['diferencia'], Decimal('50.00') - esperado)
		self.assertTrue(fila['desviacion'])

	def test_la_meta_alcanzada_se_destaca_como_cumplida(self):
		otra = self._actividad(solicitud_problema='Otra')
		Validacion(evidencia=self._evidencia(otra), funcionario_verificador=self.verificador.funcionario).aprobar_evidencia()
		Indicador.generar(self.meta)
		fila = self._ficha().context['filas'][0]
		self.assertTrue(fila['cumplida'])
		self.assertContains(self._ficha(), 'Cumplida')

	def test_el_detalle_explica_la_formula_y_enlaza_las_actividades_que_aportan(self):
		respuesta = self._ficha()
		fila = respuesta.context['filas'][0]
		self.assertIn('1 / 2 × 100 = 50 %', fila['formula'][0])
		self.assertEqual(list(fila['actividades']), [self.actividad])
		self.assertContains(respuesta, reverse('actividad_detalle', args=[self.actividad.codigo_verificador]))

	def test_el_detalle_informa_cuando_se_aplica_el_tope(self):
		self.meta.valor_objetivo = 1
		self.meta.save()
		for _ in range(2):
			extra = self._actividad(solicitud_problema='Extra')
			Validacion(evidencia=self._evidencia(extra), funcionario_verificador=self.verificador.funcionario).aprobar_evidencia()
		Indicador.generar(self.meta)
		fila = self._ficha().context['filas'][0]
		self.assertEqual(fila['cumplimiento'], Decimal('150.00'))
		self.assertIn('se aplica el tope', fila['formula'][1])

	def test_una_meta_sin_calculo_se_informa_sin_formula(self):
		Indicador.objects.filter(meta=self.meta).delete()
		fila = self._ficha().context['filas'][0]
		self.assertEqual((fila['estado'], fila['formula'], fila['diferencia']), ('Sin cálculo', [], None))

	def test_resumen_de_evidencias_y_compromisos(self):
		self._evidencia(self._actividad(solicitud_problema='Pendiente'))
		pendiente = self._compromiso(folio='FICHA-1')
		vencido = self._compromiso(folio='FICHA-2')
		vencido.fecha_comprometida = timezone.localdate() - timedelta(days=3)
		vencido.save()
		contexto = self._ficha().context
		evidencias = {fila['estado']: fila['total'] for fila in contexto['evidencias']}
		self.assertEqual((evidencias['aprobada'], evidencias['pendiente']), (1, 1))
		self.assertEqual((contexto['compromisos']['total'], contexto['compromisos']['vencidos'], contexto['compromisos']['vigentes']), (2, 1, 1))
		self.assertEqual(pendiente.estado, 'ingresado')

	def test_un_usuario_sin_funcionario_es_redirigido_con_un_mensaje(self):
		sin_ficha = User.objects.create_user('sin-ficha', password='x')
		self.client.force_login(sin_ficha)
		respuesta = self.client.get(reverse('ficha_personal'), follow=True)
		self.assertContains(respuesta, 'no tiene un funcionario asociado')

	def test_el_selector_ignora_un_periodo_ajeno_o_invalido(self):
		ajeno = Periodo.objects.create(nombre='Octubre 2026', fecha_inicio=date(2026, 10, 1), fecha_termino=date(2026, 10, 31), estado='abierto')
		for valor in (str(ajeno.pk), 'abc', '9999'):
			self.assertEqual(self._ficha(periodo=valor).context['periodo'], self.periodo, valor)

	def test_sin_metas_la_ficha_lo_indica(self):
		sin_metas = crear_funcionario('sin-metas', 'funcionario', cargo=self.cargo, delegacion=self.centro)
		respuesta = self._ficha(usuario=sin_metas)
		self.assertIsNone(respuesta.context['periodo'])
		self.assertContains(respuesta, 'Todavía no tienes metas asignadas')

	def test_exige_iniciar_sesion(self):
		self.client.logout()
		self.assertEqual(self.client.get(reverse('ficha_personal')).status_code, 302)

	def test_dashboard_y_resumen_muestran_la_diferencia_y_la_desviacion(self):
		self.client.force_login(self.coordinador)
		fila = {f['nombre']: f for f in self.client.get(reverse('dashboard')).context['delegaciones']}['Centro']
		self.assertEqual(fila['diferencia'], fila['cumplimiento'] - self.periodo.porcentaje_esperado())
		self.assertEqual(fila['desviacion'], fila['estado'] in ('Ámbar', 'Rojo'))
		self.assertContains(self.client.get(reverse('resumen')), 'Diferencia')
		self.assertContains(self.client.get(reverse('semaforo')), 'Diferencia con lo esperado')


class AnularAprobacionTests(BaseOperacion):
	"""CU-07.2 (RF-022, RF-023, RN-009, RN-013). Anular una aprobación exige motivo, recalcula hacia abajo y conserva el historial."""

	def setUp(self):
		super().setUp()
		self.meta = Meta.objects.create(item=self.item, funcionario=self.funcionario.funcionario, valor_objetivo=2)
		self.actividad = self._actividad()
		self.evidencia = self._evidencia(self.actividad)
		Validacion(evidencia=self.evidencia, funcionario_verificador=self.verificador.funcionario).aprobar_evidencia()
		Indicador.generar(self.meta)
		self.url = reverse('anular_actividad', args=[self.actividad.codigo_verificador])

	def _ultimo_avance(self):
		return Indicador.objects.filter(meta=self.meta).latest('fecha_calculo', 'pk').avance

	def test_anular_quita_la_actividad_del_avance_y_recalcula(self):
		self.assertEqual(self._ultimo_avance(), 1)
		self.actividad.anular_aprobacion('Evidencia ilegible', self.verificador.funcionario)
		self.actividad.refresh_from_db()
		self.evidencia.refresh_from_db()
		self.assertEqual((self.actividad.estado, self.evidencia.estado_revision), ('rechazada', 'rechazada'))
		self.assertEqual(self._ultimo_avance(), 0)
		self.assertEqual(self.meta.actividades_que_aportan().count(), 0)

	def test_la_validacion_original_se_conserva_como_historial(self):
		self.actividad.anular_aprobacion('Evidencia ilegible', self.verificador.funcionario)
		decisiones = list(Validacion.objects.filter(evidencia=self.evidencia).order_by('pk').values_list('decision', 'observacion'))
		self.assertEqual(decisiones, [('aprobada', None), ('rechazada', 'Evidencia ilegible')])

	def test_exige_un_motivo_y_una_actividad_aprobada(self):
		with self.assertRaises(ValidationError):
			self.actividad.anular_aprobacion('   ', self.verificador.funcionario)
		self.assertEqual(Actividad.objects.get(pk=self.actividad.pk).estado, 'aprobada')
		pendiente = self._actividad(solicitud_problema='Aun pendiente')
		with self.assertRaises(ValidationError):
			pendiente.anular_aprobacion('Motivo', self.verificador.funcionario)

	def test_un_periodo_cerrado_no_permite_anular(self):
		self.periodo.estado = 'cerrado'
		Periodo.objects.filter(pk=self.periodo.pk).update(estado='cerrado')
		with self.assertRaises(ValidationError):
			Actividad.objects.get(pk=self.actividad.pk).anular_aprobacion('Motivo', self.verificador.funcionario)
		self.assertEqual(Actividad.objects.get(pk=self.actividad.pk).estado, 'aprobada')

	def test_la_vista_anula_audita_y_muestra_el_resultado(self):
		self.client.force_login(self.verificador)
		respuesta = self.client.post(self.url, {'motivo': 'Evidencia ilegible'}, follow=True)
		self.assertContains(respuesta, 'ya no suma al avance')
		self.assertEqual(Actividad.objects.get(pk=self.actividad.pk).estado, 'rechazada')
		registro = Auditoria.objects.get(evento='anular_aprobacion')
		self.assertEqual(registro.identificador_registro, self.actividad.codigo_verificador)
		self.assertEqual(json.loads(registro.valor_nuevo)['motivo'], 'Evidencia ilegible')

	def test_la_vista_rechaza_un_motivo_vacio_sin_cambios(self):
		self.client.force_login(self.verificador)
		respuesta = self.client.post(self.url, {'motivo': ''}, follow=True)
		self.assertContains(respuesta, 'exige un motivo')
		self.assertEqual(Actividad.objects.get(pk=self.actividad.pk).estado, 'aprobada')
		self.assertFalse(Auditoria.objects.filter(evento='anular_aprobacion').exists())

	def test_un_funcionario_no_puede_anular_y_queda_registrado(self):
		self.client.force_login(self.funcionario)
		self.client.post(self.url, {'motivo': 'Quiero anularla'})
		self.assertEqual(Actividad.objects.get(pk=self.actividad.pk).estado, 'aprobada')
		self.assertTrue(Auditoria.objects.filter(evento='acceso_denegado').exists())

	def test_get_no_anula_y_el_panel_solo_se_ofrece_a_quien_corresponde(self):
		self.client.force_login(self.verificador)
		self.client.get(self.url)
		self.assertEqual(Actividad.objects.get(pk=self.actividad.pk).estado, 'aprobada')
		detalle = reverse('actividad_detalle', args=[self.actividad.codigo_verificador])
		self.assertContains(self.client.get(detalle), 'Anular aprobación')
		self.client.force_login(self.funcionario)
		self.assertNotContains(self.client.get(detalle), 'Anular aprobación')


class FiltrosYInformesTests(BaseOperacion):
	"""CU-20, CU-20.1, CU-20.2, CU-29 (RF-032, RF-033). Filtros de actividades y compromisos, informes en pantalla, para imprimir y en CSV."""

	def setUp(self):
		super().setUp()
		self.rural_user = crear_funcionario('rural-op', 'funcionario', cargo=self.cargo, delegacion=self.rural)
		self.pendiente = self._actividad(solicitud_problema='Consulta pendiente')
		self.aprobada = self._actividad(estado='aprobada', solicitud_problema='Operativo aprobado', fecha=timezone.make_aware(datetime(2026, 9, 20, 9, 0)))
		self.de_rural = self._actividad(autor=self.rural_user, delegacion=self.rural, solicitud_problema='Visita rural')

	def _filtrar(self, **datos):
		return set(filtrar_actividades(Actividad.objects.all(), datos).values_list('solicitud_problema', flat=True))

	def test_filtrar_actividades_por_cada_criterio(self):
		self.assertEqual(self._filtrar(estado='aprobada'), {'Operativo aprobado'})
		self.assertEqual(self._filtrar(delegacion=str(self.rural.pk)), {'Visita rural'})
		self.assertEqual(self._filtrar(q='operativo'), {'Operativo aprobado'})
		self.assertEqual(self._filtrar(periodo=str(self.periodo.pk)), {'Consulta pendiente', 'Operativo aprobado', 'Visita rural'})
		self.assertEqual(self._filtrar(desde='2026-09-15'), {'Operativo aprobado'})
		self.assertEqual(self._filtrar(hasta='2026-09-01'), {'Consulta pendiente', 'Visita rural'})
		self.assertEqual(self._filtrar(desde='2026-09-20', hasta='2026-09-20'), {'Operativo aprobado'})

	def test_los_valores_invalidos_se_ignoran_en_vez_de_fallar(self):
		todas = {'Consulta pendiente', 'Operativo aprobado', 'Visita rural'}
		self.assertEqual(self._filtrar(estado='inventado', delegacion='x', periodo='9;drop', desde='ayer', hasta='32-13-2026'), todas)

	def test_filtrar_compromisos_por_plazo_estado_y_periodo(self):
		hoy = timezone.localdate()
		vencido, por_vencer, lejano, hecho = (self._compromiso(folio=f'F-{n}') for n in range(4))
		for compromiso, dias, estado in ((vencido, -4, 'pendiente'), (por_vencer, 2, 'pendiente'), (lejano, 90, 'proceso'), (hecho, -4, 'realizado')):
			compromiso.fecha_comprometida, compromiso.estado = hoy + timedelta(days=dias), estado
			compromiso.save()
		folios = lambda **datos: set(filtrar_compromisos(Compromiso.objects.all(), datos).values_list('folio', flat=True))
		self.assertEqual(folios(plazo='vencidos'), {'F-0'})
		self.assertEqual(folios(plazo='por_vencer'), {'F-1'})
		self.assertEqual(folios(estado='proceso'), {'F-2'})
		self.assertEqual(folios(estado='realizado'), {'F-3'})
		self.assertEqual(folios(desde=str(hoy), hasta=str(hoy + timedelta(days=10))), {'F-1'})
		compromiso = Compromiso.objects.get(folio='F-1')
		compromiso.fecha_comprometida = date(2026, 9, 15)
		compromiso.save()
		self.assertIn('F-1', folios(periodo=str(self.periodo.pk)))
		self.assertNotIn('F-0', folios(periodo=str(self.periodo.pk)))

	def test_la_lista_de_actividades_aplica_los_filtros(self):
		self.client.force_login(self.coordinador)
		respuesta = self.client.get(reverse('actividades'), {'estado': 'aprobada'})
		self.assertEqual([a.solicitud_problema for a in respuesta.context['actividades']], ['Operativo aprobado'])
		self.assertTrue(respuesta.context['filtrado'])
		self.assertContains(self.client.get(reverse('actividades'), {'estado': 'correccion'}), 'Ninguna actividad coincide con los filtros')

	def test_la_agenda_filtra_por_plazo(self):
		vencido = self._compromiso(folio='AG-VENCIDO')
		vencido.fecha_comprometida = timezone.localdate() - timedelta(days=5)
		vencido.save()
		self._compromiso(folio='AG-VIGENTE')
		self.client.force_login(self.coordinador)
		respuesta = self.client.get(reverse('agenda'), {'plazo': 'vencidos'})
		self.assertEqual([c.folio for c in respuesta.context['compromisos']], ['AG-VENCIDO'])

	def test_el_detalle_vuelve_a_la_lista_con_los_filtros_usados(self):
		self.client.force_login(self.coordinador)
		self.client.get(reverse('actividades'), {'estado': 'aprobada', 'q': 'operativo'})
		detalle = self.client.get(reverse('actividad_detalle', args=[self.aprobada.codigo_verificador]))
		self.assertEqual(detalle.context['url_lista'], reverse('actividades') + '?estado=aprobada&q=operativo')
		self.assertContains(detalle, 'Volver a las actividades')
		self.client.get(reverse('actividades'))
		detalle = self.client.get(reverse('actividad_detalle', args=[self.aprobada.codigo_verificador]))
		self.assertEqual(detalle.context['url_lista'], reverse('actividades'))

	def test_eliminar_una_actividad_vuelve_a_la_lista_filtrada(self):
		self.client.force_login(self.coordinador)
		self.client.get(reverse('actividades'), {'estado': 'pendiente'})
		respuesta = self.client.post(reverse('actividad_eliminar', args=[self.pendiente.codigo_verificador]))
		self.assertRedirects(respuesta, reverse('actividades') + '?estado=pendiente')

	def test_cambiar_el_estado_de_un_compromiso_conserva_los_filtros_de_la_agenda(self):
		compromiso = self._compromiso(folio='AG-FILTRO')
		self.client.force_login(self.coordinador)
		self.client.get(reverse('agenda'), {'estado': 'ingresado'})
		respuesta = self.client.post(reverse('compromiso_estado', args=[compromiso.pk, 'proceso']))
		self.assertRedirects(respuesta, reverse('agenda') + '?estado=ingresado')
		self.client.get(reverse('agenda'))
		compromiso.refresh_from_db()
		respuesta = self.client.post(reverse('compromiso_estado', args=[compromiso.pk, 'realizado']))
		self.assertRedirects(respuesta, reverse('agenda'))

	def test_el_informe_de_actividades_respeta_el_ambito_del_usuario(self):
		self.client.force_login(self.rural_user)
		respuesta = self.client.get(reverse('informe'), {'tipo': 'actividades'})
		self.assertEqual([fila[0] for fila in respuesta.context['filas']], [self.de_rural.codigo_verificador])
		self.client.force_login(self.coordinador)
		respuesta = self.client.get(reverse('informe'), {'tipo': 'actividades', 'estado': 'aprobada'})
		self.assertEqual([fila[0] for fila in respuesta.context['filas']], [self.aprobada.codigo_verificador])
		self.assertContains(respuesta, 'Informe de actividades')

	def test_un_tipo_de_informe_desconocido_cae_en_actividades(self):
		self.client.force_login(self.coordinador)
		self.assertEqual(self.client.get(reverse('informe'), {'tipo': 'otro'}).context['tipo'], 'actividades')

	def test_el_informe_de_compromisos_marca_la_situacion_del_plazo(self):
		vencido = self._compromiso(folio='INF-VENCIDO')
		vencido.fecha_comprometida = timezone.localdate() - timedelta(days=2)
		vencido.save()
		self.client.force_login(self.coordinador)
		respuesta = self.client.get(reverse('informe'), {'tipo': 'compromisos', 'plazo': 'vencidos'})
		self.assertEqual(len(respuesta.context['filas']), 1)
		self.assertEqual(respuesta.context['filas'][0][0], 'INF-VENCIDO')
		self.assertEqual(respuesta.context['filas'][0][7], 'Vencido')

	def test_el_informe_de_cumplimiento_usa_los_indicadores(self):
		meta = Meta.objects.create(item=self.item, funcionario=self.funcionario.funcionario, valor_objetivo=2)
		Validacion(evidencia=self._evidencia(self.pendiente), funcionario_verificador=self.verificador.funcionario).aprobar_evidencia()
		Indicador.generar(meta)
		self.client.force_login(self.coordinador)
		respuesta = self.client.get(reverse('informe'), {'tipo': 'cumplimiento', 'periodo': self.periodo.pk})
		self.assertEqual(respuesta.context['columnas'][0], 'Delegación')
		self.assertEqual([(fila[0], fila[1]) for fila in respuesta.context['filas']], [('Centro', Decimal('50.00'))])
		filtrado = self.client.get(reverse('informe'), {'tipo': 'cumplimiento', 'periodo': self.periodo.pk, 'delegacion': self.rural.pk})
		self.assertEqual(filtrado.context['filas'], [])

	def test_el_csv_tiene_bom_separador_y_cabecera_y_queda_auditado(self):
		self.client.force_login(self.coordinador)
		respuesta = self.client.get(reverse('informe'), {'tipo': 'actividades', 'estado': 'aprobada', 'formato': 'csv'})
		self.assertEqual(respuesta['Content-Type'], 'text/csv; charset=utf-8')
		self.assertIn('informe_actividades_', respuesta['Content-Disposition'])
		contenido = respuesta.content.decode('utf-8')
		self.assertTrue(contenido.startswith('﻿Código;Fecha;Delegación'))
		lineas = contenido.strip().splitlines()
		self.assertEqual(len(lineas), 2)
		self.assertIn('Operativo aprobado', lineas[1])
		registro = Auditoria.objects.get(evento='exportar')
		self.assertEqual((registro.entidad, registro.identificador_registro), ('Informe', 'actividades'))
		self.assertEqual(json.loads(registro.valor_nuevo)['filas'], 1)

	def test_la_version_para_imprimir_ofrece_imprimir_y_oculta_los_filtros(self):
		self.client.force_login(self.coordinador)
		imprimir = self.client.get(reverse('informe'), {'tipo': 'actividades', 'formato': 'imprimir'})
		self.assertContains(imprimir, 'window.print()')
		self.assertNotContains(imprimir, 'Generar informe')
		normal = self.client.get(reverse('informe'), {'tipo': 'actividades'})
		self.assertContains(normal, 'Generar informe')
		self.assertContains(normal, 'formato=csv')

	def test_el_informe_exige_iniciar_sesion(self):
		self.assertEqual(self.client.get(reverse('informe')).status_code, 302)
		self.assertEqual(self.client.get(reverse('informe'), {'formato': 'csv'}).status_code, 302)
		self.assertFalse(Auditoria.objects.filter(evento='exportar').exists())
