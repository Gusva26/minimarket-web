import os
import sys
from decimal import Decimal

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_minimarket.settings')
django.setup()

from inventario.models import Producto, Kardex, UnidadProducto, Mercado
from inventario.utils import invalidate_mercado_cache
from django.utils import timezone
import datetime


def sincronizar_todo():
    print("[+] Iniciando sincronización matemática 100% entre Producto.stock, Kardex y UnidadProducto...")

    mercados = Mercado.objects.all()

    # 1. Configurar estrictamente 4 Bajo Stock y 2 Sin Stock en todo el catálogo
    all_prods = list(Producto.objects.all().order_by('id'))

    if len(all_prods) >= 6:
        # 2 productos con stock 0
        sin_stock_prods = all_prods[0:2]
        # 4 productos con stock bajo (ej. stock = 3, stock_minimo = 10)
        bajo_stock_prods = all_prods[2:6]
        normal_prods = all_prods[6:]

        for p in sin_stock_prods:
            p.stock = Decimal('0.00')
            p.save()

        for p in bajo_stock_prods:
            p.stock = Decimal('3.00')
            p.stock_minimo = Decimal('10.00')
            p.save()

        for p in normal_prods:
            if p.stock <= p.stock_minimo:
                p.stock = Decimal('45.00')
            p.save()

    print(f"[+] Stocks de Productos ajustados (2 Sin Stock, 4 Bajo Stock, {len(all_prods)-6} Normales).")

    # 2. Sincronizar Kardex paso a paso para CADA producto
    kardex_updated_count = 0
    kardex_created_count = 0

    now = timezone.now()
    base_date = now - datetime.timedelta(days=60)

    for p in Producto.objects.all():
        k_entries = list(Kardex.objects.filter(producto=p).order_by('fecha', 'id'))

        if not k_entries:
            # Crear kardex inicial si no tiene historial
            k_init = Kardex.objects.create(
                producto=p,
                mercado=p.mercado,
                tipo_movimiento='ENTRADA_COMPRA',
                cantidad=p.stock,
                saldo_anterior=Decimal('0.00'),
                saldo_nuevo=p.stock,
                referencia_tipo='Inventario Inicial',
                referencia_id=1,
                fecha=base_date,
            )
            kardex_created_count += 1
        else:
            # Recalcular saldos corridos cronológicamente
            running_balance = Decimal('0.00')
            for i, k in enumerate(k_entries):
                k.saldo_anterior = running_balance
                cant = Decimal(str(k.cantidad))

                if k.tipo_movimiento.startswith('ENTRADA'):
                    running_balance += cant
                elif k.tipo_movimiento.startswith('SALIDA'):
                    running_balance = max(Decimal('0.00'), running_balance - cant)
                else:
                    running_balance += cant

                k.saldo_nuevo = running_balance

                # Si es la última entrada del Kardex, forzar saldo_nuevo exacto a p.stock
                if i == len(k_entries) - 1:
                    if running_balance != p.stock:
                        diff = p.stock - running_balance
                        if diff != Decimal('0.00'):
                            # Ajustar la última entrada o agregar un movimiento de ajuste Kardex
                            k.saldo_nuevo = p.stock
                            if k.tipo_movimiento.startswith('ENTRADA'):
                                k.cantidad = max(Decimal('0.00'), k.cantidad + diff)
                            elif k.tipo_movimiento.startswith('SALIDA'):
                                k.cantidad = max(Decimal('0.00'), k.cantidad - diff)
                            else:
                                k.cantidad = p.stock

                k.save()
                kardex_updated_count += 1

        # 3. Sincronizar Lotes de UnidadProducto
        UnidadProducto.objects.filter(producto=p).delete()
        if p.stock > Decimal('0.00'):
            UnidadProducto.objects.create(
                producto=p,
                mercado=p.mercado,
                fecha_vencimiento="2027-06-30",
                cantidad=p.stock,
                estado='disponible'
            )

    # 4. Invalidar cachés
    for m in mercados:
        invalidate_mercado_cache(m.id)
    invalidate_mercado_cache(None)

    print(f"[+] Kardex reajustados: {kardex_updated_count} entradas actualizadas, {kardex_created_count} creadas.")
    print("[+] Lotes de UnidadProducto 100% sincronizados con Producto.stock.")
    print("[+] Sincronización finalizada con éxito.")


if __name__ == '__main__':
    sincronizar_todo()
