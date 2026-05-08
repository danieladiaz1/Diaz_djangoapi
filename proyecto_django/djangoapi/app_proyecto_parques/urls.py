from django.urls import path
from . import views

urlpatterns = [
    path('zonas/', views.Zonas.as_view(), name='Zonas'),
    path('rutas/', views.Rutas.as_view(), name='Rutas'),
    path('fuentes/', views.Fuentes.as_view(), name='Fuentes'),
]