from django.urls import include, path

from .views import *

urlpatterns = [
    path('', include('rest_framework.urls')),
    path('users/', UserListCreate.as_view()),
    path('users/<int:pk>/', UserDetail.as_view()),
    path('wallets/', WalletListCreate.as_view(), name='wallets'),
    path('wallets/transactions/', TransactionListCreate.as_view()),
    path('wallets/transactions/<int:pk>/', TransactionDetail.as_view()),
    path('wallets/transactions/<path:wallet_name>/', TransactionWalletDetail.as_view()),
    path('wallets/<path:name>/', WalletRetrieveDestroy.as_view()),
    
]
