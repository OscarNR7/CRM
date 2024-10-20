import os
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vendedor_form'] = VendedorForm()
        

        vendedores = Vendedor.objects.all()
        vendedor_paginator = Paginator(vendedores, 5)
        vendedor_page = self.request.GET.get('vendedor_page')
        context['vendedores'] = vendedor_paginator.get_page(vendedor_page)
        return context
    
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
    
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string('vendedores/vendedor_modal_content.html', context, request=request)
            return HttpResponse(html)
        return super().get(request, *args, **kwargs)

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

#------------------------------------------------Vendedores----------------------------------------------------------------
def agregar_vendedor(request):
    '''
        Agrega un nuevo vendedor a la base de datos.
        Args: request (HttpRequest): peticion HTTP.
    '''
    if request.method == 'POST':
        vendedor_form = VendedorForm(request.POST)
        if vendedor_form.is_valid():
            vendedor_form.save() 
            return redirect('clientes')  
    else:
        vendedor_form = VendedorForm()

    return render(request, 'vendedores/clientes.html', {'vendedor_form': vendedor_form})  

class ListarVendedores(ListView):
    '''
        Lista todos los vendedores existentes en la base de datos.
        Args: request (HttpRequest): peticion HTTP.
    '''
    model = Vendedor
    template_name = 'vendedores/clientes.html'
    context_object_name = 'vendedores'
    paginate_by = 10

class PagosClientes(ListView):
    model = Cliente
    template_name = 'vendedores/pagos.html'
    context_object_name = 'pagos_por_semana'

    def get_queryset(self):
        vendedor_id = self.request.GET.get('vendedor')
        if vendedor_id:
            clientes = Cliente.objects.filter(vendedor_id=vendedor_id).prefetch_related(
                Prefetch('pagos', queryset=Pago.objects.order_by('fecha_de_pago'))
            ).annotate(semana=ExtractWeek('fecha_de_firma'))

            pagos_por_semana = {}
            for cliente in clientes:
                semana = cliente.semana
                if semana not in pagos_por_semana:
                    pagos_por_semana[semana] = []
                pagos_por_semana[semana].append({
                    'cliente': cliente,
                    'pago': cliente.pagos.first()  # Asumiendo que queremos mostrar el último pago
                })

            return pagos_por_semana
        return {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vendedores'] = Vendedor.objects.all()
        vendedor_id = self.request.GET.get('vendedor')
        if vendedor_id:
            context['vendedor_seleccionado'] = Vendedor.objects.get(id=vendedor_id)
        return context

@login_required
def agregar_editar_pago(request, cliente_id,vendedor_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    vendedor = get_object_or_404(Vendedor, id=vendedor_id)
    pago = Pago.objects.filter(cliente=cliente).first()
    
    if request.method == 'POST':
        form = PagoForm(request.POST, instance=pago)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.cliente = cliente
            pago.save()
            return redirect(reverse('pagos') + f'?vendedor={vendedor_id}')
    else:
        form = PagoForm(instance=pago)
    
    return render(request, 'vendedores/agregar_editar_pago.html', {
        'form': form,
        'cliente': cliente,
        'Vendedor' : vendedor
    })