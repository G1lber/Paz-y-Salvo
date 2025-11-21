from django.db import models
from django.contrib.auth.hashers import make_password
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Create your models here.

class Centro(models.Model):
    nombre_centro = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre_centro


class Roles(models.Model):
    nombre_rol = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.nombre_rol


class TipoDoc(models.Model):
    nombre_tipo = models.CharField(max_length=10)

    def __str__(self):
        return self.nombre_tipo


class Programa(models.Model):
    TIPO_PROGRAMA = [
        ('tecnico', 'Técnico'),
        ('tecnologo', 'Tecnólogo'),
    ]
    id_programa = models.AutoField(primary_key=True)
    nombre_programa = models.CharField(max_length=150)
    tipo_programa = models.CharField(max_length=10, choices=TIPO_PROGRAMA, default='tecnico')
    id_centro_FK = models.ForeignKey(Centro, on_delete=models.CASCADE, null=True)
    

    def __str__(self):
        return self.nombre_programa
    
    def horas_requeridas(self):
        return 60 if self.tipo_programa == 'tecnologo' else 30


class Ficha(models.Model):
    num_ficha = models.CharField(
        max_length=50, 
        primary_key=True,
        verbose_name="Número de Ficha"
    )
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    programa_FK = models.ForeignKey(Programa, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.num_ficha)


class Usuario(models.Model):
    nombre = models.CharField(max_length=200, null=True)
    apellidos = models.CharField(max_length=100, null=True)
    num_doc = models.IntegerField(unique=True)
    id_tipodoc_FK = models.ForeignKey(TipoDoc, on_delete=models.SET_NULL, null=True)
    id_rol_FK = models.ForeignKey(Roles, on_delete=models.SET_NULL, null=True)
    id_ficha_FK = models.ForeignKey(Ficha, on_delete=models.SET_NULL, null=True)
    es_patrocinado = models.BooleanField(default=False)

    # 🔥 Nuevos campos
    resultados = models.BooleanField(default=False)
    tyt = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.nombre} {self.apellidos}'


class Login(models.Model):
    id_usuario_FK = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    password = models.CharField(max_length=100, null=True)

    def save(self, *args, **kwargs):
        # ✅ Solo encriptar si hay contraseña y no está ya encriptada
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Login de {self.id_usuario_FK}'


class PazYSalvo(models.Model):
    lugar_diligen = models.CharField(max_length=200)
    fecha_diligen = models.DateField()
    id_centro_FK = models.ForeignKey(Centro, on_delete=models.CASCADE, null=True)
    regional = models.CharField(max_length=100, null=True)
    tramite = models.CharField(max_length=200, null=True)
    id_usuario_FK = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True)
    firma_responsable = models.CharField(max_length=200, null=True)
    observaciones = models.CharField(max_length=200, null=True)
    firma_certificacion = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f'Paz y Salvo {self.id} - {self.tramite}'

class ControlPazYSalvo(models.Model):
    id_control = models.AutoField(primary_key=True)
    id_usuario_FK = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True)
    id_ficha_FK = models.ForeignKey(Ficha, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'Creado para {self.id_usuario_FK} de la ficha {self.id_ficha_FK}'

class ReporteCoordinacion(models.Model):
    id_usuario_FK = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_ficha_FK = models.ForeignKey(Ficha, on_delete=models.CASCADE)
    paz_y_salvo = models.BooleanField(default=False)
    observaciones = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Coordinación - {self.id_usuario_FK}'

class PrestarEquipos(models.Model):
    id_usuario_FK = models.ForeignKey('Usuario', on_delete=models.CASCADE, null=True)
    nombre_equipo = models.CharField(max_length=100)
    fecha_prestamo = models.DateField()
    fecha_devolucion = models.DateField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('Pendiente', 'Pendiente'),
            ('Activo', 'Activo'),
            ('Vencido', 'Vencido')
        ],
        default='Pendiente'
    )

    def __str__(self):
        return f'{self.nombre_equipo} - {self.id_usuario_FK}'

class RegistroHoras(models.Model):
    id_usuario_FK = models.ForeignKey('Usuario', on_delete=models.CASCADE, null=True)
    cantidad_horas = models.PositiveIntegerField()
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.id_usuario_FK} - {self.cantidad_horas} horas'

class PrestamoLibro(models.Model):
    id_usuario_FK = models.ForeignKey('Usuario', on_delete=models.CASCADE, null=True)
    titulo_libro = models.CharField(max_length=200)
    fecha_prestamo = models.DateField()
    estado = models.CharField(
        max_length=20,
        choices=[
            ('Pendiente', 'Pendiente'),
            ('Activo', 'Activo'),
            ('Vencido', 'Vencido')
        ],
        default='Pendiente'
    )

    def __str__(self):
        return f'{self.titulo_libro} - {self.id_usuario_FK}'
    
class PrestamoBienestar(models.Model):
    id_usuario_FK = models.ForeignKey('Usuario', on_delete=models.CASCADE, null=True)
    nombre_equipo = models.CharField(max_length=100)
    serial = models.CharField(max_length=100, null=True, blank=True)
    fecha_prestamo = models.DateField()
    fecha_devolucion = models.DateField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.nombre_equipo} - {self.id_usuario_FK}'
    
class ReporteSeguimiento(models.Model):
    id_usuario_FK = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_ficha_FK = models.ForeignKey(Ficha, on_delete=models.CASCADE)
    paz_y_salvo = models.BooleanField(default=False)
    observaciones = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Seguimiento - {self.id_usuario_FK}'
    
class Seguimiento(models.Model):
    id_aprendiz = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, related_name='seguimientos_como_aprendiz')
    id_instructor = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, related_name='seguimientos_como_instructor')

    pruebas_tyt = models.BooleanField(null=True)
    juicios_evaluativos = models.BooleanField(null=True)
    formato_etapaproductiva = models.BooleanField(null=True)
    bitacora_etapaproductiva = models.BooleanField(null=True)
    actividades_bienestar = models.BooleanField(null=True)
    pazysalvo_biblioteca = models.BooleanField(null=True)

    observaciones = models.CharField(max_length=250, null=True, blank=True)
    fecha_seguimiento = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'Seguimiento {self.id} - Aprendiz: {self.id_aprendiz} - Instructor: {self.id_instructor}'

class InstructorxAprendiz(models.Model):
    id_instructor_FK = models.ForeignKey(
        'Usuario', on_delete=models.SET_NULL, null=True, related_name='instructor_de_seguimiento'
    )
    id_aprendiz_FK = models.ForeignKey(
        'Usuario', on_delete=models.SET_NULL, null=True, related_name='aprendiz_en_seguimiento'
    )
    bitacoras_completas = models.BooleanField(default=False)  # ✅ Nuevo campo

    def __str__(self):
        return f'Instructor: {self.id_instructor_FK} - Aprendiz: {self.id_aprendiz_FK}'


@receiver(pre_save, sender=Usuario)
def eliminar_login_al_cambiar_a_aprendiz(sender, instance, **kwargs):
    if instance.pk:
        try:
            usuario_actual = Usuario.objects.get(pk=instance.pk)
            rol_actual = usuario_actual.id_rol_FK
            nuevo_rol = instance.id_rol_FK
            
            if (rol_actual != nuevo_rol and 
                nuevo_rol and 
                nuevo_rol.nombre_rol and 
                nuevo_rol.nombre_rol.lower() == 'aprendiz'):
                
                # ✅ ELIMINAR registro completo, no solo poner password=None
                Login.objects.filter(id_usuario_FK=instance).delete()
                    
        except Usuario.DoesNotExist:
            pass