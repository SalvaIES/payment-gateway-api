from rest_framework.routers import DefaultRouter
from .views import ProviderViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r'providers', ProviderViewSet, basename='provider')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = router.urls