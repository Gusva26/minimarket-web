from django.db import models
from django.utils import timezone
from proveedores.models import Proveedor
from inventario.models import Producto
from usuarios.models import Usuario

class Compra(models.Model):
    fecha = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='compras')
    tipo_comprobante = models.CharField(max_length=50, default='FACTURA', help_text='FACTURA, BOLETA, GUIA_REMISION, TICKET')
    serie_comprobante = models.CharField(max_length=20, blank=True, null=True, help_text='Serie del comprobante de compra (ej: F001)')
    numero_comprobante = models.CharField(max_length=30, blank=True, null=True, help_text='Número de comprobante de compra')
    observaciones = models.TextField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


    def __str__(self):
        return f"Compra a {self.proveedor.nombre if self.proveedor else 'N/A'} el {self.fecha.strftime('%d/%m/%Y')}"

    def actualizar_total(self):
        self.total = self.detalles.aggregate(total=models.Sum('subtotal'))['total'] or 0.00
        self.save(update_fields=['total'])

    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['-fecha']),
            models.Index(fields=['proveedor', '-fecha']),
        ]


class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='detalles_compra')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_vencimiento = models.DateField(null=True, blank=True, help_text='Fecha en que vence este lote de productos.')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_costo_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} @ S/{self.precio_costo_unitario}"

    class Meta:
        verbose_name = 'Detalle de Compra'
        verbose_name_plural = 'Detalles de Compra'
