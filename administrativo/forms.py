from django import forms
from .models import DocAdmin, HonoAdmin, GestioAdmin
from clientes.models import Cliente



class DocumentoAdminForm(forms.ModelForm):
    class Meta:
        model = DocAdmin
        fields = ["cliente", "titulo", "archivo_pdf", "estado"]
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-select"}),
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "archivo_pdf": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
        }

class HonorarioAdminForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all().order_by('nombre'),
        widget=forms.Select(attrs={"class": "form-select", "style": "width: 100%;"}),
        label="Cliente"
    )

    meses_credito = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "id": "id_meses_credito"}),
        label="Meses de Crédito"
    )

    class Meta:
        model = HonoAdmin
        fields = ["cliente", "concepto", "monto", "modalidad", "periodo", "meses_credito"]
        widgets = {
            "concepto": forms.TextInput(attrs={"class": "form-control"}),
            "monto": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "modalidad": forms.Select(attrs={"class": "form-select", "id": "id_modalidad"}),
            "periodo": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].label_from_instance = lambda obj: f"{obj.nombre} ({obj.ruc_ci})"

class GestionAdminForm(forms.ModelForm):
    class Meta:
        model = GestioAdmin
        fields = ["cliente", "descripcion", "fecha"]
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-select"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }
