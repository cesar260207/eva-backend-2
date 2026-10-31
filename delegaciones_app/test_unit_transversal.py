"""Pruebas unitarias transversales: permisos y ámbito, auditoría inmutable, registro de mantenedores e informes exportables."""
import csv
import io
from datetime import date

from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from django.utils import timezone

from . import crud
from .auditoria import cambios_de_formulario, plano
from .context_processors import permisos as procesador_permisos
from .forms import CatalogoForm, FuncionarioForm
from .informes import filas_de_actividades, filas_de_cumplimiento, respuesta_csv
from .models import Actividad, Auditoria, Catalogo, Cargo, Delegacion, Funcionario, Indicador, Meta, Periodo, Rol, UsuarioMaestro
from .permisos import (
    ADMINISTRADOR, MENSAJE_SIN_PERMISO, ROLES_DEL_SISTEMA, funcionario_de, puede_ver_todo, registrar_acceso_denegado,
    rol_requerido, roles_de, tiene_rol,
)
from .pruebas_base import EscenarioBase, crear_funcionario
from .views import MENSAJE_SOLO_AUTOR, _actividades_autorizadas, _bloqueo_actividad, _compromisos_autorizados


def peticion(usuario, metodo='get', ruta='/prueba/'):
    solicitud = getattr(RequestFactory(), metodo)(ruta)
    solicitud.user = usuario
    return solicitud


class RolesUnitTests(TestCase):
    """CU-26 Administración de delegaciones, usuarios y roles (RF-002): cómo se determinan los roles de un usuario."""

    def test_existen_los_seis_roles_del_sistema(self):
        """CU-26 Administración de usuarios y roles (RF-002). La migración crea los roles que consultan los permisos."""
        self.assertEqual(set(Rol.objects.values_list('nombre_rol', flat=True)), set(ROLES_DEL_SISTEMA))
        self.assertEqual(len(ROLES_DEL_SISTEMA), 6)

    def test_un_anonimo_no_tiene_roles(self):
        """CU-26.1 Denegar acceso por ámbito (RF-002). Sin sesión no hay permisos."""
        self.assertEqual(roles_de(AnonymousUser()), frozenset())
        self.assertFalse(tiene_rol(AnonymousUser(), ADMINISTRADOR))

    def test_los_roles_salen_del_funcionario(self):
        """CU-26 Administración de usuarios y roles (RF-002). Un usuario con dos roles tiene ambos."""
        usuario = crear_funcionario('doble-rol', 'funcionario', 'verificador')
        self.assertEqual(roles_de(usuario), {'funcionario', 'verificador'})
        self.assertTrue(tiene_rol(usuario, 'verificador', 'administrador'))
        self.assertFalse(tiene_rol(usuario, 'administrador', 'coordinador'))

    def test_un_funcionario_inactivo_no_aporta_roles(self):
        """CU-26 Administración de usuarios y roles (RF-002). Desactivar al funcionario quita sus permisos."""
        usuario = crear_funcionario('inactivo', 'administrador')
        Funcionario.objects.filter(usuario=usuario).update(estado=False)
        self.assertEqual(roles_de(usuario), frozenset())
        self.assertIsNone(funcionario_de(usuario))

    def test_una_cuenta_desactivada_no_tiene_roles(self):
        """CU-26 Administración de usuarios y roles (RF-002). is_active en falso corta el acceso."""
        usuario = crear_funcionario('cuenta-off', 'administrador')
        User.objects.filter(pk=usuario.pk).update(is_active=False)
        usuario.refresh_from_db()
        self.assertEqual(roles_de(usuario), frozenset())

    def test_el_superusuario_y_el_usuario_maestro_cuentan_como_administrador(self):
        """CU-26 Administración de usuarios y roles (RF-002). Dos formas de tener alcance global."""
        super_usuario = User.objects.create_superuser('root', password='x')
        self.assertIn(ADMINISTRADOR, roles_de(super_usuario))
        maestro = User.objects.create_user('maestro', password='x')
        registro = UsuarioMaestro.objects.create(usuario=maestro, identificador_maestro='M-1', nombre='Maestro', nivel_dominio='total')
        self.assertIn(ADMINISTRADOR, roles_de(maestro))
        registro.estado = False
        registro.save()
        self.assertNotIn(ADMINISTRADOR, roles_de(maestro))

    def test_solo_administracion_y_coordinacion_ven_todo(self):
        """CU-29.1 Restricción de búsqueda por ámbito (RF-032). El resto queda limitado a su ámbito."""
        for rol, esperado in (('administrador', True), ('coordinador', True), ('delegado', False), ('verificador', False), ('funcionario', False), ('consulta', False)):
            self.assertEqual(puede_ver_todo(crear_funcionario(f'ver-{rol}', rol)), esperado, rol)

    def test_funcionario_de_devuelve_su_funcionario(self):
        """CU-26 Administración de usuarios y roles (RF-002). Y None si no hay sesión o ficha."""
        usuario = crear_funcionario('con-ficha', 'funcionario')
        self.assertEqual(funcionario_de(usuario), usuario.funcionario)
        self.assertIsNone(funcionario_de(AnonymousUser()))
        self.assertIsNone(funcionario_de(User.objects.create_user('sin-ficha', password='x')))

    def test_el_menu_de_administracion_depende_del_rol(self):
        """CU-26 Administración de usuarios y roles (RF-002). El procesador de contexto lo calcula."""
        self.assertTrue(procesador_permisos(peticion(crear_funcionario('adm-menu', 'administrador')))['puede_administrar'])
        self.assertTrue(procesador_permisos(peticion(crear_funcionario('coord-menu', 'coordinador')))['puede_administrar'])
        self.assertFalse(procesador_permisos(peticion(crear_funcionario('func-menu', 'funcionario')))['puede_administrar'])


