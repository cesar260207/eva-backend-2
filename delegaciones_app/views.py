import uuid
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import Http404
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ActividadForm, CompromisoForm, EvidenciaForm
from .medicion import periodo_vigente, promedio_general, resultados_por_delegacion
from .models import Actividad, Auditoria, Compromiso, Delegacion, Validacion
from .permisos import ADMINISTRADOR, COORDINADOR, DELEGADO, FUNCIONARIO, VERIFICADOR, funcionario_de, puede_ver_todo, registrar_acceso_denegado, tiene_rol

# Decisión de la revisión -> método de Validacion que la aplica a cada evidencia pendiente.
DECISIONES = {'aprobar': 'aprobar_evidencia', 'rechazar': 'rechazar_evidencia', 'corregir': 'solicitar_correccion'}


def _funcionario_requerido(request):
    """Funcionario del usuario con sesión; si no tiene, avisa. Quien registra o revisa necesita uno
    porque queda como autor de la actividad o como verificador de la evidencia."""
    funcionario = funcionario_de(request.user)
    if funcionario is None:
        messages.error(request, 'Tu cuenta no tiene un funcionario asociado. Pide a un administrador que lo cree.')
    return funcionario


def _actividades_autorizadas(user):
    """Actividades que el usuario puede ver: todas si es administrador o coordinador; las de su
    delegación si tiene una; todas si es verificador sin delegación; si no, solo las que registró."""
    actividades = Actividad.objects.select_related('delegacion', 'funcionario_autor', 'item__periodo', 'catalogo').order_by('-fecha', '-creada')
    if puede_ver_todo(user):
        return actividades
    funcionario = funcionario_de(user)
    if funcionario is None:
        return actividades.none()
    if funcionario.delegacion_id:
        return actividades.filter(delegacion_id=funcionario.delegacion_id)
    if tiene_rol(user, VERIFICADOR):
        return actividades
    return actividades.filter(funcionario_autor=funcionario)


def _compromisos_autorizados(user):
    """Compromisos que el usuario puede ver: todos si es administrador o coordinador;
    solo los de su delegación si tiene una asignada (CU-29.1)."""
    compromisos = Compromiso.objects.select_related('delegacion', 'funcionario_responsable')
    if puede_ver_todo(user):
        return compromisos
    funcionario = funcionario_de(user)
    if funcionario is None:
        return compromisos.none()
    if funcionario.delegacion_id:
        return compromisos.filter(delegacion_id=funcionario.delegacion_id)
    return compromisos


def _obtener_autorizado(request, autorizados, entidad, **filtro):
    """Registro que el usuario puede ver o 404. Si existe pero queda fuera de su ámbito, el intento
    queda en la auditoría (CU-26.1)."""
    try:
        return autorizados.get(**filtro)
    except ObjectDoesNotExist:
        if autorizados.model.objects.filter(**filtro).exists():
            registrar_acceso_denegado(request, entidad, str(next(iter(filtro.values()))), 'fuera del ámbito')
        raise Http404(f'{entidad} no encontrada.') from None


MENSAJE_SOLO_AUTOR = 'Solo quien registró la actividad o la coordinación puede modificarla.'


def _bloqueo_actividad(funcionario, actividad, ve_todo):
    """Motivo por el que el funcionario no puede modificar ni eliminar la actividad, o None.

    Una actividad aprobada queda cerrada para todos: ya suma al avance de las metas y cambiarla
    alteraría ese avance sin revisión. Tampoco se modifica si su período está cerrado (RN-013).
    """
    if actividad.estado == 'aprobada':
        return 'Actividad aprobada: ya suma al avance de las metas y no se modifica.'
    if actividad.item_id and actividad.item.periodo.estado == 'cerrado':
        return 'El período de la actividad está cerrado: no se modifica.'
    if not (ve_todo or (funcionario and actividad.funcionario_autor_id == funcionario.pk)):
        return MENSAJE_SOLO_AUTOR
    return None


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
    delegaciones = list(Delegacion.objects.filter(estado=True).values_list('nombre', flat=True))
    compromisos = list(Compromiso.objects.select_related('delegacion'))
    for compromiso in compromisos:
        _decorar_compromiso(compromiso)
    alertas = sum(1 for item in compromisos if item.estado_display == 'Alerta Roja por Vencimiento')
    cumplimiento_promedio = promedio_general(resultados_por_delegacion(periodo_vigente()))
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


