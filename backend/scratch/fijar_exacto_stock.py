import os
import sys
from decimal import Decimal

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_minimarket.settings')
django.setup()

from inventario.models import Producto
from inventario.utils import invalidate_mercado_cache


def fijar_exacto_stock():
    print("[+] Reseteando catálogo para tener EXACTAMENTE 4 productos en Stock Bajo y 2 productos Sin Stock...")

    # Nombres exactos de los 4 productos en stock bajo
    exact_low_names = [
        "Aceite Motor Shell Helix Ultra 20W-50 1L",
        "Bolsa de Hielo Listo! 3kg",
        "Red Bull Energy Drink 250ml",
        "Sublime Extremo 55g"
    ]

    # Nombres exactos de los 2 productos sin stock
    exact_zero_names = [
        "Cable USB-C Carga Rápida 1m",
        "Cargador USB Doble para Auto Listo!"
    ]

    c_low = 0
    c_zero = 0
    c_normal = 0

    for p in Producto.objects.all():
        is_low = any(name.lower() in p.nombre.lower() for name in exact_low_names)
        is_zero = any(name.lower() in p.nombre.lower() for name in exact_zero_names)

        if is_low:
            p.stock_minimo = Decimal('15')
            p.stock = Decimal('3')
            p.save()
            c_low += 1
        elif is_zero:
            p.stock_minimo = Decimal('10')
            p.stock = Decimal('0')
            p.save()
            c_zero += 1
        else:
            p.stock_minimo = Decimal('10')
            if p.stock < p.stock_minimo:
                p.stock = Decimal('45')
            p.save()
            c_normal += 1

    print(f"[+] Proceso completado:")
    print(f"    - Stock Bajo (< min): {c_low}")
    print(f"    - Sin Stock (= 0):    {c_zero}")
    print(f"    - Stock Normal:       {c_normal}")

    invalidate_mercado_cache(None)


if __name__ == '__main__':
    fijar_exacto_stock()
