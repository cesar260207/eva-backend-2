"""Genera los diagramas (PlantUML) y los cuadros (Markdown) desde datos_v2.py.
Uso: python gen_v2.py <carpeta_salida> [plan_de_pruebas.md]"""
import os, re, sys, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datos_v2 import CASOS, GESTIONES, EPICAS, U, P, D, C, A, MAIL

OUT = sys.argv[1]
PLAN = sys.argv[2] if len(sys.argv) > 2 else None
os.makedirs(os.path.join(OUT, 'plantuml'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'cuadros'), exist_ok=True)

PRUEBAS = {}
if PLAN and os.path.exists(PLAN):
    for linea in open(PLAN, encoding='utf-8'):
        m = re.match(r'\| (CU-\d\d(?:\.\d)?) \| [^|]+ \| (\d+) \| (\d+) \| ([^|]+) \|', linea)
        if m:
            PRUEBAS[m.group(1)] = (int(m.group(2)), int(m.group(3)), m.group(4).strip())

ESTILO = """skinparam shadowing false
skinparam dpi 150
skinparam defaultFontName Arial
skinparam defaultFontSize 13
skinparam actorStyle awesome
skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #8E2B24
  ArrowColor #333333
}
skinparam rectangle {
  BorderColor #333333
  FontStyle bold
}
skinparam ArrowFontSize 11
"""


def alias(t):
    s = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode()
    return re.sub(r'[^A-Za-z0-9]', '_', s)


def es_software(cu):
    return int(cu.split('-')[1].split('.')[0]) <= 31


ORDEN_ACT = [U, P, D, C, A, MAIL]

# ---------------- alto nivel
L = ['@startuml cu_alto_nivel', ESTILO, 'left to right direction',
     'title Casos de uso de alto nivel del SGR (una gestión por cada épica o parte de ella)']
for a in ORDEN_ACT:
    etiqueta = f'{a}\\n(cualquier perfil)' if a == U else a
    L.append(f'actor "{etiqueta}" as {alias(a)}')
L.append('rectangle "Sistema de Gestión de Resultados (SGR)" {')
for g in GESTIONES:
    L.append(f'  usecase "{g["nombre"]}\\n({g["id"]} · {g["epica"]})" as {g["id"]}')
L.append('}')
for a in (P, D, C, A):
    L.append(f'{alias(a)} -up-|> {alias(U)}')
for g in GESTIONES:
    for a in g['actores']:
        L.append(f'{g["id"]} --> {alias(a)}' if a == MAIL else f'{alias(a)} --> {g["id"]}')
L.append('@enduml')
open(os.path.join(OUT, 'plantuml', 'cu_alto_nivel.puml'), 'w', encoding='utf-8').write('\n'.join(L))

# ---------------- detalle
COMUNES = {k for k in CASOS if sum(k in g['casos'] for g in GESTIONES) > 1}
for g in GESTIONES:
    claves = g['casos']
    L = [f'@startuml cu_detalle_{g["id"].lower()}', ESTILO, 'left to right direction',
         f'title {g["nombre"]} ({g["id"]} · {g["epica"]}): caso de uso detallado']
    actores = []
    for k in claves:
        for a in CASOS[k]['actores']:
            if a != 'Sistema' and a not in actores:
                actores.append(a)
    for a in sorted(actores, key=ORDEN_ACT.index):
        L.append(f'actor "{a}" as {alias(a)}')
    L.append(f'rectangle "{g["nombre"]}" {{')
    for k in claves:
        c = CASOS[k]
        L.append(f'  usecase "{c["cu"]}\\n{c["nombre"]}" as {k}')
    L.append('}')
    for k in claves:
        c = CASOS[k]
        if c['tipo'] == 'base':
            for a in c['actores']:
                L.append(f'{k} --> {alias(a)}' if a == MAIL else f'{alias(a)} --> {k}')
    for k in claves:
        c = CASOS[k]
        for r in c['incluye']:
            if r in claves:
                L.append(f'{k} ..> {r} : <<include>>')
        if c['tipo'] == 'extend':
            for b in c['bases']:
                if b in claves:
                    L.append(f'{k} ..> {b} : <<extend>>')
    L.append('@enduml')
    open(os.path.join(OUT, 'plantuml', f'cu_detalle_{g["id"].lower()}.puml'), 'w', encoding='utf-8').write('\n'.join(L))


# ---------------- cuadros
def celda(t):
    return str(t).replace('|', '/').replace('\n', ' ')


def ref(k):
    return f'{CASOS[k]["cu"]} {CASOS[k]["nombre"]}'


def pruebas(cu):
    if cu in PRUEBAS:
        u, i, s = PRUEBAS[cu]
        return f'{u} unitaria{"" if u == 1 else "s"} y {i} de integración ({s.lower()})'
    if es_software(cu):
        return 'Historia sin pruebas propias en el plan'
    return 'Caso nuevo: sin código propio en el plan de pruebas'


def cuadro_base(c, claves):
    extendidos = [ref(k) for k in claves if CASOS[k]['tipo'] == 'extend' and c['clave'] in CASOS[k]['bases']]
    filas = [('Identificador', c['cu']), ('Nombre', c['nombre']), ('Actor principal', ', '.join(c['actores'])),
             ('Propósito', c['proposito']), ('Precondiciones', c['pre']), ('Postcondiciones', c['post']),
             ('Flujo principal', c['flujo']), ('Casos incluidos', '; '.join(ref(k) for k in c['incluye']) or 'Ninguno'),
             ('Casos extendidos', '; '.join(extendidos) or 'Ninguno'), ('Historia de usuario', c['hu'] or '·'),
             ('Pantalla', f'`{c["pantalla"]}`' if c['pantalla'].startswith('/') else c['pantalla']),
             ('Pruebas', pruebas(c['cu']))]
    if c['nota']:
        filas.append(('Nota', c['nota']))
    return [f'### {c["cu"]} {c["nombre"]}', '', '| Campo | Descripción |', '| --- | --- |'] + \
        [f'| {a} | {celda(b)} |' for a, b in filas] + ['']


