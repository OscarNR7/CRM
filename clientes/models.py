import logging
from typing import Any
from django.db import models
from datetime import timedelta,datetime

logger = logging.getLogger('clientes')

class Vendedor(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Vendedores"
    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    #Definición de los campos para almacenar la información de los clientes
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, help_text="Nombre del cliente")
    curp = models.CharField(max_length=100, unique=True,  help_text="Clave Única de Registro de Población (CURP)")
    nss = models.CharField(max_length=100, unique=True, help_text="Número de Seguridad Social (NSS)")
    telefono = models.CharField(max_length=50, unique=True, null=True ,help_text="Numero de telefono del cliente")
    fecha_de_firma = models.DateField(null=True, blank=True, help_text="Fecha de Firma (DD/MM/YYYY)")
    fecha_de_baja = models.CharField(max_length=50, null=True, blank=True, help_text="Fecha de Baja")
    fecha_para_capturar_retiro = models.CharField(max_length=50, null=True, blank=True, help_text="Fecha para capturar retiro")
    observaciones = models.TextField(verbose_name="observaciones",null=True, blank=True,help_text="Observaciones del cliente")
    alta = models.CharField(max_length=100, null=True, blank=True,help_text="Alta")
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE, null=True, blank=True ,help_text="Vendedor al que pertenece el cliente")
    rcv = models.CharField(max_length=50,null=True,blank=True,help_text="RCV")
    direccion = models.TextField(null=True, blank=True,help_text="Dirección completa del cliente")
    colonia = models.CharField(blank=True,max_length=255, help_text="Colonia de residencia del cliente")
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
        try:
            if self.fecha_de_baja:
                try:
                    # Convertir la fecha de baja a formato correcto
                    fecha_baja_str = self.fecha_de_baja.replace('/', '-')
                    
                    # Diccionario para convertir abreviaciones de meses a números
                    meses = {
                        'Ene': '01', 'Feb': '02', 'Mar': '03', 'Abr': '04',
                        'May': '05', 'Jun': '06', 'Jul': '07', 'Ago': '08',
                        'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dic': '12',
                        #fechas en minusculas
                        'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04',
                        'may': '05', 'jun': '06', 'jul': '07', 'ago': '08',
                        'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12',
                        # Incluir también nombres completos por si acaso
                        'Enero': '01', 'Febrero': '02', 'Marzo': '03', 'Abril': '04',
                        'Mayo': '05', 'Junio': '06', 'Julio': '07', 'Agosto': '08',
                        'Septiembre': '09', 'Octubre': '10', 'Noviembre': '11', 'Diciembre': '12',
                        # Incluir también nombres completos en minusculas por si acaso
                        'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
                        'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
                        'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
                    }
                     # Lista de formatos de fecha aceptados
                    formatos_fecha = ["%d-%m-%Y", "%d/%m/%Y", "%d-%b-%Y", "%d/%b/%Y", "%d-%B-%Y", "%d/%B/%Y"]
                    
                    # Separar el día y mes
                    partes = fecha_baja_str.split('-')
                    if len(partes) == 2:
                        dia, mes = partes
                        # Usar el año actual
                        anio = str(datetime.now().year)
                    else:
                        dia, mes, anio = partes
                    
                    # Convertir el nombre del mes a número
                    mes = meses.get(mes, mes)  # Si ya es número, se mantiene igual
                    
                    # Crear fecha en formato yyyy-mm-dd
                    fecha_baja = datetime.strptime(f"{dia}-{mes}-{anio}", "%d-%m-%Y")
                    
                    # Calcular la fecha para capturar retiro (46 días después)
                    fecha_retiro = fecha_baja + timedelta(days=46)
                    
                    # Formatear la fecha de retiro como dd-mmm-yy
                    self.fecha_para_capturar_retiro = fecha_retiro.strftime("%d-%b-%y").replace(
                        fecha_retiro.strftime("%b"),
                        fecha_retiro.strftime("%b").capitalize()
                    )
                
                except Exception as e:
                    print(f"Error al calcular fecha_para_capturar_retiro: {e}")
                    pass

        except Exception as e:
            logger.error(f"Error en Models Pago.Save(): {e}")
            raise
        super().save(*args, **kwargs)
        
    # Método para definir la ordenación por defecto 
    class Meta:
        ordering = ['nombre']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

class Pago(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pagos')
    fecha_de_pago = models.DateField(null=True, blank=True)
    F46dias = models.DateField(null=True, blank=True)
    cancelacion = models.CharField(max_length=50,blank=True, null=True)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)
    anticipo = models.DecimalField(max_digits=10, decimal_places=2)
    observaciones = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.cantidad == 2500:
            self.porcentaje = 100
        else:
            self.porcentaje = (self.cantidad / 2500) * 100
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pago de {self.cliente.nombre} - {self.cliente.fecha_de_firma}"