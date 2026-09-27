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
    path('administracion/perfiles/', views.perfiles_usuario, name='perfiles_usuario'),
    path('administracion/periodos/', views.periodos_medicion, name='periodos_medicion'),
    path('administracion/', views.mantenedores, name='mantenedores'),
    path('administracion/delegaciones/nueva/', views.delegacion_form, name='delegacion_nueva'),
    path('administracion/delegaciones/<int:pk>/editar/', views.delegacion_form, name='delegacion_editar'),
    path('administracion/delegaciones/<int:pk>/estado/', views.delegacion_cambiar_estado, name='delegacion_cambiar_estado'),
    path('administracion/catalogo/', views.catalogo_lista, name='catalogo_lista'),
    path('administracion/catalogo/nuevo/', views.catalogo_form, name='catalogo_nuevo'),
    path('administracion/catalogo/<int:pk>/editar/', views.catalogo_form, name='catalogo_editar'),
    path('administracion/catalogo/<int:pk>/eliminar/', views.catalogo_eliminar, name='catalogo_eliminar'),
    # Las rutas especificas de cada CRUD deben ir antes de esta ruta generica.
    path('administracion/<slug:slug>/', views.mantenedor_lista, name='mantenedor_lista'),
    path('territorio/', views.institucional, name='institucional'),
    path('delegacion/<str:nombre>/', views.delegacion_detalle, name='delegacion_detalle'),
]
