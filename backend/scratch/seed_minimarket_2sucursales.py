import os
import sys
import random
from decimal import Decimal
from datetime import timedelta

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_minimarket.settings')
django.setup()

from django.db import connection, transaction
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from usuarios.models import Usuario
from inventario.models import Mercado, Categoria, Producto, Kardex, UnidadProducto, Transferencia, TransferenciaDetalle
from proveedores.models import Proveedor
from ventas.models import Cliente, Caja, Venta, VentaDetalle
from compras.models import Compra, DetalleCompra


def reset_database_cascade():
    with connection.cursor() as cursor:
        tables = [
            'ventas_ventadetalle',
            'ventas_venta',
            'ventas_caja',
            'ventas_cliente',
            'compras_detallecompra',
            'compras_compra',
            'proveedores_proveedor',
            'inventario_transferenciadetalle',
            'inventario_transferencia',
            'inventario_kardex',
            'inventario_unidadproducto',
            'inventario_producto',
            'inventario_categoria',
            'usuarios_usuario',
            'inventario_mercado',
        ]
        sql = f"TRUNCATE TABLE {', '.join(tables)} RESTART IDENTITY CASCADE;"
        cursor.execute(sql)


def populate_full():
    print("[+] Limpiando base de datos con TRUNCATE RESTART IDENTITY...")
    reset_database_cascade()

    with transaction.atomic():
        print("[+] Creando 2 Sucursales (Mercados)...")
        mercado1 = Mercado.objects.create(
            nombre='Listo! Express - Av. Javier Prado',
            ruc='20518923019',
            direccion='Av. Javier Prado Este 4510, Surco, Lima',
            telefono='01-435-9000',
            activo=True
        )

        mercado2 = Mercado.objects.create(
            nombre='Listo! Express - Av. Benavides',
            ruc='20518923019',
            direccion='Av. Alfredo Benavides 2190, Miraflores, Lima',
            telefono='01-446-8200',
            activo=True
        )

        # 2. Administradores (1 por sucursal) + Superusuario + Vendedores
        super_admin = Usuario.objects.create(
            username='admin', email='superadmin@listoexpress.pe',
            first_name='Super', last_name='Administrador', rol='ADMIN',
            is_superuser=True, is_staff=True, is_active=True, mercado=mercado1,
            password=make_password('admin123')
        )

        admin1_jp = Usuario.objects.create(
            username='admin_javierprado', email='admin.jp@listoexpress.pe',
            first_name='Marco', last_name='Rivas', rol='ADMIN',
            is_staff=True, is_active=True, mercado=mercado1,
            password=make_password('admin123')
        )

        admin1_ben = Usuario.objects.create(
            username='admin_benavides', email='admin.ben@listoexpress.pe',
            first_name='Renzo', last_name='Castillo', rol='ADMIN',
            is_staff=True, is_active=True, mercado=mercado2,
            password=make_password('admin123')
        )

        vendedor_jp = Usuario.objects.create(
            username='vendedor_javierprado', email='caja.jp@listoexpress.pe',
            first_name='Carlos', last_name='Mendoza', rol='VENDEDOR',
            is_active=True, mercado=mercado1,
            password=make_password('vendedor123')
        )

        vendedor_ben = Usuario.objects.create(
            username='vendedor_benavides', email='caja.ben@listoexpress.pe',
            first_name='Lucía', last_name='Fernández', rol='VENDEDOR',
            is_active=True, mercado=mercado2,
            password=make_password('vendedor123')
        )

        # 3. Categorías Existentes (Misma lista en ambas sucursales)
        cat_names = [
            'Bebidas y Gaseosas',
            'Cervezas y Licores',
            'Snacks y Salados',
            'Golosinas y Chocolates',
            'Café y Comida Rápida',
            'Galletas y Panadería',
            'Helados y Hielo',
            'Cigarrillos y Accesorios'
        ]

        cats_m1 = {name: Categoria.objects.create(nombre=name, mercado=mercado1) for name in cat_names}
        cats_m2 = {name: Categoria.objects.create(nombre=name, mercado=mercado2) for name in cat_names}

        # 4. Proveedores Reales
        prov_lindley = Proveedor.objects.create(nombre='Arca Continental Lindley S.A.', ruc='20100070970', telefono='01-614-2000', email='ventas@lindley.pe', direccion='Av. Javier Prado Este 6210, La Molina')
        prov_backus = Proveedor.objects.create(nombre='Backus y Johnston S.A.A.', ruc='20100113610', telefono='01-311-3000', email='pedidos@backus.pe', direccion='Av. Nicolás de Piérola 401, Ate')
        prov_pepsico = Proveedor.objects.create(nombre='Snacks América Latina (Pepsico)', ruc='20383840192', telefono='01-211-5000', email='atencion@pepsico.com', direccion='Av. Francisco Bolognesi 450, Santa Anita')
        prov_nestle = Proveedor.objects.create(nombre='Nestlé Perú S.A.', ruc='20100028779', telefono='01-800-10210', email='servicio@nestle.pe', direccion='Calle Luis Galvani 483, Ate')
        prov_mondelez = Proveedor.objects.create(nombre='Mondelēz Perú S.A.', ruc='20100010993', telefono='01-518-8000', email='pedidos@mondelez.com', direccion='Av. Venezuela 2470, Lima')

        # 5. Clientes Reales
        cliente_generico = Cliente.objects.create(nombre='Cliente Genérico', tipo_documento='DNI', num_documento='00000000', direccion='San Borja')
        cliente_1 = Cliente.objects.create(nombre='Juan Carlos Pérez Gómez', tipo_documento='DNI', num_documento='45892014', telefono='987654321', email='jperez@gmail.com', direccion='Av. Guardia Civil 120, San Borja')
        cliente_2 = Cliente.objects.create(nombre='María Elena Torres Ríos', tipo_documento='DNI', num_documento='41239874', telefono='912345678', email='mtorres@outlook.com', direccion='Av. Larco 450, Miraflores')
        cliente_3 = Cliente.objects.create(nombre='Empresa Transportes del Sur S.A.C.', tipo_documento='RUC', num_documento='20548962310', telefono='01-445-9988', email='contabilidad@transur.pe', direccion='Av. Circunvalación 890, San Luis')

        # 6. Catálogo de Productos Reales (Ampliados)
        # Formato: (Nombre, Categoria, PrecioVenta, Costo, StockInicial_M1, StockInicial_M2, StockMin_M1, StockMin_M2, EAN, DiasVenc, Prov)
        prod_definitions = [
            # BEBIDAS
            ('Inca Kola 600ml', 'Bebidas y Gaseosas', Decimal('3.50'), Decimal('2.10'), Decimal('100.00'), Decimal('80.00'), Decimal('15.00'), Decimal('15.00'), '7750182001015', 180, prov_lindley),
            ('Coca Cola Sin Azúcar 600ml', 'Bebidas y Gaseosas', Decimal('3.50'), Decimal('2.10'), Decimal('90.00'), Decimal('70.00'), Decimal('15.00'), Decimal('15.00'), '7750182002029', 180, prov_lindley),
            ('Agua San Luis 625ml', 'Bebidas y Gaseosas', Decimal('2.50'), Decimal('1.30'), Decimal('120.00'), Decimal('100.00'), Decimal('20.00'), Decimal('20.00'), '7750182003019', 365, prov_lindley),
            ('Monster Energy 473ml', 'Bebidas y Gaseosas', Decimal('8.50'), Decimal('5.80'), Decimal('2.00'), Decimal('45.00'), Decimal('15.00'), Decimal('10.00'), '070847811169', 240, prov_lindley), # BAJO STOCK M1
            ('Red Bull 250ml', 'Bebidas y Gaseosas', Decimal('9.00'), Decimal('6.20'), Decimal('40.00'), Decimal('50.00'), Decimal('10.00'), Decimal('10.00'), '9002490100070', 300, prov_lindley),
            ('Sporade Tropical 500ml', 'Bebidas y Gaseosas', Decimal('3.00'), Decimal('1.80'), Decimal('60.00'), Decimal('50.00'), Decimal('10.00'), Decimal('10.00'), '7751271000192', 200, prov_lindley),
            ('Volt Energizante 500ml', 'Bebidas y Gaseosas', Decimal('3.00'), Decimal('1.70'), Decimal('50.00'), Decimal('0.00'), Decimal('10.00'), Decimal('15.00'), '7751271000208', 180, prov_lindley), # SIN STOCK M2
            ('Fanta Naranja 600ml', 'Bebidas y Gaseosas', Decimal('3.50'), Decimal('2.10'), Decimal('45.00'), Decimal('40.00'), Decimal('10.00'), Decimal('10.00'), '7750182004016', 180, prov_lindley),
            ('Free Tea Durazno 500ml', 'Bebidas y Gaseosas', Decimal('3.20'), Decimal('1.90'), Decimal('35.00'), Decimal('30.00'), Decimal('10.00'), Decimal('10.00'), '7751271000314', 150, prov_lindley),

            # CERVEZAS Y LICORES
            ('Pilsen Callao Lata 355ml', 'Cervezas y Licores', Decimal('5.50'), Decimal('3.80'), Decimal('150.00'), Decimal('120.00'), Decimal('20.00'), Decimal('20.00'), '7750036000010', 150, prov_backus),
            ('Cusqueña Dorada Lata 269ml', 'Cervezas y Licores', Decimal('6.00'), Decimal('4.20'), Decimal('80.00'), Decimal('60.00'), Decimal('15.00'), Decimal('15.00'), '7750036002052', 150, prov_backus),
            ('Corona Extra 355ml', 'Cervezas y Licores', Decimal('8.00'), Decimal('5.50'), Decimal('60.00'), Decimal('50.00'), Decimal('10.00'), Decimal('10.00'), '7501064191319', 180, prov_backus),
            ('Cerveza Cristal Lata 355ml', 'Cervezas y Licores', Decimal('5.00'), Decimal('3.50'), Decimal('100.00'), Decimal('90.00'), Decimal('20.00'), Decimal('20.00'), '7750036001017', 150, prov_backus),
            ('Pisco Queirolo Quebranta 750ml', 'Cervezas y Licores', Decimal('38.00'), Decimal('26.00'), Decimal('2.00'), Decimal('15.00'), Decimal('8.00'), Decimal('8.00'), '7750123000018', 365, prov_backus), # BAJO STOCK M1

            # SNACKS
            ("Papas Lay's Clásicas 160g", 'Snacks y Salados', Decimal('7.50'), Decimal('4.90'), Decimal('60.00'), Decimal('50.00'), Decimal('10.00'), Decimal('10.00'), '7750885002011', 90, prov_pepsico),
            ('Doritos Queso Atrevido 150g', 'Snacks y Salados', Decimal('7.90'), Decimal('5.10'), Decimal('50.00'), Decimal('45.00'), Decimal('10.00'), Decimal('10.00'), '7750885003056', 90, prov_pepsico),
            ('Maní Karinto Salado 100g', 'Snacks y Salados', Decimal('3.50'), Decimal('2.20'), Decimal('70.00'), Decimal('60.00'), Decimal('10.00'), Decimal('10.00'), '7750885004015', 120, prov_pepsico),
            ('Cuates Picantes 90g', 'Snacks y Salados', Decimal('2.50'), Decimal('1.50'), Decimal('80.00'), Decimal('70.00'), Decimal('15.00'), Decimal('15.00'), '7750885005081', 90, prov_pepsico),
            ('Inka Chips Sal Maras 135g', 'Snacks y Salados', Decimal('8.50'), Decimal('5.50'), Decimal('30.00'), Decimal('25.00'), Decimal('8.00'), Decimal('8.00'), '7754321000112', 120, prov_pepsico),

            # GOLOSINAS
            ('Sublime Clásico 30g', 'Golosinas y Chocolates', Decimal('2.50'), Decimal('1.60'), Decimal('120.00'), Decimal('100.00'), Decimal('20.00'), Decimal('20.00'), '7613031000019', 180, prov_nestle),
            ("Triángulo D'Onofrio 30g", 'Golosinas y Chocolates', Decimal('2.50'), Decimal('1.60'), Decimal('100.00'), Decimal('80.00'), Decimal('15.00'), Decimal('15.00'), '7613031002020', 180, prov_nestle),
            ('Caramelos Halls Menta 10u', 'Golosinas y Chocolates', Decimal('2.00'), Decimal('1.20'), Decimal('90.00'), Decimal('75.00'), Decimal('15.00'), Decimal('15.00'), '7622210001010', 365, prov_mondelez),
            ('Chicle Trident Menta 18u', 'Golosinas y Chocolates', Decimal('3.50'), Decimal('2.10'), Decimal('80.00'), Decimal('65.00'), Decimal('10.00'), Decimal('10.00'), '7622210002024', 365, prov_mondelez),
            ('Chocolate Cua Cua 18g', 'Golosinas y Chocolates', Decimal('1.50'), Decimal('0.90'), Decimal('60.00'), Decimal('1.00'), Decimal('10.00'), Decimal('15.00'), '7622210003014', 180, prov_mondelez), # BAJO STOCK M2

            # COMIDA RÁPIDA
            ('Pan con Pollo Listo!', 'Café y Comida Rápida', Decimal('8.90'), Decimal('5.20'), Decimal('1.00'), Decimal('25.00'), Decimal('10.00'), Decimal('10.00'), '7759900001011', 3, prov_nestle), # BAJO STOCK M1
            ('Empanada de Carne Listo!', 'Café y Comida Rápida', Decimal('6.50'), Decimal('3.80'), Decimal('25.00'), Decimal('3.00'), Decimal('10.00'), Decimal('12.00'), '7759900002028', 2, prov_nestle), # BAJO STOCK M2
            ('Café Capuchino 12oz', 'Café y Comida Rápida', Decimal('6.90'), Decimal('2.50'), Decimal('100.00'), Decimal('80.00'), Decimal('15.00'), Decimal('15.00'), '7759900003018', 30, prov_nestle),
            ('Hot Dog Gigante Listo!', 'Café y Comida Rápida', Decimal('7.50'), Decimal('4.10'), Decimal('0.00'), Decimal('20.00'), Decimal('10.00'), Decimal('10.00'), '7759900004015', 2, prov_nestle), # SIN STOCK M1
            ('Sandwich Triple Pollo Huevo', 'Café y Comida Rápida', Decimal('7.90'), Decimal('4.50'), Decimal('20.00'), Decimal('18.00'), Decimal('8.00'), Decimal('8.00'), '7759900005029', 3, prov_nestle),

            # GALLETAS
            ('Galletas Oreo 4u', 'Galletas y Panadería', Decimal('2.00'), Decimal('1.20'), Decimal('100.00'), Decimal('90.00'), Decimal('15.00'), Decimal('15.00'), '7622300001020', 120, prov_mondelez),
            ('Galletas Morochas 6u', 'Galletas y Panadería', Decimal('2.20'), Decimal('1.30'), Decimal('80.00'), Decimal('70.00'), Decimal('15.00'), Decimal('15.00'), '7622300002010', 120, prov_nestle),
            ('Galletas Casino Menta 6u', 'Galletas y Panadería', Decimal('2.00'), Decimal('1.20'), Decimal('60.00'), Decimal('50.00'), Decimal('10.00'), Decimal('10.00'), '7622300003024', 120, prov_nestle),

            # HELADOS
            ("Helado Sin Parar Chocolate", 'Helados y Hielo', Decimal('5.50'), Decimal('3.60'), Decimal('40.00'), Decimal('2.00'), Decimal('10.00'), Decimal('10.00'), '7613031005014', 180, prov_nestle), # BAJO STOCK M2
            ('Bolsón de Hielo Cubos 3Kg', 'Helados y Hielo', Decimal('8.50'), Decimal('4.00'), Decimal('40.00'), Decimal('30.00'), Decimal('10.00'), Decimal('10.00'), '7759900005012', 365, prov_lindley),

            # CIGARRILLOS
            ('Cigarrillos Lucky Strike Red 20u', 'Cigarrillos y Accesorios', Decimal('16.00'), Decimal('12.50'), Decimal('40.00'), Decimal('35.00'), Decimal('10.00'), Decimal('10.00'), '7702001000105', 365, prov_mondelez),
            ('Encendedor Tokai Desechable', 'Cigarrillos y Accesorios', Decimal('2.50'), Decimal('1.20'), Decimal('80.00'), Decimal('70.00'), Decimal('15.00'), Decimal('15.00'), '4904650000102', 365, prov_mondelez)
        ]

        prods_m1 = {}
        prods_m2 = {}
        hoy = timezone.now()

        for p_name, c_name, precio, costo, stock_m1, stock_m2, stock_min1, stock_min2, ean, dias_v, prov in prod_definitions:
            # Productos Sucursal 1
            p1 = Producto.objects.create(
                nombre=p_name, categoria=cats_m1[c_name], precio=precio, costo=costo,
                stock=stock_m1, stock_minimo=stock_min1, unidad_medida='UND',
                codigo_barras=ean, mercado=mercado1
            )
            prods_m1[p_name] = p1

            if stock_m1 > 0:
                lote_cant = stock_m1 / Decimal('2.00')
                UnidadProducto.objects.create(
                    producto=p1, mercado=mercado1, fecha_vencimiento=(hoy + timedelta(days=dias_v)).date(),
                    cantidad=lote_cant, estado='disponible'
                )
                UnidadProducto.objects.create(
                    producto=p1, mercado=mercado1, fecha_vencimiento=(hoy + timedelta(days=dias_v + 60)).date(),
                    cantidad=lote_cant, estado='disponible'
                )

            Kardex.objects.create(
                producto=p1, mercado=mercado1, tipo_movimiento='ENTRADA', cantidad=stock_m1,
                saldo_anterior=Decimal('0.00'), saldo_nuevo=stock_m1, referencia_tipo='Inventario Inicial',
                referencia_detalle='Carga Inicial de Productos', fecha=hoy - timedelta(days=15), usuario=admin1_jp
            )

            # Productos Sucursal 2
            p2 = Producto.objects.create(
                nombre=p_name, categoria=cats_m2[c_name], precio=precio, costo=costo,
                stock=stock_m2, stock_minimo=stock_min2, unidad_medida='UND',
                codigo_barras=ean, mercado=mercado2
            )
            prods_m2[p_name] = p2

            if stock_m2 > 0:
                lote_cant2 = stock_m2 / Decimal('2.00')
                UnidadProducto.objects.create(
                    producto=p2, mercado=mercado2, fecha_vencimiento=(hoy + timedelta(days=dias_v)).date(),
                    cantidad=lote_cant2, estado='disponible'
                )
                UnidadProducto.objects.create(
                    producto=p2, mercado=mercado2, fecha_vencimiento=(hoy + timedelta(days=dias_v + 45)).date(),
                    cantidad=lote_cant2, estado='disponible'
                )

            Kardex.objects.create(
                producto=p2, mercado=mercado2, tipo_movimiento='ENTRADA', cantidad=stock_m2,
                saldo_anterior=Decimal('0.00'), saldo_nuevo=stock_m2, referencia_tipo='Inventario Inicial',
                referencia_detalle='Carga Inicial de Productos', fecha=hoy - timedelta(days=15), usuario=admin1_ben
            )

        print("[+] Productos e inventario inicial registrados.")

        # 7. SIMULAR COMPRAS A PROVEEDORES
        print("[+] Registrando Compras a Proveedores...")
        compra1 = Compra.objects.create(
            proveedor=prov_lindley, usuario=admin1_jp,
            total=Decimal('105.00'), fecha=hoy - timedelta(days=10)
        )
        p_ik1 = prods_m1['Inca Kola 600ml']
        DetalleCompra.objects.create(compra=compra1, producto=p_ik1, cantidad=Decimal('50.00'), precio_costo_unitario=Decimal('2.10'))
        s_ant = p_ik1.stock
        p_ik1.stock += Decimal('50.00')
        p_ik1.save()
        Kardex.objects.create(
            producto=p_ik1, mercado=mercado1, tipo_movimiento='ENTRADA', cantidad=Decimal('50.00'),
            saldo_anterior=s_ant, saldo_nuevo=p_ik1.stock, referencia_tipo='Compra', referencia_id=compra1.id,
            referencia_detalle=f'Reabastecimiento Compra #{compra1.id} Lindley', fecha=hoy - timedelta(days=10), usuario=admin1_jp
        )
        UnidadProducto.objects.create(producto=p_ik1, mercado=mercado1, fecha_vencimiento=(hoy + timedelta(days=180)).date(), cantidad=Decimal('50.00'), estado='disponible')

        compra2 = Compra.objects.create(
            proveedor=prov_backus, usuario=admin1_ben,
            total=Decimal('380.00'), fecha=hoy - timedelta(days=8)
        )
        p_pil2 = prods_m2['Pilsen Callao Lata 355ml']
        DetalleCompra.objects.create(compra=compra2, producto=p_pil2, cantidad=Decimal('100.00'), precio_costo_unitario=Decimal('3.80'))
        s_ant = p_pil2.stock
        p_pil2.stock += Decimal('100.00')
        p_pil2.save()
        Kardex.objects.create(
            producto=p_pil2, mercado=mercado2, tipo_movimiento='ENTRADA', cantidad=Decimal('100.00'),
            saldo_anterior=s_ant, saldo_nuevo=p_pil2.stock, referencia_tipo='Compra', referencia_id=compra2.id,
            referencia_detalle=f'Reabastecimiento Compra #{compra2.id} Backus', fecha=hoy - timedelta(days=8), usuario=admin1_ben
        )
        UnidadProducto.objects.create(producto=p_pil2, mercado=mercado2, fecha_vencimiento=(hoy + timedelta(days=150)).date(), cantidad=Decimal('100.00'), estado='disponible')


        # 8. SIMULAR TRANSFERENCIA ENTRE SUCURSALES (Javier Prado -> Benavides)
        print("[+] Registrando Transferencia entre Sucursales...")
        transf = Transferencia.objects.create(
            mercado_origen=mercado1, mercado_destino=mercado2,
            usuario_envio=admin1_jp, usuario_recepcion=admin1_ben,
            estado='COMPLETADA', observaciones='Transferencia urgente de Monster Energy',
            fecha_envio=hoy - timedelta(days=5), fecha_recepcion=hoy - timedelta(days=5, hours=2)
        )
        p_mon1 = prods_m1['Monster Energy 473ml']
        p_mon2 = prods_m2['Monster Energy 473ml']
        cant_tr = Decimal('10.00')
        TransferenciaDetalle.objects.create(
            transferencia=transf, producto_origen=p_mon1, producto_destino=p_mon2,
            cantidad=cant_tr, fecha_vencimiento=(hoy + timedelta(days=240)).date()
        )

        s_ant1 = p_mon1.stock
        p_mon1.stock -= cant_tr
        p_mon1.save()
        Kardex.objects.create(
            producto=p_mon1, mercado=mercado1, tipo_movimiento='SALIDA_TRANSFERENCIA', cantidad=cant_tr,
            saldo_anterior=s_ant1, saldo_nuevo=p_mon1.stock, referencia_tipo='Transferencia', referencia_id=transf.id,
            referencia_detalle=f'Transferencia enviada #{transf.id} a Benavides', fecha=hoy - timedelta(days=5), usuario=admin1_jp
        )

        s_ant2 = p_mon2.stock
        p_mon2.stock += cant_tr
        p_mon2.save()
        Kardex.objects.create(
            producto=p_mon2, mercado=mercado2, tipo_movimiento='ENTRADA_TRANSFERENCIA', cantidad=cant_tr,
            saldo_anterior=s_ant2, saldo_nuevo=p_mon2.stock, referencia_tipo='Transferencia', referencia_id=transf.id,
            referencia_detalle=f'Transferencia recibida #{transf.id} desde Javier Prado', fecha=hoy - timedelta(days=5), usuario=admin1_ben
        )

        # 9. SIMULAR AJUSTES DE INVENTARIO
        print("[+] Registrando Ajustes de Inventario (Mermas)...")
        p_lay1 = prods_m1["Papas Lay's Clásicas 160g"]
        s_ant = p_lay1.stock
        p_lay1.stock -= Decimal('2.00')
        p_lay1.save()
        Kardex.objects.create(
            producto=p_lay1, mercado=mercado1, tipo_movimiento='AJUSTE_NEGATIVO', cantidad=Decimal('2.00'),
            saldo_anterior=s_ant, saldo_nuevo=p_lay1.stock, referencia_tipo='Ajuste de Inventario',
            referencia_detalle='Merma por empaque dañado', fecha=hoy - timedelta(days=4), usuario=admin1_jp
        )

        # 10. CAJAS Y VENTAS HISTÓRICAS EN VARIOS DÍAS
        print("[+] Registrando Cajas y Ventas Históricas en Múltiples Días...")
        
        # Cajas Sucursal Javier Prado
        caja_jp_ayer = Caja.objects.create(
            usuario=vendedor_jp, mercado=mercado1, fecha_apertura=hoy - timedelta(days=1, hours=14),
            fecha_cierre=hoy - timedelta(days=1, hours=4), monto_inicial=Decimal('150.00'),
            monto_final_efectivo_real=Decimal('380.00'), monto_final_yape_real=Decimal('120.00'), monto_final_plin_real=Decimal('45.00'),
            monto_esperado_efectivo=Decimal('380.00'), monto_esperado_yape=Decimal('120.00'), monto_esperado_plin=Decimal('45.00'),
            estado='CERRADA', observaciones='Cierre cuadrado de ayer.'
        )

        # Ventas Ayer en Javier Prado
        v1 = Venta.objects.create(
            usuario=vendedor_jp, cliente=cliente_generico, fecha_hora=hoy - timedelta(days=1, hours=12),
            tipo_comprobante='TICKET', serie='T001', numero=1, subtotal=Decimal('25.42'), igv=Decimal('4.58'),
            total=Decimal('30.00'), descuento=Decimal('0.00'), costo_total=Decimal('17.50'),
            metodo_pago='Efectivo', monto_recibido=Decimal('50.00'), vuelto=Decimal('20.00'),
            estado='COMPLETADA', mercado=mercado1, caja=caja_jp_ayer
        )

        VentaDetalle.objects.create(venta=v1, producto=p_ik1, cantidad=Decimal('4.00'), precio_unitario=Decimal('3.50'), costo_unitario=p_ik1.costo, subtotal=Decimal('14.00'))
        s_ant = p_ik1.stock
        p_ik1.stock -= Decimal('4.00')
        p_ik1.save()
        Kardex.objects.create(
            producto=p_ik1, mercado=mercado1, tipo_movimiento='SALIDA', cantidad=Decimal('4.00'),
            saldo_anterior=s_ant, saldo_nuevo=p_ik1.stock, referencia_tipo='Venta', referencia_id=v1.id,
            referencia_detalle='Ticket T001-000001', fecha=hoy - timedelta(days=1, hours=12), usuario=vendedor_jp
        )

        VentaDetalle.objects.create(venta=v1, producto=p_lay1, cantidad=Decimal('2.00'), precio_unitario=Decimal('8.00'), costo_unitario=p_lay1.costo, subtotal=Decimal('16.00'))
        s_ant = p_lay1.stock
        p_lay1.stock -= Decimal('2.00')
        p_lay1.save()
        Kardex.objects.create(
            producto=p_lay1, mercado=mercado1, tipo_movimiento='SALIDA', cantidad=Decimal('2.00'),
            saldo_anterior=s_ant, saldo_nuevo=p_lay1.stock, referencia_tipo='Venta', referencia_id=v1.id,
            referencia_detalle='Ticket T001-000001', fecha=hoy - timedelta(days=1, hours=12), usuario=vendedor_jp
        )

        v2 = Venta.objects.create(
            usuario=vendedor_jp, cliente=cliente_3, fecha_hora=hoy - timedelta(days=1, hours=10),
            tipo_comprobante='FACTURA', serie='F001', numero=1, subtotal=Decimal('101.69'), igv=Decimal('18.31'),
            total=Decimal('120.00'), descuento=Decimal('0.00'), costo_total=Decimal('76.00'),
            metodo_pago='Yape', monto_recibido=Decimal('120.00'), vuelto=Decimal('0.00'), num_operacion='9840291',
            estado='COMPLETADA', mercado=mercado1, caja=caja_jp_ayer
        )
        p_pil1 = prods_m1['Pilsen Callao Lata 355ml']
        VentaDetalle.objects.create(venta=v2, producto=p_pil1, cantidad=Decimal('20.00'), precio_unitario=Decimal('6.00'), costo_unitario=p_pil1.costo, subtotal=Decimal('120.00'))
        s_ant = p_pil1.stock
        p_pil1.stock -= Decimal('20.00')
        p_pil1.save()
        Kardex.objects.create(
            producto=p_pil1, mercado=mercado1, tipo_movimiento='SALIDA', cantidad=Decimal('20.00'),
            saldo_anterior=s_ant, saldo_nuevo=p_pil1.stock, referencia_tipo='Venta', referencia_id=v2.id,
            referencia_detalle='Factura F001-000001', fecha=hoy - timedelta(days=1, hours=10), usuario=vendedor_jp
        )

        # Ventas de Días Anteriores (Hace 2, 3 y 4 días) para Gráficos
        for offset_dias in [2, 3, 4]:
            v_hist = Venta.objects.create(
                usuario=vendedor_jp, cliente=cliente_1, fecha_hora=hoy - timedelta(days=offset_dias, hours=11),
                tipo_comprobante='BOLETA', serie='B001', numero=offset_dias, subtotal=Decimal('67.80'), igv=Decimal('12.20'),
                total=Decimal('80.00'), descuento=Decimal('0.00'), costo_total=Decimal('50.00'),
                metodo_pago='Plin' if offset_dias % 2 == 0 else 'Efectivo', monto_recibido=Decimal('100.00'), vuelto=Decimal('20.00'),
                estado='COMPLETADA', mercado=mercado1, caja=caja_jp_ayer
            )
            p_red1 = prods_m1['Red Bull 250ml']
            VentaDetalle.objects.create(venta=v_hist, producto=p_red1, cantidad=Decimal('5.00'), precio_unitario=Decimal('9.00'), costo_unitario=p_red1.costo, subtotal=Decimal('45.00'))
            s_ant = p_red1.stock
            p_red1.stock -= Decimal('5.00')
            p_red1.save()
            Kardex.objects.create(
                producto=p_red1, mercado=mercado1, tipo_movimiento='SALIDA', cantidad=Decimal('5.00'),
                saldo_anterior=s_ant, saldo_nuevo=p_red1.stock, referencia_tipo='Venta', referencia_id=v_hist.id,
                referencia_detalle=f'Boleta B001-00000{offset_dias}', fecha=hoy - timedelta(days=offset_dias, hours=11), usuario=vendedor_jp
            )

        # Caja Abierta Hoy en Sucursal Benavides
        caja_ben = Caja.objects.create(
            usuario=vendedor_ben, mercado=mercado2, fecha_apertura=hoy - timedelta(hours=3),
            monto_inicial=Decimal('200.00'), monto_esperado_efectivo=Decimal('245.50'),
            monto_esperado_yape=Decimal('89.00'), monto_esperado_plin=Decimal('0.00'),
            estado='ABIERTA', observaciones='Turno mañana.'
        )

        v3 = Venta.objects.create(
            usuario=vendedor_ben, cliente=cliente_2, fecha_hora=hoy - timedelta(hours=1),
            tipo_comprobante='BOLETA', serie='B001', numero=1, subtotal=Decimal('38.56'), igv=Decimal('6.94'),
            total=Decimal('45.50'), descuento=Decimal('0.00'), costo_total=Decimal('29.10'),
            metodo_pago='Efectivo', monto_recibido=Decimal('50.00'), vuelto=Decimal('4.50'),
            estado='COMPLETADA', mercado=mercado2, caja=caja_ben
        )

        p_red2 = prods_m2['Red Bull 250ml']
        p_sub2 = prods_m2['Sublime Clásico 30g']

        VentaDetalle.objects.create(venta=v3, producto=p_red2, cantidad=Decimal('3.00'), precio_unitario=Decimal('9.00'), costo_unitario=p_red2.costo, subtotal=Decimal('27.00'))
        s_ant = p_red2.stock
        p_red2.stock -= Decimal('3.00')
        p_red2.save()
        Kardex.objects.create(
            producto=p_red2, mercado=mercado2, tipo_movimiento='SALIDA', cantidad=Decimal('3.00'),
            saldo_anterior=s_ant, saldo_nuevo=p_red2.stock, referencia_tipo='Venta', referencia_id=v3.id,
            referencia_detalle='Boleta B001-000001', fecha=hoy - timedelta(hours=1), usuario=vendedor_ben
        )

        VentaDetalle.objects.create(venta=v3, producto=p_sub2, cantidad=Decimal('7.00'), precio_unitario=Decimal('2.50'), costo_unitario=p_sub2.costo, subtotal=Decimal('17.50'))
        s_ant = p_sub2.stock
        p_sub2.stock -= Decimal('7.00')
        p_sub2.save()
        Kardex.objects.create(
            producto=p_sub2, mercado=mercado2, tipo_movimiento='SALIDA', cantidad=Decimal('7.00'),
            saldo_anterior=s_ant, saldo_nuevo=p_sub2.stock, referencia_tipo='Venta', referencia_id=v3.id,
            referencia_detalle='Boleta B001-000001', fecha=hoy - timedelta(hours=1), usuario=vendedor_ben
        )

        # Invalidate cache for all markets
        from inventario.utils import invalidate_mercado_cache
        invalidate_mercado_cache(None)

    print("=" * 70)
    print("SISTEMA POBLADO COMPLETAMENTE CON PRODUCTOS AMPLIADOS Y BAJO STOCK")
    print("=" * 70)
    print("SUCURSAL 1: Listo! Express - Av. Javier Prado")
    print("   Administrador:")
    print("     - admin_javierprado / admin123")
    print("   Vendedor:")
    print("     - vendedor_javierprado / vendedor123")
    print("-" * 70)
    print("SUCURSAL 2: Listo! Express - Av. Benavides")
    print("   Administrador:")
    print("     - admin_benavides / admin123")
    print("   Vendedor:")
    print("     - vendedor_benavides / vendedor123")
    print("-" * 70)
    print("SUPERUSUARIO GLOBAL:")
    print("     - admin / admin123")
    print("=" * 70)


if __name__ == '__main__':
    populate_full()
