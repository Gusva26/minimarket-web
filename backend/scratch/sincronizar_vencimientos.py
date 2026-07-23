import os
import sys
from decimal import Decimal
import datetime

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_minimarket.settings')
django.setup()

from inventario.models import Producto, Kardex, UnidadProducto, Mercado
from inventario.utils import invalidate_mercado_cache
from django.utils import timezone


def sincronizar_vencimientos():
    print("[+] Sincronizando vencimientos: 1 Vencido, 4 Por Vencer (2 Críticos < 7d, 2 Advertencia 7-30d) y el resto Seguros...")

    today = datetime.date(2026, 7, 22)
    mercados = Mercado.objects.all()
    all_prods = list(Producto.objects.filter(stock__gt=0).order_by('id'))

    if len(all_prods) < 10:
        print("[!] No hay suficientes productos con stock > 0.")
        return

    # Buscar productos perecibles para vencimientos lógicos
    comida_prods = [p for p in all_prods if p.categoria and ('comida' in p.categoria.nombre.lower() or 'caf' in p.categoria.nombre.lower() or 'galleta' in p.categoria.nombre.lower())]

    if len(comida_prods) < 5:
        target_prods = all_prods[:5]
    else:
        target_prods = comida_prods[:5]

    # 1 Vencido
    prod_vencido = target_prods[0]
    # 4 Por vencer (2 criticos, 2 advertencias)
    prod_critico_1 = target_prods[1]
    prod_critico_2 = target_prods[2]
    prod_adv_1 = target_prods[3]
    prod_adv_2 = target_prods[4]

    special_map = {
        prod_vencido.id: today - datetime.timedelta(days=10),        # Vencido hace 10 días (2026-07-12)
        prod_critico_1.id: today + datetime.timedelta(days=3),       # Crítico (vence en 3 días: 2026-07-25)
        prod_critico_2.id: today + datetime.timedelta(days=5),       # Crítico (vence en 5 días: 2026-07-27)
        prod_adv_1.id: today + datetime.timedelta(days=14),         # Advertencia (vence en 14 días: 2026-08-05)
        prod_adv_2.id: today + datetime.timedelta(days=22),         # Advertencia (vence en 22 días: 2026-08-13)
    }

    print(f"    - [VENCIDO]: #{prod_vencido.id} {prod_vencido.nombre} -> Vención {special_map[prod_vencido.id]}")
    print(f"    - [CRÍTICO 1]: #{prod_critico_1.id} {prod_critico_1.nombre} -> Vence {special_map[prod_critico_1.id]}")
    print(f"    - [CRÍTICO 2]: #{prod_critico_2.id} {prod_critico_2.nombre} -> Vence {special_map[prod_critico_2.id]}")
    print(f"    - [ADVERTENCIA 1]: #{prod_adv_1.id} {prod_adv_1.nombre} -> Vence {special_map[prod_adv_1.id]}")
    print(f"    - [ADVERTENCIA 2]: #{prod_adv_2.id} {prod_adv_2.nombre} -> Vence {special_map[prod_adv_2.id]}")

    # Sincronizar UnidadProducto para TODOS los productos con stock > 0
    UnidadProducto.objects.all().delete()
    unidades_creadas = 0

    for p in Producto.objects.all():
        if p.stock <= Decimal('0.00'):
            continue

        if p.id in special_map:
            fecha_venc = special_map[p.id]
        else:
            # Seguro: entre 6 y 18 meses en el futuro
            offset_days = 180 + ((p.id * 13) % 250)
            fecha_venc = today + datetime.timedelta(days=offset_days)

        estado_u = 'disponible' if fecha_venc >= today else 'vencido'

        UnidadProducto.objects.create(
            producto=p,
            mercado=p.mercado,
            fecha_vencimiento=fecha_venc,
            cantidad=p.stock,
            estado=estado_u
        )
        unidades_creadas += 1

    # Invalidar cachés
    for m in mercados:
        invalidate_mercado_cache(m.id)
    invalidate_mercado_cache(None)

    print(f"[+] Se crearon {unidades_creadas} lotes de UnidadProducto 100% sincronizados con Producto.stock.")
    print("[+] Sincronización de vencimientos completada exitosamente.")


if __name__ == '__main__':
    sincronizar_vencimientos()
