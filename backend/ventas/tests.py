import json
from unittest.mock import patch, MagicMock
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from inventario.models import Mercado, Categoria, Producto, UnidadProducto
from ventas.models import Caja, Cliente, Venta, VentaDetalle
from usuarios.models import Usuario


class VentasAPITestCase(APITestCase):
    def setUp(self):
        self.mercado = Mercado.objects.create(nombre="Mercado Principal")
        
        self.vendedor = Usuario.objects.create_user(
            username="cajero", password="password123", rol="VENDEDOR", mercado=self.mercado
        )
        self.admin = Usuario.objects.create_superuser(
            username="admin", password="password123", rol="ADMIN", mercado=self.mercado
        )
        
        self.categoria = Categoria.objects.create(nombre="Abarrotes", mercado=self.mercado)
        self.producto = Producto.objects.create(
            nombre="Aceite Primor", categoria=self.categoria, precio=10.00, stock=10.00, mercado=self.mercado
        )
        self.lote = UnidadProducto.objects.create(
            producto=self.producto,
            mercado=self.mercado,
            fecha_vencimiento=timezone.now().date() + timedelta(days=60),
            cantidad=10,
            estado='disponible'
        )

    def test_venta_falla_sin_caja_abierta(self):
        self.client.force_authenticate(user=self.vendedor)
        url = reverse('ventas-list')
        
        data = {
            'tipo_comprobante': 'TICKET',
            'metodo_pago': 'Efectivo',
            'monto_recibido': 20.00,
            'items': [
                {
                    'producto_id': self.producto.id,
                    'cantidad': 1.00,
                    'precio_unitario': 10.00
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'No hay una caja abierta para procesar la venta')

    def test_flujo_venta_y_anulacion_exitoso(self):
        self.client.force_authenticate(user=self.vendedor)
        
        # Ajustar lote y stock para que se consuma al 100% y se pueda probar la restauración de lote vinculado
        self.producto.stock = 2.00
        self.producto.save()
        self.lote.cantidad = 2.00
        self.lote.save()

        # 1. Abrir caja
        url_apertura = reverse('cajas-apertura')
        self.client.post(url_apertura, {'monto_inicial': 50.00, 'observaciones': 'Inicio de turno'})
        
        caja = Caja.objects.get(usuario=self.vendedor, estado='ABIERTA')
        self.assertEqual(caja.monto_inicial, Decimal('50.00'))
        
        # 2. Registrar la venta
        url_venta = reverse('ventas-list')
        data_venta = {
            'tipo_comprobante': 'TICKET',
            'metodo_pago': 'Efectivo',
            'monto_recibido': 20.00,
            'items': [
                {
                    'producto_id': self.producto.id,
                    'cantidad': 2.00,
                    'precio_unitario': 10.00
                }
            ]
        }
        
        response = self.client.post(url_venta, data_venta, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        venta_id = response.data['id']
        
        # Verificar stock disminuido
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 0.00)
        
        # Verificar caja monto esperado incrementado (50 inicial + 20 venta = 70 esperado)
        caja.refresh_from_db()
        self.assertEqual(caja.monto_esperado_efectivo, Decimal('70.00'))

        # 3. Anular la venta
        url_anular = reverse('ventas-anular', kwargs={'pk': venta_id})
        response_anular = self.client.post(url_anular)
        self.assertEqual(response_anular.status_code, status.HTTP_200_OK)
        
        # Verificar que el stock regresó al producto
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 2.00)
        
        # Verificar que el lote volvió a estar disponible
        self.lote.refresh_from_db()
        self.assertEqual(self.lote.cantidad, 2.00)
        self.assertEqual(self.lote.estado, 'disponible')
        
        # Verificar que la caja restó el monto esperado de la venta anulada
        caja.refresh_from_db()
        self.assertEqual(caja.monto_esperado_efectivo, Decimal('50.00'))

    def test_arqueo_y_cierre_caja(self):
        self.client.force_authenticate(user=self.vendedor)
        
        # Abrir caja
        url_apertura = reverse('cajas-apertura')
        self.client.post(url_apertura, {'monto_inicial': 100.00})
        caja = Caja.objects.get(usuario=self.vendedor, estado='ABIERTA')
        
        # Registrar venta en Yape
        url_venta = reverse('ventas-list')
        data_venta = {
            'tipo_comprobante': 'TICKET',
            'metodo_pago': 'Yape',
            'monto_recibido': 30.00,
            'items': [
                {
                    'producto_id': self.producto.id,
                    'cantidad': 3.00,
                    'precio_unitario': 10.00
                }
            ]
        }
        self.client.post(url_venta, data_venta, format='json')
        
        # Cerrar caja ingresando montos reales
        url_cierre = reverse('cajas-cierre', kwargs={'pk': caja.id})
        data_cierre = {
            'efectivo_real': 100.00, # Esperado: 100
            'yape_real': 25.00,     # Esperado: 30 (Falta 5)
            'plin_real': 0.00,      # Esperado: 0
            'observaciones': 'Faltante de 5 soles en Yape'
        }
        
        response = self.client.post(url_cierre, data_cierre, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        caja.refresh_from_db()
        self.assertEqual(caja.estado, 'CERRADA')
        self.assertEqual(caja.monto_final_yape_real, Decimal('25.00'))
        self.assertEqual(caja.monto_esperado_yape, Decimal('30.00'))

    def test_vendedor_solo_puede_ver_sus_cajas(self):
        vendedor2 = Usuario.objects.create_user(
            username="cajero2", password="password123", rol="VENDEDOR", mercado=self.mercado
        )
        caja1 = Caja.objects.create(
            usuario=self.vendedor,
            mercado=self.mercado,
            monto_inicial=10.00,
            estado='ABIERTA'
        )
        caja2 = Caja.objects.create(
            usuario=vendedor2,
            mercado=self.mercado,
            monto_inicial=20.00,
            estado='ABIERTA'
        )

        # 1. Autenticar como vendedor principal
        self.client.force_authenticate(user=self.vendedor)
        url = reverse('cajas-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], caja1.id)

        # 2. Autenticar como administrador
        self.client.force_authenticate(user=self.admin)
        response_admin = self.client.get(url)
        self.assertEqual(response_admin.status_code, status.HTTP_200_OK)
        results_admin = response_admin.data.get('results', response_admin.data)
        self.assertEqual(len(results_admin), 2)



class ClienteAPISPeruMockTestCase(APITestCase):
    def setUp(self):
        self.mercado = Mercado.objects.create(nombre="Test Mercado")
        self.vendedor = Usuario.objects.create_user(
            username="cajero", password="password123", rol="VENDEDOR", mercado=self.mercado
        )

    def test_consulta_documento_local_existente(self):
        self.client.force_authenticate(user=self.vendedor)
        Cliente.objects.create(
            nombre="Juan Pérez",
            tipo_documento="DNI",
            num_documento="00000001",
            direccion="Av. Siempre Viva 123"
        )
        
        url = reverse('clientes-consultar-documento') + "?documento=00000001"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Juan Pérez')
        self.assertEqual(response.data['origen'], 'local')

    @patch('urllib.request.urlopen')
    def test_consulta_documento_api_externa_mock(self, mock_urlopen):
        self.client.force_authenticate(user=self.vendedor)
        
        # Configurar mock de urllib response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'success': True,
            'nombres': 'María',
            'apellidoPaterno': 'Gómez',
            'apellidoMaterno': 'Sánchez'
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        url = reverse('clientes-consultar-documento') + "?documento=00000002"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'María Gómez Sánchez')
        self.assertEqual(response.data['origen'], 'api')
