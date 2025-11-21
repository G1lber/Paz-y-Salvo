from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch, Max
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Centro, Usuario, Login, Roles, Seguimiento, TipoDoc, Ficha, InstructorxAprendiz, PrestarEquipos, PrestamoLibro
from .models import PrestamoBienestar, RegistroHoras, Programa
from .forms import UsuarioForm, SeguimientoForm
from django.db.models import Q
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from .models import Ficha, Programa
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import datetime, date
from django.db.models import Sum
from django.core.paginator import Paginator
from django.http import JsonResponse
import pandas as pd
from django.contrib.auth.decorators import login_required
from datetime import date

# Create your views here.
def index(request):
    if request.method == "POST":
        num_doc = request.POST.get("username")

        try:
            usuario = Usuario.objects.get(num_doc=num_doc)
        except Usuario.DoesNotExist:
            return render(request, "index.html", {"error": "Documento no registrado"})

        # Validar rol Aprendiz
        if usuario.id_rol_FK.nombre_rol != "Aprendiz":
            return render(request, "index.html", {"error": "Solo los aprendices pueden ingresar"})

        # Guardamos el ID en sesión
        request.session["usuario_id"] = usuario.id

        return redirect("pazysalvo")

    return render(request, "index.html")


def login_view(request):

    storage = messages.get_messages(request)
    storage.used = True

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
    busqueda = request.GET.get('busqueda', '')

    usuarios = Usuario.objects.all()
    if busqueda:
        usuarios = usuarios.filter(
            Q(nombre__icontains=busqueda) |
            Q(apellidos__icontains=busqueda) |
            Q(num_doc__icontains=busqueda)
        )

    usuarios = usuarios.order_by('nombre')

    # Paginación
    paginator = Paginator(usuarios, 8)
    page_number = request.GET.get('page')
    usuarios_page = paginator.get_page(page_number)

    # Datos adicionales
    tipos_doc = TipoDoc.objects.all()
    roles = Roles.objects.all()
    fichas = Ficha.objects.all()

    return render(request, 'admin/usuarios.html', {
        'usuarios': usuarios_page,
        'tipos_doc': tipos_doc,
        'roles': roles,
        'fichas': fichas,
        'busqueda': busqueda, 
    })


# TODO: FIN MODULO USUARIO
def pazysalvo(request):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("login")

    usuario = Usuario.objects.get(id=usuario_id)

    # Validación: ¿Tiene préstamos en biblioteca?
    tiene_prestamos = PrestamoLibro.objects.filter(id_usuario_FK=usuario).exists()

    return render(request, "aprendiz/pazysalvo.html", {
        "usuario": usuario,
        "tiene_prestamos": tiene_prestamos,
        "cumple_horas_bienestar": usuario.cumple_horas_bienestar(),  # Nueva variable
    })


def inicio(request):
    return render(request, 'menu/dashboard.html')


