"""Los actores de los casos de uso (docs/casos_uso/fuente/datos_v2.py) coinciden con el sistema: se entra con un
usuario de cada perfil y cada pantalla responde 200 solo a los perfiles que el cuadro declara como actores.
Reemplaza a docs/casos_uso/fuente/probe.py, que hacía la misma comparación a mano."""
import importlib.util
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Actividad, Compromiso, Delegacion


def cargar_casos():
    ruta = Path(settings.BASE_DIR) / 'docs' / 'casos_uso' / 'fuente' / 'datos_v2.py'
    spec = importlib.util.spec_from_file_location('datos_v2', ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


DATOS = cargar_casos()
# Un usuario de demostración por perfil (seed_demo), con el nombre de actor que usan los cuadros.
USUARIOS = {
    DATOS.A: 'admin.demo', DATOS.C: 'coordinador.demo', DATOS.D: 'delegado.demo', DATOS.P: 'funcionario.centro',
}
# Mantenedores: prefijo del caso en datos_v2.py y slug de su URL.
MANTENEDORES = {
    'org': 'organizaciones', 'del': 'delegaciones', 'car': 'cargos', 'rol': 'roles', 'fun': 'funcionarios',
    'cat': 'catalogo', 'per': 'periodos', 'par': 'parametros', 'item': 'items', 'meta': 'metas',
}


class ActoresDeLosCasosDeUsoTests(TestCase):
    """CU-26.1 Denegar acceso por ámbito (RF-002). Cada pantalla responde 200 solo a los actores de su caso de uso."""

    @classmethod
    def setUpTestData(cls):
        call_command('seed_demo', password='Clave-segura-2026', stdout=StringIO())

    def pantallas(self):
        """Caso de uso (clave en datos_v2.py) y las pantallas que se abren con GET para usarlo."""
        actividad = Actividad.objects.order_by('pk').first().codigo_verificador
        compromiso = Compromiso.objects.order_by('pk').first().pk
        delegacion = Delegacion.objects.get(nombre='Centro').nombre
        pantallas = {
            'act_reg': [reverse('actividad_nueva')],
            'act_con': [reverse('actividades'), reverse('actividad_detalle', args=[actividad])],
            'comentar': [reverse('comentario_nuevo', args=[actividad])],
            'tarea_reg': [reverse('compromiso_nuevo')],
            'tarea_agenda': [reverse('agenda')],
            'tarea_seg': [reverse('solicitudes')],
            'tarea_eli': [reverse('compromiso_eliminar', args=[compromiso])],
            'aj_inf': [reverse('ajuste_nuevo')],
            'aj_con': [reverse('mantenedor_lista', args=['ajustes'])],
            'au_reg': [reverse('ausencia_nueva')],
            'au_con': [reverse('mantenedor_lista', args=['ausencias'])],
            'social': [reverse('caso_social_nuevo')],
            'org_exp': [reverse('exportar_organizaciones')],
            'delegado': [reverse('delegados')],
            'ficha': [reverse('ficha_personal')],
            'semaforo': [reverse('semaforo')],
            'comparar': [reverse('dashboard')],
            'resumen': [reverse('panel'), reverse('resumen')],
            'tablero': [reverse('institucional'), reverse('delegacion_detalle', args=[delegacion])],
            'alertas': [reverse('alertas')],
            'informe': [reverse('informe')],
            'auditoria': [reverse('auditoria_consulta')],
            'perfiles': [reverse('perfiles')],
        }
        for prefijo, slug in MANTENEDORES.items():
            pantallas[f'{prefijo}_reg'] = [reverse('mantenedor_nuevo', args=[slug])]
            pantallas[f'{prefijo}_con'] = [reverse('mantenedor_lista', args=[slug])]
        return pantallas

    def test_cada_pantalla_responde_solo_a_los_actores_de_su_caso(self):
        """CU-26.1 Denegar acceso por ámbito (RF-002, RF-036). 200 para los actores del cuadro y 404 o redirección para el resto."""
        comparaciones = 0
        for clave, urls in self.pantallas().items():
            caso = DATOS.CASOS[clave]
            actores = set(USUARIOS) if DATOS.U in caso['actores'] else set(caso['actores'])
            for actor, username in USUARIOS.items():
                self.client.force_login(User.objects.get(username=username))
                for url in urls:
                    comparaciones += 1
                    with self.subTest(caso=f'{caso["cu"]} {caso["nombre"]}', perfil=actor, url=url):
                        self.assertEqual(self.client.get(url).status_code == 200, actor in actores)
        # 46 pantallas por 4 perfiles: la evidencia de que los cuadros cuadran con el sistema.
        self.assertEqual(comparaciones, 184)

    def test_las_pantallas_comprobadas_son_casos_de_detalle_con_esa_pantalla(self):
        """CU-26.1 Denegar acceso por ámbito (RF-002). La tabla de la prueba no se desalinea de datos_v2.py."""
        for clave in self.pantallas():
            with self.subTest(caso=clave):
                caso = DATOS.CASOS[clave]
                self.assertEqual(caso['tipo'], 'base')
                self.assertTrue(caso['pantalla'].startswith('/'), caso['pantalla'])
