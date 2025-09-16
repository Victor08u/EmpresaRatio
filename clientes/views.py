from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cliente
from .forms import ClienteForm
from django.shortcuts import render
from django.contrib import messages
from django.forms.models import model_to_dict
from core.utils import registrar_auditoria

def index(request):
    return render(request, 'index.html')

@login_required
def lista_clientes(request):
    # Obtener todos los clientes inicialmente
    clientes = Cliente.objects.all()

    # Obtener los parámetros de búsqueda del request
    query_nombre = request.GET.get('nombre')
    query_ruc_ci = request.GET.get('ruc_ci')
    query_estado = request.GET.get('estado')

    # Aplicar filtros
    if query_nombre:
        clientes = clientes.filter(nombre__icontains=query_nombre)
    
    if query_ruc_ci:
        clientes = clientes.filter(ruc_ci__icontains=query_ruc_ci)
        
    if query_estado == 'activo':
        clientes = clientes.filter(activo=True)
    elif query_estado == 'inactivo':
        clientes = clientes.filter(activo=False)

    return render(request, 'clientes/lista.html', {'clientes': clientes})

@login_required
def nuevo_cliente(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente creado.")
            registrar_auditoria(request.user, form.instance, 'CREACION', None)

            return redirect('clientes:listar')
    else:
        form = ClienteForm()
    return render(request, 'clientes/formulario.html', {'form': form, 'accion': 'Nuevo'})

@login_required
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    # 1. Capturamos los datos viejos ANTES de cualquier cambio
    datos_viejos = model_to_dict(cliente)
    if request.method == "POST":
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()

             # 2. Llamamos a la función de auditoría DESPUÉS de guardar
            registrar_auditoria(request.user, cliente_actualizado, 'MODIFICACION', datos_viejos)
            messages.success(request, "Cliente actualizado.")
            return redirect('clientes:listar')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/formulario.html', {'form': form, 'accion': 'Editar'})

@login_required
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    datos_viejos = model_to_dict(cliente)
    
    if request.method == "POST":
        cliente.delete()
        messages.success(request, "Cliente eliminado.")
        # Registrar auditoría de eliminación
        registrar_auditoria(request.user, cliente, 'ELIMINACION', datos_viejos)

        return redirect('clientes:listar')
    return render(request, 'clientes/eliminar.html', {'cliente': cliente})

@login_required
def inactivar_cliente(request, id):
    # Aseguramos que el usuario esté autenticado antes de proceder
    if not request.user.is_authenticated:
        # Puedes redirigirlo a la página de inicio de sesión o mostrar un error
        return redirect('login') # O la URL de tu página de login

    cliente = get_object_or_404(Cliente, id=id)

    # Captura los datos viejos antes del cambio
    datos_viejos = model_to_dict(cliente)

    # Inactiva el cliente y guarda el cambio
    cliente.activo = False
    cliente.save()

    # Llama a la función de auditoría con los argumentos correctos
    registrar_auditoria(
        request.user,
        cliente,
        'INACTIVACION',
        datos_viejos,
    )

    messages.success(request, f"El cliente {cliente.nombre} ha sido inactivado.")
    return redirect('clientes:listar')

def activar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    datos_viejos = model_to_dict(cliente)
    
    cliente.activo = True
    cliente.save()
    
    # Registra la auditoría
    registrar_auditoria(
        request.user, 
        cliente, 
        'ACTIVACION', 
        datos_viejos
    )
    
    messages.success(request, f"El cliente {cliente.nombre} ha sido activado.")
    return redirect('clientes:listar')