# TODO: MODULO APRENDICES 
def aprendices(request):
    busqueda = request.GET.get('busqueda', '')
    aprendices_qs = Usuario.objects.filter(
        id_rol_FK__nombre_rol="Aprendiz"
    ).prefetch_related('seguimientos_como_aprendiz')

    if busqueda:
        aprendices_qs = aprendices_qs.filter(
            Q(nombre__icontains=busqueda) |
            Q(apellidos__icontains=busqueda) |
            Q(num_doc__icontains=busqueda)
        )

    aprendices_qs = aprendices_qs.order_by('apellidos', 'nombre')

    # Paginación
    paginator = Paginator(aprendices_qs, 8)  # 8 registros por página
    page_number = request.GET.get('page')
    aprendices_page = paginator.get_page(page_number)

    form_crear = UsuarioForm()
    form_editar = UsuarioForm()

    if request.method == 'POST':
        if 'crear' in request.POST:
            form_crear = UsuarioForm(request.POST)
            if form_crear.is_valid():
                id_instructor2 = form_crear.cleaned_data.get('id_instructor')
                usuario = form_crear.save(commit=False)
                usuario.id_rol_FK = Roles.objects.get(nombre_rol="Aprendiz")
                usuario.save()

                Seguimiento.objects.create(id_aprendiz=usuario, id_instructor=id_instructor2)
                InstructorxAprendiz.objects.create(id_instructor_FK=id_instructor2, id_aprendiz_FK=usuario)

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

                    id_instructor_nuevo = request.POST.get('id_instructor')
                    if id_instructor_nuevo:
                        seguimiento, _ = Seguimiento.objects.get_or_create(id_aprendiz=usuario)
                        seguimiento.id_instructor_id = id_instructor_nuevo
                        seguimiento.save()

                        instxapr, _ = InstructorxAprendiz.objects.get_or_create(id_aprendiz_FK=usuario)
                        instxapr.id_instructor_FK_id = id_instructor_nuevo
                        instxapr.save()

                    messages.success(request, 'Cambios guardados correctamente!')
                    return redirect('aprendices')
                else:
                    for error in form_editar.errors.values():
                        messages.error(request, error)

    return render(request, 'coordinador/aprendices.html', {
        'aprendices': aprendices_page,  # 👈 ahora se pasa el paginado
        'form_crear': form_crear,
        'form_editar': form_editar,
        'busqueda': busqueda,
        'instructores': Usuario.objects.filter(id_rol_FK__nombre_rol="Instructor"),
    })
# TODO: FIN MODULO APRENDICES
def editar_bitacoras(request):
    if request.method == "POST":
        # Debe coincidir con el name del input hidden del modal
        relacion_id = request.POST.get('relacion_id')  
        relacion = get_object_or_404(InstructorxAprendiz, id=relacion_id)
        relacion.bitacoras_completas = 'bitacoras_completas' in request.POST
        relacion.save()
        messages.success(request, 'Bitácoras actualizadas correctamente.')
        return redirect('aprendices-instructor')
        
def aprendicesxinstructor(request):
    instructor_id = request.session.get('usuario_id')
    if not instructor_id:
        return redirect('login')

    try:
        instructor = Usuario.objects.get(id=instructor_id)
    except Usuario.DoesNotExist:
        return HttpResponse("El instructor no existe en la base de datos")

    # Relaciones solo del instructor actual
    relaciones_instructor = InstructorxAprendiz.objects.filter(id_instructor_FK=instructor)

    # Aprendices relacionados
    aprendices_qs = Usuario.objects.filter(
        id__in=relaciones_instructor.values_list('id_aprendiz_FK', flat=True)
    ).prefetch_related(
        Prefetch(
            'aprendiz_en_seguimiento',  # ← Aquí va el related_name correcto
            queryset=relaciones_instructor,
            to_attr='relaciones_instructor_filtradas'
        )
    )

    # Filtro de búsqueda
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        aprendices_qs = aprendices_qs.filter(
            Q(nombre__icontains=busqueda) |
            Q(apellidos__icontains=busqueda) |
            Q(num_doc__icontains=busqueda)
        )

    paginator = Paginator(aprendices_qs.order_by('nombre'), 10)
    page_number = request.GET.get('page')
    aprendices_page = paginator.get_page(page_number)

    return render(request, 'instructor/aprendices.html', {
        'aprendices': aprendices_page
    })

