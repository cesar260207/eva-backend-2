"""Pruebas de la interfaz (rediseño terracota): limpieza de mensajes sobre permisos, formularios, semáforo,
ingreso y recursos locales. Solo revisan lo que muestran las plantillas; la protección real sigue en las vistas."""
import re
from datetime import date

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.template import Context, Template
from django.test import TestCase
from django.urls import reverse

from .models import Delegacion
from .pruebas_base import CLAVE_PRUEBA, EscenarioBase, crear_funcionario, fijar_hoy
from .templatetags.sgr_interfaz import campo_sgr, campos, campos_restantes


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


class FormularioDeActividadTests(EscenarioBase, TestCase):
    """CU-01 Registrar actividad, CU-01.1 y CU-01.2 Validar datos (RF-009, RNF-011, RNF-012)."""

    def setUp(self):
        self.crear_escenario()
        fijar_hoy(self, date(2026, 9, 11))

    def _datos(self, **cambios):
        datos = {
            'delegacion': self.centro.pk, 'item': self.item.pk, 'catalogo': self.catalogo.pk, 'fecha': '2026-09-10T10:00',
            'solicitud_problema': 'Consulta vecinal', 'accion': 'Orientación', 'contacto_nombre': 'Vecina de prueba',
            'contacto_telefono': '912345678', 'tipo_accion': 'ejecucion',
        }
        datos.update(cambios)
        return datos

    def test_el_telefono_invalido_se_marca_junto_al_campo(self):
        """CU-01.2 Validar datos de la actividad (RF-009, RNF-012). El error queda junto al campo, con is-invalid y aria-invalid."""
        self.client.force_login(self.usuario_autor)
        respuesta = self.client.post(reverse('actividad_nueva'), self._datos(contacto_telefono='abc'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('contacto_telefono', respuesta.context['form'].errors)
        html = respuesta.content.decode('utf-8')
        campo = re.search(r'<input[^>]*name="contacto_telefono"[^>]*>', html).group(0)
        self.assertIn('is-invalid', campo)
        self.assertIn('aria-invalid="true"', campo)
        self.assertIn('id_contacto_telefono_error', campo)
        self.assertContains(respuesta, 'id="id_contacto_telefono_error"')
        self.assertContains(respuesta, 'Revisa los campos marcados.')
        self.assertContains(respuesta, 'Guardar actividad')

    def test_el_formulario_agrupa_los_campos_sin_perder_ninguno(self):
        """CU-01 Registrar actividad (RF-009, RNF-011). Bloques con título y todos los campos del formulario."""
        self.client.force_login(self.usuario_autor)
        respuesta = self.client.get(reverse('actividad_nueva'))
        for bloque in ('Dónde y cuándo', 'Qué se hizo', 'Contacto', 'Vinculación', 'Reglas del registro'):
            self.assertContains(respuesta, bloque)
        for nombre in respuesta.context['form'].fields:
            self.assertContains(respuesta, f'name="{nombre}"', count=1, msg_prefix=nombre)
        self.assertNotContains(respuesta, 'Otros datos')


class IngresoTests(TestCase):
    """CU-32 Iniciar sesión y CU-39 Credenciales incorrectas (RF-002, RNF-011)."""

    def test_el_ingreso_muestra_el_error_general_de_credenciales(self):
        """CU-39 Credenciales incorrectas (RF-002). El aviso general aparece arriba de los campos."""
        crear_funcionario('ingreso.prueba', 'funcionario')
        respuesta = self.client.post(reverse('login'), {'username': 'ingreso.prueba', 'password': 'otra-clave'})
        self.assertEqual(respuesta.status_code, 200)
        error = respuesta.context['form'].non_field_errors()[0]
        self.assertContains(respuesta, error)
        self.assertContains(respuesta, 'alert alert-danger')

    def test_el_ingreso_conserva_textos_y_nombres_de_campos(self):
        """CU-32 Iniciar sesión (RF-002). Mismos textos, mismos name e id, y botón para mostrar la contraseña."""
        respuesta = self.client.get(reverse('login'))
        for texto in ('Ingresar al SGR', '>Ingresar</button>', '¿Olvidaste tu contraseña?', 'name="username"', 'id="id_username"', 'name="password"', 'id="id_password"', 'data-ver-clave="id_password"'):
            self.assertContains(respuesta, texto)

    def test_el_ingreso_correcto_sigue_llegando_al_panel(self):
        """CU-32 Iniciar sesión (RF-002). Con la nueva pantalla se llega igual al panel."""
        crear_funcionario('ingreso.ok', 'funcionario')
        respuesta = self.client.post(reverse('login'), {'username': 'ingreso.ok', 'password': CLAVE_PRUEBA})
        self.assertRedirects(respuesta, reverse('panel'))


class SemaforoTests(TestCase):
    """CU-16 Semáforo de avance (RF-029, RNF-012). Color propio, ícono y el mismo texto del estado."""

    def _insignia(self, estado, clase):
        return Template("{% include 'includes/_semaforo_insignia.html' %}").render(Context({'estado': estado, 'estado_class': clase}))

    def test_la_insignia_muestra_el_texto_del_estado_con_su_icono(self):
        """CU-16 Semáforo (RNF-012). El texto se lee igual que antes; el color no es la única señal."""
        casos = {'Verde': ('success', 'i-visto'), 'Ámbar': ('warning', 'i-advertencia'), 'Rojo': ('danger', 'i-equis'), 'Sin cálculo': ('secondary', 'i-neutro')}
        for estado, (clase, icono) in casos.items():
            html = self._insignia(estado, clase)
            self.assertIn(estado, html)
            self.assertIn(f'semaforo-{clase}', html)
            self.assertIn(f'#{icono}', html)
            self.assertNotIn('bg-', html)


class RecursosLocalesTests(TestCase):
    """RNF-012 y RNF-013 (Ley 19.628). Las páginas cargan solo recursos propios: ninguna IP de funcionario llega a terceros."""

    EXTERNO = re.compile(r'<(?:link|script)\b[^>]*(?:href|src)="(?:https?:)?//', re.IGNORECASE)

    def test_base_carga_sgr_js_y_ningun_recurso_externo(self):
        """RNF-013 Compatibilidad (RF-002). sgr.js se carga con defer y no hay enlaces ni scripts a otros dominios."""
        usuario = crear_funcionario('recursos.ui', 'funcionario')
        for url in (reverse('inicio'), reverse('login'), reverse('institucional')):
            respuesta = self.client.get(url)
            self.assertContains(respuesta, 'js/sgr.js" defer', msg_prefix=url)
            self.assertIsNone(self.EXTERNO.search(respuesta.content.decode('utf-8')), url)
        self.client.force_login(usuario)
        for url in (reverse('panel'), reverse('actividades'), reverse('mantenedores')):
            respuesta = self.client.get(url)
            self.assertIsNone(self.EXTERNO.search(respuesta.content.decode('utf-8')), url)
            self.assertNotContains(respuesta, 'onclick=', msg_prefix=url)


class FiltrosDeInterfazTests(TestCase):
    """RNF-011 y RNF-012. Los filtros de presentación solo agregan clases y ordenan campos."""

    class Formulario(forms.Form):
        nombre = forms.CharField(label='Nombre')
        telefono = forms.CharField(label='Teléfono', help_text='Solo dígitos')
        activo = forms.BooleanField(label='Activo', required=False)
        oculto = forms.CharField(widget=forms.HiddenInput, required=False)

    def test_campo_sgr_agrega_la_clase_de_bootstrap_y_is_invalid(self):
        """RNF-012 Accesibilidad. Con error, el campo lleva is-invalid y aria-invalid; sin error, solo su clase."""
        form = self.Formulario(data={'nombre': '', 'telefono': '123'})
        self.assertFalse(form.is_valid())
        html = campo_sgr(form['nombre'], 'form-control-lg')
        self.assertIn('class="form-control form-control-lg is-invalid"', html)
        self.assertIn('aria-invalid="true"', html)
        self.assertNotIn('is-invalid', campo_sgr(form['telefono']))
        self.assertIn('form-check-input', campo_sgr(form['activo']))
        self.assertNotIn('class=', campo_sgr(form['oculto']))

    def test_campo_sgr_respeta_la_clase_que_ya_trae_el_widget(self):
        """RNF-011 Usabilidad. Un formulario con FormularioBootstrap no repite la clase."""
        form = AuthenticationForm()
        form.fields['username'].widget.attrs['class'] = 'form-control'
        self.assertEqual(campo_sgr(form['username']).count('form-control'), 1)

    def test_campos_y_campos_restantes_no_pierden_ninguno(self):
        """RNF-011 Usabilidad. Agrupar a mano no deja campos fuera ni repite los ocultos."""
        form = self.Formulario()
        self.assertEqual([c.name for c in campos(form, 'telefono nombre inexistente oculto')], ['telefono', 'nombre'])
        self.assertEqual([c.name for c in campos_restantes(form, 'telefono')], ['nombre', 'activo'])
