"""Matriz de accesos: cada perfil entra solo a las pantallas que tiene establecidas.

La matriz ACCESOS es la especificación (README, «Seguridad y perfiles» y «Roles de trabajo y flujo», más las tablas de la
Evaluación 3). La prueba recorre todas las rutas con cada perfil y compara: «sí» = la página responde 200; «no» = no la
ve (404 o redirección a la portada, y nunca 200). Sin sesión, toda ruta interna pide iniciar sesión.
"""
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import CasoSocial, Compromiso, Hito, MembresiaOrganizacion, Organizacion, ResponsableHito, Territorio, Vecino
from .pruebas_base import EscenarioBase, crear_funcionario, fijar_hoy
from .rut import digito_verificador

A, C, D, P = 'administrador', 'coordinador', 'delegado', 'profesional'
TODOS = {A, C, D, P}

# Ruta -> perfiles que la ven. Las rutas con objeto usan objetos de la delegación propia (Centro).
ACCESOS = {
    'panel': TODOS, 'actividades': TODOS, 'actividad_nueva': TODOS, 'agenda': TODOS, 'agenda_cartas': TODOS, 'solicitudes': TODOS,
    'compromiso_nuevo': TODOS, 'dashboard': TODOS, 'semaforo': TODOS, 'matriz_cargos': TODOS, 'resumen': TODOS, 'ficha_personal': TODOS, 'informe': TODOS,
    'alertas': TODOS, 'tablero_analitico': TODOS, 'cambiar_contrasena': TODOS, 'mantenedores': TODOS, 'delegacion_propia': TODOS,
    'casos_sociales': TODOS,
    'caso_social_nuevo': {A, P},
    'ajuste_nuevo': {A, D},
    'ausencia_nueva': {A, D},
    'delegados': {A, C},
    'auditoria_consulta': {A},
    'perfiles': {A},
    'exportar_organizaciones': TODOS,
    # Mantenedores: listado
    'lista:delegaciones': {A, C}, 'lista:cargos': {A, C}, 'lista:roles': {A}, 'lista:funcionarios': {A}, 'lista:catalogo': {A, C},
    'lista:organizaciones': TODOS, 'lista:periodos': {A, C}, 'lista:parametros': {A, C}, 'lista:items': {A, C}, 'lista:metas': {A, C},
    'lista:ajustes': {A, C, D}, 'lista:ausencias': {A, C, D}, 'lista:territorios': TODOS, 'lista:vecinos': TODOS,
    'lista:membresias': TODOS, 'lista:hitos': TODOS, 'lista:subtipos': TODOS,
    # Mantenedores: agregar
    'nuevo:delegaciones': {A, C}, 'nuevo:cargos': {A, C}, 'nuevo:roles': {A}, 'nuevo:funcionarios': {A}, 'nuevo:catalogo': {A, C},
    'nuevo:organizaciones': {A}, 'nuevo:periodos': {A, C}, 'nuevo:parametros': {A}, 'nuevo:items': {A, C}, 'nuevo:metas': {A, C},
    'nuevo:ajustes': {A, D}, 'nuevo:ausencias': {A, D}, 'nuevo:territorios': {A, C}, 'nuevo:vecinos': TODOS,
    'nuevo:membresias': {A, C, D}, 'nuevo:hitos': {A, C, D}, 'nuevo:subtipos': {A, C},
    # Mantenedores: modificar y eliminar un registro de la delegación propia
    'editar:organizaciones': {A, C, D}, 'eliminar:organizaciones': {A},
    'editar:territorios': {A, C}, 'eliminar:territorios': {A, C},
    'editar:vecinos': TODOS, 'eliminar:vecinos': {A, C},
    'editar:membresias': {A, C, D}, 'eliminar:membresias': {A, C},
    'editar:hitos': {A, C, D}, 'eliminar:hitos': {A, C},
    # Registros propios del profesional (autor) en Centro
    'tarea_editar': {A, C, P}, 'tarea_eliminar': {A, C},
    'caso_social_editar': {P},
    'actividad_detalle': TODOS, 'actividad_editar': {A, C, P}, 'actividad_eliminar': {A, C}, 'evidencia_subir': {P},
}

