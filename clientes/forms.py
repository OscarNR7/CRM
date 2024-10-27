from django import forms
from .models import *
from django.core.exceptions import ValidationError
from datetime import datetime

class ClienteForm(forms.ModelForm):
    # Convertir los campos DateField a CharField
    fecha_de_firma = forms.DateField(
        required=False,
        input_formats=['%d/%m/%Y','%d/%m/%y'],  # Formato de entrada DD/MM/YYYY
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'DD/MM/YYYY'
        })
    )
    
    fecha_de_baja = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'DD-Mes-YYYY o DD/Mes/YYYY'
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
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'curp': forms.TextInput(attrs={'class': 'form-control'}),
            'nss': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_de_firmar': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control', 'rows': 2}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'rows': 3}),
            'colonia': forms.TextInput(attrs={'class': 'form-control'}),
            'alta': forms.TextInput(attrs={'class': 'form-control'}),           
            'vendedor': forms.Select(attrs={'class': 'form-control'}),
            'rcv': forms.TextInput(attrs={'class': 'form-control'}),
            'fotografia': forms.ClearableFileInput(attrs={'class': 'form-control'}),
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
    class Meta:
        model = Vendedor
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Vendedor'})
        }


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
            'observaciones': forms.TextInput(attrs={'class': 'form-control', 'rows': 2}),
        }