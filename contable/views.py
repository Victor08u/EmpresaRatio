from django.shortcuts import render, redirect, get_object_or_404
from .models import DocConta, HonoConta, GestioConta
from .forms import DocContaForm, HonoContaForm, GestioContaForm
from caja.models import Caja, MovimientoCaja
from caja.forms import CajaAperturaForm, MovimientoCajaForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from core.decorators import rol_requerido
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from caja.forms import MovimientoCajaForm
from clientes.models import Cliente
import datetime
from datetime import date
from .models import VencimientoConta
from .forms import VencimientoContaForm
from core.models import ESTADO_DOCUMENTO, MODALIDAD_PAGO
from django.db.models import Q
from core.models import TimeStampedUserModel
from core.utils import registrar_auditoria
from django.forms.models import model_to_dict
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model




User = get_user_model()



ROLES_CONTABLE = ('Contador', 'Administrador', 'admin', 'adm')

@login_required
@rol_requerido(*ROLES_CONTABLE)
# -------------------------------
# PÁGINA PRINCIPAL DE CONTABLE
# -------------------------------
def contable_home(request):
    return render(request, "contable/home.html")


# -------------------------------
# DOCUMENTOS
# -------------------------------
@login_required
@rol_requerido(*ROLES_CONTABLE)
def carga_documentos(request):
    documentos = DocConta.objects.all().order_by("-creado_en")
    # Paginación (10 por página, podés cambiarlo)
    paginator = Paginator(documentos, 10)
    page_number = request.GET.get("page")
    documentos = paginator.get_page(page_number)

    # --- Filtro por cliente ---
    cliente_nombre = request.GET.get("cliente")
    if cliente_nombre:
        documentos = documentos.filter(cliente__nombre__icontains=cliente_nombre)

    # --- Filtro por estado ---
    estado = request.GET.get("estado")
    if estado:
        documentos = documentos.filter(estado=estado)

    return render(request, "contable/documentos_list.html", {
        "documentos": documentos,
        "clientes": Cliente.objects.all(),        # para el <select> de clientes
        "ESTADO_DOCUMENTO": ESTADO_DOCUMENTO,     # para el <select> de estado
        "cliente_nombre": cliente_nombre,         # mantener el input de texto
        "estado_seleccionado": estado,            # mantener seleccionado
    })
@login_required
@rol_requerido(*ROLES_CONTABLE)
def nuevo_documento(request):
    if request.method == "POST":
        form = DocContaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, form.instance, 'CREACION', None)
            messages.success(request, "Documento cargado correctamente.")

            return redirect("contable:carga_documentos")
    else:
        form = DocContaForm()
    return render(request, "contable/documentos_form.html", {"form": form})
@login_required
@rol_requerido(*ROLES_CONTABLE)
def lista_documentos_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    # Filtramos los documentos que pertenecen solo a este cliente
    documentos = DocConta.objects.filter(cliente=cliente).order_by("-creado_en")
    return render(request, "contable/documentos_list.html", {
        "documentos": documentos,
        "cliente": cliente  # Enviamos el cliente a la plantilla
    })
@login_required
@rol_requerido(*ROLES_CONTABLE)
def eliminar_documento(request, id):
    doc = get_object_or_404(DocConta, id=id)
    datos_viejos = model_to_dict(doc)
    if request.method == "POST":
        doc.delete()
        registrar_auditoria(request.user, doc, 'ELIMINACION', datos_viejos)
        messages.success(request, "Documento eliminado correctamente.")
        return redirect("contable:carga_documentos")
    return render(request, "contable/documentos_confirm_delete.html", {"doc": doc})


# -------------------------------
# HONORARIOS
# -------------------------------
@login_required
@rol_requerido(*ROLES_CONTABLE)
def carga_honorarios(request):
    honorarios = HonoConta.objects.all().order_by("-creado_en")

    # --- Filtro por cliente ---
    cliente_nombre = request.GET.get("cliente")
    if cliente_nombre:
        honorarios = honorarios.filter(cliente__nombre__icontains=cliente_nombre)

    return render(request, "contable/honorarios_list.html", {
        "honorarios": honorarios,
        "cliente_nombre": cliente_nombre,  # para mantener el valor en el input
    })
