from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from core.views import stripe_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/auth/login/', obtain_auth_token, name='api_token_auth'),
    path('api/webhooks/stripe/', stripe_webhook, name='stripe_webhook'),
    path('', include('frontend.urls')),
]