def horasludicas(request):
    if request.method == 'POST':
        # Si viene un archivo Excel
        if 'subir_excel' in request.POST:
            archivo = request.FILES.get('archivo_excel')
            if not archivo:
                messages.error(request, "Debes seleccionar un archivo Excel.")
                return redirect('horas-ludicas')

            try:
                # Leer el archivo Excel con pandas
                df = pd.read_excel(archivo)

                # Se espera que el Excel tenga columnas: documento, horas
                for _, fila in df.iterrows():
                    documento = str(fila.get('documento')).strip() if fila.get('documento') else None
                    horas = fila.get('horas')

                    # Validar datos vacíos
                    if not documento or pd.isna(horas):
                        continue  # salta filas vacías o incompletas

                    try:
                        horas = int(horas)
                        usuario = Usuario.objects.get(num_doc=documento)
                        RegistroHoras.objects.create(
                            id_usuario_FK=usuario,
                            cantidad_horas=horas
                        )
                    except Usuario.DoesNotExist:
                        messages.warning(request, f"No se encontró usuario con documento {documento}")
                    except ValueError:
                        messages.warning(request, f"Las horas deben ser numéricas para el documento {documento}")

                messages.success(request, "Archivo procesado correctamente.")
            except Exception as e:
                messages.error(request, f"Error al procesar el archivo: {e}")

            return redirect('horas-ludicas')

        # Si se registra manualmente
        else: 
            documento = request.POST.get('aprendiz')
            horas = request.POST.get('horas')

            try:
                usuario = Usuario.objects.get(num_doc=documento)
                RegistroHoras.objects.create(
                    id_usuario_FK=usuario,
                    cantidad_horas=horas
                )
                messages.success(request, f"Se registraron {horas} hora(s) al aprendiz {usuario.nombre}.")
            except Usuario.DoesNotExist:
                messages.error(request, "No existe un aprendiz con ese documento.")

            return redirect('horas-ludicas')

    return render(request, 'bienestar/horas-ludicas.html')

def horas_faltantes(request):
    # Obtener todos los aprendices (usuarios con rol de aprendiz)
    aprendices = Usuario.objects.filter(id_rol_FK__nombre_rol='Aprendiz')
    
    horas_data = []
    
    for aprendiz in aprendices:
        # Obtener horas registradas
        horas_registradas = RegistroHoras.objects.filter(
            id_usuario_FK=aprendiz
        ).aggregate(total=Sum('cantidad_horas'))['total'] or 0
        
        # Obtener programa y horas requeridas
        horas_requeridas = 0
        programa_nombre = "No asignado"
        
        if aprendiz.id_ficha_FK and aprendiz.id_ficha_FK.programa_FK:
            programa = aprendiz.id_ficha_FK.programa_FK
            programa_nombre = programa.nombre_programa
            horas_requeridas = programa.horas_requeridas()
        
        # Calcular horas faltantes
        horas_faltantes = max(0, horas_requeridas - horas_registradas)
        
        #Mostrar aprendices le falten o no horas (if True:)
        # Solo mostrar aprendices que les falten horas
        if horas_faltantes > 0:
            horas_data.append({
                'aprendiz': aprendiz,
                'programa': programa_nombre,
                'horas_registradas': horas_registradas,
                'horas_requeridas': horas_requeridas,
                'horas_faltantes': horas_faltantes,
                'porcentaje_completado': (horas_registradas / horas_requeridas * 100) if horas_requeridas > 0 else 0
            })
    
    # Ordenar por horas faltantes (mayor a menor)
    horas_data.sort(key=lambda x: x['horas_faltantes'], reverse=True)
    
    return render(request, 'bienestar/horas_faltantes.html', {
        'horas_data': horas_data
    })

def prestarequipos(request):
    if request.method == 'POST':
        documento = request.POST.get('documento')
        equipo = request.POST.get('equipo')
        serial = request.POST.get('serial')
        fecha_prestamo = request.POST.get('fecha_prestamo')
        fecha_devolucion = request.POST.get('fecha_devolucion')
        observaciones = request.POST.get('observaciones')

        if PrestamoBienestar.objects.filter(serial=serial).exists():
            messages.error(request, f"Ya existe un préstamo con el serial {serial}.")
            return redirect('prestar-equipos')
        
        try:
            usuario = Usuario.objects.get(num_doc=documento)
            PrestamoBienestar.objects.create(
                id_usuario_FK=usuario,
                nombre_equipo=equipo,
                serial= serial,
                fecha_prestamo=fecha_prestamo,
                fecha_devolucion=fecha_devolucion if fecha_devolucion else None,
                observaciones=observaciones,
            )
            messages.success(request, "Reporte guardado correctamente ✅")
            return redirect('prestar-equipos')  # Evita reenvío del formulario
        except Usuario.DoesNotExist:
            messages.error(request, "El documento ingresado no pertenece a ningún aprendiz registrado ❌")

    # Mostrar todos los reportes
    reportes = PrestamoBienestar.objects.select_related('id_usuario_FK').all().order_by('id')

    return render(request, 'bienestar/prestar-equipos.html', {'reportes': reportes})


