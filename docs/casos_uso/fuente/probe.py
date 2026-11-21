import os, sys, django
sys.path.insert(0, sys.argv[1]); os.chdir(sys.argv[1])
os.environ['DJANGO_SETTINGS_MODULE'] = 'gestion_laserena.settings'
django.setup()
from django.test import Client
from django.test.utils import setup_test_environment
setup_test_environment()
from django.contrib.auth.models import User, Group
import delegaciones_app.models as M
from delegaciones_app.crud import MANTENEDORES
act = M.Actividad.objects.first()
comp = M.Compromiso.objects.first()
deleg = M.Delegacion.objects.first()
print('actividad', act and act.codigo_verificador, act and act.estado, 'compromiso', comp and comp.pk)
urls = [('inicio','/'),('solicitudes','/solicitudes/'),('agenda','/agenda/'),('compromiso_nuevo','/agenda/nueva/'),
 ('compromiso_editar',f'/agenda/{comp.pk}/editar/'),('compromiso_eliminar',f'/agenda/{comp.pk}/eliminar/'),
 ('actividades','/actividades/'),('actividad_nueva','/actividad/nueva/'),('actividad_detalle',f'/actividad/{act.codigo_verificador}/'),
 ('mantenedores','/administracion/'),('auditoria','/administracion/auditoria/'),('perfiles','/administracion/perfiles/'),
 ('delegados','/coordinacion/delegados/'),('territorio','/territorio/'),('delegacion_detalle',f'/delegacion/{deleg.nombre}/'),
 ('ajuste_nuevo','/ajustes/nuevo/'),('ausencia_nueva','/ausencias/nuevo/'),('caso_social_nuevo','/casos-sociales/nuevo/'),
 ('dashboard','/gestion/'),('panel','/gestion/panel/'),('semaforo','/gestion/semaforo/'),('resumen','/gestion/resumen/'),
 ('mi_ficha','/gestion/mi-ficha/'),('informes','/gestion/informes/'),('alertas','/gestion/alertas/'),
 ('export_org','/administracion/organizaciones/exportar/')]
for slug in MANTENEDORES:
    urls.append((f'm:{slug}:lista', f'/administracion/{slug}/'))
    urls.append((f'm:{slug}:nuevo', f'/administracion/{slug}/nuevo/'))
users = ['admin.demo','coordinador.demo','delegado.demo','funcionario.centro']
res = {}
for u in users:
    c = Client(); c.force_login(User.objects.get(username=u))
    for name, url in urls:
        try:
            r = c.get(url); code = r.status_code
            if code == 302: code = '302'
        except Exception as e:
            code = 'ERR ' + type(e).__name__
        res.setdefault(name, {})[u] = code
import json; json.dump(res, open(os.environ["PROBE_OUT"], "w"))
print("%-28s" % "url", "ADM COO DEL PRO")
for name, _ in urls:
    print('%-28s' % name, *['%-3s' % str(res[name][u]) for u in users])
for g in Group.objects.all():
    print('\nGRUPO', g.name, sorted(p.codename for p in g.permissions.all()))
