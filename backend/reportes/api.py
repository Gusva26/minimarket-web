from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db.models import Sum, Count, Q, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from datetime import timedelta, datetime
from django.http import HttpResponse
from django.core.cache import cache

from .serializers import ReporteVentasSerializer
from inventario.utils import get_mercado_cache_version
from ventas.models import Venta, VentaDetalle, Caja
from inventario.models import Producto
from usuarios.api import IsAdminOrSuperUser

import pandas as pd


class ReporteVentasView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperUser]

    def get(self, request):
        mercado_admin = request.user.mercado
        version = get_mercado_cache_version(mercado_admin.id)
        
        # Generar una llave de caché basada en los parámetros de búsqueda y la versión
        params_str = "_".join([f"{k}:{v}" for k, v in sorted(request.query_params.items())])
        cache_key = f"reporte_ventas_{mercado_admin.id}_v{version}_{params_str}"
        
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        ahora = timezone.now().strftime('%d/%b/%Y %H:%M:%S')
        print(f'[{ahora}] "GET {request.path} HTTP/1.1" 200 (DB QUERY)')
        serializer = ReporteVentasSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        ahora = timezone.localtime(timezone.now())
        hoy = ahora.date()
        filtro = data.get('filtro', 'hoy')

        fecha_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = ahora.replace(hour=23, minute=59, second=59, microsecond=999999)

        if filtro == 'semana':
            lunes = hoy - timedelta(days=hoy.weekday())
            fecha_inicio = timezone.make_aware(datetime.combine(lunes, datetime.min.time()))
            fecha_fin = ahora.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif filtro == 'mes':
            primero = hoy.replace(day=1)
            fecha_inicio = timezone.make_aware(datetime.combine(primero, datetime.min.time()))
            fecha_fin = ahora.replace(hour=23, minute=59, second=59, microsecond=999999)

        if data.get('fecha_exacta'):
            fecha_dt = data['fecha_exacta']
            fecha_inicio = timezone.make_aware(datetime.combine(fecha_dt, datetime.min.time()))
            fecha_fin = timezone.make_aware(datetime.combine(fecha_dt, datetime.max.time()))

        if data.get('fecha_inicio'):
            fecha_inicio = data['fecha_inicio']
        if data.get('fecha_fin'):
            fecha_fin = data['fecha_fin']

        mercado_admin = request.user.mercado

        ventas = Venta.objects.filter(
            mercado=mercado_admin,
            fecha_hora__range=(fecha_inicio, fecha_fin)
        )
        detalles = VentaDetalle.objects.filter(
            venta__mercado=mercado_admin,
            venta__fecha_hora__range=(fecha_inicio, fecha_fin)
        )
        cajas = Caja.objects.filter(
            mercado=mercado_admin,
            fecha_apertura__range=(fecha_inicio, fecha_fin),
            estado='CERRADA',
        )

        usuario_id = data.get('usuario_id')
        categoria_id = data.get('categoria_id')
        metodo_pago = data.get('metodo_pago')

        if usuario_id:
            ventas = ventas.filter(usuario_id=usuario_id)
            detalles = detalles.filter(venta__usuario_id=usuario_id)
            cajas = cajas.filter(usuario_id=usuario_id)
        if metodo_pago:
            ventas = ventas.filter(metodo_pago=metodo_pago)
            detalles = detalles.filter(venta__metodo_pago=metodo_pago)
        if categoria_id:
            ventas = ventas.filter(detalles__producto__categoria_id=categoria_id).distinct()
            detalles = detalles.filter(producto__categoria_id=categoria_id)

        utilidad_data = detalles.annotate(
            costo_total=ExpressionWrapper(
                F('cantidad') * F('producto__costo'),
                output_field=DecimalField(),
            ),
            ganancia_fila=ExpressionWrapper(
                F('subtotal') - (F('cantidad') * F('producto__costo')),
                output_field=DecimalField(),
            ),
        ).aggregate(
            total_ingresos=Sum('subtotal'),
            total_costos=Sum('costo_total'),
            utilidad_total=Sum('ganancia_fila'),
        )

        total_vendido = utilidad_data['total_ingresos'] or 0
        costo_total = utilidad_data['total_costos'] or 0
        utilidad_total = utilidad_data['utilidad_total'] or 0
        margen_porcentaje = float((utilidad_total / total_vendido * 100)) if total_vendido > 0 else 0
        cantidad_ventas = ventas.count()

        top_productos = list(detalles.values('producto__nombre', 'producto_id').annotate(
            total_qty=Sum('cantidad'),
            total_revenue=Sum('subtotal'),
        ).order_by('-total_revenue')[:10])

        detalles_periodo = VentaDetalle.objects.filter(
            venta__mercado=mercado_admin,
            venta__fecha_hora__range=(fecha_inicio, fecha_fin),
        )
        ids_vendidos = detalles_periodo.values_list('producto_id', flat=True).distinct()

        baja_rotacion_qs = Producto.objects.filter(
            mercado=mercado_admin,
            stock__gt=0,
        ).exclude(id__in=ids_vendidos).order_by('stock')[:10]

        baja_rotacion = list(baja_rotacion_qs.values('id', 'nombre', 'stock'))

        audit_cajas_data = cajas.annotate(
            total_real=ExpressionWrapper(
                F('monto_final_efectivo_real') + F('monto_final_yape_real') + F('monto_final_plin_real'),
                output_field=DecimalField(),
            ),
            total_esperado=ExpressionWrapper(
                F('monto_esperado_efectivo') + F('monto_esperado_yape') + F('monto_esperado_plin'),
                output_field=DecimalField(),
            ),
        )
        descuadre_total = 0
        for c in audit_cajas_data:
            m_real = float(c.total_real or 0)
            m_esp = float(c.total_esperado or 0)
            descuadre_total += (m_real - m_esp)

        audit_cajas = float(descuadre_total)

        metodos = ventas.values('metodo_pago').annotate(
            total=Count('metodo_pago')
        ).order_by('-total')

        ventas_time = {}
        for v in ventas.order_by('fecha_hora'):
            key = v.fecha_hora.strftime('%H:00') if filtro == 'hoy' else v.fecha_hora.strftime('%d/%m')
            ventas_time[key] = ventas_time.get(key, 0) + float(v.total)

        result = {
            'total_vendido': float(total_vendido),
            'utilidad_total': float(utilidad_total),
            'margen_porcentaje': round(margen_porcentaje, 2),
            'cantidad_ventas': cantidad_ventas,
            'costo_total': float(costo_total),
            'top_productos': top_productos,
            'baja_rotacion': baja_rotacion,
            'audit_cajas': audit_cajas,
            'fechas_chart': list(ventas_time.keys()),
            'totales_chart': list(ventas_time.values()),
            'metodos_pago_chart': [m['metodo_pago'] for m in metodos],
            'totales_metodos_chart': [m['total'] for m in metodos],
        }

        cache.set(cache_key, result, 600)  # 10 minutos
        return Response(result)


