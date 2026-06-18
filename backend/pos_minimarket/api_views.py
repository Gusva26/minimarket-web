from django.utils import timezone
from django.db.models import F, Sum, Q
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib.auth.password_validation import validate_password
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.conf import settings
from django.core.cache import cache
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from inventario.models import Producto, UnidadProducto, Kardex
from inventario.utils import get_mercado_cache_version
from ventas.models import Venta, Caja
from usuarios.models import Usuario


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mercado = request.user.mercado
        version = get_mercado_cache_version(mercado.id)
        cache_key = f"dashboard_mercado_{mercado.id}_v{version}"
        
        cached_data = cache.get(cache_key)
        if cached_data:
            # We must check if caja status changed, as it's user-specific and dynamic
            caja_abierta = Caja.objects.filter(
                usuario=request.user, mercado=mercado, estado='ABIERTA'
            ).first()
            cached_data['caja_abierta_id'] = caja_abierta.id if caja_abierta else None
            return Response(cached_data)

        ahora = timezone.now().strftime('%d/%b/%Y %H:%M:%S')
        print(f'[{ahora}] "GET {request.path} HTTP/1.1" 200 (DB QUERY)')
        hoy = timezone.now().date()

        productos_bajo_stock = list(Producto.objects.filter(
            mercado=mercado, stock__lt=F('stock_minimo')
        ).values('id', 'nombre', 'categoria__nombre', 'stock', 'stock_minimo', 'unidad_medida'))

        # Aggregated expiration data
        proximos_vencer_qs = UnidadProducto.objects.filter(
            mercado=mercado, estado='disponible', cantidad__gt=0,
            fecha_vencimiento__lte=hoy + timezone.timedelta(days=30)
        ).values(
            'producto__nombre', 'fecha_vencimiento'
        ).annotate(
            total_cantidad=Sum('cantidad')
        ).order_by('fecha_vencimiento')

        proximos_vencer = []
        for u in proximos_vencer_qs:
            delta = u['fecha_vencimiento'] - hoy
            proximos_vencer.append({
                'producto__nombre': u['producto__nombre'],
                'cantidad': float(u['total_cantidad']),
                'fecha_vencimiento': u['fecha_vencimiento'],
                'dias_para_vencer': delta.days,
                'cantidad_actual': float(u['total_cantidad'])
            })

        ventas_hoy = Venta.objects.filter(
            mercado=mercado, fecha_hora__date=hoy, estado='COMPLETADA'
        ).aggregate(total=Sum('total'))['total'] or 0

        caja_abierta = Caja.objects.filter(
            usuario=request.user, mercado=mercado, estado='ABIERTA'
        ).first()

        response_data = {
            'productos_bajo_stock': productos_bajo_stock,
            'proximos_vencer': proximos_vencer,
            'ventas_hoy': float(ventas_hoy),
            'caja_abierta_id': caja_abierta.id if caja_abierta else None,
            'mercado_nombre': mercado.nombre if mercado else None,
        }
        
        # Store in cache but without caja_abierta_id as it varies by user/session state
        cache_data_to_store = response_data.copy()
        cache.set(cache_key, cache_data_to_store, 300) # 5 min
        
        return Response(response_data)


class AuthUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'rol': user.rol,
            'is_admin': user.is_admin,
            'is_vendedor': user.is_vendedor,
            'is_superuser': user.is_superuser,
            'is_active': user.is_active,
            'mercado_id': user.mercado_id,
            'mercado_nombre': user.mercado.nombre if user.mercado else None,
        })


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        if not email:
            return Response({'error': 'El correo es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Usuario.objects.get(email=email, is_active=True)
        except Usuario.DoesNotExist:
            return Response({'error': 'El correo no está registrado en el sistema.'}, status=status.HTTP_404_NOT_FOUND)

        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        link = f"{settings.FRONTEND_URL}/#/reset-password/{uid}/{token}"

        subject = 'Recuperación de contraseña — Minimarket POS'
        message = render_to_string('emails/password_reset_email.html', {
            'user': user,
            'link': link,
        })
        send_mail(subject, message, None, [email], html_message=message)

        return Response({'mensaje': 'Se ha enviado un enlace de recuperación a tu correo electrónico.'})


class PasswordResetValidateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uid = request.data.get('uid', '')
        token = request.data.get('token', '')

        if not uid or not token:
            return Response({'error': 'Faltan parámetros.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid_val = force_str(urlsafe_base64_decode(uid))
            user = Usuario.objects.get(pk=uid_val, is_active=True)
        except (ValueError, Usuario.DoesNotExist):
            return Response({'error': 'El enlace no es válido.'}, status=status.HTTP_400_BAD_REQUEST)

        if not token_generator.check_token(user, token):
            return Response({'error': 'El enlace ha expirado o ya fue utilizado.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'mensaje': 'Token válido.'})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uid = request.data.get('uid', '')
        token = request.data.get('token', '')
        new_password1 = request.data.get('new_password1', '')
        new_password2 = request.data.get('new_password2', '')

        if not uid or not token:
            return Response({'error': 'Faltan parámetros.'}, status=status.HTTP_400_BAD_REQUEST)

        if not new_password1 or not new_password2:
            return Response({'error': 'Ambas contraseñas son obligatorias.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password1 != new_password2:
            return Response({'error': 'Las contraseñas no coinciden.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(new_password1)
        except ValidationError as e:
            return Response({'error': ' '.join(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid_val = force_str(urlsafe_base64_decode(uid))
            user = Usuario.objects.get(pk=uid_val, is_active=True)
        except (ValueError, Usuario.DoesNotExist):
            return Response({'error': 'El enlace de recuperación no es válido.'}, status=status.HTTP_400_BAD_REQUEST)

        if not token_generator.check_token(user, token):
            return Response({'error': 'El enlace de recuperación ha expirado o no es válido.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password1)
        user.save()

        return Response({'mensaje': 'Contraseña actualizada exitosamente. Ya puedes iniciar sesión.'})
