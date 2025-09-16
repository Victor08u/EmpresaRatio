from django import forms
from .models import DocConta, HonoConta, GestioConta, Cliente, VencimientoConta
from .models import TIPO_DOCUMENTO



class DocContaForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all().order_by('nombre'),
        widget=forms.Select(attrs={"class": "form-select", "style": "width: 100%;"}),
        label="Cliente"
    )

    class Meta:
        model = DocConta
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


class HonoContaForm(forms.ModelForm):
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
        model = HonoConta
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

class GestioContaForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all().order_by('nombre'),
        widget=forms.Select(attrs={"class": "form-select", "style": "width: 100%;"}),
        label="Cliente"
    )

    class Meta:
        model = GestioConta
        fields = ["cliente", "descripcion", "fecha"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].label_from_instance = lambda obj: f"{obj.nombre} ({obj.ruc_ci})"

class VencimientoContaForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all().order_by('nombre'),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="👤 Cliente"
    )

    tipo_documento = forms.ChoiceField(
        choices=TIPO_DOCUMENTO,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="📄 Tipo de Documento"
    )

    fecha_vencimiento = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        label="📅 Fecha de Vencimiento"
    )

    class Meta:
        model = VencimientoConta
        fields = ["cliente", "tipo_documento", "fecha_vencimiento"]