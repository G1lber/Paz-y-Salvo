from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch, Max
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Usuario, Login, Roles, Seguimiento, TipoDoc, Ficha
from .forms import UsuarioForm, SeguimientoForm
from django.db.models import Q
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password


# Create your views here.
def index(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == 'POST':
        num_doc = request.POST.get('num_doc')
        password = request.POST.get('password')

        if not num_doc or not password:
            messages.error(request, 'Debe ingresar el número de documento y la contraseña.')
            return render(request, 'login.html')

        if not num_doc.isdigit():
            messages.error(request, 'El número de documento debe ser numérico.')
            return render(request, 'login.html')

        try:
            usuario = Usuario.objects.get(num_doc=int(num_doc))
            login_data = Login.objects.get(id_usuario_FK=usuario)

            if check_password(password, login_data.password):
                request.session['usuario_id'] = usuario.id
                request.session['usuario_nombre'] = f"{usuario.nombre} {usuario.apellidos}"
                request.session['usuario_rol'] = usuario.id_rol_FK.nombre_rol
                return redirect('inicio')
            else:
                messages.error(request, 'Contraseña incorrecta.')

        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
        except Login.DoesNotExist:
            messages.error(request, 'Usuario sin credenciales asignadas.')

    return render(request, 'login.html')
# TODO: MODULO USUARIO

def crear_usuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        num_doc = request.POST.get('num_doc')
        id_tipodoc = request.POST.get('id_tipodoc_FK')
        id_rol = request.POST.get('id_rol_FK')
        id_ficha = request.POST.get('id_ficha_FK')  # Puede ser None si no aplica
        password = request.POST.get('password')  # Solo llegará si no es aprendiz

        # Validar si ya existe el número de documento
        if Usuario.objects.filter(num_doc=num_doc).exists():
            messages.error(request, 'Ya existe un usuario con ese número de documento.')
            return redirect('usuarios')

        try:
            # Crear el usuario
            usuario = Usuario.objects.create(
                nombre=nombre,
                apellidos=apellidos,
                num_doc=num_doc,
                id_tipodoc_FK_id=id_tipodoc,
                id_rol_FK_id=id_rol,
                id_ficha_FK_id=id_ficha if id_rol == '1' else None  # Ficha solo si es aprendiz
            )

            # Si el rol NO es aprendiz, se crea el Login con contraseña
            if id_rol != '5':  # Asegúrate de que '5' sea el ID del rol "Aprendiz"
                if password:
                    Login.objects.create(
                        id_usuario_FK=usuario,
                        password=make_password(password) # Recomendado: usar make_password(password)
                    )
                else:
                    messages.warning(request, 'Contraseña no proporcionada para un rol que la requiere.')

            messages.success(request, 'Usuario creado exitosamente.')

        except IntegrityError:
            messages.error(request, 'Error de integridad al crear el usuario.')

        return redirect('usuarios')
    
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    tipos_doc = TipoDoc.objects.all()
    roles = Roles.objects.all()
    fichas = Ficha.objects.all()

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        num_doc = request.POST.get('num_doc')
        id_tipodoc = request.POST.get('id_tipodoc_FK')
        id_rol = request.POST.get('id_rol_FK')
        id_ficha = request.POST.get('id_ficha_FK')
        password = request.POST.get('password')

        # Actualizar datos básicos
        usuario.nombre = nombre
        usuario.apellidos = apellidos
        usuario.num_doc = num_doc
        usuario.id_tipodoc_FK = TipoDoc.objects.get(pk=id_tipodoc)
        usuario.id_rol_FK = Roles.objects.get(pk=id_rol)

        # Solo asigna ficha si el rol es aprendiz (por ejemplo ID = 5)
        if id_rol == '5' and id_ficha:
            usuario.id_ficha_FK = Ficha.objects.get(pk=id_ficha)
        else:
            usuario.id_ficha_FK = None

        usuario.save()

        # Manejo de contraseña solo si el rol NO es aprendiz
        if id_rol != '5' and password:
            login = Login.objects.filter(id_usuario_FK=usuario).first()
            if login:
                login.password = make_password(password)
                login.save()
            else:
                Login.objects.create(
                    id_usuario_FK=usuario,
                    contraseña=make_password(password)
                )
            messages.success(request, 'Contraseña actualizada.')

        messages.success(request, 'Usuario actualizado exitosamente.')
        return redirect('usuarios')

    return render(request, 'editar_usuario.html', {
        'usuario': usuario,
        'tipos_doc': tipos_doc,
        'roles': roles,
        'fichas': fichas,
    })
def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)

    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
        return redirect('usuarios')  # <- Asegúrate de que diga 'usuarios' aquí

    return render(request, 'eliminar_usuario.html', {'usuario': usuario})

    
def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    tipos_doc = TipoDoc.objects.all()
    roles = Roles.objects.all()
    fichas = Ficha.objects.all()

    return render(request, 'usuarios.html', {
        'usuarios': usuarios,
        'tipos_doc': tipos_doc,
        'roles': roles,
        'fichas': fichas,
    })

# TODO: FIN MODULO USUARIO
def pazysalvo(request):
    return render(request, 'pazysalvo.html')


def inicio(request):
    return render(request, 'dashboard.html')


# TODO: MODULO APRENDICES 
def aprendices(request):
    #FUNCION de busquedad
    busqueda = request.GET.get('busqueda', '')
    aprendices = Usuario.objects.filter(id_rol_FK=5).prefetch_related('seguimientos_como_aprendiz')
    if busqueda:
        aprendices = aprendices.filter(
            Q(nombre__icontains=busqueda) |
            Q(apellidos__icontains=busqueda) |
            Q(num_doc__icontains=busqueda)
        )
    aprendices = aprendices.order_by('apellidos', 'nombre')

    form_crear = UsuarioForm()
    form_editar = UsuarioForm()
    instSeguimiento = None  # 👈 Inicialización segura aquí
    # POST - crear aprendiz
    if request.method == 'POST':
        if 'crear' in request.POST: #FUNCIÓN de crear aprendices
            form_crear = UsuarioForm(request.POST)
            if form_crear.is_valid():
                # Obtener el instructor seleccionado del formulario
                id_instructor2 = form_crear.cleaned_data.get('id_instructor')

                # Guardar el nuevo usuario como aprendiz
                usuario = form_crear.save(commit=False)
                usuario.id_rol_FK = Roles.objects.get(id=5)  # Rol aprendiz
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

                    # Obtener instructor nuevo del formulario
                    id_instructor_nuevo = request.POST.get('id_instructor')
                    if id_instructor_nuevo:
                        # Obtener o crear el seguimiento existente
                        seguimiento, creado = Seguimiento.objects.get_or_create(id_aprendiz=usuario)
                        seguimiento.id_instructor_id = id_instructor_nuevo
                        seguimiento.save()

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
        'busqueda': busqueda,
        'instructores': Usuario.objects.filter(id_rol_FK=2),
    })
# TODO: FIN MODULO APRENDICES

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


