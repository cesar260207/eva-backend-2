"""Mantenedores de las ocho tablas maestras.

Cada mantenedor se describe una sola vez en MANTENEDORES (modelo, formulario, columnas, búsqueda,
roles). Las cuatro vistas genéricas (lista, nuevo, editar y eliminar o desactivar) leen esa
descripción, así que no se repite código por tabla.
"""
import datetime
from dataclasses import dataclass
from typing import Callable, Optional

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import ProtectedError, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .auditoria import cambios_de_formulario
from .forms import CargoForm, CatalogoForm, DelegacionForm, FuncionarioForm, ItemMedibleForm, MetaForm, PeriodoForm, RolForm
from .models import Auditoria, Cargo, Catalogo, Delegacion, Funcionario, Indicador, ItemMedible, Meta, Periodo, Rol
from .permisos import ADMINISTRADOR, COORDINADOR, ROLES_DEL_SISTEMA, RolRequeridoMixin, rol_requerido, tiene_rol

ADMIN_Y_COORDINADOR = (ADMINISTRADOR, COORDINADOR)


@dataclass
class Mantenedor:
    slug: str
    titulo: str
    singular: str
    descripcion: str
    modelo: type
    form: type
    columnas: list  # (etiqueta, nombre de atributo o función del objeto)
    busqueda: tuple
    roles: tuple = ADMIN_Y_COORDINADOR
    baja: str = ''  # campo booleano que se desactiva en vez de eliminar la fila
    select_related: tuple = ()
    prefetch_related: tuple = ()
    con_actor: bool = False  # el formulario necesita saber quién lo usa
    ayuda: str = ''
    cambiar_baja: Optional[Callable] = None  # (objeto, nuevo_valor)
    bloqueo: Optional[Callable] = None  # (objeto, request) -> motivo o None
    advertencia_eliminar: Optional[Callable] = None  # (objeto) -> texto o None
    despues_de_guardar: Optional[Callable] = None  # (objeto)
    acciones_fila: Optional[Callable] = None  # (objeto) -> lista de acciones extra

    @property
    def entidad(self):
        return self.modelo.__name__

    def consulta(self):
        return self.modelo.objects.select_related(*self.select_related).prefetch_related(*self.prefetch_related)


# Comportamiento propio de cada mantenedor

def _cambiar_delegacion(delegacion, activa):
    delegacion.set_estado(activa)


def _cambiar_catalogo(elemento, activo):
    if activo:
        elemento.activar()
    else:
        elemento.desactivar()


def _cambiar_funcionario(funcionario, activo):
    funcionario.estado = activo
    funcionario.save(update_fields=['estado'])
    funcionario.usuario.is_active = activo
    funcionario.usuario.save(update_fields=['is_active'])


def _bloqueo_funcionario(funcionario, request):
    if funcionario.usuario_id == request.user.pk and funcionario.estado:
        return 'No puedes desactivar tu propia cuenta.'


def _bloqueo_rol(rol, request):
    if rol.nombre_rol in ROLES_DEL_SISTEMA:
        return f'«{rol}» es un rol del sistema: los permisos lo consultan por su nombre y no se elimina.'


def _advertencia_meta(meta):
    total = meta.indicadores.count()
    if total:
        return f'También se eliminarán los {total} indicador(es) calculados para esta meta.'


def _generar_indicador(meta):
    Indicador.generar(meta)


def _acciones_periodo(periodo):
    def accion(nombre, etiqueta, motivo=False):
        return {'url': reverse('periodo_accion', args=[periodo.pk, nombre]), 'etiqueta': etiqueta, 'motivo': motivo}

    if periodo.estado == 'borrador':
        return [accion('iniciar', 'Iniciar')]
    if periodo.estado == 'abierto':
        return [accion('cerrar', 'Cerrar')]
    return [accion('reabrir', 'Reabrir', motivo=True)]


