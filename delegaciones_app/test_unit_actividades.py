"""Pruebas unitarias del registro de actividades, la carga de evidencias y su validación (EP-01 y EP-03)."""
from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone

from .forms import ActividadForm, EvidenciaForm
from .informes import filtrar_actividades
from .models import Actividad, Cargo, Catalogo, Evidencia, Indicador, ItemMedible, Meta, Validacion, validar_tamano_evidencia
from .pruebas_base import EscenarioBase, crear_funcionario


class ActividadUnitTests(EscenarioBase, TestCase):
    """CU-01 Registro de actividades, CU-01.1 Validar campos y CU-10 Generación de códigos verificadores (RF-009 a RF-011)."""

    def setUp(self):
        self.crear_escenario()

    def _datos(self, **cambios):
        datos = {
            'delegacion': self.centro, 'item': self.item, 'catalogo': self.catalogo, 'fecha': self.fecha_valida,
            'solicitud_problema': 'Consulta vecinal', 'accion': 'Se orientó al vecino',
        }
        datos.update(cambios)
        return datos

    def test_registrar_actividad_guarda_con_codigo_y_estado_pendiente(self):
        """CU-01 Registro de actividades (RF-009). El registro válido queda pendiente de revisión con su código."""
        actividad = self.autor.registrar_actividad(self._datos())
        self.assertEqual(actividad.estado, 'pendiente')
        self.assertEqual(actividad.funcionario_autor, self.autor)
        self.assertTrue(Actividad.objects.filter(pk=actividad.pk).exists())

    def test_registrar_actividad_usa_la_delegacion_del_funcionario_si_falta(self):
        """CU-01 Registro de actividades (RF-009). Sin delegación indicada se usa la del autor."""
        datos = self._datos()
        del datos['delegacion']
        self.assertEqual(self.autor.registrar_actividad(datos).delegacion, self.centro)

    def test_registrar_actividad_invalida_no_guarda_nada(self):
        """CU-01.2 Gestionar error de validación (RF-010). Un registro con errores no se guarda."""
        with self.assertRaises(ValidationError) as error:
            self.autor.registrar_actividad(self._datos(solicitud_problema=''))
        self.assertIn('solicitud_problema', error.exception.message_dict)
        self.assertFalse(Actividad.objects.exists())

    def test_los_campos_obligatorios_se_informan_por_nombre(self):
        """CU-01.2 Gestionar error de validación (RF-010). El error nombra cada campo faltante."""
        with self.assertRaises(ValidationError) as error:
            Actividad(funcionario_autor=self.autor, delegacion=self.centro, item=self.item).full_clean(exclude=['codigo_verificador'])
        self.assertTrue({'fecha', 'solicitud_problema', 'accion'} <= set(error.exception.message_dict))

    def test_la_fecha_debe_estar_dentro_del_periodo_del_item(self):
        """CU-01.1 Validar campos de actividad (RF-010). Una fecha fuera del período se rechaza."""
        fuera = timezone.make_aware(datetime(2026, 10, 2, 9, 0))
        with self.assertRaises(ValidationError) as error:
            self.autor.registrar_actividad(self._datos(fecha=fuera))
        self.assertIn('fecha', error.exception.message_dict)

    def test_los_limites_del_periodo_son_validos(self):
        """CU-01.1 Validar campos de actividad (RF-010). El primer y el último día del período se aceptan."""
        for dia in (datetime(2026, 9, 1, 0, 0), datetime(2026, 9, 30, 23, 59)):
            self.autor.registrar_actividad(self._datos(fecha=timezone.make_aware(dia), solicitud_problema=f'Día {dia:%d}'))
        self.assertEqual(Actividad.objects.count(), 2)

    def test_no_se_registra_en_un_periodo_cerrado(self):
        """CU-01.1 Validar campos de actividad (RF-038). RN-013: el ítem de un período cerrado no admite actividades."""
        self.periodo.cerrar_periodo()
        with self.assertRaises(ValidationError):
            self.autor.registrar_actividad(self._datos())

    def test_el_telefono_de_contacto_debe_tener_un_formato_valido(self):
        """CU-01.1 Validar campos de actividad (RF-010). Dígitos, espacios, guiones y paréntesis; + o paréntesis inicial opcional."""
        for valido in ('+56 9 1234 5678', '(51) 2 123456', '912345678', '51-2-123456'):
            self.autor.registrar_actividad(self._datos(contacto_telefono=valido, solicitud_problema=f'Tel {valido}'))
        for invalido in ('abc', '12345', '+56 9 1234 5678 9999 0000', '9123-45x', '++56912345678'):
            with self.assertRaises(ValidationError, msg=invalido) as error:
                self.autor.registrar_actividad(self._datos(contacto_telefono=invalido, solicitud_problema='Tel inválido'))
            self.assertIn('contacto_telefono', error.exception.message_dict, invalido)

    def test_el_telefono_es_opcional(self):
        """CU-01.1 Validar campos de actividad (RF-010). Sin teléfono el registro es válido."""
        for vacio in (None, ''):
            self.autor.registrar_actividad(self._datos(contacto_telefono=vacio, solicitud_problema=f'Sin teléfono {vacio!r}'))

    def test_el_codigo_verificador_tiene_formato_y_se_asigna_una_vez(self):
        """CU-10 Generación de códigos verificadores (RF-011). RN-010: formato EVD-fecha-sufijo y no se regenera."""
        actividad = Actividad(funcionario_autor=self.autor, delegacion=self.centro, item=self.item)
        codigo = actividad.generar_codigo_verificador()
        self.assertRegex(codigo, r'^EVD-\d{8}-[0-9A-F]{6}$')
        self.assertEqual(actividad.generar_codigo_verificador(), codigo)

    def test_dos_actividades_nunca_comparten_codigo(self):
        """CU-10 Generación de códigos verificadores (RF-011). Los códigos generados son únicos."""
        codigos = {self.nueva_actividad(solicitud_problema=f'A{n}').codigo_verificador for n in range(10)}
        self.assertEqual(len(codigos), 10)

    def test_el_codigo_verificador_no_se_puede_modificar(self):
        """CU-10 Generación de códigos verificadores (RF-011). RN-010: el código es inmutable."""
        actividad = self.nueva_actividad()
        original = actividad.codigo_verificador
        actividad.codigo_verificador = 'EVD-00000000-AAAAAA'
        with self.assertRaises(ValidationError):
            actividad.save()
        self.assertEqual(Actividad.objects.get(pk=actividad.pk).codigo_verificador, original)

    def test_buscar_por_codigo_encuentra_la_actividad(self):
        """CU-10.1 Buscar actividad por código (RF-032). La búsqueda por código devuelve su actividad."""
        actividad = self.nueva_actividad()
        otra = self.nueva_actividad(solicitud_problema='Otra')
        encontradas = filtrar_actividades(Actividad.objects.all(), {'q': actividad.codigo_verificador})
        self.assertEqual(list(encontradas), [actividad])
        self.assertNotIn(otra, encontradas)

    def test_buscar_un_codigo_inexistente_no_devuelve_nada(self):
        """CU-10.2 Consulta sin coincidencias (RF-032). Un código sin registros da un resultado vacío."""
        self.nueva_actividad()
        self.assertFalse(filtrar_actividades(Actividad.objects.all(), {'q': 'EVD-00000000-ZZZZZZ'}).exists())


