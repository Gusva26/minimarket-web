from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Prefetch, Q
from django.utils import timezone

from .models import Compra, DetalleCompra
from .serializers import CompraSerializer, CompraCreateSerializer
from inventario.models import Producto, UnidadProducto
from inventario.utils import crear_kardex
from usuarios.api import IsAdminOrSuperUser


class CompraViewSet(viewsets.ModelViewSet):
    queryset = Compra.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperUser]
    ordering = ['-fecha']

    def get_serializer_class(self):
        if self.action == 'create':
            return CompraCreateSerializer
        return CompraSerializer

    def get_queryset(self):
        qs = Compra.objects.prefetch_related(
            Prefetch('detalles', queryset=DetalleCompra.objects.select_related('producto')),
            'proveedor', 'usuario'
        )
        user = self.request.user
        if user.mercado:
            qs = qs.filter(detalles__producto__mercado=user.mercado).distinct()

        proveedor_id = self.request.query_params.get('proveedor_id')
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        q = self.request.query_params.get('q')

        if proveedor_id:
            qs = qs.filter(proveedor_id=proveedor_id)
        if fecha_desde:
            qs = qs.filter(fecha__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha__lte=f'{fecha_hasta}T23:59:59')
        if q:
            qs = qs.filter(
                Q(id__icontains=q) |
                Q(proveedor__nombre__icontains=q) |
                Q(detalles__producto__nombre__icontains=q)
            ).distinct()

        return qs

    def create(self, request, *args, **kwargs):
        serializer = CompraCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        proveedor_id = data.get('proveedor_id')
        fecha = data.get('fecha', timezone.now())
        detalles_data = data['detalles']

        try:
            with transaction.atomic():
                compra = Compra.objects.create(
                    usuario=request.user,
                    proveedor_id=proveedor_id,
                    fecha=fecha,
                )

                detalles_obj = []
                mercado = request.user.mercado if request.user.mercado else None
                # Dictionary to accumulate totals per product for Kardex
                kardex_totals = {}

                for det in detalles_data:
                    producto = Producto.objects.select_for_update().get(
                        id=det['producto_id']
                    )

                    if mercado and producto.mercado and producto.mercado != mercado:
                        return Response(
                            {'error': f'El producto "{producto.nombre}" no pertenece a tu mercado.'},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    detalle = DetalleCompra(
                        compra=compra,
                        producto=producto,
                        cantidad=det['cantidad'],
                        precio_costo_unitario=det['precio_costo_unitario'],
                        fecha_vencimiento=det.get('fecha_vencimiento'),
                    )
                    detalle.subtotal = det['cantidad'] * det['precio_costo_unitario']
                    detalles_obj.append(detalle)

                    # Accumulate for Kardex
                    prod_id = producto.id
                    if prod_id not in kardex_totals:
                        kardex_totals[prod_id] = {
                            'obj': producto,
                            'cantidad': 0,
                            'saldo_anterior': producto.stock,
                            'nuevo_costo': det['precio_costo_unitario']
                        }
                    kardex_totals[prod_id]['cantidad'] += det['cantidad']
                    kardex_totals[prod_id]['nuevo_costo'] = det['precio_costo_unitario']

                    producto.stock += det['cantidad']
                    producto.costo = det['precio_costo_unitario']

                    # Create UnidadProducto records for each unit/quantity
                    fecha_venc = det.get('fecha_vencimiento')
                    if not fecha_venc:
                        fecha_venc = "2099-12-31"
                    
                    cantidad = det['cantidad']
                    um = producto.unidad_medida
                    if um in ('UND', 'PAQ', 'CAJ', 'BOL'):
                        # For whole units, create one record per unit
                        for _ in range(int(cantidad)):
                            UnidadProducto.objects.create(
                                producto=producto,
                                mercado=mercado,
                                fecha_vencimiento=fecha_venc,
                                cantidad=1,
                                estado='disponible',
                            )
                    else:
                        # For decimal products (KG, LT), create a single record
                        UnidadProducto.objects.create(
                            producto=producto,
                            mercado=mercado,
                            fecha_vencimiento=fecha_venc,
                            cantidad=cantidad,
                            estado='disponible',
                        )
                    producto.save()

                DetalleCompra.objects.bulk_create(detalles_obj)

                # Create Kardex entries once per product
                for prod_id, info in kardex_totals.items():
                    crear_kardex(
                        producto=info['obj'],
                        mercado=mercado,
                        tipo_movimiento='ENTRADA',
                        cantidad=info['cantidad'],
                        saldo_anterior=info['saldo_anterior'],
                        saldo_nuevo=info['obj'].stock,
                        ref_tipo='Compra',
                        ref_id=compra.id,
                        ref_detalle=f'Compra a {compra.proveedor.nombre if compra.proveedor else "N/A"}',
                        usuario=request.user
                    )

                compra.actualizar_total()

                return Response(
                    CompraSerializer(compra).data,
                    status=status.HTTP_201_CREATED,
                )

        except Producto.DoesNotExist:
            return Response(
                {'error': 'Uno o más productos no existen.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
