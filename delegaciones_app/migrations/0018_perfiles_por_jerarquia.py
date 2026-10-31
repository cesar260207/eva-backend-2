"""Perfiles según la jerarquía de la Municipalidad: Administrador > Coordinador > Delegado > Funcionario.

«Supervisor» y «Administrativo» eran los nombres genéricos de la pauta de la evaluación. Esta migración:

1. Renombra el grupo Supervisor a Coordinador y el grupo Administrativo a Funcionario. Cada grupo conserva
   su id, sus permisos y sus usuarios; solo cambia el nombre (tabla auth_group).
2. Crea el grupo Delegado (permisos intermedios): lo del Funcionario más revisar evidencias (ver, registrar
   y modificar validaciones) y consultar el historial de tareas, los indicadores y las mediciones.
3. Mueve al perfil Delegado a cada usuario que estaba en Administrativo y tiene el rol delegado o
   verificador, para que pueda aprobar y rechazar en su delegación (tabla auth_user_groups).

Las tablas propias (rol, funcionario, funcionario_rol) no cambian: el rol sigue definiendo la función y el
alcance, y el perfil el nivel de permisos. La reversa devuelve los tres perfiles anteriores.
"""
from django.db import migrations

APP = 'delegaciones_app'
RENOMBRES = (('Supervisor', 'Coordinador'), ('Administrativo', 'Funcionario'))
ROLES_DEL_DELEGADO = ('delegado', 'verificador')
PERMISOS_DELEGADO = (
    [(APP, f'{accion}_actividad') for accion in ('view', 'add', 'change')]
    + [(APP, 'view_evidencia'), (APP, 'add_evidencia')]
    + [(APP, f'{accion}_validacion') for accion in ('view', 'add', 'change')]
    + [(APP, f'{accion}_compromiso') for accion in ('view', 'add', 'change')]
    + [(APP, 'view_historialcompromiso'), (APP, 'view_indicador'), (APP, 'view_mediciondelegacion')]
)


def a_cuatro_perfiles(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    User = apps.get_model('auth', 'User')
    Funcionario = apps.get_model(APP, 'Funcionario')

    for anterior, nuevo in RENOMBRES:
        Group.objects.filter(name=anterior).update(name=nuevo)
    delegado = Group.objects.get_or_create(name='Delegado')[0]
    delegado.permissions.set([
        Permission.objects.get(content_type__app_label=app_label, codename=codename) for app_label, codename in PERMISOS_DELEGADO
    ])

    funcionario = Group.objects.filter(name='Funcionario').first()
    if funcionario is None:
        return
    revisores = Funcionario.objects.filter(roles__nombre_rol__in=ROLES_DEL_DELEGADO).values_list('usuario_id', flat=True)
    for usuario in User.objects.filter(pk__in=revisores, groups=funcionario).distinct():
        usuario.groups.remove(funcionario)
        usuario.groups.add(delegado)


def a_tres_perfiles(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    delegado = Group.objects.filter(name='Delegado').first()
    funcionario = Group.objects.filter(name='Funcionario').first()
    if delegado:
        if funcionario:
            for usuario in delegado.user_set.all():
                usuario.groups.add(funcionario)
        delegado.delete()
    for anterior, nuevo in RENOMBRES:
        Group.objects.filter(name=nuevo).update(name=anterior)


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('delegaciones_app', '0017_sin_solicitar_correccion'),
    ]

    operations = [
        migrations.RunPython(a_cuatro_perfiles, a_tres_perfiles),
    ]
