"""Pruebas de seguridad de la Evaluación Sumativa 3: perfiles (grupos y permisos de Django), paneles por
perfil, recuperación de contraseña por correo y ausencia de Django Admin."""
import re
from datetime import timedelta
from unittest import mock

from django.contrib.auth.models import Group, User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Auditoria, Cargo, Delegacion, Funcionario, Rol
from .permisos import (
    PERFIL_ADMINISTRADOR, PERFIL_COORDINADOR, PERFIL_DELEGADO, PERFIL_FUNCIONARIO, PERFILES, delegacion_propia, perfil_de, puede_revisar,
    puede_ver_todo,
)
from .pruebas_base import CLAVE_PRUEBA, crear_funcionario

CLAVE_NUEVA = 'Nueva-clave-segura-2026'


def perfiles_de(usuario):
    return set(usuario.groups.values_list('name', flat=True))


class PerfilesTests(TestCase):
    """Perfiles de acceso Administrador, Coordinador, Delegado y Funcionario como grupos de Django."""

    def test_las_migraciones_crean_los_cuatro_perfiles_con_permisos_diferenciados(self):
        """CU-26 Crear perfiles de acceso (RF-002). Cada perfil tiene más permisos que el siguiente."""
        permisos = {nombre: set(Group.objects.get(name=nombre).permissions.values_list('codename', flat=True)) for nombre in PERFILES}
        self.assertLess(permisos[PERFIL_FUNCIONARIO], permisos[PERFIL_DELEGADO])
        self.assertLess(permisos[PERFIL_DELEGADO], permisos[PERFIL_COORDINADOR])
        self.assertLess(permisos[PERFIL_COORDINADOR], permisos[PERFIL_ADMINISTRADOR])
        self.assertTrue({'add_user', 'change_user', 'view_group', 'view_auditoria', 'change_funcionario', 'delete_rol'} <= permisos[PERFIL_ADMINISTRADOR])
        self.assertFalse({'add_user', 'view_auditoria', 'view_funcionario', 'view_rol'} & permisos[PERFIL_COORDINADOR])
        self.assertIn('add_validacion', permisos[PERFIL_DELEGADO])
        self.assertFalse({p for p in permisos[PERFIL_DELEGADO] if p.startswith('delete_') or p.endswith(('_catalogo', '_periodo', '_meta'))})
        self.assertFalse({p for p in permisos[PERFIL_FUNCIONARIO] if p.startswith('delete_') or p.endswith('_validacion')})

    def test_solo_coordinador_y_administrador_tienen_permiso_de_eliminar_actividades(self):
        """CU-26.1 Restringir operaciones críticas (RF-002). La migración 0019 da delete_actividad al Coordinador; Delegado y Funcionario no lo tienen."""
        tienen = {nombre: Group.objects.get(name=nombre).permissions.filter(codename='delete_actividad').exists() for nombre in PERFILES}
        self.assertEqual(tienen, {PERFIL_ADMINISTRADOR: True, PERFIL_COORDINADOR: True, PERFIL_DELEGADO: False, PERFIL_FUNCIONARIO: False})

    def test_el_perfil_se_deduce_de_los_roles(self):
        """CU-26 Asignar perfil según roles (RF-002). Administrador, coordinador, delegado o verificador, y los demás."""
        esperados = {
            ('administrador',): PERFIL_ADMINISTRADOR, ('coordinador',): PERFIL_COORDINADOR, ('delegado',): PERFIL_DELEGADO,
            ('funcionario', 'verificador'): PERFIL_DELEGADO, ('funcionario',): PERFIL_FUNCIONARIO, ('consulta',): PERFIL_FUNCIONARIO,
        }
        for numero, (roles, perfil) in enumerate(esperados.items()):
            self.assertEqual(perfiles_de(crear_funcionario(f'p-{numero}', *roles)), {perfil}, roles)

    def test_el_perfil_coordinador_aporta_el_alcance_de_su_rol(self):
        """CU-26 Asignar perfil según roles (RF-002). Un Coordinador sin rol coordinador ve todas las delegaciones."""
        usuario = crear_funcionario('solo-grupo', 'consulta')
        usuario.groups.set([Group.objects.get(name=PERFIL_COORDINADOR)])
        self.assertEqual(perfil_de(usuario), PERFIL_COORDINADOR)
        self.assertTrue(puede_ver_todo(usuario))
        self.assertTrue(User.objects.get(pk=usuario.pk).has_perm('delegaciones_app.add_catalogo'))

    def test_el_perfil_delegado_no_da_alcance_global(self):
        """CU-26 Asignar perfil según roles (RF-002). El Delegado revisa, pero su alcance sigue siendo su delegación."""
        centro = Delegacion.objects.create(nombre='Centro')
        usuario = crear_funcionario('delegado-perfil', 'delegado', delegacion=centro)
        self.assertEqual(perfil_de(usuario), PERFIL_DELEGADO)
        self.assertFalse(puede_ver_todo(usuario))
        self.assertEqual(delegacion_propia(usuario), centro)
        self.assertTrue(puede_revisar(User.objects.get(pk=usuario.pk)))

    def test_el_perfil_funcionario_no_revisa_aunque_tenga_rol_revisor(self):
        """CU-26.1 Restringir operaciones críticas (RF-002, RF-013). Sin el permiso del perfil, el rol no basta."""
        usuario = crear_funcionario('delegado-sin-perfil', 'delegado')
        usuario.groups.set([Group.objects.get(name=PERFIL_FUNCIONARIO)])
        self.assertFalse(puede_revisar(User.objects.get(pk=usuario.pk)))

    def test_un_funcionario_desactivado_pierde_los_permisos_de_su_perfil(self):
        """CU-26 Restringir acceso por perfil (RF-002). Aunque la cuenta siga activa, su ficha inactiva corta los permisos."""
        usuario = crear_funcionario('baja-perfil', 'administrador')
        Funcionario.objects.filter(usuario=usuario).update(estado=False)
        self.assertFalse(User.objects.get(pk=usuario.pk).has_perm('delegaciones_app.view_catalogo'))


