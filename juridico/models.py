from django.db import models
from core.models import TimeStampedUserModel, ESTADO_DOCUMENTO, MODALIDAD_PAGO
from clientes.models import Cliente


class DocJuri(TimeStampedUserModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=150)
    archivo_pdf = models.FileField(upload_to='documentos/juridico/')
    estado = models.CharField(max_length=3, choices=ESTADO_DOCUMENTO, default='REC')


class HonoJuri(TimeStampedUserModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    concepto = models.CharField(max_length=150)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    modalidad = models.CharField(max_length=4, choices=MODALIDAD_PAGO, default='CONT')
    periodo = models.DateField()


class GestioJuri(TimeStampedUserModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    descripcion = models.TextField()
    fecha = models.DateField()