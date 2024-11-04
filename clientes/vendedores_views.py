import logging
from isoweek import Week
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from django.db.models.functions import ExtractWeek
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy,reverse
from django.views.generic import ListView,DeleteView
from django.utils.decorators import method_decorator
from datetime import datetime,timedelta,date

from .forms import *
from .models import *
from django.db.models import DateField
from django.db.models.functions import Cast, ExtractWeek
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


class ListarVendedores(LoginRequiredMixin,ListView):
    '''
        Lista todos los vendedores existentes en la base de datos.
        Args: request (HttpRequest): peticion HTTP.
    '''
    model = Vendedor
    template_name = 'vendedores/pagos.html'
    context_object_name = 'vendedores'
    paginate_by = 5



def get_week_of_year(fecha):
    """
    Calcula el número correcto de semana para una fecha dada.
    """
    return int(fecha.strftime('%V'))

def get_iso_calendar_data(fecha):
    """
    Retorna el año y número de semana ISO correctos para una fecha dada.
    La semana 1 es la primera semana que contiene un jueves del nuevo año.
    """
    año_iso, semana_iso, _ = fecha.isocalendar()
    return año_iso, semana_iso

def get_fechas_semana(fecha):
    """
    Calcula las fechas de inicio y fin de la semana para una fecha específica,
    considerando las reglas del calendario ISO.
    """
    # Obtener el día de la semana (1 = lunes, 7 = domingo)
    año_iso, semana_iso = get_iso_calendar_data(fecha)
    
    # Crear objeto Week de la librería isoweek
    semana = Week(año_iso, semana_iso)
    
    # Obtener lunes y domingo de la semana
    inicio_semana = semana.monday()
    fin_semana = semana.sunday()
    
    return inicio_semana, fin_semana

class PagosClientes(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'vendedores/pagos.html'
    context_object_name = 'pagos_por_semana'

    def get_queryset(self):
        vendedor_id = self.request.GET.get('vendedor')
        if not vendedor_id:
            return {}
        try:
            if vendedor_id:
                clientes = Cliente.objects.filter(vendedor_id=vendedor_id).prefetch_related(
                    Prefetch('pagos', queryset=Pago.objects.order_by('fecha_de_pago'))
                )

            pagos_por_semana = {}

            for cliente in clientes:
                try:
                    # Convertir la fecha de string a objeto date
                    if isinstance(cliente.fecha_de_firma, str):
                        fecha = datetime.strptime(cliente.fecha_de_firma, '%d-%b-%y').date()
                    else:
                        fecha = cliente.fecha_de_firma

                    # Obtener el año y semana ISO
                    año_iso, semana_iso = get_iso_calendar_data(fecha)
                    
                    # Calcular las fechas de inicio y fin de la semana
                    inicio_semana, fin_semana = get_fechas_semana(fecha)

                    # Si la semana incluye días de dos años diferentes,
                    # usar el año correcto según las reglas ISO
                    año_mostrar = año_iso

                    # Crear clave única para cada semana
                    clave = f"{año_iso}-{semana_iso}"

                    if clave not in pagos_por_semana:
                        pagos_por_semana[clave] = {
                            'clientes': [],
                            'fecha_inicio': inicio_semana,
                            'fecha_fin': fin_semana,
                            'semana': semana_iso,
                            'año': año_mostrar
                        }
                    pagos_por_semana[clave]['clientes'].append({
                        'cliente': cliente,
                        'pago': cliente.pagos.first()
                    })

                except (ValueError, AttributeError) as e:
                    logger.error(f"Error procesando fecha para cliente {cliente.id}: {e}")
                    continue

            # Ordenar por año y semana
            return dict(sorted(pagos_por_semana.items(), key=lambda x: (x[1]['año'], x[1]['semana'])))
            
        except Exception as e:
            messages.error(self.request, "Ocurrió un error al obtener los pagos.")
            logger.error(f"Error en PagosClientes.get_queryset: {e}")
            return {}

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
    
    context= {
        'form': form,
        'cliente': cliente,
        'Vendedor' : vendedor,
        'vendedor_id': vendedor_id,
    }
    return render(request, 'vendedores/agregar_editar_pago.html', context)


#eliminar vendedor + confirmacion para eliminar
@login_required
@administrador_required
def eliminar_vendedor(request, vendedor_id):
    vendedor = get_object_or_404(Vendedor, id=vendedor_id)
    if request.method == 'POST':
         vendedor.delete()
         return redirect('pagos')  # Redirecciona solo después de la confirmación
    
    return render(request, 'vendedores/pagos.html', {'object': vendedor})