class GestionDeUsuariosTests(TestCase):
    """Creación de usuarios y asignación de perfil desde el mantenedor de funcionarios."""

    def setUp(self):
        self.cargo = Cargo.objects.create(nombre='Profesional territorial')
        self.client.force_login(crear_funcionario('admin-usuarios', 'administrador'))

    def _datos(self, username, perfil='', rol='funcionario', **cambios):
        datos = {
            'username': username, 'nombre': username, 'email': f'{username}@example.com', 'cargo': self.cargo.pk,
            'perfil': Group.objects.get(name=perfil).pk if perfil else '', 'roles': [Rol.objects.get(nombre_rol=rol).pk],
            'estado': 'on', 'password': CLAVE_NUEVA, 'password_confirm': CLAVE_NUEVA,
        }
        datos.update(cambios)
        return datos

    def test_crear_usuario_con_perfil_elegido(self):
        """CU-26 Crear usuario y asignar grupo (RF-002). El perfil elegido queda como grupo de la cuenta."""
        respuesta = self.client.post(reverse('mantenedor_nuevo', args=['funcionarios']), self._datos('nuevo.coordinador', PERFIL_COORDINADOR, rol='consulta'))
        self.assertRedirects(respuesta, reverse('mantenedor_lista', args=['funcionarios']))
        usuario = User.objects.get(username='nuevo.coordinador')
        self.assertEqual(perfiles_de(usuario), {PERFIL_COORDINADOR})
        self.assertTrue(usuario.check_password(CLAVE_NUEVA))
        self.assertEqual(usuario.email, 'nuevo.coordinador@example.com')

    def test_sin_perfil_elegido_se_deduce_de_los_roles(self):
        """CU-26 Crear usuario y asignar grupo (RF-002). Sin perfil, un funcionario queda como Funcionario."""
        self.client.post(reverse('mantenedor_nuevo', args=['funcionarios']), self._datos('nuevo.funcionario'))
        self.assertEqual(perfiles_de(User.objects.get(username='nuevo.funcionario')), {PERFIL_FUNCIONARIO})

    def test_cambiar_el_perfil_reemplaza_el_grupo_anterior(self):
        """CU-26 Modificar asignación de grupo (RF-002). Un usuario queda en un solo perfil."""
        usuario = crear_funcionario('cambia.perfil', 'funcionario', cargo=self.cargo)
        datos = self._datos('cambia.perfil', PERFIL_COORDINADOR, password='', password_confirm='')
        self.client.post(reverse('mantenedor_editar', args=['funcionarios', usuario.funcionario.pk]), datos)
        self.assertEqual(perfiles_de(usuario), {PERFIL_COORDINADOR})
        cambio = Auditoria.objects.filter(evento='editar', entidad='Funcionario').get()
        self.assertIn('Coordinador', cambio.valor_nuevo)

    def test_un_perfil_menor_que_el_rol_se_rechaza(self):
        """CU-26.1 Validar perfil y roles (RF-002). El rol administrador exige el perfil Administrador."""
        respuesta = self.client.post(reverse('mantenedor_nuevo', args=['funcionarios']), self._datos('mal.perfil', PERFIL_FUNCIONARIO, rol='administrador'))
        self.assertFormError(respuesta.context['form'], 'perfil', 'El rol administrador requiere el perfil Administrador.')
        self.assertFalse(User.objects.filter(username='mal.perfil').exists())

    def test_el_rol_delegado_exige_un_perfil_que_revise(self):
        """CU-26.1 Validar perfil y roles (RF-002, RF-013). Un delegado con perfil Funcionario no podría revisar: se rechaza."""
        respuesta = self.client.post(reverse('mantenedor_nuevo', args=['funcionarios']), self._datos('mal.delegado', PERFIL_FUNCIONARIO, rol='delegado'))
        self.assertFormError(respuesta.context['form'], 'perfil', 'Los roles delegado y verificador revisan evidencias: requieren el perfil Delegado o uno superior.')
        self.client.post(reverse('mantenedor_nuevo', args=['funcionarios']), self._datos('bien.delegado', PERFIL_DELEGADO, rol='delegado'))
        self.assertEqual(perfiles_de(User.objects.get(username='bien.delegado')), {PERFIL_DELEGADO})


