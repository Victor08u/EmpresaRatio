from django import forms
from .models import Caja, MovimientoCaja


class CajaAperturaForm(forms.ModelForm):
    class Meta:
        model = Caja
        fields = ["saldo_inicial"]


class CajaCierreForm(forms.ModelForm):
    class Meta:
        model = Caja
        fields = []  # saldo_final se calcula


class MovimientoCajaForm(forms.ModelForm):
    class Meta:
        model = MovimientoCaja
        # Excluimos 'tipo' y 'concepto', que se definen en la vista
        fields = ['monto', 'modalidad', 'tipo_pago', 'numero_referencia']
        widgets = {
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'modalidad': forms.Select(attrs={'class': 'form-select'}),
            'tipo_pago': forms.Select(attrs={'class': 'form-select'}),
            'numero_referencia': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacemos que numero_referencia no sea obligatorio
        self.fields['numero_referencia'].required = False