def tabla_inc(lista, claves):
    out = ['| Identificador | Nombre | Propósito | Precondiciones | Postcondiciones | Flujo principal | Casos extendidos | Pruebas |',
           '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for k in lista:
        c = CASOS[k]
        exts = '; '.join(ref(e) for e in claves if CASOS[e]['tipo'] == 'extend' and k in CASOS[e]['bases']) or 'Ninguno'
        out.append(f'| {c["cu"]} | {c["nombre"]} | {celda(c["proposito"])} | {celda(c["pre"])} | {celda(c["post"])} | '
                   f'{celda(c["flujo"])} | {exts} | {pruebas(c["cu"])} |')
    return out + ['']


def tabla_ext(lista, claves):
    out = ['| Identificador | Nombre | Caso base | Condición | Resultado | Pruebas |', '| --- | --- | --- | --- | --- | --- |']
    for k in lista:
        c = CASOS[k]
        bases = '; '.join(ref(b) for b in c['bases'] if claves is None or b in claves)
        out.append(f'| {c["cu"]} | {c["nombre"]} | {bases} | {celda(c["condicion"])} | {celda(c["resultado"])} | {pruebas(c["cu"])} |')
    return out + ['']


trazab = []
for g in GESTIONES:
    claves = g['casos']
    bases = [k for k in claves if CASOS[k]['tipo'] == 'base']
    incs = [k for k in claves if CASOS[k]['tipo'] == 'include' and k not in COMUNES]
    exts = [k for k in claves if CASOS[k]['tipo'] == 'extend' and k not in COMUNES]
    comunes = [k for k in claves if k in COMUNES and k not in bases]
    actores = sorted({a for k in bases for a in CASOS[k]['actores']}, key=ORDEN_ACT.index)
    md = [f'## {g["id"]} {g["nombre"]}', '',
          f'Épica {g["epica"]} ({EPICAS[g["epica"]]}). {len(bases)} caso{"" if len(bases) == 1 else "s"} de detalle para {", ".join(actores)}.', '']
    for k in bases:
        md += cuadro_base(CASOS[k], claves)
        trazab.append((g['id'], CASOS[k]))
    if incs:
        md += [f'### Casos incluidos de {g["id"]}', '', 'Los ejecuta el sistema dentro del caso base; no tienen actor propio.', ''] + tabla_inc(incs, claves)
    if exts:
        md += [f'### Casos extendidos de {g["id"]}', ''] + tabla_ext(exts, claves)
    if comunes:
        md += ['Usa también los casos comunes ' + ', '.join(ref(k) for k in comunes) + '.', '']
    open(os.path.join(OUT, 'cuadros', f'{g["id"]}.md'), 'w', encoding='utf-8').write('\n'.join(md).strip() + '\n')

com_inc = [k for k in sorted(COMUNES, key=lambda k: CASOS[k]['cu']) if CASOS[k]['tipo'] == 'include']
com_ext = [k for k in sorted(COMUNES, key=lambda k: CASOS[k]['cu']) if CASOS[k]['tipo'] == 'extend']
md = ['## Casos comunes', '', 'Se usan en varias gestiones; se describen una vez.', '',
      '**Incluidos comunes**', ''] + tabla_inc(com_inc, list(CASOS)) + ['**Extensiones comunes**', ''] + tabla_ext(com_ext, None)
open(os.path.join(OUT, 'cuadros', 'comunes.md'), 'w', encoding='utf-8').write('\n'.join(md))

T = ['| Gestión | Caso de uso | Actor | Pantalla | Pruebas |', '| --- | --- | --- | --- | --- |']
for gid, c in trazab:
    pant = f'`{c["pantalla"]}`' if c['pantalla'].startswith('/') else c['pantalla']
    T.append(f'| {gid} | {c["cu"]} {c["nombre"]} | {", ".join(c["actores"])} | {celda(pant)} | {pruebas(c["cu"])} |')
open(os.path.join(OUT, 'cuadros', 'trazabilidad.md'), 'w', encoding='utf-8').write('\n'.join(T) + '\n')

# índice de códigos
I = ['| Código | Nombre | Tipo | Gestiones | Origen |', '| --- | --- | --- | --- | --- |']
tipo = {'base': 'Detalle', 'include': 'Incluido', 'extend': 'Extensión'}
def clave_orden(c):
    n = c['cu'].split('-')[1]
    a, _, b = n.partition('.')
    return (int(a), int(b or 0))
for c in sorted(CASOS.values(), key=clave_orden):
    gs = ', '.join(g['id'] for g in GESTIONES if c['clave'] in g['casos'])
    I.append(f'| {c["cu"]} | {c["nombre"]} | {tipo[c["tipo"]]} | {gs} | {"Software (plan de pruebas)" if es_software(c["cu"]) else "Nuevo"} |')
open(os.path.join(OUT, 'cuadros', 'indice_codigos.md'), 'w', encoding='utf-8').write('\n'.join(I) + '\n')
print('ok', len(GESTIONES), 'gestiones,', len(CASOS), 'casos,', len(PRUEBAS), 'códigos con pruebas')
