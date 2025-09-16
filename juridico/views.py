from django.shortcuts import render, redirect, get_object_or_404
from .models import DocJuri, HonoJuri, GestioJuri
from .forms import DocJuriForm, HonoJuriForm, GestioJuriForm
from django.contrib.auth.decorators import login_required
from core.decorators import rol_requerido
from django.contrib import messages
from caja.models import Caja
from caja.forms import MovimientoCajaForm
from django.db import transaction
from decimal import Decimal
from datetime import date
import datetime
from clientes.models import Cliente
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from core.models import ESTADO_DOCUMENTO, MODALIDAD_PAGO
from django.forms.models import model_to_dict
from core.utils import registrar_auditoria


ROLES_CONTABLE = ('Contador', 'Administrador', 'admin', 'adm')

# -------------------------------
# PÁGINA PRINCIPAL
# -------------------------------
def juridico_home(request):
    return render(request, "juridico/home.html")

# -------------------------------
# DOCUMENTOS
# -------------------------------
def documentos_juridico(request):
    documentos = DocJuri.objects.all().order_by("-creado_en")

    # Filtros
    cliente_filtro = request.GET.get("cliente")
    estado_filtro = request.GET.get("estado")

    if cliente_filtro:
        documentos = documentos.filter(cliente__nombre__icontains=cliente_filtro)
    if estado_filtro:
        documentos = documentos.filter(estado=estado_filtro)

    return render(request, "juridico/documentos_list.html", {
        "documentos": documentos,
        "ESTADO_DOCUMENTO": ESTADO_DOCUMENTO,
        "request": request
    })

def nuevo_documento_juridico(request):
    if request.method == "POST":
        form = DocJuriForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Documento cargado correctamente.")
            registrar_auditoria(request.user, form.instance, 'CREACION', None)
            return redirect("juridico:carga_documentos")
    else:
        form = DocJuriForm()
    return render(request, "juridico/documentos_form.html", {"form": form})

def eliminar_documento_juridico(request, id):
    doc = get_object_or_404(DocJuri, id=id)
    datos_viejos = model_to_dict(doc)
    if request.method == "POST":
        doc.delete()
        registrar_auditoria(request.user, doc, 'ELIMINACION', datos_viejos)
        messages.success(request, "Documento eliminado correctamente.")
        return redirect("juridico:carga_documentos")
    return render(request, "juridico/documentos_confirm_delete.html", {"doc": doc})
@login_required
@rol_requerido(*ROLES_CONTABLE)
def lista_documentos_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    # Filtramos los documentos que pertenecen solo a este cliente
    documentos = DocJuri.objects.filter(cliente=cliente).order_by("-creado_en")
    return render(request, "juridico/documentos_list.html", {
        "documentos": documentos,
        "cliente": cliente  # Enviamos el cliente a la plantilla
    })
# -------------------------------
# HONORARIOS
# -------------------------------
@login_required
@rol_requerido(*ROLES_CONTABLE)
def carga_honorarios(request):
    honorarios = HonoJuri.objects.all().order_by("-creado_en")

    # Filtros
    cliente_filtro = request.GET.get("cliente")
    modalidad_filtro = request.GET.get("modalidad")

    if cliente_filtro:
        honorarios = honorarios.filter(cliente__nombre__icontains=cliente_filtro)
    if modalidad_filtro:
        honorarios = honorarios.filter(modalidad=modalidad_filtro)

    return render(request, "juridico/honorarios_list.html", {
        "honorarios": honorarios,
        "MODALIDAD_PAGO": MODALIDAD_PAGO,
        "request": request
    })
@login_required
@rol_requerido(*ROLES_CONTABLE)
def lista_honorarios_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    # Filtramos los honorarios que pertenecen solo a este cliente
    honorarios = HonoJuri.objects.filter(cliente=cliente).order_by("-creado_en")
    return render(request, "juridico/honorarios_list.html", {
        "honorarios": honorarios,
        "cliente": cliente  # Enviamos el cliente a la plantilla
    })


