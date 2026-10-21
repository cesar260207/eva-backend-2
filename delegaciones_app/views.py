import uuid
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ActividadForm, CompromisoForm, EvidenciaForm
from .models import Actividad, Auditoria, Compromiso, Delegacion, HistorialCompromiso, MetaMedicion, PerfilUsuario


def _perfil(user):
    if not user.is_authenticated:
        return None
    return PerfilUsuario.objects.select_related('delegacion').filter(usuario=user).first()


def _puede_ver_todo(user):
    perfil = _perfil(user)
    return user.is_superuser or perfil and perfil.rol in {'administrador', 'coordinador'}


def _actividades_autorizadas(user):
    queryset = Actividad.objects.select_related('delegacion', 'funcionario')
    if _puede_ver_todo(user):
        return queryset
    perfil = _perfil(user)
    if perfil and perfil.delegacion_id:
        return queryset.filter(delegacion=perfil.delegacion)
    return queryset.filter(funcionario=user)


def _compromisos_autorizados(user):
    """Compromisos que el usuario puede ver: todos si es administrador o
    coordinador; solo los de su delegación si tiene una asignada (CU-29.1)."""
    compromisos = Compromiso.objects.select_related('delegacion', 'responsable')
    perfil = _perfil(user)
    if perfil and perfil.delegacion_id and not _puede_ver_todo(user):
        compromisos = compromisos.filter(delegacion=perfil.delegacion)
    return compromisos


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


@login_required
def solicitudes(request):
    query = request.GET.get('q', '').strip()
    compromisos = _compromisos_autorizados(request.user)
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


@login_required
def delegacion_detalle(request, nombre):
    compromisos = list(_compromisos_autorizados(request.user).filter(delegacion__nombre=nombre))
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


def _puede_editar_compromiso(user, compromiso):
    perfil = _perfil(user)
    if _puede_ver_todo(user):
        return True
    return bool(perfil and perfil.rol in {'delegado', 'funcionario'} and compromiso.responsable_id == user.pk)


@login_required
def compromiso_editar(request, pk):
    compromiso = get_object_or_404(Compromiso, pk=pk)
    if not _puede_editar_compromiso(request.user, compromiso):
        messages.error(request, 'No tienes permiso para modificar este compromiso.')
        return redirect('agenda')
    estado_anterior = compromiso.estado
    form = CompromisoForm(request.POST or None, instance=compromiso, user=request.user)
    if request.method == 'POST' and form.is_valid():
        compromiso = form.save()
        if compromiso.estado != estado_anterior:
            HistorialCompromiso.objects.create(
                compromiso=compromiso, autor=request.user,
                estado_anterior=estado_anterior, estado_nuevo=compromiso.estado,
            )
        Auditoria.objects.create(
            usuario=request.user, accion='editar', entidad='Compromiso',
            identificador=compromiso.folio, detalle={'campos': form.changed_data},
        )
        messages.success(request, f'Compromiso {compromiso.folio} actualizado.')
        return redirect('agenda')
    return render(request, 'delegaciones_app/compromiso_form.html', {
        'form': form,
        'titulo': f'Modificar compromiso {compromiso.folio}',
        'compromiso': compromiso,
    })


@login_required
@login_required
def compromiso_eliminar(request, pk):
    if not _puede_ver_todo(request.user):
        messages.error(request, 'Solo administración o coordinación puede eliminar compromisos.')
        return redirect('agenda')
    compromiso = get_object_or_404(Compromiso, pk=pk)
    if request.method == 'POST':
        folio = compromiso.folio
        Auditoria.objects.create(
            usuario=request.user, accion='eliminar', entidad='Compromiso',
            identificador=folio, detalle={'delegacion': compromiso.delegacion.nombre},
        )
        compromiso.delete()
        messages.success(request, f'Compromiso {folio} eliminado.')
        return redirect('agenda')
    return render(request, 'delegaciones_app/compromiso_confirmar_eliminar.html', {
        'compromiso': compromiso,
    })


@login_required
def agenda(request):
    compromisos = _compromisos_autorizados(request.user)
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