class AccesoPorPerfilTests(TestCase):
    """Restricciones funcionales y paneles distintos según el perfil autenticado."""

    @classmethod
    def setUpTestData(cls):
        cls.administrador = crear_funcionario('panel-admin', 'administrador')
        cls.coordinador = crear_funcionario('panel-super', 'coordinador')
        cls.funcionario = crear_funcionario('panel-adm', 'funcionario')
        cls.delegado = crear_funcionario('panel-del', 'delegado')

    def test_el_login_lleva_al_panel_de_cada_perfil(self):
        """HU-26 Panel según perfil (RF-002, RF-028). Cada perfil ve su propio panel."""
        paneles = {
            self.administrador: 'gestion_app/panel_administrador.html',
            self.coordinador: 'gestion_app/panel_coordinador.html',
            self.delegado: 'gestion_app/panel_delegado.html',
            self.funcionario: 'gestion_app/panel_funcionario.html',
        }
        for usuario, plantilla in paneles.items():
            self.client.logout()
            respuesta = self.client.post(reverse('login'), {'username': usuario.username, 'password': CLAVE_PRUEBA}, follow=True)
            self.assertRedirects(respuesta, reverse('panel'))
            self.assertTemplateUsed(respuesta, plantilla)

    def test_el_panel_administrador_muestra_gestion_de_usuarios_y_todos_los_mantenedores(self):
        """CU-26 Panel Administrador (RF-002, RF-029). Usuarios, perfiles y los ocho mantenedores."""
        self.client.force_login(self.administrador)
        respuesta = self.client.get(reverse('panel'))
        self.assertEqual(len(respuesta.context['mantenedores']), 8)
        self.assertContains(respuesta, reverse('mantenedor_nuevo', args=['funcionarios']))
        self.assertContains(respuesta, reverse('perfiles'))

    def test_el_panel_coordinador_muestra_solo_los_mantenedores_autorizados(self):
        """CU-26.1 Panel Coordinador (RF-002, RF-029). Seis mantenedores; sin usuarios ni auditoría."""
        self.client.force_login(self.coordinador)
        respuesta = self.client.get(reverse('panel'))
        self.assertEqual({m['slug'] for m in respuesta.context['mantenedores']}, {'delegaciones', 'cargos', 'catalogo', 'periodos', 'items', 'metas'})
        self.assertNotContains(respuesta, reverse('perfiles'))
        self.assertNotContains(respuesta, reverse('auditoria_consulta'))

    def test_el_funcionario_no_entra_a_operaciones_criticas(self):
        """CU-26.1 Restringir operaciones críticas (RF-002, RNF-004). Sin mantenedores, perfiles ni auditoría."""
        self.client.force_login(self.funcionario)
        for url in (reverse('mantenedores'), reverse('mantenedor_lista', args=['catalogo']), reverse('perfiles'), reverse('auditoria_consulta')):
            self.assertRedirects(self.client.get(url), reverse('inicio'), msg_prefix=url)
        self.assertNotContains(self.client.get(reverse('panel')), reverse('mantenedores'))

    def test_el_coordinador_no_gestiona_usuarios_ni_perfiles(self):
        """CU-26.1 Restringir acceso por perfil (RF-002). Permisos intermedios."""
        self.client.force_login(self.coordinador)
        self.assertEqual(self.client.get(reverse('mantenedor_lista', args=['catalogo'])).status_code, 200)
        for url in (reverse('mantenedor_lista', args=['funcionarios']), reverse('mantenedor_nuevo', args=['roles']), reverse('perfiles')):
            self.assertRedirects(self.client.get(url), reverse('inicio'), msg_prefix=url)

    def test_la_pagina_de_perfiles_lista_permisos_y_usuarios(self):
        """CU-26 Consultar perfiles y permisos (RF-002). Solo lectura para el administrador."""
        self.client.force_login(self.administrador)
        respuesta = self.client.get(reverse('perfiles'))
        self.assertEqual([perfil['nombre'] for perfil in respuesta.context['perfiles']], list(PERFILES))
        self.assertContains(respuesta, 'panel-super')

    def test_django_admin_no_esta_publicado(self):
        """CU-26 Administración sin Django Admin (RF-002). La ruta /admin/ no existe."""
        self.client.force_login(self.administrador)
        self.assertEqual(self.client.get('/admin/').status_code, 404)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', PASSWORD_RESET_TIMEOUT=3600)
