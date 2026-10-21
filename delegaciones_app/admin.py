from django.contrib import admin

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
    fields = ['autor_funcionario', 'estado_anterior', 'estado_nuevo', 'observacion', 'fecha']
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


# Organización y acceso

@admin.register(Delegacion)
class DelegacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ambito', 'estado']
    list_filter = ['estado']
    search_fields = ['nombre', 'ambito']
    inlines = [FuncionarioDeDelegacionInline]


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'vigencia']
    list_filter = ['vigencia']
    search_fields = ['nombre']


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['nombre_rol']
    search_fields = ['nombre_rol']


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ['identificador_institucional', 'nombre', 'cargo', 'delegacion', 'estado']
    list_filter = ['estado', 'cargo', 'delegacion']
    search_fields = ['identificador_institucional', 'nombre', 'usuario__username', 'usuario__email']
    autocomplete_fields = ['usuario', 'cargo', 'delegacion']
    list_select_related = ['cargo', 'delegacion']
    inlines = [FuncionarioRolInline]


@admin.register(FuncionarioRol)
class FuncionarioRolAdmin(admin.ModelAdmin):
    list_display = ['funcionario', 'rol']
    list_filter = ['rol']
    search_fields = ['funcionario__nombre', 'funcionario__identificador_institucional', 'rol__nombre_rol']
    autocomplete_fields = ['funcionario', 'rol']


@admin.register(UsuarioMaestro)
class UsuarioMaestroAdmin(admin.ModelAdmin):
    list_display = ['identificador_maestro', 'nombre', 'nivel_dominio', 'estado']
    list_filter = ['estado']
    search_fields = ['identificador_maestro', 'nombre', 'usuario__username']
    autocomplete_fields = ['usuario']


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'evento', 'entidad', 'identificador_registro', 'funcionario', 'usuario_maestro']
    list_filter = ['evento', 'entidad']
    search_fields = ['identificador_registro', 'funcionario__nombre', 'usuario_maestro__nombre']
    autocomplete_fields = ['funcionario', 'usuario_maestro']
    fields = ['fecha', 'funcionario', 'usuario_maestro', 'evento', 'entidad', 'identificador_registro', 'valor_anterior', 'valor_nuevo']
    readonly_fields = ['fecha']

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# Medición

@admin.register(Periodo)
class PeriodoAdmin(ProtegePeriodoCerradoAdmin, admin.ModelAdmin):
    list_display = ['nombre', 'fecha_inicio', 'fecha_termino', 'dias_computables', 'estado', 'umbral_minimo', 'version_parametros']
    list_filter = ['estado']
    search_fields = ['nombre']
    fields = ['nombre', 'fecha_inicio', 'fecha_termino', 'dias_computables', 'estado', 'umbral_minimo', 'version_parametros']
    readonly_fields = ['dias_computables']
    inlines = [ParametroVersionadoInline]


@admin.register(ParametroVersionado)
class ParametroVersionadoAdmin(ProtegePeriodoCerradoAdmin, admin.ModelAdmin):
    list_display = ['periodo', 'clave', 'valor']
    list_filter = ['periodo']
    search_fields = ['clave', 'valor', 'descripcion']
    autocomplete_fields = ['periodo']


@admin.register(ItemMedible)
class ItemMedibleAdmin(ProtegePeriodoCerradoAdmin, admin.ModelAdmin):
    list_display = ['nombre', 'cargo', 'periodo', 'servicio', 'ponderacion']
    list_filter = ['periodo', 'cargo']
    search_fields = ['nombre', 'servicio']
    autocomplete_fields = ['cargo', 'periodo']
    list_select_related = ['cargo', 'periodo']


@admin.register(Catalogo)
class CatalogoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'tipo', 'subtipo', 'area', 'activo']
    list_filter = ['tipo', 'activo']
    search_fields = ['codigo', 'nombre', 'area']


