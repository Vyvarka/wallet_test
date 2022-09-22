from .views import *
from django.urls import path, include

urlpatterns = [
    path('', include('rest_framework.urls')),
    path('users/', UserListCreate.as_view()),
    path('users/<int:pk>/', UserDetail.as_view()),
    path('wallet/', WalletListCreate.as_view()),
    path('wallet/<path:name>/', WalletRetrieveDestroy.as_view())
]
