from django.shortcuts import render
from .forms import ReporteForm
from contable.models import DocConta, HonoConta, GestioConta
from administrativo.models import DocAdmin, HonoAdmin, GestioAdmin
from juridico.models import DocJuri, HonoJuri, GestioJuri
from django.contrib.auth.models import User
from core.models import Auditoria
from datetime import datetime
from django.contrib.auth.decorators import login_required
from datetime import timedelta, datetime
from django.utils import timezone


# from core.decorators import rol_requerido  # Si decides proteger esto por rol

def reportes_home(request):
    """
    Página principal de reportes. Permite elegir entre diferentes tipos de reportes.
    """
    return render(request, "reportes/home.html")


def reporte_index(request):
    resultados = None
    form = ReporteForm(request.GET or None)

    if form.is_valid():
        cliente = form.cleaned_data["cliente"]
        area = form.cleaned_data["area"]
        tipo = form.cleaned_data["tipo"]
        fecha_desde = form.cleaned_data.get("fecha_desde")
        fecha_hasta = form.cleaned_data.get("fecha_hasta")

        modelo = None

        # Selección dinámica del modelo
        if area == "contable":
            if tipo == "documentos":
                modelo = DocConta
            elif tipo == "honorarios":
                modelo = HonoConta
            elif tipo == "gestiones":
                modelo = GestioConta
        elif area == "administrativo":
            if tipo == "documentos":
                modelo = DocAdmin
            elif tipo == "honorarios":
                modelo = HonoAdmin
            elif tipo == "gestiones":
                modelo = GestioAdmin
        elif area == "juridico":
            if tipo == "documentos":
                modelo = DocJuri
            elif tipo == "honorarios":
                modelo = HonoJuri
            elif tipo == "gestiones":
                modelo = GestioJuri

        if modelo:
            queryset = modelo.objects.filter(cliente=cliente)

            # determinar el campo de fecha según el modelo
            if tipo == "documentos":
                fecha_campo = "creado_en"
            elif tipo == "honorarios":
                fecha_campo = "periodo"
            elif tipo == "gestiones":
                fecha_campo = "fecha"
            else:
                fecha_campo = None

            # filtrar por fechas
            if fecha_campo:
                if fecha_desde:
                    queryset = queryset.filter(**{f"{fecha_campo}__gte": fecha_desde})
                if fecha_hasta:
                    queryset = queryset.filter(**{f"{fecha_campo}__lte": fecha_hasta})

            resultados = queryset

    return render(
        request,
        "reportes/reporte_index.html",
        {"form": form, "resultados": resultados},
    )

@login_required
# Podrías proteger esto para que solo lo vean los administradores
# @rol_requerido('Administrador')
def reporte_auditoria(request):
    usuarios = User.objects.all()
    movimientos = Auditoria.objects.filter(fecha_hora__date=timezone.localdate()).order_by('-fecha_hora')

    usuario_id = request.GET.get('usuario')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    if usuario_id and usuario_id.isdigit():
        movimientos = movimientos.filter(usuario_id=int(usuario_id))
    
    if fecha_desde:
        try:
            fecha_desde_dt = timezone.make_aware(datetime.strptime(fecha_desde, '%Y-%m-%d'))
            movimientos = movimientos.filter(fecha_hora__gte=fecha_desde_dt)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            fecha_hasta_dt = timezone.make_aware(fecha_hasta_dt)
            movimientos = movimientos.filter(fecha_hora__lte=fecha_hasta_dt)
        except ValueError:
            pass

    return render(request, 'reportes/auditoria.html', {
        'movimientos': movimientos,
        'usuarios': usuarios,
        'filtro_usuario': usuario_id,
        'filtro_desde': fecha_desde,
        'filtro_hasta': fecha_hasta,
    })




@login_required
    
def reporte_clientes(request):
    return HttpResponse("Reporte de Clientes - En construcción")

def reporte_vencimientos(request):
    return HttpResponse("Reporte de Vencimientos - En construcción")

def reporte_documentos(request):
    return HttpResponse("Reporte de Documentos - En construcción")

def reporte_honorarios(request):
    return HttpResponse("Reporte de Honorarios - En construcción")

def reporte_gestiones(request):
    return HttpResponse("Reporte de Gestiones - En construcción")

def reporte_pagos(request):
    return HttpResponse("Reporte de Pagos - En construcción")
    return HttpResponse("Reporte de Vencimientos - En construcción")

def reporte_clientes_detalle(request, cliente_id):
    return HttpResponse(f"Detalle del Cliente {cliente_id} - En construcción")

def reporte_vencimientos_detalle(request, vencimiento_id):
    return HttpResponse(f"Detalle del Vencimiento {vencimiento_id} - En construcción")  

def reporte_documentos_detalle(request, documento_id):
    return HttpResponse(f"Detalle del Documento {documento_id} - En construcción")
def reporte_honorarios_detalle(request, honorario_id):
    return HttpResponse(f"Detalle del Honorario {honorario_id} - En construcción")
def reporte_gestiones_detalle(request, gestion_id):
    return HttpResponse(f"Detalle de la Gestión {gestion_id} - En construcción")
def reporte_pagos_detalle(request, pago_id):
    return HttpResponse(f"Detalle del Pago {pago_id} - En construcción")
