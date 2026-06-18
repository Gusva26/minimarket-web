from datetime import datetime, timedelta
from django.utils import timezone


def calcular_rango_fechas(filtro='hoy', fecha_exacta=None,
                          fecha_inicio=None, fecha_fin=None):
    """
    Calcula el rango de fechas según el filtro seleccionado.
    Retorna (fecha_inicio, fecha_fin) como datetime timezone-aware.
    """
    hoy = timezone.localtime(timezone.now()).date()

    if filtro == 'hoy':
        start = timezone.make_aware(datetime.combine(hoy, datetime.min.time()))
        end = timezone.make_aware(datetime.combine(hoy, datetime.max.time()))
    elif filtro == 'semana':
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        start = timezone.make_aware(datetime.combine(inicio_semana, datetime.min.time()))
        end = timezone.make_aware(datetime.combine(hoy, datetime.max.time()))
    elif filtro == 'mes':
        inicio_mes = hoy.replace(day=1)
        start = timezone.make_aware(datetime.combine(inicio_mes, datetime.min.time()))
        end = timezone.make_aware(datetime.combine(hoy, datetime.max.time()))
    elif filtro == 'personalizado' and fecha_inicio and fecha_fin:
        d_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        d_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
        start = timezone.make_aware(datetime.combine(d_inicio, datetime.min.time()))
        end = timezone.make_aware(datetime.combine(d_fin, datetime.max.time()))
    elif fecha_exacta:
        d = datetime.strptime(fecha_exacta, '%Y-%m-%d')
        start = timezone.make_aware(datetime.combine(d, datetime.min.time()))
        end = timezone.make_aware(datetime.combine(d, datetime.max.time()))
    else:
        start = timezone.make_aware(datetime.combine(hoy, datetime.min.time()))
        end = timezone.make_aware(datetime.combine(hoy, datetime.max.time()))

    return start, end
