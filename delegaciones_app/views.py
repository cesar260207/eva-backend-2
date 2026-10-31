import os
import uuid
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import FileResponse, Http404
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ActividadForm, CompromisoForm, EvidenciaForm
from .informes import PLAZOS, filtrar_actividades, filtrar_compromisos, resumen_por_responsable, situacion_de_plazo
from .medicion import periodo_vigente, promedio_general, resultados_por_delegacion
from .models import Actividad, Auditoria, Compromiso, Delegacion, Evidencia, Funcionario, Periodo, Validacion
from .permisos import (
    ADMINISTRADOR, COORDINADOR, DELEGADO, FUNCIONARIO, VERIFICADOR, delegacion_propia, funcionario_de, puede_crear_tarea, puede_ver_todo,
    registrar_acceso_denegado, rol_requerido, tiene_rol,
)

# Decisión de la revisión -> método de Validacion que la aplica a cada evidencia pendiente. La revisión
# se simplificó a aprobar o rechazar con motivo: quien registró corrige y sube una evidencia nueva.
DECISIONES = {'aprobar': 'aprobar_evidencia', 'rechazar': 'rechazar_evidencia'}

# Quién revisa evidencias: el delegado revisa las de su delegación (su ámbito lo limita
# _actividades_autorizadas); verificador, coordinación y administración, las de su alcance.
ROLES_REVISORES = (ADMINISTRADOR, COORDINADOR, DELEGADO, VERIFICADOR)
MENSAJE_REVISION_PROPIA = 'No puedes revisar una actividad que registraste tú: la revisa otro delegado, un verificador o la coordinación.'

def _delegaciones_visibles(user):
    """Delegaciones que el usuario puede elegir en los filtros: solo la suya si su ámbito es una delegación."""
    propia = delegacion_propia(user)
    return Delegacion.objects.filter(pk=propia.pk) if propia else Delegacion.objects.filter(estado=True)


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


def _recordar_filtros(request, lista):
    """Guarda en la sesión los filtros con que se miró una lista, para volver a ella tal como estaba."""
    request.session[f'filtros_{lista}'] = request.GET.urlencode()


def _url_de_lista(request, lista):
    """URL de la lista con los últimos filtros usados (la lista sin filtros si no hay)."""
    filtros = request.session.get(f'filtros_{lista}', '')
    return f'{reverse(lista)}?{filtros}' if filtros else reverse(lista)


MENSAJE_SOLO_AUTOR = 'Solo quien registró la actividad o la coordinación puede modificarla.'


def _bloqueo_actividad(funcionario, actividad, ve_todo):
    """Motivo por el que el funcionario no puede modificar ni eliminar la actividad, o None.

    Una actividad aprobada queda cerrada para todos: ya suma al avance de las metas y cambiarla
    alteraría ese avance sin revisión. Tampoco se modifica si su período está cerrado (RN-013).
    """
    if actividad.estado == 'aprobada':
        return 'Actividad aprobada: ya suma al avance de las metas y no se modifica. Para corregirla, un verificador debe anular su aprobación.'
    if actividad.item_id and actividad.item.periodo.estado == 'cerrado':
        return 'El período de la actividad está cerrado: no se modifica.'
    if not (ve_todo or (funcionario and actividad.funcionario_autor_id == funcionario.pk)):
        return MENSAJE_SOLO_AUTOR
    return None


MENSAJE_SOLO_AUTOR_EVIDENCIA = 'Solo quien registró la actividad o la coordinación puede subir evidencias.'


def _bloqueo_evidencia(funcionario, actividad, ve_todo):
    """Motivo por el que el usuario no puede subir evidencia a la actividad, o None."""
    if actividad.estado == 'aprobada':
        return 'Actividad aprobada: ya no admite nuevas evidencias.'
    if actividad.item_id and actividad.item.periodo.estado == 'cerrado':
        return 'El período de la actividad está cerrado: no admite nuevas evidencias.'
    if not (ve_todo or (funcionario and actividad.funcionario_autor_id == funcionario.pk)):
        return MENSAJE_SOLO_AUTOR_EVIDENCIA
    return None


