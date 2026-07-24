import json
import logging
from decimal import Decimal

import pandas as pd
from django.db import transaction
from django.db.models import Count, F, Sum, Q, ExpressionWrapper, DecimalField, Case, When, Value, IntegerField


from django.utils import timezone
from django.core.cache import cache
from rest_framework import status, viewsets, generics
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from usuarios.api import IsAdminOrSuperUser, IsAdminOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse

logger = logging.getLogger(__name__)

from .models import (
    Categoria, Kardex, UnidadProducto, Mercado, Producto,
    Transferencia, TransferenciaDetalle,
)
from .serializers import (
    CategoriaSerializer, KardexSerializer, UnidadProductoSerializer,
    MercadoSerializer, ProductoCreateUpdateSerializer, ProductoSerializer,
    TransferenciaSerializer, TransferenciaListSerializer,
)


from .utils import (
    descontar_stock_fefo, devolver_stock_a_unidades, crear_kardex,
    get_mercado_cache_version, invalidate_mercado_cache
)


class ProductoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ['nombre', 'codigo_barras']
    ordering_fields = ['nombre', 'precio', 'stock']

    def get_queryset(self):
        mercado = self.request.user.mercado
        if mercado is None:
            qs = Producto.objects.all().select_related('categoria', 'mercado')
        else:
            qs = Producto.objects.filter(mercado=mercado).select_related('categoria', 'mercado')

        categoria = self.request.query_params.get('categoria')
        if categoria:
            qs = qs.filter(categoria_id=categoria)

        qs = qs.annotate(
            stock_priority=Case(
                When(stock=0, then=Value(1)),
                When(stock__lt=F('stock_minimo'), then=Value(2)),
                default=Value(3),
                output_field=IntegerField()
            )
        )

        stock_status = self.request.query_params.get('stock_status')
        if stock_status == 'bajo':
            qs = qs.filter(stock__gt=0, stock__lt=F('stock_minimo')).order_by('stock', 'nombre')
        elif stock_status == 'sin_stock':
            qs = qs.filter(stock=0).order_by('nombre')
        elif stock_status == 'normal':
            qs = qs.filter(stock__gte=F('stock_minimo')).order_by('nombre')
        else:
            qs = qs.order_by('stock_priority', 'nombre')

        return qs




    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ProductoCreateUpdateSerializer
        return ProductoSerializer

    def list(self, request, *args, **kwargs):
        mercado_id = request.user.mercado_id
        version = get_mercado_cache_version(mercado_id)
        params_str = "_".join([f"{k}:{v}" for k, v in sorted(request.query_params.items())])
        cache_key = f"productos_mercado_{mercado_id}_v{version}_{params_str}"
        
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        logger.info(f'GET {request.path} (DB QUERY)')
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 600) # 10 min
        return response

    def perform_create(self, serializer):
        prod = serializer.save(mercado=self.request.user.mercado)
        invalidate_mercado_cache(self.request.user.mercado_id)

    def perform_update(self, serializer):
        prod = serializer.save(mercado=self.request.user.mercado)
        invalidate_mercado_cache(self.request.user.mercado_id)

    def perform_destroy(self, instance):
        mercado_id = instance.mercado_id
        instance.delete()
        invalidate_mercado_cache(mercado_id)


    @action(detail=True, methods=['get'])
    def detalle(self, request, pk=None):
        producto = self.get_object()
        return Response({
            'id': producto.id,
            'nombre': producto.nombre,
            'costo': str(producto.costo),
            'precio': str(producto.precio),
            'stock': str(producto.stock),
        })

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def ajustar(self, request, pk=None):
        # Select for update to prevent concurrent lost updates
        producto = Producto.objects.select_for_update().get(pk=pk, mercado=request.user.mercado)
        tipo = request.data.get('tipo')
        cantidad = Decimal(str(request.data.get('cantidad', 0)))
        motivo = request.data.get('motivo', '')
        fecha_vencimiento = request.data.get('fecha_vencimiento')

        if cantidad <= 0:
            return Response({'error': 'Cantidad inválida.'}, status=status.HTTP_400_BAD_REQUEST)

        saldo_ant = producto.stock

        if tipo == 'SUMAR':
            producto.stock += cantidad
            tipo_mov = 'AJUSTE_POSITIVO'

            if not fecha_vencimiento:
                fecha_vencimiento = "2099-12-31"

            UnidadProducto.objects.create(
                producto=producto,
                mercado=request.user.mercado,
                fecha_vencimiento=fecha_vencimiento,
                cantidad=cantidad,
                estado='disponible',
            )

        elif tipo == 'RESTAR':
            if producto.stock < cantidad:
                return Response({'error': 'Stock insuficiente en el producto.'}, status=status.HTTP_400_BAD_REQUEST)

            exito, error_msg, _ = descontar_stock_fefo(producto, cantidad, request.user.mercado)
            if not exito:
                return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)

            producto.stock -= cantidad
            tipo_mov = 'AJUSTE_NEGATIVO'
        else:
            return Response({'error': 'Tipo debe ser SUMAR o RESTAR.'}, status=status.HTTP_400_BAD_REQUEST)

        producto.save()
        crear_kardex(
            producto=producto, mercado=request.user.mercado,
            tipo_movimiento=tipo_mov, cantidad=cantidad,
            saldo_anterior=saldo_ant, saldo_nuevo=producto.stock,
            ref_tipo='Ajuste Manual', ref_detalle=motivo, usuario=request.user,
        )
        return Response(ProductoSerializer(producto).data, status=status.HTTP_200_OK)


