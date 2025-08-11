from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('pazysalvo/', views.pazysalvo, name='pazysalvo'),
    path('inicio/', views.inicio, name='inicio'),
    path('aprendices/', views.aprendices, name='aprendices'),

    # Usuarios
    path('usuarios/', views.lista_usuarios, name='usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),

    # Otros módulos
    path('prestarlibro/', views.prestarlibro, name='prestar-libro'),
    path('pendientes-biblioteca/', views.pendientes_biblioteca, name='pendientes-biblioteca'),
    
]

