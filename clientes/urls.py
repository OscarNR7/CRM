from django.urls import path
from . import views
from .views import *
from django.conf import settings
from django.contrib.staticfiles.urls import static

urlpatterns = [
    path('',Home.as_view(), name='home'),
    path('clientes/', ListarClientes.as_view(), name = 'clientes'),
    path('clientes/agregar', views.agregar_cliente, name = 'agregar'),
    path('clientes/eliminar/<int:pk>', EliminarCliente.as_view(), name = 'eliminar'),
    path('clientes/editar/<int:id>', views.editar_cliente, name = 'editar'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  