class RecuperarContrasenaTests(TestCase):
    """Recuperación de contraseña por correo: solicitud, token, enlace, nueva contraseña y acceso."""

    def setUp(self):
        self.usuario = crear_funcionario('recupera', 'funcionario')
        self.usuario.email = 'recupera@example.com'
        self.usuario.save()

    def _solicitar(self, correo):
        return self.client.post(reverse('password_reset'), {'email': correo})

    def _enlace(self):
        return re.search(r'http://testserver(/recuperar/[^/\s]+/[^/\s]+/)', mail.outbox[-1].body).group(1)

    def test_flujo_completo_de_recuperacion(self):
        """HU-26 Recuperar contraseña por correo (RF-002, RNF-004). Solicitud, correo, enlace, cambio y acceso."""
        self.assertRedirects(self._solicitar('recupera@example.com'), reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['recupera@example.com'])
        self.assertIn('recupera', mail.outbox[0].body)

        respuesta = self.client.get(self._enlace())  # Django cambia el token de la URL por uno guardado en la sesión
        formulario_url = respuesta.url
        self.assertTrue(self.client.get(formulario_url).context['validlink'])
        respuesta = self.client.post(formulario_url, {'new_password1': CLAVE_NUEVA, 'new_password2': CLAVE_NUEVA})
        self.assertRedirects(respuesta, reverse('password_reset_complete'))

        self.assertFalse(self.client.login(username='recupera', password=CLAVE_PRUEBA))
        self.assertTrue(self.client.login(username='recupera', password=CLAVE_NUEVA))
        self.assertTrue(Auditoria.objects.filter(evento='restablecer_contrasena', identificador_registro='recupera').exists())

    def test_el_enlace_no_sirve_dos_veces(self):
        """HU-26 Validar token de recuperación (RF-002, RNF-004). Tras usarlo, el token deja de ser válido."""
        self._solicitar('recupera@example.com')
        enlace = self._enlace()
        formulario_url = self.client.get(enlace).url
        self.client.post(formulario_url, {'new_password1': CLAVE_NUEVA, 'new_password2': CLAVE_NUEVA})
        self.assertFalse(self.client.get(enlace, follow=True).context['validlink'])

    def test_un_token_alterado_se_rechaza(self):
        """HU-26 Validar token de recuperación (RF-002, RNF-004). Un token inventado no permite cambiar la contraseña."""
        self._solicitar('recupera@example.com')
        uid = self._enlace().split('/')[2]
        respuesta = self.client.get(reverse('password_reset_confirm', args=[uid, 'token-falso']))
        self.assertFalse(respuesta.context['validlink'])
        self.assertContains(respuesta, 'Enlace no válido')

    def test_un_correo_desconocido_no_envia_nada_ni_lo_revela(self):
        """HU-26 Recuperar contraseña por correo (RF-002, RNF-004). La respuesta es la misma exista o no la cuenta."""
        desconocido = self.client.post(reverse('password_reset'), {'email': 'nadie@example.com'}, follow=True)
        self.assertEqual(len(mail.outbox), 0)
        conocido = self.client.post(reverse('password_reset'), {'email': 'recupera@example.com'}, follow=True)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(desconocido.redirect_chain, conocido.redirect_chain)
        self.assertEqual(desconocido.content, conocido.content)
        self.assertContains(desconocido, 'Si el correo pertenece a una cuenta activa')

    def test_el_enlace_vence(self):
        """HU-26 Validar token de recuperación (RF-002, RNF-004). Pasado PASSWORD_RESET_TIMEOUT el enlace ya no sirve."""
        self._solicitar('recupera@example.com')
        enlace = self._enlace()
        despues = PasswordResetTokenGenerator()._now() + timedelta(seconds=3601)
        with mock.patch.object(PasswordResetTokenGenerator, '_now', return_value=despues):
            respuesta = self.client.get(enlace, follow=True)
        self.assertFalse(respuesta.context['validlink'])
        self.assertContains(respuesta, 'Enlace no válido')
        self.assertTrue(User.objects.get(pk=self.usuario.pk).check_password(CLAVE_PRUEBA))

    def test_el_correo_lleva_el_enlace_y_la_vigencia(self):
        """HU-26 Recuperar contraseña por correo (RF-002). El mensaje trae el enlace con el token y cuánto dura."""
        self._solicitar('recupera@example.com')
        correo = mail.outbox[0]
        self.assertIn('/recuperar/', correo.body)
        self.assertIn('60 minutos', correo.body)
        self.assertTrue(correo.alternatives, 'Debe incluir la versión HTML')

    def test_una_cuenta_inactiva_no_recibe_enlace(self):
        """HU-26 Recuperar contraseña por correo (RF-002, RNF-004). Desactivar la cuenta también corta la recuperación."""
        User.objects.filter(pk=self.usuario.pk).update(is_active=False)
        self._solicitar('recupera@example.com')
        self.assertEqual(len(mail.outbox), 0)

    def test_el_login_ofrece_recuperar_la_contrasena(self):
        """HU-26 Recuperar contraseña por correo (RF-002). El enlace está en la pantalla de ingreso."""
        self.assertContains(self.client.get(reverse('login')), reverse('password_reset'))
