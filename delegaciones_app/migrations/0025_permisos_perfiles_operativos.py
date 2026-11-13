from django.contrib.auth.management import create_permissions
from django.db import migrations


APP = 'delegaciones_app'
MANTENEDORES = (
    'delegacion', 'cargo', 'rol', 'funcionario', 'catalogo', 'organizacion',
    'periodo', 'parametroversionado', 'itemmedible', 'meta', 'ajuste', 'ausencia',
)


def permisos(Permission, codigos):
    salida = []
    faltantes = []
    for app_label, codename in codigos:
        permiso = Permission.objects.filter(content_type__app_label=app_label, codename=codename).first()
        if permiso is None:
            faltantes.append(f'{app_label}.{codename}')
        else:
            salida.append(permiso)
    if faltantes:
        raise RuntimeError('Faltan permisos necesarios para los perfiles: ' + ', '.join(faltantes))
    return salida


def asignar_permisos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    for nombre in ('Administrador', 'Coordinador', 'Delegado', 'Profesional'):
        Group.objects.get_or_create(name=nombre)

    # Los modelos nuevos de 0021 aún no tienen ContentType ni permisos cuando corre
    # migrate en una base limpia; se generan aquí los permisos estándar de esta app.
    for app_config in apps.get_app_configs():
        if app_config.label == APP:
            app_config.models_module = True
            create_permissions(app_config, apps=apps, verbosity=0)
            app_config.models_module = None

    perfiles = {nombre: Group.objects.filter(name=nombre).first() for nombre in (
        'Administrador', 'Coordinador', 'Delegado', 'Profesional',
    )}

    # Solo se actualizan perfiles que existan en la base; esto permite ejecutar la migración
    # también en instalaciones parciales o sin usuarios demo.
    administrador = perfiles['Administrador']
    if administrador:
        admin_codigos = list(Permission.objects.filter(content_type__app_label=APP).values_list('content_type__app_label', 'codename'))
        admin_codigos += [('auth', f'{accion}_{modelo}') for modelo in ('user', 'group') for accion in ('view', 'add', 'change', 'delete')]
        administrador.permissions.set(permisos(Permission, admin_codigos))

    coordinador = perfiles['Coordinador']
    if coordinador:
        modelos = ('organizacion', 'ajuste', 'ausencia', 'casosocial', 'comentario', 'parametroversionado')
        coord_codigos = [(APP, f'{accion}_{modelo}') for modelo in modelos for accion in ('view', 'change')]
        # La coordinación ve y edita los cinco modelos operativos y los parámetros; decide ajustes con change_ajuste.
        coordinador.permissions.add(*permisos(Permission, coord_codigos))

    delegado = perfiles['Delegado']
    if delegado:
        delegado_codigos = [
            (APP, 'view_organizacion'), (APP, 'change_organizacion'),
            (APP, 'add_ajuste'), (APP, 'add_ausencia'), (APP, 'add_comentario'),
        ]
        delegado.permissions.add(*permisos(Permission, delegado_codigos))

    profesional = perfiles['Profesional']
    if profesional:
        permisos_mantenedores = [
            f'{accion}_{modelo}' for modelo in MANTENEDORES for accion in ('view', 'add', 'change', 'delete')
        ]
        profesional.permissions.remove(*Permission.objects.filter(
            content_type__app_label=APP, codename__in=permisos_mantenedores,
        ))
        profesional_codigos = [
            (APP, 'view_organizacion'), (APP, 'add_casosocial'), (APP, 'add_comentario'),
        ]
        profesional.permissions.add(*permisos(Permission, profesional_codigos))


class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('delegaciones_app', '0024_migrar_roles_obsoletos'),
    ]

    operations = [
        migrations.RunPython(asignar_permisos, migrations.RunPython.noop),
    ]
