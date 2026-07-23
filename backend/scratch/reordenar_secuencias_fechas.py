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
from inventario.models import Mercado, Kardex
from compras.models import Compra
from ventas.models import Venta


def reordenar_fechas_y_correlativos():
    print("[+] Reordenando fechas (Mayo 2026 a Julio 2026) y correlativos secuenciales...")

    mercados = list(Mercado.objects.all())
    if not mercados:
        print("[-] No hay mercados.")
        return

    m1 = mercados[0]
    m2 = mercados[1] if len(mercados) > 1 else m1

    # Rango de fechas: Desde el 1 de Mayo de 2026 hasta el 22 de Julio de 2026 (83 días)
    start_date = datetime(2026, 5, 1, 8, 0, 0)
    end_date = datetime(2026, 7, 22, 21, 30, 0)
    total_seconds = int((end_date - start_date).total_seconds())

    # --- 1. Reordenar COMPRAS secuencialmente ---
    compras_m1 = list(Compra.objects.filter(detalles__producto__mercado=m1).distinct().order_by('id'))
    compras_m2 = list(Compra.objects.filter(detalles__producto__mercado=m2).distinct().order_by('id'))
    
    # Compras restantes sin mercado especifico
    compras_todas = list(Compra.objects.all().order_by('id'))

    print(f"[+] Procesando {len(compras_todas)} compras en total...")

    # Asignar fechas crecientes entre Mayo y Julio para Compras
    # Generar N fechas ordenadas cronologicamente
    N_compras = len(compras_todas)
    if N_compras > 0:
        step_seconds = total_seconds // (N_compras + 1)
        
        # Correlativos por sucursal
        seq_c1 = 1
        seq_c2 = 1

        for idx, compra in enumerate(compras_todas):
            sec_offset = step_seconds * (idx + 1) + random.randint(-3600, 3600)
            sec_offset = max(60, min(total_seconds - 60, sec_offset))
            nueva_fecha = timezone.make_aware(start_date + timedelta(seconds=sec_offset))

            # Determinar sucursal a partir del primer producto
            primer_det = compra.detalles.first()
            p_mercado = primer_det.producto.mercado if (primer_det and primer_det.producto) else m1

            if p_mercado == m1:
                serie = 'F001'
                num_seq = seq_c1
                seq_c1 += 1
            else:
                serie = 'F002'
                num_seq = seq_c2
                seq_c2 += 1

            num_str = str(num_seq).zfill(6)

            compra.fecha = nueva_fecha
            compra.tipo_comprobante = 'FACTURA'
            compra.serie_comprobante = serie
            compra.numero_comprobante = num_str
            compra.save()

            # Actualizar Kardex asociado
            prov_nom = compra.proveedor.nombre if compra.proveedor else 'N/A'
            ref_detalle = f"Compra FACTURA {serie}-{num_str} ({prov_nom})"
            Kardex.objects.filter(referencia_tipo='Compra', referencia_id=compra.id).update(
                fecha=nueva_fecha,
                referencia_detalle=ref_detalle
            )

    # --- 2. Reordenar VENTAS secuencialmente ---
    ventas_m1 = list(Venta.objects.filter(mercado=m1).order_by('id'))
    ventas_m2 = list(Venta.objects.filter(mercado=m2).order_by('id'))

    print(f"[+] Procesando {len(ventas_m1)} ventas para Mercado 1 y {len(ventas_m2)} ventas para Mercado 2...")

    # Paso 1: Asignar serie temporal para evitar colisiones de UniqueConstraint
    for idx, v in enumerate(ventas_m1):
        Venta.objects.filter(id=v.id).update(serie=f'TMP1_{v.id}', numero=900000 + idx)
    for idx, v in enumerate(ventas_m2):
        Venta.objects.filter(id=v.id).update(serie=f'TMP2_{v.id}', numero=900000 + idx)

    # Paso 2: Asignar correlativos finales (1, 2, 3...) y fechas cronologicas para Mercado 1
    N_v1 = len(ventas_m1)
    if N_v1 > 0:
        step_v1 = total_seconds // (N_v1 + 1)
        for idx, venta in enumerate(ventas_m1):
            sec_offset = step_v1 * (idx + 1) + random.randint(-1200, 1200)
            sec_offset = max(60, min(total_seconds - 60, sec_offset))
            nueva_fecha = timezone.make_aware(start_date + timedelta(seconds=sec_offset))
            num_seq = idx + 1
            num_str = str(num_seq).zfill(6)

            Venta.objects.filter(id=venta.id).update(
                serie='B001',
                numero=num_seq,
                tipo_comprobante='BOLETA',
                fecha_hora=nueva_fecha
            )

            ref_detalle = f"Venta POS B001-{num_str} ({venta.metodo_pago})"
            Kardex.objects.filter(referencia_tipo='Venta', referencia_id=venta.id).update(
                fecha=nueva_fecha,
                referencia_detalle=ref_detalle
            )

    # Paso 3: Asignar correlativos finales (1, 2, 3...) y fechas cronologicas para Mercado 2
    N_v2 = len(ventas_m2)
    if N_v2 > 0:
        step_v2 = total_seconds // (N_v2 + 1)
        for idx, venta in enumerate(ventas_m2):
            sec_offset = step_v2 * (idx + 1) + random.randint(-1200, 1200)
            sec_offset = max(60, min(total_seconds - 60, sec_offset))
            nueva_fecha = timezone.make_aware(start_date + timedelta(seconds=sec_offset))
            num_seq = idx + 1
            num_str = str(num_seq).zfill(6)

            Venta.objects.filter(id=venta.id).update(
                serie='B002',
                numero=num_seq,
                tipo_comprobante='BOLETA',
                fecha_hora=nueva_fecha
            )

            ref_detalle = f"Venta POS B002-{num_str} ({venta.metodo_pago})"
            Kardex.objects.filter(referencia_tipo='Venta', referencia_id=venta.id).update(
                fecha=nueva_fecha,
                referencia_detalle=ref_detalle
            )

    print("[+] Reordenamiento completado exitosamente con correlativos estrictos (B001-000001, B001-000002...) y fechas desde Mayo 2026!")



if __name__ == '__main__':
    reordenar_fechas_y_correlativos()