def _calcular_estado_compromiso(compromiso):
    """Traduce el estado persistido de un Compromiso a una etiqueta y clase
    Bootstrap para la interfaz, calculando la alerta de vencimiento en vivo."""
    if compromiso.estado == 'realizado':
        return 'Realizada', 'success'
    if compromiso.estado == 'proceso':
        return 'En proceso', 'primary'
    if compromiso.vencido:
        return 'Alerta Roja por Vencimiento', 'danger'
    if compromiso.proximo_a_vencer:
        return 'Próxima a vencer', 'warning'
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
        'pendientes': sum(1 for item in compromisos if item.estado_display in ('Pendiente', 'Próxima a vencer')),
        'en_proceso': sum(1 for item in compromisos if item.estado_display == 'En proceso'),
        'alertas': sum(1 for item in compromisos if item.estado_display == 'Alerta Roja por Vencimiento'),
    }
    return render(request, 'delegaciones_app/solicitudes.html', contexto)


@login_required
def delegacion_detalle(request, nombre):
    propia = delegacion_propia(request.user)
    if propia and propia.nombre != nombre:
        registrar_acceso_denegado(request, 'Delegacion', nombre, 'fuera del ámbito')
        messages.error(request, f'Solo puedes ver la información de la delegación {propia.nombre}.')
        return redirect('delegacion_detalle', nombre=propia.nombre)
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
        messages.success(request, f'Actividad creada con código {actividad.codigo_verificador}. Ahora sube su evidencia.')
        return redirect('evidencia_subir', actividad.codigo_verificador)
    return render(request, 'delegaciones_app/actividad_form.html', {'form': form, 'titulo': 'Registrar actividad'})


@login_required
def actividades(request):
    _recordar_filtros(request, 'actividades')
    query = request.GET.get('q', '').strip()
    registros = filtrar_actividades(_actividades_autorizadas(request.user), request.GET).annotate(
        total_evidencias=Count('evidencias', distinct=True),
        evidencias_pendientes=Count('evidencias', filter=Q(evidencias__estado_revision='pendiente'), distinct=True),
    )
    ve_todo, funcionario = puede_ver_todo(request.user), funcionario_de(request.user)
    registros = list(registros)
    for actividad in registros:
        actividad.bloqueo = _bloqueo_actividad(funcionario, actividad, ve_todo)
        actividad.puede_subir_evidencia = _bloqueo_evidencia(funcionario, actividad, ve_todo) is None
    return render(request, 'delegaciones_app/actividades.html', {
        'actividades': registros, 'query': query, 'puede_crear': request.user.is_authenticated,
        'filtros': request.GET, 'filtrado': any(request.GET.get(clave) for clave in ('q', 'delegacion', 'estado', 'periodo', 'desde', 'hasta')),
        'delegaciones_filtro': _delegaciones_visibles(request.user), 'periodos_filtro': Periodo.objects.order_by('-fecha_inicio'),
        'estados_filtro': Actividad.ESTADOS,
    })


@login_required
def actividad_detalle(request, codigo):
    """Detalle de la actividad, sus evidencias y, para quien revisa, la decisión. La carga de evidencias
    está en su propia pantalla (evidencia_subir)."""
    actividades = _actividades_autorizadas(request.user).prefetch_related('evidencias__validaciones__funcionario_verificador')
    actividad = _obtener_autorizado(request, actividades, 'Actividad', codigo_verificador=codigo)
    propio, ve_todo = funcionario_de(request.user), puede_ver_todo(request.user)
    bloqueo_evidencia = _bloqueo_evidencia(propio, actividad, ve_todo)
    es_autor = bool(propio and actividad.funcionario_autor_id == propio.pk)
    return render(request, 'delegaciones_app/actividad_detalle.html', {
        'actividad': actividad,
        'url_lista': _url_de_lista(request, 'actividades'),
        'puede_subir_evidencia': bloqueo_evidencia is None,
        'puede_modificar': _bloqueo_actividad(propio, actividad, ve_todo) is None,
        # El aviso de carga es para quien sube evidencias (el autor); quien revisa no lo ve.
        'aviso_evidencia': bloqueo_evidencia if es_autor else None,
        'puede_validar': tiene_rol(request.user, *ROLES_REVISORES) and not es_autor,
        'puede_anular': tiene_rol(request.user, *ROLES_REVISORES) and not es_autor and actividad.estado == 'aprobada' and actividad.item.periodo.estado != 'cerrado',
        'hay_pendientes': any(evidencia.estado_revision == 'pendiente' for evidencia in actividad.evidencias.all()),
    })


