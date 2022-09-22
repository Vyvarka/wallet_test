from django.contrib.auth.models import User
from rest_framework import serializers

from .models import *
from .utils import balance_generator, wallet_name_generator


class UserSerializer(serializers.ModelSerializer):
    # как отправить данные на авторизацию через postman?
    class Meta:
        model = User
        fields = ['id', 'username', 'password']


#________________________________WALLET________________________________
class WalletSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    created_on = serializers.DateTimeField(read_only=True)
    modified_on = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Wallet
        fields = '__all__'
        
    def validate_type(self, value):
        lst = [x[0] for x in Wallet.TYPE]
        if value not in lst:
            raise serializers.ValidationError(
                f'This field accepts the following values: {lst}')
        return value
    
    def validate_currency(self, value):
        lst = [x[0] for x in Wallet.CURRENCY]
        if value not in lst:
            raise serializers.ValidationError(
                f'This field accepts the following values: {lst}')
        return value
    
    def create(self, validated_data):
        lst = Wallet.objects.filter(user=validated_data['user'])
        if len(lst) < 5:
            print('create wallet')
        validated_data['name'] = wallet_name_generator()
        validated_data['balance'] = balance_generator(validated_data['currency']) or '0.00'
        return Wallet.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.balance = validated_data.get('balance', instance.balance)
        instance.modified_on = validated_data.get('modified_on', instance.modified_on)
        instance.save()
        return instance


#________________________________TRANSACTION________________________________
class TransactionSerializer(serializers.ModelSerializer):
    # как получать в поле "sender" только кошельки текущего пользователя?
    fee = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    status = serializers.CharField(max_length=6, read_only=True)
    timestamp = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'
    # переопределить функцию создания транзакций. Во время транзакции рассчитывать
    # комиссию, уменьшать сумму получения на размер комиссии, менять статус транзакции

    # добавить валидацию по типу отправляемой суммы, по кошельку-отправителю и
    # кошельку получателю (они не должны быть равны,
    # отправлять можно только со своих кошельков, тип валюты должен совпадать)
    

class TransactionWalletDetailSerializer(serializers.ModelSerializer):
    # как получать все данные связанных транзакций с кошельком?
    send_wallet = serializers.StringRelatedField(many=True, read_only=True)
    receive_wallet = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Wallet
        fields = ['name', 'send_wallet', 'receive_wallet']
        