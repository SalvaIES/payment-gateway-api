from rest_framework import viewsets, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Provider, Transaction
from .serializers import ProviderSerializer, TransactionSerializer


class ProviderViewSet(viewsets.ModelViewSet):
    """CRUD completo para proveedores de pago."""

    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'environment']


class TransactionViewSet(viewsets.ModelViewSet):
    """CRUD completo para transacciones con filtros por proveedor, estado y fecha."""

    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['status', 'incident_type', 'currency']
    ordering_fields = ['created_at', 'amount']

    def get_queryset(self):
        """Filtra las transacciones según los parámetros de la URL."""
        queryset = Transaction.objects.all()
        provider = self.request.query_params.get('provider')
        status = self.request.query_params.get('status')
        date = self.request.query_params.get('date')

        if provider:
            queryset = queryset.filter(provider__id=provider)
        if status:
            queryset = queryset.filter(status=status)
        if date:
            queryset = queryset.filter(created_at__date=date)

        return queryset