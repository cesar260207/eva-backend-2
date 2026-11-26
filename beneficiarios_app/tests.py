"""Pruebas del módulo de beneficiarios (inscripción de menores en actividades de infancia).

Cubren las reglas del Google Form original y las que agrega el SGR: RUT con dígito verificador, un RUT por actividad
con el aviso «RUT ya ingresado por <unidad>», unidad tomada de la sesión, alcance por unidad, actividades cerradas,
verificación en vivo y exportación.
"""
from django.test import TestCase
from django.urls import reverse

from delegaciones_app.models import Auditoria, Delegacion, Organizacion
from delegaciones_app.pruebas_base import CLAVE_PRUEBA, crear_funcionario

from .alcance import unidades_de
from .models import Evento, Inscripcion, UnidadMunicipal, rut_canonico

URL_INSCRIBIR = reverse('beneficiarios:inscribir')
URL_LISTA = reverse('beneficiarios:inscripciones')


class BaseBeneficiarios(TestCase):
    def setUp(self):
        self.centro = Delegacion.objects.create(nombre='Centro')
        self.rural = Delegacion.objects.create(nombre='Rural')
        self.navidad = Evento.objects.get(tipo='navidad', anio=2026)  # creada por la migración 0002
        self.dia_nino = Evento.objects.create(tipo='dia_nino', anio=2027)
        self.jjvv = Organizacion.objects.create(nombre='JJ.VV. Villa El Sol')
        self.delegado_centro = crear_funcionario('delegado.centro', 'delegado', delegacion=self.centro)
        self.delegado_centro.email = 'delegado.centro@laserena.cl'
        self.delegado_centro.save()
        self.profesional_rural = crear_funcionario('prof.rural', 'funcionario', delegacion=self.rural)
        self.coordinador = crear_funcionario('coord.benef', 'coordinador')
        self.unidad_centro = UnidadMunicipal.objects.get(nombre='Delegación Centro')
        self.unidad_rural = UnidadMunicipal.objects.get(nombre='Delegación Rural')

    def entrar(self, usuario):
        self.client.login(username=usuario.username, password=CLAVE_PRUEBA)

    def datos(self, **cambios):
        datos = {
            'evento': self.navidad.pk, 'unidad': self.unidad_centro.pk, 'nombre': 'Ana  Pérez', 'rut': '12.345.678-5',
            'rango_edad': '6-8', 'genero': 'F', 'folio_rsh': '123456789', 'tramo_rsh': '40',
            'organizacion': self.jjvv.pk, 'organizacion_otra': '', 'telefono': '912345678',
        }
        datos.update(cambios)
        return datos

    def inscribir(self, usuario, **cambios):
        self.entrar(usuario)
        respuesta = self.client.post(URL_INSCRIBIR, self.datos(**cambios))
        if respuesta.status_code == 302:
            self.client.get(respuesta.url)  # consume el mensaje de éxito para que no aparezca en la prueba siguiente
        return respuesta


class DatosInicialesTests(BaseBeneficiarios):
    def test_migracion_crea_las_nueve_unidades_y_navidad_abierta(self):
        self.assertEqual(UnidadMunicipal.objects.count(), 9)
        for nombre in ('Gabinete', 'DIDECO', 'Departamento de la Familia', 'Delegación Las Compañías'):
            self.assertTrue(UnidadMunicipal.objects.filter(nombre=nombre).exists())
        self.assertTrue(self.navidad.inscripciones_abiertas)

    def test_perfiles_reciben_permisos(self):
        self.assertTrue(self.profesional_rural.has_perm('beneficiarios_app.add_inscripcion'))
        self.assertFalse(self.profesional_rural.has_perm('beneficiarios_app.delete_inscripcion'))
        self.assertTrue(self.coordinador.has_perm('beneficiarios_app.change_evento'))


class RutTests(TestCase):
    def test_rut_canonico_sin_puntos_ni_ceros_a_la_izquierda(self):
        self.assertEqual(rut_canonico('12.345.678-5'), '12345678-5')
        self.assertEqual(rut_canonico('09.876.543-3'), '9876543-3')
        self.assertEqual(rut_canonico('20.000.000-k'), '20000000-K')


