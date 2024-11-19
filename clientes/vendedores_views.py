# Importaciones estándar de Python
import logging
from datetime import datetime, timedelta, date

# Librerías de terceros
from isoweek import Week

# Importaciones de Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch, DateField
from django.db.models.functions import Cast, ExtractWeek
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DeleteView
from django.db import IntegrityError, transaction

# Importaciones de la aplicación local
from .forms import *
from .models import *
from usuarios.decorators import gerente_required, administrador_required
from usuarios.views import log_user_activity


logger = logging.getLogger('clientes')

@login_required
@administrador_required
def agregar_vendedor(request):
    try:
        if request.method == 'POST':
            vendedor_form = VendedorForm(request.POST)
            if vendedor_form.is_valid():
                vendedor = vendedor_form.save()
                
                # Si se asignó un usuario, registrarlo en el log
                if vendedor.usuario:
                    log_user_activity(
                        user=request.user,
                        action="Agregó",
                        target=f"Al vendedor: {vendedor.nombre} y lo asignó al usuario: {vendedor.usuario.username}",
                        app_name="vendedores"
                    )
                else:
                    log_user_activity(
                        user=request.user,
                        action="Agregó",
                        target=f"Al vendedor: {vendedor.nombre}",
                        app_name="vendedores"
                    )
                    
                messages.success(request, "Vendedor agregado exitosamente.")
                return redirect('pagos')
            else:
                messages.error(request, "Por favor corrija los errores en el formulario.")
                
    except Exception as e:
        messages.error(request, "Error al agregar el vendedor.")
        logger.error(f"Error en agregar_vendedor: {e}")
    
    return render(request, 'vendedores/pagos.html', {'vendedor_form': VendedorForm()})

@login_required
@administrador_required
def editar_vendedor(request, vendedor_id):
    vendedor = get_object_or_404(Vendedor.objects.select_related('usuario'), id=vendedor_id)
    
    if request.method == 'POST':
        form = VendedorForm(request.POST, instance=vendedor)
        if form.is_valid():
            try:
                with transaction.atomic():
                    vendedor = form.save()
                    log_user_activity(
                        user=request.user,
                        action="Editó",
                        target=f"Al vendedor: {vendedor.nombre}",
                        app_name="vendedores"
                    )
                    messages.success(request, f"Vendedor {vendedor.nombre} actualizado correctamente.")
            except Exception as e:
                messages.error(request, f"Error al actualizar el vendedor: {e}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        return redirect('pagos')  # Cambia a la URL correspondiente

    else:
        form = VendedorForm(instance=vendedor)
        return HttpResponse(form.as_p())

class ListarVendedores(LoginRequiredMixin, ListView):
    model = Vendedor
    template_name = 'vendedores/pagos.html'
    context_object_name = 'vendedores'
    paginate_by = 5

    def get_queryset(self):
        return Vendedor.objects.select_related('usuario').all()

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
        user_role = self.request.user.userrole.role
        vendedor_id = self.request.GET.get('vendedor')
        
        try:
            if user_role == 'vendedor':
                # Si es vendedor, verificar primero si existe
                try:
                    vendedor = Vendedor.objects.get(usuario=self.request.user)
                    clientes = Cliente.objects.filter(vendedor=vendedor).prefetch_related(
                        Prefetch('pagos', queryset=Pago.objects.order_by('fecha_de_pago'))
                    )
                except Vendedor.DoesNotExist:
                    return {}  # Retornar diccionario vacío si no existe el vendedor
            elif user_role in ['gerente', 'administrador']:
                # Mantener la lógica actual para gerentes y administradores
                if vendedor_id:
                    clientes = Cliente.objects.filter(vendedor_id=vendedor_id).prefetch_related(
                        Prefetch('pagos', queryset=Pago.objects.order_by('fecha_de_pago'))
                    )
                else:
                    clientes = Cliente.objects.all().prefetch_related(
                        Prefetch('pagos', queryset=Pago.objects.order_by('fecha_de_pago'))
                    )
            else:
                return {}

            # Si no hay clientes, retornar diccionario vacío
            if not clientes.exists():
                return {}

            pagos_por_semana = {}

            for cliente in clientes:
                try:
                    # Convertir la fecha de string a objeto date si es necesario
                    if isinstance(cliente.fecha_de_firma, str):
                        fecha = datetime.strptime(cliente.fecha_de_firma, '%d-%b-%y').date()
                    else:
                        fecha = cliente.fecha_de_firma

                    # Obtener el año y semana ISO
                    año_iso, semana_iso = get_iso_calendar_data(fecha)

                    # Calcular las fechas de inicio y fin de la semana
                    inicio_semana, fin_semana = get_fechas_semana(fecha)

                    # Crear clave única para cada semana
                    clave = f"{año_iso}-{semana_iso}"

                    if clave not in pagos_por_semana:
                        pagos_por_semana[clave] = {
                            'clientes': [],
                            'fecha_inicio': inicio_semana,
                            'fecha_fin': fin_semana,
                            'semana': semana_iso,
                            'año': año_iso
                        }
                    pagos_por_semana[clave]['clientes'].append({
                        'cliente': cliente,
                        'pago': cliente.pagos.first()
                    })

                except (ValueError, AttributeError) as e:
                    logger.error(f"Error procesando fecha para cliente {cliente.id}: {e}")
                    continue

            return dict(sorted(pagos_por_semana.items(), key=lambda x: (x[1]['año'], x[1]['semana'])))
        except Exception as e:
            messages.error(self.request, "Ocurrió un error al obtener los pagos.")
            logger.error(f"Error en PagosClientes.get_queryset: {e}")
            return {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_role = self.request.user.userrole.role

        if user_role in ['gerente', 'administrador']:
            # Solo mostrar el selector de vendedores para gerentes y administradores
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
        elif user_role == 'vendedor':
            try:
                vendedor = Vendedor.objects.get(usuario=self.request.user)
                context['vendedor_seleccionado'] = vendedor
            except Vendedor.DoesNotExist:
                context['vendedor_seleccionado'] = None
                messages.warning(self.request, "No se encontró información del vendedor.")
            
        return context

@login_required
@administrador_required
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

            accion = "Editó o Agregó"
            log_user_activity(
                user=request.user,
                action=accion,
                target=f"El pago del cliente: {cliente.nombre}",
                app_name="pagos"
            )
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
@gerente_required
def eliminar_vendedor(request, vendedor_id):
    vendedor = get_object_or_404(Vendedor, id=vendedor_id)
    if request.method == 'POST':
         log_user_activity(
            user=request.user,
            action="Eliminó",
            target=f"vendedor: {vendedor.nombre}",
            app_name="clientes"
        )
         vendedor.delete()
         return redirect('pagos')  # Redirecciona solo después de la confirmación
    
    return render(request, 'vendedores/pagos.html', {'object': vendedor})

