from django.db import models
from django.contrib.auth import get_user_model
import json


User = get_user_model()


class TimeStampedUserModel(models.Model):
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')


class Meta:
    abstract = True

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.rol}"

class Auditoria(models.Model):
    ACCION_CHOICES = [
        ('ALTA', 'Alta'),
        ('MODIFICACION', 'Modificación'),
        ('ANULACION', 'Anulación'), # Usamos anulación en vez de baja
    ]

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tabla = models.CharField(max_length=50)
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    datos_viejos = models.TextField(blank=True, null=True)
    datos_nuevos = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.fecha_hora} - {self.usuario} - {self.accion} en {self.tabla}"

ESTADO_DOCUMENTO = (
    ('REC', 'Recibido'),
    ('ARC', 'En Archivo'),
    ('DEV', 'Devuelto'),
)


MODALIDAD_PAGO = (
    ('CONT', 'Contado'),
    ('CRED', 'Crédito'),
)