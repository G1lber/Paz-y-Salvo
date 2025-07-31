from django import forms
from .models import Usuario

from django import forms
from .models import Usuario

from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellidos', 'num_doc', 'id_tipodoc_FK', 'id_ficha_FK', 'es_patrocinado']
        labels = {
            'nombre': 'Nombre',
            'apellidos': 'Apellidos',
            'num_doc': 'Número de documento',
            'id_tipodoc_FK': 'Tipo de documento',
            'id_ficha_FK': 'Ficha',
            'es_patrocinado': '¿Es patrocinado?',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'num_doc': forms.TextInput(attrs={'class': 'form-control'}),
            'id_tipodoc_FK': forms.Select(attrs={'class': 'form-control'}),
            'id_ficha_FK': forms.Select(attrs={'class': 'form-control'}),
            'es_patrocinado': forms.CheckboxInput(attrs={'class': 'form-check-input mt-2'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personaliza los campos si es necesario
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})
        self.fields['apellidos'].widget.attrs.update({'class': 'form-control'})
        self.fields['num_doc'].widget.attrs.update({'class': 'form-control'})
        

