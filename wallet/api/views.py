from django.contrib.auth.models import User

from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *
from .permissions import *
from .models import *


#________________________________USERS________________________________
class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsOwnerOrAdminReadOnly,)


#________________________________WALLET________________________________
class WalletListCreate(generics.ListCreateAPIView):
    # queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    
    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        print(request.data)
        lst = Wallet.objects.filter(user=request.user)
        if len(lst) >= 5:
            return Response({'error': 'You have created the maximum '
                                      'possible number of wallets'})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    
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
    
