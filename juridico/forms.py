from django import forms
from .models import DocJuri, HonoJuri, GestioJuri
from clientes.models import Cliente


class DocJuriForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all().order_by('nombre'),
        widget=forms.Select(attrs={"class": "form-select", "style": "width: 100%;"}),
        label="Cliente"
    )

    class Meta:
        model = DocJuri
        fields = ["cliente", "titulo", "archivo_pdf", "estado"]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "archivo_pdf": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar nombre + RUC/CI
        self.fields['cliente'].label_from_instance = lambda obj: f"{obj.nombre} ({obj.ruc_ci})"


class HonoJuriForm(forms.ModelForm):
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
        model = HonoJuri
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

class GestioJuriForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all().order_by('nombre'),
        widget=forms.Select(attrs={"class": "form-select", "style": "width: 100%;"}),
        label="Cliente"
    )

    class Meta:
        model = GestioJuri
        fields = ["cliente", "descripcion", "fecha"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].label_from_instance = lambda obj: f"{obj.nombre} ({obj.ruc_ci})"