class ActividadEstadoUnitTests(EscenarioBase, TestCase):
    """CU-11 Validación de actividades y CU-23.1 Controlar conflicto de concurrencia (RF-013, RF-014, RF-034)."""

    def setUp(self):
        self.crear_escenario()

    def test_cambiar_estado_rechaza_un_estado_inexistente(self):
        """CU-11 Validación de actividades (RF-013). Solo existen los estados definidos."""
        actividad = self.nueva_actividad()
        with self.assertRaises(ValidationError):
            actividad.cambiar_estado('inventado')
        self.assertEqual(Actividad.objects.get(pk=actividad.pk).estado, 'pendiente')

    def test_una_actividad_aprobada_no_cambia_de_estado(self):
        """CU-11.2 Bloquear aporte al avance (RF-014). RN-009: lo aprobado ya suma y solo se anula con motivo."""
        actividad = self.nueva_actividad(estado='aprobada')
        with self.assertRaises(ValidationError):
            actividad.cambiar_estado('rechazada')
        self.assertEqual(Actividad.objects.get(pk=actividad.pk).estado, 'aprobada')

    def test_anulando_si_se_puede_salir_de_aprobada(self):
        """CU-07.2 Recalcular por anulación de registro (RF-022). La anulación explícita sí cambia el estado."""
        actividad = self.nueva_actividad(estado='aprobada')
        actividad.cambiar_estado('rechazada', anulando=True)
        self.assertEqual(Actividad.objects.get(pk=actividad.pk).estado, 'rechazada')

    def test_dos_ediciones_simultaneas_la_segunda_se_rechaza(self):
        """CU-23.1 Controlar conflicto de concurrencia (RF-034). Gana el primero que guarda; el otro debe recargar."""
        primera = Actividad.objects.get(pk=self.nueva_actividad().pk)
        segunda = Actividad.objects.get(pk=primera.pk)
        primera.accion = 'Edición A'
        primera.save()
        segunda.accion = 'Edición B'
        with self.assertRaises(ValidationError) as error:
            segunda.save()
        self.assertIn('modificado por otro usuario', error.exception.messages[0])
        self.assertEqual(Actividad.objects.get(pk=primera.pk).accion, 'Edición A')

    def test_cada_guardado_sube_la_version_en_uno(self):
        """CU-23.1 Controlar conflicto de concurrencia (RF-034). La versión crece con cada edición."""
        actividad = self.nueva_actividad()
        self.assertEqual(actividad.version, 1)
        actividad.accion = 'Cambio'
        actividad.save()
        self.assertEqual((actividad.version, Actividad.objects.get(pk=actividad.pk).version), (2, 2))

    def test_el_formulario_rechaza_una_version_desactualizada(self):
        """CU-23.1 Controlar conflicto de concurrencia (RF-034). El campo oculto version detecta datos viejos."""
        actividad = self.nueva_actividad()
        usuario = self.usuario_autor
        datos = {
            'delegacion': self.centro.pk, 'item': self.item.pk, 'catalogo': self.catalogo.pk, 'fecha': '2026-09-10T10:00',
            'solicitud_problema': 'Editada', 'accion': 'Acción', 'version': actividad.version,
        }
        Actividad.objects.filter(pk=actividad.pk).update(version=actividad.version + 1)
        formulario = ActividadForm(datos, instance=Actividad.objects.get(pk=actividad.pk), user=usuario)
        self.assertFalse(formulario.is_valid())
        datos['version'] = actividad.version + 1
        formulario = ActividadForm(datos, instance=Actividad.objects.get(pk=actividad.pk), user=usuario)
        self.assertTrue(formulario.is_valid(), formulario.errors)


