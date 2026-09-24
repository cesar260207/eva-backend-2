from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('semaforo/', views.semaforo, name='semaforo'),
    path('resumen/', views.resumen, name='resumen'),
]
