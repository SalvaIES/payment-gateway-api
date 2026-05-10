from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from core.views import stripe_webhook, redsys_payment, redsys_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/auth/login/', obtain_auth_token, name='api_token_auth'),
    path('api/webhooks/stripe/', stripe_webhook, name='stripe_webhook'),
    path('api/pay/redsys/<int:transaction_id>/', redsys_payment, name='redsys_payment'),
    path('api/webhooks/redsys/', redsys_webhook, name='redsys_webhook'),
    path('', include('frontend.urls')),
]