MANTENEDORES = {mantenedor.slug: mantenedor for mantenedor in (
    Mantenedor(
        'delegaciones', 'Delegaciones', 'delegación', 'Unidades territoriales y su estado operativo.',
        Delegacion, DelegacionForm,
        [('Nombre', 'nombre'), ('Ámbito', 'ambito'), ('Énfasis', lambda d: (d.enfasis or '')[:90])],
        ('nombre__icontains', 'ambito__icontains', 'enfasis__icontains'),
        baja='estado', cambiar_baja=_cambiar_delegacion,
    ),
    Mantenedor(
        'cargos', 'Cargos', 'cargo', 'Cargos de los funcionarios y su vigencia.',
        Cargo, CargoForm,
        [('Nombre', 'nombre')],
        ('nombre__icontains',),
        baja='vigencia',
    ),
    Mantenedor(
        'roles', 'Roles', 'rol', 'Roles que definen los permisos del sistema.',
        Rol, RolForm,
        [('Rol', 'nombre_rol'), ('Funcionarios', lambda r: r.funcionarios.count())],
        ('nombre_rol__icontains',),
        roles=(ADMINISTRADOR,), bloqueo=_bloqueo_rol,
    ),
    Mantenedor(
        'funcionarios', 'Funcionarios', 'funcionario', 'Cuentas de acceso con su cargo, delegación y roles.',
        Funcionario, FuncionarioForm,
        [
            ('Nombre', 'nombre'), ('Usuario', 'identificador_institucional'), ('Cargo', 'cargo'), ('Delegación', 'delegacion'),
            ('Roles', lambda f: ', '.join(rol.nombre_rol for rol in f.roles.all())),
        ],
        ('nombre__icontains', 'identificador_institucional__icontains', 'usuario__email__icontains', 'cargo__nombre__icontains', 'delegacion__nombre__icontains', 'roles__nombre_rol__icontains'),
        roles=(ADMINISTRADOR,), baja='estado', select_related=('cargo', 'delegacion', 'usuario'), prefetch_related=('roles',),
        con_actor=True, cambiar_baja=_cambiar_funcionario, bloqueo=_bloqueo_funcionario,
        ayuda='Al crear un funcionario también se crea su cuenta de acceso. Al editar, deja la contraseña vacía para conservarla.',
    ),
    Mantenedor(
        'catalogo', 'Catálogo', 'elemento de catálogo', 'Actividades, servicios, tipos de atención e ítems normalizados.',
        Catalogo, CatalogoForm,
        [('Tipo', 'get_tipo_display'), ('Código', 'codigo'), ('Nombre', 'nombre'), ('Área', 'area')],
        ('codigo__icontains', 'nombre__icontains', 'tipo__icontains', 'area__icontains'),
        baja='activo', cambiar_baja=_cambiar_catalogo,
    ),
    Mantenedor(
        'periodos', 'Períodos', 'período', 'Ventanas de medición y su umbral colectivo.',
        Periodo, PeriodoForm,
        [('Nombre', 'nombre'), ('Inicio', 'fecha_inicio'), ('Término', 'fecha_termino'), ('Días', 'dias_computables'), ('Umbral (%)', 'umbral_minimo'), ('Estado', 'get_estado_display')],
        ('nombre__icontains', 'estado__icontains'),
        acciones_fila=_acciones_periodo,
        ayuda='El término debe ser igual o posterior al inicio. El estado cambia con las acciones Iniciar, Cerrar y Reabrir de la lista.',
    ),
    Mantenedor(
        'items', 'Ítems medibles', 'ítem medible', 'Ítems evaluados por cargo y período, con su ponderación.',
        ItemMedible, ItemMedibleForm,
        [('Nombre', 'nombre'), ('Cargo', 'cargo'), ('Período', 'periodo'), ('Servicio', 'servicio'), ('Ponderación (%)', 'ponderacion')],
        ('nombre__icontains', 'servicio__icontains', 'cargo__nombre__icontains', 'periodo__nombre__icontains'),
        select_related=('cargo', 'periodo'),
    ),
    Mantenedor(
        'metas', 'Metas', 'meta', 'Objetivos de cada funcionario por ítem medible.',
        Meta, MetaForm,
        [
            ('Ítem', lambda m: m.item.nombre), ('Período', lambda m: m.item.periodo), ('Funcionario', 'funcionario'),
            ('Delegación', lambda m: m.funcionario.delegacion), ('Objetivo', 'valor_objetivo'), ('Unidad', 'unidad'), ('Ponderador (%)', 'ponderador'),
        ],
        ('item__nombre__icontains', 'funcionario__nombre__icontains', 'funcionario__delegacion__nombre__icontains'),
        select_related=('item__periodo', 'funcionario__delegacion'),
        advertencia_eliminar=_advertencia_meta, despues_de_guardar=_generar_indicador,
    ),
)}


