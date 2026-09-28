import uuid
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import ActividadForm, CatalogoItemForm, CompromisoForm, DelegacionForm, EvidenciaForm, EvidenciaMantenedorForm
from .models import (
    Actividad, Auditoria, CatalogoItem, Compromiso, Delegacion, Evidencia,
    HistorialCompromiso, MetaMedicion, PerfilUsuario, PeriodoMedicion,
)


# Ocho mantenedores: dos por cada integrante de un equipo de cuatro personas.
# El CRUD efectivo se administra desde Django Admin, tal como exige la pauta;
# estas vistas entregan la navegación, búsqueda ORM y los controles visuales.
MANTENEDORES = {
    'delegaciones': {'titulo': 'Delegaciones', 'descripcion': 'Unidades territoriales y su estado operativo.', 'modelo': Delegacion, 'campos': ('nombre', 'territorio', 'enfasis', 'activa'), 'busqueda': ('nombre__icontains', 'territorio__icontains', 'enfasis__icontains')},
    'perfiles': {'titulo': 'Perfiles de usuario', 'descripcion': 'Roles, cargos y ámbitos de acceso del sistema.', 'modelo': PerfilUsuario, 'campos': ('usuario', 'rol', 'delegacion', 'cargo'), 'busqueda': ('usuario__username__icontains', 'cargo__icontains', 'rol__icontains')},
    'catalogo': {'titulo': 'Catálogo de ítems', 'descripcion': 'Actividades, servicios e ítems de medición normalizados.', 'modelo': CatalogoItem, 'campos': ('categoria', 'codigo', 'nombre', 'area', 'activo'), 'busqueda': ('codigo__icontains', 'nombre__icontains', 'area__icontains')},
    'periodos': {'titulo': 'Períodos de medición', 'descripcion': 'Ventanas temporales y parámetros de evaluación.', 'modelo': PeriodoMedicion, 'campos': ('nombre', 'inicio', 'termino', 'estado'), 'busqueda': ('nombre__icontains', 'estado__icontains')},
    'actividades': {'titulo': 'Actividades', 'descripcion': 'Registros territoriales ingresados por funcionarios.', 'modelo': Actividad, 'campos': ('codigo', 'delegacion', 'funcionario', 'fecha', 'estado'), 'busqueda': ('codigo__icontains', 'descripcion__icontains', 'item_medicion__icontains')},
    'evidencias': {'titulo': 'Evidencias', 'descripcion': 'Archivos de respaldo asociados a actividades.', 'modelo': Evidencia, 'campos': ('actividad', 'archivo', 'aprobada', 'revisada_por', 'creada'), 'busqueda': ('actividad__codigo__icontains', 'comentario__icontains')},
    'compromisos': {'titulo': 'Compromisos', 'descripcion': 'Acuerdos territoriales, responsables y plazos.', 'modelo': Compromiso, 'campos': ('folio', 'delegacion', 'responsable', 'eje', 'estado', 'fecha_comprometida'), 'busqueda': ('folio__icontains', 'descripcion__icontains', 'solicitante__icontains')},
    'metas': {'titulo': 'Metas de medición', 'descripcion': 'Objetivos e indicadores de cumplimiento por delegación.', 'modelo': MetaMedicion, 'campos': ('delegacion', 'nombre', 'objetivo', 'avance', 'activa'), 'busqueda': ('nombre__icontains', 'delegacion__nombre__icontains')},
}


def _etiqueta_campo(campo):
    return campo.replace('_', ' ').capitalize()


def _valor_mantenedor(objeto, campo):
    valor = getattr(objeto, campo)
    if isinstance(valor, bool):
        return 'Sí' if valor else 'No'
    return str(valor) if valor is not None else '—'


def _perfil(user):
    if not user.is_authenticated:
        return None
    return PerfilUsuario.objects.select_related('delegacion').filter(usuario=user).first()


def _puede_ver_todo(user):
    perfil = _perfil(user)
    return user.is_superuser or perfil and perfil.rol in {'administrador', 'coordinador'}


def _puede_administrar_perfiles(user):
    perfil = _perfil(user)
    return user.is_superuser or (perfil and perfil.rol == 'administrador')


