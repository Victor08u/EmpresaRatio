# core/utils.py
import json
from .models import Auditoria
from django.forms.models import model_to_dict

def registrar_auditoria(usuario, instancia, accion, datos_viejos=None):
    """
    Registra una acción en la tabla de auditoría.
    - usuario: El request.user que realiza la acción.
    - instancia: El objeto del modelo que se está modificando (ej. un objeto Cliente).
    - accion: 'ALTA', 'MODIFICACION' o 'ANULACION'.
    - datos_viejos: Un diccionario con los datos antes del cambio (solo para modificaciones).
    """
    datos_nuevos_dict = model_to_dict(instancia)
    
    Auditoria.objects.create(
        usuario=usuario,
        tabla=instancia.__class__._meta.verbose_name, # Nombre del modelo
        accion=accion,
        datos_viejos=json.dumps(datos_viejos, default=str) if datos_viejos else None,
        datos_nuevos=json.dumps(datos_nuevos_dict, default=str)
    )