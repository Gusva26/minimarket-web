from django.db import models
from django.utils import timezone
from usuarios.models import Usuario
from inventario.models import Producto, Mercado

class Caja(models.Model):
    ESTADO_CHOICES = (
        ('ABIERTA', 'Abierta'),
        ('CERRADA', 'Cerrada'),
    )
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    mercado = models.ForeignKey(Mercado, on_delete=models.CASCADE)
    fecha_apertura = models.DateTimeField(default=timezone.now)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Montos reales ingresados por el usuario al cerrar
    monto_final_efectivo_real = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monto_final_yape_real = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monto_final_plin_real = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Montos esperados calculados por el sistema
    monto_esperado_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    monto_esperado_yape = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    monto_esperado_plin = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='ABIERTA')
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Caja {self.id} - {self.usuario.username} ({self.estado})"

    class Meta:
        verbose_name = 'Caja'
        verbose_name_plural = 'Cajas'
        ordering = ['-fecha_apertura']

class Cliente(models.Model):
    DOCUMENTO_CHOICES = (
        ('DNI', 'DNI'),
        ('RUC', 'RUC'),
    )
    nombre = models.CharField(max_length=200)
    tipo_documento = models.CharField(max_length=10, choices=DOCUMENTO_CHOICES, default='DNI')
    num_documento = models.CharField(max_length=20, unique=True)
    direccion = models.CharField(max_length=300, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.num_documento})"

class Venta(models.Model):
    METODOS_PAGO = (
        ('Efectivo', 'Efectivo'),
        ('Yape', 'Yape'),
        ('Plin', 'Plin'),
    )
    TIPO_COMPROBANTE = (
        ('TICKET', 'Ticket'),
        ('BOLETA', 'Boleta'),
        ('FACTURA', 'Factura'),
    )
    ESTADOS = (
        ('COMPLETADA', 'Completada'),
        ('ANULADA', 'Anulada'),
    )
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    
    # Datos de Facturación
    tipo_comprobante = models.CharField(max_length=20, choices=TIPO_COMPROBANTE, default='TICKET')
    serie = models.CharField(max_length=10, default='T001')
    numero = models.PositiveIntegerField(default=1)
    
    # Totales y Desglose
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    igv = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Para calcular utilidad
    
    # Detalle de Pago
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)
    monto_recibido = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    vuelto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    num_operacion = models.CharField(max_length=50, blank=True, null=True)
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='COMPLETADA')
    mercado = models.ForeignKey(Mercado, on_delete=models.CASCADE, null=True, blank=True)
    caja = models.ForeignKey(Caja, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas')

    class Meta:
        unique_together = ('mercado', 'tipo_comprobante', 'serie', 'numero')

    def __str__(self):
        return f"{self.tipo_comprobante} {self.serie}-{self.numero:06d} | S/ {self.total} ({self.estado})"

    @property
    def utilidad(self):
        return self.total - self.costo_total

class VentaDetalle(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Costo al momento de la venta
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre if self.producto else 'Producto Eliminado'}"
