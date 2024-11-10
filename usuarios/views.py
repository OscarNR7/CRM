# Importaciones de Django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DeleteView

# Importaciones de aplicaciones locales
from .models import *
from .forms import UserRoleAdminForm, UserAdminForm
from .decorators import gerente_required, administrador_required
from .clean_logs import *
from usuarios.models import UserRole


@login_required
@gerente_required
def administrar_usuarios(request):
    try:
        usuarios = User.objects.all()
        logs = UserActivityLog.objects.select_related('user').order_by('-timestamp')
        paginator = Paginator(logs, 10)  # 10 registros por página
        page = request.GET.get('page')
        logs_paginados = paginator.get_page(page)
        context = {
            'usuarios': usuarios,
            'logs': logs_paginados,
            'total_logs': logs.count()
        }
        
        return render(request, 'usuarios/listar_usuarios.html', context)
    except Exception as e:
        print(f"Error en listar_usuarios: {e}")
        messages.error(request, "Error al cargar la lista de usuarios y actividades.")
        return render(request, 'usuarios/listar_usuarios.html', {'usuarios': [], 'logs': []})

@login_required
@gerente_required
def editar_usuario(request, user_id):
    try:
        usuario = get_object_or_404(User, id=user_id)
        user_role, created = UserRole.objects.get_or_create(user=usuario)
        
        if request.method == 'POST':
            user_form = UserAdminForm(request.POST, instance=usuario)
            role_form = UserRoleAdminForm(request.POST, instance=user_role)
            if user_form.is_valid() and role_form.is_valid():
                user_form.save()
                role_form.save()
                log_user_activity(
                    user=request.user,
                    action="Editó",
                    target=f"Usuario: {usuario.username}",
                    app_name="usuarios"
                )
                messages.success(request, "Usuario actualizado exitosamente.")
                return redirect('administrar_usuarios')
            else:
                messages.error(request, "Error al actualizar usuario. Revise los campos e intente nuevamente.")
    except Exception as e:
        messages.error(request, f"Error al editar el usuario: {e}")
        return redirect('administrar_usuarios')

    user_form = UserAdminForm(instance=usuario)
    role_form = UserRoleAdminForm(instance=user_role)
    
    return render(request, 'usuarios/editar_usuario.html', {
        'user_form': user_form, 
        'role_form': role_form, 
        'usuario': usuario
    })

@login_required
@gerente_required
def crear_usuario(request):
    if request.method == 'POST':
        user_form = UserAdminForm(request.POST)
        role_form = UserRoleAdminForm(request.POST)
        try:
            if user_form.is_valid() and role_form.is_valid():
                user = user_form.save()
                role = role_form.save(commit=False)
                role.user = user
                role.save()
                log_user_activity(
                    user=request.user,
                    action="Creó",
                    target=f"Usuario: {user.username}",
                    app_name="usuarios"
                )
                messages.success(request, "Usuario creado exitosamente.")
                return redirect('administrar_usuarios')
            else:
                messages.error(request, "Error al crear usuario. Verifique los datos ingresados.")
        except Exception as e:
            messages.error(request, f"Error al crear el usuario: {e}")
            return redirect('administrar_usuarios')
    
    user_form = UserAdminForm()
    role_form = UserRoleAdminForm()
    
    return render(request, 'usuarios/crear_usuario.html', {
        'user_form': user_form, 
        'role_form': role_form
    })

@method_decorator([gerente_required], name='dispatch')
class EliminarUsuario(LoginRequiredMixin,DeleteView):
    model = User
    success_url = reverse_lazy('administrar_usuarios')
    template_name = 'usuarios/user_confirm_delete.html'
    
    def post(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            log_user_activity(
                user=self.request.user,
                action="Eliminó",
                target=f"Usuario {user.username}",
                app_name="usuarios"
            )
            messages.success(request, f"Usuario {user.username} eliminado exitosamente.")
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f"Error al eliminar el usuario: {e}")
            return redirect('administrar_usuarios')


#-------------------------------------------------login------------------------------------------------

#Funcion para cerrar sesión en el sistema
def signout(request):
    '''
        Cierra la sesión del usuario y redirecciona a la página de inicio
        Args: request (HttpRequest): peticion HTTP
    '''
    logout(request)
    return redirect('clientes')

#funcion para iniciar seseion en el sistema
def signin(request):
    '''
        Autentica al usuario en caso de éxito redirecciona a la lista de clientes.
        De lo contrario, muestra el formulario de login con el error correspondiente.
        Args: request (HttpRequest): peticion HTTP
    '''
    if request.method == 'GET':
        return render(request, 'login/signin.html', {'form': AuthenticationForm()})

    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)

    if user is None:
        messages.error(request, 'Nombre de usuario o contraseña incorrectos')
        return render(request, 'login/signin.html', {'form': AuthenticationForm()})
    else:
        login(request, user)
        return redirect('clientes')
    
def log_user_activity(user, action, target, app_name):
    try:
        UserActivityLog.objects.create(
            user=user,
            action=action,
            target=target,
            app_name=app_name
        )
        print(f"Log creado: {user} - {action} - {target}")  # Para debugging
    except Exception as e:
        print(f"Error al crear log: {str(e)}")  # Para debugging

#-------------------------------------------------------User Avtivity----------------------------------------------------------
@login_required
@gerente_required
def activity_log(request):
    try:
        # Obtener logs filtrados
        days = request.GET.get('days', None)
        days = int(days) if days else None
        logs_list = get_filtered_logs(days=days)
        
        paginator = Paginator(logs_list, 10)
        page = request.GET.get('page')
        logs = paginator.get_page(page)
        
        return render(request, 'usuarios/activity_log.html', {
            'logs': logs,
            'total_logs': logs_list.count()
        })
    except Exception as e:
        print(f"Error en la vista activity_log: {e}")
        messages.error(request, "Error al cargar el historial de actividades.")
        return render(request, 'usuarios/listar_usuarios.html', {'logs': []})

@gerente_required
def clean_logs_view(request):
    # Establece los días de retención
    retention_days = 15  # o el número que prefieras
    cutoff_date = timezone.now() - timedelta(days=retention_days)
    
    # Eliminar logs antiguos
    deleted_count = UserActivityLog.objects.filter(timestamp__lt=cutoff_date).delete()[0]
    
    # Agregar un mensaje al usuario
    messages.success(request, f'Se eliminaron {deleted_count} logs antiguos.')
    
    # Redirigir a la página anterior
    return redirect('administrar_usuarios')  # Reemplaza con la URL desea