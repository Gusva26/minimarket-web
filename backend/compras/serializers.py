from rest_framework import serializers
from .models import Compra, DetalleCompra
from inventario.serializers import ProductoSimpleSerializer, UsuarioSimpleSerializer
from proveedores.serializers import ProveedorSerializer


class DetalleCompraSerializer(serializers.ModelSerializer):
    producto = ProductoSimpleSerializer(read_only=True)

    class Meta:
        model = DetalleCompra
        fields = ['id', 'compra', 'producto', 'cantidad', 'precio_costo_unitario', 'fecha_vencimiento', 'subtotal']


class CompraSerializer(serializers.ModelSerializer):
    detalles = DetalleCompraSerializer(many=True, read_only=True)
    usuario = UsuarioSimpleSerializer(read_only=True, allow_null=True)
    proveedor = ProveedorSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Compra
        fields = ['id', 'fecha', 'usuario', 'proveedor', 'total', 'detalles']


class DetalleCompraCreateSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()
    cantidad = serializers.DecimalField(max_digits=10, decimal_places=2)
    precio_costo_unitario = serializers.DecimalField(max_digits=10, decimal_places=2)
    fecha_vencimiento = serializers.DateField(required=False, allow_null=True)


class CompraCreateSerializer(serializers.Serializer):
    proveedor_id = serializers.IntegerField(required=False, allow_null=True)
    fecha = serializers.DateTimeField(required=False)
    detalles = DetalleCompraCreateSerializer(many=True)

    def validate_detalles(self, value):
        if not value:
            raise serializers.ValidationError('Debe incluir al menos un detalle de compra.')
        return value
