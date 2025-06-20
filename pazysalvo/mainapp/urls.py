from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.custom_login, name='login'),
    path('pazysalvo/', views.pazysalvo, name='pazysalvo'),
    path('inicio/', views.inicio, name='inicio'),
    path('aprendices/', views.aprendices, name='aprendices'),
    path('prestarlibro/', views.prestarlibro, name='prestar-libro'),
    path('pendientes/', views.pendientes, name='pendientes'),
    path('pendientes/', views.pendientes, name='pendientes'),
]