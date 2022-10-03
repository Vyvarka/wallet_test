from decimal import Decimal

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F

from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from .models import *
from .utils import balance_generator, wallet_name_generator


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


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
        
    def validate_type(self, value: str):
        types = [x[0] for x in Wallet.TYPE]
        if value.lower() not in types:
            raise serializers.ValidationError(
                f'This field accepts the following values: {types}')
        return value.lower()
    
    def validate_currency(self, value: str):
        currencies = [x[0] for x in Wallet.CURRENCY]
        if value.lower() not in currencies:
            raise serializers.ValidationError(
                f'This field accepts the following values: {currencies}')
        return value.lower()
    
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

    def validate_transfer_amount(self, value):
        min_value = 0.1  # 0,1 - мин сумма при комиссии 10%. 0,01/(10%)*(100%) = 0,1
        if float(value) < min_value:
            raise serializers.ValidationError(
                f'This amount less than minimum value: {min_value}')
        return value
    
    def create(self, validated_data):
        sender = get_object_or_404(Wallet, name=validated_data['sender'])
        receiver = get_object_or_404(Wallet, name=validated_data['receiver'])

        # блок проверок перед выполнением транзакции и сохранением в БД
        if sender.name == receiver.name:  # имя кошелька-отправителя не должно совпадать с получателем
            raise serializers.ValidationError(
                f'The sender cannot be the receiver'
            )
        if sender.currency != receiver.currency:  # валюты кошельков должны совпадать
            raise serializers.ValidationError(
                f'The receiver has other type currency'
            )
        if float(sender.balance) < float(validated_data['transfer_amount']):  # сумма перевода не должна превышать баланс
            raise serializers.ValidationError(
                f'The transfer amount grosser than your balance'
            )
        if sender.user != self.context['request'].user:  # нельзя отправить средства с чужого кошелька
            raise serializers.ValidationError(
                f'The current user cannot be the sender from this wallet {sender.name}'
            )
        if sender.user != receiver.user:  # устанавливаем комиссию при отправке на чужой кошелек
            validated_data['fee'] = Transaction.FEE
        fee_amount = round(
            Decimal(validated_data['transfer_amount']) * Decimal(validated_data.get('fee', 0.00)), 2
        )

        with transaction.atomic():
            # уменьшаем баланс отправителя
            sender.balance = F('balance') - validated_data['transfer_amount']
            # увеличиваем баланс получателя с учетом комиссии
            receiver.balance = F('balance') + validated_data['transfer_amount'] - str(fee_amount)
            sender.save()
            receiver.save()
            # меняем статус транзакции
            validated_data['status'] = 'PAID'
        return Transaction.objects.create(**validated_data)