class ExportarReporteExcelView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperUser]

    def get(self, request):
        ahora = timezone.localtime(timezone.now())
        hoy = ahora.date()

        mercado_admin = request.user.mercado
        filtro = request.query_params.get('filtro', 'hoy')

        fecha_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = ahora.replace(hour=23, minute=59, second=59, microsecond=999999)

        if filtro == 'semana':
            lunes = hoy - timedelta(days=hoy.weekday())
            fecha_inicio = timezone.make_aware(datetime.combine(lunes, datetime.min.time()))
        elif filtro == 'mes':
            primero = hoy.replace(day=1)
            fecha_inicio = timezone.make_aware(datetime.combine(primero, datetime.min.time()))

        ventas = Venta.objects.filter(
            mercado=mercado_admin,
            fecha_hora__range=(fecha_inicio, fecha_fin),
        ).order_by('-fecha_hora')

        data = []
        for v in ventas:
            data.append({
                'N°': v.numero,
                'Serie': v.serie,
                'Fecha': v.fecha_hora.strftime('%d/%m/%Y %H:%M'),
                'Cliente': v.cliente.nombre if v.cliente else 'Público General',
                'Vendedor': v.usuario.username if v.usuario else '',
                'Método Pago': v.metodo_pago,
                'Subtotal': float(v.subtotal),
                'IGV': float(v.igv),
                'Total': float(v.total),
                'Estado': v.estado,
            })

        df = pd.DataFrame(data)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="reporte_ventas_{hoy}.xlsx"'

        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Ventas')

        return response


class ExportarReportePDFView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperUser]

    def get(self, request):
        ahora = timezone.localtime(timezone.now())
        hoy = ahora.date()

        mercado_admin = request.user.mercado
        filtro = request.query_params.get('filtro', 'hoy')

        fecha_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = ahora.replace(hour=23, minute=59, second=59, microsecond=999999)

        if filtro == 'semana':
            lunes = hoy - timedelta(days=hoy.weekday())
            fecha_inicio = timezone.make_aware(datetime.combine(lunes, datetime.min.time()))
        elif filtro == 'mes':
            primero = hoy.replace(day=1)
            fecha_inicio = timezone.make_aware(datetime.combine(primero, datetime.min.time()))

        ventas = Venta.objects.filter(
            mercado=mercado_admin,
            fecha_hora__range=(fecha_inicio, fecha_fin),
        ).order_by('-fecha_hora')

        total_ventas = ventas.aggregate(total=Sum('total'))['total'] or 0

        html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; font-size: 12px; }}
                h1 {{ text-align: center; font-size: 18px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #333; padding: 6px; text-align: left; }}
                th {{ background-color: #f0f0f0; }}
                .total {{ text-align: right; font-weight: bold; margin-top: 10px; }}
            </style>
        </head>
        <body>
            <h1>Reporte de Ventas - {hoy}</h1>
            <p>Mercado: {mercado_admin.nombre if mercado_admin else 'General'}</p>
            <p>Período: {fecha_inicio.strftime('%d/%m/%Y %H:%M')} - {fecha_fin.strftime('%d/%m/%Y %H:%M')}</p>
            <table>
                <tr>
                    <th>#</th><th>Fecha</th><th>Cliente</th><th>Vendedor</th><th>Método</th><th>Total</th>
                </tr>
        """

        for idx, v in enumerate(ventas, 1):
            html += f"""
                <tr>
                    <td>{v.serie}-{v.numero:06d}</td>
                    <td>{v.fecha_hora.strftime('%d/%m/%Y %H:%M')}</td>
                    <td>{v.cliente.nombre if v.cliente else 'Público General'}</td>
                    <td>{v.usuario.username if v.usuario else ''}</td>
                    <td>{v.metodo_pago}</td>
                    <td>S/ {float(v.total):.2f}</td>
                </tr>
            """

        html += f"""
            </table>
            <p class="total">Total General: S/ {float(total_ventas):.2f}</p>
            <p class="total">Cantidad de Ventas: {ventas.count()}</p>
        </body>
        </html>
        """

        try:
            from xhtml2pdf import pisa
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="reporte_ventas_{hoy}.pdf"'
            pisa_status = pisa.CreatePDF(html, dest=response)
            if pisa_status.err:
                return Response(
                    {'error': 'Error al generar el PDF'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            return response
        except ImportError:
            return Response(
                {'error': 'xhtml2pdf no está instalado'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
