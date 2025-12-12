from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch, Max
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Centro, Usuario, Login, Roles, Seguimiento, TipoDoc, Ficha, InstructorxAprendiz, PrestarEquipos, PrestamoLibro
from .models import PrestamoBienestar, RegistroHoras, Programa, AgEmpleo  # ✅ Importar AgEmpleo
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
from django.http import JsonResponse, HttpResponse, FileResponse
import pandas as pd
from django.contrib.auth.decorators import login_required
from datetime import date
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
import os
from django.conf import settings

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

        # ✅ Verificar si tiene datos actualizados
        if not usuario.datos_actualizados:
            return redirect("actualizar_datos_aprendiz")

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
    
    # Validación: ¿Tiene préstamos en almacén?
    tiene_prestamos_almacen = PrestarEquipos.objects.filter(id_usuario_FK=usuario).exists()
    
    # Obtener estados individuales
    cumple_horas = usuario.cumple_horas_bienestar()
    tiene_bitacoras = usuario.tiene_bitacoras_completas()
    cumple_academicos = usuario.cumple_requisitos_academicos()
    tiene_datos_actualizados = usuario.datos_actualizados
    
    # ✅ Verificar si cumple TODOS los requisitos
    cumple_todos_requisitos = (
        cumple_academicos and 
        tiene_bitacoras and 
        cumple_horas and 
        not tiene_prestamos and 
        not tiene_prestamos_almacen and 
        tiene_datos_actualizados
    )

    return render(request, "aprendiz/pazysalvo.html", {
        "usuario": usuario,
        "tiene_prestamos": tiene_prestamos,
        "tiene_prestamos_almacen": tiene_prestamos_almacen,
        "cumple_horas_bienestar": cumple_horas,
        "tiene_bitacoras_completas": tiene_bitacoras,
        "cumple_requisitos_academicos": cumple_academicos,
        "cumple_todos_requisitos": cumple_todos_requisitos,  # ✅ Nueva variable
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
    paginator = Paginator(aprendices_qs, 8)
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

                if id_instructor2:  # ✅ Solo crear si hay instructor
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
        'aprendices': aprendices_page,
        'form_crear': form_crear,
        'form_editar': form_editar,
        'busqueda': busqueda,
        'instructores': Usuario.objects.filter(id_rol_FK__nombre_rol="Instructor Seguimiento"),  # ✅ Cambio aquí
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
        form_type = request.POST.get('form_type')
        
        # Formulario Individual
        if form_type == 'individual':
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
                    serial=serial,
                    fecha_prestamo=fecha_prestamo,
                    fecha_devolucion=fecha_devolucion if fecha_devolucion else None,
                    observaciones=observaciones,
                )
                messages.success(request, "Reporte guardado correctamente ✅")
                return redirect('prestar-equipos')
            except Usuario.DoesNotExist:
                messages.error(request, "El documento ingresado no pertenece a ningún aprendiz registrado ❌")
        
        # Formulario Masivo (Excel)
        elif form_type == 'masiva':
            excel_file = request.FILES.get('excel_file')
            
            if excel_file:
                try:
                    # Leer el archivo Excel
                    df = pd.read_excel(excel_file)
                    
                    # Validar columnas requeridas
                    required_columns = ['documento', 'equipo', 'serial', 'fecha_prestamo']
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    
                    if missing_columns:
                        messages.error(request, f"Faltan columnas requeridas: {', '.join(missing_columns)}")
                    else:
                        success_count = 0
                        error_count = 0
                        errors = []
                        seriales_existentes = set(PrestamoBienestar.objects.values_list('serial', flat=True))
                        seriales_procesados = set()
                        
                        for index, row in df.iterrows():
                            try:
                                documento = str(row['documento']).strip()
                                equipo = row['equipo']
                                serial = str(row['serial']).strip()
                                fecha_prestamo = row['fecha_prestamo']
                                
                                # Validar serial único en el archivo
                                if serial in seriales_procesados:
                                    error_count += 1
                                    errors.append(f"Fila {index + 2}: Serial {serial} duplicado en el archivo")
                                    continue
                                
                                # Validar serial único en la base de datos
                                if serial in seriales_existentes:
                                    error_count += 1
                                    errors.append(f"Fila {index + 2}: Serial {serial} ya existe en el sistema")
                                    continue
                                
                                # Convertir fecha si es string
                                if isinstance(fecha_prestamo, str):
                                    fecha_prestamo = datetime.strptime(fecha_prestamo, '%Y-%m-%d').date()
                                
                                # Fecha de devolución (opcional)
                                fecha_devolucion = row.get('fecha_devolucion')
                                if fecha_devolucion and isinstance(fecha_devolucion, str):
                                    fecha_devolucion = datetime.strptime(fecha_devolucion, '%Y-%m-%d').date()
                                elif pd.isna(fecha_devolucion):
                                    fecha_devolucion = None
                                
                                # Observaciones (opcional)
                                observaciones = row.get('observaciones', '')
                                if pd.isna(observaciones):
                                    observaciones = ''
                                
                                # Validar que el usuario exista
                                usuario = Usuario.objects.get(num_doc=documento)
                                
                                # Validar equipo válido
                                equipos_validos = ['Portátil', 'Tablet', 'Proyector']
                                if equipo not in equipos_validos:
                                    error_count += 1
                                    errors.append(f"Fila {index + 2}: Equipo '{equipo}' no válido. Válidos: {', '.join(equipos_validos)}")
                                    continue
                                
                                # Crear el registro
                                PrestamoBienestar.objects.create(
                                    id_usuario_FK=usuario,
                                    nombre_equipo=equipo,
                                    serial=serial,
                                    fecha_prestamo=fecha_prestamo,
                                    fecha_devolucion=fecha_devolucion,
                                    observaciones=observaciones,
                                )
                                success_count += 1
                                seriales_procesados.add(serial)
                                
                            except Usuario.DoesNotExist:
                                error_count += 1
                                errors.append(f"Fila {index + 2}: Documento {documento} no encontrado")
                            except Exception as e:
                                error_count += 1
                                errors.append(f"Fila {index + 2}: Error - {str(e)}")
                        
                        # Mostrar resultados
                        if success_count > 0:
                            messages.success(request, f"✅ Se procesaron {success_count} registros correctamente")
                        if error_count > 0:
                            messages.warning(request, f"⚠️ {error_count} registros tuvieron errores")
                            # Mostrar primeros 5 errores para no saturar
                            for error in errors[:5]:
                                messages.error(request, error)
                            if len(errors) > 5:
                                messages.info(request, f"... y {len(errors) - 5} errores más")
                
                except Exception as e:
                    messages.error(request, f"Error al procesar el archivo: {str(e)}")
            
            else:
                messages.error(request, "No se seleccionó ningún archivo")

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
        form_type = request.POST.get('form_type')
        
        # Formulario Individual
        if form_type == 'individual':
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
                return redirect('pendientes-almacen')
            except Usuario.DoesNotExist:
                messages.error(request, "El documento ingresado no pertenece a ningún aprendiz registrado ❌")
        
        # Formulario Masivo (Excel)
        elif form_type == 'masiva':
            excel_file = request.FILES.get('excel_file')
            
            if excel_file:
                try:
                    # Leer el archivo Excel
                    df = pd.read_excel(excel_file)
                    
                    # Validar columnas requeridas
                    required_columns = ['documento', 'equipo', 'fecha_prestamo']
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    
                    if missing_columns:
                        messages.error(request, f"Faltan columnas requeridas: {', '.join(missing_columns)}")
                    else:
                        success_count = 0
                        error_count = 0
                        errors = []
                        
                        for index, row in df.iterrows():
                            try:
                                documento = str(row['documento']).strip()
                                equipo = row['equipo']
                                fecha_prestamo = row['fecha_prestamo']
                                
                                # Convertir fecha si es string
                                if isinstance(fecha_prestamo, str):
                                    fecha_prestamo = datetime.strptime(fecha_prestamo, '%Y-%m-%d').date()
                                
                                # Fecha de devolución (opcional)
                                fecha_devolucion = row.get('fecha_devolucion')
                                if fecha_devolucion and isinstance(fecha_devolucion, str):
                                    fecha_devolucion = datetime.strptime(fecha_devolucion, '%Y-%m-%d').date()
                                elif pd.isna(fecha_devolucion):
                                    fecha_devolucion = None
                                
                                # Observaciones (opcional)
                                observaciones = row.get('observaciones', '')
                                if pd.isna(observaciones):
                                    observaciones = ''
                                
                                # Validar que el usuario exista
                                usuario = Usuario.objects.get(num_doc=documento)
                                
                                # Crear el registro
                                PrestarEquipos.objects.create(
                                    id_usuario_FK=usuario,
                                    nombre_equipo=equipo,
                                    fecha_prestamo=fecha_prestamo,
                                    fecha_devolucion=fecha_devolucion,
                                    observaciones=observaciones,
                                )
                                success_count += 1
                                
                            except Usuario.DoesNotExist:
                                error_count += 1
                                errors.append(f"Fila {index + 2}: Documento {documento} no encontrado")
                            except Exception as e:
                                error_count += 1
                                errors.append(f"Fila {index + 2}: Error - {str(e)}")
                        
                        # Mostrar resultados
                        if success_count > 0:
                            messages.success(request, f"✅ Se procesaron {success_count} registros correctamente")
                        if error_count > 0:
                            messages.warning(request, f"⚠️ {error_count} registros tuvieron errores")
                            # Mostrar primeros 5 errores para no saturar
                            for error in errors[:5]:
                                messages.error(request, error)
                            if len(errors) > 5:
                                messages.info(request, f"... y {len(errors) - 5} errores más")
                
                except Exception as e:
                    messages.error(request, f"Error al procesar el archivo: {str(e)}")
            
            else:
                messages.error(request, "No se seleccionó ningún archivo")
    
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

def actualizar_datos_aprendiz(request):
    """
    Vista que muestra el modal para actualizar datos del aprendiz.
    Solicita información de AgEmpleo y tipo de documento.
    """
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("index")

    usuario = get_object_or_404(Usuario, id=usuario_id)

    # ✅ Permitir re-actualización: comentar esta verificación
    # if usuario.datos_actualizados:
    #     return redirect("pazysalvo")

    # Obtener o crear registro de AgEmpleo
    ag_empleo, created = AgEmpleo.objects.get_or_create(id_aprendiz_FK=usuario)

    if request.method == "POST":
        # ✅ Actualizar tipo de documento
        tipo_doc_id = request.POST.get("id_tipodoc_FK")
        if tipo_doc_id:
            usuario.id_tipodoc_FK_id = tipo_doc_id

        # ✅ Actualizar datos de AgEmpleo
        ag_empleo.fecha_nacimiento = request.POST.get("fecha_nacimiento")
        ag_empleo.telefono = request.POST.get("telefono")
        ag_empleo.telefono_2 = request.POST.get("telefono_2")
        ag_empleo.correo = request.POST.get("correo")
        ag_empleo.nombre_empresa = request.POST.get("nombre_empresa")
        ag_empleo.fecha_inicio_empresa = request.POST.get("fecha_inicio_empresa")
        ag_empleo.fecha_fin_empresa = request.POST.get("fecha_fin_empresa")

        # ✅ Marcar como actualizado
        usuario.datos_actualizados = True
        
        usuario.save()
        ag_empleo.save()

        messages.success(request, "Datos actualizados correctamente ✅")
        return redirect("pazysalvo")

    # Datos para el template
    tipos_doc = TipoDoc.objects.all()

    return render(request, "aprendiz/actualizar_datos.html", {
        "usuario": usuario,
        "ag_empleo": ag_empleo,
        "tipos_doc": tipos_doc,
    })


def agencia_empleo(request):
    """
    Vista que muestra todos los registros de empleo de los aprendices.
    Permite búsqueda por documento, nombre o empresa.
    """
    busqueda = request.GET.get('busqueda', '')

    # Consultar todos los registros de AgEmpleo con su aprendiz relacionado
    registros_empleo = AgEmpleo.objects.select_related(
        'id_aprendiz_FK',
        'id_aprendiz_FK__id_tipodoc_FK',  # ✅ Agregar tipo de documento
        'id_aprendiz_FK__id_ficha_FK',
        'id_aprendiz_FK__id_ficha_FK__programa_FK'
    ).all()

    # Filtro de búsqueda
    if busqueda:
        registros_empleo = registros_empleo.filter(
            Q(id_aprendiz_FK__num_doc__icontains=busqueda) |
            Q(id_aprendiz_FK__nombre__icontains=busqueda) |
            Q(id_aprendiz_FK__apellidos__icontains=busqueda) |
            Q(nombre_empresa__icontains=busqueda) |
            Q(correo__icontains=busqueda) |
            Q(id_aprendiz_FK__id_ficha_FK__programa_FK__nombre_programa__icontains=busqueda) |
            Q(id_aprendiz_FK__id_ficha_FK__programa_FK__tipo_programa__icontains=busqueda)
        )

    # Ordenar por apellido del aprendiz
    registros_empleo = registros_empleo.order_by('id_aprendiz_FK__apellidos', 'id_aprendiz_FK__nombre')

    # Paginación
    paginator = Paginator(registros_empleo, 10)
    page_number = request.GET.get('page')
    registros_page = paginator.get_page(page_number)

    return render(request, 'empleo/empleo.html', {
        'registros': registros_page,
        'busqueda': busqueda,
    })


def descargar_reporte_empleo(request):
    """
    Vista que genera y descarga un archivo Excel con todos los datos de empleo.
    """
    # Obtener todos los registros sin paginación
    registros_empleo = AgEmpleo.objects.select_related(
        'id_aprendiz_FK',
        'id_aprendiz_FK__id_tipodoc_FK',
        'id_aprendiz_FK__id_ficha_FK',
        'id_aprendiz_FK__id_ficha_FK__programa_FK'
    ).order_by('id_aprendiz_FK__apellidos', 'id_aprendiz_FK__nombre')

    # Crear un nuevo libro de Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte Empleo"

    # Estilos
    header_fill = PatternFill(start_color="39A900", end_color="39A900", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
    border_style = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Encabezados
    headers = [
        'Tipo Doc', 'Documento', 'Aprendiz', 'Fecha Nacimiento', 
        'Programa', 'Correo', 'Teléfono 1', 'Teléfono 2', 
        'Empresa', 'Fecha Inicio', 'Fecha Fin'
    ]

    # Escribir encabezados
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
        cell.border = border_style

    # Escribir datos
    row_num = 2
    for registro in registros_empleo:
        # Tipo de documento
        tipo_doc = registro.id_aprendiz_FK.id_tipodoc_FK.nombre_tipo if registro.id_aprendiz_FK.id_tipodoc_FK else "-"
        ws.cell(row=row_num, column=1, value=tipo_doc).border = border_style

        # Documento
        ws.cell(row=row_num, column=2, value=str(registro.id_aprendiz_FK.num_doc)).border = border_style

        # Aprendiz (nombre completo)
        nombre_completo = f"{registro.id_aprendiz_FK.nombre} {registro.id_aprendiz_FK.apellidos}"
        ws.cell(row=row_num, column=3, value=nombre_completo).border = border_style

        # Fecha de nacimiento
        fecha_nac = registro.fecha_nacimiento.strftime('%Y-%m-%d') if registro.fecha_nacimiento else "-"
        ws.cell(row=row_num, column=4, value=fecha_nac).border = border_style

        # Programa
        if registro.id_aprendiz_FK.id_ficha_FK and registro.id_aprendiz_FK.id_ficha_FK.programa_FK:
            programa = registro.id_aprendiz_FK.id_ficha_FK.programa_FK.nombre_programa
        else:
            programa = "Sin programa"
        ws.cell(row=row_num, column=5, value=programa).border = border_style

        # Correo
        ws.cell(row=row_num, column=6, value=registro.correo or "-").border = border_style

        # Teléfono 1
        ws.cell(row=row_num, column=7, value=registro.telefono or "-").border = border_style

        # Teléfono 2
        ws.cell(row=row_num, column=8, value=registro.telefono_2 or "-").border = border_style

        # Empresa
        ws.cell(row=row_num, column=9, value=registro.nombre_empresa or "-").border = border_style

        # Fecha inicio empresa
        fecha_inicio = registro.fecha_inicio_empresa.strftime('%Y-%m-%d') if registro.fecha_inicio_empresa else "-"
        ws.cell(row=row_num, column=10, value=fecha_inicio).border = border_style

        # Fecha fin empresa
        fecha_fin = registro.fecha_fin_empresa.strftime('%Y-%m-%d') if registro.fecha_fin_empresa else "-"
        ws.cell(row=row_num, column=11, value=fecha_fin).border = border_style

        row_num += 1

    # Ajustar ancho de columnas
    column_widths = [12, 15, 30, 18, 40, 30, 15, 15, 35, 15, 15]
    for i, width in enumerate(column_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width

    # Crear la respuesta HTTP con el archivo Excel
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    # Nombre del archivo con fecha actual
    filename = f'Reporte_Empleo_{date.today().strftime("%Y%m%d")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Guardar el libro en la respuesta
    wb.save(response)

    return response


def descargar_paz_y_salvo(request):
    """
    Vista que descarga la plantilla de Paz y Salvo con los datos del usuario
    """
    usuario_id = request.session.get("usuario_id")
    
    if not usuario_id:
        return redirect("index")
    
    # Verificar que el usuario cumple con todos los requisitos
    usuario = Usuario.objects.get(id=usuario_id)
    tiene_prestamos = PrestamoLibro.objects.filter(id_usuario_FK=usuario).exists()
    tiene_prestamos_almacen = PrestarEquipos.objects.filter(id_usuario_FK=usuario).exists()
    
    cumple_todos_requisitos = (
        usuario.cumple_requisitos_academicos() and 
        usuario.tiene_bitacoras_completas() and 
        usuario.cumple_horas_bienestar() and 
        not tiene_prestamos and 
        not tiene_prestamos_almacen and 
        usuario.datos_actualizados
    )
    
    # Si no cumple todos los requisitos, redirigir con mensaje de error
    if not cumple_todos_requisitos:
        # messages.error(request, "No cumples con todos los requisitos para descargar el Paz y Salvo.")
        return redirect("pazysalvo")
    
    # Ruta del archivo de plantilla
    file_path = os.path.join(settings.BASE_DIR, 'mainapp', 'static', 'plantilla', 'paz_y_salvo.xlsx')
    
    # Verificar que el archivo existe
    if not os.path.exists(file_path):
        # messages.error(request, f"No se encontró la plantilla del Paz y Salvo en: {file_path}")
        return redirect("pazysalvo")
    
    try:
        # ✅ Cargar el workbook de la plantilla
        wb = load_workbook(file_path)
        ws = wb.active
        
        # ✅ Preparar los datos del usuario
        fecha_actual = date.today().strftime("%d/%m/%Y")
        nombre_completo = f"{usuario.nombre} {usuario.apellidos}"
        tipo_doc = usuario.id_tipodoc_FK.nombre_tipo if usuario.id_tipodoc_FK else "N/A"
        numero_doc = str(usuario.num_doc)
        
        # Datos de ficha y programa
        if usuario.id_ficha_FK and usuario.id_ficha_FK.programa_FK:
            programa_nombre = usuario.id_ficha_FK.programa_FK.nombre_programa
            nivel_programa = usuario.id_ficha_FK.programa_FK.get_tipo_programa_display()
            numero_ficha = str(usuario.id_ficha_FK.num_ficha)
        else:
            programa_nombre = "Sin programa asignado"
            nivel_programa = "N/A"
            numero_ficha = "Sin ficha"
        
        # ✅ Diccionario de reemplazos
        reemplazos = {
            '{{FECHA}}': fecha_actual,
            '{{NOMBRE}}': nombre_completo,
            '{{TIPODOC}}': tipo_doc,
            '{{NUMERODOC}}': numero_doc,
            '{{PROGRAMAFORMACION}}': programa_nombre,
            '{{NIVEL}}': nivel_programa,
            '{{NUMEROFICHA}}': numero_ficha,
        }
        
        # ✅ Recorrer todas las celdas y reemplazar etiquetas
        for row in ws.iter_rows():
            for cell in row:
                if cell.value and isinstance(cell.value, str):
                    for etiqueta, valor in reemplazos.items():
                        if etiqueta in cell.value:
                            cell.value = cell.value.replace(etiqueta, valor)
                            
                            # Aplicar estilo SOLO al texto reemplazado
                            cell.font = Font(
                                name="Calibri",   # Puedes cambiar la fuente
                                size=12,          # Tamaño más grande
                                bold=False         # Opcional (negrita)
                            )
        
        # ✅ Guardar el archivo modificado en memoria
        from io import BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        # ✅ Crear respuesta HTTP con el archivo
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # Nombre del archivo descargado
        nombre_archivo = f'Paz_y_Salvo_{usuario.nombre}_{usuario.apellidos}_{date.today().strftime("%Y%m%d")}.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        
        return response
    
    except Exception as e:
        messages.error(request, f"Error al procesar el archivo: {str(e)}")
        return redirect("pazysalvo")

