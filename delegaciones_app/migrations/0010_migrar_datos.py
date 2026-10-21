# Migración de datos (fase «migrar» del patrón ampliar, migrar, contraer).
# Copia los datos de los campos y tablas antiguos a los del diseño de 17 clases.
# Usa modelos históricos (apps.get_model): no tienen los métodos ni los save()
# personalizados de models.py, por eso aquí se calculan valores como
# dias_computables o los códigos de evidencia.

import calendar
import json
from collections import Counter
from datetime import datetime, time
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations
from django.db.models import F, Sum
from django.utils import timezone
from django.utils.text import slugify

ZONA = ZoneInfo('America/Santiago')
ROLES = ['administrador', 'coordinador', 'delegado', 'funcionario', 'verificador', 'consulta']
SIN_CARGO = 'Sin cargo asignado'
PREFIJOS = {'actividad': 'ACT', 'servicio': 'SER', 'atencion': 'ATE', 'item': 'ITE'}
MARCA_PROVISIONAL = '(provisional)'


def _avisar(mensaje):
    print(f'\n  [0010_migrar_datos] {mensaje}', end='')


def _nombre(usuario):
    return f'{usuario.first_name} {usuario.last_name}'.strip() or usuario.username


def _texto(valor):
    if valor is None or isinstance(valor, str):
        return valor
    return json.dumps(valor, ensure_ascii=False, default=str)


def _dias(inicio, termino):
    return (termino - inicio).days + 1


def _codigo_unico(Modelo, campo, base, largo):
    codigo, numero = base[:largo], 2
    while Modelo.objects.filter(**{campo: codigo}).exists():
        sufijo = f'-{numero}'
        codigo, numero = f'{base[:largo - len(sufijo)]}{sufijo}', numero + 1
    return codigo