def _actividades_autorizadas(user):
    queryset = Actividad.objects.select_related('delegacion', 'funcionario')
    if _puede_ver_todo(user):
        return queryset
    perfil = _perfil(user)
    if perfil and perfil.delegacion_id:
        return queryset.filter(delegacion=perfil.delegacion)
    return queryset.filter(funcionario=user)


def _puede_validar(user):
    perfil = _perfil(user)
    return _puede_ver_todo(user) or bool(perfil and perfil.rol == 'verificador')


def _bloqueo_actividad(user, actividad, puede_ver_todo):
    """Motivo por el que `user` no puede modificar ni eliminar la actividad, o None.

    Una actividad aprobada queda cerrada para todos: ya suma en
    MetaMedicion.avance_calculado y cambiarla alteraría ese avance sin revisión.
    """
    if actividad.estado == 'aprobada':
        return 'Actividad aprobada: ya suma al avance de las metas y no se modifica.'
    if not (puede_ver_todo or actividad.funcionario_id == user.pk):
        return 'Solo quien registró la actividad o la coordinación puede modificarla.'
    return None


def _codigo_actividad():
    return f'EVD-{datetime.now():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}'


def _calcular_estado_compromiso(compromiso):
    """Traduce el estado persistido de un Compromiso a una etiqueta y clase
    Bootstrap para la interfaz, calculando la alerta de vencimiento en vivo."""
    if compromiso.estado == 'realizado':
        return 'Realizado', 'success'
    if compromiso.estado == 'proceso':
        return 'En proceso', 'primary'
    if compromiso.vencido:
        return 'Alerta Roja por Vencimiento', 'danger'
    return 'Pendiente', 'warning'


def _decorar_compromiso(compromiso):
    compromiso.estado_display, compromiso.estado_class = _calcular_estado_compromiso(compromiso)
    return compromiso


def index(request):
    ejes = [nombre for nombre, _ in Compromiso.EJES]
    delegaciones = list(Delegacion.objects.filter(activa=True).values_list('nombre', flat=True))
    compromisos = list(Compromiso.objects.select_related('delegacion'))
    for compromiso in compromisos:
        _decorar_compromiso(compromiso)
    alertas = sum(1 for item in compromisos if item.estado_display == 'Alerta Roja por Vencimiento')
    promedio = MetaMedicion.objects.filter(activa=True).aggregate(promedio=Avg('avance'))['promedio']
    metas_activas = list(MetaMedicion.objects.filter(activa=True))
    cumplimiento_promedio = round(
        sum(meta.cumplimiento for meta in metas_activas) / len(metas_activas), 1
    ) if metas_activas else 0
    return render(request, 'delegaciones_app/index.html', {
        'ejes': ejes,
        'delegaciones': delegaciones,
        'total_solicitudes': len(compromisos),
        'alertas': alertas,
        'promedio': cumplimiento_promedio,
    })


def solicitudes(request):
    query = request.GET.get('q', '').strip()
    compromisos = Compromiso.objects.select_related('delegacion')
    if query:
        compromisos = compromisos.filter(Q(folio__icontains=query) | Q(descripcion__icontains=query) | Q(delegacion__nombre__icontains=query))
    compromisos = list(compromisos)
    for compromiso in compromisos:
        _decorar_compromiso(compromiso)

    contexto = {
        'solicitudes': compromisos,
        'query': query,
        'total': len(compromisos),
        'pendientes': sum(1 for item in compromisos if item.estado_display == 'Pendiente'),
        'en_proceso': sum(1 for item in compromisos if item.estado_display == 'En proceso'),
        'alertas': sum(1 for item in compromisos if item.estado_display == 'Alerta Roja por Vencimiento'),
    }
    return render(request, 'delegaciones_app/solicitudes.html', contexto)


def delegacion_detalle(request, nombre):
    compromisos = list(Compromiso.objects.select_related('delegacion').filter(delegacion__nombre=nombre))
    for compromiso in compromisos:
        _decorar_compromiso(compromiso)

    return render(request, 'delegaciones_app/delegacion_detalle.html', {
        'nombre': nombre,
        'solicitudes': compromisos,
    })


