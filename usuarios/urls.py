from django.urls import path
from . import views

urlpatterns = [
    path('administrar/', views.administrar_usuarios, name='administrar_usuarios'),
    path('editar/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path('eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('logout/', views.signout, name = 'logout'),
    path('signin/', views.signin, name = 'signin'),
    path('signup/', views.signup, name = 'signup'),
    path('profile/', views.profile, name = 'perfil'),
]