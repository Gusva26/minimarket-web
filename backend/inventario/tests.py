import io
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

from inventario.models import Mercado, Categoria, Producto, UnidadProducto, Kardex, Transferencia, TransferenciaDetalle
from inventario.utils import descontar_stock_fefo, devolver_stock_a_unidades
from usuarios.models import Usuario


class InventarioModelsTestCase(APITestCase):
    def setUp(self):
        self.mercado = Mercado.objects.create(nombre="Mercado Origen")
        self.categoria = Categoria.objects.create(nombre="Bebidas", mercado=self.mercado)

    def test_unidad_producto_vencimiento_helpers(self):
        hoy = timezone.now().date()
        producto = Producto.objects.create(
            nombre="Gaseosa",
            categoria=self.categoria,
            precio=2.50,
            stock=10.00,
            mercado=self.mercado
        )
        
        lote_vencido = UnidadProducto.objects.create(
            producto=producto,
            mercado=self.mercado,
            fecha_vencimiento=hoy - timedelta(days=2),
            cantidad=5,
            estado='disponible'
        )
        lote_vigente = UnidadProducto.objects.create(
            producto=producto,
            mercado=self.mercado,
            fecha_vencimiento=hoy + timedelta(days=5),
            cantidad=5,
            estado='disponible'
        )

        self.assertTrue(lote_vencido.esta_vencido())
        self.assertFalse(lote_vigente.esta_vencido())
        self.assertEqual(lote_vencido.dias_para_vencer(), -2)
        self.assertEqual(lote_vigente.dias_para_vencer(), 5)

    def test_image_resizing_on_save(self):
        # Generar imagen de 600x600 px en memoria
        file = io.BytesIO()
        image = Image.new('RGB', (600, 600), 'blue')
        image.save(file, 'PNG')
        file.seek(0)
        uploaded_image = SimpleUploadedFile('test.png', file.read(), content_type='image/png')

        producto = Producto.objects.create(
            nombre="Jugo de Fresa",
            categoria=self.categoria,
            precio=3.00,
            stock=1,
            imagen=uploaded_image,
            mercado=self.mercado
        )

        # La imagen debió convertirse a JPEG y redimensionarse a 500x500 px
        producto.refresh_from_db()
        self.assertTrue(producto.imagen.name.endswith('.jpg'))
        img = Image.open(producto.imagen.path)
        self.assertEqual(img.size, (500, 500))


class FEFOAlgorithmTestCase(APITestCase):
    def setUp(self):
        self.mercado = Mercado.objects.create(nombre="Mercado FEFO")
        self.categoria = Categoria.objects.create(nombre="Abarrotes", mercado=self.mercado)
        self.producto = Producto.objects.create(
            nombre="Arroz Costeño",
            categoria=self.categoria,
            precio=4.20,
            stock=15.00,
            unidad_medida="KG",
            mercado=self.mercado
        )
        
        # Lotes con distintas fechas de vencimiento
        hoy = timezone.now().date()
        self.lote_proximo = UnidadProducto.objects.create(
            producto=self.producto,
            mercado=self.mercado,
            fecha_vencimiento=hoy + timedelta(days=2),
            cantidad=5.00,
            estado='disponible'
        )
        self.lote_lejano = UnidadProducto.objects.create(
            producto=self.producto,
            mercado=self.mercado,
            fecha_vencimiento=hoy + timedelta(days=20),
            cantidad=10.00,
            estado='disponible'
        )

    def test_fefo_descuento_lotes(self):
        # Descontar 7 unidades (debe vaciar el primer lote de 5 y tomar 2 del segundo de 10)
        exito, error_msg, unidades_usadas = descontar_stock_fefo(
            self.producto, 7.00, self.mercado
        )
        self.assertTrue(exito)
        self.assertEqual(error_msg, '')
        
        self.lote_proximo.refresh_from_db()
        self.lote_lejano.refresh_from_db()
        
        # Primer lote: consumido y marcado como vendido
        self.assertEqual(self.lote_proximo.cantidad, 0)
        self.assertEqual(self.lote_proximo.estado, 'vendido')
        
        # Segundo lote: disminuido a 8 y disponible
        self.assertEqual(self.lote_lejano.cantidad, 8.00)
        self.assertEqual(self.lote_lejano.estado, 'disponible')

    def test_fefo_insuficiente(self):
        # Intentar descontar más de lo disponible (15 unidades en total)
        exito, error_msg, unidades_usadas = descontar_stock_fefo(
            self.producto, 20.00, self.mercado
        )
        self.assertFalse(exito)
        self.assertIn('Stock insuficiente', error_msg)


