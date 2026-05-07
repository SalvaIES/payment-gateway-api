from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('providers/', views.providers, name='providers'),
    path('providers/<int:provider_id>/delete/', views.delete_provider, name='delete_provider'),
    path('transactions/', views.transactions, name='transactions'),
    path('transactions/<int:transaction_id>/update/', views.update_transaction, name='update_transaction'),
    path('transactions/<int:transaction_id>/delete/', views.delete_transaction, name='delete_transaction'),
]