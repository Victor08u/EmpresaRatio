from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'ruc_ci', 'email', 'telefono', 'direccion']  # <-- agregamos ruc_ci
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'ruc_ci': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),  # <-- widget para ruc_ci
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-lg'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
        }
