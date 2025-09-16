from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Caja, MovimientoCaja
from .forms import CajaAperturaForm, CajaCierreForm, MovimientoCajaForm
from django.db.models import Sum
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
import os
from django.conf import settings
from django.db.models import Q
from contable.models import Cliente
from reportlab.lib.utils import ImageReader
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist
from core.utils import registrar_auditoria
from django.utils.timezone import make_aware
from datetime import datetime

logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo_empresa.png')

@login_required

def caja_home(request):
    ultima_caja = Caja.objects.filter(creado_por=request.user).last()
    return render(request, "caja/home.html", {"ultima_caja": ultima_caja})



@login_required
def abrir_caja(request):
    if Caja.objects.filter(creado_por=request.user, abierta=True).exists():
        messages.warning(request, "Ya tienes una caja abierta.")
        return redirect("caja:movimientos")

    if request.method == "POST":
        form = CajaAperturaForm(request.POST)

        if form.is_valid():
            caja = form.save(commit=False)
            caja.creado_por = request.user
            caja.abierta = True
            caja.save()
            registrar_auditoria(request.user, caja, 'APERTURA', None)
            messages.success(request, "Caja abierta correctamente.")
            return redirect("caja:movimientos")
    else:
        form = CajaAperturaForm()

    return render(request, "caja/caja_abrir.html", {"form": form})


@login_required
@transaction.atomic
def cerrar_caja(request, pk):
    datos_viejos = None
    try:
        # Buscamos la caja por su ID (pk) y nos aseguramos de que esté abierta
        caja_abierta = Caja.objects.get(pk=pk, abierta=True)
    except Caja.DoesNotExist:
        messages.error(request, "La caja especificada no existe o ya está cerrada.")
        return redirect("caja:movimientos")

    # 1. CALCULAR EL ARQUEO: Agrupamos los movimientos por modalidad y sumamos sus montos
    movimientos = MovimientoCaja.objects.filter(caja_movimiento=caja_abierta)
    
    arqueo = movimientos.values('modalidad').annotate(total=Sum('monto'))
    total_general = movimientos.aggregate(Sum('monto'))['monto__sum'] or 0
    total_general += caja_abierta.saldo_inicial  # Incluir el saldo inicial en el total
        # Mostrar el saldo inicial en el arqueo
    arqueo = list(arqueo)  # Convertir a lista para manipulación
    arqueo.insert(0, {'modalidad': 'Saldo Inicial', 'total': caja_abierta.saldo_inicial})

    if request.method == "POST":
        # 2. SI EL USUARIO CONFIRMA EL CIERRE (presiona un botón "Confirmar Cierre")
        caja_abierta.fecha_cierre = timezone.now()
        caja_abierta.abierta = False
        caja_abierta.saldo_final = total_general
    
        caja_abierta.save()
        registrar_auditoria(request.user, caja_abierta, 'CIERRE', datos_viejos)

        messages.success(request, "Caja cerrada correctamente.")
        return redirect("caja:movimientos")

    # 3. MOSTRAR LA PANTALLA DE ARQUEO ANTES DE CERRAR
    return render(request, 'caja/cierre_arqueo.html', {
        'caja': caja_abierta,
        'arqueo': arqueo,
        'total_general': total_general
    })


def arqueo(request):
    # Tomamos la última caja abierta
    caja = Caja.objects.filter(abierta=True).last()
    if not caja:
        messages.warning(request, "No hay ninguna caja abierta.")
        return redirect("caja:movimientos")  # redirige a la lista de movimientos

    # Calculamos ingresos, egresos y saldo final
    ingresos = MovimientoCaja.objects.filter(caja_movimiento=caja, tipo="ING").aggregate(total=Sum("monto"))["total"] or 0
    egresos = MovimientoCaja.objects.filter(caja_movimiento=caja, tipo="EGR").aggregate(total=Sum("monto"))["total"] or 0
    saldo_final = caja.saldo_inicial + ingresos - egresos

    return render(request, "caja/arqueo.html", {
        "caja": caja,
        "ingresos": ingresos,
        "egresos": egresos,
        "saldo_final": saldo_final
    })


from django.utils.dateparse import parse_date

def movimientos(request):
    caja = Caja.objects.filter(abierta=True).last()
    movimientos = MovimientoCaja.objects.filter(caja_movimiento=caja) if caja else MovimientoCaja.objects.none()

    # Filtros por fecha
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    if fecha_desde:
        movimientos = movimientos.filter(fecha__date__gte=parse_date(fecha_desde))
    if fecha_hasta:
        movimientos = movimientos.filter(fecha__date__lte=parse_date(fecha_hasta))

    return render(
        request, 
        "caja/movimientos_list.html", 
        {"caja": caja, "movimientos": movimientos}
    )

def recibo_movimiento(request, pk):
    mov = get_object_or_404(MovimientoCaja, pk=pk)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="recibo_{mov.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # --- Logo de la empresa ---
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo_empresa2.png')
    if os.path.exists(logo_path):
        p.drawImage(logo_path, 40, height - 100, width=100, height=50, preserveAspectRatio=True)
    else:
        print("Logo NO encontrado:", logo_path)

    # --- Encabezado ---
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, height - 50, "RECIBO DE CAJA")

    # Línea decorativa
    p.setLineWidth(1)
    p.line(40, height - 60, width - 40, height - 60)

    # --- Datos del recibo ---
    p.setFont("Helvetica", 12)
    y = height - 130
    line_height = 25

    datos = [
        f"Cliente: {mov.cliente if mov.cliente else '---'}",
        f"Concepto: {mov.concepto}",
        f"Monto: Gs. {mov.monto:,.2f}",
        f"Forma de Pago: {mov.get_modalidad_display()}",
        f"Fecha: {mov.fecha.strftime('%d/%m/%Y %H:%M')}",
        f"Usuario: {mov.usuario_alta.username if mov.usuario_alta else '---'}"
    ]

    for d in datos:
        p.drawString(50, y, d)
        y -= line_height

    # --- Pie de página ---
    p.setFont("Helvetica-Oblique", 10)
    p.drawCentredString(width / 2, 30, "Gracias por su pago. ¡Mantenga este recibo como comprobante!")

    p.showPage()
    p.save()

    return response

@login_required
def movimientos_por_fecha(request):
    movimientos = None
    fecha_desde = request.GET.get("fecha_desde")
    fecha_hasta = request.GET.get("fecha_hasta")

    if fecha_desde and fecha_hasta:
        fecha_desde_dt = make_aware(datetime.strptime(fecha_desde, "%Y-%m-%d"))
        fecha_hasta_dt = make_aware(datetime.strptime(fecha_hasta, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
        movimientos = MovimientoCaja.objects.filter(fecha__range=(fecha_desde_dt, fecha_hasta_dt)).order_by("-fecha")

    return render(request, "caja/movimientos_por_fecha.html", {
        "movimientos": movimientos,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
    })