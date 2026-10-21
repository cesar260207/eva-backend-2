"""Pruebas unitarias del generador del plan de pruebas (herramienta de apoyo: no verifica un CU de la especificación)."""
from django.test import SimpleTestCase

from .plan_pruebas import (
    CATALOGO_CU, CATALOGO_RF, FICHAS_LOGIN, POR_DEFINIR, asignar_cp, clave_cu, cobertura_por_cu, cobertura_por_rf, construir_markdown, describir, requisitos, responsable_de,
)

ENTORNO = {'fecha': '01-10-2026', 'ambiente': 'Desarrollo', 'tecnologia': 'Python y Django'}


def registro(cp=None, cus=('CU-01',), rfs=(9,), resultado='Aprobado', tipo='Unitaria', modulo='test_unit_actividades', metodo='test_x', nombre='Prueba x'):
    return {
        'modulo': modulo, 'clase': 'ClaseX', 'metodo': metodo, 'cp': cp, 'cus': list(cus), 'rfs': list(rfs), 'otros': [],
        'nombre': nombre, 'detalle': '', 'tipo': tipo, 'resultado': resultado,
    }


class LecturaDeDocstringsTests(SimpleTestCase):
    """Sin CU (herramienta de apoyo). Cómo se leen los CU y RF declarados en los docstrings."""

    def test_los_requisitos_se_leen_y_los_rangos_se_expanden(self):
        """Sin CU (herramienta de apoyo). «RF-005 a RF-007» incluye el 006."""
        self.assertEqual(requisitos('RF-002, RF-005 a RF-007'), ([2, 5, 6, 7], []))

    def test_un_rnf_no_se_confunde_con_un_rf(self):
        """Sin CU (herramienta de apoyo). RNF-004 y RN-009 van aparte de los RF."""
        self.assertEqual(requisitos('RF-012, RNF-017, RN-009'), ([12], ['RN-009', 'RNF-017']))
        self.assertEqual(requisitos('RNF-004'), ([], ['RNF-004']))
        self.assertEqual(requisitos(None), ([], []))

    def test_el_docstring_de_un_metodo_define_cp_cu_nombre_y_requisitos(self):
        """Sin CU (herramienta de apoyo). Formato de las pruebas unitarias."""
        datos = describir('test_unit_x', 'C', 'test_a', 'CP-LOGIN-004 HU-26 Login con usuario vacío (RF-002, RNF-004). Detalle.', 'Clase')
        self.assertEqual((datos['cp'], datos['cus'], datos['nombre'], datos['rfs'], datos['otros'], datos['detalle']), ('CP-LOGIN-004', ['HU-26'], 'Login con usuario vacío', [2], ['RNF-004'], 'Detalle.'))
        self.assertEqual(datos['tipo'], 'Unitaria')

    def test_un_metodo_sin_cp_declarado_lo_deja_para_asignar(self):
        """Sin CU (herramienta de apoyo). El correlativo se asigna después."""
        datos = describir('test_unit_x', 'C', 'test_a', 'CU-27.1 Restringir elemento duplicado (RF-004). Un código repetido no se guarda.', '')
        self.assertIsNone(datos['cp'])
        self.assertEqual((datos['cus'], datos['nombre'], datos['rfs']), (['CU-27.1'], 'Restringir elemento duplicado', [4]))

    def test_sin_docstring_de_metodo_se_usa_el_de_la_clase(self):
        """Sin CU (herramienta de apoyo). Las pruebas de integración declaran sus CU en la clase."""
        datos = describir('test_integracion', 'C', 'test_registrar_actividad_genera_codigo', None, 'CU-26, CU-30 (RF-001, RF-036). Métodos de Delegacion.')
        self.assertEqual((datos['cus'], datos['rfs'], datos['tipo']), (['CU-26', 'CU-30'], [1, 36], 'Integración'))
        self.assertEqual(datos['nombre'], 'Registrar actividad genera codigo')

    def test_sin_ningun_docstring_valido_la_prueba_queda_sin_cu(self):
        """Sin CU (herramienta de apoyo). Una prueba sin etiqueta no se pierde: aparece sin CU."""
        datos = describir('test_integracion', 'C', 'test_algo', 'Sin etiqueta.', 'Sin CU (migración de datos). Texto.')
        self.assertEqual((datos['cus'], datos['rfs']), ([], []))

    def test_los_cu_se_ordenan_de_forma_natural(self):
        """Sin CU (herramienta de apoyo). CU-02 antes que CU-02.1 y CU-10 después de CU-09.2."""
        desordenados = ['CU-10', 'CU-02.1', 'CU-02', 'CU-09.2', 'CU-02.3', 'HU-26']
        self.assertEqual(sorted(desordenados, key=clave_cu), ['CU-02', 'CU-02.1', 'CU-02.3', 'CU-09.2', 'CU-10', 'HU-26'])


