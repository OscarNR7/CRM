from django.urls import path
from . import views
from . import vendedores_views as v_views
from .views import *
from .vendedores_views import *
from django.conf import settings
from django.contrib.staticfiles.urls import static

urlpatterns = [
    path('', Home.as_view() , name='home'),
    path('clientes/', ListarClientes.as_view(), name = 'clientes'),
    path('clientes/agregar', views.agregar_cliente, name = 'agregar'),
    path('clientes/eliminar/<int:pk>', EliminarCliente.as_view(), name = 'eliminar'),
    path('clientes/editar/<int:id>', views.editar_cliente, name = 'editar'),
    path('agregar-vendedor/', v_views.agregar_vendedor, name = 'agregar_vendedor'),
    path('listar-vendedores/',ListarVendedores.as_view(), name = 'lista_vendedores'),
    path('pagos/', v_views.PagosClientes.as_view(), name='pagos'),
    path('pago/<int:cliente_id>/<int:vendedor_id>/', v_views.agregar_editar_pago, name='agregar_editar_pago'),
    path('clientes/<int:cliente_id>/informacion/', v_views.informacion_cliente, name = 'informacion')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  