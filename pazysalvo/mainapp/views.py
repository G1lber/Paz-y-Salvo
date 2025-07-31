from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch, Max
from django.contrib.auth import authenticate, login
from django.contrib import messages
from mainapp.models import Usuario, Login, Roles

from .forms import UsuarioForm

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
    # Manejar creación
    if 'crear' in request.POST:
        form_crear = UsuarioForm(request.POST)
        if form_crear.is_valid():
            usuario = form_crear.save(commit=False)
            usuario.id_rol_FK = Roles.objects.get(id=7)  # Rol aprendiz
            usuario.save()
            messages.success(request, 'Aprendiz creado correctamente!')
            return redirect('aprendices')
        else:
            for error in form_crear.errors.values():
                messages.error(request, error)

    # Manejar edición
    elif 'editar' in request.POST:
        usuario_id = request.POST.get('usuario_id')
        usuario = get_object_or_404(Usuario, pk=usuario_id)
        form_editar = UsuarioForm(request.POST, instance=usuario)
        if form_editar.is_valid():
            form_editar.save()
            messages.success(request, 'Cambios guardados correctamente!')
            return redirect('aprendices')
        else:
            for error in form_editar.errors.values():
                messages.error(request, error)

    # Obtener lista de aprendices
    aprendices = Usuario.objects.filter(id_rol_FK=7).order_by('apellidos', 'nombre')
    form_crear = UsuarioForm()  # Formulario vacío para crear
    form_editar = UsuarioForm() # Formulario vacío para editar (se llenará con JS)

    return render(request, 'aprendices.html', {
        'aprendices': aprendices,
        'form_crear': form_crear,
        'form_editar': form_editar
    })
AQUIII


def prestarlibro(request):
    return render(request, 'prestarlibro.html')

def pendientes_biblioteca(request):
    return render(request, 'pendientes-biblioteca.html')

def reportar_equipos(request):
    return render(request, 'reportarequipos.html')

def pendientes_almacen(request):
    return render(request, 'pendientes-almacen.html')

def reportar_bitacoras(request):
    return render(request, 'reportarbitacoras.html')

def pendientes_bitacoras(request):
    return render(request, 'pendientes-bitacoras.html')

def reportar_horas(request):
    return render(request, 'reportarhoras.html')

def pendientes_horas(request):
    return render(request, 'pendientes-horas.html')

def reportar_juicios(request):
    return render(request, 'reportarjuicios.html')

def reportar_tyt(request):
    return render(request, 'reportartyt.html')

def pendientes_juiciostyt(request):
    return render(request, 'pendientes-juicios-tyt.html')