def actividad_nueva(request):
    if not request.user.is_authenticated:
        return redirect('login')
    form = ActividadForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        actividad = form.save(commit=False)
        actividad.funcionario = request.user
        actividad.codigo = _codigo_actividad()
        actividad.estado = 'pendiente'
        actividad.save()
        Auditoria.objects.create(usuario=request.user, accion='crear', entidad='Actividad', identificador=actividad.codigo)
        messages.success(request, f'Actividad creada con código {actividad.codigo}.')
        return redirect('actividad_detalle', actividad.codigo)
    return render(request, 'delegaciones_app/actividad_form.html', {'form': form, 'titulo': 'Registrar actividad'})


@login_required
def actividades(request):
    query = request.GET.get('q', '').strip()
    registros = _actividades_autorizadas(request.user)
    if query:
        registros = registros.filter(Q(codigo__icontains=query) | Q(descripcion__icontains=query) | Q(item_medicion__icontains=query))
    puede_ver_todo = _puede_ver_todo(request.user)
    registros = list(registros)
    for actividad in registros:
        actividad.bloqueo = _bloqueo_actividad(request.user, actividad, puede_ver_todo)
    return render(request, 'delegaciones_app/actividades.html', {'actividades': registros, 'query': query, 'puede_crear': request.user.is_authenticated})


@login_required
def actividad_detalle(request, codigo):
    actividad = get_object_or_404(_actividades_autorizadas(request.user), codigo=codigo)
    evidencia_form = EvidenciaForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and evidencia_form.is_valid():
        evidencia = evidencia_form.save(commit=False)
        evidencia.actividad = actividad
        evidencia.save()
        actividad.estado = 'pendiente'
        actividad.save(update_fields=['estado', 'actualizada'])
        Auditoria.objects.create(usuario=request.user, accion='cargar_evidencia', entidad='Actividad', identificador=actividad.codigo)
        messages.success(request, 'Evidencia cargada y enviada a revisión.')
        return redirect('actividad_detalle', codigo=codigo)
    return render(request, 'delegaciones_app/actividad_detalle.html', {'actividad': actividad, 'evidencia_form': evidencia_form, 'puede_validar': _puede_ver_todo(request.user) or _perfil(request.user) and _perfil(request.user).rol == 'verificador'})


@login_required
def revisar_actividad(request, codigo, decision):
    if request.method != 'POST' or decision not in {'aprobar', 'rechazar'}:
        return redirect('actividad_detalle', codigo=codigo)
    if not (_puede_ver_todo(request.user) or _perfil(request.user) and _perfil(request.user).rol == 'verificador'):
        return redirect('actividad_detalle', codigo=codigo)
    actividad = get_object_or_404(Actividad, codigo=codigo)
    actividad.estado = 'aprobada' if decision == 'aprobar' else 'rechazada'
    actividad.save(update_fields=['estado', 'actualizada'])
    for evidencia in actividad.evidencias.all():
        evidencia.aprobada = decision == 'aprobar'
        evidencia.revisada_por = request.user
        evidencia.save(update_fields=['aprobada', 'revisada_por'])
    Auditoria.objects.create(usuario=request.user, accion=decision, entidad='Actividad', identificador=actividad.codigo)
    messages.success(request, f'Actividad {actividad.codigo}: {actividad.get_estado_display()}.')
    return redirect('actividad_detalle', codigo=codigo)


@login_required
def actividad_editar(request, codigo):
    actividad = get_object_or_404(_actividades_autorizadas(request.user), codigo=codigo)
    bloqueo = _bloqueo_actividad(request.user, actividad, _puede_ver_todo(request.user))
    if bloqueo:
        messages.error(request, bloqueo)
        return redirect('actividad_detalle', codigo=codigo)
    estado_anterior = actividad.estado
    form = ActividadForm(request.POST or None, instance=actividad, user=request.user)
    if request.method == 'POST' and form.is_valid():
        actividad = form.save(commit=False)
        if estado_anterior == 'rechazada':
            # Corregir una actividad rechazada la devuelve a la cola de revisión.
            actividad.estado = 'pendiente'
        actividad.save()
        Auditoria.objects.create(
            usuario=request.user,
            accion='editar',
            entidad='Actividad',
            identificador=actividad.codigo,
            detalle={'campos': form.changed_data, 'estado_anterior': estado_anterior, 'estado': actividad.estado},
        )
        messages.success(request, f'Actividad {actividad.codigo} actualizada.')
        return redirect('actividad_detalle', codigo=actividad.codigo)
    return render(request, 'delegaciones_app/actividad_form.html', {
        'form': form,
        'titulo': f'Modificar actividad {actividad.codigo}',
        'actividad': actividad,
    })


