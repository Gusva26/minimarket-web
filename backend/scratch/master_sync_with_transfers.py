import os
import sys
import random
import datetime
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_minimarket.settings')

import django
django.setup()

from django.db import transaction, connection
from django.utils import timezone

from inventario.models import Producto, Categoria, Mercado, Kardex, UnidadProducto, Transferencia, TransferenciaDetalle
from compras.models import Compra, DetalleCompra
from proveedores.models import Proveedor
from ventas.models import Venta, VentaDetalle, Caja, Cliente
from usuarios.models import Usuario
from django.core.cache import cache
import scratch.export_two_excels as exporter

def get_supplier_for_product(p, suppliers):
    name_lower = p.nombre.lower()
    if any(k in name_lower for k in ['coca cola', 'inca kola', 'fanta', 'sprite', 'san luis', 'frugos', 'schweppes']):
        return suppliers.get('arca')
    elif any(k in name_lower for k in ['cristal', 'pilsen', 'cusqueña', 'cusquena', 'arequipeña', 'san juan', 'corona', 'volt', 'sporade', 'free tea']):
        return suppliers.get('backus')
    elif any(k in name_lower for k in ['primor', 'cocinero', 'don vittorio', 'casino', 'tentación']):
        return suppliers.get('alicorp')
    elif any(k in name_lower for k in ['frio rico', 'jet', 'sándwich', 'swanduiwc', 'alaska', 'kross', 'morochas', 'bb', 'peziduri', 'sublime', 'triángulo', 'princesa', 'sin parar']):
        return suppliers.get('nestle')
    elif any(k in name_lower for k in ['pepsi', '7up', 'concordia', 'kola real', 'lays', 'doritos', 'cheetos', 'cuates', 'inka chips']):
        return suppliers.get('pepsico')
    elif any(k in name_lower for k in ['oreo', 'ritz', 'club social', 'trident', 'halls']):
        return suppliers.get('mondelez')
    elif any(k in name_lower for k in ['lucky strike', 'hamilton', 'tokai', 'bic']):
        return suppliers.get('tabacalera')
    elif any(k in name_lower for k in ['queirolo', 'pisco']):
        return suppliers.get('queirolo')
    else:
        return suppliers.get('alicorp')

