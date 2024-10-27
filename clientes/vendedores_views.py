import logging
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
from django.views.generic import ListView,DeleteView
from django.utils.decorators import method_decorator
from datetime import datetime,timedelta

from .forms import *
from .models import *
from django.db.models import DateField
from django.db.models.functions import Cast
from usuarios.decorators import gerente_required, administrador_required

logger = logging.getLogger('clientes')

@login_required
@administrador_required
def agregar_vendedor(request):
    '''
        Agrega un nuevo vendedor a la base de datos.
        Args: request (HttpRequest): peticion HTTP.
    '''
    try:
        if request.method == 'POST':
            vendedor_form = VendedorForm(request.POST)
            if vendedor_form.is_valid():
                vendedor_form.save()
                return redirect('pagos')
    except Exception as e:
        messages.error(request, "Error al agregar el vendedor.")
        logger.error(f"Error en agregar_vendedor: {e}")  # Registro del error
    return render(request, 'vendedores/pagos.html', {'vendedor_form': VendedorForm()})  

class ListarVendedores(ListView):
    '''
        Lista todos los vendedores existentes en la base de datos.
        Args: request (HttpRequest): peticion HTTP.
    '''
    model = Vendedor
    template_name = 'vendedores/pagos.html'
    context_object_name = 'vendedores'
    paginate_by = 5

def get_fechas_semana(numero_semana, año):
    """
    Calcula las fechas de inicio y fin de una semana específica.
    """
    # Crear una fecha para el primer día del año
    primer_dia_año = datetime(año, 1, 1)
    
    # Ajustar al primer día de la primera semana
    while primer_dia_año.weekday() != 0:  # 0 es lunes
        primer_dia_año += timedelta(days=1)
    
    # Calcular el inicio de la semana deseada
    inicio_semana = primer_dia_año + timedelta(weeks=numero_semana-1)
    fin_semana = inicio_semana + timedelta(days=6)
    
    return inicio_semana, fin_semana

class PagosClientes(ListView):
    model = Cliente
    template_name = 'vendedores/pagos.html'
    context_object_name = 'pagos_por_semana'

    def get_queryset(self):
        try:
            vendedor_id = self.request.GET.get('vendedor')
            if vendedor_id:
                clientes = Cliente.objects.filter(vendedor_id=vendedor_id).prefetch_related(
                    Prefetch('pagos', queryset=Pago.objects.order_by('fecha_de_pago'))
                ).annotate(
                    fecha_de_firma_date=Cast('fecha_de_firma', DateField()),  # convierte a DateField
                    semana=ExtractWeek('fecha_de_firma_date')  # usa el campo convertido para extraer la semana
                ).order_by('semana', 'fecha_de_firma_date')

            pagos_por_semana = {}
            año_actual = datetime.now().year

            for cliente in clientes:
                semana = cliente.semana
                if semana not in pagos_por_semana:
                    fecha_inicio, fecha_fin = get_fechas_semana(semana, año_actual)
                    pagos_por_semana[semana] = {
                        'clientes': [],
                        'fecha_inicio': fecha_inicio,
                        'fecha_fin': fecha_fin
                    }
                pagos_por_semana[semana]['clientes'].append({
                    'cliente': cliente,
                    'pago': cliente.pagos.first()
                })
            return dict(sorted(pagos_por_semana.items()))
        except Exception as e:
            messages.error(self.request, "Ocurrió un error al obtener los pagos.")
            logger.error(f"Error en PagosClientes.get_queryset: {e}")  # Registro del error
            return {}  # Registro del error

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vendedores'] = Vendedor.objects.all().order_by('nombre')

        # Lógica de paginación de vendedores
        vendedores_paginados = context['vendedores']
        vendedor_paginator = Paginator(vendedores_paginados, 5)
        vendedor_page = self.request.GET.get('vendedor_page')
        context['vendedores_paginados'] = vendedor_paginator.get_page(vendedor_page)

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

#eliminar vendedor + confirmacion para eliminar
@login_required
@administrador_required
def eliminar_vendedor(request, vendedor_id):
    vendedor = get_object_or_404(Vendedor, id=vendedor_id)
    if request.method == 'POST':
         vendedor.delete()
         return redirect('pagos')  # Redirecciona solo después de la confirmación
    
    return render(request, 'vendedores/pagos.html', {'object': vendedor})

