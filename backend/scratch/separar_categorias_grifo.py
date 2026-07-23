import os
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_minimarket.settings')
django.setup()

from inventario.models import Mercado, Categoria, Producto
from inventario.utils import invalidate_mercado_cache


def separar_categorias():
    print("[+] Separando la categoría 'Cigarrillos y Accesorios' en 'Cigarrillos y Tabaco' y 'Auto y Accesorios'...")

    mercados = Mercado.objects.all()

    auto_keywords = ["aceite", "frenos", "bardahl", "cargador", "cable", "usb"]

    for mercado in mercados:
        # 1. Renombrar o buscar Cigarrillos y Accesorios -> Cigarrillos y Tabaco
        cat_cigarros = Categoria.objects.filter(mercado=mercado, nombre__icontains="Cigarrillos").first()
        if cat_cigarros:
            cat_cigarros.nombre = "Cigarrillos y Tabaco"
            cat_cigarros.save()
            print(f"[+] Categoría renombrada para {mercado.nombre}: Cigarrillos y Tabaco")
        else:
            cat_cigarros = Categoria.objects.create(mercado=mercado, nombre="Cigarrillos y Tabaco")

        # 2. Crear categoría Auto y Accesorios
        cat_auto, creado = Categoria.objects.get_or_create(
            mercado=mercado,
            nombre="Auto y Accesorios"
        )
        print(f"[+] Categoría {'creada' if creado else 'encontrada'} para {mercado.nombre}: Auto y Accesorios")

        # 3. Mover productos automotrices y tecnológicos a 'Auto y Accesorios'
        prods = Producto.objects.filter(mercado=mercado)
        moved_count = 0
        for p in prods:
            if any(kw in p.nombre.lower() for kw in auto_keywords):
                p.categoria = cat_auto
                p.save()
                moved_count += 1

        print(f"[+] Se movieron {moved_count} productos automotrices/tecnológicos a 'Auto y Accesorios' en {mercado.nombre}.")

        invalidate_mercado_cache(mercado.id)

    invalidate_mercado_cache(None)
    print("[+] ¡Proceso completado exitosamente!")


if __name__ == '__main__':
    separar_categorias()
