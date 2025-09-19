from django import forms
from .models import Caja, MovimientoCaja
from .models import MODALIDAD_PAGO


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

class MovimientoManualForm(forms.ModelForm):
    TIPO_CHOICES = [
        ('ING', 'Ingreso'),
        ('EGR', 'Egreso'),
    ]

    MODALIDAD_CHOICES = MODALIDAD_PAGO  # traído de tu modelo
    TIPO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
    ]

    tipo = forms.ChoiceField(choices=TIPO_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    modalidad = forms.ChoiceField(choices=MODALIDAD_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    tipo_pago = forms.ChoiceField(choices=TIPO_PAGO_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    monto = forms.DecimalField(max_digits=12, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'step':'0.01'}))
    numero_referencia = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
    concepto = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control'}), initial="Movimiento Manual")

    class Meta:
        model = MovimientoCaja
        fields = ['tipo', 'modalidad', 'tipo_pago', 'monto', 'numero_referencia', 'concepto']

    def clean(self):
        cleaned_data = super().clean()
        tipo_pago = cleaned_data.get('tipo_pago')  # nombre del campo correcto
        numero_ref = cleaned_data.get('numero_referencia')

        # Solo obligatorio para tarjeta o transferencia
        if tipo_pago in ['tarjeta', 'transferencia'] and not numero_ref:
            self.add_error('numero_referencia', 'Se requiere número de referencia para tarjeta o transferencia.')

        return cleaned_data
# Opciones para los campos de área y tipo