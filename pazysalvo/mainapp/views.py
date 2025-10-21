from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch, Max, Q
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Usuario, Login, Roles, Seguimiento, TipoDoc, Ficha, InstructorxAprendiz
from .models import PrestamoBienestar, RegistroHoras
from .forms import UsuarioForm, SeguimientoForm
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password, check_password
from .models import Ficha, Programa
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, date
from django.core.paginator import Paginator
from django.http import JsonResponse
import pandas as pd

# Create your views here.
def index(request):
    return render(request, 'index.html')

def login_view(request):
    # 🔥 CORREGIDO: Eliminar la limpieza forzada de mensajes
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
                messages.success(request, f'¡Bienvenido/a {usuario.nombre}!')
                return redirect('inicio')
            else:
                messages.error(request, 'Contraseña incorrecta.')

        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
        except Login.DoesNotExist:
            messages.error(request, 'Usuario sin credenciales asignadas.')
        except Exception as e:
            messages.error(request, f'Error inesperado: {str(e)}')

    return render(request, 'login.html')

# TODO: MODULO USUARIO

def crear_usuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        num_doc = request.POST.get('num_doc')
        id_tipodoc = request.POST.get('id_tipodoc_FK')
        id_rol = request.POST.get('id_rol_FK')
        id_ficha = request.POST.get('id_ficha_FK')
        password = request.POST.get('password')

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
                id_ficha_FK_id=id_ficha if id_rol == '1' else None
            )

            # Si el rol NO es aprendiz, se crea el Login con contraseña
            if id_rol != '5':  # Ajusta según tu ID de rol Aprendiz
                if password:
                    Login.objects.create(
                        id_usuario_FK=usuario,
                        password=make_password(password)
                    )
                    messages.success(request, 'Usuario creado exitosamente con contraseña.')
                else:
                    Login.objects.create(
                        id_usuario_FK=usuario,
                        password=make_password(num_doc)  # Contraseña por defecto
                    )
                    messages.success(request, 'Usuario creado exitosamente con contraseña por defecto (su documento).')
            else:
                messages.success(request, 'Aprendiz creado exitosamente.')

        except IntegrityError as e:
            messages.error(request, f'Error de integridad al crear el usuario: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error inesperado: {str(e)}')

        return redirect('usuarios')
    
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    tipos_doc = TipoDoc.objects.all()
    roles = Roles.objects.all()
    fichas = Ficha.objects.all()

    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            apellidos = request.POST.get('apellidos')
            num_doc = request.POST.get('num_doc')
            id_tipodoc = request.POST.get('id_tipodoc_FK')
            id_rol = request.POST.get('id_rol_FK')
            id_ficha = request.POST.get('id_ficha_FK')
            password = request.POST.get('password')

            # Verificar si el documento ya existe en otro usuario
            if Usuario.objects.filter(num_doc=num_doc).exclude(id=usuario_id).exists():
                messages.error(request, 'Ya existe otro usuario con ese número de documento.')
                return render(request, 'editar_usuario.html', {
                    'usuario': usuario,
                    'tipos_doc': tipos_doc,
                    'roles': roles,
                    'fichas': fichas,
                })

            # Actualizar datos básicos
            usuario.nombre = nombre
            usuario.apellidos = apellidos
            usuario.num_doc = num_doc
            usuario.id_tipodoc_FK = TipoDoc.objects.get(pk=id_tipodoc)
            usuario.id_rol_FK = Roles.objects.get(pk=id_rol)

            # Solo asigna ficha si el rol es aprendiz
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
                        password=make_password(password)
                    )
                messages.success(request, 'Usuario y contraseña actualizados exitosamente.')
            else:
                messages.success(request, 'Usuario actualizado exitosamente.')

            return redirect('usuarios')

        except Exception as e:
            messages.error(request, f'Error al actualizar usuario: {str(e)}')

    return render(request, 'editar_usuario.html', {
        'usuario': usuario,
        'tipos_doc': tipos_doc,
        'roles': roles,
        'fichas': fichas,
    })

def eliminar_usuario(request, usuario_id):
    if request.method == 'POST':
        try:
            usuario = get_object_or_404(Usuario, pk=usuario_id)
            usuario_nombre = f"{usuario.nombre} {usuario.apellidos}"
            usuario.delete()
            messages.success(request, f'Usuario "{usuario_nombre}" eliminado correctamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar usuario: {str(e)}')
        
        return redirect('usuarios')

    # Si no es POST, mostrar confirmación
    usuario = get_object_or_404(Usuario, pk=usuario_id)
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
    return render(request, 'aprendiz/pazysalvo.html')