class _Migracion:
    def __init__(self, apps):
        self.m = {nombre: apps.get_model('delegaciones_app', nombre) for nombre in (
            'Delegacion', 'PerfilUsuario', 'CatalogoItem', 'PeriodoMedicion', 'Actividad', 'Evidencia',
            'Compromiso', 'HistorialCompromiso', 'MetaMedicion', 'Auditoria', 'Cargo', 'Rol', 'Funcionario',
            'FuncionarioRol', 'UsuarioMaestro', 'Periodo', 'ParametroVersionado', 'ItemMedible', 'Catalogo',
            'Meta', 'Validacion',
        )}
        self.User = apps.get_model(settings.AUTH_USER_MODEL)
        self.roles, self.cargos, self.funcionarios = {}, {}, {}

    # Organización y acceso

    def cargo(self, texto):
        nombre = (texto or '').strip() or SIN_CARGO
        if nombre not in self.cargos:
            Cargo = self.m['Cargo']
            self.cargos[nombre] = Cargo.objects.filter(nombre=nombre).first() or Cargo.objects.create(nombre=nombre, vigencia=True)
        return self.cargos[nombre]

    def crear_funcionario(self, usuario, rol, delegacion_id=None, texto_cargo=''):
        funcionario = self.m['Funcionario'].objects.create(
            usuario=usuario, identificador_institucional=usuario.username, nombre=_nombre(usuario),
            cargo=self.cargo(texto_cargo), delegacion_id=delegacion_id, estado=usuario.is_active,
        )
        self.m['FuncionarioRol'].objects.create(funcionario=funcionario, rol=self.roles[rol])
        self.funcionarios[usuario.pk] = funcionario
        return funcionario

    def organizacion(self):
        m = self.m
        for nombre in ROLES:
            self.roles[nombre] = m['Rol'].objects.get_or_create(nombre_rol=nombre)[0]

        for perfil in m['PerfilUsuario'].objects.select_related('usuario').order_by('pk'):
            self.crear_funcionario(perfil.usuario, perfil.rol, perfil.delegacion_id, perfil.cargo)

        # Usuarios sin perfil que aparecen como autores, responsables o revisores. En la auditoría,
        # los superusuarios quedan a nombre de su UsuarioMaestro y no necesitan Funcionario.
        ids = set(m['Actividad'].objects.values_list('funcionario_id', flat=True))
        ids |= set(m['Compromiso'].objects.values_list('responsable_id', flat=True))
        ids |= set(m['HistorialCompromiso'].objects.values_list('autor_id', flat=True))
        ids |= set(m['Evidencia'].objects.values_list('revisada_por_id', flat=True))
        ids |= set(m['Auditoria'].objects.filter(usuario__is_superuser=False).values_list('usuario_id', flat=True))
        ids -= {None, *self.funcionarios}
        for usuario in self.User.objects.filter(pk__in=ids).order_by('pk'):
            self.crear_funcionario(usuario, 'consulta')

        for usuario in self.User.objects.filter(is_superuser=True).order_by('pk'):
            m['UsuarioMaestro'].objects.create(
                usuario=usuario, identificador_maestro=usuario.username, nombre=_nombre(usuario),
                nivel_dominio='total', estado=usuario.is_active,
            )

        m['Delegacion'].objects.update(estado=F('activa'), ambito=F('territorio'))

    def delegado_de(self, delegacion):
        Funcionario = self.m['Funcionario']
        existente = (
            Funcionario.objects.filter(delegacion=delegacion, roles__nombre_rol='delegado').order_by('pk').first()
            or Funcionario.objects.filter(delegacion=delegacion).order_by('pk').first()
        )
        if existente:
            return existente
        # Ninguna persona de la delegación: delegado provisional con cuenta inactiva.
        username = _codigo_unico(self.User, 'username', f'delegado.{slugify(delegacion.nombre)}', 150)
        usuario = self.User.objects.create(
            username=username, first_name=f'Delegado {delegacion.nombre}', last_name=MARCA_PROVISIONAL,
            is_active=False, password=make_password(None),
        )
        _avisar(f'Delegación «{delegacion.nombre}» sin funcionarios: se creó el delegado provisional inactivo «{username}».')
        return self.crear_funcionario(usuario, 'delegado', delegacion.pk)

    # Medición

    def periodos(self):
        m = self.m
        for antiguo in m['PeriodoMedicion'].objects.order_by('pk'):
            periodo = m['Periodo'].objects.create(
                nombre=antiguo.nombre, fecha_inicio=antiguo.inicio, fecha_termino=antiguo.termino,
                dias_computables=_dias(antiguo.inicio, antiguo.termino), estado=antiguo.estado,
                umbral_minimo=antiguo.umbral_colectivo, version_parametros=antiguo.version_parametros,
            )
            m['ParametroVersionado'].objects.create(
                periodo=periodo, clave='maximo_cumplimiento', valor=str(antiguo.maximo_cumplimiento),
                descripcion='Tope de cumplimiento migrado desde PeriodoMedicion.',
            )

    def crear_periodo(self, inicio, termino, nombre):
        nombre = _codigo_unico(self.m['Periodo'], 'nombre', nombre, 255)
        estado = 'cerrado' if termino < timezone.localdate() else 'abierto'
        _avisar(f'Se creó el período «{nombre}» ({inicio} a {termino}, {estado}).')
        return self.m['Periodo'].objects.create(
            nombre=nombre, fecha_inicio=inicio, fecha_termino=termino,
            dias_computables=_dias(inicio, termino), estado=estado,
        )

    def periodo_exacto(self, inicio, termino):
        existente = self.m['Periodo'].objects.filter(fecha_inicio=inicio, fecha_termino=termino).first()
        return existente or self.crear_periodo(inicio, termino, f'Período {inicio:%d-%m-%Y} a {termino:%d-%m-%Y}')

    def periodo_que_contiene(self, fecha):
        existente = self.m['Periodo'].objects.filter(fecha_inicio__lte=fecha, fecha_termino__gte=fecha).order_by('fecha_inicio').first()
        if existente:
            return existente
        inicio = fecha.replace(day=1)
        termino = fecha.replace(day=calendar.monthrange(fecha.year, fecha.month)[1])
        return self.crear_periodo(inicio, termino, f'Período {fecha:%m-%Y}')

    def item(self, nombre, cargo, periodo, ponderacion=0):
        ItemMedible = self.m['ItemMedible']
        existente = ItemMedible.objects.filter(nombre=nombre, cargo=cargo, periodo=periodo).first()
        return existente or ItemMedible.objects.create(nombre=nombre, cargo=cargo, periodo=periodo, ponderacion=ponderacion)

    def catalogo(self):
        Catalogo = self.m['Catalogo']
        usados = set()
        for antiguo in self.m['CatalogoItem'].objects.order_by('pk'):
            codigo = antiguo.codigo
            if codigo in usados:
                codigo = _codigo_unico(Catalogo, 'codigo', f'{PREFIJOS[antiguo.categoria]}-{antiguo.codigo}', 50)
                _avisar(f'Código de catálogo repetido «{antiguo.codigo}» ({antiguo.categoria}): queda como «{codigo}».')
            usados.add(codigo)
            Catalogo.objects.create(
                codigo=codigo, nombre=antiguo.nombre, tipo=antiguo.categoria,
                area=antiguo.area or None, activo=antiguo.activo,
            )

    def catalogo_atencion(self, nombre):
        nombre = (nombre or '').strip()
        if not nombre:
            return None
        Catalogo = self.m['Catalogo']
        existente = Catalogo.objects.filter(tipo='atencion', nombre__iexact=nombre).first()
        if existente:
            return existente
        codigo = _codigo_unico(Catalogo, 'codigo', f'ATE-{slugify(nombre).upper()}', 50)
        _avisar(f'Tipo de atención «{nombre}» no estaba en el catálogo: se creó con código «{codigo}».')
        return Catalogo.objects.create(codigo=codigo, nombre=nombre, tipo='atencion', activo=True)

    def metas(self):
        m = self.m
        for antigua in m['MetaMedicion'].objects.select_related('delegacion').order_by('pk'):
            periodo = self.periodo_exacto(antigua.periodo_inicio, antigua.periodo_termino)
            funcionario = self.delegado_de(antigua.delegacion)
            item = self.item(antigua.nombre, funcionario.cargo, periodo, antigua.ponderador)
            m['Meta'].objects.create(
                item=item, funcionario=funcionario, valor_objetivo=antigua.objetivo,
                unidad='actividades', ponderador=antigua.ponderador,
            )
            if not antigua.activa:
                _avisar(f'La meta «{antigua.nombre}» de {antigua.delegacion.nombre} estaba inactiva; el diseño no tiene ese campo.')
            maximo = m['ParametroVersionado'].objects.filter(periodo=periodo, clave='maximo_cumplimiento').values_list('valor', flat=True).first() or '150'
            if float(antigua.tope_cumplimiento) != float(maximo):
                _avisar(f'La meta «{antigua.nombre}» de {antigua.delegacion.nombre} tenía tope {antigua.tope_cumplimiento}; el período usa {maximo}.')

    def revisar_ponderaciones(self):
        sumas = self.m['ItemMedible'].objects.values('cargo__nombre', 'periodo__nombre').annotate(total=Sum('ponderacion'))
        for fila in sumas:
            if fila['total'] != 100:
                _avisar(f"RN-001: los ítems de «{fila['cargo__nombre']}» en «{fila['periodo__nombre']}» suman {fila['total']} %.")

    # Operación

    def actividades(self):
        for actividad in self.m['Actividad'].objects.order_by('pk'):
            autor = self.funcionarios[actividad.funcionario_id]
            telefono = (actividad.telefono or '').strip()
            if len(telefono) > 20:
                _avisar(f'Actividad {actividad.codigo}: teléfono recortado a 20 caracteres.')
            actividad.codigo_verificador = actividad.codigo
            actividad.funcionario_autor = autor
            actividad.solicitud_problema = actividad.descripcion
            actividad.contacto_nombre = actividad.contacto or None
            actividad.contacto_telefono = telefono[:20] or None
            actividad.fecha_hora = datetime.combine(actividad.fecha, time.min, tzinfo=ZONA)
            # La contracción exige un ítem en toda actividad: una sin ítem de medición recibe uno genérico.
            nombre_item = (actividad.item_medicion or '').strip() or 'Sin ítem de medición'
            actividad.item = self.item(nombre_item, autor.cargo, self.periodo_que_contiene(actividad.fecha))
            actividad.catalogo = self.catalogo_atencion(actividad.tipo_atencion)
            actividad.version = 1
            # update_fields excluye «actualizada», así auto_now no cambia la fecha de modificación.
            actividad.save(update_fields=[
                'codigo_verificador', 'funcionario_autor', 'solicitud_problema', 'contacto_nombre',
                'contacto_telefono', 'fecha_hora', 'item', 'catalogo', 'version',
            ])

    def evidencias(self):
        estados = {True: 'aprobada', False: 'rechazada', None: 'pendiente'}
        numeros = Counter()
        for evidencia in self.m['Evidencia'].objects.select_related('actividad').order_by('actividad_id', 'creada', 'pk'):
            actividad = evidencia.actividad
            numeros[actividad.pk] += 1
            evidencia.codigo_evidencia = f'{actividad.codigo}-{numeros[actividad.pk]:02d}'
            evidencia.funcionario_autor_id = actividad.funcionario_autor_id
            evidencia.archivo_vinculo = evidencia.archivo.name
            evidencia.fecha_carga = evidencia.creada
            evidencia.metadatos = {'comentario': evidencia.comentario} if evidencia.comentario else None
            evidencia.estado_revision = estados[evidencia.aprobada]
            evidencia.save(update_fields=['codigo_evidencia', 'funcionario_autor', 'archivo_vinculo', 'fecha_carga', 'metadatos', 'estado_revision'])
            if evidencia.revisada_por_id and evidencia.aprobada is not None:
                self.m['Validacion'].objects.create(
                    evidencia=evidencia, funcionario_verificador=self.funcionarios[evidencia.revisada_por_id],
                    decision=estados[evidencia.aprobada], fecha=evidencia.creada, version=1,
                )

    def compromisos(self):
        for compromiso in self.m['Compromiso'].objects.order_by('pk'):
            compromiso.funcionario_responsable = self.funcionarios[compromiso.responsable_id]
            compromiso.origen = 'externo' if (compromiso.solicitante or '').strip() else 'interno'
            compromiso.version = 1
            compromiso.save(update_fields=['funcionario_responsable', 'origen', 'version'])
        for registro in self.m['HistorialCompromiso'].objects.order_by('pk'):
            registro.autor_funcionario = self.funcionarios[registro.autor_id]
            registro.save(update_fields=['autor_funcionario'])

    def auditoria(self):
        maestros = dict(self.m['UsuarioMaestro'].objects.values_list('usuario_id', 'pk'))
        for registro in self.m['Auditoria'].objects.order_by('pk'):
            detalle = registro.detalle
            if isinstance(detalle, dict):
                detalle = dict(detalle)
                anterior = detalle.pop('anterior', None)
                nuevo = detalle['nuevo'] if set(detalle) == {'nuevo'} else (detalle or None)
            else:
                anterior, nuevo = None, detalle
            registro.usuario_maestro_id = maestros.get(registro.usuario_id)
            registro.funcionario = None if registro.usuario_maestro_id else self.funcionarios.get(registro.usuario_id)
            registro.evento = registro.accion
            registro.identificador_registro = registro.identificador
            registro.valor_anterior = _texto(anterior)
            registro.valor_nuevo = _texto(nuevo)
            registro.save(update_fields=['usuario_maestro', 'funcionario', 'evento', 'identificador_registro', 'valor_anterior', 'valor_nuevo'])


