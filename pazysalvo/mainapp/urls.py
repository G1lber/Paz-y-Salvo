from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('pazysalvo/', views.pazysalvo, name='pazysalvo'),
    path('inicio/', views.inicio, name='inicio'),
    path('aprendices/', views.aprendices, name='aprendices'),
    path('prestarlibro/', views.prestarlibro, name='prestar-libro'),
    path('pendientes-biblioteca/', views.pendientes_biblioteca, name='pendientes-biblioteca'),
    path('reportar-equipo/', views.reportar_equipos, name='reportarequipos'),
    path('pendientes-almacen/', views.pendientes_almacen, name='pendientes-almacen'),
]