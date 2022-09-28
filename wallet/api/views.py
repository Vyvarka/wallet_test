from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import *
from .permissions import *
from .serializers import *


# ________________________________USERS________________________________
class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsOwnerOrAdminReadOnly,)


# ________________________________WALLET________________________________
class WalletListCreate(generics.ListCreateAPIView):
    serializer_class = WalletSerializer
    
    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)


class WalletRetrieveDestroy(generics.RetrieveDestroyAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = (IsOwnerWallet,)
    
    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(Wallet, name=kwargs['name'])
        self.check_object_permissions(request, instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(Wallet, name=kwargs['name'])
        self.check_object_permissions(request, instance)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ________________________________TRANSACTION________________________________
class TransactionListCreate(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    
    def get_queryset(self):
        """
        получаем только те транзакции, которые связаны с текущим пользователем, т.е.
        где он выступал отправителем либо получателем.
        """
        return Transaction.objects.filter(
            Q(sender__user=self.request.user) |
            Q(receiver__user=self.request.user)
        )


class TransactionDetail(generics.RetrieveAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (IsSenderOrReceiverTransaction,)
    

class TransactionWalletDetail(generics.ListAPIView):
    serializer_class = TransactionSerializer
    
    def get_queryset(self):
        # можно смотреть транзакции только по своим кошелькам
        return Transaction.objects.filter(
            Q(sender__name=self.kwargs['wallet_name']) |
            Q(receiver__name=self.kwargs['wallet_name'])
        ).filter(
            Q(sender__user=self.request.user) |
            Q(receiver__user=self.request.user)
        )

    