class DecoradorRolUnitTests(TestCase):
    """CU-26.1 Denegar acceso por ámbito (RF-002, RF-036): el decorador rol_requerido y el registro del intento."""

    def setUp(self):
        @rol_requerido(ADMINISTRADOR)
        def vista(request):
            from django.http import HttpResponse
            return HttpResponse('ok')

        self.vista = vista

    def test_sin_sesion_redirige_al_login(self):
        """CU-26.1 Denegar acceso por ámbito (RF-002). El anónimo va al login y no deja auditoría."""
        respuesta = self.vista(peticion(AnonymousUser()))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('/login/', respuesta['Location'])
        self.assertFalse(Auditoria.objects.exists())

    def test_con_el_rol_correcto_ejecuta_la_vista(self):
        """CU-26 Administración de usuarios y roles (RF-002). Quien tiene el rol entra."""
        respuesta = self.vista(peticion(crear_funcionario('adm-dec', 'administrador')))
        self.assertEqual((respuesta.status_code, respuesta.content), (200, b'ok'))

    def test_sin_el_rol_redirige_y_registra_el_intento(self):
        """CU-26.1 Denegar acceso por ámbito (RF-036). Un rol insuficiente queda en la auditoría."""
        respuesta = self.vista(peticion(crear_funcionario('func-dec', 'funcionario'), ruta='/administracion/'))
        self.assertEqual((respuesta.status_code, respuesta['Location']), (302, '/'))
        registro = Auditoria.objects.get(evento='acceso_denegado')
        self.assertEqual(registro.identificador_registro, '/administracion/')
        self.assertIn('rol insuficiente', registro.valor_nuevo)

    def test_registrar_acceso_denegado_ignora_al_anonimo(self):
        """CU-26.1 Denegar acceso por ámbito (RF-036). Sin identidad no hay a quién atribuir el intento."""
        registrar_acceso_denegado(peticion(AnonymousUser()))
        self.assertFalse(Auditoria.objects.exists())

    def test_registrar_acceso_denegado_guarda_entidad_e_identificador(self):
        """CU-26.1 Denegar acceso por ámbito (RF-036). El intento nombra lo que se quiso ver."""
        usuario = crear_funcionario('func-reg', 'funcionario')
        registrar_acceso_denegado(peticion(usuario), 'Actividad', 'EVD-1', 'fuera del ámbito')
        registro = Auditoria.objects.get()
        self.assertEqual((registro.entidad, registro.identificador_registro, registro.funcionario), ('Actividad', 'EVD-1', usuario.funcionario))
        self.assertIn('fuera del ámbito', registro.valor_nuevo)

    def test_el_mensaje_de_permiso_es_el_definido(self):
        """CU-26.1 Denegar acceso por ámbito (RF-002). El texto que ve el usuario."""
        self.assertEqual(MENSAJE_SIN_PERMISO, 'No tienes permiso para acceder a esta sección.')


