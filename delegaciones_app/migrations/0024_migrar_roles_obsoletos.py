from django.db import migrations


def asignar_perfil(usuario, destino, perfiles_superiores):
    Group = usuario.groups.model
    if usuario.groups.filter(name__in=perfiles_superiores).exists():
        return
    usuario.groups.remove(*Group.objects.filter(name__in=('Administrador', 'Coordinador', 'Delegado', 'Profesional')).exclude(name=destino))
    perfil = Group.objects.filter(name=destino).first()
    if perfil:
        usuario.groups.add(perfil)


def migrar_roles_obsoletos(apps, schema_editor):
    Rol = apps.get_model('delegaciones_app', 'Rol')
    Funcionario = apps.get_model('delegaciones_app', 'Funcionario')
    Group = apps.get_model('auth', 'Group')

    for nombre in ('Administrador', 'Coordinador', 'Delegado', 'Profesional'):
        Group.objects.get_or_create(name=nombre)

    delegado = Rol.objects.filter(nombre_rol='delegado').first()
    profesional = Group.objects.filter(name='Profesional').first()
    perfil_delegado = Group.objects.filter(name='Delegado').first()

    verificador = Rol.objects.filter(nombre_rol='verificador').first()
    if verificador:
        if delegado is None:
            delegado = Rol.objects.create(nombre_rol='delegado')
        for funcionario in Funcionario.objects.filter(roles=verificador).distinct():
            funcionario.roles.add(delegado)
            funcionario.roles.remove(verificador)
            if perfil_delegado:
                asignar_perfil(funcionario.usuario, 'Delegado', ('Administrador', 'Coordinador'))
        # El rol obsoleto se retira tras conservar a sus usuarios bajo delegado.
        verificador.delete()

    consulta = Rol.objects.filter(nombre_rol='consulta').first()
    if consulta:
        funcionarios = list(Funcionario.objects.filter(roles=consulta).select_related('usuario').distinct())
        rol_funcionario = Rol.objects.filter(nombre_rol='funcionario').first()
        if funcionarios and rol_funcionario is None:
            rol_funcionario = Rol.objects.create(nombre_rol='funcionario')
        for funcionario in funcionarios:
            if profesional:
                asignar_perfil(funcionario.usuario, 'Profesional', ('Administrador', 'Coordinador', 'Delegado'))
            # El usuario de consulta pasa al rol funcional vigente si existe.
            if rol_funcionario:
                funcionario.roles.add(rol_funcionario)
            funcionario.roles.remove(consulta)
        consulta.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('delegaciones_app', '0023_ajuste_emisor_ajuste_origen_and_more'),
    ]

    operations = [
        migrations.RunPython(migrar_roles_obsoletos, migrations.RunPython.noop),
    ]
