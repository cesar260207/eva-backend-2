"""Vistas del módulo de beneficiarios: inscribir, listar, exportar, modificar y eliminar inscripciones, verificar
un RUT en vivo y administrar eventos y unidades municipales.

Permisos (asignados a los perfiles en la migración 0002):
- add_inscripcion / view_inscripcion: los cuatro perfiles, cada uno dentro de su unidad (ver alcance.py).
- change_inscripcion / delete_inscripcion: Coordinador y Administrador, sobre cualquier inscripción visible.
  Quien registró una inscripción puede corregirla o eliminarla mientras el evento siga abierto.
- change_evento / change_unidadmunicipal: Coordinador y Administrador.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET

from delegaciones_app.informes import respuesta_excel
from delegaciones_app.models import Auditoria
from delegaciones_app.permisos import permiso_requerido, registrar_acceso_denegado
from delegaciones_app.rut import es_rut_valido

from .alcance import inscripciones_visibles, unidades_de
from . import importacion
from .forms import EventoForm, ImportarForm, InscripcionForm, UnidadForm, inscripcion_existente, mensaje_rut_duplicado
from .models import Evento, Inscripcion, UnidadMunicipal, rut_canonico

PERMISO_VER = 'beneficiarios_app.view_inscripcion'
PERMISO_CREAR = 'beneficiarios_app.add_inscripcion'
PERMISO_MODIFICAR = 'beneficiarios_app.change_inscripcion'
PERMISO_ELIMINAR = 'beneficiarios_app.delete_inscripcion'
PERMISO_EVENTOS = 'beneficiarios_app.change_evento'
PERMISO_UNIDADES = 'beneficiarios_app.change_unidadmunicipal'


def _puede_modificar(user, inscripcion):
    if not inscripcion.evento.inscripciones_abiertas:
        return False
    return user.has_perm(PERMISO_MODIFICAR) or inscripcion.registrado_por_id == user.pk


def _puede_eliminar(user, inscripcion):
    if user.has_perm(PERMISO_ELIMINAR):
        return True
    return inscripcion.evento.inscripciones_abiertas and inscripcion.registrado_por_id == user.pk


def _inscripcion_autorizada(request, pk):
    """Inscripción dentro del alcance del usuario o 404; un intento fuera de su unidad queda en la auditoría."""
    try:
        return inscripciones_visibles(request.user).get(pk=pk)
    except Inscripcion.DoesNotExist:
        if Inscripcion.objects.filter(pk=pk).exists():
            registrar_acceso_denegado(request, 'Inscripcion', str(pk), 'fuera del ámbito')
        raise Http404('Inscripción no encontrada.') from None


def _filtrar(inscripciones, datos):
    """Filtros del listado (también los usa la exportación)."""
    evento = datos.get('evento', '')
    if evento.isdigit():
        inscripciones = inscripciones.filter(evento_id=evento)
    unidad = datos.get('unidad', '')
    if unidad.isdigit():
        inscripciones = inscripciones.filter(unidad_id=unidad)
    for campo in ('rango_edad', 'genero', 'tramo_rsh'):
        if datos.get(campo):
            inscripciones = inscripciones.filter(**{campo: datos[campo]})
    texto = datos.get('q', '').strip()
    if texto:
        filtro = Q(nombre__icontains=texto) | Q(folio_rsh__icontains=texto)
        if es_rut_valido(texto):
            filtro |= Q(rut=rut_canonico(texto))
        else:
            filtro |= Q(rut__icontains=texto.replace('.', ''))
        inscripciones = inscripciones.filter(filtro)
    return inscripciones


@login_required
@permiso_requerido(PERMISO_VER, PERMISO_CREAR)
def inscripciones(request):
    datos = request.GET
    lista = _filtrar(inscripciones_visibles(request.user), datos)
    totales = lista.aggregate(
        total=Count('pk'),
        masculino=Count('pk', filter=Q(genero='M')),
        femenino=Count('pk', filter=Q(genero='F')),
        otro=Count('pk', filter=Q(genero__in=['O', 'N'])),
    )
    por_edad = dict(lista.values_list('rango_edad').annotate(n=Count('pk')).order_by())
    filas = list(lista)
    for inscripcion in filas:
        inscripcion.puede_modificar = _puede_modificar(request.user, inscripcion)
        inscripcion.puede_eliminar = _puede_eliminar(request.user, inscripcion)
    return render(request, 'beneficiarios_app/inscripciones.html', {
        'inscripciones': filas,
        'totales': totales,
        'por_edad': [(etiqueta, por_edad.get(valor, 0)) for valor, etiqueta in Inscripcion.RANGOS_EDAD],
        'filtros': datos,
        'eventos': Evento.objects.all(),
        'unidades': unidades_de(request.user),
        'rangos': Inscripcion.RANGOS_EDAD,
        'generos': Inscripcion.GENEROS,
        'tramos': Inscripcion.TRAMOS_RSH,
        'puede_crear': request.user.has_perm(PERMISO_CREAR),
        'puede_administrar': request.user.has_perm(PERMISO_EVENTOS) or request.user.has_perm(PERMISO_UNIDADES),
        'consulta': datos.urlencode(),
    })


@login_required
@permiso_requerido(PERMISO_VER, PERMISO_CREAR)
def exportar(request):
    lista = _filtrar(inscripciones_visibles(request.user), request.GET)
    columnas = ['Actividad', 'Unidad municipal', 'Nombre del menor', 'RUT', 'Rango de edad', 'Género', 'Folio RSH',
                'Tramo RSH', 'JJ.VV. o agrupación', 'Teléfono', 'Registrado por', 'Correo', 'Fecha de registro']
    filas = [
        [str(i.evento), str(i.unidad), i.nombre, i.rut, i.get_rango_edad_display(), i.get_genero_display(), i.folio_rsh,
         i.get_tramo_rsh_display(), i.organizacion_nombre, i.telefono, i.registrado_por.get_username(), i.correo_registro,
         i.creado.strftime('%d-%m-%Y %H:%M')]
        for i in lista
    ]
    Auditoria.registrar_evento(request.user, 'exportar', 'Inscripcion', '', None, {'filtros': request.GET.urlencode(), 'filas': len(filas)})
    return respuesta_excel('beneficiarios.xlsx', columnas, filas)


def _guardar(request, form, evento_auditoria, anterior=None):
    """Guarda la inscripción. Si dos personas inscriben el mismo RUT a la vez, la restricción única de la base
    rechaza la segunda y se muestra el mismo mensaje que en la validación del formulario."""
    inscripcion = form.save(commit=False)
    if not inscripcion.pk:
        inscripcion.registrado_por = request.user
        inscripcion.correo_registro = request.user.email
    try:
        with transaction.atomic():
            inscripcion.save()
            Auditoria.registrar_evento(request.user, evento_auditoria, 'Inscripcion', inscripcion.pk, anterior,
                                       {'evento': str(inscripcion.evento), 'unidad': str(inscripcion.unidad)})
    except IntegrityError:
        previa = inscripcion_existente(inscripcion.evento, inscripcion.rut, excluir_pk=inscripcion.pk)
        form.add_error('rut', mensaje_rut_duplicado(previa) if previa else 'Este RUT ya está inscrito en la actividad.')
        return None
    return inscripcion


@login_required
@permiso_requerido(PERMISO_CREAR)
def inscribir(request):
    if not unidades_de(request.user).exists():
        messages.error(request, 'Tu usuario no está asignado a ninguna unidad municipal. Pide a Coordinación que te asigne una.')
        return redirect('beneficiarios:inscripciones')
    if not Evento.objects.filter(inscripciones_abiertas=True).exists():
        messages.warning(request, 'No hay actividades con inscripciones abiertas.')
        return redirect('beneficiarios:inscripciones')
    form = InscripcionForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        inscripcion = _guardar(request, form, 'crear')
        if inscripcion:
            messages.success(request, f'{inscripcion.nombre} quedó inscrito(a) en {inscripcion.evento}.')
            if 'otra' in request.POST:
                return redirect('beneficiarios:inscribir')
            return redirect('beneficiarios:inscripciones')
    return render(request, 'beneficiarios_app/inscripcion_form.html', {'form': form, 'titulo': 'Inscribir beneficiario', 'nueva': True})


@login_required
def modificar(request, pk):
    inscripcion = _inscripcion_autorizada(request, pk)
    if not _puede_modificar(request.user, inscripcion):
        registrar_acceso_denegado(request, 'Inscripcion', str(pk), 'sin permiso para modificar')
        messages.error(request, 'Solo quien registró la inscripción (o Coordinación) puede modificarla, y solo con las inscripciones abiertas.')
        return redirect('beneficiarios:inscripciones')
    form = InscripcionForm(request.POST or None, instance=inscripcion, user=request.user)
    if request.method == 'POST' and form.is_valid():
        if _guardar(request, form, 'editar', {'campos': form.changed_data}):
            messages.success(request, 'La inscripción fue modificada.')
            return redirect('beneficiarios:inscripciones')
    return render(request, 'beneficiarios_app/inscripcion_form.html', {'form': form, 'titulo': 'Modificar inscripción'})


@login_required
def eliminar(request, pk):
    inscripcion = _inscripcion_autorizada(request, pk)
    if not _puede_eliminar(request.user, inscripcion):
        registrar_acceso_denegado(request, 'Inscripcion', str(pk), 'sin permiso para eliminar')
        messages.error(request, 'No tienes permiso para eliminar esta inscripción.')
        return redirect('beneficiarios:inscripciones')
    if request.method == 'POST':
        Auditoria.registrar_evento(request.user, 'eliminar', 'Inscripcion', inscripcion.pk,
                                   {'evento': str(inscripcion.evento), 'unidad': str(inscripcion.unidad)}, None)
        inscripcion.delete()
        messages.success(request, 'La inscripción fue eliminada.')
        return redirect('beneficiarios:inscripciones')
    return render(request, 'beneficiarios_app/confirmar_eliminar.html', {'inscripcion': inscripcion})


@login_required
@permiso_requerido(PERMISO_CREAR)
def plantilla(request):
    return importacion.plantilla_excel()


@login_required
@permiso_requerido(PERMISO_CREAR)
def importar(request):
    """Inscribe en bloque la planilla Excel de una JJ.VV.; cada fila se valida como una inscripción manual."""
    if not unidades_de(request.user).exists():
        messages.error(request, 'Tu usuario no está asignado a ninguna unidad municipal. Pide a Coordinación que te asigne una.')
        return redirect('beneficiarios:inscripciones')
    form = ImportarForm(request.POST or None, request.FILES or None, user=request.user)
    resultado = None
    if request.method == 'POST' and form.is_valid():
        datos = form.cleaned_data
        resultado = importacion.procesar(
            datos['archivo'], request.user, datos['evento'], datos['unidad'],
            organizacion=datos['organizacion'], organizacion_otra=datos['organizacion_otra'], solo_revisar=datos['solo_revisar'],
        )
        if resultado.guardado:
            Auditoria.registrar_evento(request.user, 'importar', 'Inscripcion', '', None, {
                'archivo': datos['archivo'].name, 'evento': str(datos['evento']), 'unidad': str(datos['unidad']),
                'filas': len(resultado.filas), 'inscritas': resultado.validas, 'con_error': resultado.con_error,
            })
            messages.success(request, f'Se inscribieron {resultado.validas} beneficiarios desde la planilla.')
    return render(request, 'beneficiarios_app/importar.html', {'form': form, 'resultado': resultado})


@login_required
@permiso_requerido(PERMISO_CREAR)
@require_GET
def verificar_rut(request):
    """Revisión en vivo mientras se escribe el RUT: formato, dígito verificador y si ya está inscrito en el evento."""
    rut = request.GET.get('rut', '')
    if not es_rut_valido(rut):
        return JsonResponse({'valido': False, 'duplicado': False, 'mensaje': 'El RUT no es válido: revisa los números y el dígito verificador.'})
    evento = Evento.objects.filter(pk=request.GET.get('evento') or None).first() if request.GET.get('evento', '').isdigit() else None
    excluir = request.GET.get('excluir', '')
    previa = inscripcion_existente(evento, rut, excluir_pk=int(excluir) if excluir.isdigit() else None) if evento else None
    return JsonResponse({
        'valido': True, 'rut': rut_canonico(rut), 'duplicado': bool(previa),
        'mensaje': mensaje_rut_duplicado(previa) if previa else 'RUT válido y disponible.',
    })


# --- Administración: eventos y unidades -----------------------------------------------------------------------------

@login_required
@permiso_requerido(PERMISO_EVENTOS)
def eventos(request):
    lista = Evento.objects.annotate(total=Count('inscripciones'))
    return render(request, 'beneficiarios_app/eventos.html', {'eventos': lista})


@login_required
@permiso_requerido(PERMISO_EVENTOS)
def evento_form(request, pk=None):
    evento = get_object_or_404(Evento, pk=pk) if pk else None
    form = EventoForm(request.POST or None, instance=evento)
    if request.method == 'POST' and form.is_valid():
        evento = form.save()
        Auditoria.registrar_evento(request.user, 'editar' if pk else 'crear', 'Evento', evento.pk, None,
                                   {'evento': str(evento), 'inscripciones_abiertas': evento.inscripciones_abiertas})
        messages.success(request, f'{evento} fue guardado.')
        return redirect('beneficiarios:eventos')
    return render(request, 'beneficiarios_app/admin_form.html', {
        'form': form, 'titulo': 'Modificar actividad' if pk else 'Nueva actividad', 'volver': 'beneficiarios:eventos',
    })


@login_required
@permiso_requerido(PERMISO_UNIDADES)
def unidades(request):
    lista = UnidadMunicipal.objects.select_related('delegacion').annotate(
        total=Count('inscripciones', distinct=True), asignados=Count('funcionarios', distinct=True))
    return render(request, 'beneficiarios_app/unidades.html', {'unidades': lista})


@login_required
@permiso_requerido(PERMISO_UNIDADES)
def unidad_form(request, pk=None):
    unidad = get_object_or_404(UnidadMunicipal, pk=pk) if pk else None
    form = UnidadForm(request.POST or None, instance=unidad)
    if request.method == 'POST' and form.is_valid():
        unidad = form.save()
        Auditoria.registrar_evento(request.user, 'editar' if pk else 'crear', 'UnidadMunicipal', unidad.pk, None,
                                   {'nombre': unidad.nombre, 'funcionarios': list(unidad.funcionarios.values_list('pk', flat=True))})
        messages.success(request, f'La unidad {unidad} fue guardada.')
        return redirect('beneficiarios:unidades')
    return render(request, 'beneficiarios_app/admin_form.html', {
        'form': form, 'titulo': 'Modificar unidad' if pk else 'Nueva unidad', 'volver': 'beneficiarios:unidades',
    })