class InscripcionTests(BaseBeneficiarios):
    def test_delegado_inscribe_con_su_unidad_y_su_correo(self):
        respuesta = self.inscribir(self.delegado_centro)
        self.assertRedirects(respuesta, URL_LISTA)
        inscripcion = Inscripcion.objects.get()
        self.assertEqual(inscripcion.unidad, self.unidad_centro)
        self.assertEqual(inscripcion.rut, '12345678-5')
        self.assertEqual(inscripcion.nombre, 'Ana Pérez')
        self.assertEqual(inscripcion.registrado_por, self.delegado_centro)
        self.assertEqual(inscripcion.correo_registro, 'delegado.centro@laserena.cl')
        self.assertTrue(Auditoria.objects.filter(evento='crear', entidad='Inscripcion', identificador_registro=str(inscripcion.pk)).exists())

    def test_unidad_de_la_delegacion_se_enlaza_sola(self):
        self.assertEqual(list(unidades_de(self.delegado_centro)), [self.unidad_centro])
        self.unidad_centro.refresh_from_db()
        self.assertEqual(self.unidad_centro.delegacion, self.centro)

    def test_rut_duplicado_avisa_que_unidad_lo_ingreso(self):
        self.inscribir(self.delegado_centro)
        respuesta = self.inscribir(self.profesional_rural, unidad=self.unidad_rural.pk, rut='12345678-5', nombre='Otro')
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'RUT ya ingresado por Delegación Centro')
        self.assertNotContains(respuesta, 'Ana Pérez')  # no revela el nombre del menor a otra unidad
        self.assertEqual(Inscripcion.objects.count(), 1)

    def test_rut_con_cero_inicial_es_el_mismo(self):
        self.inscribir(self.delegado_centro, rut='9876543-3')
        respuesta = self.inscribir(self.delegado_centro, rut='09.876.543-3')
        self.assertContains(respuesta, 'RUT ya ingresado por Delegación Centro')

    def test_mismo_rut_en_otra_actividad_se_permite(self):
        self.inscribir(self.delegado_centro)
        self.inscribir(self.delegado_centro, evento=self.dia_nino.pk)
        self.assertEqual(Inscripcion.objects.filter(rut='12345678-5').count(), 2)

    def test_rechaza_rut_invalido_telefono_y_folio(self):
        respuesta = self.inscribir(self.delegado_centro, rut='12345678-9', telefono='22123456', folio_rsh='ABC')
        form = respuesta.context['form']
        self.assertIn('rut', form.errors)
        self.assertIn('telefono', form.errors)
        self.assertIn('folio_rsh', form.errors)
        self.assertFalse(Inscripcion.objects.exists())

    def test_genero_otro_o_prefiero_no_decir(self):
        self.inscribir(self.delegado_centro, genero='N')
        self.assertEqual(Inscripcion.objects.get().get_genero_display(), 'Prefiero no decir')

    def test_telefono_con_prefijo_56_se_normaliza(self):
        self.inscribir(self.delegado_centro, telefono='+56 9 1234 5678')
        self.assertEqual(Inscripcion.objects.get().telefono, '912345678')

    def test_exige_organizacion_de_la_lista_u_otra(self):
        respuesta = self.inscribir(self.delegado_centro, organizacion='', organizacion_otra='')
        self.assertIn('organizacion', respuesta.context['form'].errors)
        self.inscribir(self.delegado_centro, organizacion='', organizacion_otra='Club deportivo Los Leones')
        self.assertEqual(Inscripcion.objects.get().organizacion_nombre, 'Club deportivo Los Leones')

    def test_no_puede_inscribir_a_nombre_de_otra_unidad(self):
        respuesta = self.inscribir(self.delegado_centro, unidad=self.unidad_rural.pk)
        self.assertIn('unidad', respuesta.context['form'].errors)

    def test_actividad_cerrada_no_recibe_inscripciones(self):
        self.navidad.inscripciones_abiertas = False
        self.navidad.save()
        respuesta = self.inscribir(self.delegado_centro, evento=self.dia_nino.pk)
        self.assertRedirects(respuesta, URL_LISTA)  # Día del Niño sigue abierto
        respuesta = self.inscribir(self.delegado_centro, evento=self.navidad.pk, rut='9876543-3')
        self.assertIn('evento', respuesta.context['form'].errors)

    def test_unidad_sin_delegacion_por_asignacion(self):
        sin_delegacion = crear_funcionario('prof.dideco', 'funcionario')
        dideco = UnidadMunicipal.objects.get(nombre='DIDECO')
        self.entrar(sin_delegacion)
        self.assertRedirects(self.client.get(URL_INSCRIBIR), URL_LISTA)  # sin unidad: no puede inscribir
        dideco.funcionarios.add(sin_delegacion.funcionario)
        respuesta = self.inscribir(sin_delegacion, unidad=dideco.pk)
        self.assertRedirects(respuesta, URL_LISTA)
        self.assertEqual(Inscripcion.objects.get().unidad, dideco)


