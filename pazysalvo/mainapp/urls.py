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
    path('reportar-equipo/', views.reportar_equipos, name='reportarequipos'),
    path('pendientes-almacen/', views.pendientes_almacen, name='pendientes-almacen'),
    path('reportar-bitacoras/', views.reportar_bitacoras, name='reportarbitacoras'),
    path('pendientes-bitacoras/', views.pendientes_bitacoras, name='pendientes-bitacoras'),
    path('reportar-horas/', views.reportar_horas, name='reportarhoras'),
    path('pendientes-horas/', views.pendientes_horas, name='pendienteshoras'),
    path('reportar-juicios/', views.reportar_juicios, name='reportarjuicios'),
    path('reportar-tyt/', views.reportar_tyt, name='reportartyt'),
    path('pendientes-juicios-tyt/', views.pendientes_juiciostyt, name='pendientesjuiciostyt'),
]

