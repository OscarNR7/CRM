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
           'fecha_de_baja': forms.DateInput(
                attrs={'class': 'form-control', 'placeholder': 'DD-MMM'},
                format='%d-%b'
            ),
            'fecha_para_capturar_retiro': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'DD de Mes de YYYY'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control', 'rows': 2}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'rows': 3}),
            'colonia': forms.TextInput(attrs={'class': 'form-control'}),
            'alta': forms.TextInput(attrs={'class': 'form-control'}),           
            'vendedor': forms.Select(attrs={'class': 'form-control'}),
            'rcv': forms.TextInput(attrs={'class': 'form-control'}),
            'fotografia': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    fecha_de_baja = forms.DateField(
        input_formats=[
            "%d-%b",
            "%d/%m/%Y",       # 16/09/2024
            "%d-%B-%Y",       # 16-Septiembre-2024
            "%d-%b-%Y",       # 16-Sep-2024
            "%d-%b-%y",         
            ],
        widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'DD-MMM o DD/MM/YYYY, etc.'}),
    )
    fecha_de_firma = forms.DateField(
        input_formats=[
            "%d-%b",
            "%d/%m/%Y",
            "%d/%m/%y",       # 16/09/2024
            "%d-%B-%Y",       # 16-Septiembre-2024
            "%d-%b-%Y",       # 16-Sep-2024
            "%d-%b-%y",         
            ],
        widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'DD-MMM o DD/MM/YYYY, etc.'}),
    )
    fecha_para_capturar_retiro = forms.DateField(
        input_formats=[
            "%d-%b",
            "%d/%m/%Y",       # 16/09/2024
            "%d-%B-%Y",       # 16-Septiembre-2024
            "%d-%b-%Y",       # 16-Sep-2024
            "%d-%b-%y",         
            ],
        widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'DD-MMM o DD/MM/YYYY, etc.'}),
    )
    
    def clean_fecha_de_firma(self):
        fecha = self.cleaned_data['fecha_de_firma']
        if fecha.year < 2024:
            fecha = fecha.replace(year=2024)
        return fecha
    def clean_fecha_de_baja(self):
        fecha = self.cleaned_data['fecha_de_baja']
        if fecha.year < 2024:
            fecha = fecha.replace(year=2024)
        return fecha
    
    def clean_fecha_para_capturar_retiro(self):
        fecha = self.cleaned_data['fecha_para_capturar_retiro']
        if fecha.year < 2024:
            fecha = fecha.replace(year=2024)
        return fecha

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

        #