class AlcanceTests(BaseBeneficiarios):
    def setUp(self):
        super().setUp()
        self.inscribir(self.delegado_centro)
        self.inscripcion = Inscripcion.objects.get()

    def test_otra_unidad_no_ve_ni_modifica(self):
        self.entrar(self.profesional_rural)
        self.assertNotContains(self.client.get(URL_LISTA), 'Ana Pérez')
        self.assertEqual(self.client.get(reverse('beneficiarios:modificar', args=[self.inscripcion.pk])).status_code, 404)
        self.assertTrue(Auditoria.objects.filter(evento='acceso_denegado', entidad='Inscripcion').exists())

    def test_coordinacion_ve_todo_y_elimina(self):
        self.entrar(self.coordinador)
        self.assertContains(self.client.get(URL_LISTA), 'Ana Pérez')
        self.client.post(reverse('beneficiarios:eliminar', args=[self.inscripcion.pk]))
        self.assertFalse(Inscripcion.objects.exists())

    def test_autor_modifica_mientras_la_actividad_esta_abierta(self):
        url = reverse('beneficiarios:modificar', args=[self.inscripcion.pk])
        self.entrar(self.delegado_centro)
        self.client.post(url, self.datos(nombre='Ana María Pérez'))
        self.inscripcion.refresh_from_db()
        self.assertEqual(self.inscripcion.nombre, 'Ana María Pérez')
        self.navidad.inscripciones_abiertas = False
        self.navidad.save()
        self.assertRedirects(self.client.get(url), URL_LISTA)

    def test_profesional_no_administra_actividades(self):
        self.entrar(self.profesional_rural)
        self.assertNotEqual(self.client.get(reverse('beneficiarios:eventos')).status_code, 200)
        self.entrar(self.coordinador)
        self.assertEqual(self.client.get(reverse('beneficiarios:eventos')).status_code, 200)

    def test_verificar_rut_en_vivo(self):
        self.entrar(self.profesional_rural)
        url = reverse('beneficiarios:verificar_rut')
        datos = self.client.get(url, {'rut': '12345678-5', 'evento': self.navidad.pk}).json()
        self.assertTrue(datos['duplicado'])
        self.assertIn('Delegación Centro', datos['mensaje'])
        self.assertFalse(self.client.get(url, {'rut': '12345678-9'}).json()['valido'])
        self.assertFalse(self.client.get(url, {'rut': '9876543-3', 'evento': self.navidad.pk}).json()['duplicado'])

    def test_exporta_excel_solo_lo_visible(self):
        self.entrar(self.delegado_centro)
        respuesta = self.client.get(reverse('beneficiarios:exportar'))
        self.assertEqual(respuesta['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertTrue(Auditoria.objects.filter(evento='exportar', entidad='Inscripcion').exists())


URL_IMPORTAR = reverse('beneficiarios:importar')


def planilla(*filas, encabezado=None):
    """Excel en memoria como lo entregaría una JJ.VV. (con una fila de título sobre el encabezado)."""
    from io import BytesIO

    from django.core.files.uploadedfile import SimpleUploadedFile
    from openpyxl import Workbook

    from .importacion import COLUMNAS_PLANTILLA

    libro = Workbook()
    hoja = libro.active
    hoja.append(['Nómina Navidad 2026'])
    hoja.append(encabezado or COLUMNAS_PLANTILLA)
    for fila in filas:
        hoja.append(list(fila))
    salida = BytesIO()
    libro.save(salida)
    return SimpleUploadedFile('nomina.xlsx', salida.getvalue())


class ImportacionTests(BaseBeneficiarios):
    FILA_OK = ('Ana Pérez', '12.345.678-5', '6 - 8 años', 'Femenino', '123456789', '40%', 'JJ.VV. Villa El Sol', '912345678')

    def importar(self, archivo, solo_revisar=False, **cambios):
        self.entrar(self.delegado_centro)
        datos = {'evento': self.navidad.pk, 'unidad': self.unidad_centro.pk, 'organizacion': '', 'organizacion_otra': '', 'archivo': archivo}
        if solo_revisar:
            datos['solo_revisar'] = 'on'
        datos.update(cambios)
        return self.client.post(URL_IMPORTAR, datos)

    def test_solo_revisar_no_guarda(self):
        respuesta = self.importar(planilla(self.FILA_OK), solo_revisar=True)
        resultado = respuesta.context['resultado']
        self.assertEqual((resultado.validas, resultado.con_error, resultado.guardado), (1, 0, False))
        self.assertFalse(Inscripcion.objects.exists())

    def test_inscribe_filas_validas_y_convierte_formatos_de_excel(self):
        fila2 = ('Juan Soto', '11111111-1', 7, 'M', 987654321, 0.6, '', 56987654321)
        respuesta = self.importar(planilla(self.FILA_OK, fila2), organizacion_otra='Club Los Leones')
        self.assertEqual(respuesta.context['resultado'].validas, 2)
        ana = Inscripcion.objects.get(rut='12345678-5')
        self.assertEqual((ana.rango_edad, ana.genero, ana.tramo_rsh, ana.organizacion), ('6-8', 'F', 40, self.jjvv))
        juan = Inscripcion.objects.get(rut='11111111-1')
        self.assertEqual((juan.rango_edad, juan.tramo_rsh, juan.telefono, juan.folio_rsh), ('6-8', 60, '987654321', '987654321'))
        self.assertEqual(juan.organizacion_nombre, 'Club Los Leones')
        self.assertEqual(juan.registrado_por, self.delegado_centro)
        self.assertTrue(Auditoria.objects.filter(evento='importar', entidad='Inscripcion').exists())

    def test_informa_errores_por_fila_y_guarda_solo_las_validas(self):
        self.inscribir(self.profesional_rural, unidad=self.unidad_rural.pk, rut='22222222-2')
        malas = [
            ('Rut malo', '12345678-9') + self.FILA_OK[2:],
            ('Ya inscrito', '22.222.222-2') + self.FILA_OK[2:],
            ('Repetida', '12345678-5') + self.FILA_OK[2:],
        ]
        respuesta = self.importar(planilla(self.FILA_OK, *malas))
        filas = respuesta.context['resultado'].filas
        self.assertEqual([f.fila for f in filas], [3, 4, 5, 6])
        self.assertIn('dígito verificador', ' '.join(filas[1].errores))
        self.assertIn('RUT ya ingresado por Delegación Rural', ' '.join(filas[2].errores))
        self.assertIn('fila 3', ' '.join(filas[3].errores))
        self.assertEqual(Inscripcion.objects.filter(unidad=self.unidad_centro).count(), 1)

    def test_planilla_sin_columnas_obligatorias(self):
        respuesta = self.importar(planilla(('Ana', '12345678-5'), encabezado=['Nombre', 'RUT']))
        self.assertIn('Faltan columnas', respuesta.context['resultado'].error_general)
        self.assertFalse(Inscripcion.objects.exists())

    def test_rechaza_archivo_que_no_es_xlsx(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        respuesta = self.importar(SimpleUploadedFile('nomina.csv', b'nombre;rut'))
        self.assertIn('archivo', respuesta.context['form'].errors)

    def test_no_importa_a_nombre_de_otra_unidad(self):
        respuesta = self.importar(planilla(self.FILA_OK), unidad=self.unidad_rural.pk)
        self.assertIn('unidad', respuesta.context['form'].errors)
        self.assertFalse(Inscripcion.objects.exists())

    def test_descarga_plantilla_y_se_puede_reimportar(self):
        from openpyxl import load_workbook
        from django.core.files.uploadedfile import SimpleUploadedFile
        from io import BytesIO
        self.entrar(self.delegado_centro)
        respuesta = self.client.get(reverse('beneficiarios:plantilla'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(load_workbook(BytesIO(respuesta.content)).active['B1'].value, 'RUT')
        resultado = self.importar(SimpleUploadedFile('plantilla.xlsx', respuesta.content), solo_revisar=True).context['resultado']
        self.assertEqual((resultado.validas, resultado.con_error), (1, 0))  # la fila de ejemplo es válida
