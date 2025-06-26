from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from mainapp.models import Usuario, Login

# Create your views here.
def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        num_doc = request.POST.get('num_doc')
        password = request.POST.get('password')

        # Validación de campos vacíos
        if not num_doc or not password:
            messages.error(request, 'Debe ingresar el número de documento y la contraseña.')
            return render(request, 'login.html')

        # Validar que el número de documento sea un número entero
        if not num_doc.isdigit():
            messages.error(request, 'El número de documento debe ser numérico.')
            return render(request, 'login.html')

        try:
            usuario = Usuario.objects.get(num_doc=int(num_doc))
            login_data = Login.objects.get(id_usuario_FK=usuario)

            if login_data.password == password:
                request.session['usuario_id'] = usuario.id
                request.session['usuario_nombre'] = f"{usuario.nombre} {usuario.apellidos}"
                request.session['usuario_rol'] = usuario.id_rol_FK.nombre_rol
                return redirect('inicio')  # cambia esto por la vista principal
            else:
                messages.error(request, 'Contraseña incorrecta.')
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
        except Login.DoesNotExist:
            messages.error(request, 'Usuario sin credenciales asignadas.')

    return render(request, 'login.html')

def pazysalvo(request):
    return render(request, 'pazysalvo.html')

def inicio(request):
    return render(request, 'dashboard.html')

def aprendices(request):
    return render(request, 'aprendices.html')

def prestarlibro(request):
    return render(request, 'prestarlibro.html')

def pendientes_biblioteca(request):
    return render(request, 'pendientes-biblioteca.html')

def reportar_equipos(request):
    return render(request, 'reportarequipos.html')

def pendientes_almacen(request):
    return render(request, 'pendientes-almacen.html')