@login_required
def actividad_eliminar(request, codigo):
    actividad = get_object_or_404(_actividades_autorizadas(request.user), codigo=codigo)
    bloqueo = _bloqueo_actividad(request.user, actividad, _puede_ver_todo(request.user))
    if bloqueo:
        messages.error(request, bloqueo)
        return redirect('actividad_detalle', codigo=codigo)
    # Evidencia usa on_delete=CASCADE: borrar la actividad borra también sus evidencias.
    total_evidencias = actividad.evidencias.count()
    if request.method == 'POST':
        Auditoria.objects.create(
            usuario=request.user,
            accion='eliminar',
            entidad='Actividad',
            identificador=actividad.codigo,
            detalle={'delegacion': actividad.delegacion.nombre, 'evidencias_eliminadas': total_evidencias},
        )
        actividad.delete()
        messages.success(request, f'Actividad {codigo} eliminada junto con {total_evidencias} evidencia(s).')
        return redirect('actividades')
    return render(request, 'delegaciones_app/actividad_confirmar_eliminar.html', {
        'actividad': actividad,
        'total_evidencias': total_evidencias,
    })


@login_required
def delegaciones_crud(request):
    if not _puede_ver_todo(request.user):
        return redirect('inicio')
    query = request.GET.get('q', '').strip()
    delegaciones = Delegacion.objects.all()
    if query:
        delegaciones = delegaciones.filter(
            Q(nombre__icontains=query)
            | Q(territorio__icontains=query)
            | Q(enfasis__icontains=query)
        )
    return render(request, 'delegaciones_app/delegaciones_crud.html', {
        'delegaciones': delegaciones,
        'query': query,
    })


@login_required
def delegacion_cambiar_estado(request, pk):
    if request.method != 'POST' or not _puede_ver_todo(request.user):
        return redirect('delegaciones_crud')
    delegacion = get_object_or_404(Delegacion, pk=pk)
    delegacion.activa = not delegacion.activa
    delegacion.save(update_fields=['activa'])
    Auditoria.objects.create(
        usuario=request.user,
        accion='activar' if delegacion.activa else 'desactivar',
        entidad='Delegacion',
        identificador=str(delegacion.pk),
    )
    messages.success(
        request,
        f'Delegacion {delegacion.nombre}: {"activa" if delegacion.activa else "inactiva"}.',
    )
    return redirect('delegaciones_crud')


@login_required
def catalogo_lista(request):
    if not _puede_ver_todo(request.user):
        return redirect('inicio')
    query = request.GET.get('q', '').strip()
    registros = CatalogoItem.objects.all()
    if query:
        registros = registros.filter(
            Q(codigo__icontains=query)
            | Q(nombre__icontains=query)
            | Q(area__icontains=query)
            | Q(categoria__icontains=query)
        )
    return render(request, 'delegaciones_app/catalogo_lista.html', {
        'registros': registros,
        'query': query,
    })


@login_required
def catalogo_form(request, pk=None):
    if not _puede_ver_todo(request.user):
        return redirect('inicio')
    instancia = get_object_or_404(CatalogoItem, pk=pk) if pk else None
    form = CatalogoItemForm(request.POST or None, instance=instancia)
    if request.method == 'POST' and form.is_valid():
        objeto = form.save()
        Auditoria.objects.create(
            usuario=request.user,
            accion='editar' if instancia else 'crear',
            entidad='CatalogoItem',
            identificador=str(objeto.pk),
            detalle={'codigo': objeto.codigo, 'nombre': objeto.nombre},
        )
        messages.success(request, f'Elemento de catalogo "{objeto.nombre}" guardado.')
        return redirect('catalogo_lista')
    return render(request, 'delegaciones_app/catalogo_form.html', {
        'form': form,
        'titulo': 'Modificar elemento' if instancia else 'Agregar elemento al catalogo',
        'instancia': instancia,
    })