class ArmadoDelPlanTests(SimpleTestCase):
    """Sin CU (herramienta de apoyo). Asignación de CP, cobertura y documento generado."""

    def test_los_cp_se_asignan_por_modulo_y_respetan_los_declarados(self):
        """Sin CU (herramienta de apoyo). El correlativo salta los CP ya usados."""
        registros = [registro(metodo='test_b'), registro(metodo='test_a'), registro(cp='CP-ACT-001', metodo='test_c')]
        asignar_cp(registros)
        por_metodo = {r['metodo']: r['cp'] for r in registros}
        self.assertEqual(por_metodo, {'test_a': 'CP-ACT-002', 'test_b': 'CP-ACT-003', 'test_c': 'CP-ACT-001'})

    def test_el_catalogo_tiene_los_casos_de_uso_y_los_38_requisitos(self):
        """Sin CU (herramienta de apoyo). Los catálogos coinciden con la especificación."""
        self.assertEqual(len(CATALOGO_RF), 38)
        self.assertEqual(sorted(CATALOGO_RF), list(range(1, 39)))
        self.assertIn('CU-27.1', CATALOGO_CU)
        self.assertEqual(len([cu for cu in CATALOGO_CU if '.' not in cu]), 23)

    def test_cobertura_distingue_prueba_propia_subcasos_y_sin_prueba(self):
        """Sin CU (herramienta de apoyo). Aprobado, reprobado, cubierto por subcasos y sin prueba."""
        registros = [
            registro(cus=('CU-01',)), registro(cus=('CU-01.1',)), registro(cus=('CU-02.1',)),
            registro(cus=('CU-04',), resultado='Reprobado'),
        ]
        situacion = {cu: estado for cu, _, _, _, estado in cobertura_por_cu(registros)}
        self.assertEqual(situacion['CU-01'], 'Aprobado')
        self.assertEqual(situacion['CU-02'], 'Cubierto por sus subcasos')
        self.assertEqual(situacion['CU-04'], 'Reprobado')
        self.assertEqual(situacion['CU-05'], 'Sin prueba')

    def test_cobertura_por_rf_cuenta_unitarias_e_integracion(self):
        """Sin CU (herramienta de apoyo). Cada RF muestra cuántas pruebas lo cubren."""
        registros = [registro(rfs=(9,)), registro(rfs=(9, 10), tipo='Integración')]
        filas = {rf: (u, i, estado) for rf, _, u, i, estado in cobertura_por_rf(registros)}
        self.assertEqual(filas['RF-009'], (1, 1, 'Aprobado'))
        self.assertEqual(filas['RF-010'], (0, 1, 'Aprobado'))
        self.assertEqual(filas['RF-015'], (0, 0, 'Sin prueba'))

    def test_el_documento_incluye_resumen_tabla_y_fichas_de_login(self):
        """Sin CU (herramienta de apoyo). Las secciones principales del plan."""
        registros = [registro(cp=f'CP-LOGIN-00{n}', cus=('HU-26',), rfs=(2,), modulo='test_unit_autenticacion', metodo=f'test_{n}') for n in range(1, 9)]
        registros.append(registro(resultado='Reprobado', nombre='Con | barra'))
        texto = construir_markdown(registros, ENTORNO)
        for esperado in ('## 2. Resumen de resultados', '## 3. Cobertura por caso de uso', '## 4. Cobertura por requisito funcional',
                         '## 5. Tabla de casos de prueba', '## 6. Fichas de los casos de login', '| CP | CU | RF | Método de prueba | Prueba | Unidad probada | Responsable | Resultado |', '| Responsable del documento |', '| Equipo de desarrollo |',
                         '### CP-LOGIN-008', 'Pruebas que no pasaron:'):
            self.assertIn(esperado, texto)
        self.assertIn('| Pruebas ejecutadas | 9 |', texto)
        self.assertIn('| Aprobadas | 8 |', texto)
        self.assertIn('Con \\| barra', texto)

    def test_hay_una_ficha_por_cada_caso_de_login(self):
        """Sin CU (herramienta de apoyo). Los ocho casos del formato del curso."""
        self.assertEqual(sorted(FICHAS_LOGIN), [f'CP-LOGIN-00{n}' for n in range(1, 9)])


class ResponsablesTests(SimpleTestCase):
    """Sin CU (herramienta de apoyo). Cada prueba del plan muestra a su responsable."""

    def test_el_responsable_sale_de_la_familia_del_primer_caso_de_uso(self):
        """Sin CU (herramienta de apoyo). CU-11.2 pertenece a CU-11."""
        self.assertEqual(responsable_de(registro(cus=('CU-11.2',))), 'Dante Fredes')
        self.assertEqual(responsable_de(registro(cus=('CU-13', 'CU-01'))), 'Faride Luna')

    def test_sin_asignacion_queda_por_definir(self):
        """Sin CU (herramienta de apoyo). Un caso de uso sin responsable no inventa uno."""
        self.assertEqual(responsable_de(registro(cus=('CU-30',))), POR_DEFINIR)
        self.assertEqual(responsable_de(registro(cus=())), POR_DEFINIR)

    def test_las_fichas_de_login_ya_no_dicen_a_completar(self):
        """Sin CU (herramienta de apoyo). El campo Responsable de las fichas se llena desde la asignación."""
        registros = [registro(cp=f'CP-LOGIN-00{n}', cus=('HU-26',), rfs=(2,), modulo='test_unit_autenticacion', metodo=f'test_{n}') for n in range(1, 9)]
        self.assertNotIn('_a completar_', construir_markdown(registros, ENTORNO))
