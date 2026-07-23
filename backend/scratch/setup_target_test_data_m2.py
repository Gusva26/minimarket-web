import os
import sys
import datetime
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_minimarket.settings')

import django
django.setup()

from django.db import transaction
from inventario.models import Producto, Kardex, UnidadProducto
from django.core.cache import cache

def setup_test_data_m2():
    today = datetime.date.today()
    now = datetime.datetime.now()

    print("Configurando productos de prueba para Sucursal 2 (Av. Benavides)...")

    with transaction.atomic():
        # 1. POR VENCER CRÍTICO (vence en 2 días)
        p_critico = Producto.objects.get(id=58) # Sandwich Triple Pollo Huevo (Mercado 2)
        UnidadProducto.objects.filter(producto=p_critico).delete()
        UnidadProducto.objects.create(
            producto=p_critico,
            mercado=p_critico.mercado,
            fecha_vencimiento=today + datetime.timedelta(days=2),
            cantidad=p_critico.stock,
            estado='disponible'
        )
        print(f"CRÍTICO M2 OK: {p_critico.nombre} (ID {p_critico.id}) -> Vence en 2 días ({today + datetime.timedelta(days=2)})")

        # 2. POR VENCER ADVERTENCIA (vence en 14 días)
        p_adv = Producto.objects.get(id=18) # Free Tea Durazno 500ml (Mercado 2)
        UnidadProducto.objects.filter(producto=p_adv).delete()
        UnidadProducto.objects.create(
            producto=p_adv,
            mercado=p_adv.mercado,
            fecha_vencimiento=today + datetime.timedelta(days=14),
            cantidad=p_adv.stock,
            estado='disponible'
        )
        print(f"ADVERTENCIA M2 OK: {p_adv.nombre} (ID {p_adv.id}) -> Vence en 14 días ({today + datetime.timedelta(days=14)})")

        # 3. VENCIDO (venció hace 4 días)
        p_vencido = Producto.objects.get(id=52) # Empanada de Carne (Mercado 2)
        UnidadProducto.objects.filter(producto=p_vencido).delete()
        UnidadProducto.objects.create(
            producto=p_vencido,
            mercado=p_vencido.mercado,
            fecha_vencimiento=today - datetime.timedelta(days=4),
            cantidad=p_vencido.stock,
            estado='vencido'
        )
        print(f"VENCIDO M2 OK: {p_vencido.nombre} (ID {p_vencido.id}) -> Venció el {today - datetime.timedelta(days=4)}")

        # 4. POCO STOCK #1 (Stock = 2.00)
        p_stock2 = Producto.objects.get(id=28) # Pisco Queirolo (Mercado 2)
        k_last_2 = Kardex.objects.filter(producto=p_stock2).order_by('fecha', 'id').last()
        old_saldo_2 = k_last_2.saldo_nuevo if k_last_2 else p_stock2.stock
        diff_2 = old_saldo_2 - Decimal('2.00')
        if diff_2 > 0:
            Kardex.objects.create(
                producto=p_stock2,
                mercado=p_stock2.mercado,
                tipo_movimiento='SALIDA',
                cantidad=diff_2,
                saldo_anterior=old_saldo_2,
                saldo_nuevo=Decimal('2.00'),
                referencia_tipo='Venta POS',
                referencia_detalle='Venta POS B002-000999 (Plin)',
                fecha=now
            )
        p_stock2.stock = Decimal('2.00')
        p_stock2.save()
        UnidadProducto.objects.filter(producto=p_stock2).delete()
        UnidadProducto.objects.create(
            producto=p_stock2,
            mercado=p_stock2.mercado,
            fecha_vencimiento=today + datetime.timedelta(days=110),
            cantidad=Decimal('2.00'),
            estado='disponible'
        )
        print(f"POCO STOCK M2 (2.00) OK: {p_stock2.nombre} (ID {p_stock2.id}) -> Stock: 2.00, StockMin: {p_stock2.stock_minimo}")

        # 5. POCO STOCK #2 (Stock = 4.00)
        p_stock4 = Producto.objects.get(id=22) # Cusqueña Dorada (Mercado 2)
        k_last_4 = Kardex.objects.filter(producto=p_stock4).order_by('fecha', 'id').last()
        old_saldo_4 = k_last_4.saldo_nuevo if k_last_4 else p_stock4.stock
        diff_4 = old_saldo_4 - Decimal('4.00')
        if diff_4 > 0:
            Kardex.objects.create(
                producto=p_stock4,
                mercado=p_stock4.mercado,
                tipo_movimiento='SALIDA',
                cantidad=diff_4,
                saldo_anterior=old_saldo_4,
                saldo_nuevo=Decimal('4.00'),
                referencia_tipo='Venta POS',
                referencia_detalle='Venta POS B002-000998 (Efectivo)',
                fecha=now
            )
        p_stock4.stock = Decimal('4.00')
        p_stock4.save()
        UnidadProducto.objects.filter(producto=p_stock4).delete()
        UnidadProducto.objects.create(
            producto=p_stock4,
            mercado=p_stock4.mercado,
            fecha_vencimiento=today + datetime.timedelta(days=90),
            cantidad=Decimal('4.00'),
            estado='disponible'
        )
        print(f"POCO STOCK M2 (4.00) OK: {p_stock4.nombre} (ID {p_stock4.id}) -> Stock: 4.00, StockMin: {p_stock4.stock_minimo}")

        # 6. STOCK CERO (Stock = 0.00)
        p_stock0 = Producto.objects.get(id=70) # Cigarrillos Lucky Strike (Mercado 2)
        k_last_0 = Kardex.objects.filter(producto=p_stock0).order_by('fecha', 'id').last()
        old_saldo_0 = k_last_0.saldo_nuevo if k_last_0 else p_stock0.stock
        if old_saldo_0 > 0:
            Kardex.objects.create(
                producto=p_stock0,
                mercado=p_stock0.mercado,
                tipo_movimiento='SALIDA',
                cantidad=old_saldo_0,
                saldo_anterior=old_saldo_0,
                saldo_nuevo=Decimal('0.00'),
                referencia_tipo='Venta POS',
                referencia_detalle='Venta POS B002-000997 (Yape)',
                fecha=now
            )
        p_stock0.stock = Decimal('0.00')
        p_stock0.save()
        UnidadProducto.objects.filter(producto=p_stock0).delete()
        print(f"STOCK CERO M2 (0.00) OK: {p_stock0.nombre} (ID {p_stock0.id}) -> Stock: 0.00, StockMin: {p_stock0.stock_minimo}")

        cache.clear()
        print("\nÉXITO COMPLETO: Todos los datos para Sucursal 2 han sido aplicados y sincronizados.")

if __name__ == '__main__':
    setup_test_data_m2()
