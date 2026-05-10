from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class FrontendLoginTests(TestCase):
    """Pruebas para el login del frontend."""

    def setUp(self):
        """Configura el cliente y usuario de prueba."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_login_page_carga(self):
        """La página de login debe devolver 200."""
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_login_incorrecto(self):
        """Login con credenciales incorrectas vuelve al login."""
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)

    def test_dashboard_sin_sesion_redirige(self):
        """El dashboard sin sesión redirige al login."""
        response = self.client.get('/')
        self.assertRedirects(response, '/login/')

    def test_providers_sin_sesion_redirige(self):
        """Providers sin sesión redirige al login."""
        response = self.client.get('/providers/')
        self.assertRedirects(response, '/login/')

    def test_transactions_sin_sesion_redirige(self):
        """Transactions sin sesión redirige al login."""
        response = self.client.get('/transactions/')
        self.assertRedirects(response, '/login/')

    def test_logout_sin_sesion_redirige(self):
        """Logout sin sesión redirige al login."""
        response = self.client.get('/logout/')
        self.assertRedirects(response, '/login/')