from django import forms
from .models import *
from django.core.exceptions import ValidationError
from datetime import datetime

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'curp': forms.TextInput(attrs={'class': 'form-control'}),
            'nss': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_de_firma': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'DD de Mes de YYYY'}),
            'fecha_de_baja': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DD-MMM'}),
            'fecha_para_capturar_retiro': forms.DateInput(attrs={'class': 'form-control','type': 'date', 'placeholder': 'DD de Mes de YYYY'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control', 'rows': 2}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'rows': 3}),
            'colonia': forms.TextInput(attrs={'class': 'form-control'}),
            'alta': forms.TextInput(attrs={'class': 'form-control'}),           
            'vendedor': forms.Select(attrs={'class': 'form-control'}),
            'rcv': forms.TextInput(attrs={'class': 'form-control'}),
            'fotografia': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

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
        fields = ['fecha_de_pago', 'cancelacion', 'cantidad', 'anticipo', 'observaciones']
        widgets = {
            'fecha_de_pago': forms.TextInput(attrs={'type': 'date','class': 'form-control'}),
            'cancelacion': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.TextInput(attrs={'class': 'form-control'}),
            'anticipo': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control', 'rows': 2}),
        }