import os
import logging
from PIL import Image
from django.db import models
from django.utils import timezone
from django.core.files.base import ContentFile
from io import BytesIO


logger = logging.getLogger(__name__)

class Mercado(models.Model):
    nombre = models.CharField(max_length=100)
    ruc = models.CharField(max_length=11, blank=True, null=True, help_text='Número de RUC de la sucursal.')
    direccion = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Mercado"
        verbose_name_plural = "Mercados"

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    mercado = models.ForeignKey(Mercado, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    UNIDADES_MEDIDA = (
        ('UND', 'Unidad'),
        ('KG', 'Kilogramo'),
        ('LT', 'Litro'),
        ('PAQ', 'Paquete'),
    )

    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text='Costo de adquisición del producto.')
    stock = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=5.00, help_text='Alerta cuando el stock sea inferior a este valor.')
    unidad_medida = models.CharField(max_length=10, choices=UNIDADES_MEDIDA, default='UND')
    codigo_barras = models.CharField(max_length=50, blank=True, null=True, db_index=True, help_text='Código de barras para identificación rápida.')
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    mercado = models.ForeignKey(Mercado, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.get_unidad_medida_display()})"

    def tiene_stock_bajo(self):
        return self.stock < self.stock_minimo

    def save(self, *args, **kwargs):
        if self.imagen:
            try:
                img = Image.open(self.imagen)
                original_mode = img.mode
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Resize if larger than 500x500
                max_size = (500, 500)
                if img.width > 500 or img.height > 500:
                    img.thumbnail(max_size, Image.LANCZOS)
                
                # Remove background with rembg (optional)
                try:
                    from rembg import remove
                    img = remove(img)
                except ImportError:
                    pass
                except Exception as e:
                    logger.warning(f"rembg falló, usando imagen original: {e}")
                
                # Save as PNG (preserves transparency)
                output = BytesIO()
                img.save(output, format='PNG', optimize=True)
                output.seek(0)
                
                # New name with .png extension
                name = os.path.splitext(self.imagen.name)[0] + '.png'
                self.imagen = ContentFile(output.read(), name=name)
            except Exception as e:
                logger.error(f"Error procesando imagen: {e}", exc_info=True)
                
        super().save(*args, **kwargs)

class Kardex(models.Model):
    TIPO_MOVIMIENTO_CHOICES = (
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('AJUSTE_POSITIVO', 'Ajuste Positivo'),
        ('AJUSTE_NEGATIVO', 'Ajuste Negativo'),
        ('ENTRADA_TRANSFERENCIA', 'Entrada por Transferencia'),
        ('SALIDA_TRANSFERENCIA', 'Salida por Transferencia'),
    )
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos_kardex')
    mercado = models.ForeignKey(Mercado, on_delete=models.CASCADE)
    tipo_movimiento = models.CharField(max_length=30, choices=TIPO_MOVIMIENTO_CHOICES)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_nuevo = models.DecimalField(max_digits=10, decimal_places=2)
    referencia_tipo = models.CharField(max_length=50, blank=True, help_text='Tipo de documento: Compra, Venta, Ajuste, etc.')
    referencia_id = models.IntegerField(null=True, blank=True, help_text='ID del documento de referencia')
    referencia_detalle = models.CharField(max_length=200, blank=True, help_text='Descripción adicional del movimiento')
    fecha = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Kardex'
        verbose_name_plural = 'Kardex'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['producto', 'fecha']),
            models.Index(fields=['mercado', 'fecha']),
        ]
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.tipo_movimiento} {self.cantidad} - Saldo: {self.saldo_nuevo}"

class Transferencia(models.Model):
    ESTADO_CHOICES = (
        ('EN_TRANSITO', 'En Tránsito'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    )
    
    mercado_origen = models.ForeignKey(Mercado, on_delete=models.CASCADE, related_name='transferencias_enviadas')
    mercado_destino = models.ForeignKey(Mercado, on_delete=models.CASCADE, related_name='transferencias_recibidas')
    usuario_envio = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, related_name='envios_realizados')
    usuario_recepcion = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='recepciones_realizadas')
    fecha_envio = models.DateTimeField(default=timezone.now)
    fecha_recepcion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='EN_TRANSITO')
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Transferencia'
        verbose_name_plural = 'Transferencias'
        ordering = ['-fecha_envio']
    
    def __str__(self):
        return f"Transferencia #{self.id} de {self.mercado_origen.nombre} a {self.mercado_destino.nombre}"

class TransferenciaDetalle(models.Model):
    transferencia = models.ForeignKey(Transferencia, on_delete=models.CASCADE, related_name='detalles')
    producto_origen = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='transferencias_origen')
    producto_destino = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True, related_name='transferencias_destino')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_vencimiento = models.DateField(null=True, blank=True, help_text='Fecha de vencimiento del lote transferido.')
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto_origen.nombre}"

class UnidadProducto(models.Model):
    ESTADOS = (
        ('disponible', 'Disponible'),
        ('vendido', 'Vendido'),
        ('daniado', 'Dañado'),
        ('perdida', 'Pérdida'),
    )
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='unidades')
    mercado = models.ForeignKey(Mercado, on_delete=models.CASCADE)
    fecha_vencimiento = models.DateField(db_index=True)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=1,
                                   help_text='1 para unidades enteras, fracción para decimales')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='disponible')
    venta_detalle = models.ForeignKey('ventas.VentaDetalle', on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='unidades')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Unidad de Producto'
        verbose_name_plural = 'Unidades de Producto'
        ordering = ['fecha_vencimiento']
        indexes = [
            models.Index(fields=['producto', 'fecha_vencimiento', 'estado']),
            models.Index(fields=['producto', 'mercado', 'estado', 'fecha_vencimiento']),
        ]

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad} - Vence: {self.fecha_vencimiento} [{self.estado}]"

    def esta_vencido(self):
        return self.fecha_vencimiento < timezone.now().date()

    def dias_para_vencer(self):
        delta = self.fecha_vencimiento - timezone.now().date()
        return delta.days
