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
            q_clean = q.strip()
            qs = qs.filter(
                Q(id__icontains=q_clean) |
                Q(proveedor__nombre__icontains=q_clean) |
                Q(detalles__producto__nombre__icontains=q_clean) |
                Q(serie_comprobante__icontains=q_clean) |
                Q(numero_comprobante__icontains=q_clean)
            ).distinct()

        return qs



    def list(self, request, *args, **kwargs):
        from django.core.cache import cache
        from inventario.utils import get_mercado_cache_version

        mercado_id = request.user.mercado_id
        version = get_mercado_cache_version(mercado_id)
        params_str = "_".join([f"{k}:{v}" for k, v in sorted(request.query_params.items())])
        cache_key = f"compras_mercado_{mercado_id}_v{version}_{params_str}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 600)
        return response

    def create(self, request, *args, **kwargs):

        serializer = CompraCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        proveedor_id = data.get('proveedor_id')
        tipo_comprobante = data.get('tipo_comprobante', 'FACTURA')
        serie_comprobante = data.get('serie_comprobante')
        numero_comprobante = data.get('numero_comprobante')
        observaciones = data.get('observaciones')
        fecha = data.get('fecha', timezone.now())
        detalles_data = data['detalles']

        try:
            with transaction.atomic():
                compra = Compra.objects.create(
                    usuario=request.user,
                    proveedor_id=proveedor_id,
                    tipo_comprobante=tipo_comprobante,
                    serie_comprobante=serie_comprobante,
                    numero_comprobante=numero_comprobante,
                    observaciones=observaciones,
                    fecha=fecha,
                )

                detalles_obj = []
                mercado = request.user.mercado if request.user.mercado else None
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
                    if det.get('precio_venta_sugerido'):
                        producto.precio = det['precio_venta_sugerido']

                    fecha_venc = det.get('fecha_vencimiento')
                    if not fecha_venc:
                        fecha_venc = "2099-12-31"
                    
                    cantidad = det['cantidad']
                    um = producto.unidad_medida
                    if um in ('UND', 'PAQ', 'CAJ', 'BOL'):
                        for _ in range(int(cantidad)):
                            UnidadProducto.objects.create(
                                producto=producto,
                                mercado=mercado,
                                fecha_vencimiento=fecha_venc,
                                cantidad=1,
                                estado='disponible',
                            )
                    else:
                        UnidadProducto.objects.create(
                            producto=producto,
                            mercado=mercado,
                            fecha_vencimiento=fecha_venc,
                            cantidad=cantidad,
                            estado='disponible',
                        )
                    producto.save()

                DetalleCompra.objects.bulk_create(detalles_obj)

                for prod_id, info in kardex_totals.items():
                    ref_doc = f"{compra.tipo_comprobante} {compra.serie_comprobante or ''}-{compra.numero_comprobante or compra.id}".strip()
                    crear_kardex(
                        producto=info['obj'],
                        mercado=mercado,
                        tipo_movimiento='ENTRADA',
                        cantidad=info['cantidad'],
                        saldo_anterior=info['saldo_anterior'],
                        saldo_nuevo=info['obj'].stock,
                        ref_tipo='Compra',
                        ref_id=compra.id,
                        ref_detalle=f'Compra {ref_doc} ({compra.proveedor.nombre if compra.proveedor else "N/A"})',
                        usuario=request.user
                    )

                compra.actualizar_total()

                from inventario.utils import invalidate_mercado_cache
                invalidate_mercado_cache(request.user.mercado_id)

                return Response(
                    CompraSerializer(compra).data,
                    status=status.HTTP_201_CREATED,
                )



        except Producto.DoesNotExist:
            return Response(
                {'error': 'Uno o más productos no existen.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
