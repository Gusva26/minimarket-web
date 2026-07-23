import os
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_minimarket.settings')
django.setup()

from inventario.models import Categoria, Producto, UnidadProducto
from inventario.utils import invalidate_mercado_cache


def eliminar_auto_accesorios():
    print("[+] Eliminando la categoría 'Auto y Accesorios' y todos sus productos asociados...")

    cats_auto = Categoria.objects.filter(nombre__icontains="Auto")
    cat_ids = list(cats_auto.values_list('id', flat=True))

    # Buscar productos en la categoria o con palabras clave
    auto_keywords = ["aceite", "frenos", "bardahl", "cargador", "cable"]
    prods_auto = Producto.objects.filter(categoria_id__in=cat_ids)

    # Eliminar unidades de producto asociadas
    unidades_del, _ = UnidadProducto.objects.filter(producto__in=prods_auto).delete()
    prods_del, _ = prods_auto.delete()
    cats_del, _ = cats_auto.delete()

    print(f"[+] Eliminación completada:")
    print(f"    - Unidades de producto eliminadas: {unidades_del}")
    print(f"    - Productos eliminados:          {prods_del}")
    print(f"    - Categorías eliminadas:         {cats_del}")

    invalidate_mercado_cache(None)
    print("[+] Memoria caché invalidada. ¡Todo listo!")


if __name__ == '__main__':
    eliminar_auto_accesorios()
