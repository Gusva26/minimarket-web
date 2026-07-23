from rest_framework import serializers
from .models import Caja, Cliente, Venta, VentaDetalle
from inventario.serializers import ProductoSimpleSerializer, MercadoSimpleSerializer, UsuarioSimpleSerializer


class UnidadVentaSimpleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    fecha_vencimiento = serializers.DateField()
    cantidad = serializers.DecimalField(max_digits=10, decimal_places=2)


class ClienteSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'tipo_documento', 'num_documento', 'direccion']


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'tipo_documento', 'num_documento', 'direccion', 'telefono', 'email']


class CajaSerializer(serializers.ModelSerializer):
    usuario = UsuarioSimpleSerializer(read_only=True)
    mercado = MercadoSimpleSerializer(read_only=True)
    montos_esperados = serializers.SerializerMethodField()
    montos_reales = serializers.SerializerMethodField()

    class Meta:
        model = Caja
        fields = ['id', 'usuario', 'mercado', 'fecha_apertura', 'fecha_cierre', 'monto_inicial', 'montos_esperados', 'montos_reales', 'estado', 'observaciones']

    def get_montos_esperados(self, obj):
        m_efectivo = obj.monto_esperado_efectivo or 0
        m_yape = obj.monto_esperado_yape or 0
        m_plin = obj.monto_esperado_plin or 0
        return {
            'total_efectivo': str(m_efectivo),
            'total_yape': str(m_yape),
            'total_plin': str(m_plin),
            'total_general': str(m_efectivo + m_yape + m_plin),
        }

    def get_montos_reales(self, obj):
        return {
            'efectivo_real': str(obj.monto_final_efectivo_real or 0),
            'yape_real': str(obj.monto_final_yape_real or 0),
            'plin_real': str(obj.monto_final_plin_real or 0),
        }


class CajaAperturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Caja
        fields = ['monto_inicial', 'observaciones']


class CajaCierreSerializer(serializers.ModelSerializer):
    efectivo_real = serializers.DecimalField(max_digits=10, decimal_places=2, source='monto_final_efectivo_real')
    yape_real = serializers.DecimalField(max_digits=10, decimal_places=2, source='monto_final_yape_real')
    plin_real = serializers.DecimalField(max_digits=10, decimal_places=2, source='monto_final_plin_real')

    class Meta:
        model = Caja
        fields = ['efectivo_real', 'yape_real', 'plin_real', 'observaciones']


class VentaDetalleSerializer(serializers.ModelSerializer):
    producto = ProductoSimpleSerializer(read_only=True, allow_null=True)
    unidades = UnidadVentaSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = VentaDetalle
        fields = ['id', 'venta', 'producto', 'cantidad', 'precio_unitario', 'costo_unitario', 'subtotal', 'descuento', 'unidades']


class VentaSerializer(serializers.ModelSerializer):
    detalles = VentaDetalleSerializer(many=True, read_only=True)
    cliente = ClienteSimpleSerializer(read_only=True, allow_null=True)
    usuario = UsuarioSimpleSerializer(read_only=True, allow_null=True)
    mercado = MercadoSimpleSerializer(read_only=True)
    utilidad = serializers.SerializerMethodField()

    class Meta:
        model = Venta
        fields = ['id', 'usuario', 'cliente', 'fecha_hora', 'tipo_comprobante', 'serie', 'numero', 'subtotal', 'igv', 'total', 'descuento', 'costo_total', 'utilidad', 'metodo_pago', 'monto_recibido', 'vuelto', 'num_operacion', 'estado', 'mercado', 'caja', 'detalles']

    def get_utilidad(self, obj):
        return obj.utilidad


class VentaListSerializer(serializers.ModelSerializer):
    cliente = ClienteSimpleSerializer(read_only=True, allow_null=True)
    usuario = UsuarioSimpleSerializer(read_only=True, allow_null=True)
    utilidad = serializers.SerializerMethodField()

    class Meta:
        model = Venta
        fields = ['id', 'usuario', 'cliente', 'fecha_hora', 'tipo_comprobante', 'serie', 'numero', 'subtotal', 'igv', 'total', 'descuento', 'costo_total', 'utilidad', 'metodo_pago', 'monto_recibido', 'vuelto', 'num_operacion', 'estado', 'mercado']

    def get_utilidad(self, obj):
        return obj.utilidad



class ItemVentaSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()
    cantidad = serializers.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = serializers.DecimalField(max_digits=10, decimal_places=2)
    descuento = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default='0.00')


class ClienteDataSerializer(serializers.Serializer):
    num_documento = serializers.CharField(required=True)
    nombre = serializers.CharField(required=False, allow_blank=True, default='')
    direccion = serializers.CharField(required=False, allow_blank=True, default='')


class VentaCreateSerializer(serializers.Serializer):
    metodo_pago = serializers.ChoiceField(choices=Venta.METODOS_PAGO)
    tipo_comprobante = serializers.ChoiceField(choices=Venta.TIPO_COMPROBANTE)
    monto_recibido = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default='0.00')
    vuelto = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default='0.00')
    num_operacion = serializers.CharField(required=False, allow_blank=True, default='')
    cliente_data = ClienteDataSerializer(required=False, allow_null=True)
    descuento = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default='0.00')
    items = ItemVentaSerializer(many=True)
