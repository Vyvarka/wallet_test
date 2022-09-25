from django.contrib.auth.models import User
from django.db import transaction

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
        types = [x[0] for x in Wallet.TYPE]
        if value not in types:  # добавить проверку строки без учета регистра?
            raise serializers.ValidationError(
                f'This field accepts the following values: {types}')
        return value  # добавить преобразование строки для единого формата
    
    def validate_currency(self, value):
        currencies = [x[0] for x in Wallet.CURRENCY]
        if value not in currencies:  # добавить проверку строки без учета регистра?
            raise serializers.ValidationError(
                f'This field accepts the following values: {currencies}')
        return value  # добавить преобразование строки для единого формата
    
    def create(self, validated_data):
        if Wallet.objects.filter(user=validated_data['user']).count() >= Wallet.MAX_WALLETS:
            raise serializers.ValidationError(f'Limit wallets: {Wallet.MAX_WALLETS}')
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
    def validate_sender(self, value):
        return value
    
    def validate_receiver(self, value):
        return value
    
    def validate_transfer_amount(self, value):
        # print(self._kwargs.values())
        min_value = 0.1  # 0,1 - мин сумма при комиссии 10%. 0,01/(10%)*(100%) = 0,1
        if float(value) < min_value:
            raise serializers.ValidationError(
                f'This amount less than minimum value: {min_value}')
        # if float(value) < balance:
        #     raise serializers.ValidationError(
        #         f'This amount gross than your balance')
        return value
    
    def create(self, validated_data):
        try:
            s = Wallet.objects.get(name=validated_data['sender'])
            r = Wallet.objects.get(name=validated_data['receiver'])
        except:
            raise serializers.ValidationError(
                f'Not exist wallet'
            )
        
        if s.name == r.name:
            raise serializers.ValidationError(
                f'The sender cannot be the receiver'
            )
        if s.currency != r.currency:
            raise serializers.ValidationError(
                f'The receiver has other type currency'
            )
        if float(s.balance) < float(validated_data['transfer_amount']):
            raise serializers.ValidationError(
                f'Amount gross than your balance'
            )
        # if s.user != serializers.CurrentUserDefault():
        #     raise serializers.ValidationError(
        #         f'The current user is not sender'
        #     )
        if s.user != r.user:
            validated_data['fee'] = '0.10'
        with transaction.atomic():
            # s.balance -= validated_data['transfer_amount']
            # r.balance += (validated_data['transfer_amount'] -
            #               validated_data['transfer_amount'] *
            #               validated_data['fee'])
            # s.save()
            # r.save()
            validated_data['status'] = 'PAID'
        return Transaction.objects.create(**validated_data)