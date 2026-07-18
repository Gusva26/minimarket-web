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
        qs = Caja.objects.filter(mercado=self.request.user.mercado)
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
        return VentaSerializer

    def get_queryset(self):
        qs = Venta.objects.filter(mercado=self.request.user.mercado)
        if self.request.user.rol == 'VENDEDOR' and not self.request.user.is_superuser:
            qs = qs.filter(usuario=self.request.user)
        return qs.prefetch_related('detalles__producto', 'cliente', 'usuario', 'caja')

    def list(self, request, *args, **kwargs):
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
            qs = qs.filter(metodo_pago=metodo_pago)
        if tipo_comprobante:
            qs = qs.filter(tipo_comprobante=tipo_comprobante)
        if estado:
            qs = qs.filter(estado=estado)
        if q:
            if q.isdigit():
                qs = qs.filter(id=q)
            else:
                qs = qs.filter(
                    Q(detalles__producto__nombre__icontains=q) |
                    Q(usuario__username__icontains=q) |
                    Q(cliente__nombre__icontains=q) |
                    Q(num_operacion__icontains=q) |
                    Q(serie__icontains=q)
                ).distinct()

        qs = qs.order_by('-fecha_hora')

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

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
                        ref_detalle=f'Venta #{venta.id}',
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

            return Response({'status': 'success', 'message': f'Venta {venta.serie}-{venta.numero} anulada.', 'venta': VentaSerializer(venta).data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ObtenerSiguienteNumeroView(APIView):
    def get(self, request):
        tipo = request.query_params.get('tipo_comprobante', 'TICKET')
        serie, numero = obtener_siguiente_numero(request.user.mercado, tipo)
        return Response({'serie': serie, 'numero': numero})