# Utilidades de presentación y auditoría

def _texto(objeto, acceso):
    valor = acceso(objeto) if callable(acceso) else getattr(objeto, acceso)
    if callable(valor):  # por ejemplo get_tipo_display
        valor = valor()
    if isinstance(valor, bool):
        return 'Sí' if valor else 'No'
    if isinstance(valor, datetime.date):
        return valor.strftime('%d-%m-%Y')
    if valor is None or valor == '':
        return '-'
    return str(valor)


def _auditar(request, config, accion, objeto, anterior=None, nuevo=None):
    Auditoria.registrar_evento(request.user, accion, config.entidad, objeto.pk, anterior, nuevo)


def _motivo_de_proteccion(error):
    cuentas = {}
    for objeto in error.protected_objects:
        nombre = objeto._meta.verbose_name_plural
        cuentas[nombre] = cuentas.get(nombre, 0) + 1
    return ', '.join(f'{total} {nombre}' for nombre, total in cuentas.items())


# Vistas genéricas

class MantenedorMixin(RolRequeridoMixin):
    """Busca el mantenedor por el slug de la URL y aplica sus roles permitidos."""

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.config = MANTENEDORES.get(kwargs.get('slug'))
        if self.config is None:
            raise Http404('Mantenedor no encontrado.')
        self.roles_permitidos = self.config.roles

    def get_queryset(self):
        return self.config.consulta()

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto.update(config=self.config, volver_url=self.url_lista())
        return contexto

    def url_lista(self):
        return reverse('mantenedor_lista', args=[self.config.slug])

    def get_success_url(self):
        return self.url_lista()


class MantenedorLista(MantenedorMixin, ListView):
    template_name = 'delegaciones_app/crud/lista.html'

    def get_queryset(self):
        registros = super().get_queryset()
        self.query = self.request.GET.get('q', '').strip()
        if self.query:
            filtros = Q()
            for campo in self.config.busqueda:
                filtros |= Q(**{campo: self.query})
            registros = registros.filter(filtros).distinct()
        return registros

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        config = self.config
        contexto['query'] = self.query
        contexto['columnas'] = [etiqueta for etiqueta, _ in config.columnas]
        contexto['total_columnas'] = len(config.columnas) + 1 + bool(config.baja)
        contexto['filas'] = [
            {
                'pk': registro.pk,
                'valores': [_texto(registro, acceso) for _, acceso in config.columnas],
                'activo': getattr(registro, config.baja) if config.baja else None,
                'acciones': config.acciones_fila(registro) if config.acciones_fila else [],
            }
            for registro in contexto['object_list']
        ]
        return contexto


