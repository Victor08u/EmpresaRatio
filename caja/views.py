from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Caja, MovimientoCaja
from .forms import CajaAperturaForm, CajaCierreForm, MovimientoCajaForm, MovimientoManualForm
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
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph




logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo_empresa.png')

@login_required

def caja_home(request):
    ultima_caja = Caja.objects.filter(usuario=request.user).last()
    return render(request, "caja/home.html", {"ultima_caja": ultima_caja})



@login_required
def abrir_caja(request):
    if Caja.objects.filter(usuario=request.user, abierta=True).exists():
        messages.warning(request, "Ya tienes una caja abierta.")
        return redirect("caja:movimientos")

    if request.method == "POST":
        form = CajaAperturaForm(request.POST)
        if form.is_valid():
            caja = form.save(commit=False)
            caja.usuario = request.user  # 🔑 asignar dueño de la caja
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
        caja_abierta = get_object_or_404(Caja, pk=pk, usuario=request.user, abierta=True)
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
    caja_abierta = Caja.objects.filter(usuario=request.user, abierta=True).last()
    if not caja_abierta:
        messages.warning(request, "No hay ninguna caja abierta.")
        return redirect("caja:movimientos")  # redirige a la lista de movimientos

    # Calculamos ingresos, egresos y saldo final
    ingresos = MovimientoCaja.objects.filter(caja_movimiento=caja_abierta, tipo="ING").aggregate(total=Sum("monto"))["total"] or 0
    egresos = MovimientoCaja.objects.filter(caja_movimiento=caja_abierta, tipo="EGR").aggregate(total=Sum("monto"))["total"] or 0
    saldo_final = caja_abierta.saldo_inicial + ingresos - egresos

    return render(request, "caja/arqueo.html", {
        "caja": caja_abierta,
        "ingresos": ingresos,
        "egresos": egresos,
        "saldo_final": saldo_final
    })


from django.utils.dateparse import parse_date

def movimientos(request):
    caja_abierta = Caja.objects.filter(usuario=request.user, abierta=True).last()
    if not caja_abierta:
        messages.warning(request, "No hay ninguna caja abierta.")
        return redirect("caja:home")  # redirige a la lista de movimientos
    caja = caja_abierta
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

    # --- Dibujar borde redondeado ---
    p.setStrokeColor(colors.black)
    p.setLineWidth(1)
    p.roundRect(40, height - 270, width - 80, 220, 10, stroke=1, fill=0)

    # --- Logo ---
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo_empresa.png')
    if os.path.exists(logo_path):
        # ancho y alto proporcionales (máximo 100px de alto)
        p.drawImage(
            logo_path,
            55, height - 95,   # posición
            width=130, height=50,  # espacio asignado
            preserveAspectRatio=True,
            mask='auto'
        )

    # --- Encabezado ---
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(width/2, height - 65, "RECIBO")

    # --- Número y monto ---
    p.setFont("Helvetica-Bold", 10)
    p.drawRightString(width - 60, height - 60, f"N.º {mov.id}")
    p.setFont("Helvetica-Bold", 12)
    p.drawRightString(width - 60, height - 80, f"G. {mov.monto:,.0f}")

    # --- Fecha ---
    p.setFont("Helvetica", 10)
    p.drawRightString(width - 60, height - 105, mov.fecha.strftime("Obligado, %d de %B del %Y"))

    # --- Campos ---
    p.setFont("Helvetica", 10)
    p.drawString(60, height - 135, "Recibí (mos) de")
    p.line(140, height - 137, width - 60, height - 137)
    p.drawString(145, height - 135, mov.cliente.nombre if mov.cliente else "---")

    p.drawString(60, height - 160, "La cantidad de guaraníes")
    p.line(200, height - 162, width - 60, height - 162)
    p.drawString(205, height - 160, f"{mov.monto:,.0f}")

    p.drawString(60, height - 185, "En concepto de pago")
    p.line(170, height - 187, width - 60, height - 187)
    p.drawString(175, height - 185, mov.concepto)

    # --- Firma ---
    p.line(width/2 - 100, height - 230, width/2 + 100, height - 230)
    p.setFont("Helvetica", 9)
    p.drawCentredString(width/2, height - 245, "Firma y aclaración")
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(width/2, height - 260, "Ratio Asesoría Empresarial")

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

@login_required
@transaction.atomic
def nuevo_movimiento(request):
    caja_abierta = Caja.objects.filter(abierta=True, usuario=request.user).first()
    if not caja_abierta:
        messages.error(request, "No tienes ninguna caja abierta. Primero debes abrirla.")
        return redirect('caja:home')

    if request.method == "POST":
        form = MovimientoManualForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.caja_movimiento = caja_abierta  # <--- CORRECCIÓN
            movimiento.usuario_alta = request.user
            movimiento.save()
            registrar_auditoria(request.user, movimiento, 'CREACION', None)
            messages.success(request, "Movimiento registrado.")
            return redirect('caja:movimientos')
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = MovimientoManualForm()

    return render(request, 'caja/nuevo_movimiento.html', {'form': form})