@login_required
def evidencia_subir(request, codigo):
    """Sube una evidencia (JPG, PNG o PDF) a la actividad y la envía a revisión (CU-09)."""
    actividad = _obtener_autorizado(request, _actividades_autorizadas(request.user), 'Actividad', codigo_verificador=codigo)
    bloqueo = _bloqueo_evidencia(funcionario_de(request.user), actividad, puede_ver_todo(request.user))
    if bloqueo:
        if bloqueo == MENSAJE_SOLO_AUTOR_EVIDENCIA:
            registrar_acceso_denegado(request, 'Actividad', codigo, 'no es el autor')
        messages.error(request, bloqueo)
        return redirect('actividad_detalle', codigo=codigo)
    evidencia_form = EvidenciaForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        funcionario = _funcionario_requerido(request)
        if funcionario is None:
            return redirect('actividad_detalle', codigo=codigo)
        if evidencia_form.is_valid():
            with transaction.atomic():
                evidencia = funcionario.subir_evidencia(actividad, evidencia_form.cleaned_data['archivo_vinculo'], evidencia_form.cleaned_data['comentario'])
                Auditoria.registrar_evento(request.user, 'cargar_evidencia', 'Actividad', actividad.codigo_verificador, None, {'evidencia': evidencia.codigo_evidencia})
            messages.success(request, f'Evidencia {evidencia.codigo_evidencia} cargada y enviada a revisión.')
            return redirect('actividad_detalle', codigo=codigo)
    return render(request, 'delegaciones_app/evidencia_subir.html', {
        'actividad': actividad,
        'evidencia_form': evidencia_form,
        'evidencias': actividad.evidencias.all(),
        'tamano_maximo': settings.EVIDENCIA_TAMANO_MAXIMO_MB,
    })


@login_required
def evidencia_archivo(request, codigo):
    """CU-09 E2: abre o descarga el archivo de una evidencia solo si el usuario puede ver su actividad (RNF-017).
    Los archivos no se publican directamente: siempre pasan por esta vista y sus permisos."""
    evidencia = get_object_or_404(Evidencia.objects.select_related('actividad'), codigo_evidencia=codigo)
    _obtener_autorizado(request, _actividades_autorizadas(request.user), 'Actividad', codigo_verificador=evidencia.actividad.codigo_verificador)
    if not evidencia.archivo_vinculo:
        raise Http404('La evidencia no tiene archivo.')
    try:
        archivo = evidencia.archivo_vinculo.open('rb')
    except FileNotFoundError:
        raise Http404('El archivo de la evidencia no está disponible.') from None
    return FileResponse(archivo, as_attachment=request.GET.get('descargar') == '1', filename=os.path.basename(evidencia.archivo_vinculo.name))


