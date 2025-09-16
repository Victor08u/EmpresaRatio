from django.shortcuts import render, redirect, get_object_or_404
from .models import DocAdmin, HonoAdmin, GestioAdmin
from .forms import DocumentoAdminForm, HonorarioAdminForm, GestionAdminForm
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
from contable.models import HonoConta
from core.models import PerfilUsuario
from django.contrib.auth import get_user_model
from core.models import ESTADO_DOCUMENTO, MODALIDAD_PAGO
from core.utils import registrar_auditoria
from django.forms.models import model_to_dict




User = get_user_model()

ROLES_CONTABLE = ('Contador', 'Administrador', 'admin', 'adm')

# -------------------------------
# PÁGINA PRINCIPAL
# -------------------------------
def administrativo_home(request):
    return render(request, "administrativo/home.html")

# -------------------------------
# DOCUMENTOS
# -------------------------------
def documentos_admin(request):
    documentos = DocAdmin.objects.all().order_by("-creado_en")

    # Filtros
    cliente_filtro = request.GET.get("cliente")
    estado_filtro = request.GET.get("estado")

    if cliente_filtro:
        documentos = documentos.filter(cliente__nombre__icontains=cliente_filtro)
    if estado_filtro:
        documentos = documentos.filter(estado=estado_filtro)

    return render(request, "administrativo/documentos_list.html", {
        "documentos": documentos,
        "ESTADO_DOCUMENTO": ESTADO_DOCUMENTO,
        "request": request
    })

def nuevo_documento_admin(request):
    if request.method == "POST":
        form = DocumentoAdminForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, form.instance, 'CREACION', None)
            return redirect("administrativo:documentos")
    else:
        form = DocumentoAdminForm()
    return render(request, "administrativo/documentos_form.html", {"form": form})

def eliminar_documento_admin(request, id):
    doc = get_object_or_404(DocAdmin, id=id)
    datos_viejos = model_to_dict(doc)

    if request.method == "POST":
        doc.delete()
        messages.success(request, "Documento eliminado correctamente.")
        registrar_auditoria(request.user, doc, 'ELIMINACION', datos_viejos)
        return redirect("administrativo:documentos")
    return render(request, "administrativo/documentos_confirm_delete.html", {"doc": doc})

# -------------------------------
# HONORARIOS
# -------------------------------
@login_required
@rol_requerido(*ROLES_CONTABLE)
def carga_honorarios(request):
    honorarios = HonoAdmin.objects.all().order_by("-creado_en")

    # Filtrar por cliente si se ingresa algo
    cliente_query = request.GET.get("cliente")
    if cliente_query:
        honorarios = honorarios.filter(cliente__nombre__icontains=cliente_query)

    # Filtrar por modalidad si se selecciona algo
    modalidad_query = request.GET.get("modalidad")
    if modalidad_query:
        honorarios = honorarios.filter(modalidad=modalidad_query)

    return render(request, "administrativo/honorarios_list.html", {
        "honorarios": honorarios,
        "MODALIDAD_PAGO": MODALIDAD_PAGO
    })
@login_required
@rol_requerido(*ROLES_CONTABLE)
def lista_honorarios_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    # Filtramos los honorarios que pertenecen solo a este cliente
    honorarios = HonoAdmin.objects.filter(cliente=cliente).order_by("-creado_en")
    return render(request, "administrativo/honorarios_list.html", {
        "honorarios": honorarios,
        "cliente": cliente  # Enviamos el cliente a la plantilla
    })


@login_required
@rol_requerido(*ROLES_CONTABLE)
def nuevo_honorario_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    # Verificación de caja abierta
     # Verificación de caja abierta
    if not Caja.objects.filter(creado_por=request.user, abierta=True).exists():
        messages.error(request, "Error: No tiene una caja abierta. Por favor, abra una para continuar.")
        return redirect("caja:abrir_caja")

    if request.method == "POST":
        form = HonorarioAdminForm(request.POST)
        if form.is_valid():
            honorario_data = form.cleaned_data
            
            if 'fecha' in honorario_data and isinstance(honorario_data['fecha'], datetime.date):
                honorario_data['fecha'] = honorario_data['fecha'].isoformat()
            
            honorario_data['monto'] = str(honorario_data['monto'])
            honorario_data['cliente_id'] = cliente_id
            request.session['honorario_temporal'] = honorario_data
            return redirect("administrativo:registrar_pago_honorario")
    else:
        form = HonorarioAdminForm()

    return render(request, "administrativo/honorarios_form.html", {"form": form, "cliente": cliente})


