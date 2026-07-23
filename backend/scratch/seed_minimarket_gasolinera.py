import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from decimal import Decimal
from datetime import timedelta

import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_minimarket.settings')
django.setup()


from django.utils import timezone
from django.contrib.auth.hashers import make_password

from usuarios.models import Usuario
from inventario.models import Mercado, Categoria, Producto, UnidadProducto, Kardex
from proveedores.models import Proveedor
from ventas.models import Cliente


def populate():
    print("[+] Iniciando carga de datos reales para Minimarket de Gasolinera...")

    # 1. Mercado / Sucursal Principal
    mercado, _ = Mercado.objects.get_or_create(
        nombre="Listo! Express - Av. Javier Prado",
        defaults={
            'ruc': '20601234567',
            'direccion': 'Av. Javier Prado Este 2450, San Borja, Lima',
            'telefono': '01-432-8900',
            'activo': True
        }
    )
    print(f"[+] Sucursal configurada: {mercado.nombre}")

    # 2. Usuarios (Admin y Vendedor)
    admin_user, created_admin = Usuario.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@listoexpress.pe',
            'first_name': 'Administrador',
            'last_name': 'Principal',
            'rol': 'ADMIN',
            'is_superuser': True,
            'is_staff': True,
            'is_active': True,
            'mercado': mercado,
            'password': make_password('admin123')
        }
    )
    if not created_admin:
        admin_user.password = make_password('admin123')
        admin_user.mercado = mercado
        admin_user.save()
    print("[+] Usuario Administrador: admin / admin123")

    vendedor, created_vend = Usuario.objects.get_or_create(
        username='vendedor1',
        defaults={
            'email': 'vendedor1@listoexpress.pe',
            'first_name': 'Carlos',
            'last_name': 'Mendoza',
            'rol': 'VENDEDOR',
            'is_superuser': False,
            'is_staff': False,
            'is_active': True,
            'mercado': mercado,
            'password': make_password('vendedor123')
        }
    )
    if not created_vend:
        vendedor.password = make_password('vendedor123')
        vendedor.mercado = mercado
        vendedor.save()
    print("[+] Usuario Vendedor: vendedor1 / vendedor123")


    # 3. Proveedores Reales de Minimarket
    proveedores_data = [
        {
            'nombre': 'Arca Continental Lindley S.A.',
            'ruc': '20100070970',
            'telefono': '01-614-2000',
            'email': 'ventas@lindley.pe',
            'direccion': 'Av. Javier Prado Este 6210, La Molina'
        },
        {
            'nombre': 'Backus y Johnston S.A.A.',
            'ruc': '20100113610',
            'telefono': '01-311-3000',
            'email': 'pedidos@backus.pe',
            'direccion': 'Av. Nicolás de Piérola 401, Ate'
        },
        {
            'nombre': 'Snacks América Latina S.R.L. (Pepsico)',
            'ruc': '20383840192',
            'telefono': '01-211-5000',
            'email': 'atencion@pepsico.com',
            'direccion': 'Av. Francisco Bolognesi 450, Santa Anita'
        },
        {
            'nombre': 'Nestlé Perú S.A.',
            'ruc': '20100028779',
            'telefono': '01-800-10210',
            'email': 'servicio.cliente@pe.nestle.com',
            'direccion': 'Calle Luis Galvani 483, Ate'
        },
        {
            'nombre': 'Mondelēz Perú S.A.',
            'ruc': '20100010993',
            'telefono': '01-518-8000',
            'email': 'pedidos@mondelez.com',
            'direccion': 'Av. Venezuela 2470, Lima'
        }
    ]


    for p_data in proveedores_data:
        Proveedor.objects.get_or_create(ruc=p_data['ruc'], defaults=p_data)
    print(f"[+] {len(proveedores_data)} Proveedores registrados.")

    # 4. Clientes Reales
    clientes_data = [
        {'nombre': 'Cliente Genérico', 'tipo_documento': 'DNI', 'num_documento': '00000000', 'direccion': 'San Borja'},
        {'nombre': 'Juan Carlos Pérez Gómez', 'tipo_documento': 'DNI', 'num_documento': '45892014', 'telefono': '987654321', 'email': 'jperez@gmail.com', 'direccion': 'Av. Guardia Civil 120, San Borja'},
        {'nombre': 'Empresa Transportes del Sur S.A.C.', 'tipo_documento': 'RUC', 'num_documento': '20548962310', 'telefono': '01-445-9988', 'email': 'contabilidad@transur.pe', 'direccion': 'Av. Circunvalación 890, San Luis'},
    ]
    for c_data in clientes_data:
        Cliente.objects.get_or_create(num_documento=c_data['num_documento'], defaults=c_data)
    print("[+] Clientes frecuentes creados.")

    # 5. Categorías (Minimarket de Gasolinera - SIN productos de limpieza)
    categorias_nombres = [
        "Bebidas y Gaseosas",
        "Cervezas y Licores",
        "Snacks y Salados",
        "Golosinas y Chocolates",
        "Galletas y Panadería",
        "Café y Comida Rápida",
        "Helados y Hielo",
        "Cigarrillos y Accesorios"
    ]

    cat_map = {}
    for cat_name in categorias_nombres:
        cat, _ = Categoria.objects.get_or_create(nombre=cat_name, mercado=mercado)
        cat_map[cat_name] = cat
    print(f"[+] {len(cat_map)} Categorías creadas (excluyendo limpieza).")

    # 6. Catálogo de Productos Reales de Gasolinera
    productos_catalogo = [
        # Bebidas y Gaseosas
        {
            'nombre': 'Inca Kola 600ml',
            'categoria': cat_map['Bebidas y Gaseosas'],
            'precio': Decimal('3.50'),
            'costo': Decimal('2.10'),
            'stock': Decimal('48.00'),
            'stock_minimo': Decimal('10.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7750182001015',
            'dias_vencimiento': 180
        },
        {
            'nombre': 'Coca Cola Sin Azúcar 600ml',
            'categoria': cat_map['Bebidas y Gaseosas'],
            'precio': Decimal('3.50'),
            'costo': Decimal('2.10'),
            'stock': Decimal('48.00'),
            'stock_minimo': Decimal('10.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7750182002029',
            'dias_vencimiento': 180
        },
        {
            'nombre': 'Agua San Luis Sin Gas 625ml',
            'categoria': cat_map['Bebidas y Gaseosas'],
            'precio': Decimal('2.50'),
            'costo': Decimal('1.30'),
            'stock': Decimal('60.00'),
            'stock_minimo': Decimal('15.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7750182003019',
            'dias_vencimiento': 365
        },
        {
            'nombre': 'Energizante Monster Energy 473ml',
            'categoria': cat_map['Bebidas y Gaseosas'],
            'precio': Decimal('8.50'),
            'costo': Decimal('5.80'),
            'stock': Decimal('36.00'),
            'stock_minimo': Decimal('8.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '070847811169',
            'dias_vencimiento': 240
        },
        {
            'nombre': 'Rehidratante Sporade Tropical 500ml',
            'categoria': cat_map['Bebidas y Gaseosas'],
            'precio': Decimal('3.00'),
            'costo': Decimal('1.80'),
            'stock': Decimal('40.00'),
            'stock_minimo': Decimal('10.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7751271000192',
            'dias_vencimiento': 200
        },
        {
            'nombre': 'Red Bull Energy Drink 250ml',
            'categoria': cat_map['Bebidas y Gaseosas'],
            'precio': Decimal('9.00'),
            'costo': Decimal('6.20'),
            'stock': Decimal('30.00'),
            'stock_minimo': Decimal('6.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '9002490100070',
            'dias_vencimiento': 300
        },

        # Cervezas y Licores
        {
            'nombre': 'Cerveza Pilsen Callao Lata 355ml',
            'categoria': cat_map['Cervezas y Licores'],
            'precio': Decimal('5.50'),
            'costo': Decimal('3.80'),
            'stock': Decimal('72.00'),
            'stock_minimo': Decimal('24.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7750036000010',
            'dias_vencimiento': 150
        },
        {
            'nombre': 'Cerveza Cusqueña Dorada Lata 269ml',
            'categoria': cat_map['Cervezas y Licores'],
            'precio': Decimal('6.00'),
            'costo': Decimal('4.20'),
            'stock': Decimal('48.00'),
            'stock_minimo': Decimal('12.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7750036002052',
            'dias_vencimiento': 150
        },
        {
            'nombre': 'Cerveza Corona Extra Botella 355ml',
            'categoria': cat_map['Cervezas y Licores'],
            'precio': Decimal('8.00'),
            'costo': Decimal('5.50'),
            'stock': Decimal('40.00'),
            'stock_minimo': Decimal('10.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7501064191319',
            'dias_vencimiento': 180
        },
        {
            'nombre': 'Six Pack Cerveza Heineken Latas 269ml',
            'categoria': cat_map['Cervezas y Licores'],
            'precio': Decimal('29.90'),
            'costo': Decimal('21.00'),
            'stock': Decimal('15.00'),
            'stock_minimo': Decimal('5.00'),
            'unidad_medida': 'PAQ',
            'codigo_barras': '8712000028212',
            'dias_vencimiento': 180
        },

        # Snacks y Salados
        {
            'nombre': "Papas Lay's Clásicas 160g",
            'categoria': cat_map['Snacks y Salados'],
            'precio': Decimal('7.50'),
            'costo': Decimal('4.90'),
            'stock': Decimal('30.00'),
            'stock_minimo': Decimal('8.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7750885002011',
            'dias_vencimiento': 90
        },
        {
            'nombre': 'Doritos Queso Atrevido 150g',
            'categoria': cat_map['Snacks y Salados'],
            'precio': Decimal('7.90'),
            'costo': Decimal('5.10'),
            'stock': Decimal('25.00'),
            'stock_minimo': Decimal('6.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7750885003056',
            'dias_vencimiento': 90
        },
        {
            'nombre': 'Maní Karinto Salado 100g',
            'categoria': cat_map['Snacks y Salados'],
            'precio': Decimal('3.50'),
            'costo': Decimal('2.20'),
            'stock': Decimal('35.00'),
            'stock_minimo': Decimal('10.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7750885004015',
            'dias_vencimiento': 120
        },
        {
            'nombre': 'Cuates Picantes 90g',
            'categoria': cat_map['Snacks y Salados'],
            'precio': Decimal('2.50'),
            'costo': Decimal('1.50'),
            'stock': Decimal('40.00'),
            'stock_minimo': Decimal('10.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7750885005081',
            'dias_vencimiento': 90
        },

        # Golosinas y Chocolates
        {
            'nombre': 'Chocolate Sublime Clásico 30g',
            'categoria': cat_map['Golosinas y Chocolates'],
            'precio': Decimal('2.50'),
            'costo': Decimal('1.60'),
            'stock': Decimal('60.00'),
            'stock_minimo': Decimal('15.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7613031000019',
            'dias_vencimiento': 180
        },
        {
            'nombre': "Chocolate Triángulo D'Onofrio 30g",
            'categoria': cat_map['Golosinas y Chocolates'],
            'precio': Decimal('2.50'),
            'costo': Decimal('1.60'),
            'stock': Decimal('50.00'),
            'stock_minimo': Decimal('12.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7613031002020',
            'dias_vencimiento': 180
        },
        {
            'nombre': 'Caramelos Halls Menta 10u',
            'categoria': cat_map['Golosinas y Chocolates'],
            'precio': Decimal('2.00'),
            'costo': Decimal('1.20'),
            'stock': Decimal('45.00'),
            'stock_minimo': Decimal('10.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7622210001010',
            'dias_vencimiento': 365
        },
        {
            'nombre': 'Chicle Trident Menta Fuerte 18u',
            'categoria': cat_map['Golosinas y Chocolates'],
            'precio': Decimal('3.50'),
            'costo': Decimal('2.10'),
            'stock': Decimal('40.00'),
            'stock_minimo': Decimal('10.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7622210002024',
            'dias_vencimiento': 365
        },

        # Galletas y Panadería / Comida Rápida
        {
            'nombre': 'Galletas Oreo Paquete 4u',
            'categoria': cat_map['Galletas y Panadería'],
            'precio': Decimal('2.00'),
            'costo': Decimal('1.20'),
            'stock': Decimal('50.00'),
            'stock_minimo': Decimal('12.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7622300001020',
            'dias_vencimiento': 120
        },
        {
            'nombre': 'Galletas Casino Menta 6u',
            'categoria': cat_map['Galletas y Panadería'],
            'precio': Decimal('1.80'),
            'costo': Decimal('1.10'),
            'stock': Decimal('45.00'),
            'stock_minimo': Decimal('10.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7750012001017',
            'dias_vencimiento': 120
        },
        {
            'nombre': 'Pan con Pollo Desmenuzado Listo!',
            'categoria': cat_map['Café y Comida Rápida'],
            'precio': Decimal('8.90'),
            'costo': Decimal('5.20'),
            'stock': Decimal('15.00'),
            'stock_minimo': Decimal('4.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7759900001011',
            'dias_vencimiento': 3
        },
        {
            'nombre': 'Empanada de Carne Listo!',
            'categoria': cat_map['Café y Comida Rápida'],
            'precio': Decimal('6.50'),
            'costo': Decimal('3.80'),
            'stock': Decimal('20.00'),
            'stock_minimo': Decimal('5.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7759900002028',
            'dias_vencimiento': 2
        },
        {
            'nombre': 'Café Capuchino Vaso 12oz',
            'categoria': cat_map['Café y Comida Rápida'],
            'precio': Decimal('6.90'),
            'costo': Decimal('2.50'),
            'stock': Decimal('50.00'),
            'stock_minimo': Decimal('10.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7759900003018',
            'dias_vencimiento': 30
        },

        # Helados y Hielo
        {
            'nombre': "Helado D'Onofrio Sin Parar Chocolate",
            'categoria': cat_map['Helados y Hielo'],
            'precio': Decimal('5.50'),
            'costo': Decimal('3.60'),
            'stock': Decimal('30.00'),
            'stock_minimo': Decimal('8.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7613031005014',
            'dias_vencimiento': 180
        },
        {
            'nombre': 'Bolsón de Hielo en Cubos 3Kg',
            'categoria': cat_map['Helados y Hielo'],
            'precio': Decimal('8.50'),
            'costo': Decimal('4.00'),
            'stock': Decimal('25.00'),
            'stock_minimo': Decimal('5.00'),
            'unidad_medida': 'BOL',
            'codigo_barras': '7759900005012',
            'dias_vencimiento': 365
        },

        # Cigarrillos y Accesorios
        {
            'nombre': 'Cigarrillos Lucky Strike Red 20u',
            'categoria': cat_map['Cigarrillos y Accesorios'],
            'precio': Decimal('16.00'),
            'costo': Decimal('12.50'),
            'stock': Decimal('30.00'),
            'stock_minimo': Decimal('6.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '7702001000105',
            'dias_vencimiento': 365
        },
        {
            'nombre': 'Encendedor Tokai Desechable',
            'categoria': cat_map['Cigarrillos y Accesorios'],
            'precio': Decimal('2.50'),
            'costo': Decimal('1.20'),
            'stock': Decimal('50.00'),
            'stock_minimo': Decimal('10.00'),
            'unidad_medida': 'UND',
            'codigo_barras': '4904650000102',
            'dias_vencimiento': 365
        }
    ]

    hoy = timezone.now().date()
    productos_creados = 0

    for p_info in productos_catalogo:
        dias_venc = p_info.pop('dias_vencimiento')
        producto, created = Producto.objects.get_or_create(
            codigo_barras=p_info['codigo_barras'],
            mercado=mercado,
            defaults={**p_info, 'mercado': mercado}
        )
        if not created:
            for k, v in p_info.items():
                setattr(producto, k, v)
            producto.mercado = mercado
            producto.save()

        # Crear Lotes FEFO (UnidadProducto) para el producto
        UnidadProducto.objects.filter(producto=producto, mercado=mercado).delete()

        cant_total = int(producto.stock)
        lote_1_cant = cant_total // 2
        lote_2_cant = cant_total - lote_1_cant

        # Lote 1: próximo a vencer
        fecha_venc_1 = hoy + timedelta(days=dias_venc)
        UnidadProducto.objects.create(
            producto=producto,
            mercado=mercado,
            fecha_vencimiento=fecha_venc_1,
            cantidad=Decimal(str(lote_1_cant)),
            estado='disponible'
        )

        # Lote 2: fecha posterior
        fecha_venc_2 = hoy + timedelta(days=dias_venc + 60)
        UnidadProducto.objects.create(
            producto=producto,
            mercado=mercado,
            fecha_vencimiento=fecha_venc_2,
            cantidad=Decimal(str(lote_2_cant)),
            estado='disponible'
        )

        # Kardex Inicial
        Kardex.objects.create(
            producto=producto,
            mercado=mercado,
            tipo_movimiento='ENTRADA',
            cantidad=producto.stock,
            saldo_anterior=Decimal('0.00'),
            saldo_nuevo=producto.stock,
            referencia_tipo='Inventario Inicial',
            referencia_detalle='Carga Inicial de Productos para Minimarket Gasolinera',
            usuario=admin_user
        )

        productos_creados += 1

    print(f"[+] Exito! Se cargaron {productos_creados} productos reales con lotes FEFO e Historial Kardex.")
    print("=" * 60)
    print("DATOS DE ACCESO:")
    print("  ADMINISTRADOR:")
    print("    Usuario:  admin")
    print("    Clave:    admin123")
    print("  VENDEDOR:")
    print("    Usuario:  vendedor1")
    print("    Clave:    vendedor123")
    print("=" * 60)


if __name__ == '__main__':
    populate()