def run_master_sync():
    print("=================================================================")
    print("INICIANDO RECONSTRUCCIÓN CON TRANSFERENCIAS, VENTAS Y COMPRAS")
    print("REGLA #1: TABLA PRODUCTO MANTIENE STOCK ACTUAL CONGELADO E INTACTO")
    print("=================================================================")

    now = timezone.now()
    today = now.date()

    admin_user = Usuario.objects.filter(is_active=True).first()
    usuarios = list(Usuario.objects.filter(is_active=True))

    with connection.cursor() as cursor:
        cursor.execute("SET statement_timeout = 0;")
        # Truncar primero tablas con FK a Producto
        cursor.execute("TRUNCATE TABLE inventario_transferenciadetalle CASCADE;")
        cursor.execute("TRUNCATE TABLE inventario_transferencia CASCADE;")
        cursor.execute("TRUNCATE TABLE compras_detallecompra CASCADE;")
        cursor.execute("TRUNCATE TABLE compras_compra CASCADE;")
        cursor.execute("TRUNCATE TABLE inventario_kardex CASCADE;")
        cursor.execute("TRUNCATE TABLE ventas_ventadetalle CASCADE;")
        cursor.execute("TRUNCATE TABLE ventas_venta CASCADE;")
        cursor.execute("TRUNCATE TABLE ventas_caja CASCADE;")
        cursor.execute("TRUNCATE TABLE inventario_unidadproducto CASCADE;")

        # Eliminar Fanta Naranja 500ml de la BD
        cursor.execute("DELETE FROM inventario_producto WHERE LOWER(nombre) LIKE '%fanta%500ml%';")

    with transaction.atomic():
        # Proveedores Oficiales
        suppliers_data = {
            'arca': ('Arca Continental Lindley S.A.', '20100100100', '013144000', 'Av. Javier Prado Este 5210, La Molina'),
            'backus': ('Unión de Cervecerías Peruanas Backus y Johnston S.A.A.', '20100113610', '013113000', 'Av. Nicolás de Piérola 400, Ate'),
            'alicorp': ('Alicorp S.A.A.', '20100055237', '013159000', 'Av. Argentina 4793, Carmen de la Legua'),
            'nestle': ('Nestlé Perú S.A.', '20100166837', '0180010210', 'Calle Luis Cornejo 145, Lima'),
            'pepsico': ('Pepsico Alimentos Perú S.R.L.', '20268252208', '012114000', 'Av. Francisco Bolognesi 505, Miraflores'),
            'mondelez': ('Mondelēz Perú S.A.', '20514138029', '016183000', 'Av. Pedro de Osma 409, Barranco'),
            'tabacalera': ('Tabacalera del Oriente S.A.', '20100456100', '014412000', 'Av. República de Panamá 3505, San Isidro'),
            'queirolo': ('Santiago Queirolo S.A.C.', '20100139499', '014631000', 'Av. San Martín 1090, Pueblo Libre')
        }
        suppliers_objs = {}
        for key, (name, ruc, tel, addr) in suppliers_data.items():
            p_obj = Proveedor.objects.filter(ruc=ruc).first() or Proveedor.objects.filter(nombre=name).first()
            if not p_obj:
                p_obj = Proveedor.objects.create(nombre=name, ruc=ruc, telefono=tel, direccion=addr, estado_sunat='HABIDO / ACTIVO', activo=True)
            else:
                p_obj.nombre = name
                p_obj.ruc = ruc
                p_obj.save()
            suppliers_objs[key] = p_obj

        # Clientes Registrados
        clients_data = [
            ('Juan Carlos Pérez Ramos', 'DNI', '45891234', 'Av. Javier Prado 1204, San Borja', '987654321'),
            ('María Fernanda Mendoza Vargas', 'DNI', '71234567', 'Av. Benavides 2310, Miraflores', '912345678'),
            ('Carlos Alberto Torres Silva', 'DNI', '10458912', 'Jr. Las Camelias 450, San Isidro', '955443322'),
            ('Constructora & Comercializadora del Sur S.A.C.', 'RUC', '20601234567', 'Av. Primavera 890, Surco', '014332211'),
            ('Distribuidora & Servicios San Martín S.R.L.', 'RUC', '20549876543', 'Av. La Marina 1500, San Miguel', '015667788')
        ]
        clients_objs = []
        for name, doc_type, num_doc, addr, tel in clients_data:
            c_obj = Cliente.objects.filter(num_documento=num_doc).first()
            if not c_obj:
                c_obj = Cliente.objects.create(nombre=name, tipo_documento=doc_type, num_documento=num_doc, direccion=addr, telefono=tel)
            clients_objs.append(c_obj)

        all_prods = list(Producto.objects.all().select_related('categoria', 'mercado').order_by('mercado_id', 'id'))
        prods_dict = {p.id: p for p in all_prods}

        # Cajas Diarias (60 Días)
        cajas_map = {}
        for m_id in [1, 2]:
            mercado_obj = Mercado.objects.get(id=m_id)
            for day_offset in range(59, -1, -1):
                caja_date = today - datetime.timedelta(days=day_offset)
                dt_apertura = timezone.make_aware(datetime.datetime.combine(caja_date, datetime.time(8, 0, 0)))
                is_today = (day_offset == 0)
                dt_cierre = None if is_today else timezone.make_aware(datetime.datetime.combine(caja_date, datetime.time(22, 0, 0)))
                estado_caja = 'ABIERTA' if is_today else 'CERRADA'
                
                c_user = random.choice(usuarios)
                caja_obj = Caja.objects.create(
                    usuario=c_user,
                    mercado=mercado_obj,
                    fecha_apertura=dt_apertura,
                    fecha_cierre=dt_cierre,
                    monto_inicial=Decimal('150.00'),
                    estado=estado_caja
                )
                cajas_map[(m_id, day_offset)] = caja_obj

        sold_qty_map = {p.id: Decimal('0.00') for p in all_prods}
        transferred_in_map = {p.id: Decimal('0.00') for p in all_prods}
        transferred_out_map = {p.id: Decimal('0.00') for p in all_prods}

        kardex_movements_to_create = []

        # 2. Generar Transferencias entre Sucursales (12 a 15 transferencias en 60 días)
        mercado_1 = Mercado.objects.get(id=1)
        mercado_2 = Mercado.objects.get(id=2)
        prods_m1_map = {p.nombre.lower(): p for p in all_prods if p.mercado_id == 1}
        prods_m2_map = {p.nombre.lower(): p for p in all_prods if p.mercado_id == 2}

        common_names = list(set(prods_m1_map.keys()).intersection(set(prods_m2_map.keys())))

        for t_idx in range(1, 14):
            t_days_ago = 55 - (t_idx * 4)
            if t_days_ago < 3:
                t_days_ago = random.randint(2, 5)

            t_date = timezone.make_aware(datetime.datetime.combine(today - datetime.timedelta(days=t_days_ago), datetime.time(11, 30, 0)))
            
            from_m1 = (t_idx % 2 == 1)
            orig_m = mercado_1 if from_m1 else mercado_2
            dest_m = mercado_2 if from_m1 else mercado_1

            tr_obj = Transferencia.objects.create(
                mercado_origen=orig_m,
                mercado_destino=dest_m,
                usuario_envio=admin_user,
                usuario_recepcion=admin_user,
                fecha_envio=t_date,
                fecha_recepcion=t_date + datetime.timedelta(hours=2),
                estado='COMPLETADA',
                observaciones=f'Transferencia de rebalanceo de stock #{str(t_idx).zfill(4)}'
            )

            sample_names = random.sample(common_names, min(len(common_names), random.randint(2, 4)))
            for p_name in sample_names:
                p_orig = prods_m1_map[p_name] if from_m1 else prods_m2_map[p_name]
                p_dest = prods_m2_map[p_name] if from_m1 else prods_m1_map[p_name]
                
                qty_tr = Decimal('3.00') if 'bebida' in (p_orig.categoria.nombre if p_orig.categoria else '').lower() else Decimal('2.00')

                TransferenciaDetalle.objects.create(
                    transferencia=tr_obj,
                    producto_origen=p_orig,
                    producto_destino=p_dest,
                    cantidad=qty_tr,
                    fecha_vencimiento=today + datetime.timedelta(days=120)
                )

                transferred_out_map[p_orig.id] += qty_tr
                transferred_in_map[p_dest.id] += qty_tr

                ref_num = f"#TR-{str(tr_obj.id).zfill(4)}"
                kardex_movements_to_create.append((
                    p_orig, orig_m.id, admin_user, 'SALIDA_TRANSFERENCIA', qty_tr,
                    tr_obj.id, f"Transferencia {ref_num} a {dest_m.nombre}", t_date
                ))
                kardex_movements_to_create.append((
                    p_dest, dest_m.id, admin_user, 'ENTRADA_TRANSFERENCIA', qty_tr,
                    tr_obj.id, f"Transferencia {ref_num} desde {orig_m.nombre}", t_date + datetime.timedelta(hours=2)
                ))

        # 3. Ventas Múltiples Diarias (10 a 16 ventas/día/sucursal)
        for m_id in [1, 2]:
            m_prods = [p for p in all_prods if p.mercado_id == m_id]
            boleta_counter = 1
            ticket_counter = 1

            for day_offset in range(55, -1, -1):
                caja_activa = cajas_map[(m_id, day_offset)]
                sale_date_base = today - datetime.timedelta(days=day_offset)

                daily_sales_num = random.randint(8, 14)

                for vs in range(daily_sales_num):
                    sale_time = datetime.time(8 + (vs * 1) % 13, random.randint(0, 59), random.randint(0, 59))
                    sale_datetime = timezone.make_aware(datetime.datetime.combine(sale_date_base, sale_time))

                    is_boleta = (boleta_counter <= ticket_counter)
                    if is_boleta:
                        serie = f"B00{m_id}"
                        num = boleta_counter
                        tipo_doc = 'BOLETA'
                        boleta_counter += 1
                    else:
                        serie = f"T00{m_id}"
                        num = ticket_counter
                        tipo_doc = 'TICKET'
                        ticket_counter += 1

                    num_comp = f"{serie}-{str(num).zfill(8)}"
                    basket = random.sample(m_prods, min(len(m_prods), random.randint(1, 4)))
                    cliente_asig = random.choice(clients_objs) if is_boleta and random.random() > 0.4 else None

                    v = Venta.objects.create(
                        mercado_id=m_id,
                        usuario=caja_activa.usuario,
                        cliente=cliente_asig,
                        caja=caja_activa,
                        tipo_comprobante=tipo_doc,
                        serie=serie,
                        numero=num,
                        subtotal=Decimal('0.00'),
                        igv=Decimal('0.00'),
                        total=Decimal('0.00'),
                        costo_total=Decimal('0.00'),
                        metodo_pago=random.choice(['Efectivo', 'Yape', 'Plin']),
                        estado='COMPLETADA'
                    )
                    Venta.objects.filter(id=v.id).update(fecha_hora=sale_datetime)

                    total_venta = Decimal('0.00')
                    total_costo = Decimal('0.00')
                    detalles_v_to_create = []

                    for p in basket:
                        qty = Decimal('2.00') if p.categoria and p.categoria.nombre == 'Bebidas' else Decimal('1.00')
                        item_subtotal = p.precio * qty
                        total_venta += item_subtotal
                        total_costo += (p.costo * qty)

                        sold_qty_map[p.id] += qty

                        detalles_v_to_create.append(
                            VentaDetalle(
                                venta=v,
                                producto=p,
                                cantidad=qty,
                                precio_unitario=p.precio,
                                subtotal=item_subtotal
                            )
                        )

                        kardex_movements_to_create.append((
                            p, m_id, v.usuario, 'SALIDA', qty,
                            v.id, f"{tipo_doc.capitalize()} {num_comp}", sale_datetime
                        ))

                    igv_v = (total_venta * Decimal('0.18')).quantize(Decimal('0.01'))
                    v.subtotal = total_venta - igv_v
                    v.igv = igv_v
                    v.total = total_venta
                    v.costo_total = total_costo
                    v.save(update_fields=['subtotal', 'igv', 'total', 'costo_total'])

                    VentaDetalle.objects.bulk_create(detalles_v_to_create)

        # 4. Compras a Proveedores: Cantidad Comprada = Stock Intacto + Ventas + Transferencias_Salida - Transferencias_Entrada
        lotes_to_create = []
        kardex_final_to_create = []
        detalles_compra_to_create = []
        purchase_counter = 1

        for m_id in [1, 2]:
            m_prods = [p for p in all_prods if p.mercado_id == m_id]
            prov_groups = {}
            for p in m_prods:
                prov = get_supplier_for_product(p, suppliers_objs)
                if prov not in prov_groups:
                    prov_groups[prov] = []
                prov_groups[prov].append(p)

            for prov, prods_group in prov_groups.items():
                compra_date = now - datetime.timedelta(days=random.randint(56, 59), hours=random.randint(8, 14))
                serie_f = f"F00{m_id}"
                num_f = str(purchase_counter).zfill(7)
                purchase_counter += 1

                compra_obj = Compra.objects.create(
                    usuario=admin_user,
                    proveedor=prov,
                    tipo_comprobante='FACTURA',
                    serie_comprobante=serie_f,
                    numero_comprobante=num_f,
                    observaciones=f'Compra de reabastecimiento directo de {prov.nombre}',
                    total=Decimal('0.00')
                )
                Compra.objects.filter(id=compra_obj.id).update(fecha=compra_date)

                total_compra = Decimal('0.00')

                for p in prods_group:
                    b_qty = p.stock + sold_qty_map[p.id] + transferred_out_map[p.id] - transferred_in_map[p.id]
                    b_qty = max(b_qty, Decimal('0.00'))

                    p._temp_bought_qty = b_qty
                    p._temp_running_kardex = Decimal('0.00')

                    costo_unit = p.costo
                    subt = b_qty * costo_unit
                    total_compra += subt

                    days_offset = 180 if p.categoria and p.categoria.nombre in ['Bebidas', 'Licores'] else 120
                    expiry = today + datetime.timedelta(days=days_offset)

                    detalles_compra_to_create.append(
                        DetalleCompra(
                            compra=compra_obj,
                            producto=p,
                            cantidad=b_qty,
                            precio_costo_unitario=costo_unit,
                            subtotal=subt,
                            fecha_vencimiento=expiry
                        )
                    )

                    ref_detalle = f"Factura Proveedor {serie_f}-{num_f} ({prov.nombre[:25]})"
                    kardex_movements_to_create.append((
                        p, m_id, admin_user, 'ENTRADA', b_qty,
                        compra_obj.id, ref_detalle, compra_date
                    ))

                compra_obj.total = total_compra
                compra_obj.save(update_fields=['total'])

        DetalleCompra.objects.bulk_create(detalles_compra_to_create)

        # 5. Ordenar Todos los Movimientos Kardex por Fecha Cronológica y Calcular Saldos en Tiempo Real
        kardex_movements_to_create.sort(key=lambda x: x[7])

        for p_obj, m_id, user_obj, tipo_mov, qty, ref_id, ref_det, mov_dt in kardex_movements_to_create:
            p = prods_dict[p_obj.id]
            saldo_ant = p._temp_running_kardex

            if tipo_mov in ['ENTRADA', 'ENTRADA_TRANSFERENCIA']:
                saldo_nuevo = saldo_ant + qty
            else:
                saldo_nuevo = saldo_ant - qty

            p._temp_running_kardex = saldo_nuevo

            kardex_final_to_create.append(
                Kardex(
                    producto=p,
                    mercado_id=m_id,
                    usuario=user_obj,
                    tipo_movimiento=tipo_mov,
                    cantidad=qty,
                    saldo_anterior=saldo_ant,
                    saldo_nuevo=saldo_nuevo,
                    referencia_tipo='Compra' if tipo_mov == 'ENTRADA' else ('Transferencia' if 'TRANSFERENCIA' in tipo_mov else 'Venta'),
                    referencia_id=ref_id,
                    referencia_detalle=ref_det,
                    fecha=mov_dt
                )
            )

        # 6. Sincronizar Cajas
        for (m_id, day_offset), caja_obj in cajas_map.items():
            ventas_caja = Venta.objects.filter(caja=caja_obj, estado='COMPLETADA')
            
            sum_efectivo = Decimal('0.00')
            sum_yape = Decimal('0.00')
            sum_plin = Decimal('0.00')

            for v in ventas_caja:
                if v.metodo_pago == 'Efectivo':
                    sum_efectivo += v.total
                elif v.metodo_pago == 'Yape':
                    sum_yape += v.total
                elif v.metodo_pago == 'Plin':
                    sum_plin += v.total

            caja_obj.monto_esperado_efectivo = caja_obj.monto_inicial + sum_efectivo
            caja_obj.monto_esperado_yape = sum_yape
            caja_obj.monto_esperado_plin = sum_plin

            if caja_obj.estado == 'CERRADA':
                caja_obj.monto_final_efectivo_real = caja_obj.monto_esperado_efectivo
                caja_obj.monto_final_yape_real = caja_obj.monto_esperado_yape
                caja_obj.monto_final_plin_real = caja_obj.monto_esperado_plin
            
            caja_obj.save()

        # 7. Lotes FEFO en UnidadProducto coincidiendo 100% con p.stock
        for p in all_prods:
            st = p.stock
            if st > 0:
                name_l = p.nombre.lower()
                if 'empanada' in name_l or 'sandwich' in name_l:
                    expiry = today + datetime.timedelta(days=4)
                elif 'free tea' in name_l:
                    expiry = today - datetime.timedelta(days=3)
                else:
                    days_off = 180 if p.categoria and p.categoria.nombre in ['Bebidas', 'Licores'] else 120
                    expiry = today + datetime.timedelta(days=days_off)

                lotes_to_create.append(
                    UnidadProducto(
                        producto=p,
                        mercado_id=p.mercado_id,
                        fecha_vencimiento=expiry,
                        cantidad=st,
                        estado='disponible'
                    )
                )

        UnidadProducto.objects.bulk_create(lotes_to_create)
        Kardex.objects.bulk_create(kardex_final_to_create)

        cache.clear()
        print("=================================================================")
        print("ÉXITO MATEMÁTICO ABSOLUTO: COMPRAS, VENTAS, TRANSFERENCIAS Y KARDEX SINCRONIZADOS.")
        print("=================================================================")

    exporter.export_two_branch_excels()

if __name__ == '__main__':
    run_master_sync()
