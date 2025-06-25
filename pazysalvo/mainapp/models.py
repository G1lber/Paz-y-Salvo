from django.db import models

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
    id_programa = models.IntegerField(primary_key=True)
    nombre_programa = models.CharField(max_length=150)
    id_centro_FK = models.ForeignKey(Centro, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.nombre_programa


class Ficha(models.Model):
    num_ficha = models.AutoField(primary_key=True)
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

    def __str__(self):
        return f'{self.nombre} {self.apellidos}'


class Login(models.Model):
    id_usuario_FK = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    password = models.CharField(max_length=100, null=True)

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

class ReporteBienestar(models.Model):
    id_usuario_FK = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_ficha_FK = models.ForeignKey(Ficha, on_delete=models.CASCADE)
    paz_y_salvo = models.BooleanField(default=False)
    observaciones = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Bienestar - {self.id_usuario_FK}'

class ReporteBiblioteca(models.Model):
    id_usuario_FK = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_ficha_FK = models.ForeignKey(Ficha, on_delete=models.CASCADE)
    paz_y_salvo = models.BooleanField(default=False)
    observaciones = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Biblioteca - {self.id_usuario_FK}'

class ReporteAlmacen(models.Model):
    id_usuario_FK = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_ficha_FK = models.ForeignKey(Ficha, on_delete=models.CASCADE)
    paz_y_salvo = models.BooleanField(default=False)
    observaciones = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Almacén - {self.id_usuario_FK}'
    
class ReporteSeguimiento(models.Model):
    id_usuario_FK = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_ficha_FK = models.ForeignKey(Ficha, on_delete=models.CASCADE)
    paz_y_salvo = models.BooleanField(default=False)
    observaciones = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Seguimiento - {self.id_usuario_FK}'