"""Plan de pruebas generado a partir de los docstrings de las pruebas y de su resultado.

Cada prueba declara en su docstring el caso de uso que verifica y los requisitos que cubre:

    «CU-27.1 Restringir elemento duplicado (RF-004). Un código repetido no se guarda.»

Las pruebas de integración lo declaran una sola vez en el docstring de su clase:

    «CU-26, CU-30 (RF-001, RF-002, RF-036). Métodos de Delegacion, Cargo, Funcionario y Auditoria.»

Este módulo solo transforma texto en tablas; el comando `plan_pruebas` ejecuta las pruebas y le entrega los resultados.
"""
import re
from collections import defaultdict

CATALOGO_CU = {
    'CU-01': 'Registro de actividades', 'CU-01.1': 'Validar campos de actividad', 'CU-01.2': 'Gestionar error de validación',
    'CU-02': 'Registro de compromisos ciudadanos', 'CU-02.1': 'Validar datos de compromiso', 'CU-02.2': 'Bloquear guardado por campos faltantes',
    'CU-02.3': 'Destacar compromiso vencido',
    'CU-04': 'Administración de funciones por cargo', 'CU-04.1': 'Validar reglas de configuración', 'CU-04.2': 'Bloquear guardado por ponderación inválida',
    'CU-05': 'Definición de metas', 'CU-05.1': 'Validar parámetros de meta', 'CU-05.2': 'Bloquear guardado por valor inválido', 'CU-05.3': 'Notificar período cerrado',
    'CU-06': 'Seguimiento de avance', 'CU-06.1': 'Recalcular indicadores automáticamente', 'CU-06.2': 'Destacar meta cumplida',
    'CU-07': 'Cálculo automático de cumplimiento', 'CU-07.1': 'Aplicar fórmulas de medición', 'CU-07.2': 'Recalcular por anulación de registro',
    'CU-07.3': 'Mostrar detalle en reporte',
    'CU-09': 'Registro de evidencia fotográfica', 'CU-09.1': 'Validar archivo de evidencia', 'CU-09.2': 'Rechazar carga inválida',
    'CU-10': 'Generación de códigos verificadores', 'CU-10.1': 'Buscar actividad por código', 'CU-10.2': 'Consulta sin coincidencias',
    'CU-11': 'Validación de actividades', 'CU-11.1': 'Registrar trazabilidad de decisión', 'CU-11.2': 'Bloquear aporte al avance',
    'CU-12': 'Agenda compartida', 'CU-12.1': 'Filtrar agenda compartida', 'CU-12.2': 'Consulta sin coincidencias en agenda',
    'CU-13': 'Actualización de estados', 'CU-13.1': 'Registrar historial de cambio de estado', 'CU-13.2': 'Reflejar cierre de compromiso',
    'CU-14': 'Seguimiento de compromisos', 'CU-14.1': 'Clasificar compromisos por vencimiento', 'CU-14.2': 'Generar alerta por vencimiento próximo',
    'CU-16': 'Semáforo de cumplimiento', 'CU-16.1': 'Calcular estado del semáforo',
    'CU-17': 'Comparación entre avance esperado y real', 'CU-17.1': 'Calcular diferencia de avance', 'CU-17.2': 'Destacar desviación significativa',
    'CU-18': 'Resumen ejecutivo', 'CU-18.1': 'Consolidar datos de delegación', 'CU-18.2': 'Navegar al detalle de gestión',
    'CU-20': 'Generación de informes', 'CU-20.1': 'Consolidar datos filtrados', 'CU-20.2': 'Restringir por ámbito de permisos',
    'CU-23': 'Trabajo colaborativo en línea', 'CU-23.1': 'Controlar conflicto de concurrencia',
    'CU-25': 'Modificar parámetros',
    'CU-26': 'Administración de delegaciones, usuarios y roles', 'CU-26.1': 'Denegar acceso por ámbito',
    'CU-27': 'Administración de catálogos', 'CU-27.1': 'Restringir elemento duplicado',
    'CU-28': 'Administración de períodos', 'CU-28.1': 'Restricción por período cerrado',
    'CU-29': 'Búsqueda y filtros', 'CU-29.1': 'Restricción de búsqueda por ámbito',
    'CU-30': 'Auditoría de cambios', 'CU-30.1': 'Bloqueo por alteración no autorizada',
}

