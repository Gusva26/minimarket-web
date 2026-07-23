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
from django.utils import timezone

from usuarios.models import Usuario
from inventario.models import Mercado, Categoria, Producto, Kardex, UnidadProducto
from proveedores.models import Proveedor
from ventas.models import Cliente, Caja, Venta, VentaDetalle
from compras.models import Compra, DetalleCompra


from inventario.utils import crear_kardex

def generar_datos_masivos():
    print("[+] Iniciando poblamiento masivo de Proveedores, Compras y Ventas...")

    mercados = list(Mercado.objects.all())
    if not mercados:
        print("[-] No hay mercados creados.")
        return

    m1 = mercados[0]
    m2 = mercados[1] if len(mercados) > 1 else m1

    # 1. Poblar 15 Proveedores Peruanos de renombre
    print("[+] Creando 15 Proveedores reales en Perú...")
    proveedores_data = [
        ("Arca Continental Lindley S.A.", "20100010729", "Carlos Benavides", "01-614-2000", "ventas@lindley.pe", "Av. Javier Prado Este 6210, La Molina"),
        ("Alicorp S.A.A.", "20100055237", "Mariana Torres", "01-315-0800", "pedidos@alicorp.com.pe", "Av. Argentina 4793, Carmen de la Legua"),
        ("Leche Gloria S.A.", "20100190797", "Roberto Gómez", "01-470-7170", "contacto@gloria.com.pe", "Av. República de Panamá 2461, Santa Catalina"),
        ("Unión de Cervecerías Peruanas Backus y Johnston S.A.A.", "20100113610", "Fernando Castillo", "01-311-3000", "ventas@backus.pe", "Av. Nicolás de Piérola 400, Ate"),
        ("Mondelez Peru S.A.", "20100123593", "Lucía Morales", "01-211-5000", "atencion@mondelez.com", "Av. Canaval y Moreyra 480, San Isidro"),
        ("Nestle Peru S.A.", "20100122945", "Gustavo Rivas", "01-511-6000", "servicio.cliente@pe.nestle.com", "Av. Los Castillos 438, Ate"),


        ("Pepsico Alimentos Perú S.R.L.", "20431267812", "Patricia Mendoza", "01-213-3300", "ventas.pepsico@pepsico.com", "Av. Francisco Bolognesi 125, Santa Anita"),
        ("Kimberly-Clark Perú S.R.L.", "20295195431", "Alejandro Ruiz", "01-211-7000", "kc.ventas@kcc.com", "Av. Elmer Faucett 3550, Callao"),
        ("Procter & Gamble Perú S.R.L.", "20300305611", "Sofía Vargas", "01-611-8000", "contacto.pg@pg.com", "Av. Los Frutales 445, Ate"),
        ("San Fernando S.A.", "20100154308", "Eduardo Paredes", "01-213-5300", "atencion@san-fernando.com.pe", "Av. República de Panamá 4295, Surquillo"),
        ("Molitalia S.A.", "20100060907", "Carmen Silva", "01-513-5600", "ventas@molitalia.com.pe", "Av. Venezuela 2850, Lima"),
        ("Softys Perú S.A.", "20202928371", "Jorge Ramírez", "01-613-4000", "pedidos@softys.com", "Av. Elmer Faucett 4100, Callao"),
        ("La Calera S.A.", "20136271928", "Felipe Vega", "01-411-9000", "ventas@lacalera.com.pe", "Av. Defensores del Morro 1200, Chorrillos"),
        ("British American Tobacco Perú S.A.", "20100049281", "Daniela Alarcón", "01-610-1000", "info@bat.com.pe", "Av. Victor Andrés Belaunde 147, San Isidro"),
        ("Comercializadora de Helados D'Onofrio S.A.", "20549281029", "Manuel Castro", "01-511-6100", "donofrio.pedidos@pe.nestle.com", "Av. Venezuela 2580, Lima"),
    ]

    from django.db.models import Q
    proveedores_objs = []
    for nom, ruc, cont, tel, em, dir_f in proveedores_data:
        prov = Proveedor.objects.filter(Q(nombre=nom) | Q(ruc=ruc)).first()
        if not prov:
            prov = Proveedor.objects.create(
                nombre=nom,
                ruc=ruc,
                persona_contacto=cont,
                telefono=tel,
                email=em,
                direccion=dir_f,
                estado_sunat='HABIDO / ACTIVO',
                activo=True
            )
        else:
            prov.nombre = nom
            prov.ruc = ruc
            prov.persona_contacto = cont
            prov.telefono = tel
            prov.email = em
            prov.direccion = dir_f
            prov.estado_sunat = 'HABIDO / ACTIVO'
            prov.save()
        proveedores_objs.append(prov)




        # 2. Obtener productos de ambas sucursales
        prods_m1 = list(Producto.objects.filter(mercado=m1))
        prods_m2 = list(Producto.objects.filter(mercado=m2))

        usuarios_admin = list(Usuario.objects.filter(rol='ADMINISTRADOR'))
        usuario_sys = usuarios_admin[0] if usuarios_admin else Usuario.objects.first()

        now = timezone.now()

        # 3. Crear 45 Compras históricas (últimos 30 días)
        print("[+] Registrando 45 Compras de reabastecimiento con comprobantes...")
        tipos_doc = ['FACTURA', 'FACTURA', 'FACTURA', 'BOLETA', 'GUIA_REMISION']
        
        for i in range(25):
            days_ago = random.randint(1, 30)
            fecha_compra = now - timedelta(days=days_ago, hours=random.randint(1, 10))
            prov = random.choice(proveedores_objs)
            mercado_target = random.choice([m1, m2])
            prods_pool = prods_m1 if mercado_target == m1 else prods_m2

            if not prods_pool:
                continue

            tipo_doc = random.choice(tipos_doc)
            serie_doc = f"F00{random.randint(1, 4)}" if tipo_doc == 'FACTURA' else f"B00{random.randint(1, 3)}"
            num_doc = str(random.randint(100, 9999)).zfill(6)

            compra = Compra.objects.create(
                usuario=usuario_sys,
                proveedor=prov,
                tipo_comprobante=tipo_doc,
                serie_comprobante=serie_doc,
                numero_comprobante=num_doc,
                observaciones=f"Reabastecimiento regular lote {i+100}",
                fecha=fecha_compra
            )

            num_items = random.randint(2, 6)
            items_compra = random.sample(prods_pool, min(num_items, len(prods_pool)))

            for p in items_compra:
                qty = random.randint(10, 50)
                costo_u = p.costo
                subt = Decimal(str(qty)) * costo_u
                
                venc_date = (fecha_compra + timedelta(days=random.randint(180, 540))).date()

                DetalleCompra.objects.create(
                    compra=compra,
                    producto=p,
                    cantidad=Decimal(str(qty)),
                    precio_costo_unitario=costo_u,
                    fecha_vencimiento=venc_date
                )

                saldo_prev = p.stock
                p.stock += qty
                p.save()

                ref_str = f"Compra {tipo_doc} {serie_doc}-{num_doc} ({prov.nombre})"
                k = crear_kardex(
                    producto=p,
                    mercado=mercado_target,
                    tipo_movimiento='ENTRADA',
                    cantidad=Decimal(str(qty)),
                    saldo_anterior=saldo_prev,
                    saldo_nuevo=p.stock,
                    ref_tipo='Compra',
                    ref_id=compra.id,
                    ref_detalle=ref_str,
                    usuario=usuario_sys
                )
                k.fecha = fecha_compra
                k.save()

                unidades_batch = [
                    UnidadProducto(
                        producto=p,
                        mercado=mercado_target,
                        fecha_vencimiento=venc_date,
                        cantidad=1,
                        estado='disponible'
                    ) for _ in range(qty)
                ]
                UnidadProducto.objects.bulk_create(unidades_batch)


            compra.actualizar_total()

        # 4. Crear 60 Ventas POS variadas (últimos 30 días)
        print("[+] Registrando 60 Transacciones de Ventas POS...")
        cajas = list(Caja.objects.all())
        clientes = list(Cliente.objects.all())
        vendedores = list(Usuario.objects.filter(rol__in=['VENDEDOR', 'ADMINISTRADOR']))

        metodos_pago = ['Efectivo', 'Efectivo', 'Yape', 'Plin']

        for i in range(60):
            days_ago = random.randint(0, 25)
            hour = random.randint(7, 22)
            minute = random.randint(0, 59)
            fecha_venta = now - timedelta(days=days_ago)
            fecha_venta = fecha_venta.replace(hour=hour, minute=minute)

            mercado_target = random.choice([m1, m2])
            caja_target = random.choice([c for c in cajas if c.mercado == mercado_target]) if cajas else None
            vendedor_target = random.choice([v for v in vendedores if v.mercado == mercado_target or v.mercado is None])
            cliente_target = random.choice(clientes) if (clientes and random.random() > 0.4) else None
            prods_pool = prods_m1 if mercado_target == m1 else prods_m2

            if not prods_pool:
                continue

            serie_b = f"B00{1 if mercado_target == m1 else 2}"
            num_b = random.randint(100, 9999)
            metodo = random.choice(metodos_pago)

            venta = Venta.objects.create(
                mercado=mercado_target,
                caja=caja_target,
                usuario=vendedor_target,
                cliente=cliente_target,
                serie=serie_b,
                numero=num_b,
                tipo_comprobante='BOLETA',
                metodo_pago=metodo,
                estado='COMPLETADA',
                total=Decimal('0.00'),
                monto_recibido=Decimal('0.00'),
                vuelto=Decimal('0.00')
            )
            Venta.objects.filter(id=venta.id).update(fecha_hora=fecha_venta)

            num_prods = random.randint(1, 5)
            prods_venta = random.sample(prods_pool, min(num_prods, len(prods_pool)))
            subtotal_venta = Decimal('0.00')
            costo_total_v = Decimal('0.00')

            for p in prods_venta:
                qty = random.randint(1, 4)
                precio_u = p.precio
                subt = Decimal(str(qty)) * precio_u
                subtotal_venta += subt
                costo_total_v += Decimal(str(qty)) * p.costo

                VentaDetalle.objects.create(
                    venta=venta,
                    producto=p,
                    cantidad=Decimal(str(qty)),
                    precio_unitario=precio_u,
                    subtotal=subt
                )

                if p.stock >= qty:
                    saldo_prev = p.stock
                    p.stock -= qty
                    p.save()

                    k = crear_kardex(
                        producto=p,
                        mercado=mercado_target,
                        tipo_movimiento='SALIDA',
                        cantidad=Decimal(str(qty)),
                        saldo_anterior=saldo_prev,
                        saldo_nuevo=p.stock,
                        ref_tipo='Venta',
                        ref_id=venta.id,
                        ref_detalle=f'Venta POS {serie_b}-{num_b} ({metodo})',
                        usuario=vendedor_target
                    )
                    Kardex.objects.filter(id=k.id).update(fecha=fecha_venta)

            venta.subtotal = (subtotal_venta / Decimal('1.18')).quantize(Decimal('0.01'))
            venta.igv = subtotal_venta - venta.subtotal
            venta.total = subtotal_venta
            venta.costo_total = costo_total_v
            if metodo == 'Efectivo':
                monto_p = (subtotal_venta + Decimal(random.choice(['0.00', '2.00', '5.00', '10.00']))).quantize(Decimal('0.01'))
                venta.monto_recibido = monto_p
                venta.vuelto = monto_p - subtotal_venta
            else:
                venta.monto_recibido = subtotal_venta
                venta.vuelto = Decimal('0.00')

            venta.save()


    print("[+] Poblamiento masivo completado con éxito!")


if __name__ == '__main__':
    generar_datos_masivos()
