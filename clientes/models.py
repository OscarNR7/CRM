from typing import Any
from django.db import models
from datetime import timedelta

class Vendedor(models.Model):
    nombre = models.CharField(max_length=100, help_text="Nombre del Vendedor")

    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    # Definición de los campos para almacenar la información de los clientes
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, help_text="Nombre del cliente")
    curp = models.CharField(max_length=100, unique=True,  help_text="Clave Única de Registro de Población (CURP)")
    nss = models.CharField(max_length=100, unique=True, help_text="Número de Seguridad Social (NSS)")
    telefono = models.CharField(max_length=50, unique=True, null=True ,help_text="Numero de telefono del cliente")
    fecha_de_firma = models.DateField(null=True ,blank=True, help_text="Fecha de Firma")
    fecha_de_baja = models.DateField(null=True, blank=True, help_text="Fecha de Baja")
    fecha_para_capturar_retiro = models.DateField(null=True,blank = True,help_text="Fecha para capturar retiro")
    observaciones = models.TextField(verbose_name="referencia",null=True, blank=True,help_text="Observaciones del cliente")
    alta = models.CharField(max_length=100, null=True, blank=True,help_text="Alta")
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE, null=True,help_text="Vendedor al que pertenece el cliente")
    rcv = models.CharField(max_length=50,null=True,blank=True,help_text="RCV")
    direccion = models.TextField(help_text="Dirección completa del cliente")
    colonia = models.CharField(max_length=255, help_text="Colonia de residencia del cliente")
    fotografia = models.ImageField(upload_to='clientes/fotos/', null=True,blank=True,verbose_name="Foto", help_text="Fotografía del cliente")

    # Método para representar el cliente como una cadena 
    def __str__(self):
        #fila= "Nombre" + self.nombre - "CURP" + self.curp - "NSS" + self.nss - "Colonia" + self.colonia
        # return fila
        return f"{self.nombre}  - {self.curp} - {self.colonia}"
    
    def delete(self, *args, **kwargs):
        # Verificar si hay una fotografía antes de intentar eliminarla
        if self.fotografia and self.fotografia.name:
            self.fotografia.delete()
        super().delete(*args, **kwargs)
    
    #funcion para calcular la fecha para el retiro
    def save(self, *args, **kwargs):
        #calcular la fecha para el retiro
        if self.fecha_de_baja:
            self.fecha_para_capturar_retiro = self.fecha_de_baja + timedelta(days=46)
        super().save(*args, **kwargs)
        
    # Método para definir la ordenación por defecto 
    class Meta:
        ordering = ['nombre']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    