class AlcanceUnitTests(EscenarioBase, TestCase):
    """CU-26.1 Denegar acceso por ámbito, CU-29.1 Restricción de búsqueda por ámbito y CU-20.2 Restringir por ámbito de permisos (RF-002, RF-032)."""

    def setUp(self):
        self.crear_escenario()
        self.del_centro = self.nueva_actividad(solicitud_problema='Centro')
        self.de_rural = self.nueva_actividad(delegacion=self.rural, solicitud_problema='Rural', funcionario_autor=crear_funcionario('rural-alc', 'funcionario', cargo=self.cargo, delegacion=self.rural).funcionario)
        self.compromiso_centro = self.nuevo_compromiso(folio='AL-C')
        self.compromiso_rural = self.nuevo_compromiso(folio='AL-R', delegacion=self.rural)

    def _codigos(self, usuario):
        return set(_actividades_autorizadas(usuario).values_list('solicitud_problema', flat=True))

    def _folios(self, usuario):
        return set(_compromisos_autorizados(usuario).values_list('folio', flat=True))

    def test_administracion_y_coordinacion_ven_todas_las_actividades(self):
        """CU-29.1 Restricción de búsqueda por ámbito (RF-032). Alcance global."""
        for rol in ('administrador', 'coordinador'):
            self.assertEqual(self._codigos(crear_funcionario(f'glob-{rol}', rol)), {'Centro', 'Rural'}, rol)

    def test_quien_tiene_delegacion_solo_ve_la_suya(self):
        """CU-20.2 Restringir por ámbito de permisos (RF-032). Un funcionario del Centro no ve lo de Rural."""
        self.assertEqual(self._codigos(self.usuario_autor), {'Centro'})
        self.assertEqual(self._folios(self.usuario_autor), {'AL-C'})

    def test_un_verificador_sin_delegacion_revisa_todas(self):
        """CU-11 Validación de actividades (RF-013). Puede revisar actividades de cualquier delegación."""
        self.assertEqual(self._codigos(self.usuario_verificador), {'Centro', 'Rural'})

    def test_un_funcionario_sin_delegacion_solo_ve_lo_que_registro(self):
        """CU-29.1 Restricción de búsqueda por ámbito (RF-032). Sin delegación, solo sus propias actividades."""
        suelto = crear_funcionario('suelto', 'funcionario', cargo=self.cargo)
        propia = self.nueva_actividad(funcionario_autor=suelto.funcionario, solicitud_problema='Propia')
        self.assertEqual(self._codigos(suelto), {'Propia'})
        self.assertEqual(list(_actividades_autorizadas(suelto)), [propia])

    def test_un_usuario_sin_funcionario_no_ve_nada(self):
        """CU-26.1 Denegar acceso por ámbito (RF-002). Una cuenta sin ficha no consulta registros."""
        sin_ficha = User.objects.create_user('sin-ficha-alc', password='x')
        self.assertEqual(self._codigos(sin_ficha), set())
        self.assertEqual(self._folios(sin_ficha), set())

    def test_los_compromisos_de_administracion_incluyen_todas_las_delegaciones(self):
        """CU-29.1 Restricción de búsqueda por ámbito (RF-032). Alcance global en la agenda."""
        self.assertEqual(self._folios(crear_funcionario('adm-comp', 'administrador')), {'AL-C', 'AL-R'})

    def test_bloqueo_de_una_actividad_aprobada(self):
        """CU-11.2 Bloquear aporte al avance (RF-014). Aprobada no se modifica ni siquiera por la coordinación."""
        aprobada = self.nueva_actividad(estado='aprobada', solicitud_problema='Aprobada')
        self.assertIn('ya suma al avance', _bloqueo_actividad(self.autor, aprobada, True))

    def test_bloqueo_de_una_actividad_de_periodo_cerrado(self):
        """CU-28.1 Restricción por período cerrado (RF-038). RN-013 alcanza a la edición de actividades."""
        self.periodo.cerrar_periodo()
        actividad = Actividad.objects.select_related('item__periodo').get(pk=self.del_centro.pk)
        self.assertIn('período de la actividad está cerrado', _bloqueo_actividad(self.autor, actividad, True))

    def test_solo_el_autor_o_la_coordinacion_modifican(self):
        """CU-26.1 Denegar acceso por ámbito (RF-002). Otro funcionario recibe el mensaje de solo autor."""
        otro = crear_funcionario('otro-autor', 'funcionario', cargo=self.cargo, delegacion=self.centro).funcionario
        self.assertEqual(_bloqueo_actividad(otro, self.del_centro, False), MENSAJE_SOLO_AUTOR)
        self.assertIsNone(_bloqueo_actividad(self.autor, self.del_centro, False))
        self.assertIsNone(_bloqueo_actividad(otro, self.del_centro, True))


