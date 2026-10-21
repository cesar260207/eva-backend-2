from django.contrib import admin

from .auditoria import cambios_de_formulario, plano
from .models import (
    Actividad,
    Auditoria,
    Cargo,
    Catalogo,
    Compromiso,
    Delegacion,
    Evidencia,
    Funcionario,
    FuncionarioRol,
    HistorialCompromiso,
    Indicador,
    ItemMedible,
    MedicionDelegacion,
    Meta,
    ParametroVersionado,
    Periodo,
    Rol,
    UsuarioMaestro,
    Validacion,
)


class ProtegePeriodoCerradoAdmin:
    """RN-013: un período cerrado (y lo que depende de él) no se elimina desde el admin.

    Sin esto, el borrado fallaría con un error del modelo o, en una acción masiva,
    se saltaría la regla. La edición ya la rechaza el clean() del modelo.
    """

    def _periodo(self, obj):
        return obj if isinstance(obj, Periodo) else obj.obtener_periodo()

    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            periodo = self._periodo(obj)
            if periodo is not None and periodo.estado == 'cerrado':
                return False
        return super().has_delete_permission(request, obj)


class AdminAuditado(admin.ModelAdmin):
    """Deja en la auditoría las altas, los cambios y las bajas hechos desde el admin (RF-036, RNF-008)."""

    def _auditar(self, request, evento, obj, anterior=None, nuevo=None):
        Auditoria.registrar_evento(request.user, evento, type(obj).__name__, obj.pk, anterior, nuevo)

    def save_model(self, request, obj, form, change):
        anterior, nuevo = cambios_de_formulario(form, editando=change)
        super().save_model(request, obj, form, change)
        self._auditar(request, 'admin_editar' if change else 'admin_crear', obj, anterior, nuevo)

    def delete_model(self, request, obj):
        pk, descripcion = obj.pk, str(obj)
        super().delete_model(request, obj)
        Auditoria.registrar_evento(request.user, 'admin_eliminar', type(obj).__name__, pk, {'descripcion': descripcion})

    def delete_queryset(self, request, queryset):
        # Una por una, para que se apliquen las reglas del modelo y cada baja quede auditada.
        for obj in queryset:
            self.delete_model(request, obj)

    def save_formset(self, request, form, formset, change):
        instancias = formset.save(commit=False)
        campos_cambiados = {obj.pk: campos for obj, campos in formset.changed_objects}
        for obj in formset.deleted_objects:
            pk, descripcion = obj.pk, str(obj)
            obj.delete()
            Auditoria.registrar_evento(request.user, 'admin_eliminar', type(obj).__name__, pk, {'descripcion': descripcion})
        for obj in instancias:
            creado = obj._state.adding
            obj.save()
            nuevo = {campo: plano(getattr(obj, campo)) for campo in campos_cambiados.get(obj.pk, [])} or {'descripcion': str(obj)}
            self._auditar(request, 'admin_crear' if creado else 'admin_editar', obj, None, nuevo)
        formset.save_m2m()


# Inlines

class FuncionarioDeDelegacionInline(admin.TabularInline):
    model = Funcionario
    extra = 0
    fields = ['identificador_institucional', 'nombre', 'cargo', 'estado']
    readonly_fields = fields
    show_change_link = True
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class FuncionarioRolInline(admin.TabularInline):
    model = FuncionarioRol
    extra = 0
    autocomplete_fields = ['rol']


class ParametroVersionadoInline(admin.TabularInline):
    model = ParametroVersionado
    extra = 0


class EvidenciaInline(admin.TabularInline):
    model = Evidencia
    extra = 0
    fields = ['codigo_evidencia', 'funcionario_autor', 'archivo_vinculo', 'estado_revision']
    readonly_fields = ['codigo_evidencia']
    autocomplete_fields = ['funcionario_autor']
    show_change_link = True


class ValidacionInline(admin.TabularInline):
    model = Validacion
    extra = 0
    fields = ['funcionario_verificador', 'decision', 'observacion', 'resultado', 'fecha', 'version']
    autocomplete_fields = ['funcionario_verificador']


class HistorialCompromisoInline(admin.TabularInline):
    model = HistorialCompromiso
    extra = 0
    fields = ['autor', 'estado_anterior', 'estado_nuevo', 'observacion', 'fecha']
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


# Organización y acceso

@admin.register(Delegacion)
class DelegacionAdmin(AdminAuditado):
    list_display = ['nombre', 'ambito', 'estado']
    list_filter = ['estado']
    search_fields = ['nombre', 'ambito']
    inlines = [FuncionarioDeDelegacionInline]


@admin.register(Cargo)
class CargoAdmin(AdminAuditado):
    list_display = ['nombre', 'vigencia']
    list_filter = ['vigencia']
    search_fields = ['nombre']


@admin.register(Rol)
class RolAdmin(AdminAuditado):
    list_display = ['nombre_rol']
    search_fields = ['nombre_rol']