class ActividadFormUnitTests(EscenarioBase, TestCase):
    """CU-01.1 Validar campos de actividad y CU-01.2 Gestionar error de validación (RF-009, RF-010)."""

    def setUp(self):
        self.crear_escenario()

    def _datos(self, **cambios):
        datos = {
            'delegacion': self.centro.pk, 'item': self.item.pk, 'catalogo': self.catalogo.pk, 'fecha': '2026-09-10T10:00',
            'solicitud_problema': 'Consulta', 'accion': 'Orientación',
        }
        datos.update(cambios)
        return datos

    def test_un_formulario_completo_es_valido(self):
        """CU-01.1 Validar campos de actividad (RF-010). Con todos los datos obligatorios no hay errores."""
        formulario = ActividadForm(self._datos(), user=self.usuario_autor)
        self.assertTrue(formulario.is_valid(), formulario.errors)

    def test_cada_campo_obligatorio_se_informa(self):
        """CU-01.2 Gestionar error de validación (RF-010). Vacío cada obligatorio, el error apunta a ese campo."""
        for campo in ('item', 'catalogo', 'fecha', 'solicitud_problema', 'accion'):
            formulario = ActividadForm(self._datos(**{campo: ''}), user=self.usuario_autor)
            self.assertFalse(formulario.is_valid(), campo)
            self.assertIn(campo, formulario.errors, campo)

    def test_el_formato_de_fecha_invalido_se_informa(self):
        """CU-01.2 Gestionar error de validación (RF-010). Una fecha mal escrita no se guarda."""
        formulario = ActividadForm(self._datos(fecha='ayer a las diez'), user=self.usuario_autor)
        self.assertFalse(formulario.is_valid())
        self.assertIn('fecha', formulario.errors)

    def test_un_telefono_invalido_se_informa_en_el_formulario(self):
        """CU-01.2 Gestionar error de validación (RF-010). El error del teléfono aparece en su campo."""
        formulario = ActividadForm(self._datos(contacto_telefono='no es teléfono'), user=self.usuario_autor)
        self.assertFalse(formulario.is_valid())
        self.assertIn('contacto_telefono', formulario.errors)

    def test_solo_se_ofrecen_items_de_periodos_abiertos_y_del_cargo_del_usuario(self):
        """CU-01.1 Validar campos de actividad (RF-009). Los ítems de otro cargo o de períodos cerrados no aparecen."""
        otro_cargo = Cargo.objects.create(nombre='Técnico')
        ajeno = ItemMedible.objects.create(cargo=otro_cargo, periodo=self.periodo, nombre='Ajeno', ponderacion=100)
        formulario = ActividadForm(user=self.usuario_autor)
        self.assertIn(self.item, formulario.fields['item'].queryset)
        self.assertNotIn(ajeno, formulario.fields['item'].queryset)

    def test_solo_se_ofrecen_tipos_de_atencion_activos(self):
        """CU-27 Administración de catálogos (RF-004). Un tipo desactivado no se puede elegir en registros nuevos."""
        inactivo = Catalogo.objects.create(codigo='AT-OFF', nombre='Desactivado', tipo='atencion', activo=False)
        servicio = Catalogo.objects.create(codigo='SV-1', nombre='Servicio', tipo='servicio')
        formulario = ActividadForm(user=self.usuario_autor)
        self.assertIn(self.catalogo, formulario.fields['catalogo'].queryset)
        self.assertNotIn(inactivo, formulario.fields['catalogo'].queryset)
        self.assertNotIn(servicio, formulario.fields['catalogo'].queryset)

    def test_quien_tiene_delegacion_solo_registra_en_la_suya(self):
        """CU-26.1 Denegar acceso por ámbito (RF-002). El formulario no ofrece delegaciones ajenas."""
        formulario = ActividadForm(user=self.usuario_autor)
        self.assertEqual(list(formulario.fields['delegacion'].queryset), [self.centro])
        rechazada = ActividadForm(self._datos(delegacion=self.rural.pk), user=self.usuario_autor)
        self.assertFalse(rechazada.is_valid())
        self.assertIn('delegacion', rechazada.errors)


