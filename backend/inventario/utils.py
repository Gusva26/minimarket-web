from decimal import Decimal
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone
from .models import UnidadProducto, Kardex


def get_mercado_cache_version(mercado_id):
    """Obtiene la versión actual de la caché para un mercado."""
    if not mercado_id:
        return 1
    return cache.get_or_set(f"version_mercado_{mercado_id}", 1)


def cached_list(cache_key_prefix, mercado_id, params_str, timeout=300):
    """Cachea la respuesta de un listado, invalidado por versión de mercado."""
    version = get_mercado_cache_version(mercado_id)
    cache_key = f"{cache_key_prefix}_v{version}_{params_str}"
    cached = cache.get(cache_key)
    if cached is not None:
        return False, cached
    return True, cache_key


def set_cached_list(cache_key, data, timeout=300):
    """Guarda datos en caché si la key fue generada por cached_list."""
    cache.set(cache_key, data, timeout)


def mercado_filter(request):
    """Retorna filtro de mercado según el usuario. Si es superuser sin mercado, retorna vacío."""
    mercado = request.user.mercado
    if mercado:
        return {'mercado': mercado}
    return {}


def invalidate_mercado_cache(mercado_id):
    """Invalida la caché de un mercado incrementando su versión."""
    if not mercado_id:
        return
    try:
        cache.incr(f"version_mercado_{mercado_id}")
    except ValueError:
        cache.set(f"version_mercado_{mercado_id}", 1)


def descontar_stock_fefo(producto, cantidad, mercado, venta_detalle=None):
    """
    Descuenta stock de un producto siguiendo lógica FEFO
    (First Expiry, First Out).

    Para productos de unidad entera (UND, PAQ): marca unidades individuales
    como 'vendido' con FK a venta_detalle.
    Para productos decimales (KG, LT): reduce la cantidad de la unidad más próxima a vencer.

    Retorna (exito, mensaje_error, unidades_ids_usadas).
    """
    cantidad_por_descontar = Decimal(str(cantidad))
    unidades_usadas = []

    unidades = UnidadProducto.objects.filter(
        producto=producto,
        mercado=mercado,
        estado='disponible',
        cantidad__gt=0,
        fecha_vencimiento__gte=timezone.now().date()
    ).order_by('fecha_vencimiento', 'id')

    for u in unidades:
        if cantidad_por_descontar <= 0:
            break

        if u.cantidad <= cantidad_por_descontar:
            cantidad_por_descontar -= u.cantidad
            u.estado = 'vendido'
            u.cantidad = Decimal('0.00')
            if venta_detalle:
                u.venta_detalle = venta_detalle
            u.save()
            unidades_usadas.append(u.id)
        else:
            u.cantidad -= cantidad_por_descontar
            cantidad_por_descontar = Decimal('0.00')
            u.save()
            # For decimal products partially consumed, we don't set venta_detalle
            # on the remaining portion. The full trace is only for fully consumed units.

    if cantidad_por_descontar > 0:
        return False, f'Stock insuficiente en unidades, faltan {cantidad_por_descontar}', []

    return True, '', unidades_usadas


def devolver_stock_a_unidades(producto, cantidad, mercado, fecha_vencimiento=None, venta_detalle=None):
    """
    Devuelve stock de un producto a las unidades disponibles.

    Si se proporciona venta_detalle, busca las unidades vinculadas a ese
    detalle de venta y las marca como 'disponible' nuevamente.
    Si se proporciona fecha_vencimiento, crea una nueva UnidadProducto.
    """
    if venta_detalle:
        unidades = UnidadProducto.objects.filter(
            producto=producto,
            mercado=mercado,
            venta_detalle=venta_detalle,
        )
        if unidades.exists():
            for u in unidades:
                u.estado = 'disponible'
                u.venta_detalle = None
                u.cantidad = cantidad / unidades.count()
                u.save()
            return
        # If no units found for this venta_detalle, fall through to create new record

    if not fecha_vencimiento:
        fecha_vencimiento = "2099-12-31"

    UnidadProducto.objects.create(
        producto=producto,
        mercado=mercado,
        fecha_vencimiento=fecha_vencimiento,
        cantidad=cantidad,
        estado='disponible',
    )


devolver_stock_a_lotes = devolver_stock_a_unidades


def crear_kardex(producto, mercado, tipo_movimiento, cantidad,
                 saldo_anterior, saldo_nuevo, ref_tipo='', ref_id=None,
                 ref_detalle='', usuario=None):
    """
    Crea un registro en la tabla Kardex.
    """
    return Kardex.objects.create(
        producto=producto,
        mercado=mercado,
        tipo_movimiento=tipo_movimiento,
        cantidad=cantidad,
        saldo_anterior=saldo_anterior,
        saldo_nuevo=saldo_nuevo,
        referencia_tipo=ref_tipo,
        referencia_id=ref_id,
        referencia_detalle=ref_detalle,
        usuario=usuario,
    )