def editar_prestamo(request, id):
    prestamo = get_object_or_404(PrestamoBienestar, id=id)

    if request.method == 'POST':
        prestamo.nombre_equipo = request.POST.get('nombre_equipo')
        prestamo.serial = request.POST.get('serial')
        prestamo.fecha_prestamo = request.POST.get('fecha_prestamo')
        prestamo.fecha_devolucion = request.POST.get('fecha_devolucion')
        prestamo.observaciones = request.POST.get('observaciones')
        prestamo.save()
        messages.success(request, 'El préstamo fue actualizado correctamente.')
        return redirect('prestar-equipos')  
    
    return render(request, 'modales/modalEditarPrestamo.html', {'prestamo': prestamo})


def eliminar_prestamo(request, id):
    prestamo = get_object_or_404(PrestamoBienestar, id=id)
    prestamo.delete()
    messages.success(request, 'El préstamo fue eliminado correctamente.')
    return redirect('prestar-equipos')  

def equiposalmacen(request):  
    if request.method == 'POST':
        documento = request.POST.get('documento')
        equipo = request.POST.get('equipo')
        fecha_prestamo = request.POST.get('fecha_prestamo')
        fecha_devolucion = request.POST.get('fecha_devolucion')
        observaciones = request.POST.get('observaciones')
        
        try:
            usuario = Usuario.objects.get(num_doc=documento)
            PrestarEquipos.objects.create(
                id_usuario_FK=usuario,
                nombre_equipo=equipo,
                fecha_prestamo=fecha_prestamo,
                fecha_devolucion=fecha_devolucion if fecha_devolucion else None,
                observaciones=observaciones,
            )
            messages.success(request, "Reporte guardado correctamente ✅")
            return redirect('pendientes-almacen')  # Evita reenvío del formulario
        except Usuario.DoesNotExist:
            messages.error(request, "El documento ingresado no pertenece a ningún aprendiz registrado ❌")

    # # Mostrar todos los reportes
    # reportes = PrestarEquipos.objects.select_related('id_usuario_FK').all().order_by('id')

    return render(request, 'almacen/prestarequipos.html')

def pendientesalmacen(request):
    # Obtener todos los equipos
    equipos = PrestarEquipos.objects.select_related("id_usuario_FK").all().order_by('-fecha_prestamo')
    hoy = date.today()

    # Actualizar automáticamente los estados según las fechas
    for equipo in equipos:
        if equipo.fecha_devolucion:  # verificar que tenga una fecha de devolución
            if equipo.fecha_devolucion < hoy:
                nuevo_estado = "Vencido"
            elif equipo.fecha_devolucion == hoy:
                nuevo_estado = "Vence hoy"
            else:
                nuevo_estado = "Activo"

            # Solo guardar si cambió el estado
            if equipo.estado != nuevo_estado:
                equipo.estado = nuevo_estado
                equipo.save()

    # Si el usuario elimina un equipo
    if request.method == "POST":
        equipo_id = request.POST.get("equipo_id")
        if "eliminar" in request.POST:
            equipo = PrestarEquipos.objects.get(id=equipo_id)
            equipo.delete()
            messages.success(request, f"Equipo '{equipo.nombre_equipo}' eliminado correctamente.")
            return redirect('pendientes-almacen')

    return render(request, 'almacen/pendientes.html', {"equipos": equipos})