@login_required
def actividad_nueva(request):
    funcionario = _funcionario_requerido(request)
    if funcionario is None:
        return redirect('inicio')
    form = ActividadForm(request.POST or None, user=request.user, compromisos=_compromisos_autorizados(request.user))
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            actividad = funcionario.registrar_actividad(form.cleaned_data)
            Auditoria.registrar_evento(
                request.user, 'crear', 'Actividad', actividad.codigo_verificador, None,
                {'delegacion': actividad.delegacion.nombre, 'item': str(actividad.item)},
            )
        messages.success(request, f'Actividad creada con código {actividad.codigo_verificador}.')
        return redirect('actividad_detalle', actividad.codigo_verificador)
    return render(request, 'delegaciones_app/actividad_form.html', {'form': form, 'titulo': 'Registrar actividad'})


@login_required
def actividades(request):
    query = request.GET.get('q', '').strip()
    registros = _actividades_autorizadas(request.user)
    if query:
        registros = registros.filter(Q(codigo_verificador__icontains=query) | Q(solicitud_problema__icontains=query) | Q(item__nombre__icontains=query))
    ve_todo, funcionario = puede_ver_todo(request.user), funcionario_de(request.user)
    registros = list(registros)
    for actividad in registros:
        actividad.bloqueo = _bloqueo_actividad(funcionario, actividad, ve_todo)
    return render(request, 'delegaciones_app/actividades.html', {'actividades': registros, 'query': query, 'puede_crear': request.user.is_authenticated})


@login_required
def actividad_detalle(request, codigo):
    actividades = _actividades_autorizadas(request.user).prefetch_related('evidencias__validaciones__funcionario_verificador')
    actividad = _obtener_autorizado(request, actividades, 'Actividad', codigo_verificador=codigo)
    evidencia_form = EvidenciaForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if actividad.estado == 'aprobada':
            messages.error(request, 'Actividad aprobada: ya no admite nuevas evidencias.')
            return redirect('actividad_detalle', codigo=codigo)
        funcionario = _funcionario_requerido(request)
        if funcionario is None:
            return redirect('actividad_detalle', codigo=codigo)
        if evidencia_form.is_valid():
            with transaction.atomic():
                evidencia = funcionario.subir_evidencia(actividad, evidencia_form.cleaned_data['archivo_vinculo'], evidencia_form.cleaned_data['comentario'])
                Auditoria.registrar_evento(request.user, 'cargar_evidencia', 'Actividad', actividad.codigo_verificador, None, {'evidencia': evidencia.codigo_evidencia})
            messages.success(request, 'Evidencia cargada y enviada a revisión.')
            return redirect('actividad_detalle', codigo=codigo)
    return render(request, 'delegaciones_app/actividad_detalle.html', {
        'actividad': actividad,
        'evidencia_form': evidencia_form,
        'puede_validar': tiene_rol(request.user, ADMINISTRADOR, COORDINADOR, VERIFICADOR),
        'hay_pendientes': any(evidencia.estado_revision == 'pendiente' for evidencia in actividad.evidencias.all()),
    })


