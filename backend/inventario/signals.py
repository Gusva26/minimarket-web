from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import Producto, Kardex, Categoria, UnidadProducto
from compras.models import DetalleCompra
from ventas.models import VentaDetalle, Venta
from django.contrib.auth import get_user_model
from inventario.utils import crear_kardex, invalidate_mercado_cache

User = get_user_model()

@receiver([post_save, post_delete], sender=Producto)
def invalidate_producto_cache(sender, instance, **kwargs):
    """Invalida la caché cuando un producto cambia."""
    invalidate_mercado_cache(instance.mercado_id)

@receiver([post_save, post_delete], sender=Categoria)
def invalidate_categoria_cache(sender, instance, **kwargs):
    """Invalida la caché cuando una categoría cambia."""
    invalidate_mercado_cache(instance.mercado_id)

@receiver([post_save, post_delete], sender=UnidadProducto)
def invalidate_unidad_cache(sender, instance, **kwargs):
    """Invalida la caché cuando cambian los lotes/vencimientos."""
    invalidate_mercado_cache(instance.mercado_id)

@receiver([post_save, post_delete], sender=Venta)
def invalidate_venta_cache(sender, instance, **kwargs):
    """Invalida la caché cuando hay nuevas ventas (afecta Dashboard)."""
    invalidate_mercado_cache(instance.mercado_id)

@receiver(post_save, sender=DetalleCompra)
def registrar_entrada_compra(sender, instance, created, **kwargs):
    """Registrar entrada de stock cuando se guarda un detalle de compra"""
    if created:
        producto = instance.producto
        saldo_nuevo = producto.stock
        saldo_anterior = saldo_nuevo - instance.cantidad

        crear_kardex(
            producto=producto, mercado=producto.mercado,
            tipo_movimiento='ENTRADA', cantidad=instance.cantidad,
            saldo_anterior=saldo_anterior, saldo_nuevo=saldo_nuevo,
            ref_tipo='Compra', ref_id=instance.compra.id,
            ref_detalle=f'Compra a {instance.compra.proveedor.nombre if instance.compra.proveedor else "N/A"}',
            usuario=instance.compra.usuario
        )
        # Invalida caché del mercado
        invalidate_mercado_cache(producto.mercado_id)

@receiver(post_save, sender=VentaDetalle)
def registrar_salida_venta(sender, instance, created, **kwargs):
    """Registrar salida de stock cuando se guarda un detalle de venta"""
    if created:
        producto = instance.producto
        saldo_anterior = producto.stock
        saldo_nuevo = producto.stock - instance.cantidad

        crear_kardex(
            producto=producto, mercado=producto.mercado,
            tipo_movimiento='SALIDA', cantidad=instance.cantidad,
            saldo_anterior=saldo_anterior, saldo_nuevo=saldo_nuevo,
            ref_tipo='Venta', ref_id=instance.venta.id,
            ref_detalle=f'Venta #{instance.venta.id}',
            usuario=instance.venta.usuario
        )
        # Invalida caché del mercado
        invalidate_mercado_cache(producto.mercado_id)