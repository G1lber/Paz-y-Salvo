from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('pazysalvo/', views.pazysalvo, name='pazysalvo'),
    path('inicio/', views.inicio, name='inicio'),
    path('aprendices/', views.aprendices, name='aprendices'),
    path('aprendices-instructor/', views.aprendicesxinstructor, name='aprendices-instructor'),
    path('editar-bitacoras/', views.editar_bitacoras, name='editar_bitacoras'),

    # Usuarios
    path('usuarios/', views.lista_usuarios, name='usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),

    path('fichas/', views.fichas, name='fichas'),
    path('fichas/crear/', views.crear_ficha, name='crear-ficha'),
    path('fichas/editar/', views.editar_ficha, name='editar-ficha'),
    path('fichas/eliminar/', views.eliminar_ficha, name='eliminar-ficha'),
    path("crear-programa/", views.crear_programa, name="crear-programa"),

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
    path('actualizar-datos/', views.actualizar_datos_aprendiz, name='actualizar_datos_aprendiz'),
    path('agencia-publica-empleo/', views.agencia_empleo, name='agencia-publica-empleo'),
    path('descargar-reporte-empleo/', views.descargar_reporte_empleo, name='descargar-reporte-empleo'),
    path('descargar-paz-y-salvo/', views.descargar_paz_y_salvo, name='descargar-paz-y-salvo'),
]