@login_required
def revisar_actividad(request, codigo, decision):
    """Aprueba, rechaza o pide corrección: una Validacion por cada evidencia pendiente (RN-009)."""
    if request.method != 'POST' or decision not in DECISIONES:
        return redirect('actividad_detalle', codigo=codigo)
    if not tiene_rol(request.user, ADMINISTRADOR, COORDINADOR, VERIFICADOR):
        registrar_acceso_denegado(request, 'Actividad', codigo)
        return redirect('actividad_detalle', codigo=codigo)
    verificador = _funcionario_requerido(request)
    if verificador is None:
        return redirect('actividad_detalle', codigo=codigo)
    actividad = _obtener_autorizado(request, _actividades_autorizadas(request.user), 'Actividad', codigo_verificador=codigo)
    pendientes = list(actividad.evidencias.filter(estado_revision='pendiente'))
    if not pendientes:
        messages.error(request, 'La actividad no tiene evidencias pendientes de revisión.')
        return redirect('actividad_detalle', codigo=codigo)
    observacion = request.POST.get('observacion', '').strip()
    estado_anterior = actividad.estado
    try:
        with transaction.atomic():
            for evidencia in pendientes:
                getattr(Validacion(evidencia=evidencia, funcionario_verificador=verificador), DECISIONES[decision])(observacion)
            actividad.actualizar_indicadores()
            Auditoria.registrar_evento(
                request.user, decision, 'Actividad', actividad.codigo_verificador,
                {'estado': estado_anterior}, {'estado': actividad.estado, 'observacion': observacion},
            )
    except ValidationError as error:
        messages.error(request, ' '.join(error.messages))
        return redirect('actividad_detalle', codigo=codigo)
    messages.success(request, f'Actividad {actividad.codigo_verificador}: {actividad.get_estado_display()}.')
    return redirect('actividad_detalle', codigo=codigo)


@login_required
def actividad_editar(request, codigo):
    actividad = _obtener_autorizado(request, _actividades_autorizadas(request.user), 'Actividad', codigo_verificador=codigo)
    bloqueo = _bloqueo_actividad(funcionario_de(request.user), actividad, puede_ver_todo(request.user))
    if bloqueo:
        if bloqueo == MENSAJE_SOLO_AUTOR:
            registrar_acceso_denegado(request, 'Actividad', codigo, 'no es el autor')
        messages.error(request, bloqueo)
        return redirect('actividad_detalle', codigo=codigo)
    estado_anterior = actividad.estado
    form = ActividadForm(request.POST or None, instance=actividad, user=request.user, compromisos=_compromisos_autorizados(request.user))
    if request.method == 'POST' and form.is_valid():
        actividad = form.save(commit=False)
        # Corregir una actividad rechazada o con corrección solicitada la devuelve a la cola de revisión.
        devuelta_a_revision = estado_anterior in {'rechazada', 'correccion'}
        if devuelta_a_revision:
            actividad.estado = 'pendiente'
        try:
            with transaction.atomic():
                actividad.save()
                if devuelta_a_revision:
                    actividad.evidencias.exclude(estado_revision='aprobada').update(estado_revision='pendiente')
                Auditoria.registrar_evento(
                    request.user, 'editar', 'Actividad', actividad.codigo_verificador,
                    {'estado': estado_anterior}, {'campos': form.changed_data, 'estado': actividad.estado},
                )
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, f'Actividad {actividad.codigo_verificador} actualizada.')
            return redirect('actividad_detalle', codigo=actividad.codigo_verificador)
    return render(request, 'delegaciones_app/actividad_form.html', {
        'form': form,
        'titulo': f'Modificar actividad {actividad.codigo_verificador}',
        'actividad': actividad,
    })


