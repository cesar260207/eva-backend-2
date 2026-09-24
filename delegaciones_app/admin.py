from django.contrib import admin

from .models import (
    Actividad,
    Auditoria,
    CatalogoItem,
    Compromiso,
    Delegacion,
    Evidencia,
    HistorialCompromiso,
    MetaMedicion,
    PerfilUsuario,
    PeriodoMedicion,
)


class EvidenciaInline(admin.TabularInline):
    model = Evidencia
    extra = 0


class HistorialCompromisoInline(admin.TabularInline):
    model = HistorialCompromiso
    extra = 0
    readonly_fields = ['autor', 'estado_anterior', 'estado_nuevo', 'observacion', 'fecha']
    can_delete = False


@admin.register(Delegacion)
class DelegacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'territorio', 'activa']
    list_filter = ['activa']
    search_fields = ['nombre', 'territorio']


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'rol', 'delegacion', 'cargo']
    list_filter = ['rol', 'delegacion']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name', 'cargo']
    autocomplete_fields = ['usuario', 'delegacion']


@admin.register(CatalogoItem)
class CatalogoItemAdmin(admin.ModelAdmin):
    list_display = ['categoria', 'codigo', 'nombre', 'area', 'activo']
    list_filter = ['categoria', 'activo']
    search_fields = ['codigo', 'nombre', 'area']


@admin.register(PeriodoMedicion)
class PeriodoMedicionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'inicio', 'termino', 'estado', 'umbral_colectivo', 'maximo_cumplimiento']
    list_filter = ['estado']
    search_fields = ['nombre']


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'delegacion', 'funcionario', 'fecha', 'estado', 'item_medicion']
    list_filter = ['estado', 'delegacion', 'tipo_atencion']
    search_fields = ['codigo', 'descripcion', 'accion', 'item_medicion', 'funcionario__username']
    autocomplete_fields = ['delegacion', 'funcionario']
    date_hierarchy = 'fecha'
    readonly_fields = ['codigo', 'creada', 'actualizada']
    inlines = [EvidenciaInline]


@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = ['actividad', 'archivo', 'aprobada', 'revisada_por', 'creada']
    list_filter = ['aprobada']
    search_fields = ['actividad__codigo']
    autocomplete_fields = ['actividad', 'revisada_por']


@admin.register(Compromiso)
class CompromisoAdmin(admin.ModelAdmin):
    list_display = ['folio', 'delegacion', 'responsable', 'eje', 'estado', 'fecha_comprometida']
    list_filter = ['estado', 'eje', 'delegacion']
    search_fields = ['folio', 'descripcion', 'solicitante', 'territorio']
    autocomplete_fields = ['delegacion', 'responsable']
    date_hierarchy = 'fecha_comprometida'
    readonly_fields = ['creado']
    inlines = [HistorialCompromisoInline]


@admin.register(MetaMedicion)
class MetaMedicionAdmin(admin.ModelAdmin):
    list_display = ['delegacion', 'nombre', 'objetivo', 'avance', 'ponderador', 'activa']
    list_filter = ['activa', 'delegacion']
    search_fields = ['nombre', 'delegacion__nombre']
    autocomplete_fields = ['delegacion']


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'usuario', 'accion', 'entidad', 'identificador']
    list_filter = ['accion', 'entidad']
    search_fields = ['identificador', 'usuario__username']
    autocomplete_fields = ['usuario']
    readonly_fields = ['usuario', 'accion', 'entidad', 'identificador', 'detalle', 'fecha']

    def has_add_permission(self, request):
        # La auditoría se genera automáticamente desde las vistas; no se crea a mano.
        return False