def prestarlibro(request):
    if request.method == 'POST':
        # 🔹 Si viene un archivo Excel
        if 'subir_excel' in request.POST:
            archivo = request.FILES.get('archivo_excel')
            if not archivo:
                messages.error(request, "Debes seleccionar un archivo Excel.")
                return redirect('prestar-libro')

            try:
                df = pd.read_excel(archivo)

                # Se espera que el Excel tenga: documento, titulo_libro, fecha_prestamo, fecha_devolucion (opcional)
                for _, fila in df.iterrows():
                    documento = str(fila.get('documento')).strip() if fila.get('documento') else None
                    titulo_libro = fila.get('titulo_libro')
                    fecha_prestamo = fila.get('fecha_prestamo')
                    fecha_devolucion = fila.get('fecha_devolucion')

                    # Omitir filas vacías o incompletas
                    if not documento or not titulo_libro or pd.isna(fecha_prestamo):
                        continue

                    # ✅ Asegurar que las fechas sean del tipo date (no Timestamp)
                    if pd.notna(fecha_prestamo) and hasattr(fecha_prestamo, 'date'):
                        fecha_prestamo = fecha_prestamo.date()
                    if pd.notna(fecha_devolucion) and hasattr(fecha_devolucion, 'date'):
                        fecha_devolucion = fecha_devolucion.date()

                    try:
                        usuario = Usuario.objects.get(num_doc=documento)

                        # ✅ Determinar estado automáticamente según fechas
                        hoy = date.today()
                        if fecha_devolucion:
                            if fecha_devolucion < hoy:
                                estado = "Vencido"
                            elif fecha_devolucion == hoy:
                                estado = "Vence hoy"
                            else:
                                estado = "Activo"
                        else:
                            estado = "Activo"

                        PrestamoLibro.objects.create(
                            id_usuario_FK=usuario,
                            titulo_libro=titulo_libro,
                            fecha_prestamo=fecha_prestamo,
                            fecha_devolucion=fecha_devolucion,
                            estado=estado
                        )

                    except Usuario.DoesNotExist:
                        messages.warning(request, f"No se encontró usuario con documento {documento}")

                messages.success(request, "Archivo procesado correctamente.")
            except Exception as e:
                messages.error(request, f"Error al procesar el archivo: {e}")

            return redirect('prestar-libro')

        # 🔹 Si se registra manualmente
        else:
            documento = request.POST.get('aprendiz')
            titulo_libro = request.POST.get('libro')
            fecha_prestamo = request.POST.get('fecha_prestamo')

            if not (documento and titulo_libro and fecha_prestamo):
                messages.error(request, "Todos los campos son obligatorios.")
                return redirect('prestar-libro')

            try:
                usuario = Usuario.objects.get(num_doc=documento)
                PrestamoLibro.objects.create(
                    id_usuario_FK=usuario,
                    titulo_libro=titulo_libro,
                    fecha_prestamo=fecha_prestamo,
                    estado='Activo'
                )
                messages.success(request, f"Se registró el préstamo del libro '{titulo_libro}' al aprendiz {usuario.nombre}.")
            except Usuario.DoesNotExist:
                messages.error(request, "No existe un aprendiz con ese documento.")

            return redirect('prestar-libro')

    return render(request, 'biblioteca/prestarlibro.html')


def reportes_biblioteca(request):
    busqueda = request.GET.get("busqueda", "")

    prestamos = PrestamoLibro.objects.all()

    if busqueda:
        prestamos = prestamos.filter(
            Q(id_usuario_FK__num_doc__icontains=busqueda) |
            Q(titulo_libro__icontains=busqueda)
        )

    return render(request, "biblioteca/pendientes-biblioteca.html", {
        "prestamos": prestamos
    })

def eliminar_libro(request, id):
    prestamo = get_object_or_404(PrestamoLibro, id=id)
    prestamo.delete()
    return redirect('pendientes-biblioteca')