class ImportarProductosView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    parser_classes = [MultiPartParser, FormParser]

    @transaction.atomic
    def post(self, request):
        archivo = request.FILES.get('archivo')
        if not archivo:
            return Response({'error': 'Por favor seleccione un archivo.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)

            df.columns = [c.lower().replace(' ', '_') for c in df.columns]
            columnas_req = ['nombre', 'precio', 'costo']
            for col in columnas_req:
                if col not in df.columns:
                    return Response(
                        {'error': f'Falta la columna: {col}'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            mercado = request.user.mercado

            # Pre-fetch existing categories and products in a single step to avoid N+1 queries
            existing_categories = {c.nombre.strip().lower(): c for c in Categoria.objects.filter(mercado=mercado)}
            existing_products = {p.nombre.strip().lower(): p for p in Producto.objects.filter(mercado=mercado)}

            # Phase 1: Batch-create missing categories
            missing_cat_names = set()
            for _, row in df.iterrows():
                cat_nombre = str(row.get('categoria', '')).strip()
                if cat_nombre and cat_nombre.lower() != 'nan':
                    cat_lower = cat_nombre.lower()
                    if cat_lower not in existing_categories and cat_lower not in missing_cat_names:
                        missing_cat_names.add(cat_nombre)

            if missing_cat_names:
                new_cats = [Categoria(nombre=name, mercado=mercado) for name in missing_cat_names]
                Categoria.objects.bulk_create(new_cats)
                # Refresh existing_categories cache with newly created objects
                for c in Categoria.objects.filter(mercado=mercado, nombre__in=missing_cat_names):
                    existing_categories[c.nombre.strip().lower()] = c

            # Phase 2: Distribute products into creation and update batches
            products_to_create = []
            products_to_update = []

            for _, row in df.iterrows():
                prod_name = str(row['nombre']).strip()
                prod_name_lower = prod_name.lower()

                cat_nombre = str(row.get('categoria', '')).strip()
                cat_obj = None
                if cat_nombre and cat_nombre.lower() != 'nan':
                    cat_obj = existing_categories.get(cat_nombre.lower())

                codigo_barras = str(row.get('codigo_barras', '')).strip() if pd.notnull(row.get('codigo_barras')) else None
                precio = Decimal(str(row['precio']))
                costo = Decimal(str(row['costo']))
                stock_minimo = Decimal(str(row.get('stock_minimo', 5.0)))
                unidad_medida = str(row.get('unidad_medida', 'UND')).strip().upper()
                um_mapping = {
                    'UNIDAD': 'UND', 'UNIDADES': 'UND',
                    'KILOGRAMO': 'KG', 'KILOGRAMOS': 'KG', 'KILO': 'KG', 'KILOS': 'KG',
                    'LITRO': 'LT', 'LITROS': 'LT',
                    'PAQUETE': 'PAQ', 'PAQUETES': 'PAQ',
                    'CAJA': 'CAJ', 'CAJAS': 'CAJ',
                    'BOLSA': 'BOL', 'BOLSAS': 'BOL',
                }
                unidad_medida = um_mapping.get(unidad_medida, unidad_medida)
                if unidad_medida not in [u[0] for u in Producto.UNIDADES_MEDIDA]:
                    unidad_medida = 'UND'

                if prod_name_lower in existing_products:
                    p = existing_products[prod_name_lower]
                    p.codigo_barras = codigo_barras
                    p.categoria = cat_obj
                    p.precio = precio
                    p.costo = costo
                    p.stock_minimo = stock_minimo
                    p.unidad_medida = unidad_medida
                    products_to_update.append(p)
                else:
                    p = Producto(
                        nombre=prod_name,
                        mercado=mercado,
                        codigo_barras=codigo_barras,
                        categoria=cat_obj,
                        precio=precio,
                        costo=costo,
                        stock_minimo=stock_minimo,
                        unidad_medida=unidad_medida
                    )
                    products_to_create.append(p)

            # Phase 3: Execute bulk DB operations
            if products_to_create:
                Producto.objects.bulk_create(products_to_create)
            if products_to_update:
                Producto.objects.bulk_update(
                    products_to_update,
                    fields=['codigo_barras', 'categoria', 'precio', 'costo', 'stock_minimo', 'unidad_medida']
                )

            # Invalidate cache once at the end
            from inventario.utils import invalidate_mercado_cache
            invalidate_mercado_cache(mercado.id)

            procesados = len(products_to_create) + len(products_to_update)
            return Response({'mensaje': f'Importación exitosa. {procesados} productos procesados.'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CategoriaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = CategoriaSerializer
    ordering = ['nombre']
    filter_backends = [SearchFilter]
    search_fields = ['nombre']

    def get_queryset(self):
        mercado = self.request.user.mercado
        if mercado is None:
            qs = Categoria.objects.all().select_related('mercado')
        else:
            qs = Categoria.objects.filter(mercado=mercado).select_related('mercado')
        return qs.annotate(
            cantidad_productos=Count('producto')
        )

    def list(self, request, *args, **kwargs):
        version = get_mercado_cache_version(request.user.mercado_id)
        query_params = request.GET.urlencode()
        cache_key = f"categorias_mercado_{request.user.mercado_id}_v{version}_{query_params}"
        data = cache.get(cache_key)
        if data is None:
            logger.info(f'GET {request.path} (DB QUERY)')
            response = super().list(request, *args, **kwargs)
            data = response.data
            cache.set(cache_key, data, 3600)
        return Response(data)

    def perform_create(self, serializer):
        serializer.save(mercado=self.request.user.mercado)

    def perform_update(self, serializer):
        serializer.save(mercado=self.request.user.mercado)

    def destroy(self, request, *args, **kwargs):
        categoria = self.get_object()
        if Producto.objects.filter(categoria=categoria).exists():
            return Response(
                {'error': 'No se puede eliminar una categoría que tiene productos.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


class KardexListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = KardexSerializer

    def get_queryset(self):
        mercado = self.request.user.mercado
        if mercado is None:
            qs = Kardex.objects.all().select_related('producto', 'usuario', 'mercado')
        else:
            qs = Kardex.objects.filter(mercado=mercado).select_related('producto', 'usuario', 'mercado')

        producto_id = self.request.query_params.get('producto_id') or self.request.query_params.get('producto')
        q = self.request.query_params.get('q') or self.request.query_params.get('buscar')
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')

        if producto_id:
            qs = qs.filter(producto_id=producto_id)

        if q:
            qs = qs.filter(
                Q(producto__nombre__icontains=q) |
                Q(producto__codigo_barras__icontains=q) |
                Q(referencia_tipo__icontains=q) |
                Q(referencia_detalle__icontains=q)
            )

        tipo_movimiento = self.request.query_params.get('tipo_movimiento')
        if tipo_movimiento:
            if tipo_movimiento == 'ENTRADA':
                qs = qs.filter(tipo_movimiento__in=['ENTRADA', 'ENTRADA_TRANSFERENCIA'])
            elif tipo_movimiento == 'SALIDA':
                qs = qs.filter(tipo_movimiento__in=['SALIDA', 'SALIDA_TRANSFERENCIA'])
            elif tipo_movimiento == 'AJUSTE':
                qs = qs.filter(tipo_movimiento__in=['AJUSTE_POSITIVO', 'AJUSTE_NEGATIVO'])
            else:
                qs = qs.filter(tipo_movimiento=tipo_movimiento)

        if fecha_desde:
            qs = qs.filter(fecha__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha__lte=fecha_hasta)

        return qs.order_by('-fecha')



    def list(self, request, *args, **kwargs):
        mercado_id = request.user.mercado_id
        version = get_mercado_cache_version(mercado_id)
        params_str = "_".join([f"{k}:{v}" for k, v in sorted(request.query_params.items())])
        cache_key = f"kardex_mercado_{mercado_id}_v{version}_{params_str}"
        
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        logger.info(f'GET {request.path} (DB QUERY)')
        queryset = self.get_queryset()
        resumen = self._calcular_resumen(queryset)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['resumen'] = resumen
            cache.set(cache_key, response.data, 300) # 5 min
            return response

        serializer = self.get_serializer(queryset, many=True)
        result = {
            'results': serializer.data,
            'resumen': resumen,
        }
        cache.set(cache_key, result, 300)
        return Response(result)

    def _calcular_resumen(self, qs):
        entradas = qs.filter(
            tipo_movimiento__in=['ENTRADA', 'ENTRADA_TRANSFERENCIA', 'AJUSTE_POSITIVO'],
        ).count()
        salidas = qs.filter(
            tipo_movimiento__in=['SALIDA', 'SALIDA_TRANSFERENCIA', 'AJUSTE_NEGATIVO'],
        ).count()
        ajustes = qs.filter(
            tipo_movimiento__in=['AJUSTE_POSITIVO', 'AJUSTE_NEGATIVO'],
        ).count()
        return {
            'entradas': entradas,
            'salidas': salidas,
            'ajustes': ajustes,
        }


class ValoracionInventarioView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]

    def get(self, request):
        mercado = request.user.mercado
        mercado_id = mercado.id if mercado else None
        page_number = request.query_params.get('page', 1)
        page_size = int(request.query_params.get('page_size', 10))
        version = get_mercado_cache_version(mercado_id)
        cache_key = f"valoracion_mercado_{mercado_id}_v{version}_page{page_number}_ps{page_size}"
        use_cache = page_size == 10


        if use_cache:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)

        logger.info(f'GET {request.path} (DB QUERY)')

        productos_qs = Producto.objects.filter(stock__gt=0)
        if mercado:
            productos_qs = productos_qs.filter(mercado=mercado)
        
        productos_qs = productos_qs.annotate(
            valor_costo=ExpressionWrapper(F('stock') * F('costo'), output_field=DecimalField()),
            valor_venta=ExpressionWrapper(F('stock') * F('precio'), output_field=DecimalField()),
            utilidad_proyectada=ExpressionWrapper(F('stock') * (F('precio') - F('costo')), output_field=DecimalField()),
        ).order_by('-valor_costo')

        from django.core.paginator import Paginator
        paginator = Paginator(productos_qs, page_size)
        page_obj = paginator.get_page(page_number)

        productos_data = []
        for p in page_obj:
            productos_data.append({
                'id': p.id,
                'nombre': p.nombre,
                'stock': str(p.stock),
                'costo': str(p.costo),
                'precio': str(p.precio),
                'valor_total': str(p.valor_costo),
                'valor_venta': str(p.valor_venta),
                'utilidad_proyectada': str(p.utilidad_proyectada),
                'categoria': {'nombre': p.categoria.nombre} if p.categoria else None,
            })

        categorias_valor = Categoria.objects.annotate(
            valor_categoria=Sum(F('producto__stock') * F('producto__costo')),
        )
        if mercado:
            categorias_valor = categorias_valor.filter(mercado=mercado)
        categorias_valor = categorias_valor.filter(valor_categoria__gt=0).order_by('-valor_categoria')

        cat_ids = [c.id for c in categorias_valor]
        mfilter_p = {'categoria_id__in': cat_ids, 'stock__gt': 0}
        if mercado:
            mfilter_p['mercado'] = mercado
        items_counts = Producto.objects.filter(**mfilter_p).values('categoria_id').annotate(cnt=Count('id'))
        items_map = {i['categoria_id']: i['cnt'] for i in items_counts}

        categorias_data = []
        for c in categorias_valor:
            categorias_data.append({
                'id': c.id,
                'nombre': c.nombre,
                'total_items': items_map.get(c.id, 0),
                'valor_categoria': str(c.valor_categoria),
            })

        totales = productos_qs.aggregate(
            gran_total_costo=Sum('valor_costo'),
            gran_total_venta=Sum('valor_venta'),
            utilidad_potencial=Sum('utilidad_proyectada'),
            total_unidades=Sum('stock'),
        )

        costo_t = totales['gran_total_costo'] or Decimal('0.00')
        venta_t = totales['gran_total_venta'] or Decimal('0.00')
        util_t = totales['utilidad_potencial'] or Decimal('0.00')
        margen_p = float((util_t / venta_t) * 100) if venta_t > 0 else 0.0

        response_data = {
            'productos': productos_data,
            'pagination': {
                'count': paginator.count,
                'total_pages': paginator.num_pages,
                'num_pages': paginator.num_pages,
                'current_page': page_obj.number,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'next': page_obj.has_next(),
                'previous': page_obj.has_previous(),
                'page_size': page_size,
            },

            'categorias_valor': categorias_data,
            'gran_total': str(costo_t),
            'gran_total_costo': str(costo_t),
            'gran_total_venta': str(venta_t),
            'utilidad_potencial': str(util_t),
            'margen_potencial_porcentaje': round(margen_p, 2),
            'total_unidades': str(totales['total_unidades'] or 0),
        }
        
        if use_cache:
            cache.set(cache_key, response_data, 600)

        return Response(response_data)


class ReporteVencimientosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mercado = request.user.mercado
        mercado_id = mercado.id if mercado else None
        page_number = request.query_params.get('page', 1)
        version = get_mercado_cache_version(mercado_id)
        params_str = "_".join([f"{k}:{v}" for k, v in sorted(request.query_params.items())])
        cache_key = f"vencimientos_mercado_{mercado_id}_v{version}_{params_str}"
        
        page_size = int(request.query_params.get('page_size', 25))
        use_cache = page_size == 25

        if use_cache:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)

        logger.info(f'GET {request.path} (DB QUERY)')
        q = request.query_params.get('q')
        categoria_id = request.query_params.get('categoria')
        estado = request.query_params.get('estado')

        hoy = timezone.now().date()
        fecha_critica = hoy + timezone.timedelta(days=7)
        fecha_advertencia = hoy + timezone.timedelta(days=30)

        # Base queryset
        unidades_qs = UnidadProducto.objects.filter(
            estado='disponible',
            cantidad__gt=0,
        )
        if mercado:
            unidades_qs = unidades_qs.filter(mercado=mercado)

        # Apply filters BEFORE aggregation to keep summary consistent if needed, 
        # but usually summary is for the WHOLE inventory. 
        # The user wants "filters for control de vencimientos", so they likely apply to the list.

        if q:
            unidades_qs = unidades_qs.filter(producto__nombre__icontains=q)
        if categoria_id:
            unidades_qs = unidades_qs.filter(producto__categoria_id=categoria_id)
        
        # Aggregate quantities by product and expiration date
        aggregated_qs = unidades_qs.values(
            'producto_id', 
            'producto__nombre', 
            'producto__categoria__nombre', 
            'fecha_vencimiento'
        ).annotate(
            total_cantidad=Sum('cantidad')
        ).order_by('fecha_vencimiento', 'producto__nombre')

        # Filter by status (on aggregated results)
        if estado:
            if estado == 'vencido':
                aggregated_qs = [u for u in aggregated_qs if u['fecha_vencimiento'] < hoy]
            elif estado == 'critico':
                aggregated_qs = [u for u in aggregated_qs if hoy <= u['fecha_vencimiento'] <= fecha_critica]
            elif estado == 'advertencia':
                aggregated_qs = [u for u in aggregated_qs if fecha_critica < u['fecha_vencimiento'] <= fecha_advertencia]
            elif estado == 'seguro':
                aggregated_qs = [u for u in aggregated_qs if u['fecha_vencimiento'] > fecha_advertencia]
            
            total_lotes = len(aggregated_qs)
        else:
            total_lotes = aggregated_qs.count()

        # Summary counts (based on ALL available units in mercado, or filtered?)
        # Usually summary cards show the state of the WHOLE inventory.
        all_unidades_agg = UnidadProducto.objects.filter(
            mercado=mercado, estado='disponible', cantidad__gt=0
        ).values('producto_id', 'fecha_vencimiento').annotate(total=Sum('cantidad'))
        
        criticos_count = 0
        advertencia_count = 0
        for u in all_unidades_agg:
            fv = u['fecha_vencimiento']
            if fv <= fecha_critica:
                criticos_count += 1
            elif fv <= fecha_advertencia:
                advertencia_count += 1

        # Pagination for aggregated_qs (which might be a list now if filtered by status)
        from django.core.paginator import Paginator
        paginator = Paginator(aggregated_qs, page_size)
        page_obj = paginator.get_page(page_number)

        # Map data for frontend
        unidades_data = []
        for u in page_obj:
            unidades_data.append({
                'producto': {
                    'nombre': u['producto__nombre'],
                    'categoria': {'nombre': u['producto__categoria__nombre']}
                },
                'cantidad': float(u['total_cantidad']),
                'fecha_vencimiento': u['fecha_vencimiento']
            })

        response_data = {
            'unidades': unidades_data,
            'pagination': {
                'count': paginator.count,
                'num_pages': paginator.num_pages,
                'current_page': page_obj.number,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            },
            'resumen': {
                'criticos': criticos_count,
                'advertencia': advertencia_count,
                'total': len(all_unidades_agg),
            },
        }
        cache.set(cache_key, response_data, 600) # 10 min
        return Response(response_data)


class TransferenciaViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return TransferenciaListSerializer
        return TransferenciaSerializer

    def get_queryset(self):
        usuario = self.request.user
        if usuario.mercado is None:
            qs = Transferencia.objects.all()
        else:
            qs = Transferencia.objects.filter(
                Q(mercado_origen=usuario.mercado) | Q(mercado_destino=usuario.mercado),
            )

        qs = qs.select_related('mercado_origen', 'mercado_destino', 'usuario_envio', 'usuario_recepcion')
        if self.action != 'list':
            qs = qs.prefetch_related('detalles__producto_origen__categoria', 'detalles__producto_destino__categoria')


        estado = self.request.query_params.get('estado')
        q = self.request.query_params.get('q')

        if estado:
            qs = qs.filter(estado=estado)
        if q:
            qs = qs.filter(
                Q(id__icontains=q) |
                Q(mercado_origen__nombre__icontains=q) |
                Q(mercado_destino__nombre__icontains=q)
            )

        return qs.order_by('-fecha_envio')

    def list(self, request):
        mercado_id = request.user.mercado_id
        version = get_mercado_cache_version(mercado_id)
        params_str = "_".join([f"{k}:{v}" for k, v in sorted(request.query_params.items())])
        cache_key = f"transferencias_mercado_{mercado_id}_v{version}_{params_str}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            res_data = self.get_paginated_response(serializer.data).data
            cache.set(cache_key, res_data, 300)
            return Response(res_data)
        serializer = self.get_serializer(queryset, many=True)
        res_data = serializer.data
        cache.set(cache_key, res_data, 300)
        return Response(res_data)


    def retrieve(self, request, pk=None):
        transferencia = self.get_object()
        serializer = self.get_serializer(transferencia)
        return Response(serializer.data)

    @transaction.atomic
    def create(self, request):
        mercado_actual = request.user.mercado
        mercado_destino_id = request.data.get('mercado_destino_id')
        productos_data = request.data.get('productos')
        productos_json = request.data.get('productos_json')
        observaciones = request.data.get('observaciones', '')

        if not mercado_destino_id:
            return Response({'error': 'mercado_destino_id es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        if not productos_data and not productos_json:
            return Response({'error': 'productos o productos_json es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        # Convert products to a common format: { producto_id: cantidad }
        final_products = {}
        if productos_json:
            if isinstance(productos_json, str):
                productos_json = json.loads(productos_json)
            final_products = productos_json
        elif productos_data:
            for item in productos_data:
                final_products[str(item['producto_id'])] = item['cantidad']

        mercado_dest = Mercado.objects.get(pk=mercado_destino_id)

        if mercado_dest == mercado_actual:
            return Response({'error': 'No puedes transferir al mismo mercado.'}, status=status.HTTP_400_BAD_REQUEST)

        transf = Transferencia.objects.create(
            mercado_origen=mercado_actual,
            mercado_destino=mercado_dest,
            usuario_envio=request.user,
            estado='EN_TRANSITO',
            observaciones=observaciones
        )

        errores = []

        for producto_id_str, cant_total in final_products.items():
            cant_total = Decimal(str(cant_total))
            try:
                prod = Producto.objects.select_for_update().get(pk=producto_id_str, mercado=mercado_actual)
            except Producto.DoesNotExist:
                errores.append(f'Producto ID {producto_id_str} no encontrado en tu mercado.')
                continue

            if prod.stock < cant_total:
                errores.append(f'Stock insuficiente: {prod.nombre}')
                continue

            saldo_ant_global = prod.stock

            exito, error_msg, _ = descontar_stock_fefo(prod, cant_total, mercado_actual)
            if not exito:
                errores.append(f'{prod.nombre}: {error_msg}')
                continue

            # Record the transfer detail
            TransferenciaDetalle.objects.create(
                transferencia=transf,
                producto_origen=prod,
                cantidad=cant_total,
                fecha_vencimiento=None,
            )

            prod.stock -= cant_total
            prod.save()

            crear_kardex(
                producto=prod, mercado=mercado_actual,
                tipo_movimiento='SALIDA_TRANSFERENCIA', cantidad=cant_total,
                saldo_anterior=saldo_ant_global, saldo_nuevo=prod.stock,
                ref_tipo='Transf. Enviada', ref_id=transf.id,
                usuario=request.user,
            )

        if errores:
            return Response({
                'transferencia': TransferenciaSerializer(transf).data,
                'errores': errores,
            }, status=status.HTTP_207_MULTI_STATUS)

        return Response(TransferenciaSerializer(transf).data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    @action(detail=True, methods=['post'])
    def recibir(self, request, pk=None):
        t = self.get_object()
        if t.estado != 'EN_TRANSITO':
            return Response({'error': 'Solo se pueden recibir transferencias en tránsito.'}, status=status.HTTP_400_BAD_REQUEST)

        mercado_dest = request.user.mercado

        for det in t.detalles.all():
            prod_dest, creado = Producto.objects.get_or_create(
                nombre=det.producto_origen.nombre,
                mercado=mercado_dest,
                defaults={
                    'precio': det.producto_origen.precio,
                    'costo': det.producto_origen.costo,
                    'stock': 0,
                    'unidad_medida': det.producto_origen.unidad_medida,
                    'stock_minimo': det.producto_origen.stock_minimo,
                },
            )
            if creado and det.producto_origen.categoria:
                cat_dest, _ = Categoria.objects.get_or_create(
                    nombre=det.producto_origen.categoria.nombre,
                    mercado=mercado_dest,
                )
                prod_dest.categoria = cat_dest
                prod_dest.save()

            saldo_ant = prod_dest.stock

            fecha_venc = det.fecha_vencimiento
            if not fecha_venc:
                fecha_venc = "2099-12-31"

            UnidadProducto.objects.create(
                producto=prod_dest,
                mercado=mercado_dest,
                fecha_vencimiento=fecha_venc,
                cantidad=det.cantidad,
                estado='disponible',
            )

            prod_dest.stock += det.cantidad
            prod_dest.save()
            det.producto_destino = prod_dest
            det.save()

            Kardex.objects.create(
                producto=prod_dest,
                mercado=mercado_dest,
                tipo_movimiento='ENTRADA_TRANSFERENCIA',
                cantidad=det.cantidad,
                saldo_anterior=saldo_ant,
                saldo_nuevo=prod_dest.stock,
                referencia_tipo='Transf. Recibida',
                referencia_id=t.id,
                usuario=request.user,
            )

        t.estado = 'COMPLETADA'
        t.usuario_recepcion = request.user
        t.fecha_recepcion = timezone.now()
        t.save()

        return Response(TransferenciaSerializer(t).data, status=status.HTTP_200_OK)

    @transaction.atomic
    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        t = self.get_object()
        if t.estado != 'EN_TRANSITO':
            return Response({'error': 'Solo se pueden rechazar transferencias en tránsito.'}, status=status.HTTP_400_BAD_REQUEST)
        if request.user.mercado != t.mercado_destino:
            return Response({'error': 'Solo el mercado destino puede rechazar.'}, status=status.HTTP_403_FORBIDDEN)

        motivo = request.data.get('motivo_rechazo', '')

        for det in t.detalles.all():
            prod_orig = det.producto_origen
            saldo_ant = prod_orig.stock
            prod_orig.stock += det.cantidad
            prod_orig.save()

            devolver_stock_a_unidades(prod_orig, det.cantidad, t.mercado_origen, det.fecha_vencimiento)

            crear_kardex(
                producto=prod_orig, mercado=t.mercado_origen,
                tipo_movimiento='ENTRADA', cantidad=det.cantidad,
                saldo_anterior=saldo_ant, saldo_nuevo=prod_orig.stock,
                ref_tipo='Transferencia Rechazada', ref_id=t.id,
                ref_detalle=f'Devuelto por {t.mercado_destino.nombre}. Motivo: {motivo}',
                usuario=request.user,
            )

        t.estado = 'CANCELADA'
        t.observaciones += f'\n[RECHAZADA por {request.user.username}]: {motivo}'
        t.save()

        return Response(TransferenciaSerializer(t).data, status=status.HTTP_200_OK)

    @transaction.atomic
    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        t = self.get_object()
        if t.estado != 'EN_TRANSITO':
            return Response({'error': 'Solo se pueden anular transferencias en tránsito.'}, status=status.HTTP_400_BAD_REQUEST)
        if request.user.mercado != t.mercado_origen:
            return Response({'error': 'Solo el mercado origen puede anular.'}, status=status.HTTP_403_FORBIDDEN)

        for det in t.detalles.all():
            prod_orig = det.producto_origen
            saldo_ant = prod_orig.stock
            prod_orig.stock += det.cantidad
            prod_orig.save()

            devolver_stock_a_unidades(prod_orig, det.cantidad, t.mercado_origen, det.fecha_vencimiento)

            crear_kardex(
                producto=prod_orig, mercado=t.mercado_origen,
                tipo_movimiento='ENTRADA', cantidad=det.cantidad,
                saldo_anterior=saldo_ant, saldo_nuevo=prod_orig.stock,
                ref_tipo='Transferencia Anulada', ref_id=t.id,
                ref_detalle=f'Anulada por emisor: {request.user.username}',
                usuario=request.user,
            )

        t.estado = 'CANCELADA'
        t.observaciones += f'\n[ANULADA por emisor {request.user.username}]'
        t.save()

        return Response(TransferenciaSerializer(t).data, status=status.HTTP_200_OK)


class MercadoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = MercadoSerializer
    ordering = ['nombre']

    def get_queryset(self):
        usuario = self.request.user
        rol_upper = str(getattr(usuario, 'rol', '') or '').upper()
        is_admin_user = (rol_upper in ['ADMIN', 'ADMINISTRADOR'] or usuario.is_staff or usuario.is_superuser)

        if is_admin_user and self.request.query_params.get('manage') == 'true':
            return Mercado.objects.all()

        qs = Mercado.objects.filter(activo=True)
        if self.request.query_params.get('all') != 'true':
            qs = qs.exclude(pk=usuario.mercado_id)
        return qs

    @action(detail=False, methods=['post'], url_path='update-global')
    def update_global(self, request):
        usuario = request.user
        rol_upper = str(getattr(usuario, 'rol', '') or '').upper()
        is_admin_user = (rol_upper in ['ADMIN', 'ADMINISTRADOR'] or usuario.is_staff or usuario.is_superuser)

        if not is_admin_user:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
            
        nombre_negocio = request.data.get('nombre_negocio', '').strip()
        ruc = request.data.get('ruc', '').strip()
        telefono = request.data.get('telefono', '').strip()
        
        if not nombre_negocio or not ruc:
            return Response({'error': 'Nombre de negocio y RUC son requeridos'}, status=status.HTTP_400_BAD_REQUEST)
            
        with transaction.atomic():
            for m in Mercado.objects.all():
                full_name = m.nombre
                branch_name = ""
                if " - " in full_name:
                    branch_name = full_name.split(" - ", 1)[1].strip()
                elif full_name.startswith("Minimarket "):
                    branch_name = full_name[11:].strip()
                else:
                    branch_name = ""
                        
                if branch_name:
                    m.nombre = f"{nombre_negocio} - {branch_name}"
                else:
                    m.nombre = nombre_negocio
                    
                m.ruc = ruc
                m.telefono = telefono
                m.save()

        from inventario.utils import invalidate_mercado_cache
        invalidate_mercado_cache(None)
                
        return Response({'status': 'ok'})




class ExportarProductosExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mercado = request.user.mercado
        productos = Producto.objects.filter(
            mercado=mercado
        ).select_related('categoria').order_by('nombre')

        data = []
        for p in productos:
            data.append({
                'Nombre': p.nombre,
                'Codigo Barras': p.codigo_barras or '',
                'Categoria': p.categoria.nombre if p.categoria else '',
                'Unidad Medida': p.get_unidad_medida_display() if hasattr(p, 'get_unidad_medida_display') else p.unidad_medida,
                'Stock': float(p.stock),
                'Stock Minimo': float(p.stock_minimo),
                'Precio': float(p.precio),
                'Costo': float(p.costo),
            })

        df = pd.DataFrame(data)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        hoy = timezone.localtime(timezone.now()).strftime('%Y-%m-%d')
        response['Content-Disposition'] = f'attachment; filename="productos_{hoy}.xlsx"'

        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Productos')

        return response
