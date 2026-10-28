"""Perfiles de acceso como grupos de Django, con sus permisos.

- Administrador: acceso total (todos los permisos de la aplicación y gestión de usuarios).
- Supervisor: los seis mantenedores operativos y las transacciones; sin usuarios, roles ni auditoría.
- Administrativo: solo registrar y seguir sus actividades, evidencias y compromisos; sin mantenedores
  ni operaciones críticas (eliminar, revisar evidencias, auditoría).

A los usuarios existentes se les asigna el perfil según sus roles: superusuario, UsuarioMaestro o rol
administrador -> Administrador; rol coordinador -> Supervisor; cualquier otro funcionario -> Administrativo.
Los permisos se definen aquí (y no se importan de la aplicación) para que la migración no cambie si el código cambia.
"""
from django.contrib.auth.management import create_permissions
from django.db import migrations

APP = 'delegaciones_app'
CRUD = ('view', 'add', 'change', 'delete')
MAESTROS_OPERATIVOS = ('delegacion', 'cargo', 'catalogo', 'periodo', 'itemmedible', 'meta')

PERMISOS_SUPERVISOR = (
    [(APP, f'{accion}_{modelo}') for modelo in MAESTROS_OPERATIVOS for accion in CRUD]
    + [(APP, f'{accion}_{modelo}') for modelo in ('actividad', 'evidencia', 'validacion', 'compromiso') for accion in ('view', 'add', 'change')]
    + [(APP, 'delete_compromiso'), (APP, 'view_historialcompromiso'), (APP, 'view_indicador'), (APP, 'view_mediciondelegacion')]
)
PERMISOS_ADMINISTRATIVO = (
    [(APP, f'{accion}_actividad') for accion in ('view', 'add', 'change')]
    + [(APP, 'view_evidencia'), (APP, 'add_evidencia')]
    + [(APP, f'{accion}_compromiso') for accion in ('view', 'add', 'change')]
)
PERMISOS_ADMINISTRADOR_AUTH = [('auth', f'{accion}_user') for accion in CRUD] + [('auth', 'view_group')]


def _permisos(Permission, pares):
    permisos = []
    for app_label, codename in pares:
        permisos.append(Permission.objects.get(content_type__app_label=app_label, codename=codename))
    return permisos


def crear_perfiles(apps, schema_editor):
    # En una base nueva los permisos se crean después de migrar; aquí se crean antes para poder asignarlos.
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    User = apps.get_model('auth', 'User')
    Funcionario = apps.get_model(APP, 'Funcionario')
    UsuarioMaestro = apps.get_model(APP, 'UsuarioMaestro')

    administrador = Group.objects.get_or_create(name='Administrador')[0]
    supervisor = Group.objects.get_or_create(name='Supervisor')[0]
    administrativo = Group.objects.get_or_create(name='Administrativo')[0]
    administrador.permissions.set(
        list(Permission.objects.filter(content_type__app_label=APP)) + _permisos(Permission, PERMISOS_ADMINISTRADOR_AUTH)
    )
    supervisor.permissions.set(_permisos(Permission, PERMISOS_SUPERVISOR))
    administrativo.permissions.set(_permisos(Permission, PERMISOS_ADMINISTRATIVO))

    perfiles = (administrador, supervisor, administrativo)
    maestros = set(UsuarioMaestro.objects.exclude(usuario=None).values_list('usuario_id', flat=True))
    for usuario in User.objects.all():
        if usuario.groups.filter(pk__in=[perfil.pk for perfil in perfiles]).exists():
            continue
        roles = set(Funcionario.objects.filter(usuario=usuario).values_list('roles__nombre_rol', flat=True))
        if usuario.is_superuser or usuario.pk in maestros or 'administrador' in roles:
            usuario.groups.add(administrador)
        elif 'coordinador' in roles:
            usuario.groups.add(supervisor)
        elif Funcionario.objects.filter(usuario=usuario).exists():
            usuario.groups.add(administrativo)


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('delegaciones_app', '0014_limite_tamano_evidencia'),
    ]

    operations = [
        migrations.RunPython(crear_perfiles, migrations.RunPython.noop),
    ]