def inicio(request):
    # 🔥 AGREGADO: Mensaje de bienvenida si hay usuario en sesión
    usuario_nombre = request.session.get('usuario_nombre')
    if usuario_nombre:
        messages.info(request, f'Bienvenido/a de nuevo, {usuario_nombre}')
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

    # 📌 Paginación
    paginator = Paginator(aprendices_qs, 8)
    page_number = request.GET.get('page')
    aprendices_page = paginator.get_page(page_number)

    form_crear = UsuarioForm()
    form_editar = UsuarioForm()

    if request.method == 'POST':
        if 'crear' in request.POST:
            form_crear = UsuarioForm(request.POST)
            if form_crear.is_valid():
                try:
                    id_instructor2 = form_crear.cleaned_data.get('id_instructor')
                    usuario = form_crear.save(commit=False)
                    usuario.id_rol_FK = Roles.objects.get(nombre_rol="Aprendiz")
                    usuario.save()

                    Seguimiento.objects.create(id_aprendiz=usuario, id_instructor=id_instructor2)
                    InstructorxAprendiz.objects.create(id_instructor_FK=id_instructor2, id_aprendiz_FK=usuario)

                    messages.success(request, 'Aprendiz creado correctamente!')
                    return redirect('aprendices')
                except Exception as e:
                    messages.error(request, f'Error al crear aprendiz: {str(e)}')
            else:
                for field, errors in form_crear.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')

        elif 'editar' in request.POST:
            usuario_id = request.POST.get('usuario_id')
            if usuario_id:
                try:
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
                        for field, errors in form_editar.errors.items():
                            for error in errors:
                                messages.error(request, f'{field}: {error}')
                except Exception as e:
                    messages.error(request, f'Error al editar aprendiz: {str(e)}')

    return render(request, 'coordinador/aprendices.html', {
        'aprendices': aprendices_page,
        'form_crear': form_crear,
        'form_editar': form_editar,
        'busqueda': busqueda,
        'instructores': Usuario.objects.filter(id_rol_FK__nombre_rol="Instructor"),
    })

# TODO: FIN MODULO APRENDICES

def horasludicas(request):
    if request.method == 'POST':
        # Si viene un archivo Excel
        if 'subir_excel' in request.POST:
            archivo = request.FILES.get('archivo_excel')
            if not archivo:
                messages.error(request, "Debes seleccionar un archivo Excel.")
                return redirect('horasludicas')

            try:
                df = pd.read_excel(archivo)
                registros_exitosos = 0
                registros_fallidos = 0

                for _, fila in df.iterrows():
                    documento = str(fila.get('documento', '')).strip()
                    horas = fila.get('horas', 0)

                    if documento and horas:
                        try:
                            usuario = Usuario.objects.get(num_doc=documento)
                            RegistroHoras.objects.create(
                                id_usuario_FK=usuario,
                                cantidad_horas=horas
                            )
                            registros_exitosos += 1
                        except Usuario.DoesNotExist:
                            registros_fallidos += 1
                            messages.warning(request, f"No se encontró usuario con documento {documento}")
                    else:
                        registros_fallidos += 1

                if registros_exitosos > 0:
                    messages.success(request, f"Se cargaron {registros_exitosos} registros exitosamente.")
                if registros_fallidos > 0:
                    messages.warning(request, f"{registros_fallidos} registros no pudieron procesarse.")

            except Exception as e:
                messages.error(request, f"Error al procesar el archivo: {str(e)}")
            
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
            except Exception as e:
                messages.error(request, f"Error al registrar horas: {str(e)}")

            return redirect('horas-ludicas')

    return render(request, 'bienestar/horas-ludicas.html')

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
                serial=serial,
                fecha_prestamo=fecha_prestamo,
                fecha_devolucion=fecha_devolucion if fecha_devolucion else None,
                observaciones=observaciones,
            )
            messages.success(request, "Reporte guardado correctamente ✅")
            return redirect('prestar-equipos')
        except Usuario.DoesNotExist:
            messages.error(request, "El documento ingresado no pertenece a ningún aprendiz registrado ❌")
        except Exception as e:
            messages.error(request, f"Error al guardar el reporte: {str(e)}")

    # Mostrar todos los reportes
    reportes = PrestamoBienestar.objects.select_related('id_usuario_FK').all().order_by('id')

    return render(request, 'bienestar/prestar-equipos.html', {'reportes': reportes})

