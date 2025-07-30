from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'num_doc': forms.NumberInput(attrs={'class': 'form-control'}),
            'id_tipodoc_FK': forms.Select(attrs={'class': 'form-control'}),
            'id_rol_FK': forms.Select(attrs={'class': 'form-control'}),
            'id_ficha_FK': forms.Select(attrs={'class': 'form-control'}),
        }