CATALOGO_RF = {
    1: 'Administrar delegaciones', 2: 'Administrar usuarios y roles', 3: 'Configurar cargos y funciones',
    4: 'Mantener catálogo de actividades y servicios', 5: 'Configurar períodos de medición', 6: 'Configurar ponderaciones',
    7: 'Configurar metas y umbrales', 8: 'Presentar ficha personal', 9: 'Registrar actividades', 10: 'Validar campos de actividad',
    11: 'Generar código verificador de evidencia', 12: 'Asociar evidencia', 13: 'Validar evidencia', 14: 'Controlar puntuación por validación',
    15: 'Registrar atención social por etapas', 16: 'Crear compromisos en agenda colectiva', 17: 'Asignar compromiso', 18: 'Gestionar estados',
    19: 'Controlar plazos', 20: 'Relacionar agenda y medición', 21: 'Generar resumen colectivo', 22: 'Calcular avance actual',
    23: 'Calcular porcentaje de cumplimiento', 24: 'Calcular cumplimiento ponderado', 25: 'Aplicar incentivos y penalizaciones',
    26: 'Calcular meta esperada al día', 27: 'Mostrar semáforo de avance', 28: 'Mostrar tablero personal', 29: 'Mostrar tablero de delegación',
    30: 'Medir actividad reciente', 31: 'Mostrar vista global por cargos', 32: 'Buscar y filtrar información', 33: 'Generar y exportar informes',
    34: 'Permitir trabajo simultáneo', 35: 'Facilitar coordinación', 36: 'Mantener trazabilidad', 37: 'Emitir alertas', 38: 'Versionar parámetros',
}

CODIGO_DE_MODULO = {
    'test_integracion': 'INT', 'test_unit_autenticacion': 'LOGIN', 'test_unit_organizacion': 'ORG', 'test_unit_actividades': 'ACT',
    'test_unit_medicion': 'MED', 'test_unit_compromisos': 'COM', 'test_unit_transversal': 'TRA', 'test_unit_plan_pruebas': 'PLAN', 'test_unit_alertas': 'ALE',
}

# Estado de los requisitos que no están completos en el sistema (se declara aquí para que el plan lo diga con claridad).
OBSERVACIONES_RF = {
    15: 'No implementado: no existe el registro de atenciones sociales por etapas.',
    20: 'No implementado: cerrar un compromiso no alimenta el indicador del ítem; solo cuentan las actividades aprobadas.',
    25: 'No implementado: el campo ajuste del indicador se guarda pero no entra al cálculo.',
    31: 'No implementado: no hay vista global por cargos.',
    35: 'No implementado: no hay observaciones o comentarios asociados a registros.',
}

# Ficha de cada caso de login, con los campos del formato del plan de pruebas.
_USUARIO = 'usuario.prueba'
FICHAS_LOGIN = {
    'CP-LOGIN-001': ('Login con usuario y contraseña válidos', 'Verificar que se autentique a un usuario registrado y activo.',
                     f'Usuario: {_USUARIO} / Contraseña: la registrada', 'El formulario es válido y entrega el usuario autenticado.'),
    'CP-LOGIN-002': ('Login con contraseña incorrecta', 'Verificar que se rechace una contraseña incorrecta para un usuario existente.',
                     f'Usuario: {_USUARIO} / Contraseña: otra-clave', 'El formulario es inválido, informa credenciales inválidas y no entrega usuario.'),
    'CP-LOGIN-003': ('Login con usuario inexistente', 'Verificar que se rechace un usuario que no está registrado.',
                     'Usuario: no.existe / Contraseña: cualquiera', 'El formulario es inválido, con el mismo mensaje genérico de credenciales inválidas.'),
    'CP-LOGIN-004': ('Login con usuario vacío', 'Verificar que el usuario sea obligatorio.',
                     'Usuario: (vacío) / Contraseña: válida', 'El formulario es inválido y señala solo el campo usuario como obligatorio.'),
    'CP-LOGIN-005': ('Login con contraseña vacía', 'Verificar que la contraseña sea obligatoria.',
                     f'Usuario: {_USUARIO} / Contraseña: (vacía)', 'El formulario es inválido y señala solo el campo contraseña como obligatorio.'),
    'CP-LOGIN-006': ('Login con ambos campos vacíos', 'Verificar que ambos campos sean obligatorios.',
                     'Usuario: (vacío) / Contraseña: (vacía)', 'El formulario es inválido y señala los dos campos.'),
    'CP-LOGIN-007': ('Login con usuario inactivo', 'Verificar que una cuenta desactivada no pueda iniciar sesión.',
                     f'Usuario: {_USUARIO} con is_active falso / Contraseña: válida', 'El formulario es inválido y authenticate() no devuelve usuario.'),
    'CP-LOGIN-008': ('Login con formato inválido', 'Verificar el rechazo de entradas con formato inválido.',
                     "Usuarios: «' OR '1'='1», 151 caracteres, «<script>…</script>» y solo espacios", 'Todos se rechazan sin error del sistema y sin entregar usuario; los espacios señalan el campo usuario.'),
}

