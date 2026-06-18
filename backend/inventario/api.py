import json
import logging
from decimal import Decimal

import pandas as pd
from django.db import transaction
from django.db.models import Count, F, Sum, Q
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

logger = logging.getLogger(__name__)

from .models import (
    Categoria, Kardex, UnidadProducto, Mercado, Producto,
    Transferencia, TransferenciaDetalle,
)
from .serializers import (
    CategoriaSerializer, KardexSerializer, UnidadProductoSerializer,
    MercadoSerializer, ProductoCreateUpdateSerializer, ProductoSerializer,
    TransferenciaSerializer,
)

from .utils import (
    descontar_stock_fefo, devolver_stock_a_unidades, crear_kardex,
    get_mercado_cache_version, invalidate_mercado_cache
)


class ProductoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ['nombre', 'codigo_barras']
    ordering_fields = ['nombre', 'precio', 'stock']
    ordering = ['nombre']

    def get_queryset(self):
        qs = Producto.objects.filter(mercado=self.request.user.mercado).select_related('categoria', 'mercado')

        categoria = self.request.query_params.get('categoria')
        if categoria:
            qs = qs.filter(categoria_id=categoria)

        stock_status = self.request.query_params.get('stock_status')
        if stock_status == 'bajo':
            qs = qs.filter(stock__gt=0, stock__lt=F('stock_minimo'))
        elif stock_status == 'sin_stock':
            qs = qs.filter(stock=0)
        elif stock_status == 'normal':
            qs = qs.filter(stock__gte=F('stock_minimo'))

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
        serializer.save(mercado=self.request.user.mercado)

    def perform_update(self, serializer):
        serializer.save(mercado=self.request.user.mercado)

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
        producto = self.get_object()
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
        return Categoria.objects.filter(mercado=self.request.user.mercado).annotate(
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
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    serializer_class = KardexSerializer

    def get_queryset(self):
        qs = Kardex.objects.filter(mercado=self.request.user.mercado)
        producto_id = self.request.query_params.get('producto_id')
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')

        if producto_id:
            qs = qs.filter(producto_id=producto_id)
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
        page_number = request.query_params.get('page', 1)
        page_size = int(request.query_params.get('page_size', 25))
        version = get_mercado_cache_version(mercado.id)
        cache_key = f"valoracion_mercado_{mercado.id}_v{version}_page{page_number}_ps{page_size}"
        use_cache = page_size == 25

        if use_cache:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)

        logger.info(f'GET {request.path} (DB QUERY)')

        productos_qs = Producto.objects.filter(mercado=mercado, stock__gt=0).annotate(
            valor_total=F('stock') * F('costo'),
        ).order_by('-valor_total')

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
                'valor_total': str(p.valor_total),
                'categoria': {'nombre': p.categoria.nombre} if p.categoria else None,
            })

        categorias_valor = Categoria.objects.filter(mercado=mercado).annotate(
            valor_categoria=Sum(F('producto__stock') * F('producto__costo')),
        ).filter(valor_categoria__gt=0).order_by('-valor_categoria')

        cat_ids = [c.id for c in categorias_valor]
        items_counts = Producto.objects.filter(
            categoria_id__in=cat_ids, mercado=mercado, stock__gt=0
        ).values('categoria_id').annotate(cnt=Count('id'))
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
            gran_total=Sum(F('stock') * F('costo')),
            total_unidades=Sum('stock'),
        )

        response_data = {
            'productos': productos_data,
            'pagination': {
                'count': paginator.count,
                'num_pages': paginator.num_pages,
                'current_page': page_obj.number,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            },
            'categorias_valor': categorias_data,
            'gran_total': str(totales['gran_total'] or 0),
            'total_unidades': str(totales['total_unidades'] or 0),
        }
        
        if use_cache:
            cache.set(cache_key, response_data, 600) # 10 min
        return Response(response_data)


class ReporteVencimientosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mercado = request.user.mercado
        page_number = request.query_params.get('page', 1)
        version = get_mercado_cache_version(mercado.id)
        params_str = "_".join([f"{k}:{v}" for k, v in sorted(request.query_params.items())])
        cache_key = f"vencimientos_mercado_{mercado.id}_v{version}_{params_str}"
        
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
            mercado=mercado,
            estado='disponible',
            cantidad__gt=0,
        )

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
    serializer_class = TransferenciaSerializer

    def get_queryset(self):
        usuario = self.request.user
        if not usuario.mercado:
            return Transferencia.objects.none()
        qs = Transferencia.objects.filter(
            Q(mercado_origen=usuario.mercado) | Q(mercado_destino=usuario.mercado),
        )

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
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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


class MercadoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MercadoSerializer
    ordering = ['nombre']

    def get_queryset(self):
        usuario = self.request.user
        qs = Mercado.objects.filter(activo=True)
        if self.request.query_params.get('all') != 'true':
            qs = qs.exclude(pk=usuario.mercado_id)
        return qs
