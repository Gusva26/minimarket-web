import os
import sys
import random
from decimal import Decimal

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_minimarket.settings')
django.setup()

from inventario.models import Producto, Kardex
from ventas.models import Venta
from inventario.utils import invalidate_mercado_cache


def ajustar_stocks_y_anulaciones():
    print("[+] Ajustando stocks para productos con Stock Bajo y Sin Stock...")

    productos = list(Producto.objects.all())
    if not productos:
        print("[-] No hay productos.")
        return

    # 1. Asignar Stock Bajo a ~14 productos (stock < stock_minimo)
    low_stock_prods = random.sample(productos, min(14, len(productos)))
    for p in low_stock_prods:
        p.stock_minimo = Decimal('15')
        p.stock = Decimal(str(random.randint(1, 5)))
        p.save()

    # 2. Asignar Sin Stock (stock = 0) a ~6 productos
    remaining = [p for p in productos if p not in low_stock_prods]
    zero_stock_prods = random.sample(remaining, min(6, len(remaining)))
    for p in zero_stock_prods:
        p.stock_minimo = Decimal('10')
        p.stock = Decimal('0')
        p.save()

    print(f"[+] Stocks actualizados: {len(low_stock_prods)} productos con STOCK BAJO y {len(zero_stock_prods)} productos SIN STOCK.")

    # 3. Anular 6 ventas estratégicamente para mostrar el filtro de Ventas Anuladas
    print("[+] Marcando 6 ventas como ANULADA para pruebas de filtros y flujo de anulación...")
    ventas = list(Venta.objects.filter(estado='COMPLETADA').order_by('-fecha_hora')[:30])
    ventas_anular = random.sample(ventas, min(6, len(ventas)))

    for v in ventas_anular:
        v.estado = 'ANULADA'
        v.save()

        # Actualizar referencia Kardex
        Kardex.objects.filter(referencia_tipo='Venta', referencia_id=v.id).update(
            referencia_detalle=f"ANULADA: {v.tipo_comprobante} {v.serie}-{str(v.numero).zfill(6)} ({v.metodo_pago})"
        )

    print(f"[+] {len(ventas_anular)} ventas anuladas registradas con éxito.")

    # Invalidate cache
    invalidate_mercado_cache(None)
    print("[+] Memoria caché invalidada. ¡Todo listo!")


if __name__ == '__main__':
    ajustar_stocks_y_anulaciones()
