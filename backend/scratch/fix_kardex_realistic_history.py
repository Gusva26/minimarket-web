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
from usuarios.models import Usuario
from django.core.cache import cache

def fix_realistic_kardex():
    print("Iniciando reconstrucción con ventas realistas graduales y asignación completa de usuarios...")

    default_user = Usuario.objects.filter(is_active=True).order_by('id').first()
    if not default_user:
        print("ERROR: No se encontró usuario activo en la BD.")
        return

    today = datetime.date.today()
    now = datetime.datetime.now()

    # 1. Asignar usuario por defecto a cualquier Kardex que no tenga usuario
    Kardex.objects.filter(usuario__isnull=True).update(usuario=default_user)

    # 2. Configurar Productos de Prueba con Historial de Ventas Graduales (1 a 4 unidades por ticket)
    # Lista de configuraciones por producto
    # (producto_id, target_stock, inicial_stock, es_vencido, dias_vencimiento)
    configs = [
        # SUCURSAL 1 (Javier Prado)
        (57, Decimal('15.00'), Decimal('15.00'), False, 3),   # Sandwich Triple -> Vence en 3 días (Crítico)
        (1, Decimal('20.00'), Decimal('20.00'), False, 18),   # Inca Kola -> Vence en 18 días (Advertencia)
        (51, Decimal('12.00'), Decimal('12.00'), True, -5),   # Empanada Carne -> Venció hace 5 días
        (27, Decimal('2.00'), Decimal('15.00'), False, 120),  # Pisco Queirolo -> Stock 2.00
        (86, Decimal('3.00'), Decimal('15.00'), False, 150),  # Whisky Red Label -> Stock 3.00
        (69, Decimal('0.00'), Decimal('12.00'), False, 90),   # Lucky Strike -> Stock 0.00

        # SUCURSAL 2 (Benavides)
        (58, Decimal('18.00'), Decimal('18.00'), False, 2),   # Sandwich Triple -> Vence en 2 días (Crítico M2)
        (18, Decimal('25.00'), Decimal('25.00'), False, 14),  # Free Tea -> Vence en 14 días (Advertencia M2)
        (52, Decimal('10.00'), Decimal('10.00'), True, -4),   # Empanada Carne -> Venció hace 4 días M2
        (28, Decimal('2.00'), Decimal('14.00'), False, 110),  # Pisco Queirolo -> Stock 2.00 M2
        (22, Decimal('4.00'), Decimal('16.00'), False, 90),   # Cusqueña Dorada -> Stock 4.00 M2
        (70, Decimal('0.00'), Decimal('15.00'), False, 80),   # Lucky Strike -> Stock 0.00 M2
    ]


    with transaction.atomic():
        for prod_id, target_stock, init_stock, is_vencido, days_venc in configs:
            try:
                p = Producto.objects.get(id=prod_id)
            except Producto.DoesNotExist:
                continue

            # Eliminar movimientos de Kardex anteriores irrealmente gigantes de este producto
            Kardex.objects.filter(producto=p).delete()

            mercado = p.mercado
            serie = "B001" if mercado.id == 1 else "B002"
            
            running = init_stock
            
            # Movimiento 1: Inventario Inicial (hace 7 días)
            fecha_inicial = now - datetime.timedelta(days=7)
            Kardex.objects.create(
                producto=p,
                mercado=mercado,
                usuario=default_user,
                tipo_movimiento='ENTRADA',
                cantidad=init_stock,
                saldo_anterior=Decimal('0.00'),
                saldo_nuevo=init_stock,
                referencia_tipo='Inventario Inicial',
                referencia_detalle='Carga Inicial de Stock por Auditoría',
                fecha=fecha_inicial
            )

            # Si target_stock < init_stock, generar ventas graduales de 1 a 3 unidades por ticket
            to_reduce = init_stock - target_stock
            ticket_num = 100 + (p.id % 50)
            day_offset = 6

            while to_reduce > 0:
                sale_qty = min(to_reduce, Decimal(str(1 + ((ticket_num * 2) % 3))))
                if sale_qty <= 0:
                    break

                saldo_ant = running
                running -= sale_qty
                to_reduce -= sale_qty

                fecha_venta = now - datetime.timedelta(days=max(0, day_offset), minutes=(ticket_num * 17) % 300)
                ticket_num += 1
                doc_num = f"{serie}-{ticket_num:06d}"

                Kardex.objects.create(
                    producto=p,
                    mercado=mercado,
                    usuario=default_user,
                    tipo_movimiento='SALIDA',
                    cantidad=sale_qty,
                    saldo_anterior=saldo_ant,
                    saldo_nuevo=running,
                    referencia_tipo='Venta POS',
                    referencia_detalle=f"Venta POS {doc_num} (Efectivo)",
                    fecha=fecha_venta
                )
                if day_offset > 0:
                    day_offset -= 1


            # Actualizar Producto.stock
            p.stock = running
            p.save()

            # Configurar Lote (UnidadProducto)
            UnidadProducto.objects.filter(producto=p).delete()
            if running > Decimal('0.00'):
                UnidadProducto.objects.create(
                    producto=p,
                    mercado=mercado,
                    fecha_vencimiento=today + datetime.timedelta(days=days_venc),
                    cantidad=running,
                    estado='vencido' if is_vencido else 'disponible'
                )
            print(f"PRODUCTO AUDITADO OK: {p.nombre} (ID {p.id} - Sucursal {mercado.id}) -> Stock: {p.stock}, Usuario: {default_user.username}")

        # Garantizar que ningún Kardex en la BD se quede sin usuario
        Kardex.objects.filter(usuario__isnull=True).update(usuario=default_user)

        cache.clear()
        print("\nÉXITO COMPLETO: Kardex reconstruido con ventas graduales realistas, saldos rojos para salidas y 100% de usuarios asignados.")

if __name__ == '__main__':
    fix_realistic_kardex()