@login_required
@rol_requerido(*ROLES_CONTABLE)
def nuevo_honorario(request):
    # Verificación de caja abierta
    if request.method == "POST":
        honorario_form = HonorarioAdminForm(request.POST)

        if honorario_form.is_valid():
            honorario_data = honorario_form.cleaned_data
            honorario_data = serializar_fechas(honorario_data)

            if 'cliente' in honorario_data and honorario_data['cliente']:
                honorario_data['cliente_id'] = honorario_data['cliente'].pk
                del honorario_data['cliente']

            honorario_data['monto'] = str(honorario_data['monto'])
            request.session['honorario_temporal'] = honorario_data
            return redirect("administrativo:registrar_pago_honorario")

    else:
        honorario_form = HonorarioAdminForm()

    return render(request, "administrativo/honorarios_form.html", {"form": honorario_form})
@login_required
@rol_requerido(*ROLES_CONTABLE)
def eliminar_honorario(request, id):
    honorario = get_object_or_404(HonoAdmin, pk=id)
    datos_viejos = model_to_dict(honorario)
    if request.method == "POST":
        honorario.delete()
        registrar_auditoria(request.user, honorario, 'ELIMINACION', datos_viejos)

        messages.success(request, "Honorario eliminado correctamente.")
    return redirect('administrativo:carga_honorarios')
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
            honorario = HonoAdmin.objects.create(
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
            registrar_auditoria(request.user, movimiento, 'ALTA', None)
            registrar_auditoria(request.user, honorario, 'ALTA', None)
            # D. ¡MUY IMPORTANTE! Limpiamos la sesión
            del request.session['honorario_temporal']
            
            # Aquí llamarías a la auditoría para ambos modelos
            # registrar_auditoria(request.user, honorario, 'ALTA')
            # registrar_auditoria(request.user, movimiento, 'ALTA')

            messages.success(request, "¡Honorario y pago registrados exitosamente!")
            return redirect('administrativo:lista_honorarios_cliente', cliente_id=cliente.id)
        else:
            print(form_pago.errors)  # 👈
            messages.error(request, f"Errores en el formulario: {form_pago.errors}")
            
    else:
        # Al cargar la página por primera vez, pre-llenamos el formulario con datos útiles
        form_pago = MovimientoCajaForm(initial={'monto': monto_honorario})

    return render(request, 'administrativo/registrar_pago_form.html', {
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
def gestiones_admin(request):
    gestiones = GestioAdmin.objects.all().order_by("-creado_en")

    # Filtros
    cliente_filtro = request.GET.get("cliente")
    fecha_filtro = request.GET.get("fecha")

    if cliente_filtro:
        gestiones = gestiones.filter(cliente__nombre__icontains=cliente_filtro)

    if fecha_filtro:
        gestiones = gestiones.filter(fecha=fecha_filtro)

    return render(request, "administrativo/gestiones_list.html", {
        "gestiones": gestiones,
        "request": request
    })


def nueva_gestion_admin(request):
    if request.method == "POST":
        form = GestionAdminForm(request.POST)

        if form.is_valid():

            form.save()
            registrar_auditoria(request.user, form.instance, 'CREACION', None)
            return redirect("administrativo:gestiones")
    else:
        form = GestionAdminForm()
    return render(request, "administrativo/gestiones_form.html", {"form": form})

def eliminar_gestion_admin(request, id):
    gestion = get_object_or_404(GestioAdmin, id=id)
    datos_viejos = model_to_dict(gestion)
    if request.method == "POST":
        gestion.delete()
        registrar_auditoria(request.user, gestion, 'ELIMINACION', datos_viejos)
        return redirect("administrativo:gestiones")
    return render(request, "administrativo/gestiones_confirm_delete.html", {"gestion": gestion})    

def editar_gestion_admin(request, id):
    gestion = get_object_or_404(GestioAdmin, id=id)
    datos_viejos = model_to_dict(gestion)
    if request.method == "POST":
        form = GestionAdminForm(request.POST, instance=gestion)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, gestion, 'MODIFICACION', datos_viejos)
            return redirect("administrativo:gestiones")
    else:
        form = GestionAdminForm(instance=gestion)
    return render(request, "administrativo/gestiones_form.html", {"form": form, "editar": True})


