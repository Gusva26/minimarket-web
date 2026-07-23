from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django.db.models import Sum, Count

from .models import Proveedor
from .serializers import ProveedorSerializer
from compras.models import Compra, DetalleCompra
from usuarios.api import IsAdminOrSuperUser


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperUser]
    def list(self, request, *args, **kwargs):
        from django.core.cache import cache
        from inventario.utils import get_mercado_cache_version

        mercado_id = request.user.mercado_id or 0
        version = get_mercado_cache_version(mercado_id)
        params_str = "_".join([f"{k}:{v}" for k, v in sorted(request.query_params.items())])
        cache_key = f"proveedores_v{version}_{params_str}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 600)
        return response

    @action(detail=True, methods=['get'])

    def resumen_360(self, request, pk=None):
        proveedor = self.get_object()
        compras = Compra.objects.filter(proveedor=proveedor)
        
        m_filter = {}
        if request.user.mercado:
            m_filter['detalles__producto__mercado'] = request.user.mercado
            compras = compras.filter(**m_filter).distinct()

        total_compras = compras.aggregate(total=Sum('total'))['total'] or 0.00
        num_pedidos = compras.count()
        ultima_compra = compras.order_by('-fecha').first()

        detalles = DetalleCompra.objects.filter(compra__proveedor=proveedor)
        if request.user.mercado:
            detalles = detalles.filter(producto__mercado=request.user.mercado)

        productos_top = list(detalles.values('producto__nombre').annotate(
            total_qty=Sum('cantidad'),
            total_spent=Sum('subtotal')
        ).order_by('-total_spent')[:10])

        return Response({
            'proveedor': ProveedorSerializer(proveedor).data,
            'total_acumulado': float(total_compras),
            'num_pedidos': num_pedidos,
            'ultima_compra': ultima_compra.fecha.strftime('%d/%m/%Y %H:%M') if ultima_compra else None,
            'top_productos': productos_top
        })

