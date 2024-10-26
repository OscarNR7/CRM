from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from django.db.models.functions import ExtractWeek
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy,reverse
from django.views.generic import ListView
from django.utils.decorators import method_decorator

from .forms import *
from .models import *
from usuarios.decorators import gerente_required, administrador_required

@login_required
@administrador_required
def agregar_vendedor(request):
    '''
        Agrega un nuevo vendedor a la base de datos.
        Args: request (HttpRequest): peticion HTTP.
    '''
    if request.method == 'POST':
        vendedor_form = VendedorForm(request.POST)
        if vendedor_form.is_valid():
            vendedor_form.save() 
            return redirect('pagos')  
    else:
        vendedor_form = VendedorForm()

    return render(request, 'vendedores/pagos.html', {'vendedor_form': vendedor_form})  

class ListarVendedores(ListView):
    '''
        Lista todos los vendedores existentes en la base de datos.
        Args: request (HttpRequest): peticion HTTP.
    '''
    model = Vendedor
    template_name = 'vendedores/pagos.html'
    context_object_name = 'vendedores'
    paginate_by = 5

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
        context['vendedores'] = Vendedor.objects.all().order_by('nombre')

        # Lógica de paginación de vendedores
        vendedor_paginator = Paginator(context['vendedores'], 5)
        vendedor_page = self.request.GET.get('vendedor_page')
        context['vendedores'] = vendedor_paginator.get_page(vendedor_page)

        vendedor_id = self.request.GET.get('vendedor')
        if vendedor_id:
            context['vendedor_seleccionado'] = Vendedor.objects.get(id=vendedor_id)

        # Agregar el formulario de vendedores para el modal
        context['vendedor_form'] = VendedorForm()
        
        return context

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        
        # Lógica para manejar la petición AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string('vendedores/vendedor_modal_content.html', context, request=request)
            return HttpResponse(html)

        return super().get(request, *args, **kwargs)


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

@login_required
def informacion_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    return render(request, 'clientes/informacion_cliente.html', {'cliente': cliente, 'cliente_id': cliente_id})