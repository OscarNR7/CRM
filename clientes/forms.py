from django import forms
from .models import *
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory
from datetime import datetime

class TelefonoForm(forms.ModelForm):
    class Meta:
        model = Telefono
        fields = ['numero']
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese número telefónico'})
        }
TelefonoFormSet = modelformset_factory(
    Telefono,
    form=TelefonoForm,
    extra=0,
    can_delete=True
)
class ClienteForm(forms.ModelForm):
    # Convertir los campos DateField a CharField
    fecha_de_baja = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'DD-Mes o DD-Mes-YYYY',
            
        })
    )
    
    fecha_para_capturar_retiro = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'DD-Mes-YYYY o DD/Mes/YYYY'
        })
    )

    class Meta:
        model = Cliente
        exclude = ['telefono'] 
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'curp': forms.TextInput(attrs={'class': 'form-control'}),
            'nss': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_de_firma': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'DD/MMM/YYYY'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control', 'rows': 2}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'rows': 3}),
            'colonia': forms.TextInput(attrs={'class': 'form-control'}),
            'cambio_de_afore': forms.Select(attrs={'class': 'form-control'}),
            'alta': forms.TextInput(attrs={'class': 'form-control'}),           
            'vendedor': forms.Select(attrs={'class': 'form-control'}),
            'rcv': forms.TextInput(attrs={'class': 'form-control'}),
            'fotografia': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'foto_aval': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_fecha_de_firma(self):
        fecha = self.cleaned_data.get('fecha_de_firma')
        if not fecha:
            return None
        try:
            # Guardar la fecha como fue ingresada
            return fecha
        except:
            return fecha

    def clean_fecha_de_baja(self):
        fecha = self.cleaned_data.get('fecha_de_baja')
        if not fecha:
            return None
        try:
            # Guardar la fecha como fue ingresada
            return fecha
        except:
            return fecha

    def clean_fecha_para_capturar_retiro(self):
        fecha = self.cleaned_data.get('fecha_para_capturar_retiro')
        if not fecha:
            return None
        try:
            # Guardar la fecha como fue ingresada
            return fecha
        except:
            return fecha

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Guardar las fechas como texto en los campos
        if self.cleaned_data.get('fecha_de_firma'):
            instance.fecha_de_firma = self.cleaned_data.get('fecha_de_firma')
        
        if self.cleaned_data.get('fecha_de_baja'):
            instance.fecha_de_baja = self.cleaned_data.get('fecha_de_baja')
        
        if self.cleaned_data.get('fecha_para_capturar_retiro'):
            instance.fecha_para_capturar_retiro = self.cleaned_data.get('fecha_para_capturar_retiro')

        if commit:
            instance.save()
        return instance

class VendedorForm(forms.ModelForm):
    usuario = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        empty_label="Seleccione un usuario",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Seleccione un usuario'
        })
    )

    class Meta:
        model = Vendedor
        fields = ['nombre', 'usuario']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nombre del Vendedor'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Primero, obtener todos los usuarios que son vendedores
        usuarios_query = User.objects.filter(userrole__role='vendedor')
        
        # Si estamos editando un vendedor existente
        if self.instance and self.instance.pk:
            if self.instance.usuario:
                # Incluir el usuario actual del vendedor
                usuarios_disponibles = usuarios_query.filter(
                    Q(vendedor__isnull=True) | Q(id=self.instance.usuario.id)
                )
            else:
                # Si no tiene usuario asignado, mostrar solo los disponibles
                usuarios_disponibles = usuarios_query.filter(vendedor__isnull=True)
        else:
            # Para nuevo vendedor, mostrar solo usuarios sin asignar
            usuarios_disponibles = usuarios_query.filter(vendedor__isnull=True)

        self.fields['usuario'].queryset = usuarios_disponibles.distinct().order_by('username')
        
        # Establecer el valor inicial si hay un usuario asignado
        if self.instance and self.instance.usuario:
            self.fields['usuario'].initial = self.instance.usuario.id


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['fecha_de_pago','F46dias', 'cancelacion', 'cantidad', 'anticipo', 'observaciones']
        widgets = {
            'fecha_de_pago': forms.TextInput(attrs={'type': 'date','class': 'form-control'}),
            'F46dias': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control', 'rows': 2}),
            'cancelacion': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.TextInput(attrs={'class': 'form-control'}),
            'anticipo': forms.TextInput(attrs={'class': 'form-control'}),
        }