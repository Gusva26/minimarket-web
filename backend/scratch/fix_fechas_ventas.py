import os
import sys
import random
from datetime import datetime, timedelta

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_minimarket.settings')
django.setup()

from django.utils import timezone
from django.db import connection
from ventas.models import Venta
from inventario.models import Kardex


def corregir_fechas_distribuidas():
    print("[+] Distribuyendo las 1,718 ventas uniformemente día por día entre el 1 de Mayo y el 22 de Julio de 2026...")

    ventas = list(Venta.objects.all().order_by('id'))
    total_v = len(ventas)

    start_date = datetime(2026, 5, 1, 7, 30, 0)
    end_date = datetime(2026, 7, 22, 22, 0, 0)
    total_seconds = int((end_date - start_date).total_seconds())

    step = total_seconds / max(1, total_v - 1)

    peak_hours = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]

    # Actualizar mediante raw SQL o batch en memoria para máxima velocidad
    queries = []
    kardex_queries = []

    for idx, v in enumerate(ventas):
        # Calcular fecha incremental + ligera variación de minutos
        day_offset = int((idx / total_v) * 82)
        curr_day = start_date.date() + timedelta(days=day_offset)
        h = random.choice(peak_hours)
        m = random.randint(0, 59)
        s = random.randint(0, 59)
        dt = datetime(curr_day.year, curr_day.month, curr_day.day, h, m, s)
        dt_str = dt.strftime('%Y-%m-%d %H:%M:%S+00')

        queries.append(f"UPDATE ventas_venta SET fecha_hora = '{dt_str}' WHERE id = {v.id};")
        kardex_queries.append(f"UPDATE inventario_kardex SET fecha = '{dt_str}' WHERE referencia_tipo = 'Venta' AND referencia_id = {v.id};")

    print("[+] Ejecutando actualización masiva de fechas en la base de datos PostgreSQL...")
    with connection.cursor() as cursor:
        cursor.execute("\n".join(queries))
        cursor.execute("\n".join(kardex_queries))

    print("[+] Fechas distribuidas con éxito!")


if __name__ == '__main__':
    corregir_fechas_distribuidas()
