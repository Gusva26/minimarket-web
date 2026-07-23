from rest_framework import serializers


class ReporteVentasSerializer(serializers.Serializer):
    filtro = serializers.ChoiceField(
        choices=['hoy', 'ayer', 'semana', 'mes', 'mes_anterior', 'personalizado'],
        required=False,
        default='hoy',
    )

    fecha_exacta = serializers.DateField(required=False, allow_null=True)
    fecha_inicio = serializers.DateTimeField(required=False, allow_null=True)
    fecha_fin = serializers.DateTimeField(required=False, allow_null=True)
    usuario_id = serializers.IntegerField(required=False, allow_null=True)
    categoria_id = serializers.IntegerField(required=False, allow_null=True)
    metodo_pago = serializers.CharField(required=False, allow_null=True)