_CU = r'(?:CU|HU)-\d+(?:\.\d+)?'
PATRON_METODO = re.compile(rf'^(?:(?P<cp>CP-[A-Z]+-\d{{3}})\s+)?(?P<cu>{_CU})\s+(?P<nombre>.+?)\s*\((?P<req>[^)]*)\)\.?\s*(?P<detalle>.*)$')
PATRON_CLASE = re.compile(rf'^(?P<cus>{_CU}(?:,\s*{_CU})*)\s*\((?P<req>[^)]*)\)\.?\s*(?P<detalle>.*)$')
PATRON_RF = re.compile(r'(?<![A-Z])RF-(\d{3})(?:\s+a\s+RF-(\d{3}))?')
PATRON_OTROS = re.compile(r'(?<![A-Z])(?:RNF|RN)-\d{3}')


def clave_cu(cu):
    """Orden natural de un CU: CU-02 antes que CU-02.1 y CU-10 después de CU-09."""
    familia, _, subcaso = cu.partition('.')
    return (familia[:2], int(familia[3:]), int(subcaso) if subcaso else 0)


def requisitos(texto):
    """(lista de números de RF, otros requisitos RNF y RN) citados en un texto; «RF-005 a RF-007» incluye los intermedios."""
    rfs = set()
    for inicio, fin in PATRON_RF.findall(texto or ''):
        rfs.update(range(int(inicio), int(fin or inicio) + 1))
    return sorted(rfs), sorted(set(PATRON_OTROS.findall(texto or '')))


def nombre_legible(metodo):
    texto = metodo.removeprefix('test_').replace('_', ' ')
    return texto[:1].upper() + texto[1:]


def describir(modulo, clase, metodo, doc_metodo, doc_clase):
    """Datos de una prueba leídos de sus docstrings; None en los campos que no se declaran."""
    primera_linea = (doc_metodo or '').strip().splitlines()[0] if (doc_metodo or '').strip() else ''
    por_metodo = PATRON_METODO.match(primera_linea)
    por_clase = PATRON_CLASE.match(((doc_clase or '').strip().splitlines() or [''])[0])
    if por_metodo:
        cus, texto_req = [por_metodo['cu']], por_metodo['req']
        nombre, detalle, cp = por_metodo['nombre'], por_metodo['detalle'], por_metodo['cp']
    elif por_clase:
        cus, texto_req = [cu.strip() for cu in por_clase['cus'].split(',')], por_clase['req']
        nombre, detalle, cp = nombre_legible(metodo), por_clase['detalle'], None
    else:
        cus, texto_req, nombre, detalle, cp = [], '', nombre_legible(metodo), '', None
    rfs, otros = requisitos(texto_req)
    return {
        'modulo': modulo, 'clase': clase, 'metodo': metodo, 'cp': cp, 'cus': cus, 'rfs': rfs, 'otros': otros,
        'nombre': nombre, 'detalle': detalle,
        'tipo': 'Integración' if modulo == 'test_integracion' else 'Unitaria',
    }