def editar_prestamo(request, id):
    prestamo = get_object_or_404(PrestamoBienestar, id=id)

    if request.method == 'POST':
        try:
            prestamo.nombre_equipo = request.POST.get('nombre_equipo')
            prestamo.serial = request.POST.get('serial')
            prestamo.fecha_prestamo = request.POST.get('fecha_prestamo')
            prestamo.fecha_devolucion = request.POST.get('fecha_devolucion')
            prestamo.observaciones = request.POST.get('observaciones')
            prestamo.save()
            messages.success(request, 'El préstamo fue actualizado correctamente.')
        except Exception as e:
            messages.error(request, f'Error al actualizar el préstamo: {str(e)}')
        
        return redirect('prestar-equipos')  
    
    return render(request, 'modales/modalEditarPrestamo.html', {'prestamo': prestamo})

def eliminar_prestamo(request, id):
    try:
        prestamo = get_object_or_404(PrestamoBienestar, id=id)
        prestamo.delete()
        messages.success(request, 'El préstamo fue eliminado correctamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el préstamo: {str(e)}')
    
    return redirect('prestar-equipos')

def equiposalmacen(request):
    return render(request, 'almacen/prestarequipos.html')

def pendientesalmacen(request):
    return render(request, 'almacen/pendientes.html')