class EvidenciaUnitTests(EscenarioBase, TestCase):
    """CU-09 Registro de evidencia fotográfica, CU-09.1 Validar archivo y CU-09.2 Rechazar carga inválida (RF-012, RNF-017)."""

    def setUp(self):
        self.crear_escenario()
        self.actividad = self.nueva_actividad()

    def _archivo(self, nombre='respaldo.pdf', contenido=b'%PDF-1.4 prueba'):
        return SimpleUploadedFile(nombre, contenido)

    def test_subir_evidencia_vincula_el_archivo_y_envia_a_revision(self):
        """CU-09 Registro de evidencia fotográfica (RF-012). La evidencia queda ligada a la actividad y pendiente."""
        evidencia = self.autor.subir_evidencia(self.actividad, self._archivo(), 'Foto del operativo')
        self.assertEqual((evidencia.actividad, evidencia.estado_revision, evidencia.funcionario_autor), (self.actividad, 'pendiente', self.autor))
        self.assertEqual(evidencia.metadatos, {'comentario': 'Foto del operativo'})
        self.assertTrue(evidencia.descargar_archivo())

    def test_el_codigo_de_evidencia_deriva_del_de_la_actividad(self):
        """CU-09 Registro de evidencia fotográfica (RF-012). Código de la actividad más un correlativo."""
        primera = self.nueva_evidencia(self.actividad)
        segunda = self.nueva_evidencia(self.actividad)
        self.assertEqual(primera.codigo_evidencia, f'{self.actividad.codigo_verificador}-01')
        self.assertEqual(segunda.codigo_evidencia, f'{self.actividad.codigo_verificador}-02')

    def test_el_codigo_de_evidencia_no_se_puede_modificar(self):
        """CU-09 Registro de evidencia fotográfica (RF-012). El código de la evidencia es inmutable."""
        evidencia = self.nueva_evidencia(self.actividad)
        evidencia.codigo_evidencia = 'OTRO-01'
        with self.assertRaises(ValidationError):
            evidencia.save()

    def test_formatos_permitidos(self):
        """CU-09.1 Validar archivo de evidencia (RF-012). JPG, JPEG, PNG y PDF se aceptan, sin importar mayúsculas."""
        for nombre in ('a.jpg', 'a.jpeg', 'a.png', 'a.pdf', 'FOTO.JPG'):
            Evidencia(actividad=self.actividad, funcionario_autor=self.autor, archivo_vinculo=self._archivo(nombre)).full_clean(exclude=['codigo_evidencia'])

    def test_formatos_no_permitidos_se_rechazan(self):
        """CU-09.2 Rechazar carga inválida (RF-012). Ejecutables, documentos y archivos sin extensión no entran."""
        for nombre in ('virus.exe', 'texto.txt', 'planilla.xlsx', 'sin_extension', 'doble.pdf.exe'):
            with self.assertRaises(ValidationError, msg=nombre) as error:
                Evidencia(actividad=self.actividad, funcionario_autor=self.autor, archivo_vinculo=self._archivo(nombre)).full_clean(exclude=['codigo_evidencia'])
            self.assertIn('archivo_vinculo', error.exception.message_dict, nombre)

    @override_settings(EVIDENCIA_TAMANO_MAXIMO_MB=1)
    def test_el_limite_de_tamano_es_configurable(self):
        """CU-09.2 Rechazar carga inválida (RNF-017). El motivo indica el peso y el máximo permitido."""
        validar_tamano_evidencia(self._archivo(contenido=b'0' * 1024 * 1024))
        with self.assertRaises(ValidationError) as error:
            validar_tamano_evidencia(self._archivo(contenido=b'0' * (1024 * 1024 + 1)))
        self.assertIn('máximo permitido es 1 MB', error.exception.messages[0])

    def test_el_formulario_exige_un_archivo(self):
        """CU-09.1 Validar archivo de evidencia (RF-012). Sin archivo no hay carga."""
        formulario = EvidenciaForm({}, {})
        self.assertFalse(formulario.is_valid())
        self.assertIn('archivo_vinculo', formulario.errors)

    def test_el_formulario_rechaza_una_extension_no_permitida(self):
        """CU-09.2 Rechazar carga inválida (RF-012). El motivo exacto del rechazo se informa."""
        formulario = EvidenciaForm({}, {'archivo_vinculo': self._archivo('malo.exe')})
        self.assertFalse(formulario.is_valid())
        self.assertIn('exe', str(formulario.errors['archivo_vinculo']))

    def test_reemplazar_archivo_vuelve_a_revision(self):
        """CU-11 Validación de actividades (RF-013). Un archivo nuevo debe revisarse de nuevo."""
        evidencia = self.autor.subir_evidencia(self.actividad, self._archivo())
        Validacion(evidencia=evidencia, funcionario_verificador=self.verificador).rechazar_evidencia('Foto borrosa')
        evidencia.refresh_from_db()
        evidencia.reemplazar_archivo(self._archivo('nueva.pdf'))
        evidencia.refresh_from_db()
        self.actividad.refresh_from_db()
        self.assertEqual((evidencia.estado_revision, self.actividad.estado), ('pendiente', 'pendiente'))

    def test_enviar_a_revision_no_reabre_una_actividad_aprobada(self):
        """CU-11.2 Bloquear aporte al avance (RF-014). Lo ya aprobado no vuelve a pendiente."""
        aprobada = self.nueva_actividad(estado='aprobada', solicitud_problema='Ya aprobada')
        evidencia = self.nueva_evidencia(aprobada)
        evidencia.enviar_a_revision()
        aprobada.refresh_from_db()
        self.assertEqual(aprobada.estado, 'aprobada')