@login_required
def actividad_eliminar(request, codigo):
    actividad = _obtener_autorizado(request, _actividades_autorizadas(request.user), 'Actividad', codigo_verificador=codigo)
    bloqueo = _bloqueo_actividad(funcionario_de(request.user), actividad, puede_ver_todo(request.user))
    if bloqueo:
        if bloqueo == MENSAJE_SOLO_AUTOR:
            registrar_acceso_denegado(request, 'Actividad', codigo, 'no es el autor')
        messages.error(request, bloqueo)
        return redirect('actividad_detalle', codigo=codigo)
    # Evidencia usa on_delete=CASCADE: borrar la actividad borra también sus evidencias.
    total_evidencias = actividad.evidencias.count()
    if request.method == 'POST':
        with transaction.atomic():
            Auditoria.registrar_evento(
                request.user, 'eliminar', 'Actividad', actividad.codigo_verificador,
                {'delegacion': actividad.delegacion.nombre, 'evidencias_eliminadas': total_evidencias},
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
    if not tiene_rol(request.user, ADMINISTRADOR, COORDINADOR, DELEGADO, FUNCIONARIO):
        registrar_acceso_denegado(request, 'Compromiso', None, 'rol insuficiente')
        return redirect('inicio')
    funcionario = _funcionario_requerido(request)
    if funcionario is None:
        return redirect('inicio')
    form = CompromisoForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        compromiso = form.save(commit=False)
        if not puede_ver_todo(request.user):
            compromiso.funcionario_responsable = funcionario
        compromiso.folio = f'AGR-{datetime.now():%Y%m%d}-{uuid.uuid4().hex[:5].upper()}'
        with transaction.atomic():
            compromiso.save()
            compromiso.registrar_historial(funcionario, '', 'Creación del compromiso')
            Auditoria.registrar_evento(request.user, 'crear', 'Compromiso', compromiso.folio, None, {'delegacion': compromiso.delegacion.nombre})
        messages.success(request, f'Compromiso creado con folio {compromiso.folio}.')
        return redirect('agenda')
    return render(request, 'delegaciones_app/compromiso_form.html', {'form': form, 'titulo': 'Nuevo compromiso'})


@login_required
def compromiso_estado(request, pk, estado):
    if request.method != 'POST' or estado not in {'ingresado', 'pendiente', 'proceso', 'realizado'}:
        return redirect('agenda')
    funcionario = _funcionario_requerido(request)
    if funcionario is None:
        return redirect('agenda')
    compromiso = _obtener_autorizado(request, _compromisos_autorizados(request.user), 'Compromiso', pk=pk)
    anterior = compromiso.estado
    try:
        with transaction.atomic():
            compromiso.set_estado(estado, funcionario)
            Auditoria.registrar_evento(request.user, 'cambio_estado', 'Compromiso', compromiso.folio, anterior, estado)
    except ValidationError as error:
        messages.error(request, ' '.join(error.messages))
    else:
        messages.success(request, f'El compromiso {compromiso.folio} cambió a {compromiso.get_estado_display()}.')
    return redirect('agenda')


def _puede_editar_compromiso(user, funcionario, compromiso):
    if puede_ver_todo(user):
        return True
    return bool(funcionario and tiene_rol(user, DELEGADO, FUNCIONARIO) and compromiso.funcionario_responsable_id == funcionario.pk)


@login_required
def compromiso_editar(request, pk):
    compromiso = get_object_or_404(Compromiso, pk=pk)
    if not _puede_editar_compromiso(request.user, funcionario_de(request.user), compromiso):
        registrar_acceso_denegado(request, 'Compromiso', compromiso.folio, 'no es el responsable')
        messages.error(request, 'No tienes permiso para modificar este compromiso.')
        return redirect('agenda')
    form = CompromisoForm(request.POST or None, instance=compromiso, user=request.user)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                compromiso = form.save()
                Auditoria.registrar_evento(request.user, 'editar', 'Compromiso', compromiso.folio, None, {'campos': form.changed_data})
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, f'Compromiso {compromiso.folio} actualizado.')
            return redirect('agenda')
    return render(request, 'delegaciones_app/compromiso_form.html', {
        'form': form,
        'titulo': f'Modificar compromiso {compromiso.folio}',
        'compromiso': compromiso,
    })


@login_required
def compromiso_eliminar(request, pk):
    if not puede_ver_todo(request.user):
        registrar_acceso_denegado(request, 'Compromiso', str(pk), 'rol insuficiente')
        messages.error(request, 'Solo administración o coordinación puede eliminar compromisos.')
        return redirect('agenda')
    compromiso = get_object_or_404(Compromiso, pk=pk)
    if request.method == 'POST':
        folio = compromiso.folio
        with transaction.atomic():
            Auditoria.registrar_evento(request.user, 'eliminar', 'Compromiso', folio, {'delegacion': compromiso.delegacion.nombre})
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
        'delegaciones_filtro': Delegacion.objects.filter(estado=True),
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
