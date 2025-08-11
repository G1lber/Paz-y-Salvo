from django.contrib import admin
from .models import Usuario, Login, Ficha, Roles,TipoDoc

admin.site.register(Ficha)
admin.site.register(Roles)
admin.site.register(Usuario)
admin.site.register(TipoDoc)
admin.site.register(Login)
# Register your models here.
