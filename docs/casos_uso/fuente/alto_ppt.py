"""Diagrama de alto nivel apaisado (16:9) para la presentación."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, Polygon
from datos_v2 import GESTIONES

G = {g['id']: g for g in GESTIONES}
W, H = 1600, 900
fig = plt.figure(figsize=(16, 9), dpi=150)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis('off')
ROJO, GRIS = '#8E2B24', '#333333'
EW, EH = 305, 56
XL, XR = 575, 1040
izq = ['G01', 'G02', 'G03', 'G05', 'G09', 'G17', 'G18', 'G08']
der = ['G04', 'G06', 'G07', 'G10', 'G11', 'G14', 'G15', 'G16', 'G12', 'G13', 'G19']
pos = {}
for i, gid in enumerate(izq):
    pos[gid] = (XL, 112 + i * (838 - 112) / (len(izq) - 1))
for i, gid in enumerate(der):
    pos[gid] = (XR, 122 + i * (768 - 122) / (len(der) - 1))

ax.add_patch(Rectangle((405, 50), 810, 822, fill=False, lw=1.6, ec=GRIS))
ax.text(810, 70, 'Sistema de Gestión de Resultados (SGR)', ha='center', va='center', fontsize=13, weight='bold')

ACT = {'Servidor de correo': (115, 120), 'Usuario': (115, 470), 'Profesional': (115, 800),
       'Delegado': (1460, 150), 'Coordinador': (1460, 450), 'Administrador': (1460, 815)}

def actor(x, y, nombre):
    ax.add_patch(plt.Circle((x, y - 36), 11, fill=False, lw=1.6, ec=GRIS, zorder=5))
    ax.plot([x, x], [y - 25, y + 6], color=GRIS, lw=1.6, zorder=5)
    ax.plot([x - 18, x + 18], [y - 14, y - 14], color=GRIS, lw=1.6, zorder=5)
    ax.plot([x, x - 14], [y + 6, y + 28], color=GRIS, lw=1.6, zorder=5)
    ax.plot([x, x + 14], [y + 6, y + 28], color=GRIS, lw=1.6, zorder=5)
    ax.text(x, y + 38, nombre, ha='center', va='top', fontsize=11.5, weight='bold', zorder=5)

for n, (x, y) in ACT.items():
    actor(x, y, 'Usuario\n(cualquier perfil)' if n == 'Usuario' else n)

def asociar(a, gid):
    x, y = ACT[a]
    gx, gy = pos[gid]
    if x < 800:
        p0, p1 = (x + 24, y - 12), (gx - EW / 2 + 2, gy)
    else:
        p0, p1 = (x - 24, y - 12), (gx + EW / 2 - 2, gy)
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=GRIS, lw=1.05, zorder=1)

def flecha_abierta(p, q):
    """Línea con punta simple (asociación dirigida al actor secundario)."""
    ax.annotate('', xy=q, xytext=p, arrowprops=dict(arrowstyle='-|>', color=GRIS, lw=1.05, mutation_scale=14), zorder=1)

def herencia(puntos):
    for p, q in zip(puntos[:-1], puntos[1:]):
        ax.plot([p[0], q[0]], [p[1], q[1]], color=GRIS, lw=1.3, zorder=1)
    (x0, y0), (x1, y1) = puntos[-2], puntos[-1]
    ang = math.atan2(y1 - y0, x1 - x0)
    largo, ancho = 16, 9
    bx, by = x1 - largo * math.cos(ang), y1 - largo * math.sin(ang)
    nx, ny = -math.sin(ang) * ancho, math.cos(ang) * ancho
    ax.add_patch(Polygon([(x1, y1), (bx + nx, by + ny), (bx - nx, by - ny)], closed=True, fc='white', ec=GRIS, lw=1.3, zorder=6))

for g in GESTIONES:
    for a in g['actores']:
        if a == 'Administrador' and 'Coordinador' in g['actores']:
            continue
        if a == 'Servidor de correo':
            gx, gy = pos[g['id']]
            flecha_abierta((gx - EW / 2 + 2, gy), (ACT[a][0] + 26, ACT[a][1] - 12))
        else:
            asociar(a, g['id'])

# herencias
herencia([(115, 772), (115, 556)])                                   # Profesional -> Usuario
herencia([(1460, 787), (1460, 520)])                                 # Administrador -> Coordinador
herencia([(1490, 150 - 14), (1535, 136), (1535, 890), (40, 890), (40, 456), (88, 456)])   # Delegado -> Usuario
ax.plot([1488, 1535], [436, 436], color=GRIS, lw=1.3, zorder=1)      # Coordinador se une a la misma herencia

for gid, (x, y) in pos.items():
    ax.add_patch(Ellipse((x, y), EW, EH, fc='white', ec=ROJO, lw=1.4, zorder=3))
    ax.text(x, y - 8, G[gid]['nombre'], ha='center', va='center', fontsize=10, zorder=4)
    ax.text(x, y + 13, f'{gid} · {G[gid]["epica"]}', ha='center', va='center', fontsize=8.3, color='#555555', zorder=4)

ax.text(810, 884, 'Triángulo = herencia: Profesional, Delegado y Coordinador heredan de Usuario (lo que puede hacer cualquier perfil); '
        'el Administrador hereda del Coordinador.', ha='center', va='center', fontsize=8.6, color='#444444',
        bbox=dict(fc='white', ec='none', pad=1), zorder=7)
fig.savefig(sys.argv[1], dpi=150, facecolor='white')
print('ok')
