"""Pruebas de las funciones agregadas en la Evaluación 3 (protocolo en docs/PROTOCOLO_PRUEBAS.md).

Cada prueba declara en su docstring su código de caso (CP-EVA-nnn), el caso de uso y el requisito que verifica.
"""
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.core import mail
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from gestion_app import graficos

from .cuentas import generar_contrasena_temporal
from .forms import CompromisoForm, MetaForm
from .models import (
    Actividad, Auditoria, CasoSocial, Catalogo, Compromiso, Funcionario, Hito, MembresiaOrganizacion, Meta, Organizacion,
    SubtipoAtencion, Territorio, Validacion, Vecino,
)
from .pruebas_base import CLAVE_PRUEBA, EscenarioBase, crear_funcionario, fijar_hoy
from .rut import digito_verificador, es_rut_valido, normalizar_rut

FECHA_HOY = date(2026, 9, 10)


def rut_valido(cuerpo):
    return f'{cuerpo}-{digito_verificador(cuerpo)}'


class ContrasenaTemporalTests(TestCase):
    """Creación de usuarios con contraseña temporal y cambio obligatorio en el primer ingreso."""

    def setUp(self):
        self.admin = crear_funcionario('admin-e3', 'administrador')
        self.cargo = Funcionario.objects.get(usuario=self.admin).cargo
        self.client.force_login(self.admin)

    def _crear(self, **extra):
        datos = {
            'username': 'nuevo.e3', 'nombre': 'Nuevo E3', 'email': 'nuevo@example.com', 'cargo': self.cargo.pk,
            'roles': [Funcionario.objects.get(usuario=self.admin).roles.model.objects.get(nombre_rol='funcionario').pk], 'estado': 'on',
            'password': '', 'password_confirm': '',
        }
        datos.update(extra)
        return self.client.post(reverse('mantenedor_nuevo', args=['funcionarios']), datos, follow=True)

    def test_crear_sin_contrasena_genera_una_temporal_y_la_muestra_una_vez(self):
        """CP-EVA-001 CU-26 Crear usuario con contraseña temporal (RF-051). Sin clave escrita, el sistema genera una y la muestra."""
        respuesta = self._crear()
        funcionario = Funcionario.objects.get(identificador_institucional='nuevo.e3')
        self.assertTrue(funcionario.debe_cambiar_contrasena)
        avisos = [str(m) for m in respuesta.context['messages']]
        temporal = next(a for a in avisos if 'Contraseña temporal' in a).split(': ')[1].split(' ')[0]
        self.assertTrue(funcionario.usuario.check_password(temporal))
        self.assertFalse(Auditoria.objects.filter(valor_nuevo__contains=temporal).exists())

    def test_una_contrasena_escrita_al_crear_tambien_es_temporal(self):
        """CP-EVA-002 CU-26 Crear usuario con contraseña temporal (RF-051). La clave que asigna la administración obliga a cambiarla."""
        self._crear(password='Clave-Temporal-2026', password_confirm='Clave-Temporal-2026')
        self.assertTrue(Funcionario.objects.get(identificador_institucional='nuevo.e3').debe_cambiar_contrasena)

    def test_el_primer_ingreso_obliga_a_cambiar_la_contrasena(self):
        """CP-EVA-003 CU-26 Cambio obligatorio en el primer ingreso (RF-051). Cualquier página redirige a cambiar la contraseña."""
        usuario = crear_funcionario('temporal-e3', 'funcionario')
        Funcionario.objects.filter(usuario=usuario).update(debe_cambiar_contrasena=True)
        self.client.logout()
        respuesta = self.client.post(reverse('login'), {'username': 'temporal-e3', 'password': CLAVE_PRUEBA})
        self.assertRedirects(respuesta, reverse('panel'), target_status_code=302)
        for ruta in (reverse('panel'), reverse('actividades'), reverse('agenda'), reverse('tablero_analitico')):
            self.assertRedirects(self.client.get(ruta), reverse('cambiar_contrasena'))
        self.assertContains(self.client.get(reverse('cambiar_contrasena')), 'Cambia tu contraseña temporal')

    def test_cambiar_la_contrasena_libera_la_cuenta_y_queda_auditado(self):
        """CP-EVA-004 CU-26 Cambio obligatorio en el primer ingreso (RF-051, RF-036). Tras cambiarla, el sistema se usa normalmente."""
        usuario = crear_funcionario('temporal2-e3', 'funcionario')
        Funcionario.objects.filter(usuario=usuario).update(debe_cambiar_contrasena=True)
        self.client.force_login(usuario)
        respuesta = self.client.post(reverse('cambiar_contrasena'), {
            'old_password': CLAVE_PRUEBA, 'new_password1': 'Personal-Segura-2026', 'new_password2': 'Personal-Segura-2026',
        })
        self.assertRedirects(respuesta, reverse('panel'))
        self.assertFalse(Funcionario.objects.get(usuario=usuario).debe_cambiar_contrasena)
        self.assertEqual(self.client.get(reverse('actividades')).status_code, 200)
        self.assertTrue(Auditoria.objects.filter(evento='cambiar_contrasena', identificador_registro='temporal2-e3').exists())

    def test_la_nueva_contrasena_debe_cumplir_las_reglas(self):
        """CP-EVA-005 CU-26 Cambio obligatorio en el primer ingreso (RF-051). Una clave débil o igual en ambos campos se valida."""
        usuario = crear_funcionario('temporal3-e3', 'funcionario')
        Funcionario.objects.filter(usuario=usuario).update(debe_cambiar_contrasena=True)
        self.client.force_login(usuario)
        respuesta = self.client.post(reverse('cambiar_contrasena'), {'old_password': CLAVE_PRUEBA, 'new_password1': '123', 'new_password2': '123'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(Funcionario.objects.get(usuario=usuario).debe_cambiar_contrasena)

    def test_con_contrasena_temporal_se_puede_cerrar_la_sesion(self):
        """CP-EVA-006 CU-26 Cambio obligatorio en el primer ingreso (RF-051). Salir no exige cambiarla."""
        usuario = crear_funcionario('temporal4-e3', 'funcionario')
        Funcionario.objects.filter(usuario=usuario).update(debe_cambiar_contrasena=True)
        self.client.force_login(usuario)
        self.assertRedirects(self.client.post(reverse('logout')), reverse('inicio'))

    def test_restablecer_desde_la_edicion_genera_otra_temporal(self):
        """CP-EVA-007 CU-26 Crear usuario con contraseña temporal (RF-051). La administración restablece con una clave temporal nueva."""
        usuario = crear_funcionario('reset-e3', 'funcionario')
        funcionario = Funcionario.objects.get(usuario=usuario)
        datos = {'username': 'reset-e3', 'nombre': 'reset-e3', 'email': '', 'cargo': funcionario.cargo_id,
                 'roles': [r.pk for r in funcionario.roles.all()], 'estado': 'on', 'generar_temporal': 'on'}
        self.client.post(reverse('mantenedor_editar', args=['funcionarios', funcionario.pk]), datos)
        funcionario.refresh_from_db()
        self.assertTrue(funcionario.debe_cambiar_contrasena)
        self.assertFalse(funcionario.usuario.check_password(CLAVE_PRUEBA))

    def test_recuperar_por_correo_quita_la_marca_temporal(self):
        """CP-EVA-008 CU-26 Recuperar contraseña (RF-051). Quien recupera por correo elige su propia clave."""
        usuario = crear_funcionario('recupera-e3', 'funcionario')
        usuario.email = 'recupera@example.com'
        usuario.save()
        Funcionario.objects.filter(usuario=usuario).update(debe_cambiar_contrasena=True)
        self.client.logout()
        self.client.post(reverse('password_reset'), {'email': 'recupera@example.com'})
        enlace = next(linea for linea in mail.outbox[0].body.splitlines() if '/recuperar/' in linea).strip()
        ruta = enlace[enlace.index('/recuperar/'):]
        respuesta = self.client.get(ruta, follow=True)
        self.client.post(respuesta.redirect_chain[-1][0], {'new_password1': 'Recuperada-Segura-26', 'new_password2': 'Recuperada-Segura-26'})
        self.assertFalse(Funcionario.objects.get(usuario=usuario).debe_cambiar_contrasena)

    def test_la_contrasena_temporal_es_aleatoria_y_robusta(self):
        """CP-EVA-009 CU-26 Crear usuario con contraseña temporal (RF-051, RNF-004). Cada clave generada es distinta y mezcla caracteres."""
        claves = {generar_contrasena_temporal() for _ in range(50)}
        self.assertEqual(len(claves), 50)
        for clave in claves:
            self.assertEqual(len(clave), 12)
            self.assertTrue(any(c.isupper() for c in clave) and any(c.islower() for c in clave) and any(c.isdigit() for c in clave))

    def test_la_contrasena_se_guarda_como_hash(self):
        """CP-EVA-010 CU-26 Almacenar contraseñas con hash (RNF-004). La base nunca guarda la clave en texto plano."""
        usuario = User.objects.get(username='admin-e3')
        self.assertNotIn(CLAVE_PRUEBA, usuario.password)
        self.assertRegex(usuario.password, r'^[a-z0-9_]+\$')
        from django.conf import settings
        from django.contrib.auth.hashers import get_hashers
        # Fuera de las pruebas se usa el hasher por defecto de Django (PBKDF2-SHA256 con sal).
        self.assertTrue(settings.EJECUTANDO_PRUEBAS)
        self.assertTrue(get_hashers())


@override_settings(LOGIN_MAX_INTENTOS=3, LOGIN_BLOQUEO_MINUTOS=15)
class BloqueoDeIngresoTests(TestCase):
    """Bloqueo temporal del ingreso tras varios intentos fallidos (fuerza bruta)."""

    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        crear_funcionario('bloqueo-e3', 'funcionario')
        crear_funcionario('otro-e3', 'funcionario')

    def _ingresar(self, usuario, clave):
        return self.client.post(reverse('login'), {'username': usuario, 'password': clave})

    def test_tras_los_intentos_fallidos_se_bloquea_aunque_la_clave_sea_correcta(self):
        """CP-EVA-011 CU-26 Bloquear ingreso por intentos fallidos (RF-061, RNF-004). El cuarto intento, aun correcto, se rechaza."""
        for _ in range(3):
            self._ingresar('bloqueo-e3', 'incorrecta')
        respuesta = self._ingresar('bloqueo-e3', CLAVE_PRUEBA)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Demasiados intentos fallidos')
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertTrue(Auditoria.objects.filter(evento='bloqueo_ingreso', identificador_registro='bloqueo-e3').exists())

    def test_el_bloqueo_no_afecta_a_otra_cuenta(self):
        """CP-EVA-012 CU-26 Bloquear ingreso por intentos fallidos (RF-061). Otro usuario sigue ingresando."""
        for _ in range(3):
            self._ingresar('bloqueo-e3', 'incorrecta')
        self.assertRedirects(self._ingresar('otro-e3', CLAVE_PRUEBA), reverse('panel'), fetch_redirect_response=False)

    def test_un_ingreso_correcto_reinicia_el_contador(self):
        """CP-EVA-013 CU-26 Bloquear ingreso por intentos fallidos (RF-061). Los fallos previos a un ingreso correcto no se acumulan."""
        for _ in range(2):
            self._ingresar('bloqueo-e3', 'incorrecta')
        self._ingresar('bloqueo-e3', CLAVE_PRUEBA)
        self.client.logout()
        for _ in range(2):
            self._ingresar('bloqueo-e3', 'incorrecta')
        self.assertRedirects(self._ingresar('bloqueo-e3', CLAVE_PRUEBA), reverse('panel'), fetch_redirect_response=False)


class CacheCompartidaTests(TestCase):
    """El contador de intentos de ingreso se comparte entre los procesos de Gunicorn del servidor."""

    def test_en_el_servidor_la_cache_es_compartida_por_los_procesos(self):
        """CP-EVA-068 CU-26 Bloquear ingreso por intentos fallidos (RF-061, RNF-004). Regresión DEF-09: dos procesos ven el mismo contador."""
        import json
        import subprocess
        import sys
        import tempfile
        from django.conf import settings
        from django.core.cache.backends.filebased import FileBasedCache
        # 1) Fuera de las pruebas (como corre Gunicorn), settings elige la caché en archivos.
        salida = subprocess.run(
            [sys.executable, 'manage.py', 'shell', '-c', 'import json; from django.conf import settings; print(json.dumps(settings.CACHES))'],
            cwd=settings.BASE_DIR, capture_output=True, text=True, check=True,
        ).stdout.strip().splitlines()[-1]
        self.assertEqual(json.loads(salida)['default']['BACKEND'], 'django.core.cache.backends.filebased.FileBasedCache')
        # 2) Dos procesos con esa caché (dos instancias sobre la misma carpeta) ven el mismo contador.
        carpeta = tempfile.mkdtemp()
        worker_1, worker_2 = FileBasedCache(carpeta, {}), FileBasedCache(carpeta, {})
        worker_1.set('sgr-login-prueba', 4, 60)
        self.assertEqual(worker_2.get('sgr-login-prueba'), 4)


class MasAntecedentesTests(EscenarioBase, TestCase):
    """Flujo de verificación con el estado «solicitud de más antecedentes»."""

    def setUp(self):
        self.crear_escenario()
        fijar_hoy(self, FECHA_HOY)
        self.actividad = self.nueva_actividad(contacto_nombre='Vecina', contacto_telefono='912345678')
        self.evidencia = self.nueva_evidencia(self.actividad)
        Meta.objects.create(item=self.item, funcionario=self.autor, valor_objetivo=2)

    def _revisar(self, decision, observacion=''):
        self.client.force_login(self.usuario_verificador)
        return self.client.post(reverse('revisar_actividad', args=[self.actividad.codigo_verificador, decision]), {'observacion': observacion})

    def test_solicitar_antecedentes_exige_indicar_que_falta(self):
        """CP-EVA-014 CU-11 Solicitar más antecedentes (RF-052, RN-009). Sin detalle la solicitud no se registra."""
        self._revisar('antecedentes', '')
        self.actividad.refresh_from_db()
        self.assertEqual(self.actividad.estado, 'pendiente')
        self.assertFalse(Validacion.objects.exists())

    def test_la_solicitud_deja_la_actividad_en_espera_y_sin_puntaje(self):
        """CP-EVA-015 CU-11 Solicitar más antecedentes (RF-052, RN-009). La actividad queda «más antecedentes» y no suma al avance."""
        self._revisar('antecedentes', 'Falta la foto del lugar intervenido.')
        self.actividad.refresh_from_db()
        self.evidencia.refresh_from_db()
        self.assertEqual(self.actividad.estado, 'antecedentes')
        self.assertEqual(self.evidencia.estado_revision, 'antecedentes')
        self.assertEqual(Meta.objects.get().actividades_que_aportan().count(), 0)
        self.assertTrue(Auditoria.objects.filter(evento='antecedentes', identificador_registro=self.actividad.codigo_verificador).exists())

    def test_completar_los_antecedentes_vuelve_a_revision_y_al_aprobar_suma(self):
        """CP-EVA-016 CU-11 Solicitar más antecedentes (RF-052, RN-009). Nueva evidencia -> pendiente -> aprobada y suma."""
        self._revisar('antecedentes', 'Falta la foto.')
        self.client.force_login(self.usuario_autor)
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.post(reverse('evidencia_subir', args=[self.actividad.codigo_verificador]),
                         {'archivo_vinculo': SimpleUploadedFile('foto.png', b'\x89PNG\r\n', content_type='image/png'), 'comentario': 'Foto agregada'})
        self.actividad.refresh_from_db()
        self.assertEqual(self.actividad.estado, 'pendiente')
        self._revisar('aprobar')
        self.actividad.refresh_from_db()
        self.assertEqual(self.actividad.estado, 'aprobada')
        self.assertEqual(Meta.objects.get().actividades_que_aportan().count(), 1)

    def test_corregir_la_actividad_la_devuelve_a_revision(self):
        """CP-EVA-017 CU-11 Solicitar más antecedentes (RF-052). Modificar la actividad pedida vuelve a «pendiente»."""
        self._revisar('antecedentes', 'Indica el lugar exacto.')
        self.client.force_login(self.usuario_autor)
        actividad = Actividad.objects.get(pk=self.actividad.pk)
        datos = {
            'delegacion': self.centro.pk, 'lugar': 'Plaza de Armas', 'item': self.item.pk, 'catalogo': self.catalogo.pk,
            'fecha': '2026-09-10T10:00', 'solicitud_problema': 'Solicitud', 'accion': 'Acción', 'contacto_nombre': 'Vecina',
            'contacto_telefono': '912345678', 'tipo_accion': 'ejecucion', 'version': actividad.version,
        }
        self.client.post(reverse('actividad_editar', args=[actividad.codigo_verificador]), datos)
        actividad.refresh_from_db()
        self.assertEqual((actividad.estado, actividad.lugar), ('pendiente', 'Plaza de Armas'))
        self.assertEqual(actividad.evidencias.get().estado_revision, 'pendiente')

    def test_el_autor_ve_la_alerta_y_el_estado_en_su_lista(self):
        """CP-EVA-060 CU-14.2 Alertas (RF-052, RF-037). Regresión DEF-07: el autor ve qué falta y la lista no dice «En preparación»."""
        self._revisar('antecedentes', 'Falta la foto del lugar intervenido.')
        self.client.force_login(self.usuario_autor)
        self.assertContains(self.client.get(reverse('alertas')), 'Falta la foto del lugar intervenido.')
        lista = self.client.get(reverse('actividades'))
        self.assertContains(lista, 'Completar antecedentes solicitados')
        self.assertNotContains(lista, 'En preparación')

    def test_el_boton_de_antecedentes_aparece_para_el_revisor(self):
        """CP-EVA-018 CU-11 Solicitar más antecedentes (RF-052). El revisor ve las tres decisiones; el autor no."""
        self.client.force_login(self.usuario_verificador)
        url = reverse('revisar_actividad', args=[self.actividad.codigo_verificador, 'antecedentes'])
        self.assertContains(self.client.get(reverse('actividad_detalle', args=[self.actividad.codigo_verificador])), url)
        self.client.force_login(self.usuario_autor)
        self.assertNotContains(self.client.get(reverse('actividad_detalle', args=[self.actividad.codigo_verificador])), url)


class TuboTests(EscenarioBase, TestCase):
    """Tubo de seguimiento y Tubo de cartas: consulta compartida, búsqueda dinámica, filtros y permisos."""

    def setUp(self):
        self.crear_escenario()
        self.companero = crear_funcionario('companero-e3', 'funcionario', cargo=self.cargo, delegacion=self.centro)
        self.coordinador = crear_funcionario('coord-e3', 'coordinador', cargo=self.cargo)
        self.tarea = self.nuevo_compromiso(folio='AGR-E3-0001', solicitante='María Pérez', solicitante_rut='12.345.678-5')
        self.carta = self.nuevo_compromiso(folio='CAR-E3-0001', tipo='carta', solicitante='Junta Vecinal Norte')

    def test_el_rut_del_solicitante_se_valida_y_se_normaliza(self):
        """CP-EVA-019 CU-02.1 Validar datos de compromiso (RF-054). El RUT se guarda sin puntos y uno inválido se rechaza."""
        self.assertEqual(Compromiso.objects.get(pk=self.tarea.pk).solicitante_rut, '12345678-5')
        self.tarea.solicitante_rut = '12.345.678-9'
        with self.assertRaises(ValidationError):
            self.tarea.full_clean()

    def test_busca_por_codigo_rut_o_nombre(self):
        """CP-EVA-020 CU-29 Búsqueda dinámica del Tubo (RF-054, RF-032). Código, RUT con o sin puntos y nombre encuentran la tarea."""
        self.client.force_login(self.companero)
        for texto in ('AGR-E3', '12.345.678-5', '123456785', '12345678', 'maría'):
            respuesta = self.client.get(reverse('agenda'), {'q': texto})
            self.assertContains(respuesta, 'AGR-E3-0001', msg_prefix=texto)
        self.assertNotContains(self.client.get(reverse('agenda'), {'q': '99999999'}), 'AGR-E3-0001')

    def test_la_busqueda_al_escribir_devuelve_solo_los_resultados(self):
        """CP-EVA-021 CU-29 Búsqueda dinámica del Tubo (RF-054). Con parcial=1 responde el bloque de resultados, sin la página."""
        self.client.force_login(self.companero)
        respuesta = self.client.get(reverse('agenda'), {'q': 'María', 'parcial': '1'})
        self.assertContains(respuesta, 'AGR-E3-0001')
        self.assertNotContains(respuesta, '<html')
        self.assertTemplateUsed(respuesta, 'delegaciones_app/_tubo_resultados.html')
        self.assertContains(self.client.get(reverse('agenda')), 'data-busqueda-dinamica')

    def test_el_tubo_de_cartas_separa_las_cartas(self):
        """CP-EVA-022 CU-12 Tubo de cartas (RF-053). Las cartas se ven solo en su Tubo y las solicitudes en el de seguimiento."""
        self.client.force_login(self.companero)
        seguimiento = self.client.get(reverse('agenda'))
        cartas = self.client.get(reverse('agenda'), {'tubo': 'carta'})
        self.assertContains(seguimiento, 'AGR-E3-0001')
        self.assertNotContains(seguimiento, 'CAR-E3-0001')
        self.assertContains(cartas, 'CAR-E3-0001')
        self.assertNotContains(cartas, 'AGR-E3-0001')

    def test_registrar_una_carta_genera_su_folio(self):
        """CP-EVA-023 CU-02 Tubo de cartas (RF-053, RN-010). La carta recibe un folio CAR- generado y queda con historial."""
        self.client.force_login(self.usuario_autor)
        respuesta = self.client.post(reverse('compromiso_nuevo') + '?tubo=carta', {
            'tipo': 'carta', 'delegacion': self.centro.pk, 'funcionario_responsable': self.autor.pk, 'origen': 'externo',
            'solicitante': 'Club Deportivo', 'solicitante_rut': '', 'solicitante_telefono': '', 'territorio': 'Centro',
            'eje': 'Gestión Social', 'estado': 'ingresado', 'descripcion': 'Solicita uso de multicancha', 'fecha_comprometida': (timezone.localdate() + timedelta(days=5)).isoformat(),
        })
        carta = Compromiso.objects.get(descripcion='Solicita uso de multicancha')
        self.assertRedirects(respuesta, reverse('agenda') + '?tubo=carta', fetch_redirect_response=False)
        self.assertEqual(carta.tipo, 'carta')
        self.assertRegex(carta.folio, r'^CAR-\d{8}-[0-9A-F]{5}$')
        self.assertEqual(carta.historial.get().observacion, 'Ingreso de la carta')

    def test_las_cartas_no_cambian_el_item_del_tubo_y_el_informe_las_distingue(self):
        """CP-EVA-069 CU-07.1 Aplicar fórmulas de medición (RF-050, RF-053). Regresión DEF-10 y DEF-11: el % del Tubo mide solo tareas."""
        from .informes import filas_de_compromisos
        from .models import Indicador, ItemMedible
        item = ItemMedible.objects.create(cargo=self.cargo, periodo=self.periodo, nombre='Soluciones de ingresos al tubo', ponderacion=0, tipo_calculo='tubo')
        meta = Meta.objects.create(item=item, funcionario=self.autor, valor_objetivo=100)
        datos = {'item': item, 'solicitante_telefono': '912345678', 'fecha_ingreso': date(2026, 9, 5)}
        self.nuevo_compromiso(folio='TUB-1', estado='realizado', **datos)
        self.nuevo_compromiso(folio='TUB-2', **datos)
        self.nuevo_compromiso(folio='CAR-T1', tipo='carta', **datos)
        self.nuevo_compromiso(folio='CAR-T2', tipo='carta', **datos)
        self.assertEqual(Indicador.generar(meta).cumplimiento, Decimal('50.00'))  # 1 de 2 tareas; las 2 cartas no cuentan
        columnas, filas = filas_de_compromisos(Compromiso.objects.filter(folio__in=['TUB-1', 'CAR-T1']).order_by('folio'))
        self.assertEqual([dict(zip(columnas, fila))['Tubo'] for fila in filas], ['Cartas', 'Trabajo'])

    def test_filtra_por_funcionario_responsable(self):
        """CP-EVA-024 CU-12.1 Filtrar agenda compartida (RF-054, RF-032). El filtro «Funcionario» muestra solo sus tareas."""
        self.nuevo_compromiso(folio='AGR-E3-0002', funcionario_responsable=self.companero.funcionario)
        self.client.force_login(self.usuario_autor)
        respuesta = self.client.get(reverse('agenda'), {'responsable': self.companero.funcionario.pk})
        self.assertContains(respuesta, 'AGR-E3-0002')
        self.assertNotContains(respuesta, 'AGR-E3-0001')

    def test_toda_la_delegacion_consulta_pero_solo_el_responsable_modifica(self):
        """CP-EVA-025 CU-26.1 Permisos del Tubo (RF-054, RF-018). El compañero ve la tarea pero no la modifica."""
        self.client.force_login(self.companero)
        self.assertContains(self.client.get(reverse('agenda')), 'AGR-E3-0001')
        self.client.post(reverse('compromiso_estado', args=[self.tarea.pk, 'proceso']))
        self.assertEqual(Compromiso.objects.get(pk=self.tarea.pk).estado, 'ingresado')
        self.assertEqual(self.client.get(reverse('compromiso_editar', args=[self.tarea.pk])).status_code, 302)

    def test_una_tarea_realizada_queda_cerrada_para_su_responsable(self):
        """CP-EVA-026 CU-13.2 Reflejar cierre de compromiso (RF-018). Realizada, el responsable ya no la cambia; coordinación la reabre."""
        self.tarea.set_estado('realizado', self.autor, 'Resuelta')
        self.client.force_login(self.usuario_autor)
        respuesta = self.client.post(reverse('compromiso_estado', args=[self.tarea.pk, 'proceso']), follow=True)
        self.assertContains(respuesta, 'solo la coordinación puede reabrirla')
        self.assertEqual(Compromiso.objects.get(pk=self.tarea.pk).estado, 'realizado')
        respuesta = self.client.get(reverse('compromiso_editar', args=[self.tarea.pk]), follow=True)
        self.assertContains(respuesta, 'solo la coordinación puede reabrirla')
        self.client.force_login(self.coordinador)
        self.client.post(reverse('compromiso_estado', args=[self.tarea.pk, 'proceso']), {'observacion': 'Reapertura'})
        self.assertEqual(Compromiso.objects.get(pk=self.tarea.pk).estado, 'proceso')

    def test_el_formulario_del_tubo_usa_selector_de_fecha(self):
        """CP-EVA-027 CU-02.1 Validar datos de compromiso (RF-016). Regresión DEF-01: el plazo se elige con un calendario."""
        self.assertIn('type="date"', str(CompromisoForm(user=self.usuario_autor)['fecha_comprometida']))
        from .forms import ComentarioForm
        self.assertEqual(ComentarioForm().fields['contenido'].label, 'Comentario')


class VecinosYAutocompletadoTests(EscenarioBase, TestCase):
    """Vecinos, RUT y autocompletado de datos ya registrados."""

    def setUp(self):
        self.crear_escenario()
        self.territorio = Territorio.objects.create(nombre='Casco histórico', delegacion=self.centro)
        self.territorio_rural = Territorio.objects.create(nombre='Algarrobito', delegacion=self.rural)
        self.vecino = Vecino.objects.create(rut='11.111.111-1', nombres='Ana', apellidos='Rojas', telefono='+56 9 1111 1111', territorio=self.territorio)
        self.vecino_rural = Vecino.objects.create(rut=rut_valido(22222222), nombres='Luis', apellidos='Soto', territorio=self.territorio_rural)

    def test_el_rut_se_valida_con_modulo_11(self):
        """CP-EVA-028 CU-27.1 Mantener vecinos (RF-055). Dígito verificador correcto, incorrecto y con K."""
        self.assertTrue(es_rut_valido('11.111.111-1'))
        self.assertFalse(es_rut_valido('11.111.111-2'))
        self.assertTrue(es_rut_valido(rut_valido(10000013)))
        self.assertEqual(digito_verificador(10000013), 'K')
        self.assertEqual(normalizar_rut(' 11.111.111-1 '), '11111111-1')
        self.assertFalse(es_rut_valido('abc'))

    def test_un_rut_repetido_o_invalido_no_se_guarda(self):
        """CP-EVA-029 CU-27.1 Restringir elemento duplicado (RF-055). El mismo RUT con otro formato es duplicado."""
        coordinador = crear_funcionario('coord-vec', 'coordinador')
        self.client.force_login(coordinador)
        base = {'nombres': 'X', 'apellidos': 'Y', 'telefono': '', 'email': '', 'direccion': '', 'territorio': self.territorio.pk, 'activo': 'on'}
        respuesta = self.client.post(reverse('mantenedor_nuevo', args=['vecinos']), {**base, 'rut': '11111111-1'})
        self.assertContains(respuesta, 'Ya existe un vecino registrado con este RUT')
        respuesta = self.client.post(reverse('mantenedor_nuevo', args=['vecinos']), {**base, 'rut': '11111111-2'})
        self.assertContains(respuesta, 'El RUT no es válido')
        self.assertEqual(Vecino.objects.count(), 2)

    def test_el_delegado_ve_y_modifica_solo_los_vecinos_de_su_delegacion(self):
        """CP-EVA-030 CU-26.1 Denegar acceso por ámbito (RF-055). Un vecino de otra delegación no existe para el delegado."""
        self.client.force_login(self.usuario_verificador)
        lista = self.client.get(reverse('mantenedor_lista', args=['vecinos']))
        self.assertContains(lista, '11111111-1')
        self.assertNotContains(lista, self.vecino_rural.rut)
        self.assertEqual(self.client.get(reverse('mantenedor_editar', args=['vecinos', self.vecino_rural.pk])).status_code, 404)
        self.assertTrue(Auditoria.objects.filter(evento='acceso_denegado', entidad='Vecino').exists())

    def test_la_busqueda_por_rut_entrega_los_datos_para_autocompletar(self):
        """CP-EVA-031 CU-02 Autocompletar datos del vecino (RF-062). Un RUT registrado devuelve nombre y teléfono."""
        self.client.force_login(self.usuario_autor)
        datos = self.client.get(reverse('vecino_buscar'), {'rut': '11.111.111-1'}).json()
        self.assertEqual((datos['encontrado'], datos['nombre'], datos['telefono']), (True, 'Ana Rojas', '+56 9 1111 1111'))
        self.assertEqual(self.client.get(reverse('vecino_buscar'), {'rut': rut_valido(22222222)}).json()['encontrado'], False)
        self.assertEqual(self.client.get(reverse('vecino_buscar'), {'rut': '123'}).json()['rut_valido'], False)

    def test_la_busqueda_de_vecinos_exige_permiso(self):
        """CP-EVA-032 CU-26.1 Denegar acceso por ámbito (RF-062). Sin permiso de ver vecinos responde 403."""
        usuario = User.objects.create_user('sin-perfil-e3', password=CLAVE_PRUEBA)
        self.client.force_login(usuario)
        self.assertEqual(self.client.get(reverse('vecino_buscar'), {'rut': '11111111-1'}).status_code, 403)

    def test_elegir_un_vecino_completa_la_tarea(self):
        """CP-EVA-033 CU-02 Autocompletar datos del vecino (RF-062). Con un vecino, RUT, nombre y teléfono vacíos se completan."""
        tarea = Compromiso(folio='AGR-E3-V', delegacion=self.centro, funcionario_responsable=self.autor, origen='externo', solicitante='',
                           territorio='Centro', descripcion='Poda', fecha_comprometida=timezone.localdate(), vecino=self.vecino)
        tarea.clean()
        self.assertEqual((tarea.solicitante, tarea.solicitante_rut, tarea.solicitante_telefono), ('Ana Rojas', '11111111-1', '+56 9 1111 1111'))

    def test_la_delegacion_del_vecino_es_la_de_su_territorio(self):
        """CP-EVA-034 CU-27 Mantener vecinos (RF-055). Sin duplicar la delegación: se deduce del territorio."""
        self.assertEqual(self.vecino.delegacion, self.centro)


class MembresiasHitosYCatalogosTests(EscenarioBase, TestCase):
    """Membresía y dirigencia en organizaciones, hitos con responsables, territorios y subtipos de atención."""

    def setUp(self):
        self.crear_escenario()
        self.territorio = Territorio.objects.create(nombre='Casco histórico', delegacion=self.centro)
        self.junta = Organizacion.objects.create(nombre='JV Centro', tipo='junta_vecinos', delegacion=self.centro)
        self.ana = Vecino.objects.create(rut=rut_valido(11111111), nombres='Ana', apellidos='Rojas', territorio=self.territorio)
        self.beto = Vecino.objects.create(rut=rut_valido(12121212), nombres='Beto', apellidos='Díaz', territorio=self.territorio)
        self.coordinador = crear_funcionario('coord-mh', 'coordinador', cargo=self.cargo)

    def test_la_presidencia_es_unica_en_cada_periodo(self):
        """CP-EVA-035 CU-27.1 Membresía y dirigencia (RF-056). No hay dos presidentes vigentes a la vez."""
        MembresiaOrganizacion.objects.create(vecino=self.ana, organizacion=self.junta, cargo='presidente', fecha_inicio=date(2026, 1, 1))
        otra = MembresiaOrganizacion(vecino=self.beto, organizacion=self.junta, cargo='presidente', fecha_inicio=date(2026, 6, 1))
        with self.assertRaises(ValidationError):
            otra.full_clean()
        otra.cargo = 'socio'
        otra.full_clean()  # como socio sí puede

    def test_un_vecino_no_tiene_dos_membresias_traslapadas(self):
        """CP-EVA-036 CU-27.1 Membresía y dirigencia (RF-056). La misma persona no se inscribe dos veces en las mismas fechas."""
        MembresiaOrganizacion.objects.create(vecino=self.ana, organizacion=self.junta, fecha_inicio=date(2026, 1, 1), fecha_termino=date(2026, 6, 30))
        with self.assertRaises(ValidationError):
            MembresiaOrganizacion(vecino=self.ana, organizacion=self.junta, fecha_inicio=date(2026, 6, 1)).full_clean()
        MembresiaOrganizacion(vecino=self.ana, organizacion=self.junta, fecha_inicio=date(2026, 7, 1)).full_clean()

    def test_el_termino_no_puede_ser_anterior_al_inicio(self):
        """CP-EVA-037 CU-27.1 Membresía y dirigencia (RF-056). Validación en el modelo y restricción CHECK en la base."""
        with self.assertRaises(ValidationError):
            MembresiaOrganizacion(vecino=self.ana, organizacion=self.junta, fecha_inicio=date(2026, 5, 1), fecha_termino=date(2026, 4, 1)).full_clean()
        with self.assertRaises(IntegrityError), transaction.atomic():
            MembresiaOrganizacion.objects.create(vecino=self.ana, organizacion=self.junta, fecha_inicio=date(2026, 5, 1), fecha_termino=date(2026, 4, 1))

    def test_un_hito_se_crea_con_responsable_principal_y_apoyo(self):
        """CP-EVA-038 CU-27 Hitos con responsables (RF-057). El formulario guarda un principal y los apoyos."""
        self.client.force_login(self.coordinador)
        self.client.post(reverse('mantenedor_nuevo', args=['hitos']), {
            'nombre': 'Operativo de invierno', 'descripcion': '', 'delegacion': self.centro.pk, 'territorio': self.territorio.pk,
            'fecha_programada': '2026-12-01', 'estado': 'planificado', 'fecha_realizacion': '',
            'responsable_principal': self.verificador.pk, 'responsables_apoyo': [self.autor.pk],
        })
        hito = Hito.objects.get(nombre='Operativo de invierno')
        self.assertEqual(dict(hito.asignaciones.values_list('funcionario_id', 'rol')), {self.verificador.pk: 'principal', self.autor.pk: 'apoyo'})

    def test_un_responsable_de_otra_delegacion_se_rechaza(self):
        """CP-EVA-039 CU-27.1 Hitos con responsables (RF-057). Los responsables son de la delegación del hito."""
        ajeno = crear_funcionario('rural-hito', 'funcionario', cargo=self.cargo, delegacion=self.rural).funcionario
        self.client.force_login(self.coordinador)
        respuesta = self.client.post(reverse('mantenedor_nuevo', args=['hitos']), {
            'nombre': 'Hito ajeno', 'delegacion': self.centro.pk, 'fecha_programada': '2026-12-01', 'estado': 'planificado',
            'responsable_principal': ajeno.pk,
        })
        self.assertContains(respuesta, 'pertenece a la delegación Rural')
        self.assertFalse(Hito.objects.filter(nombre='Hito ajeno').exists())

    def test_un_hito_realizado_exige_su_fecha(self):
        """CP-EVA-040 CU-27.1 Hitos con responsables (RF-057). Realizado sin fecha de realización no se guarda."""
        with self.assertRaises(ValidationError):
            Hito(nombre='H', delegacion=self.centro, fecha_programada=date(2026, 9, 1), estado='realizado').full_clean()

    def test_el_territorio_es_unico_en_su_delegacion(self):
        """CP-EVA-041 CU-27.1 Restringir elemento duplicado (RF-055). El mismo nombre en la misma delegación es duplicado."""
        self.client.force_login(self.coordinador)
        respuesta = self.client.post(reverse('mantenedor_nuevo', args=['territorios']), {'nombre': 'Casco  histórico', 'delegacion': self.centro.pk, 'activo': 'on'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Territorio.objects.filter(delegacion=self.centro).count(), 1)
        Territorio.objects.create(nombre='Casco histórico', delegacion=self.rural)  # en otra delegación sí

    def test_el_delegado_no_crea_territorios(self):
        """CP-EVA-042 CU-26.1 Denegar acceso por ámbito (RF-055). Crear territorios es de coordinación."""
        self.client.force_login(self.usuario_verificador)
        self.assertEqual(self.client.get(reverse('mantenedor_nuevo', args=['territorios'])).status_code, 404)
        self.assertEqual(self.client.get(reverse('mantenedor_lista', args=['territorios'])).status_code, 200)

    def test_el_subtipo_debe_ser_del_tipo_de_atencion_elegido(self):
        """CP-EVA-043 CU-01.1 Validar campos de actividad (RF-058). Un subtipo de otro tipo de atención se rechaza."""
        fijar_hoy(self, FECHA_HOY)
        otro_tipo = Catalogo.objects.create(codigo='AT-OTRO', nombre='Otro', tipo='atencion')
        ajeno = SubtipoAtencion.objects.create(tipo=otro_tipo, nombre='Alumbrado')
        propio = SubtipoAtencion.objects.create(tipo=self.catalogo, nombre='Poda')
        actividad = self.nueva_actividad()
        actividad.subtipo_atencion = ajeno
        with self.assertRaises(ValidationError):
            actividad.full_clean()
        actividad.subtipo_atencion = propio
        actividad.full_clean()

    def test_un_subtipo_solo_cuelga_de_un_tipo_de_atencion(self):
        """CP-EVA-044 CU-27.1 Tipos y subtipos de atención (RF-058). No se cuelga de un servicio del catálogo."""
        servicio = Catalogo.objects.create(codigo='SRV-X', nombre='Servicio', tipo='servicio')
        with self.assertRaises(ValidationError):
            SubtipoAtencion(tipo=servicio, nombre='X').full_clean()

    def test_la_meta_de_un_funcionario_no_se_duplica(self):
        """CP-EVA-045 CU-05.1 Validar parámetros de meta (RF-007). Un ítem se asigna una sola vez a cada funcionario."""
        Meta.objects.create(item=self.item, funcionario=self.autor, valor_objetivo=5)
        form = MetaForm({'item': self.item.pk, 'funcionario': self.autor.pk, 'valor_objetivo': 3, 'unidad': 'actividades', 'ponderador': 100})
        self.assertFalse(form.is_valid())
        with self.assertRaises(IntegrityError), transaction.atomic():
            Meta.objects.create(item=self.item, funcionario=self.autor, valor_objetivo=3)

    def test_la_organizacion_y_su_territorio_son_de_la_misma_delegacion(self):
        """CP-EVA-046 CU-27.1 Membresía y dirigencia (RF-056). El territorio de una junta es de su delegación."""
        self.junta.unidad_territorial = Territorio.objects.create(nombre='Algarrobito', delegacion=self.rural)
        with self.assertRaises(ValidationError):
            self.junta.full_clean()

    def test_los_perfiles_reciben_los_permisos_de_las_tablas_nuevas(self):
        """CP-EVA-047 CU-26 Perfiles y permisos (RF-002). Coordinación administra; delegado y profesional según su función."""
        permisos = {g.name: set(g.permissions.values_list('codename', flat=True)) for g in Group.objects.all()}
        self.assertTrue({'add_territorio', 'delete_vecino', 'change_hito'} <= permisos['Coordinador'])
        self.assertTrue({'add_vecino', 'add_hito', 'add_membresiaorganizacion'} <= permisos['Delegado'])
        self.assertNotIn('add_territorio', permisos['Delegado'])
        self.assertTrue({'view_vecino', 'add_vecino', 'view_casosocial'} <= permisos['Profesional'])
        self.assertNotIn('delete_vecino', permisos['Profesional'])


class IngresoAlTuboTests(EscenarioBase, TestCase):
    """Una actividad o gestión social puede ingresar o no al Tubo."""

    def setUp(self):
        self.crear_escenario()
        fijar_hoy(self, FECHA_HOY)
        self.client.force_login(self.usuario_autor)

    def _datos_actividad(self, **extra):
        datos = {
            'delegacion': self.centro.pk, 'lugar': 'Plaza', 'item': self.item.pk, 'catalogo': self.catalogo.pk, 'fecha': '2026-09-10T10:00',
            'solicitud_problema': 'Luminaria apagada', 'accion': 'Se deriva', 'contacto_nombre': 'Ana Rojas', 'contacto_telefono': '912345678',
            'tipo_accion': 'ejecucion',
        }
        datos.update(extra)
        return datos

    def test_una_actividad_marcada_ingresa_al_tubo(self):
        """CP-EVA-048 CU-01 Ingresar actividad al Tubo (RF-059, RF-020). Se crea la tarea vinculada con los datos ya ingresados."""
        self.client.post(reverse('actividad_nueva'), self._datos_actividad(ingresar_al_tubo='on', plazo_tubo='2026-09-20'))
        actividad = Actividad.objects.get(solicitud_problema='Luminaria apagada')
        tarea = actividad.compromiso
        self.assertIsNotNone(tarea)
        self.assertEqual((tarea.solicitante, tarea.solicitante_telefono, tarea.fecha_comprometida, tarea.funcionario_responsable),
                         ('Ana Rojas', '912345678', date(2026, 9, 20), self.autor))
        self.assertEqual(tarea.historial.count(), 1)

    def test_una_actividad_sin_marcar_no_ingresa_al_tubo(self):
        """CP-EVA-049 CU-01 Ingresar actividad al Tubo (RF-059). Sin marcar, no se crea ninguna tarea."""
        self.client.post(reverse('actividad_nueva'), self._datos_actividad())
        self.assertIsNone(Actividad.objects.get(solicitud_problema='Luminaria apagada').compromiso)
        self.assertFalse(Compromiso.objects.exists())

    def test_una_gestion_social_puede_ingresar_al_tubo(self):
        """CP-EVA-050 CU-03 Registrar atención social (RF-059, RF-015). Marcada, crea la tarea; sin marcar, no."""
        base = {'nombre_usuario': 'Ana Rojas', 'telefono_usuario': '912345678', 'etapa': 1, 'tipo': 'pgu', 'subtipo': '', 'observacion': ''}
        self.client.post(reverse('caso_social_nuevo'), {**base, 'ingresar_al_tubo': 'on'})
        self.client.post(reverse('caso_social_nuevo'), {**base, 'etapa': 2})
        con_tubo, sin_tubo = CasoSocial.objects.order_by('etapa')
        self.assertIsNotNone(con_tubo.compromiso)
        self.assertEqual(con_tubo.compromiso.delegacion, self.centro)
        self.assertIsNone(sin_tubo.compromiso)
        self.assertContains(self.client.get(reverse('casos_sociales')), con_tubo.compromiso.folio)

    def test_la_gestion_social_autocompleta_desde_el_vecino(self):
        """CP-EVA-051 CU-03 Autocompletar datos del vecino (RF-062). Con vecino, nombre y teléfono se completan; sin ambos, error."""
        territorio = Territorio.objects.create(nombre='Casco', delegacion=self.centro)
        vecino = Vecino.objects.create(rut=rut_valido(11111111), nombres='Ana', apellidos='Rojas', telefono='912345678', territorio=territorio)
        self.client.post(reverse('caso_social_nuevo'), {'vecino': vecino.pk, 'nombre_usuario': '', 'telefono_usuario': '', 'etapa': 1, 'tipo': 'pgu'})
        caso = CasoSocial.objects.get()
        self.assertEqual((caso.nombre_usuario, caso.telefono_usuario), ('Ana Rojas', '912345678'))
        respuesta = self.client.post(reverse('caso_social_nuevo'), {'nombre_usuario': '', 'telefono_usuario': '', 'etapa': 1, 'tipo': 'pgu'})
        self.assertContains(respuesta, 'Este campo es obligatorio')

    def test_solo_el_autor_modifica_su_gestion_social(self):
        """CP-EVA-052 CU-26.1 Denegar acceso por ámbito (RF-015). Otro profesional no modifica la gestión ajena."""
        caso = CasoSocial.objects.create(funcionario=self.autor, nombre_usuario='Ana', telefono_usuario='912345678', tipo='pgu')
        otro = crear_funcionario('otro-cs', 'funcionario', cargo=self.cargo, delegacion=self.centro)
        self.client.force_login(otro)
        self.assertEqual(self.client.get(reverse('caso_social_editar', args=[caso.pk])).status_code, 404)
        self.client.force_login(self.usuario_autor)
        self.client.post(reverse('caso_social_editar', args=[caso.pk]), {'nombre_usuario': 'Ana María', 'telefono_usuario': '912345678', 'etapa': 1, 'tipo': 'pgu'})
        self.assertEqual(CasoSocial.objects.get(pk=caso.pk).nombre_usuario, 'Ana María')


class DashboardTests(EscenarioBase, TestCase):
    """Dashboard con gráficos y semáforo por funcionario y por delegación."""

    def setUp(self):
        self.crear_escenario()
        fijar_hoy(self, FECHA_HOY)
        self.coordinador = crear_funcionario('coord-dash', 'coordinador', cargo=self.cargo)
        self.meta = Meta.objects.create(item=self.item, funcionario=self.autor, valor_objetivo=2)
        actividad = self.nueva_actividad(contacto_nombre='Ana', contacto_telefono='912345678')
        Validacion(evidencia=self.nueva_evidencia(actividad), funcionario_verificador=self.verificador).aprobar_evidencia()
        actividad.actualizar_indicadores()
        self.nuevo_compromiso(folio='AGR-D-1')
        self.nuevo_compromiso(folio='AGR-D-2', dias=-3)
        self.rural_tarea = self.nuevo_compromiso(folio='AGR-D-R', delegacion=self.rural,
                                                 funcionario_responsable=crear_funcionario('rural-d', 'delegado', cargo=self.cargo, delegacion=self.rural).funcionario)

    def test_el_dashboard_muestra_los_cinco_graficos(self):
        """CP-EVA-053 CU-18 Dashboard con gráficos (RF-060, RF-029). Cumplimiento, semáforo, compromisos, carga y tendencia."""
        self.client.force_login(self.coordinador)
        respuesta = self.client.get(reverse('tablero_analitico'), {'desde': '2026-09-01', 'hasta': '2026-09-30'})
        for titulo in ('Cumplimiento por delegación', 'Semáforo por funcionario', 'Estado de los compromisos', 'Carga de trabajo', 'Tendencia semanal'):
            self.assertContains(respuesta, titulo)
        self.assertContains(respuesta, 'Ver datos en tabla')
        self.assertContains(respuesta, '<svg class="viz-lineas"')

    def test_el_delegado_ve_solo_su_delegacion(self):
        """CP-EVA-054 CU-20.2 Restringir por ámbito de permisos (RF-060). El delegado no ve otras delegaciones en el dashboard."""
        self.client.force_login(self.usuario_verificador)
        respuesta = self.client.get(reverse('tablero_analitico'))
        self.assertEqual([fila['nombre'] for fila in respuesta.context['estado_compromisos']], ['Centro'])
        respuesta = self.client.get(reverse('tablero_analitico'), {'delegacion': self.rural.pk})
        self.assertEqual([fila['nombre'] for fila in respuesta.context['estado_compromisos']], ['Centro'])

    def test_el_filtro_por_funcionario_restringe_la_carga(self):
        """CP-EVA-055 CU-18.1 Consolidar datos de delegación (RF-060, RF-032). Filtrar por funcionario deja solo su carga."""
        self.client.force_login(self.coordinador)
        respuesta = self.client.get(reverse('tablero_analitico'), {'funcionario': self.autor.pk, 'desde': '2026-09-01', 'hasta': '2026-09-30'})
        self.assertEqual([fila['nombre'] for fila in respuesta.context['carga']], [self.autor.nombre])
        self.assertEqual(respuesta.context['actividades_aprobadas'], 1)

    def test_estado_de_compromisos_calcula_porcentajes_y_vencidas(self):
        """CP-EVA-056 CU-14.1 Clasificar compromisos por vencimiento (RF-060, RF-021). Totales, % realizado y vencidas por delegación."""
        Compromiso.objects.filter(folio='AGR-D-1').update(estado='realizado')
        filas = {fila['nombre']: fila for fila in graficos.estado_de_compromisos(Compromiso.objects.all())}
        self.assertEqual((filas['Centro']['total'], filas['Centro']['vencidas'], filas['Centro']['pct_realizado']), (2, 1, Decimal('50.0')))
        self.assertEqual(sum(segmento['valor'] for segmento in filas['Centro']['segmentos']), 2)

    def test_la_tendencia_cuenta_registradas_y_aprobadas_por_semana(self):
        """CP-EVA-057 CU-17 Tendencia semanal (RF-060, RF-030). Una actividad aprobada cuenta en su semana en ambas series."""
        tendencia = graficos.tendencia_semanal(Actividad.objects.all(), date(2026, 9, 1), date(2026, 9, 30))
        semana = next(fila for fila in tendencia['filas'] if fila['semana'] == date(2026, 9, 7))
        self.assertEqual((semana['registradas'], semana['aprobadas']), (1, 1))
        self.assertEqual(tendencia['total_registradas'], 1)


class ProtocoloTests(TestCase):
    """El protocolo de pruebas solo referencia pruebas que existen y cubre todos los requerimientos de la guía."""

    def test_cada_caso_apunta_a_pruebas_existentes(self):
        """CP-EVA-058 CU-30 Trazabilidad del protocolo (RF-036). Un caso automatizado no puede citar una prueba inexistente."""
        import unittest
        from . import protocolo
        cargador = unittest.TestLoader()
        citadas = [p for caso in protocolo.CASOS for p in caso['pruebas']] + [p for d in protocolo.DEFECTOS for p in d['reejecucion']]
        for prueba in citadas:
            with self.subTest(prueba=prueba):
                suite = cargador.loadTestsFromName(prueba)
                self.assertEqual(suite.countTestCases(), 1)
                self.assertNotIn('_FailedTest', type(next(iter(suite))).__name__)
        self.assertEqual(set(protocolo.REQUERIMIENTOS), {caso['requerimiento'] for caso in protocolo.CASOS})
        self.assertEqual(set(protocolo.REQUERIMIENTOS), set(protocolo.PANTALLAS))
        for caso in protocolo.CASOS:
            self.assertTrue(caso['manual'] or caso['pruebas'], caso['codigo'])
            self.assertTrue(caso['pasos'] and caso['esperado'] and caso['precondiciones'], caso['codigo'])


class RespaldoTests(EscenarioBase, TestCase):
    """Respaldo y recuperación con el comando `respaldo`."""

    def setUp(self):
        self.crear_escenario()

    def test_el_respaldo_se_restaura_en_una_base_vacia(self):
        """CP-EVA-059 CU-30 Respaldo y recuperación (RNF-012). El .zip trae datos y archivos, y loaddata los recupera."""
        import json
        import tempfile
        import zipfile
        from pathlib import Path
        from django.core.management import call_command
        territorio = Territorio.objects.create(nombre='Casco', delegacion=self.centro)
        Vecino.objects.create(rut=rut_valido(11111111), nombres='Ana', apellidos='Rojas', territorio=territorio)
        carpeta = Path(tempfile.mkdtemp())
        call_command('respaldo', destino=str(carpeta), stdout=open(carpeta / 'salida.txt', 'w'))
        archivo = next(carpeta.glob('sgr_*.zip'))
        with zipfile.ZipFile(archivo) as zip_respaldo:
            datos = zip_respaldo.read('datos.json').decode('utf-8')
        modelos = {fila['model'] for fila in json.loads(datos)}
        self.assertTrue({'delegaciones_app.vecino', 'delegaciones_app.territorio', 'auth.user'} <= modelos)
        Vecino.objects.all().delete()
        (carpeta / 'datos.json').write_text(datos, encoding='utf-8')
        call_command('loaddata', str(carpeta / 'datos.json'), verbosity=0)
        self.assertEqual(Vecino.objects.get().rut, rut_valido(11111111))