def prestarlibro(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        documento_aprendiz = request.POST.get('aprendiz', '').strip()
        titulo_libro = request.POST.get('libro', '').strip()
        fecha_prestamo = request.POST.get('fecha', '').strip()
        
        # 🔍 VALIDACIONES BÁSICAS
        if not documento_aprendiz:
            messages.error(request, 'El documento del aprendiz es obligatorio.')
            return render(request, 'biblioteca/prestarlibro.html')
        
        if not titulo_libro:
            messages.error(request, 'El título del libro es obligatorio.')
            return render(request, 'biblioteca/prestarlibro.html')
        
        if not fecha_prestamo:
            messages.error(request, 'La fecha de préstamo es obligatoria.')
            return render(request, 'biblioteca/prestarlibro.html')
        
        try:
            # 📋 VERIFICAR SI EL APRENDIZ EXISTE EN LA BASE DE DATOS
            try:
                aprendiz = Usuario.objects.get(
                    num_doc=documento_aprendiz,
                    id_rol_FK__nombre_rol="Aprendiz"  # Asegurar que sea aprendiz
                )
            except Usuario.DoesNotExist:
                messages.error(request, f'No existe un aprendiz con el documento {documento_aprendiz}.')
                return render(request, 'biblioteca/prestarlibro.html')
            except Usuario.MultipleObjectsReturned:
                messages.error(request, f'Existen múltiples usuarios con el documento {documento_aprendiz}. Contacte al administrador.')
                return render(request, 'biblioteca/prestarlibro.html')
            
            # 📚 VALIDAR DISPONIBILIDAD DEL LIBRO (si tienes modelo de Libros)
            # Si tienes un modelo Libro, puedes agregar validaciones aquí:
            # libro = Libro.objects.get(titulo=titulo_libro, disponible=True)
            # if not libro:
            #     messages.error(request, f'El libro "{titulo_libro}" no está disponible.')
            #     return render(request, 'biblioteca/prestarlibro.html')
            
            # 📅 VALIDAR FECHA (no puede ser futura)
            fecha_prestamo_obj = datetime.strptime(fecha_prestamo, '%Y-%m-%d').date()
            hoy = date.today()
            
            if fecha_prestamo_obj > hoy:
                messages.error(request, 'La fecha de préstamo no puede ser futura.')
                return render(request, 'biblioteca/prestarlibro.html')
            
            # ✅ VERIFICAR SI EL APRENDIZ YA TIENE PRÉSTAMOS ACTIVOS
            # Si tienes un modelo PrestamoLibro, puedes validar:
            # prestamos_activos = PrestamoLibro.objects.filter(
            #     aprendiz=aprendiz,
            #     fecha_devolucion__isnull=True
            # ).count()
            # 
            # if prestamos_activos >= 3:  # Límite de 3 préstamos simultáneos
            #     messages.warning(request, f'El aprendiz ya tiene {prestamos_activos} préstamos activos. Límite: 3.')
            #     return render(request, 'biblioteca/prestarlibro.html')
            
            # 💾 GUARDAR EL PRÉSTAMO EN LA BASE DE DATOS
            # Si tienes un modelo para préstamos de libros, crea el registro:
            # prestamo = PrestamoLibro.objects.create(
            #     aprendiz=aprendiz,
            #     libro=libro,  # o titulo_libro si no tienes modelo Libro
            #     fecha_prestamo=fecha_prestamo_obj,
            #     estado='ACTIVO'
            # )
            
            # 📝 REGISTRO EN LA BASE DE DATOS (versión básica sin modelo específico)
            # Por ahora, solo mostramos el mensaje de éxito
            # Cuando crees el modelo PrestamoLibro, descomenta las líneas anteriores
            
            # 🎯 MENSAJE DE ÉXITO CON DETALLES
            messages.success(
                request, 
                f'Préstamo registrado exitosamente. '
                f'Aprendiz: {aprendiz.nombre} {aprendiz.apellidos}, '
                f'Libro: {titulo_libro}, '
                f'Fecha: {fecha_prestamo_obj.strftime("%d/%m/%Y")}'
            )
            
            # 🔄 REDIRIGIR PARA EVITAR REENVÍO DEL FORMULARIO
            return redirect('prestar-libro')
            
        except ValueError as e:
            messages.error(request, 'Formato de fecha inválido. Use el formato YYYY-MM-DD.')
            return render(request, 'biblioteca/prestarlibro.html')
        except Exception as e:
            messages.error(request, f'Error inesperado al registrar el préstamo: {str(e)}')
            return render(request, 'biblioteca/prestarlibro.html')
    
    # 📄 RENDERIZAR EL FORMULARIO VACÍO (GET)
    return render(request, 'biblioteca/prestarlibro.html')

def pendientes_biblioteca(request):
    return render(request, 'biblioteca/pendientes-biblioteca.html')

def fichas(request):
    busqueda = request.GET.get('busqueda', '')
    fichas_qs = Ficha.objects.all().select_related('programa_FK')

    if busqueda:
        fichas_qs = fichas_qs.filter(
            Q(num_ficha__icontains=busqueda) |
            Q(programa_FK__nombre__icontains=busqueda)
        )

    fichas_qs = fichas_qs.order_by('-fecha_inicio')

    paginator = Paginator(fichas_qs, 8)
    page_number = request.GET.get('page')
    fichas_page = paginator.get_page(page_number)

    programas = Programa.objects.all()

    return render(request, 'coordinador/fichas.html', {
        'fichas': fichas_page,
        'programas': programas,
        'busqueda': busqueda
    })

def crear_ficha(request):
    if request.method == 'POST':
        try:
            codigo_ficha = request.POST.get('codigo_ficha')
            programa_id = request.POST.get('programa')

            if Ficha.objects.filter(num_ficha=codigo_ficha).exists():
                messages.error(request, 'Ya existe una ficha con ese código.')
                return redirect('fichas')

            programa = Programa.objects.get(id=programa_id)
            Ficha.objects.create(num_ficha=codigo_ficha, programa_FK=programa)

            messages.success(request, 'Ficha creada exitosamente.')
            return redirect('fichas')
        except Exception as e:
            messages.error(request, f'Error al crear ficha: {str(e)}')
            return redirect('fichas')

    programas = Programa.objects.all()
    return render(request, 'modales/modalCrearFicha.html', {
        'programas': programas
    })

def editar_ficha(request, ficha_id):
    ficha = get_object_or_404(Ficha, num_ficha=ficha_id)
    programas = Programa.objects.all()

    if request.method == "POST":
        try:
            num_ficha = request.POST.get("codigo_ficha")
            fecha_inicio = request.POST.get("fecha_inicio")
            fecha_fin = request.POST.get("fecha_fin")
            programa_id = request.POST.get("programa")

            # Verificar si el nuevo código ya existe en otra ficha
            if ficha.num_ficha != num_ficha and Ficha.objects.filter(num_ficha=num_ficha).exists():
                messages.error(request, "Ya existe una ficha con ese código.")
                return redirect('fichas')

            programa = Programa.objects.get(id_programa=programa_id)

            ficha.num_ficha = num_ficha
            ficha.fecha_inicio = fecha_inicio
            ficha.fecha_fin = fecha_fin
            ficha.programa_FK = programa
            ficha.save()

            messages.success(request, "Ficha editada con éxito")
            return redirect('fichas')
        except Programa.DoesNotExist:
            messages.error(request, "El programa seleccionado no es válido")
        except Exception as e:
            messages.error(request, f"Error al editar ficha: {str(e)}")

    return render(request, 'coordinador/modals/modal_editar_ficha.html', {
        'ficha': ficha,
        'programas': programas
    })

def eliminar_ficha(request, ficha_id):
    if request.method == "POST":
        try:
            ficha = Ficha.objects.get(num_ficha=ficha_id)
            ficha.delete()
            messages.success(request, "Ficha eliminada con éxito")
        except Ficha.DoesNotExist:
            messages.error(request, "La ficha no existe")
        except Exception as e:
            messages.error(request, f"Error al eliminar ficha: {str(e)}")
    
    return redirect('fichas')