@login_required
def catalogo_eliminar(request, pk):
    if not _puede_ver_todo(request.user):
        return redirect('inicio')
    objeto = get_object_or_404(CatalogoItem, pk=pk)
    if request.method == 'POST':
        nombre, identificador = objeto.nombre, str(objeto.pk)
        Auditoria.objects.create(
            usuario=request.user,
            accion='eliminar',
            entidad='CatalogoItem',
            identificador=identificador,
            detalle={'codigo': objeto.codigo, 'nombre': nombre},
        )
        objeto.delete()
        messages.success(request, f'Elemento de catalogo "{nombre}" eliminado.')
        return redirect('catalogo_lista')
    return render(request, 'delegaciones_app/catalogo_confirmar_eliminar.html', {
        'objeto': objeto,
    })


@login_required
def evidencia_lista(request):
    if not _puede_ver_todo(request.user):
        return redirect('inicio')
    query = request.GET.get('q', '').strip()
    registros = Evidencia.objects.select_related('actividad', 'revisada_por').order_by('-creada')
    if query:
        registros = registros.filter(
            Q(actividad__codigo__icontains=query)
            | Q(comentario__icontains=query)
        )
    return render(request, 'delegaciones_app/evidencia_lista.html', {
        'registros': registros,
        'query': query,
    })


@login_required
def evidencia_form(request, pk=None):
    if not _puede_ver_todo(request.user):
        return redirect('inicio')
    instancia = get_object_or_404(Evidencia, pk=pk) if pk else None
    # Al editar sin subir un archivo nuevo, el FileField conserva el actual.
    form = EvidenciaMantenedorForm(
        request.POST or None, request.FILES or None,
        instance=instancia, puede_validar=_puede_validar(request.user),
    )
    if request.method == 'POST' and form.is_valid():
        objeto = form.save(commit=False)
        if 'aprobada' in form.changed_data:
            objeto.revisada_por = request.user if objeto.aprobada is not None else None
        objeto.save()
        Auditoria.objects.create(
            usuario=request.user,
            accion='editar' if instancia else 'crear',
            entidad='Evidencia',
            identificador=str(objeto.pk),
            detalle={'actividad': objeto.actividad.codigo, 'archivo': objeto.archivo.name},
        )
        messages.success(request, f'Evidencia de la actividad {objeto.actividad.codigo} guardada.')
        return redirect('evidencia_lista')
    return render(request, 'delegaciones_app/evidencia_form.html', {
        'form': form,
        'titulo': 'Modificar evidencia' if instancia else 'Agregar evidencia',
        'instancia': instancia,
    })


@login_required
def evidencia_eliminar(request, pk):
    if not _puede_ver_todo(request.user):
        return redirect('inicio')
    objeto = get_object_or_404(Evidencia.objects.select_related('actividad'), pk=pk)
    if request.method == 'POST':
        Auditoria.objects.create(
            usuario=request.user,
            accion='eliminar',
            entidad='Evidencia',
            identificador=str(objeto.pk),
            detalle={'actividad': objeto.actividad.codigo, 'archivo': objeto.archivo.name},
        )
        objeto.delete()
        messages.success(request, f'Evidencia de la actividad {objeto.actividad.codigo} eliminada.')
        return redirect('evidencia_lista')
    return render(request, 'delegaciones_app/evidencia_confirmar_eliminar.html', {
        'objeto': objeto,
    })


@login_required
def mantenedores(request):
    """Índice de los ocho mantenedores requeridos para el equipo."""
    if not _puede_ver_todo(request.user):
        return redirect('inicio')
    return render(request, 'delegaciones_app/mantenedores.html', {
        'mantenedores': [dict(configuracion, slug=slug) for slug, configuracion in MANTENEDORES.items()],
    })


@login_required
def mantenedor_lista(request, slug):
    if not _puede_ver_todo(request.user):
        return redirect('inicio')
    try:
        configuracion = MANTENEDORES[slug]
    except KeyError as error:
        from django.http import Http404
        raise Http404('Mantenedor no encontrado.') from error

    query = request.GET.get('q', '').strip()
    registros = configuracion['modelo'].objects.all()
    if query:
        filtros = Q()
        for campo in configuracion['busqueda']:
            filtros |= Q(**{campo: query})
        registros = registros.filter(filtros)
    registros = registros.select_related()
    modelo = configuracion['modelo']
    app_label, model_name = modelo._meta.app_label, modelo._meta.model_name
    filas = [
        {'pk': registro.pk, 'valores': [_valor_mantenedor(registro, campo) for campo in configuracion['campos']]}
        for registro in registros
    ]
    return render(request, 'delegaciones_app/mantenedor_lista.html', {
        'mantenedor': configuracion,
        'query': query,
        'columnas': [_etiqueta_campo(campo) for campo in configuracion['campos']],
        'filas': filas,
        'url_agregar': reverse(f'admin:{app_label}_{model_name}_add'),
        'url_editar_base': f'/admin/{app_label}/{model_name}/',
    })