@login_required
@rol_requerido(*ROLES_CONTABLE)
def lista_honorarios_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    # Filtramos los honorarios que pertenecen solo a este cliente
    honorarios = HonoConta.objects.filter(cliente=cliente).order_by("-creado_en")
    return render(request, "contable/honorarios_list.html", {
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
        form = HonoContaForm(request.POST)
        if form.is_valid():
            honorario_data = form.cleaned_data
            
            if 'fecha' in honorario_data and isinstance(honorario_data['fecha'], datetime.date):
                honorario_data['fecha'] = honorario_data['fecha'].isoformat()
            
            honorario_data['monto'] = str(honorario_data['monto'])
            honorario_data['cliente_id'] = cliente_id
            request.session['honorario_temporal'] = honorario_data
            return redirect("contable:registrar_pago_honorario")
    else:
        form = HonoContaForm()
    
    return render(request, "contable/honorarios_form.html", {"form": form, "cliente": cliente})


@login_required
@rol_requerido(*ROLES_CONTABLE)
def nuevo_honorario(request):
    # Verificación de caja abierta
    if request.method == "POST":
        honorario_form = HonoContaForm(request.POST)
        if honorario_form.is_valid():
            honorario_data = honorario_form.cleaned_data
            honorario_data = serializar_fechas(honorario_data)

            if 'cliente' in honorario_data and honorario_data['cliente']:
                honorario_data['cliente_id'] = honorario_data['cliente'].pk
                del honorario_data['cliente']

            honorario_data['monto'] = str(honorario_data['monto'])
            request.session['honorario_temporal'] = honorario_data
            return redirect("contable:registrar_pago_honorario")

    else:
        honorario_form = HonoContaForm()

    return render(request, "contable/honorarios_form.html", {"form": honorario_form})
@login_required
@rol_requerido(*ROLES_CONTABLE)
def eliminar_honorario(request, id):
    honorario = get_object_or_404(HonoConta, pk=id)
    datos_viejos = model_to_dict(honorario)
    if request.method == "POST":
        honorario.delete()
        registrar_auditoria(request.user, honorario, 'ELIMINACION', datos_viejos)

        messages.success(request, "Honorario eliminado correctamente.")
    return redirect('contable:carga_honorarios')
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
            # Creamos y guardamos el Honorario
            honorario = HonoConta.objects.create(
                cliente=cliente,
                monto=monto_honorario,
                concepto=honorario_data['concepto'],
                periodo=periodo_actual,
            )

            # Caja abierta
            try:
                caja_abierta = Caja.objects.get(usuario=request.user, abierta=True)
            except Caja.DoesNotExist:
                messages.error(request, "No tienes ninguna caja abierta. Abre una caja antes de registrar pagos.")
                return redirect("caja:abrir_caja")  # o la URL que corresponda

            # Movimiento de caja
            movimiento = form_pago.save(commit=False)
            movimiento.tipo = "ING"  # siempre ingreso
            movimiento.concepto = f"Cobro por honorario: {honorario.concepto}"
            movimiento.caja_movimiento = caja_abierta
            movimiento.cliente = cliente
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
            return redirect('contable:lista_honorarios_cliente', cliente_id=cliente.id)
        else:
            print(form_pago.errors)  # 👈
            messages.error(request, f"Errores en el formulario: {form_pago.errors}")
            
    else:
        # Al cargar la página por primera vez, pre-llenamos el formulario con datos útiles
        form_pago = MovimientoCajaForm(initial={'monto': monto_honorario})

    return render(request, 'contable/registrar_pago_form.html', {
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
    gestiones = GestioConta.objects.all().order_by("-creado_en")

    # Filtro por cliente
    cliente = request.GET.get("cliente")
    if cliente:
        gestiones = gestiones.filter(cliente__nombre__icontains=cliente)

    return render(request, "contable/gestiones_list.html", {
        "gestiones": gestiones,
        "cliente": cliente,  # para mantener valor en el input del filtro
    })
@login_required
@rol_requerido(*ROLES_CONTABLE)
def nueva_gestion(request):
    if request.method == "POST":
        form = GestioContaForm(request.POST)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, form.instance, 'CREACION', None)
            messages.success(request, "Gestión cargada correctamente.")
            return redirect("contable:carga_gestiones")
    else:
        form = GestioContaForm()
    return render(request, "contable/gestiones_form.html", {"form": form})
@login_required
@rol_requerido(*ROLES_CONTABLE)
def lista_gestiones_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    # Filtramos las gestiones que pertenecen solo a este cliente
    gestiones = GestioConta.objects.filter(cliente=cliente).order_by("-creado_en")
    return render(request, "contable/gestiones_list.html", {
        "gestiones": gestiones,
        "cliente": cliente  # Enviamos el cliente a la plantilla
    })
@login_required
@rol_requerido(*ROLES_CONTABLE)
def eliminar_gestion(request, id):
    gest = get_object_or_404(GestioConta, id=id)
    datos_viejos = model_to_dict(gest)
    if request.method == "POST":
        gest.delete()
        registrar_auditoria(request.user, gest, 'ELIMINACION', datos_viejos)
        return redirect("contable:carga_gestiones")
    return render(request, "contable/gestiones_confirm_delete.html", {"gest": gest})

@login_required
@rol_requerido(*ROLES_CONTABLE)
def lista_vencimientos(request):
    vencimientos = VencimientoConta.objects.all().order_by("fecha_vencimiento")

    cliente = request.GET.get("cliente")
    tipo_documento = request.GET.get("tipo_documento")

    if cliente:
        vencimientos = vencimientos.filter(cliente__nombre__icontains=cliente)
    if tipo_documento:
        vencimientos = vencimientos.filter(tipo_documento=tipo_documento)

    # Obtener choices desde el campo del modelo
    tipo_choices = VencimientoConta._meta.get_field("tipo_documento").choices

    return render(request, "contable/vencimientos_list.html", {
        "vencimientos": vencimientos,
        "TIPO_DOCUMENTO": tipo_choices,
        "today": date.today(),
    })

@login_required
@rol_requerido(*ROLES_CONTABLE)
def nuevo_vencimiento(request):
    if request.method == "POST":
        form = VencimientoContaForm(request.POST)
        if form.is_valid():
            venc = form.save(commit=False)
            venc.usuario_alta = request.user
            venc.save()
            registrar_auditoria(request.user, venc, 'CREACION', None)
            messages.success(request, "Vencimiento creado correctamente.")
            return redirect("contable:lista_vencimientos")
    else:
        form = VencimientoContaForm()
    return render(request, "contable/vencimientos_form.html", {"form": form})

@login_required
@rol_requerido(*ROLES_CONTABLE)
def marcar_recibido(request, pk):
    venc = get_object_or_404(VencimientoConta, pk=pk)
    datos_viejos = model_to_dict(venc)
    if request.method == "POST":
        venc.mover_al_siguiente_mes()
        registrar_auditoria(request.user, venc, 'MODIFICACION', datos_viejos)
        messages.success(request, "Vencimiento actualizado al siguiente mes.")
        return redirect("contable:lista_vencimientos")
    return render(request, "contable/vencimiento_confirmar.html", {"vencimiento": venc})