def migrar(apps, schema_editor):
    migracion = _Migracion(apps)
    migracion.organizacion()
    migracion.periodos()
    migracion.catalogo()
    migracion.metas()
    migracion.actividades()
    migracion.revisar_ponderaciones()
    migracion.evidencias()
    migracion.compromisos()
    migracion.auditoria()


def revertir(apps, schema_editor):
    """Los datos antiguos siguen intactos: basta con borrar lo creado y vaciar los campos nuevos."""
    m = _Migracion(apps).m
    User = apps.get_model(settings.AUTH_USER_MODEL)
    provisionales = list(User.objects.filter(last_name=MARCA_PROVISIONAL, is_active=False, perfil__isnull=True).values_list('pk', flat=True))
    m['Validacion'].objects.all().delete()
    apps.get_model('delegaciones_app', 'Indicador').objects.all().delete()
    m['Auditoria'].objects.update(funcionario=None, usuario_maestro=None, evento=None, identificador_registro=None, valor_anterior=None, valor_nuevo=None)
    m['HistorialCompromiso'].objects.update(autor_funcionario=None)
    m['Compromiso'].objects.update(funcionario_responsable=None, item=None, origen=None, version=1)
    m['Evidencia'].objects.update(codigo_evidencia=None, funcionario_autor=None, archivo_vinculo=None, fecha_carga=None, metadatos=None, estado_revision='pendiente')
    m['Actividad'].objects.update(
        codigo_verificador=None, funcionario_autor=None, item=None, catalogo=None, compromiso=None, fecha_hora=None,
        solicitud_problema=None, contacto_nombre=None, contacto_telefono=None, version=1,
    )
    for nombre in ('Meta', 'ItemMedible', 'ParametroVersionado', 'Periodo', 'Catalogo', 'UsuarioMaestro', 'FuncionarioRol', 'Funcionario', 'Cargo', 'Rol'):
        m[nombre].objects.all().delete()
    m['Delegacion'].objects.update(estado=True, ambito=None)
    User.objects.filter(pk__in=provisionales).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('delegaciones_app', '0009_ampliar_operacion'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(migrar, revertir),
    ]
