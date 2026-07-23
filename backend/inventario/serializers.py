from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Mercado, Categoria, Producto, Kardex, UnidadProducto, Transferencia, TransferenciaDetalle

User = get_user_model()


class MercadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mercado
        fields = ['id', 'nombre', 'ruc', 'direccion', 'telefono', 'activo']


class CategoriaSerializer(serializers.ModelSerializer):
    cantidad_productos = serializers.IntegerField(read_only=True)

    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'mercado', 'cantidad_productos']
        extra_kwargs = {
            'mercado': {'required': False, 'allow_null': True},
        }


class CategoriaSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']


class UsuarioSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class MercadoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mercado
        fields = ['id', 'nombre', 'ruc', 'direccion']


class ProductoSimpleSerializer(serializers.ModelSerializer):
    categoria = CategoriaSimpleSerializer(read_only=True)

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'categoria']


class ProductoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSimpleSerializer(read_only=True)
    tiene_stock_bajo = serializers.BooleanField(read_only=True)

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'codigo_barras', 'categoria', 'precio', 'costo', 'stock', 'stock_minimo', 'unidad_medida', 'imagen', 'mercado', 'tiene_stock_bajo']


class ProductoCreateUpdateSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'codigo_barras', 'categoria', 'unidad_medida', 'precio', 'costo', 'stock', 'stock_minimo', 'imagen']
        extra_kwargs = {
            'categoria': {'required': False, 'allow_null': True},
        }


class KardexSerializer(serializers.ModelSerializer):
    producto = ProductoSimpleSerializer(read_only=True)
    usuario = UsuarioSimpleSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Kardex
        fields = ['id', 'producto', 'mercado', 'tipo_movimiento', 'cantidad', 'saldo_anterior', 'saldo_nuevo', 'referencia_tipo', 'referencia_id', 'referencia_detalle', 'fecha', 'usuario']


class UnidadProductoSerializer(serializers.ModelSerializer):
    producto = ProductoSimpleSerializer(read_only=True)
    dias_para_vencer = serializers.IntegerField(read_only=True)
    esta_vencido = serializers.BooleanField(read_only=True)

    class Meta:
        model = UnidadProducto
        fields = ['id', 'producto', 'mercado', 'fecha_vencimiento', 'cantidad', 'estado', 'venta_detalle', 'dias_para_vencer', 'esta_vencido']


class TransferenciaDetalleSerializer(serializers.ModelSerializer):
    producto_origen = ProductoSimpleSerializer(read_only=True)
    producto_destino = ProductoSimpleSerializer(read_only=True, allow_null=True)

    class Meta:
        model = TransferenciaDetalle
        fields = ['id', 'transferencia', 'producto_origen', 'producto_destino', 'cantidad', 'fecha_vencimiento']


class TransferenciaListSerializer(serializers.ModelSerializer):
    mercado_origen = MercadoSimpleSerializer(read_only=True)
    mercado_destino = MercadoSimpleSerializer(read_only=True)
    usuario_envio = UsuarioSimpleSerializer(read_only=True, allow_null=True)
    usuario_recepcion = UsuarioSimpleSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Transferencia
        fields = ['id', 'mercado_origen', 'mercado_destino', 'usuario_envio', 'usuario_recepcion', 'fecha_envio', 'fecha_recepcion', 'estado', 'observaciones']


class TransferenciaSerializer(serializers.ModelSerializer):
    detalles = TransferenciaDetalleSerializer(many=True, read_only=True)
    mercado_origen = MercadoSimpleSerializer(read_only=True)
    mercado_destino = MercadoSimpleSerializer(read_only=True)
    usuario_envio = UsuarioSimpleSerializer(read_only=True, allow_null=True)
    usuario_recepcion = UsuarioSimpleSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Transferencia
        fields = ['id', 'mercado_origen', 'mercado_destino', 'usuario_envio', 'usuario_recepcion', 'fecha_envio', 'fecha_recepcion', 'estado', 'observaciones', 'detalles']