@login_required
def delegacion_form(request, pk=None):
    if not _puede_ver_todo(request.user):
        return redirect('inicio')
    delegacion = get_object_or_404(Delegacion, pk=pk) if pk else None
    form = DelegacionForm(request.POST or None, instance=delegacion)
    if request.method == 'POST' and form.is_valid():
        objeto = form.save()
        Auditoria.objects.create(usuario=request.user, accion='editar' if pk else 'crear', entidad='Delegacion', identificador=str(objeto.pk))
        messages.success(request, 'Delegación guardada correctamente.')
        return redirect('delegaciones_crud')
    return render(request, 'delegaciones_app/delegacion_form.html', {'form': form, 'titulo': 'Editar delegación' if pk else 'Nueva delegación'})


@login_required
def compromiso_nuevo(request):
    perfil = _perfil(request.user)
    if not (_puede_ver_todo(request.user) or perfil and perfil.rol in {'delegado', 'funcionario'}):
        return redirect('inicio')
    form = CompromisoForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        compromiso = form.save(commit=False)
        if perfil and perfil.rol in {'delegado', 'funcionario'}:
            compromiso.responsable = request.user
        compromiso.folio = f'AGR-{datetime.now():%Y%m%d}-{uuid.uuid4().hex[:5].upper()}'
        compromiso.save()
        HistorialCompromiso.objects.create(compromiso=compromiso, autor=request.user, estado_anterior='', estado_nuevo=compromiso.estado, observacion='Creación del compromiso')
        Auditoria.objects.create(usuario=request.user, accion='crear', entidad='Compromiso', identificador=compromiso.folio)
        messages.success(request, f'Compromiso creado con folio {compromiso.folio}.')
        return redirect('agenda')
    return render(request, 'delegaciones_app/compromiso_form.html', {'form': form, 'titulo': 'Nuevo compromiso'})


@login_required
def compromiso_estado(request, pk, estado):
    if request.method != 'POST' or estado not in {'ingresado', 'pendiente', 'proceso', 'realizado'}:
        return redirect('agenda')
    perfil = _perfil(request.user)
    queryset = Compromiso.objects.all()
    if perfil and perfil.delegacion_id and not _puede_ver_todo(request.user):
        queryset = queryset.filter(delegacion=perfil.delegacion)
    compromiso = get_object_or_404(queryset, pk=pk)
    anterior = compromiso.estado
    compromiso.estado = estado
    compromiso.save(update_fields=['estado'])
    HistorialCompromiso.objects.create(compromiso=compromiso, autor=request.user, estado_anterior=anterior, estado_nuevo=estado)
    Auditoria.objects.create(usuario=request.user, accion='cambio_estado', entidad='Compromiso', identificador=compromiso.folio, detalle={'anterior': anterior, 'nuevo': estado})
    messages.success(request, f'El compromiso {compromiso.folio} cambió a {compromiso.get_estado_display()}.')
    return redirect('agenda')