class AuditoriaUnitTests(TestCase):
    """CU-30 Auditoría de cambios y CU-30.1 Bloqueo por alteración no autorizada (RF-036, RNF-008)."""

    def setUp(self):
        self.usuario = crear_funcionario('auditado', 'funcionario')

    def test_un_evento_queda_a_nombre_del_funcionario(self):
        """CU-30 Auditoría de cambios (RF-036). Quién, qué, sobre qué registro y cuándo."""
        antes = timezone.now()
        evento = Auditoria.registrar_evento(self.usuario, 'crear', 'Actividad', 'EVD-1', None, {'estado': 'pendiente'})
        self.assertEqual((evento.funcionario, evento.usuario_maestro, evento.evento, evento.entidad, evento.identificador_registro), (self.usuario.funcionario, None, 'crear', 'Actividad', 'EVD-1'))
        self.assertGreaterEqual(evento.fecha, antes)

    def test_el_usuario_maestro_tiene_prioridad_sobre_el_funcionario(self):
        """CU-30 Auditoría de cambios (RF-036). Un superusuario con registro maestro se atribuye al maestro."""
        maestro = UsuarioMaestro.objects.create(usuario=self.usuario, identificador_maestro='M-2', nombre='Maestro', nivel_dominio='total')
        evento = Auditoria.registrar_evento(self.usuario, 'editar', 'Cargo', 1)
        self.assertEqual((evento.usuario_maestro, evento.funcionario), (maestro, None))

    def test_los_valores_se_guardan_como_json_legible(self):
        """CU-30 Auditoría de cambios (RF-036). Antes y después, con tildes sin escapar."""
        evento = Auditoria.registrar_evento(self.usuario, 'editar', 'Cargo', 1, {'nombre': 'Técnico'}, {'nombre': 'Técnico senior'})
        self.assertEqual(evento.valor_anterior, '{"nombre": "Técnico"}')
        self.assertEqual(evento.valor_nuevo, '{"nombre": "Técnico senior"}')

    def test_un_texto_se_guarda_tal_cual_y_none_queda_vacio(self):
        """CU-30 Auditoría de cambios (RF-036). Sin doble codificación."""
        evento = Auditoria.registrar_evento(self.usuario, 'cambio_estado', 'Compromiso', 'F-1', 'pendiente', 'proceso')
        self.assertEqual((evento.valor_anterior, evento.valor_nuevo), ('pendiente', 'proceso'))
        self.assertIsNone(Auditoria.registrar_evento(self.usuario, 'crear', 'Cargo', 2).valor_anterior)

    def test_un_evento_registrado_no_se_puede_guardar_de_nuevo(self):
        """CU-30.1 Bloqueo por alteración no autorizada (RNF-008). La auditoría no se reescribe."""
        evento = Auditoria.registrar_evento(self.usuario, 'crear', 'Cargo', 3)
        evento.evento = 'otra cosa'
        with self.assertRaises(ValidationError):
            evento.save()
        self.assertEqual(Auditoria.objects.get(pk=evento.pk).evento, 'crear')

    def test_un_evento_no_se_elimina(self):
        """CU-30.1 Bloqueo por alteración no autorizada (RNF-008). Ni individualmente."""
        evento = Auditoria.registrar_evento(self.usuario, 'crear', 'Cargo', 4)
        with self.assertRaises(ValidationError):
            evento.delete()
        self.assertTrue(Auditoria.objects.filter(pk=evento.pk).exists())

    def test_tampoco_se_modifica_ni_elimina_en_bloque(self):
        """CU-30.1 Bloqueo por alteración no autorizada (RNF-008). Update y delete de un queryset se rechazan."""
        Auditoria.registrar_evento(self.usuario, 'crear', 'Cargo', 5)
        with self.assertRaises(ValidationError):
            Auditoria.objects.all().update(evento='borrado')
        with self.assertRaises(ValidationError):
            Auditoria.objects.all().delete()
        self.assertEqual(Auditoria.objects.get().evento, 'crear')

    def test_plano_convierte_valores_a_tipos_guardables(self):
        """CU-30 Auditoría de cambios (RF-036). Objetos y relaciones se guardan como texto."""
        cargo = Cargo.objects.create(nombre='Profesional')
        self.assertEqual((plano(None), plano(True), plano(3), plano('x')), (None, True, 3, 'x'))
        self.assertEqual(plano(cargo), 'Profesional')
        self.assertEqual(plano(Cargo.objects.filter(pk=cargo.pk)), ['Profesional'])

    def test_los_cambios_de_un_formulario_nuevo_no_tienen_valor_anterior(self):
        """CU-30 Auditoría de cambios (RF-036). Al crear solo hay valores nuevos."""
        formulario = CatalogoForm({'codigo': 'X-1', 'nombre': 'Algo', 'tipo': 'atencion', 'activo': 'on'})
        self.assertTrue(formulario.is_valid(), formulario.errors)
        anterior, nuevo = cambios_de_formulario(formulario)
        self.assertIsNone(anterior)
        self.assertEqual(nuevo['codigo'], 'X-1')

    def test_los_cambios_de_una_edicion_traen_antes_y_despues_solo_de_lo_que_cambio(self):
        """CU-30 Auditoría de cambios (RF-036). Los campos intactos no ensucian el registro."""
        elemento = Catalogo.objects.create(codigo='X-2', nombre='Original', tipo='atencion')
        formulario = CatalogoForm({'codigo': 'X-2', 'nombre': 'Cambiado', 'tipo': 'atencion', 'activo': 'on'}, instance=elemento)
        self.assertTrue(formulario.is_valid(), formulario.errors)
        anterior, nuevo = cambios_de_formulario(formulario)
        self.assertEqual((anterior, nuevo), ({'nombre': 'Original'}, {'nombre': 'Cambiado'}))

    def test_las_contrasenas_no_quedan_en_la_auditoria(self):
        """CU-30 Auditoría de cambios (RNF-004, RF-036). Los campos sensibles se excluyen."""
        cargo = Cargo.objects.create(nombre='Profesional')
        formulario = FuncionarioForm({
            'username': 'nuevo.u', 'nombre': 'Nuevo', 'cargo': cargo.pk, 'roles': [Rol.objects.get(nombre_rol='funcionario').pk],
            'estado': 'on', 'password': 'Clave-segura-2026', 'password_confirm': 'Clave-segura-2026',
        })
        self.assertTrue(formulario.is_valid(), formulario.errors)
        _, nuevo = cambios_de_formulario(formulario, ignorar=FuncionarioForm.campos_sin_auditar)
        self.assertNotIn('password', nuevo)
        self.assertNotIn('password_confirm', nuevo)
        self.assertNotIn('Clave-segura-2026', str(nuevo))