# Rutas de registros de OTRA delegación (Rural): solo el alcance global las ve.
ACCESOS_OTRA_DELEGACION = {
    'delegacion_ajena': {A, C}, 'actividad_ajena': {A, C}, 'tarea_ajena_editar': {A, C}, 'editar:vecino_ajeno': {A, C},
    'editar:hito_ajeno': {A, C}, 'editar:membresia_ajena': {A, C}, 'editar:organizacion_ajena': {A, C}, 'caso_social_ajeno': set(),
}


def rut(cuerpo):
    return f'{cuerpo}-{digito_verificador(cuerpo)}'


class MatrizDeAccesosTests(EscenarioBase, TestCase):
    """CU-26.1 Denegar acceso por ámbito (RF-002, RNF-004). Cada perfil entra solo a lo establecido."""

    def setUp(self):
        self.crear_escenario()
        fijar_hoy(self, date(2026, 9, 10))
        self.usuarios = {
            A: crear_funcionario('adm-matriz', 'administrador', cargo=self.cargo),
            C: crear_funcionario('coord-matriz', 'coordinador', cargo=self.cargo),
            D: self.usuario_verificador,
            P: self.usuario_autor,
        }
        self.delegado_rural = crear_funcionario('del-rural-matriz', 'delegado', cargo=self.cargo, delegacion=self.rural)
        self.actividad = self.nueva_actividad()
        self.actividad_rural = self.nueva_actividad(funcionario_autor=self.delegado_rural.funcionario, delegacion=self.rural)
        self.tarea = self.nuevo_compromiso(folio='MAT-1')
        self.tarea_rural = self.nuevo_compromiso(folio='MAT-2', delegacion=self.rural, funcionario_responsable=self.delegado_rural.funcionario)
        self.territorio = Territorio.objects.create(nombre='Casco', delegacion=self.centro)
        self.territorio_rural = Territorio.objects.create(nombre='Algarrobito', delegacion=self.rural)
        self.vecino = Vecino.objects.create(rut=rut(11111111), nombres='Ana', apellidos='R', territorio=self.territorio)
        self.vecino_rural = Vecino.objects.create(rut=rut(22222222), nombres='Luis', apellidos='S', territorio=self.territorio_rural)
        self.organizacion = Organizacion.objects.create(nombre='JV Centro', delegacion=self.centro)
        self.organizacion_rural = Organizacion.objects.create(nombre='JV Rural', delegacion=self.rural)
        self.membresia = MembresiaOrganizacion.objects.create(vecino=self.vecino, organizacion=self.organizacion)
        self.membresia_rural = MembresiaOrganizacion.objects.create(vecino=self.vecino_rural, organizacion=self.organizacion_rural)
        self.hito = Hito.objects.create(nombre='H1', delegacion=self.centro, fecha_programada=date(2026, 12, 1))
        ResponsableHito.objects.create(hito=self.hito, funcionario=self.verificador, rol='principal')
        self.hito_rural = Hito.objects.create(nombre='H2', delegacion=self.rural, fecha_programada=date(2026, 12, 1))
        self.caso = CasoSocial.objects.create(funcionario=self.autor, nombre_usuario='Ana', telefono_usuario='912345678', tipo='pgu')
        self.caso_rural = CasoSocial.objects.create(funcionario=self.delegado_rural.funcionario, nombre_usuario='Luis', telefono_usuario='912345678', tipo='pgu')

    def _urls(self):
        m = lambda accion, slug, pk=None: reverse(f'mantenedor_{accion}', args=[slug] + ([pk] if pk else []))
        urls = {
            'panel': reverse('panel'), 'actividades': reverse('actividades'), 'actividad_nueva': reverse('actividad_nueva'),
            'agenda': reverse('agenda'), 'agenda_cartas': reverse('agenda') + '?tubo=carta', 'solicitudes': reverse('solicitudes'),
            'compromiso_nuevo': reverse('compromiso_nuevo'), 'dashboard': reverse('dashboard'), 'semaforo': reverse('semaforo'),
            'matriz_cargos': reverse('matriz_cargos'), 'resumen': reverse('resumen'), 'ficha_personal': reverse('ficha_personal'), 'informe': reverse('informe'), 'alertas': reverse('alertas'),
            'tablero_analitico': reverse('tablero_analitico'), 'cambiar_contrasena': reverse('cambiar_contrasena'), 'mantenedores': reverse('mantenedores'),
            'delegacion_propia': reverse('delegacion_detalle', args=['Centro']), 'casos_sociales': reverse('casos_sociales'),
            'caso_social_nuevo': reverse('caso_social_nuevo'), 'ajuste_nuevo': reverse('ajuste_nuevo'), 'ausencia_nueva': reverse('ausencia_nueva'),
            'delegados': reverse('delegados'), 'auditoria_consulta': reverse('auditoria_consulta'), 'perfiles': reverse('perfiles'),
            'exportar_organizaciones': reverse('exportar_organizaciones'),
            'tarea_editar': reverse('compromiso_editar', args=[self.tarea.pk]), 'tarea_eliminar': reverse('compromiso_eliminar', args=[self.tarea.pk]),
            'caso_social_editar': reverse('caso_social_editar', args=[self.caso.pk]),
            'actividad_detalle': reverse('actividad_detalle', args=[self.actividad.codigo_verificador]),
            'actividad_editar': reverse('actividad_editar', args=[self.actividad.codigo_verificador]),
            'actividad_eliminar': reverse('actividad_eliminar', args=[self.actividad.codigo_verificador]),
            'evidencia_subir': reverse('evidencia_subir', args=[self.actividad.codigo_verificador]),
            'editar:organizaciones': m('editar', 'organizaciones', self.organizacion.pk), 'eliminar:organizaciones': m('eliminar', 'organizaciones', self.organizacion.pk),
            'editar:territorios': m('editar', 'territorios', self.territorio.pk), 'eliminar:territorios': m('eliminar', 'territorios', self.territorio.pk),
            'editar:vecinos': m('editar', 'vecinos', self.vecino.pk), 'eliminar:vecinos': m('eliminar', 'vecinos', self.vecino.pk),
            'editar:membresias': m('editar', 'membresias', self.membresia.pk), 'eliminar:membresias': m('eliminar', 'membresias', self.membresia.pk),
            'editar:hitos': m('editar', 'hitos', self.hito.pk), 'eliminar:hitos': m('eliminar', 'hitos', self.hito.pk),
            # otra delegación
            'delegacion_ajena': reverse('delegacion_detalle', args=['Rural']),
            'actividad_ajena': reverse('actividad_detalle', args=[self.actividad_rural.codigo_verificador]),
            'tarea_ajena_editar': reverse('compromiso_editar', args=[self.tarea_rural.pk]),
            'editar:vecino_ajeno': m('editar', 'vecinos', self.vecino_rural.pk), 'editar:hito_ajeno': m('editar', 'hitos', self.hito_rural.pk),
            'editar:membresia_ajena': m('editar', 'membresias', self.membresia_rural.pk),
            'editar:organizacion_ajena': m('editar', 'organizaciones', self.organizacion_rural.pk),
            'caso_social_ajeno': reverse('caso_social_editar', args=[self.caso_rural.pk]),
        }
        for slug in ('delegaciones', 'cargos', 'roles', 'funcionarios', 'catalogo', 'organizaciones', 'periodos', 'parametros', 'items', 'metas',
                     'ajustes', 'ausencias', 'territorios', 'vecinos', 'membresias', 'hitos', 'subtipos'):
            urls[f'lista:{slug}'] = m('lista', slug)
            urls[f'nuevo:{slug}'] = m('nuevo', slug)
        return urls

    def test_cada_perfil_entra_solo_a_lo_establecido(self):
        """CP-EVA-061 CU-26.1 Matriz de accesos (RF-002, RNF-004). Todas las rutas con los cuatro perfiles."""
        urls = self._urls()
        esperado = {**ACCESOS, **ACCESOS_OTRA_DELEGACION}
        self.assertEqual(set(esperado), set(urls), 'La matriz debe cubrir todas las rutas probadas')
        diferencias = []
        for perfil, usuario in self.usuarios.items():
            self.client.force_login(usuario)
            for nombre, url in urls.items():
                codigo = self.client.get(url).status_code
                if (codigo == 200) != (perfil in esperado[nombre]):
                    diferencias.append(f'{perfil:13} {nombre:28} {url} -> {codigo} (esperado {"sí" if perfil in esperado[nombre] else "no"})')
        self.assertEqual(diferencias, [], '\n' + '\n'.join(diferencias))

    def test_sin_sesion_toda_ruta_interna_pide_iniciar_sesion(self):
        """CP-EVA-062 CU-26.1 Matriz de accesos (RF-002, RNF-004). Sin sesión solo se ven portada, territorio, login y recuperación."""
        for url in (reverse('inicio'), reverse('institucional'), reverse('login'), reverse('password_reset')):
            self.assertEqual(self.client.get(url).status_code, 200, url)
        diferencias = []
        for nombre, url in self._urls().items():
            respuesta = self.client.get(url)
            if respuesta.status_code != 302 or not respuesta['Location'].startswith(reverse('login')):
                diferencias.append(f'{nombre}: {respuesta.status_code} {respuesta.get("Location", "")}')
        self.assertEqual(diferencias, [], '\n' + '\n'.join(diferencias))

    def test_un_usuario_sin_perfil_ni_funcionario_no_entra_a_nada_operativo(self):
        """CP-EVA-063 CU-26.1 Matriz de accesos (RF-002). Una cuenta sin perfil ni ficha no ve datos ni mantenedores."""
        self.client.force_login(User.objects.create_user('sin-perfil-matriz', password='x'))
        abiertas = []
        for nombre, url in self._urls().items():
            if nombre in ('cambiar_contrasena',):
                continue
            respuesta = self.client.get(url)
            if respuesta.status_code == 200 and nombre not in ('panel', 'dashboard', 'semaforo', 'matriz_cargos', 'resumen', 'informe', 'alertas', 'tablero_analitico',
                                                                'actividades', 'agenda', 'agenda_cartas', 'solicitudes'):
                abiertas.append(f'{nombre}: {url}')
        self.assertEqual(abiertas, [], '\n' + '\n'.join(abiertas))

    def test_un_funcionario_desactivado_pierde_el_acceso(self):
        """CP-EVA-064 CU-26.1 Matriz de accesos (RF-002). Con la ficha desactivada no ve mantenedores ni revisa."""
        self.coordinador_inactivo = self.usuarios[C]
        self.coordinador_inactivo.funcionario.estado = False
        self.coordinador_inactivo.funcionario.save()
        self.client.force_login(self.coordinador_inactivo)
        for url in (reverse('mantenedores'), reverse('delegados'), reverse('mantenedor_lista', args=['vecinos'])):
            self.assertNotEqual(self.client.get(url).status_code, 200, url)

    def test_las_paginas_permitidas_no_muestran_datos_de_otra_delegacion(self):
        """CP-EVA-065 CU-29.1 Restricción de búsqueda por ámbito (RF-032). Delegado y profesional no ven registros de Rural."""
        ajenos = [self.tarea_rural.folio, self.actividad_rural.codigo_verificador, self.vecino_rural.rut, 'JV Rural', 'Luis</strong>', '>H2<']
        urls = self._urls()
        urls['informe_tareas'] = reverse('informe') + '?tipo=compromisos'
        urls['informe_rural'] = reverse('informe') + f'?tipo=actividades&delegacion={self.rural.pk}'
        urls['tablero_rural'] = reverse('tablero_analitico') + f'?delegacion={self.rural.pk}&desde=2026-09-01&hasta=2026-09-30'
        urls['agenda_rural'] = reverse('agenda') + f'?delegacion={self.rural.pk}'
        paginas = ['panel', 'actividades', 'agenda', 'solicitudes', 'dashboard', 'semaforo', 'matriz_cargos', 'resumen', 'informe', 'alertas', 'tablero_analitico',
                   'casos_sociales', 'lista:vecinos', 'lista:organizaciones', 'lista:membresias', 'lista:hitos', 'lista:territorios',
                   'exportar_organizaciones', 'informe_tareas', 'informe_rural', 'tablero_rural', 'agenda_rural']
        filtraciones = []
        for perfil in (D, P):
            self.client.force_login(self.usuarios[perfil])
            for nombre in paginas:
                contenido = self.client.get(urls[nombre]).content.decode('utf-8')
                filtraciones += [f'{perfil} {nombre}: {texto}' for texto in ajenos if texto in contenido]
            if self.client.get(reverse('vecino_buscar'), {'rut': self.vecino_rural.rut}).json().get('encontrado'):
                filtraciones.append(f'{perfil} vecino_buscar: {self.vecino_rural.rut}')
        self.assertEqual(filtraciones, [], '\n' + '\n'.join(filtraciones))
        # Control positivo: la coordinación sí ve esos mismos datos, así que la búsqueda de textos detecta una filtración real.
        self.client.force_login(self.usuarios[C])
        vistos = {
            self.tarea_rural.folio: urls['agenda'], self.actividad_rural.codigo_verificador: urls['actividades'], self.vecino_rural.rut: urls['lista:vecinos'],
            'JV Rural': urls['lista:organizaciones'], 'Luis</strong>': urls['casos_sociales'], '>H2<': urls['lista:hitos'],
        }
        for texto, url in vistos.items():
            self.assertContains(self.client.get(url), texto, msg_prefix=f'control positivo {url}')

    def test_un_usuario_sin_perfil_no_ve_datos_en_las_paginas_generales(self):
        """CP-EVA-066 CU-29.1 Restricción por ámbito (RF-002). Paneles, listas e informes llegan vacíos a una cuenta sin perfil ni ficha."""
        self.client.force_login(User.objects.create_user('sin-perfil-datos', password='x'))
        datos = [self.tarea.folio, self.tarea_rural.folio, self.actividad.codigo_verificador, self.actividad_rural.codigo_verificador]
        filtraciones = []
        for nombre in ('panel', 'dashboard', 'semaforo', 'resumen', 'informe', 'alertas', 'tablero_analitico', 'actividades', 'agenda', 'solicitudes'):
            contenido = self.client.get(self._urls()[nombre]).content.decode('utf-8')
            filtraciones += [f'{nombre}: {texto}' for texto in datos if texto in contenido]
        self.assertEqual(filtraciones, [], '\n' + '\n'.join(filtraciones))

    def test_las_acciones_post_respetan_el_perfil(self):
        """CP-EVA-067 CU-26.1 Restringir operaciones críticas (RF-002, RNF-004). Enviar el formulario a mano no salta el permiso."""
        from .models import Actividad, Ajuste, Evidencia, Periodo
        self.nueva_evidencia(self.actividad)
        ajuste = Ajuste.objects.create(tipo='felicitacion', emisor='JV', funcionario=self.autor, periodo=self.periodo,
                                       respaldo='ajustes/x.pdf', informado_por=self.verificador)
        no_aprobada = lambda actividad: (lambda: Actividad.objects.get(pk=actividad.pk).estado != 'aprobada')
        existe = lambda modelo, pk: (lambda: modelo.objects.filter(pk=pk).exists())
        ajuste_sin_decidir = lambda: Ajuste.objects.get(pk=ajuste.pk).estado == 'informado'
        caso_intacto = lambda: CasoSocial.objects.get(pk=self.caso.pk).nombre_usuario == 'Ana'
        datos_caso = {'nombre_usuario': 'Cambiado', 'telefono_usuario': '912345678', 'etapa': 1, 'tipo': 'pgu'}
        sin_evidencia_nueva = lambda: Evidencia.objects.filter(actividad=self.actividad).count() == 1
        intentos = {
            P: [
                ('revisar', reverse('revisar_actividad', args=[self.actividad.codigo_verificador, 'aprobar']), {}, no_aprobada(self.actividad)),
                ('eliminar actividad', reverse('actividad_eliminar', args=[self.actividad.codigo_verificador]), {}, existe(Actividad, self.actividad.pk)),
                ('eliminar tarea', reverse('compromiso_eliminar', args=[self.tarea.pk]), {}, existe(Compromiso, self.tarea.pk)),
                ('decidir ajuste', reverse('ajuste_decidir', args=[ajuste.pk, 'aplicar']), {}, ajuste_sin_decidir),
                ('cerrar período', reverse('periodo_accion', args=[self.periodo.pk, 'cerrar']), {}, lambda: Periodo.objects.get(pk=self.periodo.pk).estado == 'abierto'),
                ('eliminar vecino', reverse('mantenedor_eliminar', args=['vecinos', self.vecino.pk]), {}, existe(Vecino, self.vecino.pk)),
                ('crear territorio', reverse('mantenedor_nuevo', args=['territorios']), {'nombre': 'X', 'delegacion': self.centro.pk, 'activo': 'on'},
                 lambda: not Territorio.objects.filter(nombre='X').exists()),
                ('estado de tarea ajena', reverse('compromiso_estado', args=[self.tarea_rural.pk, 'proceso']), {},
                 lambda: Compromiso.objects.get(pk=self.tarea_rural.pk).estado == 'ingresado'),
                ('comentar actividad ajena', reverse('comentario_nuevo', args=[self.actividad_rural.codigo_verificador]), {'contenido': 'x'},
                 lambda: not self.actividad_rural.comentarios.exists()),
            ],
            D: [
                ('decidir ajuste', reverse('ajuste_decidir', args=[ajuste.pk, 'aplicar']), {}, ajuste_sin_decidir),
                ('eliminar actividad', reverse('actividad_eliminar', args=[self.actividad.codigo_verificador]), {}, existe(Actividad, self.actividad.pk)),
                ('eliminar tarea', reverse('compromiso_eliminar', args=[self.tarea.pk]), {}, existe(Compromiso, self.tarea.pk)),
                ('revisar actividad ajena', reverse('revisar_actividad', args=[self.actividad_rural.codigo_verificador, 'aprobar']), {}, no_aprobada(self.actividad_rural)),
                ('subir evidencia ajena', reverse('evidencia_subir', args=[self.actividad.codigo_verificador]), {}, sin_evidencia_nueva),
                ('modificar gestión social ajena', reverse('caso_social_editar', args=[self.caso.pk]), datos_caso, caso_intacto),
                ('editar hito de Rural', reverse('mantenedor_editar', args=['hitos', self.hito_rural.pk]),
                 {'nombre': 'Cambiado', 'delegacion': self.rural.pk, 'fecha_programada': '2026-12-01', 'estado': 'planificado',
                  'responsable_principal': self.verificador.pk}, lambda: Hito.objects.get(pk=self.hito_rural.pk).nombre == 'H2'),
                ('crear usuario', reverse('mantenedor_nuevo', args=['funcionarios']), {'username': 'intruso', 'nombre': 'I', 'cargo': self.cargo.pk},
                 lambda: not User.objects.filter(username='intruso').exists()),
            ],
            C: [
                ('crear usuario', reverse('mantenedor_nuevo', args=['funcionarios']), {'username': 'intruso2', 'nombre': 'I', 'cargo': self.cargo.pk},
                 lambda: not User.objects.filter(username='intruso2').exists()),
                ('subir evidencia ajena', reverse('evidencia_subir', args=[self.actividad.codigo_verificador]), {}, sin_evidencia_nueva),
                ('modificar gestión social ajena', reverse('caso_social_editar', args=[self.caso.pk]), datos_caso, caso_intacto),
            ],
        }
        fallas = []
        for perfil, lista in intentos.items():
            self.client.force_login(self.usuarios[perfil])
            for nombre, url, datos, no_ocurrio in lista:
                self.client.post(url, datos)
                if not no_ocurrio():
                    fallas.append(f'{perfil}: {nombre}')
        self.assertEqual(fallas, [], '\n' + '\n'.join(fallas))
