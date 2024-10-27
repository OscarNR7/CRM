from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserRole
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from usuarios.models import UserRole
from django.contrib.auth import login, logout, authenticate
from .forms import UserRoleAdminForm, UserAdminForm
from .decorators import gerente_required, administrador_required
from django.views.generic import DeleteView
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError

@login_required
@gerente_required
def administrar_usuarios(request):
    try:
        usuarios = User.objects.all()
    except Exception as e:
        messages.error(request, f"Error al listar los usuarios: {e}")
        return redirect('home')
    
    return render(request, 'usuarios/listar_usuarios.html', {'usuarios': usuarios})

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
    
    def delete(self, request, *args, **kwargs):
        try:
            usuario = self.get_object()
            messages.success(request, f"Usuario {usuario.username} eliminado exitosamente.")
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f"Error al eliminar el usuario: {e}")
            return redirect('administrar_usuarios')


#-------------------------------------------------login------------------------------------------------

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        try:
            if form.is_valid():
                user = form.save()
                UserRole.objects.create(user=user, role='supervisor')  # Rol por defecto
                login(request, user)
                messages.success(request, "Usuario registrado y autenticado exitosamente.")
                return redirect('home')
            else:
                messages.error(request, "Error en el registro. Verifique los datos.")
        except ValidationError as e:
            messages.error(request, f"Error de validación: {e}")
        except Exception as e:
            messages.error(request, f"Error al registrar el usuario: {e}")
    else:
        form = UserCreationForm()
    
    return render(request, 'login/signup.html', {'form': form})

#Funcion para cerrar sesión en el sistema
def signout(request):
    '''
        Cierra la sesión del usuario y redirecciona a la página de inicio
        Args: request (HttpRequest): peticion HTTP
    '''
    logout(request)
    return redirect('home')

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
        messages.success(request, "Sesión iniciada exitosamente.")
        return redirect('home')
    
def profile(request):
    try:
        usuario = request.user
    except Exception as e:
        messages.error(request, f"Error al cargar el perfil: {e}")
        return redirect('home')
    
    return render(request, 'usuarios/profile.html', {'usuario': usuario})