class MantenedoresUnitTests(TestCase):
    """CU-04, CU-26, CU-27 y CU-28 (RF-001 a RF-007): descripción de los ocho mantenedores y sus reglas de baja."""

    def test_son_exactamente_ocho_mantenedores(self):
        """CU-26 Administración de delegaciones, usuarios y roles (RF-001). Las ocho tablas maestras."""
        self.assertEqual(set(crud.MANTENEDORES), {'delegaciones', 'cargos', 'roles', 'funcionarios', 'catalogo', 'periodos', 'items', 'metas'})

    def test_cada_mantenedor_apunta_a_un_modelo_y_un_formulario_coherentes(self):
        """CU-26 Administración de delegaciones, usuarios y roles (RF-001). La consulta se arma sin error."""
        for slug, config in crud.MANTENEDORES.items():
            self.assertEqual(config.form._meta.model, config.modelo, slug)
            self.assertEqual(config.entidad, config.modelo.__name__, slug)
            list(config.consulta())
            self.assertTrue(config.columnas and config.busqueda, slug)

    def test_roles_y_funcionarios_son_solo_de_administracion(self):
        """CU-26.1 Denegar acceso por ámbito (RF-002). El perfil Coordinador no administra cuentas ni roles."""
        supervisor = crear_funcionario('coord-permisos', 'coordinador')
        administrador = crear_funcionario('adm-permisos', 'administrador')
        for slug in ('roles', 'funcionarios'):
            self.assertFalse(any(crud.MANTENEDORES[slug].permisos_de(supervisor).values()), slug)
            self.assertTrue(all(crud.MANTENEDORES[slug].permisos_de(administrador).values()), slug)
        for slug in ('delegaciones', 'cargos', 'catalogo', 'periodos', 'items', 'metas'):
            self.assertTrue(all(crud.MANTENEDORES[slug].permisos_de(supervisor).values()), slug)

    def test_los_roles_del_sistema_no_se_eliminan_pero_uno_propio_si(self):
        """CU-26 Administración de usuarios y roles (RF-002). Los permisos consultan esos nombres."""
        propio = Rol.objects.create(nombre_rol='auditor-externo')
        self.assertIsNone(crud._bloqueo_rol(propio, None))
        for nombre in ROLES_DEL_SISTEMA:
            self.assertIn('rol del sistema', crud._bloqueo_rol(Rol.objects.get(nombre_rol=nombre), None), nombre)

    def test_nadie_desactiva_su_propia_cuenta(self):
        """CU-26.1 Denegar acceso por ámbito (RF-002). Evita el bloqueo de quien administra."""
        usuario = crear_funcionario('yo-mismo', 'administrador')
        otro = crear_funcionario('otro-func', 'funcionario')
        self.assertEqual(crud._bloqueo_funcionario(usuario.funcionario, peticion(usuario)), 'No puedes desactivar tu propia cuenta.')
        self.assertIsNone(crud._bloqueo_funcionario(otro.funcionario, peticion(usuario)))
        Funcionario.objects.filter(pk=usuario.funcionario.pk).update(estado=False)
        usuario.funcionario.refresh_from_db()
        self.assertIsNone(crud._bloqueo_funcionario(usuario.funcionario, peticion(usuario)))

    def test_desactivar_un_funcionario_desactiva_tambien_su_cuenta(self):
        """CU-26 Administración de usuarios y roles (RF-002). Sin cuenta activa no inicia sesión."""
        usuario = crear_funcionario('baja-cuenta', 'funcionario')
        crud._cambiar_funcionario(usuario.funcionario, False)
        usuario.refresh_from_db()
        usuario.funcionario.refresh_from_db()
        self.assertEqual((usuario.is_active, usuario.funcionario.estado), (False, False))
        crud._cambiar_funcionario(usuario.funcionario, True)
        usuario.refresh_from_db()
        self.assertTrue(usuario.is_active)

    def test_cambiar_baja_de_delegacion_y_catalogo(self):
        """CU-27 Administración de catálogos (RF-004). Desactivar conserva la fila."""
        delegacion = Delegacion.objects.create(nombre='Temporal')
        elemento = Catalogo.objects.create(codigo='B-1', nombre='Baja', tipo='atencion')
        crud._cambiar_delegacion(delegacion, False)
        crud._cambiar_catalogo(elemento, False)
        delegacion.refresh_from_db()
        elemento.refresh_from_db()
        self.assertEqual((delegacion.estado, elemento.activo), (False, False))
        crud._cambiar_catalogo(elemento, True)
        elemento.refresh_from_db()
        self.assertTrue(elemento.activo)

    def test_las_acciones_de_un_periodo_dependen_de_su_estado(self):
        """CU-28 Administración de períodos (RF-005). Borrador se inicia, abierto se cierra, cerrado se reabre con motivo."""
        esperado = {'borrador': ('Iniciar', False), 'abierto': ('Cerrar', False), 'cerrado': ('Reabrir', True)}
        for estado, (etiqueta, motivo) in esperado.items():
            periodo = Periodo(pk=1, nombre=estado, estado=estado)
            acciones = crud._acciones_periodo(periodo)
            self.assertEqual([(a['etiqueta'], a['motivo']) for a in acciones], [(etiqueta, motivo)], estado)

    def test_texto_formatea_booleanos_fechas_y_vacios(self):
        """CU-26 Administración de delegaciones, usuarios y roles (RF-001). Presentación de las columnas del listado."""
        cargo = Cargo.objects.create(nombre='Profesional', vigencia=True)
        periodo = Periodo(nombre='P', fecha_inicio=date(2026, 9, 1), fecha_termino=date(2026, 9, 30))
        self.assertEqual(crud._texto(cargo, 'vigencia'), 'Sí')
        self.assertEqual(crud._texto(periodo, 'fecha_inicio'), '01-09-2026')
        self.assertEqual(crud._texto(Delegacion(nombre='X', ambito=None), 'ambito'), '-')
        self.assertEqual(crud._texto(Delegacion(nombre='X', ambito=''), 'ambito'), '-')
        self.assertEqual(crud._texto(Catalogo(tipo='atencion'), 'get_tipo_display'), 'Tipo de atención')


