from datetime import datetime
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from pyredsys.payment import request_payment, MerchantParameters
from pyredsys.notification import validate_notification, SignatureVerificationError
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
        """Crea la transacción y un PaymentIntent en Stripe si el proveedor es Stripe."""
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
                    stripe_payment_intent_id=intent.id,
                    stripe_client_secret=intent.client_secret
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


def stripe_payment(request, transaction_id):
    """Muestra el formulario de pago de Stripe."""
    try:
        transaction = Transaction.objects.get(id=transaction_id)
    except Transaction.DoesNotExist:
        return HttpResponse(status=404)

    if not transaction.stripe_client_secret:
        return HttpResponse('Esta transacción no tiene un client secret de Stripe.', status=400)

    return render(request, 'core/stripe_payment.html', {
        'transaction': transaction,
        'client_secret': transaction.stripe_client_secret,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    })


@csrf_exempt
def redsys_payment(request, transaction_id):
    """Genera el formulario de pago de Redsys."""
    try:
        transaction = Transaction.objects.get(id=transaction_id)
    except Transaction.DoesNotExist:
        return HttpResponse(status=404)

    merchant_params = MerchantParameters(
        DS_MERCHANT_AMOUNT=int(transaction.amount * 100),
        DS_MERCHANT_ORDER=f'P{str(transaction.id).zfill(11)}',
        DS_MERCHANT_MERCHANTCODE=int(settings.REDSYS_MERCHANT_CODE),
        DS_MERCHANT_CURRENCY=978,
        DS_MERCHANT_TRANSACTIONTYPE=0,
        DS_MERCHANT_TERMINAL=int(settings.REDSYS_TERMINAL),
        DS_MERCHANT_MERCHANTURL='https://outscore-footless-pebbly.ngrok-free.dev/api/webhooks/redsys/',
        DS_MERCHANT_URLOK='https://outscore-footless-pebbly.ngrok-free.dev/transactions/',
        DS_MERCHANT_URLKO='https://outscore-footless-pebbly.ngrok-free.dev/transactions/',
    )

    signed = request_payment(
        settings.REDSYS_SECRET_KEY,
        merchant_params
    )

    return render(request, 'core/redsys_payment.html', {
        'redsys_url': settings.REDSYS_URL,
        'merchant_parameters': signed.Ds_MerchantParameters,
        'merchant_signature': signed.Ds_Signature,
        'signature_version': signed.Ds_SignatureVersion,
    })


@csrf_exempt
def redsys_webhook(request):
    """Recibe y procesa las notificaciones de Redsys."""
    if request.method == 'POST':
        try:
            parameters = request.POST.get('Ds_MerchantParameters')
            signature = request.POST.get('Ds_Signature')
            version = request.POST.get('Ds_SignatureVersion')

            notification = validate_notification(
                settings.REDSYS_SECRET_KEY,
                parameters,
                signature,
                version
            )

            response_code = notification.Ds_Response
            order = notification.Ds_Order.lstrip('P').lstrip('0') or '0'

            if response_code < 100:
                Transaction.objects.filter(id=order).update(
                    status='completed'
                )
            else:
                Transaction.objects.filter(id=order).update(
                    status='failed',
                    incident_type='error_conexion'
                )
        except SignatureVerificationError:
            return HttpResponse(status=400)
        except Exception:
            return HttpResponse(status=400)

    return HttpResponse(status=200)
