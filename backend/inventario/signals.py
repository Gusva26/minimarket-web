from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Producto, Categoria, UnidadProducto
from compras.models import DetalleCompra
from ventas.models import VentaDetalle, Venta
from inventario.utils import invalidate_mercado_cache

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
def invalidar_cache_compra(sender, instance, **kwargs):
    invalidate_mercado_cache(instance.producto.mercado_id)

@receiver(post_save, sender=VentaDetalle)
def invalidar_cache_venta(sender, instance, **kwargs):
    invalidate_mercado_cache(instance.producto.mercado_id)