@login_required
def revisar_actividad(request, codigo, decision):
    """Aprueba o rechaza (con motivo): una Validacion por cada evidencia pendiente (RN-009)."""
    if request.method != 'POST' or decision not in DECISIONES:
        return redirect('actividad_detalle', codigo=codigo)
    if not tiene_rol(request.user, *ROLES_REVISORES):
        registrar_acceso_denegado(request, 'Actividad', codigo)
        return redirect('actividad_detalle', codigo=codigo)
    verificador = _funcionario_requerido(request)
    if verificador is None:
        return redirect('actividad_detalle', codigo=codigo)
    actividad = _obtener_autorizado(request, _actividades_autorizadas(request.user), 'Actividad', codigo_verificador=codigo)
    if actividad.funcionario_autor_id == verificador.pk:
        messages.error(request, MENSAJE_REVISION_PROPIA)
        return redirect('actividad_detalle', codigo=codigo)
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
def anular_actividad(request, codigo):
    """Anula la aprobación de una actividad con un motivo; recalcula los indicadores (CU-07.2)."""
    if request.method != 'POST':
        return redirect('actividad_detalle', codigo=codigo)
    if not tiene_rol(request.user, *ROLES_REVISORES):
        registrar_acceso_denegado(request, 'Actividad', codigo)
        return redirect('actividad_detalle', codigo=codigo)
    verificador = _funcionario_requerido(request)
    if verificador is None:
        return redirect('actividad_detalle', codigo=codigo)
    actividad = _obtener_autorizado(request, _actividades_autorizadas(request.user), 'Actividad', codigo_verificador=codigo)
    if actividad.funcionario_autor_id == verificador.pk:
        messages.error(request, MENSAJE_REVISION_PROPIA)
        return redirect('actividad_detalle', codigo=codigo)
    motivo = request.POST.get('motivo', '').strip()
    try:
        with transaction.atomic():
            actividad.anular_aprobacion(motivo, verificador)
            Auditoria.registrar_evento(
                request.user, 'anular_aprobacion', 'Actividad', actividad.codigo_verificador,
                {'estado': 'aprobada'}, {'estado': actividad.estado, 'motivo': motivo},
            )
    except ValidationError as error:
        messages.error(request, ' '.join(error.messages))
    else:
        messages.success(request, f'Se anuló la aprobación de {actividad.codigo_verificador}: ya no suma al avance.')
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
        # Corregir una actividad rechazada la devuelve a la cola de revisión.
        devuelta_a_revision = estado_anterior == 'rechazada'
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
        return redirect(_url_de_lista(request, 'actividades'))
    return render(request, 'delegaciones_app/actividad_confirmar_eliminar.html', {
        'actividad': actividad,
        'total_evidencias': total_evidencias,
    })


@login_required
def compromiso_nuevo(request):
    if not puede_crear_tarea(request.user):
        registrar_acceso_denegado(request, 'Compromiso', None, 'rol insuficiente')
        return redirect('inicio')
    funcionario = _funcionario_requerido(request)
    if funcionario is None:
        return redirect('inicio')
    form = CompromisoForm(request.POST or None, user=request.user, initial={'delegacion': request.GET.get('delegacion')})
    if request.method == 'POST' and form.is_valid():
        compromiso = form.save(commit=False)
        if not puede_ver_todo(request.user):
            compromiso.funcionario_responsable = funcionario
        compromiso.folio = f'AGR-{datetime.now():%Y%m%d}-{uuid.uuid4().hex[:5].upper()}'
        with transaction.atomic():
            compromiso.save()
            compromiso.registrar_historial(funcionario, '', 'Creación de la tarea')
            Auditoria.registrar_evento(request.user, 'crear', 'Compromiso', compromiso.folio, None, {'delegacion': compromiso.delegacion.nombre})
        messages.success(request, f'Tarea creada con folio {compromiso.folio}.')
        return redirect('agenda')
    return render(request, 'delegaciones_app/compromiso_form.html', {'form': form, 'titulo': 'Agregar al tubo de trabajo', 'asigna': puede_ver_todo(request.user)})


