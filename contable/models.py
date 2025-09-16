from django.db import models
from core.models import TimeStampedUserModel, ESTADO_DOCUMENTO, MODALIDAD_PAGO
from clientes.models import Cliente
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()



class DocConta(TimeStampedUserModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=150)
    archivo_pdf = models.FileField(upload_to='documentos/contable/')
    estado = models.CharField(max_length=3, choices=ESTADO_DOCUMENTO, default='REC')


class HonoConta(TimeStampedUserModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    concepto = models.CharField(max_length=150)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    modalidad = models.CharField(max_length=4, choices=MODALIDAD_PAGO, default='CONT')
    periodo = models.DateField()
    meses_credito = models.PositiveIntegerField(blank=True, null=True)  # solo aplica si es crédito



class GestioConta(TimeStampedUserModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    descripcion = models.TextField()
    fecha = models.DateField()

TIPO_DOCUMENTO = [
    ('IVA', 'IVA'),
    ('REN', 'Renta'),
    ('ANT', 'Anticipos'),
    ('FAC', 'Facilidad'),
    ('IPS', 'IPS'),
]

class VencimientoConta(TimeStampedUserModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo_documento = models.CharField(max_length=10, choices=TIPO_DOCUMENTO)
    fecha_vencimiento = models.DateField()
    notificado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cliente} - {self.tipo_documento} ({self.fecha_vencimiento})"

    def mover_al_siguiente_mes(self):
        """Cuando el cliente trae el documento, pasar el vencimiento al mes siguiente."""
        # Ej: si vence el 15/09/2025, al registrar recibido → 15/10/2025
        mes = self.fecha_vencimiento.month + 1
        año = self.fecha_vencimiento.year
        if mes > 12:
            mes = 1
            año += 1
        self.fecha_vencimiento = self.fecha_vencimiento.replace(year=año, month=mes)
        self.notificado = False
        self.save()