class ValidacionUnitTests(EscenarioBase, TestCase):
    """CU-11 Validación de actividades, CU-11.1 Registrar trazabilidad de decisión y CU-11.2 Bloquear aporte al avance (RF-013, RF-014)."""

    def setUp(self):
        self.crear_escenario()
        self.actividad = self.nueva_actividad()
        self.evidencia = self.nueva_evidencia(self.actividad)

    def _validacion(self):
        return Validacion(evidencia=self.evidencia, funcionario_verificador=self.verificador)

    def test_aprobar_marca_la_evidencia_y_la_actividad(self):
        """CU-11 Validación de actividades (RF-013). La aprobación se refleja en ambas."""
        self._validacion().aprobar_evidencia('Conforme')
        self.evidencia.refresh_from_db()
        self.actividad.refresh_from_db()
        self.assertEqual((self.evidencia.estado_revision, self.actividad.estado), ('aprobada', 'aprobada'))

    def test_la_decision_deja_verificador_fecha_resultado_y_observacion(self):
        """CU-11.1 Registrar trazabilidad de decisión (RF-013). Quién, cuándo, qué decidió y por qué."""
        antes = timezone.now()
        validacion = self._validacion().aprobar_evidencia('Conforme')
        validacion.refresh_from_db()
        self.assertEqual((validacion.funcionario_verificador, validacion.decision, validacion.observacion), (self.verificador, 'aprobada', 'Conforme'))
        self.assertGreaterEqual(validacion.fecha, antes)

    def test_cada_revision_incrementa_el_numero_de_version(self):
        """CU-11.1 Registrar trazabilidad de decisión (RF-013). Primera, segunda revisión, y así."""
        primera = self._validacion().rechazar_evidencia('Falta foto')
        self.evidencia.refresh_from_db()
        segunda = self._validacion().aprobar_evidencia()
        self.assertEqual((primera.version, segunda.version), (1, 2))
        self.assertEqual(self.evidencia.validaciones.count(), 2)

    def test_rechazar_exige_un_motivo_y_no_aporta_al_avance(self):
        """CU-11.2 Bloquear aporte al avance (RF-014). Sin motivo no hay rechazo; con él la actividad queda rechazada."""
        for vacio in (None, '', '   '):
            with self.assertRaises(ValidationError):
                self._validacion().rechazar_evidencia(vacio)
        self.assertFalse(Validacion.objects.exists())
        self._validacion().rechazar_evidencia('Foto ilegible')
        self.actividad.refresh_from_db()
        self.assertEqual(self.actividad.estado, 'rechazada')
        self.assertEqual(Validacion.objects.get().observacion, 'Foto ilegible')

    def test_la_revision_solo_aprueba_o_rechaza(self):
        """CU-11 Validación de actividades (RF-013). Ya no existe «Solicitar corrección»: solo aprobar o rechazar."""
        self.assertFalse(hasattr(Validacion, 'solicitar_correccion'))
        self.assertEqual([valor for valor, _ in Validacion.DECISIONES], ['aprobada', 'rechazada'])
        self.assertNotIn('correccion', dict(Actividad.ESTADOS))
        self.assertNotIn('correccion', dict(Evidencia.ESTADOS_REVISION))

    def test_solo_las_actividades_aprobadas_cuentan_para_la_meta(self):
        """CU-11.2 Bloquear aporte al avance (RF-014). RN-009: rechazada no suma."""
        meta = Meta.objects.create(item=self.item, funcionario=self.autor, valor_objetivo=5)
        self._validacion().rechazar_evidencia('No sirve')
        self.assertEqual(meta.actividades_que_aportan().count(), 0)
        otra = self.nueva_actividad(solicitud_problema='Buena')
        Validacion(evidencia=self.nueva_evidencia(otra), funcionario_verificador=self.verificador).aprobar_evidencia()
        self.assertEqual(list(meta.actividades_que_aportan()), [otra])

    def test_una_aprobacion_recalcula_los_indicadores_de_la_meta(self):
        """CU-06.1 Recalcular indicadores automáticamente (RF-022). Aprobar una actividad deja un indicador nuevo."""
        meta = Meta.objects.create(item=self.item, funcionario=self.autor, valor_objetivo=4)
        self._validacion().aprobar_evidencia()
        self.actividad.refresh_from_db()
        indicadores = self.actividad.actualizar_indicadores()
        self.assertEqual(len(indicadores), 1)
        self.assertEqual((indicadores[0].avance, indicadores[0].cumplimiento), (1, 25))
        self.assertEqual(Indicador.objects.filter(meta=meta).count(), 1)

    def test_con_el_periodo_cerrado_los_indicadores_no_se_recalculan(self):
        """CU-28.1 Restricción por período cerrado (RF-038). RN-013: un período cerrado queda congelado."""
        Meta.objects.create(item=self.item, funcionario=self.autor, valor_objetivo=4)
        self.periodo.cerrar_periodo()
        self.actividad.refresh_from_db()
        self.assertEqual(self.actividad.actualizar_indicadores(), [])
        self.assertFalse(Indicador.objects.exists())

    def test_anular_una_aprobacion_deja_sin_efecto_el_aporte(self):
        """CU-07.2 Recalcular por anulación de registro (RF-022). Con motivo, la actividad deja de sumar."""
        meta = Meta.objects.create(item=self.item, funcionario=self.autor, valor_objetivo=4)
        self._validacion().aprobar_evidencia()
        self.actividad.refresh_from_db()
        self.actividad.anular_aprobacion('Error de carga', self.verificador)
        self.assertEqual(meta.actividades_que_aportan().count(), 0)
        self.assertEqual(Indicador.objects.filter(meta=meta).latest('fecha_calculo', 'pk').avance, 0)
