from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Usuario
from .serializers import (
    UsuarioSerializer,
    UsuarioCreateSerializer,
    UsuarioUpdateSerializer,
    CambioPasswordSerializer,
)


class IsAdminOrSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and
                    (request.user.is_admin or request.user.is_superuser))


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permite acceso de lectura (GET, HEAD, OPTIONS) a cualquier usuario autenticado,
    pero restringe las modificaciones (POST, PUT, PATCH, DELETE) únicamente a
    administradores o superusuarios.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user.rol == 'ADMIN' or request.user.is_superuser)


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['username']

    admin_only_actions = ['list', 'retrieve', 'create', 'update',
                          'partial_update', 'destroy']

    def get_permissions(self):
        if self.action in self.admin_only_actions:
            return [IsAdminOrSuperUser()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        if self.action == 'partial_update':
            return UsuarioUpdateSerializer
        return UsuarioSerializer

    def perform_create(self, serializer):
        usuario = serializer.save()
        usuario.set_password(serializer.validated_data['password'])
        usuario.save()

    def destroy(self, request, *args, **kwargs):
        usuario = self.get_object()
        if usuario == request.user:
            return Response(
                {'error': 'No puedes eliminar tu propio usuario.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class CambiarPasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperUser]

    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        serializer = CambioPasswordSerializer(data=request.data)
        if serializer.is_valid():
            usuario.set_password(serializer.validated_data['new_password1'])
            usuario.save()
            return Response({'mensaje': 'Contraseña actualizada exitosamente.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ToggleActivoUsuarioView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperUser]

    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        if usuario == request.user:
            return Response(
                {'error': 'No puedes desactivar tu propio usuario.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        usuario.is_active = not usuario.is_active
        usuario.save()
        estado = 'activado' if usuario.is_active else 'desactivado'
        return Response({
            'mensaje': f'Usuario {estado} exitosamente.',
            'is_active': usuario.is_active,
        })
