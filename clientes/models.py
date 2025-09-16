from django.db import models


class Cliente(models.Model):
    nombre = models.CharField(max_length=150)
    ruc_ci = models.CharField(max_length=50, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    fecha_alta = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)


    class Meta:
        ordering = ['nombre']


    def __str__(self):
        return self.nombre