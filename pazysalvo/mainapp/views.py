from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch, Max
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Usuario, Login, Roles, Seguimiento
from .forms import UsuarioForm, SeguimientoForm
from django.db.models import Q



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

def crear_usuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        documento = request.POST.get('documento')
        rol = request.POST.get('rol')

        Usuario.objects.create(
            nombre=nombre,
            apellidos=apellidos,
            documento=documento,
            rol=rol
        )
        return redirect('usuarios')
    return redirect('usuarios')

def pazysalvo(request):
    return render(request, 'pazysalvo.html')

def inicio(request):
    return render(request, 'dashboard.html')


def usuarios(request):
    return render(request, 'usuarios.html')


def aprendices(request):
    busqueda = request.GET.get('busqueda', '')
    aprendices = Usuario.objects.filter(id_rol_FK=7)
    if busqueda:
        aprendices = aprendices.filter(
            Q(nombre__icontains=busqueda) |
            Q(apellidos__icontains=busqueda) |
            Q(num_doc__icontains=busqueda)
        )
    aprendices = aprendices.order_by('apellidos', 'nombre')

    form_crear = UsuarioForm()
    form_editar = UsuarioForm()

    # POST - crear aprendiz
    if request.method == 'POST':
        if 'crear' in request.POST:
            form_crear = UsuarioForm(request.POST)
            print(form_crear)
            if form_crear.is_valid():
                # Obtener el instructor seleccionado del formulario
                id_instructor2 = form_crear.cleaned_data.get('id_instructor')

                # Guardar el nuevo usuario como aprendiz
                usuario = form_crear.save(commit=False)
                usuario.id_rol_FK = Roles.objects.get(id=7)  # Rol aprendiz
                usuario.save()  # OJO: ahora sí estás guardando correctamente
                # Crear el seguimiento
                seguimiento = Seguimiento.objects.create(
                    id_aprendiz=usuario,
                    id_instructor=id_instructor2
                )
                messages.success(request, 'Aprendiz creado correctamente!')
                return redirect('aprendices')
            else:
                for error in form_crear.errors.values():
                    messages.error(request, error)

        elif 'editar' in request.POST:
            usuario_id = request.POST.get('usuario_id')
            if usuario_id:
                usuario = get_object_or_404(Usuario, pk=usuario_id)
                form_editar = UsuarioForm(request.POST, instance=usuario)
                if form_editar.is_valid():
                    form_editar.save()
                    messages.success(request, 'Cambios guardados correctamente!')
                    return redirect('aprendices')
                else:
                    for error in form_editar.errors.values():
                        messages.error(request, error)

    # Siempre devolver render
    return render(request, 'aprendices.html', {
        'aprendices': aprendices,
        'form_crear': form_crear,
        'form_editar': form_editar,
        'busqueda': busqueda
    })


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


