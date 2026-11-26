from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('panel/', views.panel, name='panel'),
    path('tablero/', views.tablero_analitico, name='tablero_analitico'),
    path('semaforo/', views.semaforo, name='semaforo'),
    path('matriz/', views.matriz_cargos, name='matriz_cargos'),
    path('resumen/', views.resumen, name='resumen'),
    path('mi-ficha/', views.ficha_personal, name='ficha_personal'),
    path('informes/', views.informe, name='informe'),
    path('alertas/', views.alertas, name='alertas'),
]
