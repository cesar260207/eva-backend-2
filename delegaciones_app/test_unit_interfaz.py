"""Pruebas de la interfaz (rediseño terracota): limpieza de mensajes sobre permisos, formularios, semáforo,
ingreso y recursos locales. Solo revisan lo que muestran las plantillas; la protección real sigue en las vistas."""
from django.test import TestCase
from django.urls import reverse

from .pruebas_base import crear_funcionario
from .models import Delegacion


MENSAJES_DE_PERMISOS = ('Restringido para tu perfil', 'Permisos mínimos', 'Permisos intermedios', 'Acceso total')


class LimpiezaDePanelesTests(TestCase):
    """CU-26 y CU-26.1 Paneles por perfil (RF-002, RNF-011). Cada perfil ve lo que puede hacer, sin listas de lo que no."""

    def setUp(self):
        self.centro = Delegacion.objects.create(nombre='Centro')
        self.usuarios = {
            'administrador': crear_funcionario('admin.ui', 'administrador'),
            'coordinador': crear_funcionario('coord.ui', 'coordinador'),
            'delegado': crear_funcionario('delegado.ui', 'delegado', delegacion=self.centro),
            'funcionario': crear_funcionario('profesional.ui', 'funcionario', delegacion=self.centro),
        }

    def test_ningun_panel_describe_permisos_ni_restricciones(self):
        """CU-26 Panel por perfil (RF-002, RNF-011). Sin descripciones de permisos ni bloques de restricciones."""
        for perfil, usuario in self.usuarios.items():
            self.client.force_login(usuario)
            respuesta = self.client.get(reverse('panel'))
            self.assertEqual(respuesta.status_code, 200, perfil)
            for mensaje in MENSAJES_DE_PERMISOS:
                self.assertNotContains(respuesta, mensaje, msg_prefix=perfil)
            self.assertNotContains(respuesta, 'Roles:', msg_prefix=perfil)

    def test_el_panel_del_profesional_mantiene_registrar_y_administracion(self):
        """CU-01 Registrar actividad (RF-009) y CU-26.1 (RF-002). El acceso principal sigue en el panel y el menú lleva a Administración."""
        self.client.force_login(self.usuarios['funcionario'])
        respuesta = self.client.get(reverse('panel'))
        self.assertContains(respuesta, 'Registrar actividad con evidencia')
        self.assertContains(respuesta, reverse('actividad_nueva'))
        self.assertContains(respuesta, reverse('mantenedores'))

    def test_el_panel_del_coordinador_no_reserva_ni_detalla_acciones(self):
        """CU-26.1 Panel Coordinador (RF-002). Sin la nota de lo reservado ni los rótulos «crear · editar · eliminar»."""
        self.client.force_login(self.usuarios['coordinador'])
        respuesta = self.client.get(reverse('panel'))
        self.assertNotContains(respuesta, 'quedan reservados al perfil Administrador')
        self.assertNotContains(respuesta, ' · editar')
        self.assertContains(respuesta, reverse('mantenedor_lista', args=['catalogo']))

    def test_la_lista_de_solo_lectura_no_anuncia_el_perfil(self):
        """CU-26.1 Restringir acceso por perfil (RF-002). Sin permiso de agregar no hay botón ni insignia de perfil."""
        self.client.force_login(self.usuarios['funcionario'])
        respuesta = self.client.get(reverse('mantenedor_lista', args=['organizaciones']))
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotContains(respuesta, 'Solo lectura para tu perfil')
        self.assertNotContains(respuesta, reverse('mantenedor_nuevo', args=['organizaciones']))


class IndiceDeMantenedoresTests(TestCase):
    """CU-26.1 Restringir acceso por perfil (RF-002, RNF-011). El índice muestra solo las secciones que cada perfil usa."""

    def test_el_profesional_ve_solo_organizaciones_comunitarias(self):
        """CU-26.1 (RF-002). El Profesional ve una sola tarjeta, la de organizaciones, sin tarjetas bloqueadas."""
        self.client.force_login(crear_funcionario('profesional.indice', 'funcionario'))
        respuesta = self.client.get(reverse('mantenedores'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Abrir sección', count=1)
        self.assertContains(respuesta, reverse('mantenedor_lista', args=['organizaciones']))
        self.assertNotContains(respuesta, 'No disponible para tu perfil')
        self.assertNotContains(respuesta, 'Sección 01')
        for slug in ('delegaciones', 'cargos', 'roles', 'funcionarios', 'catalogo', 'periodos', 'parametros', 'items', 'metas', 'ajustes', 'ausencias'):
            self.assertNotContains(respuesta, reverse('mantenedor_lista', args=[slug]), msg_prefix=slug)
            self.assertNotContains(respuesta, reverse('mantenedor_nuevo', args=[slug]), msg_prefix=slug)
