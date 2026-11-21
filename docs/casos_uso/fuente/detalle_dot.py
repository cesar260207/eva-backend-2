"""Diagramas de detalle con Graphviz (dot), apaisados, para la presentación."""
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datos_v2 import CASOS, GESTIONES

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
G = {g['id']: g for g in GESTIONES}

# monito
mon = os.path.join(OUT, '_actor.png')
fig = plt.figure(figsize=(0.5, 0.8), dpi=150); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 50); ax.set_ylim(80, 0); ax.axis('off')
ax.add_patch(plt.Circle((25, 12), 9, fill=False, lw=1.6, ec='#333333'))
for (a, b), (c, d) in [((25, 21), (25, 52)), ((10, 33), (40, 33)), ((25, 52), (12, 76)), ((25, 52), (38, 76))]:
    ax.plot([a, c], [b, d], color='#333333', lw=1.6)
fig.savefig(mon, transparent=True); plt.close(fig)


def esc(t):
    return t.replace('"', '\\"')


def generar(gid, mostrar=None, nombre=None, ratio=None):
    g = G[gid]
    claves = [k for k in g['casos'] if mostrar is None or k in mostrar]
    bases = [k for k in claves if CASOS[k]['tipo'] == 'base']
    actores = []
    for k in bases:
        for a in CASOS[k]['actores']:
            if a not in actores:
                actores.append(a)
    ext_base = [k for k in claves if CASOS[k]['tipo'] == 'extend' and any(b in bases for b in CASOS[k]['bases'])]
    incs = [k for k in claves if CASOS[k]['tipo'] == 'include']
    ext_inc = [k for k in claves if CASOS[k]['tipo'] == 'extend' and k not in ext_base]
    L = ['digraph G {', 'rankdir=LR; newrank=true; nodesep=0.22; ranksep=0.75; splines=true; pad=0.25;',
         'graph [fontname="DejaVu Sans", fontsize=15, labelloc=t, labeljust=l];',
         'node [fontname="DejaVu Sans", fontsize=11];', 'edge [fontname="DejaVu Sans", fontsize=9, color="#333333", fontcolor="#444444"];']
    if ratio:
        L.append(f'size="{ratio}"; ratio=fill;')
    L.append(f'subgraph cluster_s {{ label=<<b>{g["nombre"]} ({gid} · {g["epica"]})</b>>; color="#333333"; penwidth=1.4; margin=14;')
    for k in claves:
        c = CASOS[k]
        color = {'base': '#8E2B24', 'include': '#666666', 'extend': '#B5651D'}[c['tipo']]
        fill = '#F4F4F4' if c['tipo'] == 'include' else 'white'
        negrita = ('<b>', '</b>') if c['tipo'] == 'base' else ('', '')
        L.append(f'"{k}" [shape=ellipse, style=filled, fillcolor="{fill}", color="{color}", penwidth=1.5, '
                 f'label=<{negrita[0]}{c["nombre"]}{negrita[1]}<br/><font point-size="9" color="#555555">{c["cu"]}</font>>];')
    L.append('}')
    for a in actores:
        etiqueta = 'Usuario<br/>(cualquier perfil)' if a == 'Usuario' else a
        L.append(f'"A_{a}" [shape=none, image="{mon}", labelloc=b, imagepos=tc, height=1.05, width=1.2, fixedsize=true, '
                 f'label=<<b>{etiqueta}</b>>, fontsize=11];')
    # rangos: actores | extensiones de casos | casos | incluidos | extensiones de incluidos
    L.append('{rank=same; ' + ' '.join(f'"A_{a}";' for a in actores) + '}')
    if 'Usuario' in actores:
        for a in actores:
            if a in ('Profesional', 'Delegado', 'Coordinador', 'Administrador'):
                L.append(f'"A_{a}" -> "A_Usuario" [arrowhead=empty, arrowsize=1.1, penwidth=1.1, constraint=false];')
    L.append('label=<<font point-size="10" color="#444444">Rojo: caso de detalle · Gris: incluido (siempre ocurre) · '
             'Café: extensión (solo si se cumple su condición) · Triángulo: herencia</font>>; labelloc=b; labeljust=r;')
    if bases:
        L.append('{rank=same; ' + ' '.join(f'"{k}";' for k in bases) + '}')
    for k in bases:
        for a in CASOS[k]['actores']:
            L.append(f'"A_{a}" -> "{k}" [arrowhead=none, penwidth=1.1, weight=3];')
        for r in CASOS[k]['incluye']:
            if r in claves:
                L.append(f'"{k}" -> "{r}" [style=dashed, arrowhead=vee, arrowsize=0.7, label="«include»"];')
    for k in ext_base:
        for b in CASOS[k]['bases']:
            if b in bases:
                # se dibuja de la base hacia la extensión para que quede a la derecha o al lado, pero la flecha apunta a la base
                L.append(f'"{b}" -> "{k}" [style=dashed, dir=back, arrowtail=vee, arrowsize=0.7, label="«extend»", constraint=true, weight=1];')
    for k in ext_inc:
        for b in CASOS[k]['bases']:
            if b in claves:
                L.append(f'"{b}" -> "{k}" [style=dashed, dir=back, arrowtail=vee, arrowsize=0.7, label="«extend»"];')
    L.append('}')
    fuente = os.path.join(OUT, f'{nombre or gid}.dot')
    open(fuente, 'w', encoding='utf-8').write('\n'.join(L))
    png = os.path.join(OUT, f'{nombre or gid}.png')
    subprocess.run(['dot', '-Tpng', '-Gdpi=150', fuente, '-o', png], check=True)
    return png


for gid in sys.argv[2:]:
    print(generar(gid, nombre=f'diapositiva_{gid.lower()}'))
