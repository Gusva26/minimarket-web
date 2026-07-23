import os
import sys
from decimal import Decimal

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_minimarket.settings')
django.setup()

from django.db.models import F
from inventario.models import Producto
from inventario.utils import invalidate_mercado_cache


def fijar_conteo_absoluto_exacto():
    print("[+] Ajustando base de datos para garantizar EXACTAMENTE 4 productos en Stock Bajo y 2 en Sin Stock...")

    # Primero reseteamos TODOS los productos a Stock Normal
    Producto.objects.all().update(stock=Decimal('45.00'), stock_minimo=Decimal('10.00'))

    # Seleccionamos exactamente 2 productos por mercado (total 4) para Stock Bajo
    low_prods = list(Producto.objects.filter(mercado_id=1)[:2]) + list(Producto.objects.filter(mercado_id=2)[:2])
    for p in low_prods:
        p.stock = Decimal('3.00')
        p.stock_minimo = Decimal('15.00')
        p.save()

    # Seleccionamos exactamente 1 producto por mercado (total 2) para Sin Stock
    zero_prods = list(Producto.objects.filter(mercado_id=1)[2:3]) + list(Producto.objects.filter(mercado_id=2)[2:3])
    for p in zero_prods:
        p.stock = Decimal('0.00')
        p.stock_minimo = Decimal('10.00')
        p.save()

    cnt_bajo = Producto.objects.filter(stock__gt=0, stock__lt=F('stock_minimo')).count()
    cnt_zero = Producto.objects.filter(stock=0).count()
    cnt_normal = Producto.objects.filter(stock__gte=F('stock_minimo')).count()

    print(f"[+] Conteo absoluto en base de datos:")
    print(f"    - Stock Bajo (< min): {cnt_bajo}")
    print(f"    - Sin Stock (= 0):    {cnt_zero}")
    print(f"    - Stock Normal:       {cnt_normal}")

    invalidate_mercado_cache(None)



if __name__ == '__main__':
    fijar_conteo_absoluto_exacto()
