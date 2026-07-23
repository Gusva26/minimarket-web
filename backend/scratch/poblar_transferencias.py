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
from inventario.models import Mercado, Producto, Transferencia, TransferenciaDetalle
from usuarios.models import Usuario
from inventario.utils import invalidate_mercado_cache


def poblar_transferencias():
    print("[+] Poblando transferencias entre sucursales...")

    m1 = Mercado.objects.get(id=1) # Av. Javier Prado
    m2 = Mercado.objects.get(id=2) # Av. Benavides

    u1 = Usuario.objects.filter(mercado=m1).first() or Usuario.objects.filter(is_superuser=True).first()
    u2 = Usuario.objects.filter(mercado=m2).first() or Usuario.objects.filter(is_superuser=True).first()

    prods_m1 = list(Producto.objects.filter(mercado=m1))
    prods_m2 = list(Producto.objects.filter(mercado=m2))

    if not prods_m1 or not prods_m2:
        print("[-] No hay productos suficientes para realizar transferencias.")
        return

    # Limpiar transferencias anteriores si existen
    Transferencia.objects.all().delete()
    print("[+] Registro anterior de transferencias limpiado.")

    start_date = datetime(2026, 6, 1, 9, 0, 0)
    
    transferencias_data = [
        (m1, m2, u1, u2, 'COMPLETADA', 'Reabastecimiento de bebidas energizantes por alta demanda', 2),
        (m2, m1, u2, u1, 'COMPLETADA', 'Transferencia de stock de licores para evento de fin de semana', 5),
        (m1, m2, u1, u2, 'COMPLETADA', 'Redistribución de snacks salados y frutos secos', 9),
        (m2, m1, u2, u1, 'COMPLETADA', 'Envío de bolsas de hielo y helados en pote', 14),
        (m1, m2, u1, u2, 'CANCELADA', 'Transferencia solicitada por error de pedido interno', 18),
        (m2, m1, u2, u1, 'COMPLETADA', 'Rebalanceo de golosinas y chocolates entre tiendas', 22),
        (m1, m2, u1, u2, 'COMPLETADA', 'Transferencia de accesorios para autos y aceites de motor', 28),
        (m2, m1, u2, u1, 'COMPLETADA', 'Envío de insumos de cafetería y empanadas congeladas', 35),
        (m1, m2, u1, u2, 'EN_TRANSITO', 'Traslado en ruta de cigarrillos y encendedores BIC', 42),
        (m2, m1, u2, u1, 'COMPLETADA', 'Reposición de galletas y pan de molde Bimbo', 46),
        (m1, m2, u1, u2, 'EN_TRANSITO', 'Despacho urgente de agua embotellada y energizantes Volt', 50),
        (m2, m1, u2, u1, 'COMPLETADA', 'Transferencia de cierre de mes de licores premium', 51),
    ]

    tot_trans = 0
    tot_detalles = 0

    for orig, dest, u_env, u_rec, est, obs, day_offset in transferencias_data:
        dt_envio = timezone.make_aware(start_date + timedelta(days=day_offset, hours=random.randint(0, 4)))
        dt_recep = (dt_envio + timedelta(hours=random.randint(2, 6))) if est == 'COMPLETADA' else None


        t = Transferencia.objects.create(
            mercado_origen=orig,
            mercado_destino=dest,
            usuario_envio=u_env,
            usuario_recepcion=u_rec if est == 'COMPLETADA' else None,
            fecha_envio=dt_envio,
            fecha_recepcion=dt_recep,
            estado=est,
            observaciones=obs
        )
        tot_trans += 1

        # Seleccionar 2-4 productos de origen y buscar correspondientes en destino
        prods_origen_pool = prods_m1 if orig == m1 else prods_m2
        prods_destino_pool = prods_m2 if orig == m1 else prods_m1

        sample_prods = random.sample(prods_origen_pool, min(3, len(prods_origen_pool)))
        for p_orig in sample_prods:
            # Buscar mismo producto en destino por nombre
            p_dest = next((p for p in prods_destino_pool if p.nombre == p_orig.nombre), None)
            
            cant = Decimal(str(random.randint(10, 50)))
            f_venc = (dt_envio + timedelta(days=random.randint(180, 360))).date()

            TransferenciaDetalle.objects.create(
                transferencia=t,
                producto_origen=p_orig,
                producto_destino=p_dest,
                cantidad=cant,
                fecha_vencimiento=f_venc
            )
            tot_detalles += 1

    print(f"[+] Se crearon {tot_trans} transferencias con {tot_detalles} detalles de productos registrados.")
    invalidate_mercado_cache(None)


if __name__ == '__main__':
    poblar_transferencias()
