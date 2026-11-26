from django.urls import path

from . import views

app_name = 'beneficiarios'

urlpatterns = [
    path('', views.inscripciones, name='inscripciones'),
    path('inscribir/', views.inscribir, name='inscribir'),
    path('importar/', views.importar, name='importar'),
    path('importar/plantilla/', views.plantilla, name='plantilla'),
    path('exportar/', views.exportar, name='exportar'),
    path('verificar-rut/', views.verificar_rut, name='verificar_rut'),
    path('<int:pk>/modificar/', views.modificar, name='modificar'),
    path('<int:pk>/eliminar/', views.eliminar, name='eliminar'),
    path('actividades/', views.eventos, name='eventos'),
    path('actividades/nueva/', views.evento_form, name='evento_nuevo'),
    path('actividades/<int:pk>/', views.evento_form, name='evento_editar'),
    path('unidades/', views.unidades, name='unidades'),
    path('unidades/nueva/', views.unidad_form, name='unidad_nueva'),
    path('unidades/<int:pk>/', views.unidad_form, name='unidad_editar'),
]