@login_required
@rol_requerido(*ROLES_CONTABLE)
def nuevo_honorario_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    if not Caja.objects.filter(creado_por=request.user, abierta=True).exists():
        messages.error(request, "Error: No tiene una caja abierta. Por favor, abra una para continuar.")
        return redirect("caja:abrir_caja")

    if request.method == "POST":
        form = HonoJuriForm(request.POST)
        if form.is_valid():
            honorario_data = form.cleaned_data
            
            if 'fecha' in honorario_data and isinstance(honorario_data['fecha'], datetime.date):
                honorario_data['fecha'] = honorario_data['fecha'].isoformat()
            
            honorario_data['monto'] = str(honorario_data['monto'])
            honorario_data['cliente_id'] = cliente_id
            request.session['honorario_temporal'] = honorario_data
            return redirect("juridico:registrar_pago_honorario")
    else:
        form = HonoJuriForm()

    return render(request, "juridico/honorarios_form.html", {"form": form, "cliente": cliente})


@login_required
@rol_requerido(*ROLES_CONTABLE)
def nuevo_honorario(request):
    # Verificación de caja abierta
    if request.method == "POST":
        honorario_form = HonoJuriForm(request.POST)
        if honorario_form.is_valid():
            honorario_data = honorario_form.cleaned_data
            honorario_data = serializar_fechas(honorario_data)

            if 'cliente' in honorario_data and honorario_data['cliente']:
                honorario_data['cliente_id'] = honorario_data['cliente'].pk
                del honorario_data['cliente']

            honorario_data['monto'] = str(honorario_data['monto'])
            request.session['honorario_temporal'] = honorario_data
            return redirect("juridico:registrar_pago_honorario")

    else:
        honorario_form = HonoJuriForm()

    return render(request, "juridico/honorarios_form.html", {"form": honorario_form})
@login_required
@rol_requerido(*ROLES_CONTABLE)
def eliminar_honorario(request, id):
    honorario = get_object_or_404(HonoJuri, pk=id)
    datos_viejos = model_to_dict(honorario)
    if request.method == "POST":
        honorario.delete()
        registrar_auditoria(request.user, honorario, 'ELIMINACION', datos_viejos)
        messages.success(request, "Honorario eliminado correctamente.")
    return redirect('juridico:carga_honorarios')