class MantenedorFormularioMixin(MantenedorMixin):
    template_name = 'delegaciones_app/mantenedor_form.html'
    accion_titulo = ''

    def get_form_class(self):
        return self.config.form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.config.con_actor:
            kwargs['actor'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto.update(titulo=f'{self.accion_titulo} {self.config.singular}', ayuda=self.config.ayuda)
        return contexto

    def form_valid(self, form):
        editando = form.instance.pk is not None
        anterior, nuevo = cambios_de_formulario(form, getattr(form, 'campos_sin_auditar', ()))
        with transaction.atomic():
            respuesta = super().form_valid(form)
            _auditar(self.request, self.config, 'editar' if editando else 'crear', self.object, anterior, nuevo)
            if self.config.despues_de_guardar:
                self.config.despues_de_guardar(self.object)
        messages.success(self.request, f'Se guardó: {self.object}.')
        return respuesta


class MantenedorNuevo(MantenedorFormularioMixin, CreateView):
    accion_titulo = 'Agregar'


class MantenedorEditar(MantenedorFormularioMixin, UpdateView):
    accion_titulo = 'Modificar'


class MantenedorEliminar(MantenedorMixin, DeleteView):
    """Confirma y elimina la fila o, si el mantenedor tiene `baja`, la activa o desactiva."""

    template_name = 'delegaciones_app/mantenedor_confirmar_eliminar.html'

    def _bloqueo(self):
        return self.config.bloqueo(self.object, self.request) if self.config.bloqueo else None

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        config, objeto = self.config, self.object
        if config.baja:
            activo = getattr(objeto, config.baja)
            verbo, sustantivo = ('desactivar', 'desactivación') if activo else ('activar', 'activación')
            advertencia = 'La fila se conserva con su historial y se puede volver a activar.' if activo else None
        else:
            verbo, sustantivo = 'eliminar', 'eliminación'
            advertencia = config.advertencia_eliminar(objeto) if config.advertencia_eliminar else 'Esta acción no se puede deshacer.'
        contexto.update(
            objeto=objeto, titulo=f'{verbo.capitalize()} {config.singular}', advertencia=advertencia,
            pregunta=f'¿Confirmas {verbo}', boton=f'Confirmar {sustantivo}', bloqueo=self._bloqueo(),
            peligro=verbo != 'activar',
        )
        return contexto

    def form_valid(self, form):
        objeto, config = self.object, self.config
        motivo = self._bloqueo()
        if motivo:
            messages.error(self.request, motivo)
            return redirect(self.get_success_url())
        if config.baja:
            return self._cambiar_baja(objeto)
        return self._eliminar(objeto)

    def _cambiar_baja(self, objeto):
        config = self.config
        activar = not getattr(objeto, config.baja)
        with transaction.atomic():
            if config.cambiar_baja:
                config.cambiar_baja(objeto, activar)
            else:
                setattr(objeto, config.baja, activar)
                objeto.save(update_fields=[config.baja])
            _auditar(self.request, config, 'activar' if activar else 'desactivar', objeto, {config.baja: not activar}, {config.baja: activar})
        messages.success(self.request, f'{objeto}: {"activado" if activar else "desactivado"}.')
        return redirect(self.get_success_url())

    def _eliminar(self, objeto):
        descripcion = str(objeto)
        try:
            with transaction.atomic():
                _auditar(self.request, self.config, 'eliminar', objeto, {'descripcion': descripcion})
                objeto.delete()
        except ProtectedError as error:
            messages.error(self.request, f'No se puede eliminar «{descripcion}» porque tiene registros asociados: {_motivo_de_proteccion(error)}.')
        except ValidationError as error:
            messages.error(self.request, ' '.join(error.messages))
        else:
            messages.success(self.request, f'Se eliminó: {descripcion}.')
        return redirect(self.get_success_url())


class PeriodoAccion(RolRequeridoMixin, View):
    """Iniciar, cerrar y reabrir un período (las reglas están en los métodos del modelo)."""

    roles_permitidos = ADMIN_Y_COORDINADOR
    ACCIONES = {'iniciar': 'iniciado', 'cerrar': 'cerrado', 'reabrir': 'reabierto'}

    def post(self, request, pk, accion):
        if accion not in self.ACCIONES:
            raise Http404('Acción no válida.')
        periodo = get_object_or_404(Periodo, pk=pk)
        try:
            with transaction.atomic():
                if accion == 'iniciar':
                    periodo.iniciar_periodo()
                elif accion == 'cerrar':
                    periodo.cerrar_periodo()
                else:
                    periodo.reabrir_periodo(request.POST.get('motivo', ''), request.user)
                if accion != 'reabrir':  # reabrir_periodo ya deja su propio registro de auditoría
                    Auditoria.registrar_evento(request.user, f'{accion}_periodo', 'Periodo', periodo.pk, None, {'estado': periodo.estado})
        except ValidationError as error:
            messages.error(request, ' '.join(error.messages))
        else:
            messages.success(request, f'Período «{periodo}» {self.ACCIONES[accion]}.')
        return redirect('mantenedor_lista', slug='periodos')


@rol_requerido(*ADMIN_Y_COORDINADOR)
def indice(request):
    """Índice de los ocho mantenedores; los que el usuario no puede usar aparecen deshabilitados."""
    tarjetas = [
        {'slug': m.slug, 'titulo': m.titulo, 'descripcion': m.descripcion, 'permitido': tiene_rol(request.user, *m.roles)}
        for m in MANTENEDORES.values()
    ]
    return render(request, 'delegaciones_app/mantenedores.html', {'tarjetas': tarjetas, 'puede_auditar': tiene_rol(request.user, ADMINISTRADOR)})
