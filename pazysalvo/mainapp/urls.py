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

    path('fichas/', views.fichas, name='fichas'),
    path('fichas/crear/', views.crear_ficha, name='crear_ficha'),
    path('fichas/editar/<int:ficha_id>/', views.editar_ficha, name='editar_ficha'),
    path('fichas/eliminar/<int:ficha_id>/', views.eliminar_ficha, name='eliminar_ficha'),

    # Otros módulos
    path('horasludicas/', views.horasludicas, name='horas-ludicas'),
    path('horas-faltantes/', views.horas_faltantes, name='horas-faltantes'),
    path('prestarequipos/', views.prestarequipos, name='prestar-equipos'),
    path('editar_prestamo/<int:id>/', views.editar_prestamo, name='editar_prestamo'),
    path('eliminar_prestamo/<int:id>/', views.eliminar_prestamo, name='eliminar_prestamo'),
    path('equiposalmacen/', views.equiposalmacen, name='equipos-almacen'),
    path('pendientesalmacen/', views.pendientesalmacen, name='pendientes-almacen'),
    path('prestarlibro/', views.prestarlibro, name='prestar-libro'),
    path('pendientes-biblioteca/', views.reportes_biblioteca, name='pendientes-biblioteca'),
    path('eliminar-prestamo/<int:id>/', views.eliminar_libro, name='eliminar_prestamo'),
]