periodo_actual = date.today()
@login_required
@rol_requerido(*ROLES_CONTABLE)
@transaction.atomic # ¡Clave! O se guarda todo, o no se guarda nada.
def registrar_pago_honorario(request):
    # 1. Recuperamos los datos del honorario desde la sesión
    honorario_data = request.session.get('honorario_temporal')
    
    # Si por alguna razón no hay datos en la sesión, evitamos un error
    if not honorario_data:
        messages.error(request, "Ha ocurrido un error o la sesión ha expirado. Por favor, intente cargar el honorario de nuevo.")
        # Asumiendo que tienes una lista general de clientes
        return redirect("clientes:listar")

    # Obtenemos la instancia del cliente
    cliente = get_object_or_404(Cliente, id=honorario_data['cliente_id'])
    monto_honorario = Decimal(honorario_data['monto']) # Convertimos de nuevo a Decimal

    if request.method == 'POST':
        # Usamos un formulario específico para el movimiento de caja
        form_pago = MovimientoCajaForm(request.POST)
        if form_pago.is_valid():
            # ---- ¡AQUÍ OCURRE LA MAGIA! ----
            
            # A. Creamos y guardamos el Honorario con los datos de la sesión
            honorario = HonoJuri.objects.create(
                cliente=cliente,
                monto=monto_honorario,
                concepto=honorario_data['concepto'],
                periodo=periodo_actual,
            )

            # B. Obtenemos la caja abierta del usuario
            caja_abierta = Caja.objects.get(creado_por=request.user, abierta=True)

            # C. Creamos y guardamos el Movimiento de Caja con los datos del formulario de pago
            movimiento = form_pago.save(commit=False)
            movimiento.caja_movimiento = caja_abierta
            movimiento.cliente = cliente
            movimiento.tipo = "ING" # Ingreso
            movimiento.concepto = f"Cobro por honorario: {honorario.concepto}"
            movimiento.monto = monto_honorario # El monto es el mismo que el del honorario
            movimiento.usuario_alta = request.user
            movimiento.save()
            caja_abierta.saldo_actual += monto_honorario
            caja_abierta.save()
            registrar_auditoria(request.user, caja_abierta, 'MODIFICACION', model_to_dict(caja_abierta))
            registrar_auditoria(request.user, honorario, 'CREACION', None)
            registrar_auditoria(request.user, movimiento, 'CREACION', None)

            # Actualizamos el saldo de la caja
            

            # D. ¡MUY IMPORTANTE! Limpiamos la sesión
            del request.session['honorario_temporal']
            
            # Aquí llamarías a la auditoría para ambos modelos
            # registrar_auditoria(request.user, honorario, 'ALTA')
            # registrar_auditoria(request.user, movimiento, 'ALTA')

            messages.success(request, "¡Honorario y pago registrados exitosamente!")
            return redirect('juridico:lista_honorarios_cliente', cliente_id=cliente.id)
        else:
            print(form_pago.errors)  # 👈
            messages.error(request, f"Errores en el formulario: {form_pago.errors}")
            
    else:
        # Al cargar la página por primera vez, pre-llenamos el formulario con datos útiles
        form_pago = MovimientoCajaForm(initial={'monto': monto_honorario})

    return render(request, 'juridico/registrar_pago_form.html', {
        'form_pago': form_pago,
        'cliente': cliente,
        'honorario_data': honorario_data
    })

def serializar_fechas(diccionario):
    for key, value in diccionario.items():
        if isinstance(value, datetime.date):
            diccionario[key] = value.isoformat()
    return diccionario
# -------------------------------
# GESTIONES
# -------------------------------
@login_required
@rol_requerido(*ROLES_CONTABLE)
def carga_gestiones(request):
    gestiones = GestioJuri.objects.all().order_by("-creado_en")

    # Filtros
    cliente_filtro = request.GET.get("cliente")
    fecha_filtro = request.GET.get("fecha")

    if cliente_filtro:
        gestiones = gestiones.filter(cliente__nombre__icontains=cliente_filtro)

    if fecha_filtro:
        gestiones = gestiones.filter(fecha__month=fecha_filtro)

    return render(request, "juridico/gestiones_list.html", {
        "gestiones": gestiones,
        "request": request
    })
@login_required
@rol_requerido(*ROLES_CONTABLE)
def nueva_gestion(request):
    if request.method == "POST":
        form = GestioJuriForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Gestión creada correctamente.")
            registrar_auditoria(request.user, form.instance, 'CREACION', None)

            return redirect("juridico:carga_gestiones")
    else:
        form = GestioJuriForm()
    return render(request, "juridico/gestiones_form.html", {"form": form})
@login_required
@rol_requerido(*ROLES_CONTABLE)
def lista_gestiones_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    # Filtramos las gestiones que pertenecen solo a este cliente
    gestiones = GestioJuri.objects.filter(cliente=cliente).order_by("-creado_en")
    return render(request, "juridico/gestiones_list.html", {
        "gestiones": gestiones,
        "cliente": cliente  # Enviamos el cliente a la plantilla
    })
@login_required
@rol_requerido(*ROLES_CONTABLE)
def eliminar_gestion(request, id):
    gest = get_object_or_404(GestioJuri, id=id)
    datos_viejos = model_to_dict(gest)
    if request.method == "POST":
        gest.delete()
        registrar_auditoria(request.user, gest, 'ELIMINACION', datos_viejos)
        messages.success(request, "Gestión eliminada correctamente.")
        return redirect("juridico:carga_gestiones")
    return render(request, "juridico/gestiones_confirm_delete.html", {"gest": gest})
