from django.core.management.base import BaseCommand
from mainapp.models import Roles, TipoDoc, Centro

class Command(BaseCommand):
    help = 'Puebla la base de datos con datos iniciales (roles, tipos de documento, centros)'

    def handle(self, *args, **options):
        roles = [
            "Admin",
            "Coordinador Academico",
            "Biblioteca",
            "Responsable Bienestar",
            "Responsable Almacen",
            "Instructor Seguimiento",
            "Coordinador Empleo",
            "Aprendiz",
        ]
        for nombre in roles:
            Roles.objects.get_or_create(nombre_rol=nombre)
            self.stdout.write(self.style.SUCCESS(f"Rol '{nombre}' listo"))

        tipos = ["CC", "TI", "CE", "NIT"]
        for nombre in tipos:
            TipoDoc.objects.get_or_create(nombre_tipo=nombre)
            self.stdout.write(self.style.SUCCESS(f"TipoDoc '{nombre}' listo"))

        centro_nombre = "Centro de Formación"
        Centro.objects.get_or_create(nombre_centro=centro_nombre)
        self.stdout.write(self.style.SUCCESS(f"Centro '{centro_nombre}' listo"))

        self.stdout.write(self.style.SUCCESS("Seed completado exitosamente"))
