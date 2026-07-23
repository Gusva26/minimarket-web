import os
import sys
import random
from decimal import Decimal

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_minimarket.settings')
django.setup()

from inventario.models import Producto, Kardex, UnidadProducto, Mercado
from inventario.utils import invalidate_mercado_cache
from django.utils import timezone
import datetime


def generar_stock_coherente(producto):
    """
    Genera un stock realista y variado dependiendo de la categoría y nombre del producto.
    """
    cat_nombre = producto.categoria.nombre.lower() if producto.categoria else ''
    pid = producto.id

    # Usar el ID del producto para que el valor sea determinista y único
    mod = (pid * 17 + 11) % 50

    if 'bebida' in cat_nombre or 'gaseosa' in cat_nombre:
        # Alto volumen: 40 a 140 unidades
        return Decimal(str(40 + (mod * 2)))
    elif 'cerveza' in cat_nombre or 'licor' in cat_nombre:
        # Volumen medio-alto: 18 a 60 unidades
        return Decimal(str(18 + mod))
    elif 'snack' in cat_nombre or 'salado' in cat_nombre:
        # Volumen medio-alto: 30 a 85 unidades
        return Decimal(str(30 + int(mod * 1.1)))
    elif 'golosina' in cat_nombre or 'chocolate' in cat_nombre:
        # Volumen alto: 35 a 95 unidades
        return Decimal(str(35 + int(mod * 1.2)))
    elif 'comida' in cat_nombre or 'caf' in cat_nombre:
        # Perecibles/Fresco: 12 a 32 unidades
        return Decimal(str(12 + (mod % 20)))
    elif 'galleta' in cat_nombre or 'panader' in cat_nombre:
        # Volumen medio: 25 a 70 unidades
        return Decimal(str(25 + int(mod * 0.9)))
    elif 'helado' in cat_nombre or 'hielo' in cat_nombre:
        # Congelados: 15 a 45 unidades
        return Decimal(str(15 + (mod % 30)))
    elif 'cigarrillo' in cat_nombre or 'tabaco' in cat_nombre:
        # Tabaco: 20 a 55 unidades
        return Decimal(str(20 + (mod % 35)))
    else:
        return Decimal(str(25 + (mod % 40)))


def ejecutar():
    print("[+] Generando varianza de stocks realista y coherente por categoría...")

    mercados = Mercado.objects.all()
    all_prods = list(Producto.objects.all().order_by('id'))

    if len(all_prods) < 6:
        print("[!] No hay suficientes productos para ajustar.")
        return

    # Selección fija de productos para Bajo Stock (4) y Sin Stock (2)
    sin_stock_prods = all_prods[0:2]       # 2 productos con stock 0
    bajo_stock_prods = all_prods[2:6]      # 4 productos con stock bajo (stock <= stock_minimo)
    normal_prods = all_prods[6:]           # El resto con stocks variados reales

    # 1. Aplicar Sin Stock (0)
    for p in sin_stock_prods:
        p.stock = Decimal('0.00')
        p.save()

    # 2. Aplicar Bajo Stock (entre 2 y 4 unidades, con stock_minimo = 10)
    stocks_bajo = [Decimal('2.00'), Decimal('4.00'), Decimal('3.00'), Decimal('5.00')]
    for i, p in enumerate(bajo_stock_prods):
        p.stock = stocks_bajo[i % len(stocks_bajo)]
        p.stock_minimo = Decimal('10.00')
        p.save()

    # 3. Aplicar Stock Variado y Coherente a todos los demás productos
    for p in normal_prods:
        p.stock = generar_stock_coherente(p)
        p.stock_minimo = Decimal('10.00')
        p.save()

    print(f"[+] Stocks asignados con éxito a {len(all_prods)} productos.")

    # 4. Re-sincronizar el Kardex de CADA producto para que el saldo final sea idéntico a p.stock
    now = timezone.now()
    base_date = now - datetime.timedelta(days=60)
    updated_kardex = 0

    for p in Producto.objects.all():
        k_entries = list(Kardex.objects.filter(producto=p).order_by('fecha', 'id'))

        if not k_entries:
            Kardex.objects.create(
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
        else:
            running_balance = Decimal('0.00')
            for idx, k in enumerate(k_entries):
                k.saldo_anterior = running_balance
                cant = Decimal(str(k.cantidad))

                if k.tipo_movimiento.startswith('ENTRADA'):
                    running_balance += cant
                elif k.tipo_movimiento.startswith('SALIDA'):
                    running_balance = max(Decimal('0.00'), running_balance - cant)
                else:
                    running_balance += cant

                k.saldo_nuevo = running_balance

                # En el último movimiento del Kardex, igualar exactamente al stock del producto
                if idx == len(k_entries) - 1:
                    diff = p.stock - running_balance
                    if diff != Decimal('0.00'):
                        k.saldo_nuevo = p.stock
                        if k.tipo_movimiento.startswith('ENTRADA'):
                            k.cantidad = max(Decimal('0.00'), k.cantidad + diff)
                        elif k.tipo_movimiento.startswith('SALIDA'):
                            k.cantidad = max(Decimal('0.00'), k.cantidad - diff)
                        else:
                            k.cantidad = p.stock

                k.save()
                updated_kardex += 1

        # 5. Re-sincronizar Lotes de UnidadProducto
        UnidadProducto.objects.filter(producto=p).delete()
        if p.stock > Decimal('0.00'):
            UnidadProducto.objects.create(
                producto=p,
                mercado=p.mercado,
                fecha_vencimiento="2027-06-30",
                cantidad=p.stock,
                estado='disponible'
            )

    # 6. Invalidar cachés
    for m in mercados:
        invalidate_mercado_cache(m.id)
    invalidate_mercado_cache(None)

    print(f"[+] Kardex actualizado: {updated_kardex} movimientos reajustados.")
    print("[+] Lotes de UnidadProducto 100% sincronizados.")
    print("[+] ¡Proceso finalizado exitosamente!")


if __name__ == '__main__':
    ejecutar()