@login_required
def compromiso_estado(request, pk, estado):
    if request.method != 'POST' or estado not in {'ingresado', 'pendiente', 'proceso', 'realizado'}:
        return redirect(_url_de_lista(request, 'agenda'))
    funcionario = _funcionario_requerido(request)
    if funcionario is None:
        return redirect(_url_de_lista(request, 'agenda'))
    compromiso = _obtener_autorizado(request, _compromisos_autorizados(request.user), 'Compromiso', pk=pk)
    if not _editor_de_compromisos(request.user)(compromiso):
        registrar_acceso_denegado(request, 'Compromiso', compromiso.folio, 'no es el responsable')
        messages.error(request, MENSAJE_SOLO_RESPONSABLE)
        return redirect(_url_de_lista(request, 'agenda'))
    anterior = compromiso.estado
    observacion = request.POST.get('observacion', '').strip()
    try:
        with transaction.atomic():
            compromiso.set_estado(estado, funcionario, observacion or None)
            nuevo = {'estado': estado, 'observacion': observacion} if observacion else estado
            Auditoria.registrar_evento(request.user, 'cambio_estado', 'Compromiso', compromiso.folio, anterior, nuevo)
    except ValidationError as error:
        messages.error(request, ' '.join(error.messages))
    else:
        messages.success(request, f'La tarea {compromiso.folio} cambió a {compromiso.get_estado_display()}.')
    return redirect(_url_de_lista(request, 'agenda'))


MENSAJE_SOLO_RESPONSABLE = 'No tienes permiso para modificar esta tarea: lo hace su responsable o la coordinación.'


def _editor_de_compromisos(user):
    """Función que dice si el usuario modifica una tarea (sus datos y su estado): la modifican su responsable,
    si es delegado o funcionario, y la coordinación. Consulta los roles una sola vez para toda una lista."""
    if puede_ver_todo(user):
        return lambda compromiso: True
    funcionario = funcionario_de(user)
    if funcionario is None or not tiene_rol(user, DELEGADO, FUNCIONARIO):
        return lambda compromiso: False
    return lambda compromiso: compromiso.funcionario_responsable_id == funcionario.pk


@login_required
def compromiso_editar(request, pk):
    compromiso = _obtener_autorizado(request, _compromisos_autorizados(request.user), 'Compromiso', pk=pk)
    if not _editor_de_compromisos(request.user)(compromiso):
        registrar_acceso_denegado(request, 'Compromiso', compromiso.folio, 'no es el responsable')
        messages.error(request, MENSAJE_SOLO_RESPONSABLE)
        return redirect(_url_de_lista(request, 'agenda'))
    form = CompromisoForm(request.POST or None, instance=compromiso, user=request.user)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                compromiso = form.save()
                Auditoria.registrar_evento(request.user, 'editar', 'Compromiso', compromiso.folio, None, {'campos': form.changed_data})
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, f'Tarea {compromiso.folio} actualizada.')
            return redirect(_url_de_lista(request, 'agenda'))
    return render(request, 'delegaciones_app/compromiso_form.html', {
        'form': form,
        'titulo': f'Modificar tarea {compromiso.folio}',
        'compromiso': compromiso,
        'asigna': puede_ver_todo(request.user),
    })


@login_required
def compromiso_eliminar(request, pk):
    if not puede_ver_todo(request.user):
        registrar_acceso_denegado(request, 'Compromiso', str(pk), 'rol insuficiente')
        messages.error(request, 'Solo administración o coordinación puede eliminar tareas.')
        return redirect('agenda')
    compromiso = get_object_or_404(Compromiso, pk=pk)
    motivo = compromiso.motivo_no_eliminable()
    if request.method == 'POST':
        folio = compromiso.folio
        try:
            with transaction.atomic():
                compromiso.delete()
                Auditoria.registrar_evento(request.user, 'eliminar', 'Compromiso', folio, {'delegacion': compromiso.delegacion.nombre})
        except ValidationError as error:
            messages.error(request, ' '.join(error.messages))
        else:
            messages.success(request, f'Tarea {folio} eliminada.')
        return redirect(_url_de_lista(request, 'agenda'))
    return render(request, 'delegaciones_app/compromiso_confirmar_eliminar.html', {
        'compromiso': compromiso,
        'bloqueo': motivo,
    })


