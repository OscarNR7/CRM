from django.urls import path
from . import views
from.views import *


urlpatterns = [
    path('administrar/', views.administrar_usuarios, name='administrar_usuarios'),
    path('editar/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path('eliminar/<int:pk>/', EliminarUsuario.as_view(), name='eliminar_usuario'),
    path('logout/', views.signout, name = 'logout'),
    path('', views.signin, name = 'signin'),
    path('profile/', views.profile, name = 'perfil'),
    path('actividad/', views.activity_log, name='activity_log'),
    path('clean-logs/', clean_logs_view, name='clean_logs'),
]