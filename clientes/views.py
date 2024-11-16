# Importaciones de librerías estándar de Python
import os
import logging
from datetime import datetime

# Importaciones de Django
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
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, ListView, UpdateView, DeleteView, CreateView, FormView

# Importaciones de la aplicación local
from .forms import *
from .models import *
from usuarios.decorators import gerente_required, administrador_required
from usuarios.views import log_user_activity

logger = logging.getLogger('clientes')

# Create your views here.
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
        orden = self.request.GET.get('orden', 'nombre')  # Orden por defecto es por nombre
        queryset = Cliente.objects.all()
        
        if self.request.user.userrole.role in ['gerente', 'administrador']:
            queryset = Cliente.objects.all()
        else:
            # Obtener el vendedor asociado al usuario actual
            try:
                vendedor = self.request.user.vendedor
                queryset = Cliente.objects.filter(vendedor=vendedor)
            except Vendedor.DoesNotExist:
                queryset = Cliente.objects.none()

        # Filtrado de búsqueda
        if query:
            terms = query.split()
            search_filters = Q()
            for term in terms:
                if term:
                    search_filters |= (Q(nombre__icontains=term) |
                                       Q(curp__icontains=term) |
                                       Q(nss__icontains=term) |
                                       Q(direccion__icontains=term) |
                                       Q(colonia__icontains=term) |
                                       Q(vendedor__nombre__icontains=term))
            queryset = queryset.filter(search_filters)
        
        # Ordenar por el criterio seleccionado
        if orden == 'id':
            queryset = queryset.order_by('id')
        else:
            queryset = queryset.order_by('nombre')
        
        return queryset.distinct()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_term'] = self.request.GET.get('search', '')
        context['orden'] = self.request.GET.get('orden', 'nombre')
        return context
   
#funcion para agregar un nuevo cliente
@login_required
@administrador_required
def agregar_cliente(request):
    if request.method == 'POST':
        formulario = ClienteForm(request.POST, request.FILES)
        telefono_formset = TelefonoFormSet(request.POST, prefix='telefonos')
        
        if formulario.is_valid() and telefono_formset.is_valid():
            try:
                # Guardar el cliente
                cliente = formulario.save()

                
                # Guardar los teléfonos
                for telefono_form in telefono_formset:
                    if telefono_form.cleaned_data and not telefono_form.cleaned_data.get('DELETE', False):
                        numero = telefono_form.cleaned_data.get('numero')
                        if numero and numero.strip():
                            Telefono.objects.create(cliente=cliente, numero=numero)

                log_user_activity(
                    user=request.user,
                    action="Agregó",
                    target=f"cliente: {cliente.nombre}-{cliente.curp}",
                    app_name="clientes"
                )
                messages.success(request, 'Cliente agregado exitosamente.')
                if 'guardar_y_agregar' in request.POST:
                    return redirect('agregar')
                return redirect('clientes')
                
            except Exception as e:
                messages.error(request, f"Error al agregar cliente: {str(e)}")
                logger.error(f"Error en agregar_cliente: {e}")
    else:
        formulario = ClienteForm()
        telefono_formset = TelefonoFormSet(prefix='telefonos', queryset=Telefono.objects.none())
    
    return render(request, 'clientes/agregar.html', {
        'formulario': formulario,
        'telefono_formset': telefono_formset,
        'modo': 'agregar'
    })

@login_required
@gerente_required
def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    
    if request.method == 'POST':
        formulario = ClienteForm(request.POST, request.FILES, instance=cliente)
        telefono_formset = TelefonoFormSet(
            request.POST, 
            prefix='telefonos',
            queryset=cliente.telefonos.all()
        )
        
        if formulario.is_valid() and telefono_formset.is_valid():
            try:
                # Guardar el cliente
                cliente = formulario.save()
                
                # Manejar los teléfonos
                telefonos_a_mantener = []
                
                # Procesar el formset
                for form in telefono_formset:
                    if form.cleaned_data:
                        numero = form.cleaned_data.get('numero', '').strip()
                        if numero:  # Solo procesar si hay un número válido
                            if form.instance.pk:
                                if not form.cleaned_data.get('DELETE', False):
                                    form.save()
                                    telefonos_a_mantener.append(form.instance.pk)
                            else:
                                nuevo_telefono = Telefono.objects.create(
                                    cliente=cliente,
                                    numero=numero
                                )
                                telefonos_a_mantener.append(nuevo_telefono.pk)

                log_user_activity(
                    user=request.user,
                    action="Editó",
                    target=f"cliente: {cliente.nombre}-{cliente.curp}",
                    app_name="clientes"
                )
                
                # Eliminar teléfonos que no están en la lista a mantener
                cliente.telefonos.exclude(pk__in=telefonos_a_mantener).delete()
                
                messages.success(request, 'Cliente actualizado exitosamente.')
                return redirect('clientes')
                
            except Exception as e:
                messages.error(request, f"Error al actualizar cliente: {str(e)}")
                logger.error(f"Error en editar_cliente: {e}")
    else:
        formulario = ClienteForm(instance=cliente)
        # Solo mostrar teléfonos existentes, sin formularios extras
        telefono_formset = TelefonoFormSet(
            prefix='telefonos',
            queryset=cliente.telefonos.all()
        )
    
    return render(request, 'clientes/editar.html', {
        'formulario': formulario,
        'telefono_formset': telefono_formset,
        'modo': 'editar'
    })

#funcion para eliminar un cliente existente 
@method_decorator([gerente_required], name='dispatch')
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
        log_user_activity(
                user=self.request.user,
                action="Eliminó",
                target=f"cliente {cliente.nombre} {cliente.apellido}",
                app_name="clientes"
            )
        
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

@require_POST
@login_required
@administrador_required
def eliminar_telefono(request, telefono_id):
    """
    Elimina un teléfono específico via AJAX
    """
    try:
        telefono = get_object_or_404(Telefono, id=telefono_id)
        cliente_id = telefono.cliente.id
        numero = telefono.numero
        
        # Eliminar el teléfono
        telefono.delete()
        
        # Registrar la acción
        logger.info(f"Teléfono {numero} eliminado del cliente {cliente_id}")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Teléfono eliminado correctamente'
        })
    except Telefono.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'El teléfono no existe'
        }, status=404)
    except Exception as e:
        logger.error(f"Error al eliminar teléfono {telefono_id}: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error al eliminar el teléfono: {str(e)}'
        }, status=400)