def asignar_cp(registros):
    """Da un CP a cada prueba que no declara el suyo: CP-<módulo>-<correlativo> en orden alfabético estable."""
    usados = {registro['cp'] for registro in registros if registro['cp']}
    grupos = defaultdict(list)
    for registro in sorted(registros, key=lambda r: (r['modulo'], r['clase'], r['metodo'])):
        if not registro['cp']:
            grupos[registro['modulo']].append(registro)
    for modulo, grupo in grupos.items():
        codigo = CODIGO_DE_MODULO.get(modulo, modulo.removeprefix('test_').upper()[:3])
        numero = 0
        for registro in grupo:
            numero += 1
            while f'CP-{codigo}-{numero:03d}' in usados:
                numero += 1
            registro['cp'] = f'CP-{codigo}-{numero:03d}'
            usados.add(registro['cp'])
    return registros


def _celda(texto):
    return str(texto).replace('|', '\\|').replace('\n', ' ')


def _estado(registros):
    if not registros:
        return None
    return 'Aprobado' if all(r['resultado'] == 'Aprobado' for r in registros) else 'Reprobado'


def cobertura_por_cu(registros):
    """Por cada CU del catálogo: pruebas, resultado y, si no tiene pruebas propias, si lo cubren sus subcasos."""
    por_cu = defaultdict(list)
    for registro in registros:
        for cu in registro['cus']:
            por_cu[cu].append(registro)
    filas = []
    for cu in sorted(CATALOGO_CU, key=clave_cu):
        propias = por_cu.get(cu, [])
        hijos = [r for otro, lista in por_cu.items() if otro.startswith(cu + '.') for r in lista] if '.' not in cu else []
        if propias:
            situacion = _estado(propias)
        elif hijos:
            situacion = 'Cubierto por sus subcasos'
        else:
            situacion = 'Sin prueba'
        unitarias = sum(1 for r in propias if r['tipo'] == 'Unitaria')
        filas.append((cu, CATALOGO_CU[cu], unitarias, len(propias) - unitarias, situacion))
    return filas


def cobertura_por_rf(registros):
    por_rf = defaultdict(list)
    for registro in registros:
        for rf in registro['rfs']:
            por_rf[rf].append(registro)
    filas = []
    for numero, nombre in CATALOGO_RF.items():
        pruebas = por_rf.get(numero, [])
        unitarias = sum(1 for r in pruebas if r['tipo'] == 'Unitaria')
        filas.append((f'RF-{numero:03d}', nombre, unitarias, len(pruebas) - unitarias, _estado(pruebas) or 'Sin prueba'))
    return filas