def agenda(request):
    perfil = _perfil(request.user) if request.user.is_authenticated else None
    compromisos = Compromiso.objects.select_related('delegacion', 'responsable').all()
    if perfil and perfil.delegacion_id and not _puede_ver_todo(request.user):
        compromisos = compromisos.filter(delegacion=perfil.delegacion)
    delegacion_id = request.GET.get('delegacion')
    estado = request.GET.get('estado')
    query = request.GET.get('q', '').strip()
    if delegacion_id:
        compromisos = compromisos.filter(delegacion_id=delegacion_id)
    if estado:
        compromisos = compromisos.filter(estado=estado)
    if query:
        compromisos = compromisos.filter(
            Q(folio__icontains=query)
            | Q(descripcion__icontains=query)
            | Q(solicitante__icontains=query)
            | Q(delegacion__nombre__icontains=query)
        )
    compromisos = list(compromisos)
    for compromiso in compromisos:
        compromiso.estado_display = 'Vencido' if compromiso.vencido else compromiso.get_estado_display()
        compromiso.estado_class = 'danger' if compromiso.vencido else ('success' if compromiso.estado == 'realizado' else 'warning')
    return render(request, 'delegaciones_app/agenda.html', {
        'compromisos': compromisos,
        'delegaciones_filtro': Delegacion.objects.filter(activa=True),
        'estado_filtro': estado or '',
        'delegacion_filtro': delegacion_id or '',
        'query': query,
        'proximos': sum(1 for item in compromisos if item.estado != 'realizado' and not item.vencido),
        'vencidos': sum(1 for item in compromisos if item.vencido),
        'realizados': sum(1 for item in compromisos if item.estado == 'realizado'),
    })


def institucional(request):
    delegaciones = [
        ('Avenida del Mar', 'Borde costero, turismo, residencial y servicios', 'Coordinación estacional, espacios públicos, seguridad y prevención.'),
        ('Centro', 'Centro histórico, administrativo, comercial y patrimonial', 'Atención territorial, convivencia urbana y gestión del espacio público.'),
        ('La Antena', 'Sector urbano oriental y barrios asociados', 'Participación vecinal, apoyo social y coordinación de servicios.'),
        ('Las Compañías', 'Sector urbano norte de alta densidad', 'Gestión comunitaria, acceso a programas y operativos sociales.'),
        ('La Pampa', 'Sector urbano sur y áreas residenciales', 'Asistencia social, subsidios, aseo, alumbrado y plazas.'),
        ('Rural', 'Localidades y comunidades rurales dispersas', 'Acercamiento de servicios, emergencias y coordinación intersectorial.'),
    ]
    return render(request, 'delegaciones_app/institucional.html', {
        'delegaciones': delegaciones,
        'poblacion': '250.141',
        'urbano': '89,14 %',
        'rural': '10,86 %',
    })


@login_required
def perfiles_usuario(request):
    if not _puede_administrar_perfiles(request.user):
        return redirect('inicio')

    query = request.GET.get('q', '').strip()
    perfiles = PerfilUsuario.objects.select_related('usuario', 'delegacion').all()

    if query:
        perfiles = perfiles.filter(
            Q(usuario__username__icontains=query)
            | Q(usuario__first_name__icontains=query)
            | Q(usuario__last_name__icontains=query)
            | Q(rol__icontains=query)
            | Q(delegacion__nombre__icontains=query)
            | Q(cargo__icontains=query)
        )

    conteos_por_rol = {
        fila['rol']: fila['total']
        for fila in PerfilUsuario.objects.values('rol').annotate(total=Count('pk'))
    }
    resumen_roles = [
        {'nombre': etiqueta, 'total': conteos_por_rol.get(codigo, 0)}
        for codigo, etiqueta in PerfilUsuario.ROLES
    ]

    return render(request, 'delegaciones_app/perfiles_usuario.html', {
        'perfiles': perfiles,
        'query': query,
        'total_perfiles': perfiles.count(),
        'resumen_roles': resumen_roles,
    })


@login_required
def periodos_medicion(request):
    if not _puede_ver_todo(request.user):
        return redirect('inicio')

    query = request.GET.get('q', '').strip()
    todos_los_periodos = PeriodoMedicion.objects.all()
    periodos = todos_los_periodos.order_by('-inicio', 'nombre')

    if query:
        periodos = periodos.filter(
            Q(nombre__icontains=query)
            | Q(estado__icontains=query)
        )

    resumen_estados = [
        {
            'nombre': etiqueta,
            'total': todos_los_periodos.filter(estado=codigo).count(),
        }
        for codigo, etiqueta in PeriodoMedicion.ESTADOS
    ]
    periodo_abierto = todos_los_periodos.filter(
        estado='abierto'
    ).order_by('-inicio').first()

    return render(request, 'delegaciones_app/periodos_medicion.html', {
        'periodos': periodos,
        'query': query,
        'total_periodos': todos_los_periodos.count(),
        'resumen_estados': resumen_estados,
        'periodo_abierto': periodo_abierto,
    })