@admin.register(Funcionario)
class FuncionarioAdmin(AdminAuditado):
    list_display = ['identificador_institucional', 'nombre', 'cargo', 'delegacion', 'estado']
    list_filter = ['estado', 'cargo', 'delegacion']
    search_fields = ['identificador_institucional', 'nombre', 'usuario__username', 'usuario__email']
    autocomplete_fields = ['usuario', 'cargo', 'delegacion']
    list_select_related = ['cargo', 'delegacion']
    inlines = [FuncionarioRolInline]


@admin.register(FuncionarioRol)
class FuncionarioRolAdmin(AdminAuditado):
    list_display = ['funcionario', 'rol']
    list_filter = ['rol']
    search_fields = ['funcionario__nombre', 'funcionario__identificador_institucional', 'rol__nombre_rol']
    autocomplete_fields = ['funcionario', 'rol']


@admin.register(UsuarioMaestro)
class UsuarioMaestroAdmin(AdminAuditado):
    list_display = ['identificador_maestro', 'nombre', 'nivel_dominio', 'estado']
    list_filter = ['estado']
    search_fields = ['identificador_maestro', 'nombre', 'usuario__username']
    autocomplete_fields = ['usuario']


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    """La auditoría es de solo lectura incluso para el superusuario (CU-30.1, RNF-008): ningún intento de
    agregar, modificar o eliminar prospera, y cada intento queda registrado como un evento más."""

    list_display = ['fecha', 'evento', 'entidad', 'identificador_registro', 'funcionario', 'usuario_maestro']
    list_filter = ['evento', 'entidad']
    search_fields = ['identificador_registro', 'funcionario__nombre', 'usuario_maestro__nombre']
    date_hierarchy = 'fecha'
    fields = ['fecha', 'funcionario', 'usuario_maestro', 'evento', 'entidad', 'identificador_registro', 'valor_anterior', 'valor_nuevo']
    readonly_fields = fields

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        return {}

    def _registrar_intento(self, request, accion, object_id=''):
        Auditoria.registrar_evento(request.user, 'intento_alteracion', 'Auditoria', object_id, None, {'accion': accion, 'metodo': request.method})

    def add_view(self, request, form_url='', extra_context=None):
        self._registrar_intento(request, 'agregar')
        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.method == 'POST':
            self._registrar_intento(request, 'modificar', object_id)
        return super().change_view(request, object_id, form_url, extra_context)

    def delete_view(self, request, object_id, extra_context=None):
        self._registrar_intento(request, 'eliminar', object_id)
        return super().delete_view(request, object_id, extra_context)



# Medición

@admin.register(Periodo)
class PeriodoAdmin(ProtegePeriodoCerradoAdmin, AdminAuditado):
    list_display = ['nombre', 'fecha_inicio', 'fecha_termino', 'dias_computables', 'estado', 'umbral_minimo', 'version_parametros']
    list_filter = ['estado']
    search_fields = ['nombre']
    fields = ['nombre', 'fecha_inicio', 'fecha_termino', 'dias_computables', 'estado', 'umbral_minimo', 'version_parametros']
    readonly_fields = ['dias_computables']
    inlines = [ParametroVersionadoInline]


@admin.register(ParametroVersionado)
class ParametroVersionadoAdmin(ProtegePeriodoCerradoAdmin, AdminAuditado):
    list_display = ['periodo', 'clave', 'valor']
    list_filter = ['periodo']
    search_fields = ['clave', 'valor', 'descripcion']
    autocomplete_fields = ['periodo']


@admin.register(ItemMedible)
class ItemMedibleAdmin(ProtegePeriodoCerradoAdmin, AdminAuditado):
    list_display = ['nombre', 'cargo', 'periodo', 'servicio', 'ponderacion']
    list_filter = ['periodo', 'cargo']
    search_fields = ['nombre', 'servicio']
    autocomplete_fields = ['cargo', 'periodo']
    list_select_related = ['cargo', 'periodo']


@admin.register(Catalogo)
class CatalogoAdmin(AdminAuditado):
    list_display = ['codigo', 'nombre', 'tipo', 'subtipo', 'area', 'activo']
    list_filter = ['tipo', 'activo']
    search_fields = ['codigo', 'nombre', 'area']


@admin.register(Meta)
class MetaAdmin(ProtegePeriodoCerradoAdmin, AdminAuditado):
    list_display = ['item', 'funcionario', 'valor_objetivo', 'unidad', 'ponderador']
    list_filter = ['item__periodo', 'funcionario__delegacion']
    search_fields = ['item__nombre', 'funcionario__nombre']
    autocomplete_fields = ['item', 'funcionario']
    list_select_related = ['item__periodo', 'funcionario']


