"""Pruebas unitarias de autenticación (HU-26, RNF-004). Unidad probada: AuthenticationForm, la validación de credenciales de LoginView."""
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.test import TestCase

from .pruebas_base import CLAVE_PRUEBA


class ValidarCredencialesTests(TestCase):
    """HU-26 Acceso con identidad individual (RF-001, RF-002, RNF-004, RNF-005). Los 8 casos de login del plan de pruebas."""

    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user('usuario.prueba', password=CLAVE_PRUEBA)

    def _formulario(self, username, password):
        return AuthenticationForm(request=None, data={'username': username, 'password': password})

    def test_login_con_usuario_y_contrasena_validos(self):
        """CP-LOGIN-001 HU-26 Login con usuario y contraseña válidos (RF-002, RNF-004)."""
        formulario = self._formulario('usuario.prueba', CLAVE_PRUEBA)
        self.assertTrue(formulario.is_valid())
        self.assertEqual(formulario.get_user(), self.usuario)

    def test_login_con_contrasena_incorrecta(self):
        """CP-LOGIN-002 HU-26 Login con contraseña incorrecta (RF-002, RNF-004)."""
        formulario = self._formulario('usuario.prueba', 'otra-clave')
        self.assertFalse(formulario.is_valid())
        self.assertIn('__all__', formulario.errors)
        self.assertIsNone(formulario.get_user())

    def test_login_con_usuario_inexistente(self):
        """CP-LOGIN-003 HU-26 Login con usuario inexistente (RF-002, RNF-004)."""
        formulario = self._formulario('no.existe', CLAVE_PRUEBA)
        self.assertFalse(formulario.is_valid())
        self.assertIn('__all__', formulario.errors)
        self.assertIsNone(formulario.get_user())

    def test_login_con_usuario_vacio(self):
        """CP-LOGIN-004 HU-26 Login con usuario vacío (RF-002, RNF-004)."""
        formulario = self._formulario('', CLAVE_PRUEBA)
        self.assertFalse(formulario.is_valid())
        self.assertEqual(set(formulario.errors), {'username'})
        self.assertEqual(formulario.errors['username'][0], 'Este campo es obligatorio.')

    def test_login_con_contrasena_vacia(self):
        """CP-LOGIN-005 HU-26 Login con contraseña vacía (RF-002, RNF-004)."""
        formulario = self._formulario('usuario.prueba', '')
        self.assertFalse(formulario.is_valid())
        self.assertEqual(set(formulario.errors), {'password'})

    def test_login_con_usuario_y_contrasena_vacios(self):
        """CP-LOGIN-006 HU-26 Login con ambos campos vacíos (RF-002, RNF-004)."""
        formulario = self._formulario('', '')
        self.assertFalse(formulario.is_valid())
        self.assertEqual(set(formulario.errors), {'username', 'password'})

    def test_login_con_usuario_inactivo(self):
        """CP-LOGIN-007 HU-26 Login con usuario inactivo (RF-002, RNF-004)."""
        User.objects.filter(pk=self.usuario.pk).update(is_active=False)
        formulario = self._formulario('usuario.prueba', CLAVE_PRUEBA)
        self.assertFalse(formulario.is_valid())
        self.assertIsNone(authenticate(username='usuario.prueba', password=CLAVE_PRUEBA))

    def test_login_con_formato_invalido(self):
        """CP-LOGIN-008 HU-26 Login con formato inválido: solo espacios, texto de inyección y usuario de 151 caracteres (RF-002, RNF-004)."""
        formatos = ["' OR '1'='1", 'u' * 151, '<script>alert(1)</script>']
        for usuario in formatos:
            formulario = self._formulario(usuario, CLAVE_PRUEBA)
            self.assertFalse(formulario.is_valid(), usuario)
            self.assertIsNone(formulario.get_user(), usuario)
        solo_espacios = self._formulario('   ', CLAVE_PRUEBA)
        self.assertFalse(solo_espacios.is_valid())
        self.assertIn('username', solo_espacios.errors)
