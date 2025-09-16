from django import forms
from clientes.models import Cliente

AREA_CHOICES = [
    ("contable", "Contable"),
    ("administrativo", "Administrativo"),
    ("juridico", "Jurídico"),
]

TIPO_CHOICES = [
    ("documentos", "Documentos"),
    ("honorarios", "Honorarios"),
    ("gestiones", "Gestiones"),
]

class ReporteForm(forms.Form):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        label="Cliente",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "placeholder": "Seleccione un cliente"
            }
        )
    )
    area = forms.ChoiceField(
        choices=AREA_CHOICES,
        label="Área",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        )
    )
    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        label="Tipo de Comprobante",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        )
    )
    fecha_desde = forms.DateField(
        required=False,
        label="Desde",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        )
    )
    fecha_hasta = forms.DateField(
        required=False,
        label="Hasta",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        )
    )
    # Puedes agregar más campos de filtro según sea necesario