import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Q
from django.views.generic import TemplateView, ListView, UpdateView, DeleteView, CreateView
from .models import Cliente
from .forms import ClienteForm
from usuarios.models import UserRole
from usuarios.decorators import gerente_required, administrador_required


# Create your views here.

#Renderiza la pagina de inicio
class Home(TemplateView):
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
        '''
            
        '''
        query = self.request.GET.get('search','')
        cliente = Cliente.objects.all()
        
        if query:

            terms = query.split()
            search_filters = Q()

            for term in terms:
                search_filters |= Q(nombre__icontains=term) |Q(curp__icontains=term)| Q(nss__icontains=term) |Q(direccion__icontains=term) | Q(colonia__icontains=term) | Q(telefono__icontains=term) 
                
            cliente = cliente.filter(search_filters)
        return cliente

#funcion para agregar un nuevo cliente
@login_required
@administrador_required
def agregar_cliente(request):
    '''
        Agrega un nuevo cliente a la base de datos
        Args: request (HttpRequest): peticion HTTP
    '''
    formulario = ClienteForm(request.POST or None, request.FILES or None)
    if formulario.is_valid():
        formulario.save()
        return redirect('clientes')
    return render(request, 'clientes/agregar.html',{'formulario':formulario})

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
    return render(request, 'clientes/editar.html',{'formulario':formulario})
    
#funcion para eliminar un cliente existente 
@method_decorator([administrador_required], name='dispatch')
class EliminarCliente(LoginRequiredMixin,DeleteView):
    '''
    Elimina un cliente existente en la base de datos
    Args: request (HttpRequest): peticion HTTP, id (int): id del cliente
    '''
    model = Cliente
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

#------------------------------------------------LOGIN----------------------------------------------------------------

#Funcion para registrar un usuario al sistema


