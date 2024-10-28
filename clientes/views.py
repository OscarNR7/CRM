import os
import logging
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q, Prefetch
from django.db.models.functions import ExtractWeek
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy,reverse
from django.views.generic import TemplateView, ListView, UpdateView, DeleteView, CreateView, FormView
from django.utils.decorators import method_decorator


from .forms import *
from .models import *
from usuarios.decorators import gerente_required, administrador_required
from usuarios.models import UserRole

logger = logging.getLogger('clientes')

# Create your views here.
#Renderiza la pagina de inicio
class Home(LoginRequiredMixin,TemplateView):
    '''
    Renderiza la pagina de inicio con los detalles de la empresa
     Args: request (HttpRequest): peticion HTTP
    '''
    template_name = 'home.html'

#Calse que muestra la pagina de la lista de clientes y aplicar las busqueda de los clientes
class ListarClientes(LoginRequiredMixin,ListView):
    '''
    Lista todos los clientes
    Args: request (HttpRequest): peticion HTTP

    '''
    model = Cliente
    template_name = 'clientes/clientes.html'
    context_object_name = 'clientes'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('search', '').strip()
        queryset = Cliente.objects.all()
        
        if query:
            terms = query.split()
            search_filters = Q()

            for term in terms:
                terms = query.split()
                if term:
                    search_filters |= ( Q(nombre__icontains=term) |
                    Q(curp__icontains=term)| 
                    Q(nss__icontains=term) |
                    Q(direccion__icontains=term) | 
                    Q(colonia__icontains=term) | 
                    Q(telefono__icontains=term)  | 
                    Q(vendedor__nombre__icontains=term)
                    )
            queryset = queryset.filter(search_filters)
        return queryset.distinct()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_term'] = self.request.GET.get('search', '')
        return context
    
#funcion para agregar un nuevo cliente
@login_required
@administrador_required
def agregar_cliente(request):
    '''
        Agrega un nuevo cliente a la base de datos
        Args: request (HttpRequest): peticion HTTP
    '''
    formulario = ClienteForm(request.POST or None, request.FILES or None)
    try:
        if formulario.is_valid():
            formulario.save()
            if 'guardar_y_agregar' in request.POST:
                return redirect('agregar')
            return redirect('clientes')
    except IntegrityError as e:
        messages.error(request, f"Error al agregar cliente: {e}")
    except Exception as e:
        messages.error(request, "Ocurrió un error inesperado.")
        logger.error(f"Error en agregar_cliente: {e}")  # Registro del error
    return render(request, 'clientes/agregar.html', {'formulario': formulario, 'modo': 'agregar'})

#funcion para editar un cliente existente
@login_required
@administrador_required
def editar_cliente(request, id):
    '''
        Edita un cliente existente en la base de datos
        Args: request (HttpRequest): peticion HTTP, id (int): id del cliente
    '''
    cliente = get_object_or_404(Cliente,id=id)
    formulario = ClienteForm(request.POST or None, request.FILES or None, instance=cliente)
    if formulario.is_valid() and request.POST:
        formulario.save()
        return redirect('clientes')
    return render(request, 'clientes/editar.html',{'formulario':formulario, 'modo':'editar'})
    
#funcion para eliminar un cliente existente 
@method_decorator([administrador_required], name='dispatch')
class EliminarCliente(LoginRequiredMixin,DeleteView):
    '''
    Elimina un cliente existente en la base de datos
    Args: request (HttpRequest): peticion HTTP, id (int): id del cliente
    '''
    model = Cliente
    template_name = 'clientes/cliente_confirm_delete.html'
    success_url = reverse_lazy('clientes')
    def delete(self, request, *args, **kwargs):
        # Obtener el objeto cliente que se va a eliminar
        cliente = self.get_object()
        
        # Si el cliente tiene una imagen asociada, eliminarla del sistema de archivos
        if cliente.imagen:
            imagen_path = os.path.join(settings.MEDIA_ROOT, cliente.imagen.name)
            if os.path.isfile(imagen_path):
                os.remove(imagen_path)
        
        # Eliminar el cliente
        return super().delete(request, *args, **kwargs)
    
@login_required
def informacion_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    return render(request, 'clientes/informacion_cliente.html', {'cliente': cliente, 'cliente_id': cliente_id})


from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.conf import settings

def create_admin(request):
    # Token simple para validar - debes configurarlo en tus variables de entorno de Render
    token = request.GET.get('token')
    if token != settings.ADMIN_SECRET_TOKEN:  # Configura esto en tus variables de entorno
        return HttpResponse('No autorizado', status=403)
    
    try:
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            usuario = User.objects.create_superuser(
                username='oscarnr',
                email='oscar@gmail.com',
                password='12345'  # Cámbiala inmediatamente después
            )
            return HttpResponse('Superusuario creado con éxito!')
        return HttpResponse('El superusuario ya existe')
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}')