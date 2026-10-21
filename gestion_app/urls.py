from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('semaforo/', views.semaforo, name='semaforo'),
    path('resumen/', views.resumen, name='resumen'),
    path('mi-ficha/', views.ficha_personal, name='ficha_personal'),
    path('informes/', views.informe, name='informe'),
    path('alertas/', views.alertas, name='alertas'),
]