@admin.register(Meta)
class MetaAdmin(ProtegePeriodoCerradoAdmin, admin.ModelAdmin):
    list_display = ['item', 'funcionario', 'valor_objetivo', 'unidad', 'ponderador']
    list_filter = ['item__periodo', 'funcionario__delegacion']
    search_fields = ['item__nombre', 'funcionario__nombre']
    autocomplete_fields = ['item', 'funcionario']
    list_select_related = ['item__periodo', 'funcionario']


@admin.register(Indicador)
class IndicadorAdmin(ProtegePeriodoCerradoAdmin, admin.ModelAdmin):
    list_display = ['meta', 'periodo', 'fecha_calculo', 'avance', 'cumplimiento', 'ponderacion', 'ajuste', 'semaforo']
    list_filter = ['semaforo', 'periodo']
    search_fields = ['meta__item__nombre', 'meta__funcionario__nombre']
    autocomplete_fields = ['meta', 'periodo']
    date_hierarchy = 'fecha_calculo'


# Operación

@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ['codigo_verificador', 'delegacion', 'funcionario_autor', 'fecha_hora', 'estado', 'item']
    list_filter = ['estado', 'delegacion', 'item__periodo', 'catalogo']
    search_fields = ['codigo_verificador', 'solicitud_problema', 'accion', 'funcionario_autor__nombre']
    autocomplete_fields = ['delegacion', 'funcionario_autor', 'item', 'catalogo', 'compromiso']
    date_hierarchy = 'fecha_hora'
    fields = [
        'codigo_verificador', 'delegacion', 'funcionario_autor', 'item', 'catalogo', 'compromiso', 'fecha_hora',
        'solicitud_problema', 'accion', 'contacto_nombre', 'contacto_telefono', 'estado', 'version', 'creada', 'actualizada',
    ]
    readonly_fields = ['codigo_verificador', 'version', 'creada', 'actualizada']
    list_select_related = ['delegacion', 'funcionario_autor', 'item']
    inlines = [EvidenciaInline]


@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = ['codigo_evidencia', 'actividad', 'funcionario_autor', 'estado_revision', 'fecha_carga']
    list_filter = ['estado_revision']
    search_fields = ['codigo_evidencia', 'actividad__codigo_verificador']
    autocomplete_fields = ['actividad', 'funcionario_autor']
    fields = ['codigo_evidencia', 'actividad', 'funcionario_autor', 'archivo_vinculo', 'metadatos', 'estado_revision', 'fecha_carga']
    readonly_fields = ['codigo_evidencia', 'fecha_carga']
    inlines = [ValidacionInline]


@admin.register(Validacion)
class ValidacionAdmin(admin.ModelAdmin):
    list_display = ['evidencia', 'funcionario_verificador', 'decision', 'fecha', 'version']
    list_filter = ['decision']
    search_fields = ['evidencia__codigo_evidencia', 'observacion', 'funcionario_verificador__nombre']
    autocomplete_fields = ['evidencia', 'funcionario_verificador']
    date_hierarchy = 'fecha'


@admin.register(Compromiso)
class CompromisoAdmin(admin.ModelAdmin):
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


@admin.register(HistorialCompromiso)
class HistorialCompromisoAdmin(admin.ModelAdmin):
    list_display = ['compromiso', 'autor_funcionario', 'estado_anterior', 'estado_nuevo', 'fecha']
    list_filter = ['estado_anterior', 'estado_nuevo', 'fecha']
    search_fields = ['compromiso__folio', 'compromiso__descripcion', 'autor_funcionario__nombre', 'observacion']
    autocomplete_fields = ['compromiso', 'autor_funcionario']
    date_hierarchy = 'fecha'
    fields = ['compromiso', 'autor_funcionario', 'estado_anterior', 'estado_nuevo', 'observacion', 'fecha']
    readonly_fields = ['fecha']


@admin.register(MedicionDelegacion)
class MedicionDelegacionAdmin(admin.ModelAdmin):
    list_display = ['delegacion', 'cumplimiento', 'meta', 'fecha_datos', 'estado_reportado']
    list_filter = ['estado_reportado', 'delegacion', 'fecha_datos']
    search_fields = ['delegacion__nombre', 'observacion']
    autocomplete_fields = ['delegacion']
    date_hierarchy = 'fecha_datos'
