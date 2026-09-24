from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='inicio'),
    path('solicitudes/', views.solicitudes, name='solicitudes'),
    path('agenda/', views.agenda, name='agenda'),
    path('agenda/nueva/', views.compromiso_nuevo, name='compromiso_nuevo'),
    path('agenda/<int:pk>/estado/<str:estado>/', views.compromiso_estado, name='compromiso_estado'),
    path('actividades/', views.actividades, name='actividades'),
    path('actividad/nueva/', views.actividad_nueva, name='actividad_nueva'),
    path('actividad/<str:codigo>/', views.actividad_detalle, name='actividad_detalle'),
    path('actividad/<str:codigo>/<str:decision>/', views.revisar_actividad, name='revisar_actividad'),
    path('administracion/delegaciones/', views.delegaciones_crud, name='delegaciones_crud'),
    path('administracion/', views.mantenedores, name='mantenedores'),
    path('administracion/<slug:slug>/', views.mantenedor_lista, name='mantenedor_lista'),
    path('administracion/delegaciones/nueva/', views.delegacion_form, name='delegacion_nueva'),
    path('administracion/delegaciones/<int:pk>/editar/', views.delegacion_form, name='delegacion_editar'),
    path('territorio/', views.institucional, name='institucional'),
    path('delegacion/<str:nombre>/', views.delegacion_detalle, name='delegacion_detalle'),
]
