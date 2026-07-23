from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

def ping_view(request):
    return JsonResponse({'status': 'ok'})


from usuarios.api import UsuarioViewSet, CambiarPasswordView, ToggleActivoUsuarioView
from inventario.api import (
    ProductoViewSet, CategoriaViewSet, KardexListView,
    ImportarProductosView, ExportarProductosExcelView,
    ValoracionInventarioView,
    ReporteVencimientosView, TransferenciaViewSet, MercadoViewSet
)
from ventas.api import CajaViewSet, ClienteViewSet, VentaViewSet, ObtenerSiguienteNumeroView
from compras.api import CompraViewSet
from proveedores.api import ProveedorViewSet
from reportes.api import ReporteVentasView, ExportarReporteExcelView, ExportarReportePDFView
from .api_views import (
    DashboardView, AuthUserView, CambiarMercadoView, PasswordResetView, PasswordResetValidateView, PasswordResetConfirmView,
    CookieTokenObtainPairView, CookieTokenRefreshView, CookieLogoutView
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')
router.register(r'productos', ProductoViewSet, basename='productos')
router.register(r'categorias', CategoriaViewSet, basename='categorias')
router.register(r'transferencias', TransferenciaViewSet, basename='transferencias')
router.register(r'mercados', MercadoViewSet, basename='mercados')
router.register(r'cajas', CajaViewSet, basename='cajas')
router.register(r'clientes', ClienteViewSet, basename='clientes')
router.register(r'ventas', VentaViewSet, basename='ventas')
router.register(r'compras', CompraViewSet, basename='compras')
router.register(r'proveedores', ProveedorViewSet, basename='proveedores')

urlpatterns = [
    # Auth
    path('ping/', ping_view, name='ping'),
    path('auth/login/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', CookieLogoutView.as_view(), name='token_logout'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/me/', AuthUserView.as_view(), name='auth_user'),
    path('auth/cambiar-mercado/', CambiarMercadoView.as_view(), name='cambiar_mercado'),
    path('auth/password-reset/', PasswordResetView.as_view(), name='password_reset'),

    path('auth/password-reset/validate/', PasswordResetValidateView.as_view(), name='password_reset_validate'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='api_dashboard'),

    # Usuarios extras
    path('usuarios/<int:pk>/cambiar-password/', CambiarPasswordView.as_view(), name='cambiar_password'),
    path('usuarios/<int:pk>/toggle-activo/', ToggleActivoUsuarioView.as_view(), name='toggle_activo'),

    # Inventario extras
    path('productos/importar/', ImportarProductosView.as_view(), name='importar_productos'),
    path('productos/exportar/', ExportarProductosExcelView.as_view(), name='exportar_productos'),
    path('kardex/', KardexListView.as_view(), name='kardex_list'),
    path('inventario/valoracion/', ValoracionInventarioView.as_view(), name='valoracion_inventario'),
    path('inventario/vencimientos/', ReporteVencimientosView.as_view(), name='reporte_vencimientos'),

    # Ventas extras
    path('ventas/obtener-numero/', ObtenerSiguienteNumeroView.as_view(), name='obtener_numero'),

    # Reportes
    path('reportes/ventas/', ReporteVentasView.as_view(), name='reporte_ventas'),
    path('reportes/ventas/excel/', ExportarReporteExcelView.as_view(), name='reporte_ventas_excel'),
    path('reportes/ventas/pdf/', ExportarReportePDFView.as_view(), name='reporte_ventas_pdf'),

    # Router
    path('', include(router.urls)),
]
