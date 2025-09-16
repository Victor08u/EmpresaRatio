from django.db import models
from django.conf import settings
from core.models import TimeStampedUserModel, MODALIDAD_PAGO
from clientes.models import Cliente
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver



class Caja(TimeStampedUserModel):
    fecha = models.DateField(auto_now_add=True)
    abierta = models.BooleanField(default=True)
    saldo_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_final = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        estado = "Abierta" if self.abierta else "Cerrada"
        return f"Caja {self.fecha} ({estado})"
    
    def calcular_saldo(self):
        ingresos = self.movimientocaja_set.filter(tipo="ING").aggregate(total=Sum("monto"))["total"] or 0
        egresos = self.movimientocaja_set.filter(tipo="EGR").aggregate(total=Sum("monto"))["total"] or 0
        return self.saldo_inicial + ingresos - egresos

    def cerrar(self):
        self.saldo_final = self.calcular_saldo()
        self.abierta = False
        self.save()

class MovimientoCaja(TimeStampedUserModel):
    TIPO_CHOICES = (
        ("ING", "Ingreso"),
        ("EGR", "Egreso"),
    )
    PAGO_CHOICES = (
        ("efectivo", "Efectivo"),
        ("tarjeta", "Tarjeta"),
        ("transferencia", "Transferencia"),
    )

    caja_movimiento = models.ForeignKey(Caja, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    tipo = models.CharField(max_length=3, choices=TIPO_CHOICES)
    concepto = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    modalidad = models.CharField(max_length=10, choices=MODALIDAD_PAGO)
    tipo_pago = models.CharField(max_length=15, choices=PAGO_CHOICES, default="efectivo")
    numero_referencia = models.CharField(max_length=50, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario_alta = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="movimientos_creados"
    )

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.concepto} - {self.monto}"

    def save(self, *args, **kwargs):
        if not self.caja_movimiento.abierta:
            raise ValueError("No se pueden registrar movimientos en una caja cerrada.")
        super().save(*args, **kwargs)

class Recibo(TimeStampedUserModel):
    movimiento = models.OneToOneField(MovimientoCaja, on_delete=models.CASCADE, related_name="recibo")
    detalle = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Recibo #{self.id} - {self.movimiento.concepto}"

@receiver(post_save, sender=MovimientoCaja)
def crear_recibo(sender, instance, created, **kwargs):
    if created and instance.tipo == "ING":  # solo ingresos generan recibo
        Recibo.objects.create(movimiento=instance)