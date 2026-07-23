from django.db import models

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100, unique=True, help_text='Nombre del proveedor')
    ruc = models.CharField(max_length=11, unique=True, null=True, blank=True, help_text='RUC del proveedor')
    telefono = models.CharField(max_length=15, blank=True, help_text='Teléfono de contacto')
    direccion = models.TextField(blank=True, help_text='Dirección del proveedor')
    email = models.EmailField(blank=True, help_text='Email de contacto')
    persona_contacto = models.CharField(max_length=100, blank=True, null=True, help_text='Persona de contacto / Ejecutivo')
    estado_sunat = models.CharField(max_length=50, default='HABIDO / ACTIVO', help_text='Estado del RUC en SUNAT')
    notas = models.TextField(blank=True, null=True, help_text='Notas u observaciones comerciales')
    activo = models.BooleanField(default=True)


    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']
