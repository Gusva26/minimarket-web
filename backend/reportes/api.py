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
        mercado_id = mercado_admin.id if mercado_admin else None
        version = get_mercado_cache_version(mercado_id)
        
        params_str = "_".join([f"{k}:{v}" for k, v in sorted(request.query_params.items())])
        cache_key = f"reporte_ventas_{mercado_id or 'all'}_v{version}_{params_str}"
        
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        ahora = timezone.localtime(timezone.now())
        hoy = ahora.date()

        serializer = ReporteVentasSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        filtro = data.get('filtro', 'hoy')

        fecha_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = ahora.replace(hour=23, minute=59, second=59, microsecond=999999)

        if filtro == 'ayer':
            ayer = hoy - timedelta(days=1)
            fecha_inicio = timezone.make_aware(datetime.combine(ayer, datetime.min.time()))
            fecha_fin = timezone.make_aware(datetime.combine(ayer, datetime.max.time()))
        elif filtro == 'semana':
            lunes = hoy - timedelta(days=hoy.weekday())
            fecha_inicio = timezone.make_aware(datetime.combine(lunes, datetime.min.time()))
            fecha_fin = ahora.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif filtro == 'mes':
            primero = hoy.replace(day=1)
            fecha_inicio = timezone.make_aware(datetime.combine(primero, datetime.min.time()))
            fecha_fin = ahora.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif filtro == 'mes_anterior':
            primer_dia_este_mes = hoy.replace(day=1)
            ultimo_dia_mes_pasado = primer_dia_este_mes - timedelta(days=1)
            primer_dia_mes_pasado = ultimo_dia_mes_pasado.replace(day=1)
            fecha_inicio = timezone.make_aware(datetime.combine(primer_dia_mes_pasado, datetime.min.time()))
            fecha_fin = timezone.make_aware(datetime.combine(ultimo_dia_mes_pasado, datetime.max.time()))

        if data.get('fecha_exacta'):
            fecha_dt = data['fecha_exacta']
            fecha_inicio = timezone.make_aware(datetime.combine(fecha_dt, datetime.min.time()))
            fecha_fin = timezone.make_aware(datetime.combine(fecha_dt, datetime.max.time()))

        if data.get('fecha_inicio'):
            fecha_inicio = data['fecha_inicio']
        if data.get('fecha_fin'):
            fecha_fin = data['fecha_fin']

        mfiltro_v = {'fecha_hora__range': (fecha_inicio, fecha_fin)}
        mfiltro_d = {'venta__fecha_hora__range': (fecha_inicio, fecha_fin)}
        mfiltro_c = {'fecha_apertura__range': (fecha_inicio, fecha_fin), 'estado': 'CERRADA'}
        mfiltro_p = {}

        if mercado_admin:
            mfiltro_v['mercado'] = mercado_admin
            mfiltro_d['venta__mercado'] = mercado_admin
            mfiltro_c['mercado'] = mercado_admin
            mfiltro_p['mercado'] = mercado_admin

        ventas = Venta.objects.filter(**mfiltro_v)
        detalles = VentaDetalle.objects.filter(**mfiltro_d)
        cajas = Caja.objects.filter(**mfiltro_c)

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
                F('cantidad') * F('costo_unitario'),
                output_field=DecimalField(),
            ),
            ganancia_fila=ExpressionWrapper(
                F('subtotal') - (F('cantidad') * F('costo_unitario')),
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
        ticket_promedio = float(total_vendido / cantidad_ventas) if cantidad_ventas > 0 else 0.0

        top_productos = list(detalles.values('producto__nombre', 'producto_id').annotate(
            total_qty=Sum('cantidad'),
            total_revenue=Sum('subtotal'),
        ).order_by('-total_revenue')[:10])

        ids_vendidos = detalles.values_list('producto_id', flat=True).distinct()
        baja_rotacion_qs = Producto.objects.filter(stock__gt=0, **mfiltro_p).exclude(id__in=ids_vendidos).order_by('stock')[:10]
        baja_rotacion = list(baja_rotacion_qs.values('id', 'nombre', 'stock', 'precio'))

        metodos = list(ventas.values('metodo_pago').annotate(
            num_conteo=Count('id'),
            monto=Sum('total')
        ).order_by('-monto'))

        cat_stats = list(detalles.values('producto__categoria__nombre').annotate(
            monto=Sum('subtotal'),
            cantidad=Sum('cantidad')
        ).order_by('-monto'))

        cajeros_stats = list(ventas.values('usuario__username', 'usuario__first_name', 'usuario__last_name').annotate(
            total_monto=Sum('total'),
            num_ventas=Count('id')
        ).order_by('-total_monto'))

        ventas_time = {}
        if filtro in ('hoy', 'ayer'):
            for h in range(7, 23):
                ventas_time[f"{h:02d}:00"] = 0.0
        elif filtro == 'semana':
            lunes = hoy - timedelta(days=hoy.weekday())
            dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
            for i in range(7):
                d = lunes + timedelta(days=i)
                key = f"{dias_semana[i]} {d.strftime('%d/%m')}"
                ventas_time[key] = 0.0
        elif filtro in ('mes', 'mes_anterior'):
            d_start = fecha_inicio.date()
            d_end = fecha_fin.date()
            curr = d_start
            while curr <= d_end:
                ventas_time[curr.strftime('%d/%m')] = 0.0
                curr += timedelta(days=1)
        elif filtro == 'personalizado':
            d_start = fecha_inicio.date()
            d_end = fecha_fin.date()
            curr = d_start
            while curr <= d_end and (curr - d_start).days <= 60:
                ventas_time[curr.strftime('%d/%m')] = 0.0
                curr += timedelta(days=1)

        for v in ventas.order_by('fecha_hora'):
            v_local = timezone.localtime(v.fecha_hora)
            if filtro in ('hoy', 'ayer'):
                key = v_local.strftime('%H:00')
            elif filtro == 'semana':
                dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
                key = f"{dias_semana[v_local.weekday()]} {v_local.strftime('%d/%m')}"
            else:
                key = v_local.strftime('%d/%m')

            if key in ventas_time:
                ventas_time[key] += float(v.total)
            else:
                ventas_time[key] = float(v.total)


        result = {
            'total_vendido': float(total_vendido),
            'utilidad_total': float(utilidad_total),
            'margen_porcentaje': round(margen_porcentaje, 2),
            'cantidad_ventas': cantidad_ventas,
            'ticket_promedio': round(ticket_promedio, 2),
            'costo_total': float(costo_total),
            'top_productos': top_productos,
            'baja_rotacion': baja_rotacion,
            'fechas_chart': list(ventas_time.keys()),
            'totales_chart': list(ventas_time.values()),
            'metodos_pago_chart': [m['metodo_pago'] or 'Efectivo' for m in metodos],
            'totales_metodos_chart': [float(m['monto'] or 0) for m in metodos],
            'categorias_chart': [c['producto__categoria__nombre'] or 'Sin Categoría' for c in cat_stats],
            'totales_categorias_chart': [float(c['monto'] or 0) for c in cat_stats],
            'cajeros_stats': [
                {
                    'nombre': f"{c['usuario__first_name'] or ''} {c['usuario__last_name'] or ''}".strip() or c['usuario__username'],
                    'monto': float(c['total_monto'] or 0),
                    'ventas': c['num_ventas']
                } for c in cajeros_stats
            ]
        }

        cache.set(cache_key, result, 600)
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

        mfiltro = {'fecha_hora__range': (fecha_inicio, fecha_fin)}
        if mercado_admin:
            mfiltro['mercado'] = mercado_admin

        ventas = Venta.objects.filter(**mfiltro).order_by('-fecha_hora')

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

        mfiltro = {'fecha_hora__range': (fecha_inicio, fecha_fin)}
        if mercado_admin:
            mfiltro['mercado'] = mercado_admin

        ventas = Venta.objects.filter(**mfiltro).order_by('-fecha_hora')

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