def construir_markdown(registros, entorno):
    """Documento Markdown con el plan de pruebas y sus resultados."""
    registros = asignar_cp(list(registros))
    total = len(registros)
    aprobadas = sum(1 for r in registros if r['resultado'] == 'Aprobado')
    reprobadas = [r for r in registros if r['resultado'] != 'Aprobado']
    unitarias = sum(1 for r in registros if r['tipo'] == 'Unitaria')
    l = []
    l += ['# Plan de pruebas del Sistema de Gestión de Delegaciones', '',
          'Generado con `python manage.py plan_pruebas` a partir de los docstrings de las pruebas y de su ejecución. No se edita a mano: se vuelve a generar.', '',
          '## 1. Identificación del documento', '', '| Campo | Información |', '|---|---|',
          '| Nombre del proyecto | Sistema de Gestión de Delegaciones |', '| Tipo de pruebas | Unitarias y de integración |', '| Versión | 1.0 |',
          f"| Fecha | {entorno['fecha']} |", f"| Ambiente de pruebas | {entorno['ambiente']} |", f"| Tecnología utilizada | {entorno['tecnologia']} |", '',
          '## 2. Resumen de resultados', '', '| Concepto | Cantidad |', '|---|---|',
          f'| Pruebas ejecutadas | {total} |', f'| Unitarias | {unitarias} |', f'| De integración | {total - unitarias} |',
          f'| Aprobadas | {aprobadas} |', f'| Reprobadas o con error | {len(reprobadas)} |', '']
    if reprobadas:
        l += ['Pruebas que no pasaron:', ''] + [f"- {r['cp']} ({r['clase']}.{r['metodo']}): {r['resultado']}" for r in reprobadas] + ['']
    cu_filas = cobertura_por_cu(registros)
    l += ['## 3. Cobertura por caso de uso', '',
          'Los casos de uso son los de la especificación detallada (CU-01 a CU-30). «Cubierto por sus subcasos» indica que el caso base no tiene pruebas propias pero sí sus extensiones.', '',
          '| CU | Nombre | Unitarias | Integración (por clase) | Situación |', '|---|---|---|---|---|']
    l += [f'| {cu} | {nombre} | {u} | {i} | {situacion} |' for cu, nombre, u, i, situacion in cu_filas]
    sin_prueba = [cu for cu, _, _, _, situacion in cu_filas if situacion == 'Sin prueba']
    l += ['', 'Casos de uso sin ninguna prueba: ' + (', '.join(sin_prueba) if sin_prueba else 'ninguno.'), '']
    rf_filas = cobertura_por_rf(registros)
    l += ['## 4. Cobertura por requisito funcional', '',
          'En las pruebas de integración el CU y los RF se declaran por clase, así que cada prueba de la clase cuenta para todos los que la clase cita.', '',
          '| RF | Requisito | Unitarias | Integración (por clase) | Situación | Observación |', '|---|---|---|---|---|---|']
    l += [f'| {rf} | {nombre} | {u} | {i} | {situacion} | {OBSERVACIONES_RF.get(int(rf[3:]), "")} |' for rf, nombre, u, i, situacion in rf_filas]
    sin_rf = [rf for rf, _, _, _, situacion in rf_filas if situacion == 'Sin prueba']
    l += ['', 'Requisitos sin ninguna prueba: ' + (', '.join(sin_rf) if sin_rf else 'ninguno.'), '']
    l += ['## 5. Tabla de casos de prueba', '',
          'Una fila por prueba. La columna CU lista los casos de uso que verifica y RF los requisitos (RNF y RN cuando aplican). '
          'En las pruebas de integración, CU y RF son los de su clase.', '',
          '| CP | CU | RF | Método de prueba | Prueba | Unidad probada | Resultado |', '|---|---|---|---|---|---|---|']
    ordenados = sorted(registros, key=lambda r: (clave_cu(r['cus'][0]) if r['cus'] else ('ZZ', 0, 0), r['cp']))
    for r in ordenados:
        requisitos_texto = ', '.join([f'RF-{n:03d}' for n in r['rfs']] + r['otros']) or '-'
        descripcion = r['detalle'] or r['nombre']
        l.append(f"| {r['cp']} | {_celda(', '.join(r['cus']) or '-')} | {_celda(requisitos_texto)} | {r['tipo']} | {_celda(descripcion)} | {r['clase']}.{r['metodo']} | {r['resultado']} |")
    login = [r for r in sorted(registros, key=lambda r: r['cp']) if r['cp'] in FICHAS_LOGIN]
    if login:
        l += ['', '## 6. Fichas de los casos de login', '',
              'Siguen el formato del plan de pruebas del curso. La unidad probada es el formulario de autenticación `AuthenticationForm`, que usa `LoginView`.']
        for r in login:
            nombre, objetivo, datos, esperado = FICHAS_LOGIN[r['cp']]
            marca = '☒' if r['resultado'] == 'Aprobado' else '☐'
            l += ['', f"### {r['cp']}", '', '| Campo | Detalle |', '|---|---|',
                  f"| ID Caso de Prueba | {r['cp']} |", '| Módulo | Autenticación |', '| Unidad a probar | AuthenticationForm (validación de credenciales) |',
                  f'| Nombre | {nombre} |', f'| Objetivo | {objetivo} |', '| Precondiciones | El usuario de prueba está registrado (activo salvo en el caso 007). |',
                  f'| Datos de entrada | {_celda(datos)} |', '| Pasos | 1. Construir el formulario con los datos. 2. Validarlo. 3. Revisar errores y usuario obtenido. |',
                  f'| Resultado esperado | {esperado} |',
                  f"| Resultado obtenido | {'Coincide con lo esperado.' if r['resultado'] == 'Aprobado' else 'No coincide: ' + r['resultado']} |",
                  f"| Estado | {marca} Aprobado {'☐' if marca == '☒' else '☒'} Reprobado ☐ No ejecutado |",
                  f"| Responsable | _a completar_ |", f"| Fecha ejecución | {entorno['fecha']} |", f"| Observaciones | Prueba `{r['clase']}.{r['metodo']}`. |"]
    l.append('')
    return '\n'.join(l)
