from rest_framework.response import Response
from rest_framework.views import APIView

from wallet.api.models import Wallet
from wallet.api.serializers import WalletSerializer


class WalletListCreate(APIView):
    def get(self, request):
        w = Wallet.objects.all()
        return Response({'wallets': WalletSerializer(w, many=True).data})
    
    def post(self, request):
        serializer = WalletSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'post': serializer.data})
    
    def put(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        if not pk:
            return Response({'error': 'PUT not allowed'})
        
        try:
            instance = Wallet.objects.get(pk=pk)
        except:
            return Response({'error': 'Object does not exist'})
        serializer = WalletSerializer(data=request.data, instance=instance)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'updated': serializer.data})
    
    def delete(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        if not pk:
            return Response({'error': 'PUT not allowed'})
        
        try:
            instance = Wallet.objects.get(pk=pk)
        except:
            return Response({'error': 'Object does not exist'})
        instance.delete()
        return Response({'deleted': f'{instance}'})