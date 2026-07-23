from rest_framework import serializers
from .models import Proveedor


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['id', 'nombre', 'ruc', 'telefono', 'direccion', 'email', 'persona_contacto', 'estado_sunat', 'notas', 'activo']