def fichas(request):
    # 🔍 Captura el término de búsqueda
    busqueda = request.GET.get('busqueda', '')
    centros = Centro.objects.all()

    # 📌 Query base
    fichas_qs = Ficha.objects.all().select_related('programa_FK')

    # 🔍 Filtro por número de ficha o programa
    if busqueda:
        fichas_qs = fichas_qs.filter(
            Q(num_ficha__icontains=busqueda) |
            Q(programa_FK__nombre_programa__icontains=busqueda)
        )

    fichas_qs = fichas_qs.order_by('-fecha_inicio')

    # 📑 Paginación
    paginator = Paginator(fichas_qs, 8)
    page_number = request.GET.get('page')
    fichas_page = paginator.get_page(page_number)

    programas = Programa.objects.all()

    return render(request, 'coordinador/fichas.html', {
        'fichas': fichas_page,
        'programas': programas,
        "centros": centros,
        'busqueda': busqueda
    })

def crear_ficha(request):
    if request.method == 'POST':
        try:
            num_ficha = request.POST.get('num_ficha', '').strip()
            programa_id = request.POST.get('programa')
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')
            
            # Validar que el número de ficha no esté vacío
            if not num_ficha:
                messages.error(request, "El número de ficha es obligatorio")
                return redirect('fichas')
            
            # Validar que la ficha no exista ya
            if Ficha.objects.filter(num_ficha=num_ficha).exists():
                messages.error(request, f"La ficha {num_ficha} ya existe")
                return redirect('fichas')
            
            programa = Programa.objects.get(id_programa=programa_id)
            
            # Crear ficha con número manual
            Ficha.objects.create(
                num_ficha=num_ficha,
                programa_FK=programa,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            
            messages.success(request, f"Ficha {num_ficha} creada con éxito")
            return redirect('fichas')
            
        except Programa.DoesNotExist:
            messages.error(request, "El programa seleccionado no es válido")
        except Exception as e:
            messages.error(request, f"Error al crear la ficha: {str(e)}")

    return redirect('fichas')

def editar_ficha(request):
    if request.method == "POST":
        ficha_id = request.POST.get("ficha_id")
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_fin = request.POST.get("fecha_fin")
        programa_id = request.POST.get("programa")

        try:
            ficha = Ficha.objects.get(num_ficha=ficha_id)
            programa = Programa.objects.get(id_programa=programa_id)

            ficha.fecha_inicio = fecha_inicio
            ficha.fecha_fin = fecha_fin
            ficha.programa_FK = programa
            ficha.save()

            messages.success(request, "Ficha editada con éxito")
            
        except Ficha.DoesNotExist:
            messages.error(request, "La ficha no existe")
        except Programa.DoesNotExist:
            messages.error(request, "El programa seleccionado no es válido")
        except Exception as e:
            messages.error(request, f"Error al editar la ficha: {str(e)}")

    return redirect('fichas')
def crear_programa(request):
    if request.method == "POST":

        nombre_programa = request.POST.get("nombre_programa")
        tipo_programa = request.POST.get("tipo_programa")
        centro_id = request.POST.get("centro")

        try:
            Programa.objects.create(
                nombre_programa=nombre_programa,
                tipo_programa=tipo_programa,   # si tu modelo NO tiene este campo, BORRAR ESTA LÍNEA
                id_centro_FK_id=centro_id
            )
            messages.success(request, "Programa creado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al crear el programa: {e}")

        return redirect("fichas")

    messages.error(request, "Solicitud inválida.")
    return redirect("fichas")


def eliminar_ficha(request):
    if request.method == "POST":
        ficha_id = request.POST.get("ficha_id", "").strip()
        
        if not ficha_id or not ficha_id.isdigit():
            messages.error(request, "ID de ficha inválido")
            return redirect('fichas')
        
        try:
            ficha = Ficha.objects.get(num_ficha=int(ficha_id))
            ficha.delete()
            messages.success(request, f"Ficha {ficha_id} eliminada con éxito")
        except Ficha.DoesNotExist:
            messages.error(request, f"La ficha {ficha_id} no existe")
    
    return redirect('fichas')

