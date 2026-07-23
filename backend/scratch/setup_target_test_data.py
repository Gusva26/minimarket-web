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

def setup_test_data():
    today = datetime.date.today()
    now = datetime.datetime.now()

    print("Configurando productos de prueba para Vencimientos y Stock Bajo...")

    with transaction.atomic():
        # 1. POR VENCER CRÍTICO (vence en 3 días)
        p_critico = Producto.objects.get(id=57) # Sandwich Triple Pollo Huevo
        UnidadProducto.objects.filter(producto=p_critico).delete()
        UnidadProducto.objects.create(
            producto=p_critico,
            mercado=p_critico.mercado,
            fecha_vencimiento=today + datetime.timedelta(days=3),
            cantidad=p_critico.stock,
            estado='disponible'
        )
        print(f"CRÍTICO OK: {p_critico.nombre} (ID {p_critico.id}) -> Vence en 3 días ({today + datetime.timedelta(days=3)})")

        # 2. POR VENCER ADVERTENCIA (vence en 18 días)
        # Buscar Leche Gloria o similar
        p_adv = Producto.objects.filter(nombre__icontains='Leche').first()
        if not p_adv:
            p_adv = Producto.objects.get(id=1)
        UnidadProducto.objects.filter(producto=p_adv).delete()
        UnidadProducto.objects.create(
            producto=p_adv,
            mercado=p_adv.mercado,
            fecha_vencimiento=today + datetime.timedelta(days=18),
            cantidad=p_adv.stock,
            estado='disponible'
        )
        print(f"ADVERTENCIA OK: {p_adv.nombre} (ID {p_adv.id}) -> Vence en 18 días ({today + datetime.timedelta(days=18)})")

        # 3. VENCIDO (venció hace 5 días)
        p_vencido = Producto.objects.get(id=51) # Empanada de Carne
        UnidadProducto.objects.filter(producto=p_vencido).delete()
        UnidadProducto.objects.create(
            producto=p_vencido,
            mercado=p_vencido.mercado,
            fecha_vencimiento=today - datetime.timedelta(days=5),
            cantidad=p_vencido.stock,
            estado='vencido'
        )
        print(f"VENCIDO OK: {p_vencido.nombre} (ID {p_vencido.id}) -> Venció el {today - datetime.timedelta(days=5)}")

        # 4. POCO STOCK #1 (Stock = 2.00)
        p_stock2 = Producto.objects.get(id=27) # Pisco Queirolo
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
                referencia_detalle='Venta POS B001-000999 (Efectivo)',
                fecha=now
            )
        p_stock2.stock = Decimal('2.00')
        p_stock2.save()
        UnidadProducto.objects.filter(producto=p_stock2).delete()
        UnidadProducto.objects.create(
            producto=p_stock2,
            mercado=p_stock2.mercado,
            fecha_vencimiento=today + datetime.timedelta(days=120),
            cantidad=Decimal('2.00'),
            estado='disponible'
        )
        print(f"POCO STOCK (2.00) OK: {p_stock2.nombre} (ID {p_stock2.id}) -> Stock: 2.00, StockMin: {p_stock2.stock_minimo}")

        # 5. POCO STOCK #2 (Stock = 3.00)
        p_stock3 = Producto.objects.get(id=86) # Whisky Red Label
        k_last_3 = Kardex.objects.filter(producto=p_stock3).order_by('fecha', 'id').last()
        old_saldo_3 = k_last_3.saldo_nuevo if k_last_3 else p_stock3.stock
        diff_3 = old_saldo_3 - Decimal('3.00')
        if diff_3 > 0:
            Kardex.objects.create(
                producto=p_stock3,
                mercado=p_stock3.mercado,
                tipo_movimiento='SALIDA',
                cantidad=diff_3,
                saldo_anterior=old_saldo_3,
                saldo_nuevo=Decimal('3.00'),
                referencia_tipo='Venta POS',
                referencia_detalle='Venta POS B001-000998 (Plin)',
                fecha=now
            )
        p_stock3.stock = Decimal('3.00')
        p_stock3.save()
        UnidadProducto.objects.filter(producto=p_stock3).delete()
        UnidadProducto.objects.create(
            producto=p_stock3,
            mercado=p_stock3.mercado,
            fecha_vencimiento=today + datetime.timedelta(days=150),
            cantidad=Decimal('3.00'),
            estado='disponible'
        )
        print(f"POCO STOCK (3.00) OK: {p_stock3.nombre} (ID {p_stock3.id}) -> Stock: 3.00, StockMin: {p_stock3.stock_minimo}")

        # 6. STOCK CERO (Stock = 0.00)
        p_stock0 = Producto.objects.get(id=69) # Cigarrillos Lucky Strike
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
                referencia_detalle='Venta POS B001-000997 (Tarjeta Visa)',
                fecha=now
            )
        p_stock0.stock = Decimal('0.00')
        p_stock0.save()
        UnidadProducto.objects.filter(producto=p_stock0).delete()
        print(f"STOCK CERO (0.00) OK: {p_stock0.nombre} (ID {p_stock0.id}) -> Stock: 0.00, StockMin: {p_stock0.stock_minimo}")

        cache.clear()
        print("\nÉXITO COMPLETO: Todos los datos han sido aplicados y sincronizados en Producto, Kardex y UnidadProducto.")

if __name__ == '__main__':
    setup_test_data()
