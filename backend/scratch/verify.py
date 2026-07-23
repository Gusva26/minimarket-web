import os
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_minimarket.settings')
django.setup()


from compras.models import Compra
from ventas.models import Venta

print("=== COMPRAS REORDENADAS ===")
for c in Compra.objects.all().order_by('fecha')[:8]:
    dt_str = c.fecha.strftime('%d/%m/%Y %H:%M')
    prov = c.proveedor.nombre if c.proveedor else 'N/A'
    print(f"ID:{c.id:<4} | {c.tipo_comprobante:<7} {c.serie_comprobante}-{c.numero_comprobante} | Fecha: {dt_str} | Proveedor: {prov}")

print("\n=== VENTAS MERCADO 1 (AV. JAVIER PRADO) ===")
for v in Venta.objects.filter(mercado_id=1).order_by('fecha_hora')[:8]:
    dt_str = v.fecha_hora.strftime('%d/%m/%Y %H:%M')
    num_str = str(v.numero).zfill(6)
    print(f"ID:{v.id:<4} | {v.tipo_comprobante:<7} {v.serie}-{num_str} | Fecha: {dt_str} | Total: S/ {v.total}")

print("\n=== VENTAS MERCADO 2 (AV. BENAVIDES) ===")
for v in Venta.objects.filter(mercado_id=2).order_by('fecha_hora')[:8]:
    dt_str = v.fecha_hora.strftime('%d/%m/%Y %H:%M')
    num_str = str(v.numero).zfill(6)
    print(f"ID:{v.id:<4} | {v.tipo_comprobante:<7} {v.serie}-{num_str} | Fecha: {dt_str} | Total: S/ {v.total}")
