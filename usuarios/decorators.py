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
                # Si el usuario no tiene un rol asignado, lo redirigimos a 'home'
                return redirect('home')
        return redirect('home')
    return _wrapped_view

def administrador_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                if request.user.userrole.role in ['gerente', 'administrador']:
                    return view_func(request, *args, **kwargs)
            except UserRole.DoesNotExist:
                return redirect('home')
        return redirect('home')
    return _wrapped_view