class InformesUnitTests(EscenarioBase, TestCase):
    """CU-20 Generación de informes, CU-20.1 Consolidar datos filtrados y CU-20.2 Restringir por ámbito (RF-033)."""

    def setUp(self):
        self.crear_escenario()

    def test_las_filas_de_actividades_traen_los_datos_del_informe(self):
        """CU-20.1 Consolidar datos filtrados (RF-033). Columnas y valores listos para exportar."""
        actividad = self.nueva_actividad(solicitud_problema='Consulta vecinal')
        columnas, filas = filas_de_actividades(Actividad.objects.select_related('delegacion', 'item', 'funcionario_autor'))
        fila = dict(zip(columnas, filas[0]))
        self.assertEqual(columnas[:3], ['Código', 'Fecha', 'Delegación'])
        self.assertEqual((fila['Código'], fila['Fecha'], fila['Delegación'], fila['Estado']), (actividad.codigo_verificador, '10-09-2026 10:00', 'Centro', 'Pendiente de revisión'))

    def test_las_filas_de_cumplimiento_incluyen_la_diferencia(self):
        """CU-20.1 Consolidar datos filtrados (RF-033). Una fila por delegación con su cumplimiento y estado."""
        resultados = [
            {'nombre': 'Centro', 'cumplimiento': 100, 'diferencia': 50, 'estado': 'Verde'},
            {'nombre': 'Rural', 'cumplimiento': 0, 'diferencia': None, 'estado': 'Sin cálculo'},
        ]
        columnas, filas = filas_de_cumplimiento(resultados, 50)
        self.assertEqual(columnas, ['Delegación', 'Cumplimiento (%)', 'Esperado al día (%)', 'Diferencia (puntos)', 'Estado'])
        self.assertEqual(filas, [['Centro', 100, 50, 50, 'Verde'], ['Rural', 0, 50, '', 'Sin cálculo']])

    def test_el_csv_tiene_bom_separador_punto_y_coma_y_nombre_de_archivo(self):
        """CU-20 Generación de informes (RF-033). Abre bien en Excel con tildes."""
        respuesta = respuesta_csv('informe_prueba.csv', ['Código', 'Descripción'], [['A-1', 'Poda; árboles'], ['A-2', 'Con "comillas"']])
        contenido = respuesta.content.decode('utf-8')
        self.assertTrue(contenido.startswith('﻿Código;Descripción'))
        self.assertEqual(respuesta['Content-Type'], 'text/csv; charset=utf-8')
        self.assertEqual(respuesta['Content-Disposition'], 'attachment; filename="informe_prueba.csv"')
        filas = list(csv.reader(io.StringIO(contenido.lstrip('﻿')), delimiter=';'))
        self.assertEqual(filas, [['Código', 'Descripción'], ['A-1', 'Poda; árboles'], ['A-2', 'Con "comillas"']])

    def test_un_informe_vacio_solo_trae_la_cabecera(self):
        """CU-20.1 Consolidar datos filtrados (RF-033). Sin registros no hay error."""
        columnas, filas = filas_de_actividades(Actividad.objects.none())
        respuesta = respuesta_csv('vacio.csv', columnas, filas)
        self.assertEqual(len(respuesta.content.decode('utf-8').strip().splitlines()), 1)


class AdvertenciaMetaUnitTests(EscenarioBase, TestCase):
    """CU-05 Definición de metas (RF-007): aviso previo a eliminar una meta."""

    def test_eliminar_una_meta_advierte_cuantos_indicadores_se_pierden(self):
        """CU-05 Definición de metas (RF-007). La advertencia cuenta los indicadores calculados."""
        self.crear_escenario()
        meta = Meta.objects.create(item=self.item, funcionario=self.autor, valor_objetivo=3)
        self.assertIsNone(crud._advertencia_meta(meta))
        Indicador.generar(meta)
        Indicador.generar(meta)
        self.assertIn('2 indicador(es)', crud._advertencia_meta(meta))
