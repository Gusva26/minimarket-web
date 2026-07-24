from decimal import Decimal
from datetime import datetime

from django.db import transaction
from django.utils import timezone
from django.db.models import Q

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Caja, Cliente, Venta, VentaDetalle
from .serializers import (
    CajaSerializer, CajaAperturaSerializer, CajaCierreSerializer,
    ClienteSerializer, VentaSerializer, VentaCreateSerializer,
)
from inventario.models import Producto, Kardex

from django.conf import settings
import urllib.request
import ssl
import json

from inventario.utils import descontar_stock_fefo, devolver_stock_a_unidades, crear_kardex


def obtener_siguiente_numero(mercado, tipo):
    series = {'TICKET': 'T001', 'BOLETA': 'B001', 'FACTURA': 'F001'}
    serie = series.get(tipo, 'T001')
    with transaction.atomic():
        ultima_venta = Venta.objects.select_for_update().filter(
            mercado=mercado, tipo_comprobante=tipo, serie=serie
        ).order_by('-numero').first()
        if ultima_venta:
            return serie, ultima_venta.numero + 1
        return serie, 1


class CajaViewSet(viewsets.ModelViewSet):
    serializer_class = CajaSerializer

    def get_queryset(self):
        mercado = self.request.user.mercado
        if mercado is None:
            qs = Caja.objects.all().select_related('usuario', 'mercado')
        else:
            qs = Caja.objects.filter(mercado=mercado).select_related('usuario', 'mercado')

        if self.request.user.rol == 'VENDEDOR' and not self.request.user.is_superuser:
            qs = qs.filter(usuario=self.request.user)
        return qs


    @action(detail=False, methods=['post'])
    def apertura(self, request):
        if Caja.objects.filter(usuario=request.user, mercado=request.user.mercado, estado='ABIERTA').exists():
            return Response({'error': 'Ya hay una caja abierta para este usuario'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CajaAperturaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        caja = Caja.objects.create(
            usuario=request.user,
            mercado=request.user.mercado,
            monto_inicial=serializer.validated_data['monto_inicial'],
            observaciones=serializer.validated_data.get('observaciones', ''),
            monto_esperado_efectivo=serializer.validated_data['monto_inicial'],
        )
        return Response(CajaSerializer(caja).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def cierre(self, request, pk=None):
        caja = self.get_object()
        if caja.estado == 'CERRADA':
            return Response({'error': 'La caja ya está cerrada'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CajaCierreSerializer(data=request.data, instance=caja)
        serializer.is_valid(raise_exception=True)
        caja = serializer.save(estado='CERRADA', fecha_cierre=timezone.now())
        return Response(CajaSerializer(caja).data)


class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    search_fields = ['nombre', 'num_documento']

    def get_queryset(self):
        return Cliente.objects.all()

    @action(detail=False, methods=['get'], url_path='consultar-documento')
    def consultar_documento(self, request):
        documento = request.query_params.get('documento', '')
        if not documento:
            return Response({'error': 'Documento requerido'}, status=status.HTTP_400_BAD_REQUEST)

        cliente = Cliente.objects.filter(num_documento=documento).first()
        if cliente:
            return Response({
                'status': 'success', 'origen': 'local',
                'nombre': cliente.nombre, 'direccion': cliente.direccion or '',
                'id': cliente.id, 'tipo_documento': cliente.tipo_documento,
                'num_documento': cliente.num_documento,
            })

        token = getattr(settings, 'APISPERU_TOKEN', '')
        if not token:
            return Response({'error': 'API Token no configurado en settings.py'}, status=status.HTTP_400_BAD_REQUEST)

        tipo = 'dni' if len(documento) == 8 else 'ruc'
        url = f"https://dniruc.apisperu.com/api/v1/{tipo}/{documento}?token={token}"

        try:
            ssl_context = ssl._create_unverified_context()
            req = urllib.request.Request(url, headers={'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=12, context=ssl_context) as response:
                res_body = response.read().decode()
                data = json.loads(res_body)

            if data.get('success') is False:
                return Response({'error': data.get('message', 'No se encontró el documento')}, status=status.HTTP_404_NOT_FOUND)

            if tipo == 'dni':
                nombre = f"{data.get('nombres', '')} {data.get('apellidoPaterno', '')} {data.get('apellidoMaterno', '')}".strip()
                direccion = ''
            else:
                nombre = data.get('razonSocial', '')
                direccion = data.get('direccion', '')

            return Response({
                'status': 'success', 'origen': 'api',
                'nombre': nombre, 'direccion': direccion,
            })

        except Exception as e:
            return Response({'error': f'Error en consulta: {str(e)}'}, status=status.HTTP_502_BAD_GATEWAY)


class VentaViewSet(viewsets.ModelViewSet):
    ordering = ['-fecha_hora']

    def get_serializer_class(self):
        if self.action == 'create':
            return VentaCreateSerializer
        elif self.action == 'list':
            from .serializers import VentaListSerializer
            return VentaListSerializer
        return VentaSerializer

    def get_queryset(self):
        mercado = self.request.user.mercado
        if mercado is None:
            qs = Venta.objects.all()
        else:
            qs = Venta.objects.filter(mercado=mercado)

        if self.request.user.rol == 'VENDEDOR' and not self.request.user.is_superuser:
            qs = qs.filter(usuario=self.request.user)

        qs = qs.select_related('cliente', 'usuario', 'mercado')
        if self.action != 'list':
            qs = qs.select_related('caja').prefetch_related('detalles__producto')
        return qs



    def list(self, request, *args, **kwargs):
        from django.core.cache import cache
        from inventario.utils import get_mercado_cache_version

        mercado_id = request.user.mercado_id
        version = get_mercado_cache_version(mercado_id)
        params_str = "_".join([f"{k}:{v}" for k, v in sorted(request.query_params.items())])
        cache_key = f"ventas_mercado_{mercado_id}_v{version}_{params_str}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        qs = self.filter_queryset(self.get_queryset())

        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        metodo_pago = request.query_params.get('metodo_pago')
        tipo_comprobante = request.query_params.get('tipo_comprobante')
        estado = request.query_params.get('estado')
        q = request.query_params.get('q')

        if fecha_inicio:
            d = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            start = timezone.make_aware(datetime.combine(d, datetime.min.time()))
            qs = qs.filter(fecha_hora__gte=start)
        if fecha_fin:
            d = datetime.strptime(fecha_fin, '%Y-%m-%d')
            end = timezone.make_aware(datetime.combine(d, datetime.max.time()))
            qs = qs.filter(fecha_hora__lte=end)
        if metodo_pago:
            qs = qs.filter(metodo_pago__iexact=metodo_pago)
        if tipo_comprobante:
            qs = qs.filter(tipo_comprobante__iexact=tipo_comprobante)
        if estado:
            qs = qs.filter(estado__iexact=estado)
        if q:
            q_clean = q.strip()
            q_filter = (
                Q(detalles__producto__nombre__icontains=q_clean) |
                Q(usuario__username__icontains=q_clean) |
                Q(cliente__nombre__icontains=q_clean) |
                Q(cliente__num_documento__icontains=q_clean) |
                Q(num_operacion__icontains=q_clean) |
                Q(serie__icontains=q_clean)
            )
            if q_clean.isdigit():
                q_filter |= Q(id=int(q_clean)) | Q(numero=int(q_clean))
            qs = qs.filter(q_filter).distinct()


        qs = qs.order_by('-fecha_hora')

        # Calcular KPIs globales agregados sobre todo el queryset filtrado (sin limitar a 1 pagina)
        from django.db.models import Sum
        total_completado = qs.filter(estado='COMPLETADA').aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        cant_completada = qs.filter(estado='COMPLETADA').count()
        total_anulado = qs.filter(estado='ANULADA').aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        cant_anulada = qs.filter(estado='ANULADA').count()
        ticket_promedio = (total_completado / cant_completada) if cant_completada > 0 else Decimal('0.00')

        summary_data = {
            'total_completado': float(total_completado),
            'cant_completada': cant_completada,
            'ticket_promedio': float(round(ticket_promedio, 2)),
            'total_anulado': float(total_anulado),
            'cant_anulada': cant_anulada,
        }

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            res_obj = self.get_paginated_response(serializer.data).data
            res_obj['summary'] = summary_data
            cache.set(cache_key, res_obj, 2)
            return Response(res_obj)

        serializer = self.get_serializer(qs, many=True)
        res_data = {
            'results': serializer.data,
            'summary': summary_data
        }
        cache.set(cache_key, res_data, 2)
        return Response(res_data)



    def create(self, request, *args, **kwargs):
        serializer = VentaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        caja = Caja.objects.filter(
            usuario=request.user, mercado=request.user.mercado, estado='ABIERTA'
        ).first()
        if not caja:
            return Response({'error': 'No hay una caja abierta para procesar la venta'}, status=status.HTTP_400_BAD_REQUEST)

        cliente_data = data.get('cliente_data')
        cliente = None
        if cliente_data and cliente_data.get('num_documento'):
            num_doc = cliente_data['num_documento']
            cliente, created = Cliente.objects.get_or_create(
                num_documento=num_doc,
                defaults={
                    'nombre': cliente_data.get('nombre', 'Cliente Genérico'),
                    'tipo_documento': 'RUC' if len(num_doc) == 11 else 'DNI',
                    'direccion': cliente_data.get('direccion', ''),
                }
            )
            if not created:
                if cliente_data.get('nombre'):
                    cliente.nombre = cliente_data['nombre']
                if cliente_data.get('direccion'):
                    cliente.direccion = cliente_data['direccion']
                cliente.save()

        tipo_comprobante = data['tipo_comprobante']
        items_data = data['items']

        try:
            with transaction.atomic():
                validated_items = []
                total_catalogo = Decimal('0.00')
                for item in items_data:
                    producto = Producto.objects.select_for_update().get(
                        pk=item['producto_id'], mercado=request.user.mercado
                    )
                    cantidad = Decimal(item['cantidad'])
                    if producto.stock < cantidad:
                        raise ValueError(f"Stock insuficiente para {producto.nombre}")
                    
                    precio = producto.precio
                    item_descuento = Decimal(item.get('descuento', '0.00'))
                    item_subtotal = (precio * cantidad) - item_descuento
                    if item_subtotal < 0:
                        raise ValueError(f"El descuento para {producto.nombre} no puede ser mayor que su subtotal")
                    
                    total_catalogo += precio * cantidad
                    validated_items.append({
                        'producto': producto,
                        'cantidad': cantidad,
                        'precio': precio,
                        'descuento': item_descuento,
                        'subtotal': item_subtotal,
                    })

                descuento_global = Decimal(data.get('descuento', '0.00'))
                descuento_total = sum(item['descuento'] for item in validated_items) + descuento_global
                total_neto = total_catalogo - descuento_total
                if total_neto < 0:
                    raise ValueError("El descuento total no puede ser mayor que el total de la venta")

                subtotal = total_neto / Decimal('1.18')
                igv = total_neto - subtotal
                monto_recibido = Decimal(data.get('monto_recibido', 0))
                vuelto = max(Decimal('0.00'), monto_recibido - total_neto)

                serie, numero = obtener_siguiente_numero(request.user.mercado, tipo_comprobante)
                venta = Venta.objects.create(
                    usuario=request.user,
                    cliente=cliente,
                    total=total_neto,
                    descuento=descuento_total,
                    subtotal=subtotal,
                    igv=igv,
                    metodo_pago=data['metodo_pago'],
                    monto_recibido=monto_recibido,
                    vuelto=vuelto,
                    num_operacion=data.get('num_operacion', ''),
                    tipo_comprobante=tipo_comprobante,
                    serie=serie,
                    numero=numero,
                    mercado=request.user.mercado,
                    caja=caja,
                )

                costo_total = Decimal('0.00')
                for v_item in validated_items:
                    producto = v_item['producto']
                    cantidad = v_item['cantidad']
                    precio = v_item['precio']

                    costo_unitario = producto.costo or Decimal('0.00')
                    saldo_anterior = producto.stock

                    detalle = VentaDetalle.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=precio,
                        costo_unitario=costo_unitario,
                        descuento=v_item['descuento'],
                        subtotal=v_item['subtotal'],
                    )

                    # FEFO deduction with per-unit traceability
                    exito, error_msg, unidades_ids = descontar_stock_fefo(
                        producto, cantidad, request.user.mercado, venta_detalle=detalle
                    )
                    if not exito:
                        raise ValueError(f'{producto.nombre}: {error_msg}')

                    producto.stock -= cantidad
                    producto.save()

                    crear_kardex(
                        producto=producto, mercado=request.user.mercado,
                        tipo_movimiento='SALIDA', cantidad=cantidad,
                        saldo_anterior=saldo_anterior, saldo_nuevo=producto.stock,
                        ref_tipo='Venta', ref_id=venta.id,
                        ref_detalle=f'{venta.tipo_comprobante} {venta.serie}-{venta.numero:06d}',
                        usuario=request.user,
                    )


                    costo_total += costo_unitario * cantidad

                venta.costo_total = costo_total
                venta.save()

                if data['metodo_pago'] == 'Efectivo':
                    caja.monto_esperado_efectivo += total_neto
                elif data['metodo_pago'] == 'Yape':
                    caja.monto_esperado_yape += total_neto
                elif data['metodo_pago'] == 'Plin':
                    caja.monto_esperado_plin += total_neto
                caja.save()

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Error al procesar la venta: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        from inventario.utils import invalidate_mercado_cache
        invalidate_mercado_cache(request.user.mercado_id)

        result = VentaSerializer(venta)
        return Response(result.data, status=status.HTTP_201_CREATED)


    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        venta = self.get_object()
        if venta.estado == 'ANULADA':
            return Response({'error': 'La venta ya está anulada'}, status=status.HTTP_400_BAD_REQUEST)

        hoy = timezone.localtime(timezone.now()).date()
        fecha_venta = timezone.localtime(venta.fecha_hora).date()
        if fecha_venta != hoy and not request.user.is_superuser:
            return Response({'error': 'No se puede anular una venta de días anteriores. Contacte al administrador.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                for detalle in venta.detalles.all():
                    if detalle.producto:
                        producto = detalle.producto
                        cantidad = detalle.cantidad
                        saldo_anterior = producto.stock
                        producto.stock += cantidad
                        producto.save()

                        # Return stock to unidades via venta_detalle link
                        devolver_stock_a_unidades(
                            producto, cantidad, venta.mercado,
                            venta_detalle=detalle,
                        )

                        crear_kardex(
                            producto=producto, mercado=venta.mercado,
                            tipo_movimiento='ENTRADA', cantidad=cantidad,
                            saldo_anterior=saldo_anterior, saldo_nuevo=producto.stock,
                            ref_tipo='Anulación Venta', ref_id=venta.id,
                            ref_detalle=f'Anulación de Venta {venta.serie}-{venta.numero}',
                            usuario=request.user,
                        )

                caja = venta.caja
                if caja and caja.estado == 'ABIERTA':
                    if venta.metodo_pago == 'Efectivo':
                        caja.monto_esperado_efectivo -= venta.total
                    elif venta.metodo_pago == 'Yape':
                        caja.monto_esperado_yape -= venta.total
                    elif venta.metodo_pago == 'Plin':
                        caja.monto_esperado_plin -= venta.total
                    caja.save()

                venta.estado = 'ANULADA'
                venta.save()

            invalidate_mercado_cache(venta.mercado_id)
            return Response({'status': 'success', 'message': f'Venta {venta.serie}-{venta.numero} anulada.', 'venta': VentaSerializer(venta).data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        from django.http import HttpResponse
        from xhtml2pdf import pisa

        venta = self.get_object()
        detalles = venta.detalles.select_related('producto').all()

        mercado_nombre = venta.mercado.nombre if venta.mercado else 'MINIMARKET'
        mercado_direccion = venta.mercado.direccion if (venta.mercado and venta.mercado.direccion) else 'Lima, Perú'
        cajero_nombre = f"{venta.usuario.first_name} {venta.usuario.last_name}".strip() if venta.usuario else 'Cajero'
        if not cajero_nombre and venta.usuario:
            cajero_nombre = venta.usuario.username

        cliente_nombre = venta.cliente.nombre if venta.cliente else 'Cliente Anónimo'
        cliente_doc = f"{venta.cliente.tipo_documento}: {venta.cliente.num_documento}" if (venta.cliente and venta.cliente.num_documento) else 'S/N'
        cliente_dir = venta.cliente.direccion if (venta.cliente and venta.cliente.direccion) else ''

        serie_num = f"{venta.serie}-{str(venta.numero).zfill(8)}"
        fecha_str = timezone.localtime(venta.fecha_hora).strftime('%d/%m/%Y %H:%M:%S')

        items_rows = ""
        for det in detalles:
            p_name = det.producto.nombre if det.producto else "Producto"
            cant = float(det.cantidad)
            p_unit = float(det.precio_unitario)
            subt = float(det.subtotal)
            items_rows += f"""
            <tr>
                <td style="padding: 4px 2px; border-bottom: 1px dashed #cbd5e1;">{p_name}</td>
                <td style="padding: 4px 2px; text-align: center; border-bottom: 1px dashed #cbd5e1;">{cant:g}</td>
                <td style="padding: 4px 2px; text-align: right; border-bottom: 1px dashed #cbd5e1;">S/ {p_unit:.2f}</td>
                <td style="padding: 4px 2px; text-align: right; border-bottom: 1px dashed #cbd5e1;">S/ {subt:.2f}</td>
            </tr>
            """

        html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{
                    size: 80mm 200mm;
                    margin: 4mm;
                }}
                body {{
                    font-family: 'Helvetica', 'Arial', sans-serif;
                    font-size: 10px;
                    color: #0f172a;
                    line-height: 1.3;
                }}
                .header {{
                    text-align: center;
                    border-bottom: 1px solid #0f172a;
                    padding-bottom: 6px;
                    margin-bottom: 6px;
                }}
                .title {{
                    font-size: 13px;
                    font-weight: bold;
                    text-transform: uppercase;
                }}
                .subtitle {{
                    font-size: 8.5px;
                    color: #475569;
                }}
                .doc-box {{
                    text-align: center;
                    background-color: #f1f5f9;
                    border: 1px solid #cbd5e1;
                    padding: 5px;
                    margin: 6px 0;
                    border-radius: 4px;
                }}
                .doc-type {{
                    font-size: 11px;
                    font-weight: bold;
                }}
                .doc-num {{
                    font-size: 12px;
                    font-weight: bold;
                    color: #2563eb;
                }}
                .meta-table {{
                    width: 100%;
                    margin-bottom: 6px;
                    font-size: 8.5px;
                }}
                .items-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 6px 0;
                }}
                .items-table th {{
                    background-color: #0f172a;
                    color: #ffffff;
                    padding: 4px 2px;
                    font-size: 8px;
                    text-transform: uppercase;
                }}
                .totals-table {{
                    width: 100%;
                    margin-top: 6px;
                    border-top: 1px solid #0f172a;
                    padding-top: 4px;
                    font-size: 9px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 10px;
                    font-size: 8px;
                    color: #64748b;
                    border-top: 1px dashed #cbd5e1;
                    padding-top: 6px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">{mercado_nombre}</div>
                <div class="subtitle">{mercado_direccion}</div>
                <div class="subtitle">RUC: 20601234567 | Tel: (01) 458-9000</div>
            </div>

            <div class="doc-box">
                <div class="doc-type">{venta.tipo_comprobante} ELECTRÓNICA</div>
                <div class="doc-num">{serie_num}</div>
            </div>

            <table class="meta-table">
                <tr>
                    <td><strong>Fecha:</strong> {fecha_str}</td>
                    <td style="text-align:right;"><strong>Cajero:</strong> {cajero_nombre}</td>
                </tr>
                <tr>
                    <td colspan="2"><strong>Cliente:</strong> {cliente_nombre} ({cliente_doc})</td>
                </tr>
                {f'<tr><td colspan="2"><strong>Dirección:</strong> {cliente_dir}</td></tr>' if cliente_dir else ''}
                <tr>
                    <td><strong>Método Pago:</strong> {venta.metodo_pago}</td>
                    <td style="text-align:right;"><strong>Estado:</strong> {venta.estado}</td>
                </tr>
            </table>

            <table class="items-table">
                <thead>
                    <tr>
                        <th style="text-align:left;">Producto</th>
                        <th style="text-align:center;">Cant.</th>
                        <th style="text-align:right;">P.U.</th>
                        <th style="text-align:right;">Total</th>
                    </tr>
                </thead>
                <tbody>
                    {items_rows}
                </tbody>
            </table>

            <table class="totals-table">
                <tr>
                    <td>Op. Gravada:</td>
                    <td style="text-align:right;">S/ {float(venta.subtotal):.2f}</td>
                </tr>
                <tr>
                    <td>IGV (18%):</td>
                    <td style="text-align:right;">S/ {float(venta.igv):.2f}</td>
                </tr>
                <tr style="font-size: 10.5px; font-weight: bold;">
                    <td>TOTAL A PAGAR:</td>
                    <td style="text-align:right; color:#059669;">S/ {float(venta.total):.2f}</td>
                </tr>
            </table>

            <div class="footer">
                <div>¡Gracias por su compra en {mercado_nombre}!</div>
                <div>Representación impresa del comprobante electrónico</div>
            </div>
        </body>
        </html>
        """

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="Comprobante_{serie_num}.pdf"'
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return Response({'error': 'Error al generar el PDF del comprobante'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response


class ObtenerSiguienteNumeroView(APIView):
    def get(self, request):
        tipo = request.query_params.get('tipo_comprobante', 'TICKET')
        serie, numero = obtener_siguiente_numero(request.user.mercado, tipo)
        return Response({'serie': serie, 'numero': numero})
