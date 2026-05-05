import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework import viewsets, filters, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Provider, Transaction
from .serializers import ProviderSerializer, TransactionSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


class ProviderViewSet(viewsets.ModelViewSet):
    """CRUD completo para proveedores de pago."""

    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'environment']


class TransactionViewSet(viewsets.ModelViewSet):
    """CRUD completo para transacciones con filtros."""

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
        status_param = self.request.query_params.get('status')
        date = self.request.query_params.get('date')

        if provider:
            queryset = queryset.filter(provider__id=provider)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if date:
            queryset = queryset.filter(created_at__date=date)

        return queryset

    def create(self, request, *args, **kwargs):
        """Crea la transacción y un PaymentIntent en Stripe."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = serializer.validated_data['provider']

        if provider.name.lower() == 'stripe':
            try:
                amount = serializer.validated_data['amount']
                currency = serializer.validated_data['currency'].lower()
                intent = stripe.PaymentIntent.create(
                    amount=int(amount * 100),
                    currency=currency,
                    metadata={'provider': provider.name},
                    automatic_payment_methods={
                        'enabled': True,
                        'allow_redirects': 'never'
                    }
                )
                transaction = serializer.save(
                    stripe_payment_intent_id=intent.id
                )
            except stripe.StripeError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            transaction = serializer.save()

        return Response(
            self.get_serializer(transaction).data,
            status=status.HTTP_201_CREATED
        )


@csrf_exempt
def stripe_webhook(request):
    """Recibe y procesa los eventos webhook de Stripe."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.errors.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        payment_intent_id = intent['id']
        Transaction.objects.filter(
            stripe_payment_intent_id=payment_intent_id
        ).update(status='completed')

    elif event['type'] == 'payment_intent.payment_failed':
        intent = event['data']['object']
        payment_intent_id = intent['id']
        Transaction.objects.filter(
            stripe_payment_intent_id=payment_intent_id
        ).update(status='failed', incident_type='impago')

    return HttpResponse(status=200)