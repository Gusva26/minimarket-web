from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from usuarios.models import Usuario
from inventario.models import Mercado


class UsuarioModelTestCase(APITestCase):
    def setUp(self):
        self.mercado = Mercado.objects.create(nombre="Test Mercado")

    def test_creacion_usuario_roles(self):
        admin = Usuario.objects.create_user(
            username="admin_user",
            password="password123",
            rol="ADMIN",
            mercado=self.mercado
        )
        vendedor = Usuario.objects.create_user(
            username="vendedor_user",
            password="password123",
            rol="VENDEDOR",
            mercado=self.mercado
        )

        self.assertTrue(admin.is_admin)
        self.assertFalse(admin.is_vendedor)
        self.assertTrue(vendedor.is_vendedor)
        self.assertFalse(vendedor.is_admin)


class UsuarioAuthAPITestCase(APITestCase):
    def setUp(self):
        self.mercado = Mercado.objects.create(nombre="Test Mercado")
        self.admin = Usuario.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="password123",
            rol="ADMIN",
            mercado=self.mercado
        )
        self.vendedor = Usuario.objects.create_user(
            username="vendedor",
            email="vendedor@test.com",
            password="password123",
            rol="VENDEDOR",
            mercado=self.mercado
        )

    def test_login_exitoso_y_jwt(self):
        url = reverse('token_obtain_pair')
        data = {
            'username': 'vendedor',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)
        self.assertEqual(response.data.get('status'), 'success')

    def test_login_incorrecto(self):
        url = reverse('token_obtain_pair')
        data = {
            'username': 'vendedor',
            'password': 'wrong_password'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_permisos_usuario_viewset(self):
        # Intentar listar usuarios sin autenticación
        url = reverse('usuarios-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Autenticar como vendedor (no admin) y listar usuarios (debería dar Forbidden)
        self.client.force_authenticate(user=self.vendedor)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Autenticar como admin y listar usuarios (debería dar OK)
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_desactivar_usuario_toggle(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('toggle_activo', kwargs={'pk': self.vendedor.pk})
        
        # Desactivar
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.vendedor.refresh_from_db()
        self.assertFalse(self.vendedor.is_active)

        # Activar de nuevo
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.vendedor.refresh_from_db()
        self.assertTrue(self.vendedor.is_active)

    def test_no_desactivarse_a_si_mismo(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('toggle_activo', kwargs={'pk': self.admin.pk})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)


class PingAPITestCase(APITestCase):
    def test_ping_endpoint(self):
        url = reverse('ping')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'status': 'ok'})