class TransferenciasAPITestCase(APITestCase):
    def setUp(self):
        self.mercado_orig = Mercado.objects.create(nombre="Sede Norte")
        self.mercado_dest = Mercado.objects.create(nombre="Sede Sur")
        
        self.admin = Usuario.objects.create_superuser(
            username="admin", password="password123", rol="ADMIN", mercado=self.mercado_orig
        )
        self.receiver = Usuario.objects.create_user(
            username="receptor", password="password123", rol="ADMIN", mercado=self.mercado_dest
        )
        
        self.categoria_orig = Categoria.objects.create(nombre="Lácteos", mercado=self.mercado_orig)
        self.producto_orig = Producto.objects.create(
            nombre="Leche Gloria", categoria=self.categoria_orig, precio=4.00, stock=10.00, mercado=self.mercado_orig
        )
        
        self.lote_orig = UnidadProducto.objects.create(
            producto=self.producto_orig,
            mercado=self.mercado_orig,
            fecha_vencimiento=timezone.now().date() + timedelta(days=30),
            cantidad=10,
            estado='disponible'
        )

    def test_flujo_transferencia_completo(self):
        self.client.force_authenticate(user=self.admin)
        
        # Crear transferencia
        url_crear = reverse('transferencias-list')
        data_transferencia = {
            'mercado_destino_id': self.mercado_dest.id,
            'observaciones': 'Traspaso de leche',
            'productos': [
                {
                    'producto_id': self.producto_orig.id,
                    'cantidad': 4.00
                }
            ]
        }
        
        response = self.client.post(url_crear, data_transferencia, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        trans_id = response.data['id']
        
        # Validar descuento en origen
        self.producto_orig.refresh_from_db()
        self.assertEqual(self.producto_orig.stock, 6.00) # De 10 bajó a 6
        
        # Recibir transferencia en destino (autenticado como el receptor de la sucursal de destino)
        self.client.force_authenticate(user=self.receiver)
        url_recibir = reverse('transferencias-recibir', kwargs={'pk': trans_id})
        response_recibir = self.client.post(url_recibir)
        self.assertEqual(response_recibir.status_code, status.HTTP_200_OK)
        
        # Verificar stock en destino
        # El receptor debe haber creado el producto automáticamente si no existía
        producto_dest = Producto.objects.get(nombre="Leche Gloria", mercado=self.mercado_dest)
        self.assertEqual(producto_dest.stock, 4.00)
        
        # Verificar lote creado en destino
        lote_dest = UnidadProducto.objects.get(producto=producto_dest, mercado=self.mercado_dest)
        self.assertEqual(lote_dest.cantidad, 4.00)
        self.assertEqual(lote_dest.estado, 'disponible')


class InventarioPermissionsAPITestCase(APITestCase):
    def setUp(self):
        self.mercado = Mercado.objects.create(nombre="Sede Permisos")
        self.vendedor = Usuario.objects.create_user(
            username="vendedor_cajero", password="password123", rol="VENDEDOR", mercado=self.mercado
        )
        self.admin = Usuario.objects.create_superuser(
            username="admin_gerente", password="password123", rol="ADMIN", mercado=self.mercado
        )
        self.categoria = Categoria.objects.create(nombre="Abarrotes", mercado=self.mercado)
        self.producto = Producto.objects.create(
            nombre="Aceite Primor", categoria=self.categoria, precio=10.00, stock=10.00, mercado=self.mercado
        )

    def test_vendedor_puede_ver_productos_pero_no_crear_ni_ajustar(self):
        # 1. Autenticar como vendedor (cajero)
        self.client.force_authenticate(user=self.vendedor)
        
        # 2. Debería poder listar productos (GET)
        url_list = reverse('productos-list')
        response_get = self.client.get(url_list)
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)

        # 3. Debería poder ver el detalle de un producto
        url_detail = reverse('productos-detail', kwargs={'pk': self.producto.id})
        response_detail = self.client.get(url_detail)
        self.assertEqual(response_detail.status_code, status.HTTP_200_OK)

        # 4. Debería recibir FORBIDDEN al intentar crear un producto (POST)
        response_post = self.client.post(url_list, {
            'nombre': 'Nuevo Producto de Cajero',
            'precio': 5.00,
            'stock': 100,
        }, format='json')
        self.assertEqual(response_post.status_code, status.HTTP_403_FORBIDDEN)

        # 5. Debería recibir FORBIDDEN al intentar ajustar stock (POST)
        url_ajustar = reverse('productos-ajustar', kwargs={'pk': self.producto.id})
        response_ajustar = self.client.post(url_ajustar, {
            'tipo': 'SUMAR',
            'cantidad': 10
        }, format='json')
        self.assertEqual(response_ajustar.status_code, status.HTTP_403_FORBIDDEN)

    def test_vendedor_no_puede_ver_valoracion_ni_importar(self):
        self.client.force_authenticate(user=self.vendedor)

        # 1. Debería recibir FORBIDDEN al ver valoración (GET)
        url_val = reverse('valoracion_inventario')
        response_val = self.client.get(url_val)
        self.assertEqual(response_val.status_code, status.HTTP_403_FORBIDDEN)

        # 2. Debería recibir FORBIDDEN al importar productos (POST)
        url_imp = reverse('importar_productos')
        response_imp = self.client.post(url_imp, {})
        self.assertEqual(response_imp.status_code, status.HTTP_403_FORBIDDEN)

    def test_vendedor_no_puede_ver_kardex(self):
        self.client.force_authenticate(user=self.vendedor)
        url_kardex = reverse('kardex_list')
        response = self.client.get(url_kardex)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_puede_crear_y_ver_valoracion(self):
        # 1. Autenticar como administrador
        self.client.force_authenticate(user=self.admin)

        # 2. Debería poder crear producto
        url_list = reverse('productos-list')
        response_post = self.client.post(url_list, {
            'nombre': 'Aceite Cocinero',
            'precio': 8.50,
            'costo': 6.00,
            'stock': 10,
            'unidad_medida': 'UND'
        }, format='json')
        self.assertEqual(response_post.status_code, status.HTTP_201_CREATED)

        # 3. Debería poder ver valoración
        url_val = reverse('valoracion_inventario')
        response_val = self.client.get(url_val)
        self.assertEqual(response_val.status_code, status.HTTP_200_OK)

        # 4. Debería poder ver kardex
        url_kardex = reverse('kardex_list')
        response_kardex = self.client.get(url_kardex)
        self.assertEqual(response_kardex.status_code, status.HTTP_200_OK)
