from decimal import Decimal
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
    permission_classes = [permissions.IsAuthenticated]


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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        ahora = timezone.localtime(timezone.now())
        hoy = ahora.date()

        mercado_admin = request.user.mercado
        filtro = request.query_params.get('filtro', 'hoy')

        fecha_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = ahora.replace(hour=23, minute=59, second=59, microsecond=999999)

        if filtro == 'ayer':
            ayer = hoy - timedelta(days=1)
            fecha_inicio = timezone.make_aware(datetime.combine(ayer, datetime.min.time()))
            fecha_fin = timezone.make_aware(datetime.combine(ayer, datetime.max.time()))
        elif filtro == 'semana':
            lunes = hoy - timedelta(days=hoy.weekday())
            fecha_inicio = timezone.make_aware(datetime.combine(lunes, datetime.min.time()))
        elif filtro == 'mes':
            primero = hoy.replace(day=1)
            fecha_inicio = timezone.make_aware(datetime.combine(primero, datetime.min.time()))
        elif filtro == 'mes_anterior':
            primer_dia_este_mes = hoy.replace(day=1)
            ultimo_dia_mes_pasado = primer_dia_este_mes - timedelta(days=1)
            primer_dia_mes_pasado = ultimo_dia_mes_pasado.replace(day=1)
            fecha_inicio = timezone.make_aware(datetime.combine(primer_dia_mes_pasado, datetime.min.time()))
            fecha_fin = timezone.make_aware(datetime.combine(ultimo_dia_mes_pasado, datetime.max.time()))

        fi_param = request.query_params.get('fecha_inicio')
        ff_param = request.query_params.get('fecha_fin')
        if fi_param:
            try:
                dt = datetime.strptime(fi_param, '%Y-%m-%d')
                fecha_inicio = timezone.make_aware(datetime.combine(dt.date(), datetime.min.time()))
            except Exception: pass
        if ff_param:
            try:
                dt = datetime.strptime(ff_param, '%Y-%m-%d')
                fecha_fin = timezone.make_aware(datetime.combine(dt.date(), datetime.max.time()))
            except Exception: pass

        mfiltro = {'fecha_hora__range': (fecha_inicio, fecha_fin)}
        if mercado_admin:
            mfiltro['mercado'] = mercado_admin

        metodo_pago = request.query_params.get('metodo_pago')
        if metodo_pago:
            mfiltro['metodo_pago'] = metodo_pago

        ventas = Venta.objects.filter(**mfiltro).select_related('cliente', 'usuario', 'mercado').order_by('-fecha_hora')

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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        ahora = timezone.localtime(timezone.now())
        hoy = ahora.date()

        mercado_admin = request.user.mercado
        filtro = request.query_params.get('filtro', 'hoy')

        fecha_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = ahora.replace(hour=23, minute=59, second=59, microsecond=999999)

        if filtro == 'ayer':
            ayer = hoy - timedelta(days=1)
            fecha_inicio = timezone.make_aware(datetime.combine(ayer, datetime.min.time()))
            fecha_fin = timezone.make_aware(datetime.combine(ayer, datetime.max.time()))
        elif filtro == 'semana':
            lunes = hoy - timedelta(days=hoy.weekday())
            fecha_inicio = timezone.make_aware(datetime.combine(lunes, datetime.min.time()))
        elif filtro == 'mes':
            primero = hoy.replace(day=1)
            fecha_inicio = timezone.make_aware(datetime.combine(primero, datetime.min.time()))
        elif filtro == 'mes_anterior':
            primer_dia_este_mes = hoy.replace(day=1)
            ultimo_dia_mes_pasado = primer_dia_este_mes - timedelta(days=1)
            primer_dia_mes_pasado = ultimo_dia_mes_pasado.replace(day=1)
            fecha_inicio = timezone.make_aware(datetime.combine(primer_dia_mes_pasado, datetime.min.time()))
            fecha_fin = timezone.make_aware(datetime.combine(ultimo_dia_mes_pasado, datetime.max.time()))

        fi_param = request.query_params.get('fecha_inicio')
        ff_param = request.query_params.get('fecha_fin')
        if fi_param:
            try:
                dt = datetime.strptime(fi_param, '%Y-%m-%d')
                fecha_inicio = timezone.make_aware(datetime.combine(dt.date(), datetime.min.time()))
            except Exception: pass
        if ff_param:
            try:
                dt = datetime.strptime(ff_param, '%Y-%m-%d')
                fecha_fin = timezone.make_aware(datetime.combine(dt.date(), datetime.max.time()))
            except Exception: pass

        mfiltro = {'fecha_hora__range': (fecha_inicio, fecha_fin)}
        if mercado_admin:
            mfiltro['mercado'] = mercado_admin

        metodo_pago = request.query_params.get('metodo_pago')
        if metodo_pago:
            mfiltro['metodo_pago'] = metodo_pago

        # Optimizado: select_related para evitar N+1 queries y max 1000 registros para evitar timeouts
        ventas_qs = Venta.objects.filter(**mfiltro).select_related('cliente', 'usuario', 'mercado').order_by('-fecha_hora')
        
        # Calcular agregaciones KPI para la cabecera del PDF
        total_completadas = ventas_qs.filter(estado='COMPLETADA').aggregate(t=Sum('total'))['t'] or Decimal('0.00')
        cant_completadas = ventas_qs.filter(estado='COMPLETADA').count()
        total_anuladas = ventas_qs.filter(estado='ANULADA').aggregate(t=Sum('total'))['t'] or Decimal('0.00')
        cant_anuladas = ventas_qs.filter(estado='ANULADA').count()
        ticket_promedio = float(total_completadas / cant_completadas) if cant_completadas > 0 else 0.0

        ventas_list = list(ventas_qs[:1000])

        rows = []
        for idx, v in enumerate(ventas_list):
            cli_nombre = v.cliente.nombre if v.cliente else 'Público General'
            usr_name = v.usuario.username if v.usuario else 'Sistema'
            comprobante = f"{v.serie}-{v.numero:06d}"
            fecha_str = v.fecha_hora.strftime('%d/%m/%Y %H:%M')
            bg_style = 'background-color: #f8fafc;' if idx % 2 == 1 else 'background-color: #ffffff;'
            
            estado_html = '<span style="color:#166534;background-color:#dcfce7;padding:2px 6px;border-radius:4px;font-size:9px;font-weight:bold;">COMPLETADA</span>' if v.estado == 'COMPLETADA' else '<span style="color:#991b1b;background-color:#fee2e2;padding:2px 6px;border-radius:4px;font-size:9px;font-weight:bold;">ANULADA</span>'

            rows.append(f"""
                <tr style="{bg_style}">
                    <td style="font-weight:bold;color:#4f46e5;">{comprobante}</td>
                    <td style="color:#475569;">{fecha_str}</td>
                    <td>{cli_nombre}</td>
                    <td style="color:#475569;">{usr_name}</td>
                    <td>{v.metodo_pago}</td>
                    <td style="text-align:center;">{estado_html}</td>
                    <td style="text-align:right;font-weight:bold;">S/ {float(v.total):.2f}</td>
                </tr>
            """)

        html_table_body = "".join(rows)
        sucursal_nombre = mercado_admin.nombre if mercado_admin else 'Todas las Sucursales'

        html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{
                    size: A4 portrait;
                    margin: 1.2cm;
                }}
                body {{
                    font-family: 'Helvetica', 'Arial', sans-serif;
                    font-size: 10px;
                    color: #1e293b;
                    line-height: 1.4;
                }}
                .header-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 15px;
                    border-bottom: 2px solid #6366f1;
                    padding-bottom: 10px;
                }}
                .header-title {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #0f172a;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .header-sub {{
                    font-size: 11px;
                    color: #6366f1;
                    font-weight: bold;
                }}
                .meta-table {{
                    width: 100%;
                    margin-bottom: 15px;
                    background-color: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    padding: 8px 12px;
                }}
                .meta-label {{
                    font-weight: bold;
                    color: #64748b;
                }}
                .kpi-table {{
                    width: 100%;
                    border-collapse: separate;
                    border-spacing: 8px;
                    margin-bottom: 15px;
                }}
                .kpi-box {{
                    background-color: #f1f5f9;
                    border: 1px solid #cbd5e1;
                    border-radius: 6px;
                    padding: 8px;
                    text-align: center;
                }}
                .kpi-title {{
                    font-size: 9px;
                    color: #475569;
                    text-transform: uppercase;
                    font-weight: bold;
                }}
                .kpi-val {{
                    font-size: 13px;
                    font-weight: bold;
                    color: #0f172a;
                    margin-top: 3px;
                }}
                .data-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }}
                .data-table th {{
                    background-color: #1e293b;
                    color: #ffffff;
                    font-weight: bold;
                    text-align: left;
                    padding: 7px 8px;
                    font-size: 9px;
                    text-transform: uppercase;
                }}
                .data-table td {{
                    border-bottom: 1px solid #e2e8f0;
                    padding: 6px 8px;
                    font-size: 9.5px;
                }}
                .footer-summary {{
                    margin-top: 15px;
                    float: right;
                    width: 250px;
                    background-color: #f8fafc;
                    border: 1px solid #cbd5e1;
                    border-radius: 6px;
                    padding: 8px 12px;
                }}
            </style>
        </head>
        <body>
            <!-- Banner Cabecera -->
            <table class="header-table">
                <tr>
                    <td style="vertical-align:middle;">
                        <div class="header-title">Reporte Ejecutivo de Ventas</div>
                        <div class="header-sub">{sucursal_nombre}</div>
                    </td>
                    <td style="text-align:right;vertical-align:middle;color:#64748b;font-size:9px;">
                        Emisión: {ahora.strftime('%d/%m/%Y %H:%M')}<br>
                        Generado por: {request.user.username}
                    </td>
                </tr>
            </table>

            <!-- Meta Filtros -->
            <table class="meta-table">
                <tr>
                    <td style="width:50%;"><span class="meta-label">Rango de Fechas:</span> {fecha_inicio.strftime('%d/%m/%Y %H:%M')} — {fecha_fin.strftime('%d/%m/%Y %H:%M')}</td>
                    <td style="width:50%;text-align:right;"><span class="meta-label">Filtro Aplicado:</span> {filtro.upper()} {f'| {metodo_pago}' if metodo_pago else ''}</td>
                </tr>
            </table>

            <!-- Resumen KPI -->
            <table class="kpi-table">
                <tr>
                    <td class="kpi-box" style="width:25%;border-left: 3px solid #10b981;">
                        <div class="kpi-title">Ventas Totales</div>
                        <div class="kpi-val" style="color:#059669;">S/ {float(total_completadas):,.2f}</div>
                    </td>
                    <td class="kpi-box" style="width:25%;border-left: 3px solid #6366f1;">
                        <div class="kpi-title">Transacciones</div>
                        <div class="kpi-val">{cant_completadas} completadas</div>
                    </td>
                    <td class="kpi-box" style="width:25%;border-left: 3px solid #06b6d4;">
                        <div class="kpi-title">Ticket Promedio</div>
                        <div class="kpi-val">S/ {ticket_promedio:,.2f}</div>
                    </td>
                    <td class="kpi-box" style="width:25%;border-left: 3px solid #ef4444;">
                        <div class="kpi-title">Anulaciones</div>
                        <div class="kpi-val" style="color:#dc2626;">{cant_anuladas} ({f'S/ {float(total_anuladas):,.2f}'})</div>
                    </td>
                </tr>
            </table>

            <!-- Tabla de Datos -->
            <table class="data-table">
                <thead>
                    <tr>
                        <th style="width:15%;">Comprobante</th>
                        <th style="width:18%;">Fecha / Hora</th>
                        <th>Cliente</th>
                        <th style="width:14%;">Vendedor</th>
                        <th style="width:12%;">Método</th>
                        <th style="width:13%;text-align:center;">Estado</th>
                        <th style="width:14%;text-align:right;">Monto Total</th>
                    </tr>
                </thead>
                <tbody>
                    {html_table_body}
                </tbody>
            </table>

            <!-- Resumen Pie -->
            <div class="footer-summary">
                <table style="width:100%;">
                    <tr>
                        <td style="color:#64748b;font-weight:bold;">Total Neto Cobrado:</td>
                        <td style="text-align:right;font-size:12px;font-weight:bold;color:#059669;">S/ {float(total_completadas):,.2f}</td>
                    </tr>
                </table>
            </div>
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




