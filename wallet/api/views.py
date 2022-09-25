from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .permissions import *
from .serializers import *


# ________________________________USERS________________________________
class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsOwnerOrAdminReadOnly,)


# ________________________________WALLET________________________________
class WalletListCreate(generics.ListCreateAPIView):
    # queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    
    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)


class WalletRetrieveDestroy(generics.RetrieveDestroyAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = (IsOwnerWallet,)
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = Wallet.objects.get(name=kwargs['name'])
        except:
            return Response({'error': 'Wallet does not exist'})
        self.check_object_permissions(request, instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = Wallet.objects.get(name=kwargs['name'])
        except:
            return Response({'error': 'Wallet does not exist'})
        self.check_object_permissions(request, instance)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ________________________________TRANSACTION________________________________
class TransactionListCreate(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
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
    # queryset = Transaction.objects.all()
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

    
