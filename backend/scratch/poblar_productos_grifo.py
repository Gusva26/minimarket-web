import os
import sys
from decimal import Decimal

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_minimarket.settings')
django.setup()

from inventario.models import Mercado, Categoria, Producto, UnidadProducto
from inventario.utils import invalidate_mercado_cache

def agregar_productos_grifo():
    print("[+] Agregando nuevos productos de Minimarket de Grifo (Convenience Store / Listo!)...")

    mercados = list(Mercado.objects.all())
    if not mercados:
        print("[-] No hay mercados registrados.")
        return

    # Definicion de productos por nombre exacto de Categoria (existente)
    nuevos_productos = [
        # BEBIDAS Y GASEOSAS
        ("Bebidas y Gaseosas", [
            ("Red Bull Energy Drink 250ml", "7611675000019", Decimal("5.50"), Decimal("8.50"), Decimal("48"), Decimal("12"), "Unidad"),
            ("Monster Energy Green 473ml", "070847012345", Decimal("6.20"), Decimal("9.90"), Decimal("36"), Decimal("10"), "Unidad"),
            ("Volt Energizante Citrus 500ml", "7750182001234", Decimal("1.80"), Decimal("3.00"), Decimal("60"), Decimal("15"), "Unidad"),
            ("Gatorade Cool Blue 750ml", "052000338753", Decimal("3.20"), Decimal("5.20"), Decimal("40"), Decimal("10"), "Unidad"),
            ("Agua San Luis Con Gas 625ml", "775089000112", Decimal("1.10"), Decimal("2.20"), Decimal("80"), Decimal("20"), "Unidad"),
            ("Coca Cola Sin Azúcar Lata 355ml", "775089000234", Decimal("1.80"), Decimal("3.50"), Decimal("72"), Decimal("18"), "Unidad"),
            ("Fanta Naranja 500ml", "775089000345", Decimal("1.60"), Decimal("2.90"), Decimal("50"), Decimal("12"), "Unidad"),
            ("Sprite 500ml", "775089000456", Decimal("1.60"), Decimal("2.90"), Decimal("45"), Decimal("12"), "Unidad"),
            ("Free Tea Durazno 500ml", "775018200567", Decimal("1.50"), Decimal("2.80"), Decimal("40"), Decimal("10"), "Unidad"),
        ]),

        # CERVEZAS Y LICORES
        ("Cervezas y Licores", [
            ("Pilsen Callao Six Pack Latas 355ml", "775003600101", Decimal("22.50"), Decimal("29.90"), Decimal("24"), Decimal("6"), "Pack"),
            ("Cusqueña Dorada Six Pack Latas 355ml", "775003600202", Decimal("26.00"), Decimal("34.90"), Decimal("20"), Decimal("5"), "Pack"),
            ("Corona Extra Bottle 355ml Pack 4", "750106419123", Decimal("21.00"), Decimal("28.50"), Decimal("18"), Decimal("4"), "Pack"),
            ("Smirnoff Ice Red Bottle 275ml", "500028101234", Decimal("5.80"), Decimal("8.90"), Decimal("30"), Decimal("8"), "Unidad"),
            ("Four Loko Gold 473ml", "853898002123", Decimal("9.50"), Decimal("14.50"), Decimal("24"), Decimal("6"), "Unidad"),
            ("Whisky Johnnie Walker Red Label 750ml", "500026702345", Decimal("45.00"), Decimal("68.00"), Decimal("10"), Decimal("3"), "Botella"),
            ("Ron Cartavio Selecto Black 750ml", "775012300456", Decimal("24.00"), Decimal("36.90"), Decimal("12"), Decimal("3"), "Botella"),
        ]),

        # SNACKS Y SALADOS
        ("Snacks y Salados", [
            ("Lay's Onduladas Jamón Serrano 150g", "775012000567", Decimal("4.20"), Decimal("6.90"), Decimal("40"), Decimal("10"), "Bolsa"),
            ("Doritos Cheese Queso 145g", "775012000678", Decimal("4.00"), Decimal("6.50"), Decimal("45"), Decimal("10"), "Bolsa"),
            ("Cheetos Cheesetris 140g", "775012000789", Decimal("3.50"), Decimal("5.80"), Decimal("35"), Decimal("8"), "Bolsa"),
            ("Pringles Original 124g", "038000138567", Decimal("7.50"), Decimal("11.90"), Decimal("30"), Decimal("6"), "Lata"),
            ("Maní Karinto Salado 100g", "775012000890", Decimal("2.10"), Decimal("3.50"), Decimal("50"), Decimal("12"), "Bolsa"),
            ("Maní Confitado Karinto 100g", "775012000901", Decimal("2.10"), Decimal("3.50"), Decimal("45"), Decimal("12"), "Bolsa"),
            ("Chifle Plátano Karinto 120g", "775012000912", Decimal("2.80"), Decimal("4.50"), Decimal("30"), Decimal("8"), "Bolsa"),
        ]),

        # GOLOSINAS Y CHOCOLATES
        ("Golosinas y Chocolates", [
            ("Sublime Extremo 55g", "775001200123", Decimal("1.80"), Decimal("3.00"), Decimal("60"), Decimal("15"), "Unidad"),
            ("Triángulo D'Onofrio 30g", "775001200234", Decimal("1.20"), Decimal("2.20"), Decimal("70"), Decimal("15"), "Unidad"),
            ("Cua Cua Field 18g", "775005000345", Decimal("0.60"), Decimal("1.20"), Decimal("100"), Decimal("25"), "Unidad"),
            ("Princesa Nestlé 30g", "775001200456", Decimal("1.20"), Decimal("2.20"), Decimal("50"), Decimal("12"), "Unidad"),
            ("Snickers Bar 52g", "040000001234", Decimal("2.50"), Decimal("4.20"), Decimal("40"), Decimal("10"), "Unidad"),
            ("Caramelos Tic Tac Menta 16g", "009800001234", Decimal("1.80"), Decimal("3.20"), Decimal("45"), Decimal("10"), "Cajita"),
        ]),

        # CAFÉ Y COMIDA RÁPIDA
        ("Café y Comida Rápida", [
            ("Café Americano Listo! 12oz", "SERV-CAF-AME", Decimal("1.50"), Decimal("4.90"), Decimal("200"), Decimal("20"), "Vaso"),
            ("Café Cappuccino Listo! 12oz", "SERV-CAF-CAP", Decimal("2.10"), Decimal("6.50"), Decimal("180"), Decimal("20"), "Vaso"),
            ("Empanada de Carne Listo!", "SERV-EMP-CAR", Decimal("2.80"), Decimal("6.20"), Decimal("25"), Decimal("5"), "Unidad"),
            ("Empanada de Pollo Listo!", "SERV-EMP-POL", Decimal("2.80"), Decimal("6.20"), Decimal("25"), Decimal("5"), "Unidad"),
            ("Sandwich Mixto Jamón y Queso Caliente", "SERV-SAN-MIX", Decimal("3.20"), Decimal("7.50"), Decimal("20"), Decimal("5"), "Unidad"),
            ("Croissant de Jamón y Queso", "SERV-CRO-MIX", Decimal("3.50"), Decimal("7.90"), Decimal("15"), Decimal("4"), "Unidad"),
        ]),

        # GALLETAS Y PANADERÍA
        ("Galletas y Panadería", [
            ("Oreo Original Six Pack 216g", "775005000567", Decimal("3.20"), Decimal("5.50"), Decimal("40"), Decimal("10"), "Pack"),
            ("Ritz Crackers 200g", "775005000678", Decimal("2.80"), Decimal("4.80"), Decimal("35"), Decimal("8"), "Paquete"),
            ("Casino Menta Pack 6", "775005000789", Decimal("2.50"), Decimal("4.20"), Decimal("50"), Decimal("12"), "Pack"),
            ("Pan de Molde Blanco Bimbo 480g", "775081000123", Decimal("4.80"), Decimal("7.50"), Decimal("20"), Decimal("5"), "Bolsa"),
        ]),

        # HELADOS Y HIELO
        ("Helados y Hielo", [
            ("Bolsa de Hielo Listo! 3kg", "775099000123", Decimal("2.50"), Decimal("6.50"), Decimal("30"), Decimal("8"), "Bolsa"),
            ("Peziduri Vainilla 1L", "775001200567", Decimal("8.50"), Decimal("14.90"), Decimal("15"), Decimal("4"), "Pote"),
            ("Sin Parar Chocolate 140ml", "775001200678", Decimal("2.80"), Decimal("4.80"), Decimal("40"), Decimal("10"), "Vaso"),
            ("Sublime Paleta 75ml", "775001200789", Decimal("2.20"), Decimal("3.90"), Decimal("45"), Decimal("10"), "Unidad"),
        ]),

        # CIGARRILLOS Y ACCESORIOS
        ("Cigarrillos y Accesorios", [
            ("Lucky Strike Convertibles Pack x 20", "775000400123", Decimal("13.50"), Decimal("18.00"), Decimal("30"), Decimal("8"), "Cajetilla"),
            ("Hamilton Rojo Pack x 20", "775000400234", Decimal("12.00"), Decimal("16.50"), Decimal("25"), Decimal("6"), "Cajetilla"),
            ("Encendedor BIC Grande Variado", "308612345678", Decimal("2.20"), Decimal("4.50"), Decimal("60"), Decimal("15"), "Unidad"),
            ("Aceite Motor Shell Helix Ultra 20W-50 1L", "501198700123", Decimal("22.00"), Decimal("34.00"), Decimal("12"), Decimal("3"), "Botella"),
            ("Líquido de Frenos Bardahl DOT 4 355ml", "075726001234", Decimal("12.00"), Decimal("19.50"), Decimal("10"), Decimal("2"), "Frasco"),
            ("Cargador USB Doble para Auto Listo!", "775099000234", Decimal("8.00"), Decimal("19.90"), Decimal("15"), Decimal("3"), "Unidad"),
            ("Cable USB-C Carga Rápida 1m", "775099000345", Decimal("6.50"), Decimal("16.90"), Decimal("20"), Decimal("4"), "Unidad"),
        ]),
    ]

    total_creados = 0

    for mercado in mercados:
        print(f"[+] Procesando productos para sucursal: {mercado.nombre}...")
        cats_db = {c.nombre.strip().lower(): c for c in Categoria.objects.filter(mercado=mercado)}

        for cat_nombre_ref, prods in nuevos_productos:
            cat_obj = cats_db.get(cat_nombre_ref.strip().lower())
            if not cat_obj:
                print(f"[-] No se encontró la categoría '{cat_nombre_ref}' para {mercado.nombre}")
                continue

            for nom, code, costo, precio, stock, s_min, um in prods:
                # Código único con sufijo por mercado si fuera necesario
                code_unique = f"{code}-{mercado.id}" if not code.startswith("SERV-") else f"{code}-{mercado.id}"

                prod, created = Producto.objects.update_or_create(
                    mercado=mercado,
                    nombre=nom,
                    defaults={
                        'categoria': cat_obj,
                        'codigo_barras': code_unique,
                        'costo': costo,
                        'precio': precio,
                        'stock': stock,
                        'stock_minimo': s_min,
                        'unidad_medida': um,
                    }
                )
                if created:
                    total_creados += 1
                    # Crear unidad de producto inicial
                    UnidadProducto.objects.create(
                        producto=prod,
                        mercado=mercado,
                        fecha_vencimiento="2027-12-31",
                        cantidad=stock,
                        estado='disponible'
                    )

        invalidate_mercado_cache(mercado.id)

    total_prods = Producto.objects.count()
    print(f"[+] ¡Proceso completado! Se agregaron {total_creados} nuevos productos. Total de productos en catálogo: {total_prods}")


if __name__ == '__main__':
    agregar_productos_grifo()
