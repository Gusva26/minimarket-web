import os
import sys
import random
from datetime import datetime, timedelta
from decimal import Decimal

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_minimarket.settings')
django.setup()

from django.utils import timezone
from inventario.models import Mercado, Producto, Kardex
from ventas.models import Venta, VentaDetalle, Caja, Cliente
from usuarios.models import Usuario


def generar_ventas_variadas_fast():
    print("[+] Limpiando ventas anteriores...")
    VentaDetalle.objects.all().delete()
    Venta.objects.all().delete()

    mercados = list(Mercado.objects.all())
    if not mercados:
        print("[-] No hay mercados.")
        return

    m1 = mercados[0]
    m2 = mercados[1] if len(mercados) > 1 else m1

    cajas = list(Caja.objects.all())
    vendedores = list(Usuario.objects.filter(rol__in=['VENDEDOR', 'ADMINISTRADOR']))

    clientes_data = [
        ("Inversiones Sacatuca S.A.C.", "RUC", "20601234567", "Av. Primavera 450, Surco"),
        ("Corporación Gastronómica del Sur", "RUC", "20519283741", "Calle Los Pinos 120, Miraflores"),
        ("Constructora & Servicios Perú S.A.", "RUC", "20481920391", "Av. Javier Prado 2100, San Isidro"),
        ("Comercial Don Pepe E.I.R.L.", "RUC", "20391029384", "Av. Benavides 1890, Surco"),
        ("Juan Carlos Mendoza", "DNI", "45892019", "Calle las Flores 123"),
        ("María Elena Torres", "DNI", "71293048", "Av. Arequipa 550"),
        ("Carlos Alberto Benavides", "DNI", "10293847", "Jr. Huallaga 450"),
        ("Ana Sofía Ruiz", "DNI", "73829102", "Av. Larco 880"),
        ("Pedro Luis Gómez", "DNI", "48291039", "Calle San Martín 320"),
    ]

    clientes_objs = []
    for nom, t_doc, num_doc, dir_f in clientes_data:
        c, _ = Cliente.objects.get_or_create(
            num_documento=num_doc,
            defaults={'nombre': nom, 'tipo_documento': t_doc, 'direccion': dir_f}
        )
        clientes_objs.append(c)

    clientes_ruc = [c for c in clientes_objs if c.tipo_documento == 'RUC']
    clientes_dni = [c for c in clientes_objs if c.tipo_documento == 'DNI']

    seq_m1 = {'TICKET': 1, 'BOLETA': 1, 'FACTURA': 1}
    seq_m2 = {'TICKET': 1, 'BOLETA': 1, 'FACTURA': 1}

    prods_m1 = list(Producto.objects.filter(mercado=m1))
    prods_m2 = list(Producto.objects.filter(mercado=m2))

    start_date = datetime(2026, 5, 1)
    end_date = datetime(2026, 7, 22)
    delta_days = (end_date - start_date).days

    ventas_objs = []
    detalles_objs = []
    kardex_objs = []

    peak_hours = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]

    print(f"[+] Preparando ventas variadas para {delta_days} días (Mayo - Julio 2026)...")

    for day_idx in range(delta_days + 1):
        curr_day = start_date + timedelta(days=day_idx)

        for mercado_target, prods_pool, seq_dict in [(m1, prods_m1, seq_m1), (m2, prods_m2, seq_m2)]:
            if not prods_pool:
                continue

            num_ventas_hoy = random.randint(6, 15)
            caja_target = random.choice([c for c in cajas if c.mercado == mercado_target]) if cajas else None
            vendedor_target = random.choice([v for v in vendedores if v.mercado == mercado_target or v.mercado is None])

            for _ in range(num_ventas_hoy):
                h = random.choice(peak_hours)
                m = random.randint(0, 59)
                s = random.randint(0, 59)
                fecha_venta = timezone.make_aware(curr_day.replace(hour=h, minute=m, second=s))

                r_type = random.random()
                if r_type < 0.60:
                    tipo_doc = 'BOLETA'
                    serie_doc = f"B00{1 if mercado_target == m1 else 2}"
                    cliente_target = random.choice(clientes_dni) if (clientes_dni and random.random() > 0.3) else None
                elif r_type < 0.85:
                    tipo_doc = 'FACTURA'
                    serie_doc = f"F00{1 if mercado_target == m1 else 2}"
                    cliente_target = random.choice(clientes_ruc)
                else:
                    tipo_doc = 'TICKET'
                    serie_doc = f"T00{1 if mercado_target == m1 else 2}"
                    cliente_target = None

                num_seq = seq_dict[tipo_doc]
                seq_dict[tipo_doc] += 1
                num_str = str(num_seq).zfill(6)

                metodo = random.choice(['Efectivo', 'Efectivo', 'Yape', 'Plin'])
                num_op = f"OP-{random.randint(100000, 999999)}" if metodo in ['Yape', 'Plin'] else ''

                v = Venta(
                    mercado=mercado_target,
                    caja=caja_target,
                    usuario=vendedor_target,
                    cliente=cliente_target,
                    tipo_comprobante=tipo_doc,
                    serie=serie_doc,
                    numero=num_seq,
                    metodo_pago=metodo,
                    num_operacion=num_op,
                    estado='COMPLETADA',
                    fecha_hora=fecha_venta,
                    total=Decimal('0.00'),
                    subtotal=Decimal('0.00'),
                    igv=Decimal('0.00'),
                    costo_total=Decimal('0.00'),
                    monto_recibido=Decimal('0.00'),
                    vuelto=Decimal('0.00')
                )
                ventas_objs.append((v, prods_pool, num_str, metodo, fecha_venta, vendedor_target, mercado_target, tipo_doc, serie_doc))

    print(f"[+] Bulk-creating {len(ventas_objs)} Ventas...")
    created_ventas = Venta.objects.bulk_create([item[0] for item in ventas_objs])

    print("[+] Bulk-creating VentaDetalles y Kardex...")
    for idx, (v_obj, prods_pool, num_str, metodo, fecha_venta, vendedor_target, mercado_target, tipo_doc, serie_doc) in enumerate(ventas_objs):
        v_db = created_ventas[idx]
        num_items = random.randint(1, 4)
        prods_venta = random.sample(prods_pool, min(num_items, len(prods_pool)))
        total_v = Decimal('0.00')
        costo_v = Decimal('0.00')

        for p in prods_venta:
            qty = Decimal(str(random.randint(1, 3)))
            precio_u = p.precio
            subt = qty * precio_u
            costo_u = p.costo
            total_v += subt
            costo_v += qty * costo_u

            detalles_objs.append(
                VentaDetalle(
                    venta=v_db,
                    producto=p,
                    cantidad=qty,
                    precio_unitario=precio_u,
                    costo_unitario=costo_u,
                    subtotal=subt
                )
            )

            kardex_objs.append(
                Kardex(
                    producto=p,
                    mercado=mercado_target,
                    tipo_movimiento='SALIDA',
                    cantidad=qty,
                    saldo_anterior=p.stock,
                    saldo_nuevo=max(Decimal('0.00'), p.stock - qty),
                    referencia_tipo='Venta',
                    referencia_id=v_db.id,
                    referencia_detalle=f'Venta {tipo_doc} {serie_doc}-{num_str} ({metodo})',
                    usuario=vendedor_target,
                    fecha=fecha_venta
                )
            )

        subt_v = (total_v / Decimal('1.18')).quantize(Decimal('0.01'))
        igv_v = total_v - subt_v
        monto_rec = total_v + Decimal(random.choice(['0.00', '2.00', '5.00'])) if metodo == 'Efectivo' else total_v
        vuelto_v = max(Decimal('0.00'), monto_rec - total_v)

        v_db.subtotal = subt_v
        v_db.igv = igv_v
        v_db.total = total_v
        v_db.costo_total = costo_v
        v_db.monto_recibido = monto_rec
        v_db.vuelto = vuelto_v

    print("[+] Actualizando totales de ventas...")
    Venta.objects.bulk_update(created_ventas, fields=['subtotal', 'igv', 'total', 'costo_total', 'monto_recibido', 'vuelto'])

    print(f"[+] Insertando {len(detalles_objs)} detalles de venta...")
    VentaDetalle.objects.bulk_create(detalles_objs)

    print(f"[+] Insertando {len(kardex_objs)} registros de Kardex...")
    Kardex.objects.bulk_create(kardex_objs)

    print(f"[+] ¡Proceso completado exitosamente! {len(created_ventas)} ventas variadas insertadas (Facturas, Boletas, Tickets).")


if __name__ == '__main__':
    generar_ventas_variadas_fast()