@admin.register(Indicador)
class IndicadorAdmin(ProtegePeriodoCerradoAdmin, AdminAuditado):
    list_display = ['meta', 'periodo', 'fecha_calculo', 'avance', 'cumplimiento', 'ponderacion', 'ajuste', 'semaforo']
    list_filter = ['semaforo', 'periodo']
    search_fields = ['meta__item__nombre', 'meta__funcionario__nombre']
    autocomplete_fields = ['meta', 'periodo']
    date_hierarchy = 'fecha_calculo'


# Operación

@admin.register(Actividad)
class ActividadAdmin(AdminAuditado):
    list_display = ['codigo_verificador', 'delegacion', 'funcionario_autor', 'fecha', 'estado', 'item']
    list_filter = ['estado', 'delegacion', 'item__periodo', 'catalogo']
    search_fields = ['codigo_verificador', 'solicitud_problema', 'accion', 'funcionario_autor__nombre']
    autocomplete_fields = ['delegacion', 'funcionario_autor', 'item', 'catalogo', 'compromiso']
    date_hierarchy = 'fecha'
    fields = [
        'codigo_verificador', 'delegacion', 'funcionario_autor', 'item', 'catalogo', 'compromiso', 'fecha',
        'solicitud_problema', 'accion', 'contacto_nombre', 'contacto_telefono', 'estado', 'version', 'creada', 'actualizada',
    ]
    readonly_fields = ['codigo_verificador', 'version', 'creada', 'actualizada']
    list_select_related = ['delegacion', 'funcionario_autor', 'item']
    inlines = [EvidenciaInline]


@admin.register(Evidencia)
class EvidenciaAdmin(AdminAuditado):
    list_display = ['codigo_evidencia', 'actividad', 'funcionario_autor', 'estado_revision', 'fecha_carga']
    list_filter = ['estado_revision']
    search_fields = ['codigo_evidencia', 'actividad__codigo_verificador']
    autocomplete_fields = ['actividad', 'funcionario_autor']
    fields = ['codigo_evidencia', 'actividad', 'funcionario_autor', 'archivo_vinculo', 'metadatos', 'estado_revision', 'fecha_carga']
    readonly_fields = ['codigo_evidencia', 'fecha_carga']
    inlines = [ValidacionInline]


@admin.register(Validacion)
class ValidacionAdmin(AdminAuditado):
    list_display = ['evidencia', 'funcionario_verificador', 'decision', 'fecha', 'version']
    list_filter = ['decision']
    search_fields = ['evidencia__codigo_evidencia', 'observacion', 'funcionario_verificador__nombre']
    autocomplete_fields = ['evidencia', 'funcionario_verificador']
    date_hierarchy = 'fecha'


@admin.register(Compromiso)
class CompromisoAdmin(AdminAuditado):
    list_display = ['folio', 'delegacion', 'funcionario_responsable', 'origen', 'eje', 'estado', 'fecha_comprometida', 'version']
    list_filter = ['estado', 'eje', 'origen', 'delegacion']
    search_fields = ['folio', 'descripcion', 'solicitante', 'territorio']
    autocomplete_fields = ['delegacion', 'funcionario_responsable', 'item']
    date_hierarchy = 'fecha_comprometida'
    fields = [
        'folio', 'delegacion', 'funcionario_responsable', 'origen', 'solicitante', 'territorio', 'eje', 'descripcion',
        'fecha_comprometida', 'fecha_ingreso', 'area_apoyo', 'item', 'estado', 'observacion', 'version', 'creado',
    ]
    readonly_fields = ['version', 'creado']
    list_select_related = ['delegacion', 'funcionario_responsable']
    inlines = [HistorialCompromisoInline]

    def has_delete_permission(self, request, obj=None):
        # CU-14.2: un incumplimiento se conserva con su historial.
        if obj is not None and obj.motivo_no_eliminable():
            return False
        return super().has_delete_permission(request, obj)


@admin.register(HistorialCompromiso)
class HistorialCompromisoAdmin(AdminAuditado):
    list_display = ['compromiso', 'autor', 'estado_anterior', 'estado_nuevo', 'fecha']
    list_filter = ['estado_anterior', 'estado_nuevo', 'fecha']
    search_fields = ['compromiso__folio', 'compromiso__descripcion', 'autor__nombre', 'observacion']
    autocomplete_fields = ['compromiso', 'autor']
    date_hierarchy = 'fecha'
    fields = ['compromiso', 'autor', 'estado_anterior', 'estado_nuevo', 'observacion', 'fecha']
    readonly_fields = ['fecha']


@admin.register(MedicionDelegacion)
class MedicionDelegacionAdmin(AdminAuditado):
    list_display = ['delegacion', 'cumplimiento', 'meta', 'fecha_datos', 'estado_reportado']
    list_filter = ['estado_reportado', 'delegacion', 'fecha_datos']
    search_fields = ['delegacion__nombre', 'observacion']
    autocomplete_fields = ['delegacion']
    date_hierarchy = 'fecha_datos'
