from django.shortcuts import redirect
from functools import wraps
from .models import UserRole

def gerente_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                if request.user.userrole.role == 'gerente':
                    return view_func(request, *args, **kwargs)
            except UserRole.DoesNotExist:
                # Si el usuario no tiene un rol asignado, lo redirigimos a 'clientes'
                return redirect('clientes')
        return redirect('clientes')
    return _wrapped_view

def administrador_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                if request.user.userrole.role in ['gerente', 'administrador']:
                    return view_func(request, *args, **kwargs)
            except UserRole.DoesNotExist:
                return redirect('clientes')
        return redirect('clientes')
    return _wrapped_view

def vendedor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                role = request.user.userrole.role
                if role == 'vendedor':
                    return view_func(request, *args, **kwargs)
                elif role in ['gerente', 'administrador']:
                    # Gerentes y administradores tienen acceso a todo
                    return view_func(request, *args, **kwargs)
            except UserRole.DoesNotExist:
                pass
        # Si no es vendedor, gerente o administrador, redirigir o denegar
        return redirect('clientes')  # O usar `raise PermissionDenied`
    return _wrapped_view
