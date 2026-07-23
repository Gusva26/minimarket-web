import os
import sys
from decimal import Decimal

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_minimarket.settings')
django.setup()

from inventario.models import Producto
from inventario.utils import invalidate_mercado_cache


def fijar_stock_bajo_pagina1():
    print("[+] Ajustando stocks en productos de las letras A-D para visibilidad directa en Página 1...")

    prods_p1 = list(Producto.objects.filter(nombre__iregex=r'^[A-D]').order_by('nombre'))
    print(f"[+] Encontrados {len(prods_p1)} productos que inician con A-D:")

    low_stock_names = [
        "Aceite Motor Shell Helix Ultra 20W-50 1L",
        "Agua San Luis Con Gas 625ml",
        "Alfajor Clásico",
        "Bolsa de Hielo Listo! 3kg",
        "Cerveza Pilsen Callao Six Pack Latas 355ml",
        "Coca Cola Sin Azúcar Lata 355ml",
        "Croissant de Jamón y Queso",
        "Cua Cua Field 18g",
        "Doritos Cheese Queso 145g",
    ]

    zero_stock_names = [
        "Cable USB-C Carga Rápida 1m",
        "Cargador USB Doble para Auto Listo!",
        "Chifle Plátano Karinto 120g",
    ]

    c_low = 0
    c_zero = 0

    for p in Producto.objects.all():
        if any(target.lower() in p.nombre.lower() for target in low_stock_names):
            p.stock_minimo = Decimal('15')
            p.stock = Decimal('3')
            p.save()
            c_low += 1
        elif any(target.lower() in p.nombre.lower() for target in zero_stock_names):
            p.stock_minimo = Decimal('10')
            p.stock = Decimal('0')
            p.save()
            c_zero += 1

    print(f"[+] Ajuste completado: {c_low} productos configurados con STOCK BAJO (3 un) y {c_zero} productos SIN STOCK (0 un).")
    invalidate_mercado_cache(None)


if __name__ == '__main__':
    fijar_stock_bajo_pagina1()
