from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from .models import Provider, Transaction


class ProviderTests(TestCase):
    """Pruebas para el endpoint de proveedores."""

    def setUp(self):
        """Configura el cliente autenticado y un proveedor de prueba."""
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.provider = Provider.objects.create(
            name='Stripe',
            api_key='sk_test_123',
            environment='sandbox'
        )

    def test_listar_proveedores(self):
        """GET /api/providers/ debe devolver 200 y la lista de proveedores."""
        response = self.client.get('/api/providers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_crear_proveedor(self):
        """POST /api/providers/ debe crear un proveedor y devolver 201."""
        data = {'name': 'PayPal', 'api_key': 'pk_test_456', 'environment': 'sandbox'}
        response = self.client.post('/api/providers/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Provider.objects.count(), 2)

    def test_acceso_sin_token(self):
        """GET sin autenticación debe devolver 401."""
        self.client.credentials()
        response = self.client.get('/api/providers/')
        self.assertEqual(response.status_code, 401)


class TransactionTests(TestCase):
    """Pruebas para el endpoint de transacciones."""

    def setUp(self):
        """Configura el cliente autenticado, proveedor y transacción de prueba."""
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.provider = Provider.objects.create(
            name='Stripe',
            api_key='sk_test_123',
            environment='sandbox'
        )
        self.transaction = Transaction.objects.create(
            provider=self.provider,
            amount=99.99,
            currency='EUR',
            status='pending'
        )

    def test_crear_transaccion(self):
        """POST /api/transactions/ debe crear una transacción y devolver 201."""
        data = {
            'provider': self.provider.id,
            'amount': '49.99',
            'currency': 'EUR',
            'status': 'pending'
        }
        response = self.client.post('/api/transactions/', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_importe_negativo(self):
        """POST con importe negativo debe devolver 400."""
        data = {
            'provider': self.provider.id,
            'amount': '-10.00',
            'currency': 'EUR',
            'status': 'pending'
        }
        response = self.client.post('/api/transactions/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_failed_sin_incidencia(self):
        """PUT con status failed sin incident_type debe devolver 400."""
        response = self.client.put(
            f'/api/transactions/{self.transaction.id}/',
            {'provider': self.provider.id, 'amount': '99.99',
             'currency': 'EUR', 'status': 'failed', 'incident_type': ''},
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_filtro_por_estado(self):
        """GET /api/transactions/?status=pending debe filtrar correctamente."""
        response = self.client.get('/api/transactions/?status=pending')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(t['status'] == 'pending' for t in response.data))