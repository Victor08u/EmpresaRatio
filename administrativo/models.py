from django.db import models
from django.conf import settings
from core.models import TimeStampedUserModel, ESTADO_DOCUMENTO, MODALIDAD_PAGO
from clientes.models import Cliente
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()



class DocAdmin(TimeStampedUserModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=150)
    archivo_pdf = models.FileField(upload_to='documentos/administrativo/')
    estado = models.CharField(max_length=3, choices=ESTADO_DOCUMENTO, default='REC')

    def __str__(self):
        return f"{self.cliente} - {self.titulo}"


class HonoAdmin(TimeStampedUserModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    concepto = models.CharField(max_length=150)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    modalidad = models.CharField(max_length=4, choices=MODALIDAD_PAGO, default='CONT')
    periodo = models.DateField()
    meses_credito = models.PositiveIntegerField(blank=True, null=True)  # solo aplica si es crédito


class GestioAdmin(TimeStampedUserModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    descripcion = models.TextField()
    fecha = models.DateField()


    def __str__(self):
        return f"{self.cliente} - {self.fecha}"