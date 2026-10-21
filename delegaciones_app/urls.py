from django.urls import path
from . import crud, views

urlpatterns = [
    path('', views.index, name='inicio'),
    path('solicitudes/', views.solicitudes, name='solicitudes'),
    path('agenda/', views.agenda, name='agenda'),
    path('agenda/nueva/', views.compromiso_nuevo, name='compromiso_nuevo'),
    path('agenda/<int:pk>/estado/<str:estado>/', views.compromiso_estado, name='compromiso_estado'),
    path('agenda/<int:pk>/editar/', views.compromiso_editar, name='compromiso_editar'),
    path('agenda/<int:pk>/eliminar/', views.compromiso_eliminar, name='compromiso_eliminar'),
    path('actividades/', views.actividades, name='actividades'),
    path('actividad/nueva/', views.actividad_nueva, name='actividad_nueva'),
    path('actividad/<str:codigo>/', views.actividad_detalle, name='actividad_detalle'),
    # editar/eliminar deben ir antes de <str:decision>, que tambien los capturaria.
    path('actividad/<str:codigo>/editar/', views.actividad_editar, name='actividad_editar'),
    path('actividad/<str:codigo>/eliminar/', views.actividad_eliminar, name='actividad_eliminar'),
    path('actividad/<str:codigo>/<str:decision>/', views.revisar_actividad, name='revisar_actividad'),
    # Mantenedores de las tablas maestras (ver crud.py).
    path('administracion/', crud.indice, name='mantenedores'),
    path('administracion/periodos/<int:pk>/estado/<str:accion>/', crud.PeriodoAccion.as_view(), name='periodo_accion'),
    path('administracion/<slug:slug>/', crud.MantenedorLista.as_view(), name='mantenedor_lista'),
    path('administracion/<slug:slug>/nuevo/', crud.MantenedorNuevo.as_view(), name='mantenedor_nuevo'),
    path('administracion/<slug:slug>/<int:pk>/editar/', crud.MantenedorEditar.as_view(), name='mantenedor_editar'),
    path('administracion/<slug:slug>/<int:pk>/eliminar/', crud.MantenedorEliminar.as_view(), name='mantenedor_eliminar'),
    path('territorio/', views.institucional, name='institucional'),
    path('delegacion/<str:nombre>/', views.delegacion_detalle, name='delegacion_detalle'),
]