@login_required
def agenda(request):
    _recordar_filtros(request, 'agenda')
    delegacion_id = request.GET.get('delegacion')
    estado = request.GET.get('estado')
    query = request.GET.get('q', '').strip()
    compromisos = list(filtrar_compromisos(_compromisos_autorizados(request.user), request.GET))
    puede_modificar = _editor_de_compromisos(request.user)
    for compromiso in compromisos:
        compromiso.estado_display, compromiso.estado_class = situacion_de_plazo(compromiso)
        compromiso.puede_modificar = puede_modificar(compromiso)
    resumen_responsables, resumen_total = resumen_por_responsable(compromisos)
    return render(request, 'delegaciones_app/agenda.html', {
        'compromisos': compromisos,
        'delegaciones_filtro': _delegaciones_visibles(request.user),
        'estado_filtro': estado or '',
        'estados_filtro': Compromiso.ESTADOS,
        'puede_crear_compromiso': puede_crear_tarea(request.user),
        'puede_eliminar_compromiso': puede_ver_todo(request.user),
        'delegacion_filtro': delegacion_id or '',
        'filtros': request.GET,
        'resumen_responsables': resumen_responsables,
        'resumen_total': resumen_total,
        'plazos_filtro': PLAZOS,
        'query': query,
        'proximos': sum(1 for item in compromisos if item.estado != 'realizado' and not item.vencido),
        'por_vencer': sum(1 for item in compromisos if item.proximo_a_vencer),
        'dias_alerta': settings.COMPROMISO_DIAS_ALERTA,
        'vencidos': sum(1 for item in compromisos if item.vencido),
        'realizados': sum(1 for item in compromisos if item.estado == 'realizado'),
    })


@rol_requerido(ADMINISTRADOR, COORDINADOR)
def delegados(request):
    """Coordinación: delegados de cada delegación, su carga de trabajo y su asignación.

    Es la función propia del coordinador frente al delegado: el delegado trabaja su delegación;
    el coordinador ve todas, asigna cada delegado a su delegación y le asigna compromisos.
    """
    candidatos = Funcionario.objects.filter(estado=True, roles__nombre_rol=DELEGADO).select_related('delegacion').distinct()
    if request.method == 'POST':
        funcionario = get_object_or_404(candidatos, pk=request.POST.get('funcionario'))
        delegacion = get_object_or_404(Delegacion, pk=request.POST.get('delegacion'), estado=True)
        anterior = funcionario.delegacion.nombre if funcionario.delegacion_id else None
        with transaction.atomic():
            funcionario.delegacion = delegacion
            funcionario.save(update_fields=['delegacion'])
            Auditoria.registrar_evento(request.user, 'asignar_delegado', 'Funcionario', funcionario.identificador_institucional, {'delegacion': anterior}, {'delegacion': delegacion.nombre})
        messages.success(request, f'{funcionario.nombre} quedó asignado a la delegación {delegacion.nombre}.')
        return redirect('delegados')

    periodo = periodo_vigente()
    cumplimiento = {fila['nombre']: fila for fila in resultados_por_delegacion(periodo)} if periodo else {}
    abiertos = list(Compromiso.objects.exclude(estado='realizado').only('delegacion_id', 'fecha_comprometida', 'estado'))
    pendientes = dict(Actividad.objects.filter(estado='pendiente').values_list('delegacion').annotate(total=Count('pk')).order_by())
    filas = []
    for delegacion in Delegacion.objects.filter(estado=True):
        propios = [c for c in abiertos if c.delegacion_id == delegacion.pk]
        filas.append({
            'delegacion': delegacion,
            'delegados': [f for f in candidatos if f.delegacion_id == delegacion.pk],
            'compromisos_abiertos': len(propios),
            'compromisos_vencidos': sum(1 for c in propios if c.vencido),
            'actividades_pendientes': pendientes.get(delegacion.pk, 0),
            'cumplimiento': cumplimiento.get(delegacion.nombre),
        })
    return render(request, 'delegaciones_app/delegados.html', {
        'filas': filas,
        'candidatos': candidatos,
        'sin_delegacion': [f for f in candidatos if not f.delegacion_id],
        'periodo': periodo,
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
