from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter

from .models import Proveedor
from .serializers import ProveedorSerializer
from usuarios.api import IsAdminOrSuperUser


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperUser]
    ordering = ['nombre']
    filter_backends = [SearchFilter]
    search_fields = ['nombre', 'ruc']
