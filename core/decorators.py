# C:\SISTEMAS\RATIO\recepcion_docs\core\decorators.py

from django.core.exceptions import PermissionDenied
from functools import wraps

def rol_requerido(*roles_permitidos):
    """
    Decora una vista para restringir el acceso a usuarios que pertenecen
    a uno de los grupos especificados.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Condición de salida rápida para superusuarios o staff
            if request.user.is_superuser or request.user.is_staff:
                return view_func(request, *args, **kwargs)

            # Si el usuario está autenticado, verifica sus grupos
            if request.user.is_authenticated:
                user_groups = [group.name for group in request.user.groups.all()]
                if any(rol in user_groups for rol in roles_permitidos):
                    return view_func(request, *args, **kwargs)
            
            # Si el usuario no está autenticado o no tiene el rol, se deniega el acceso.
            raise PermissionDenied
        return _wrapped_view
    return decorator