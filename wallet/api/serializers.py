from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F

from rest_framework import serializers

from .models import *
from .utils import balance_generator, wallet_name_generator


class UserSerializer(serializers.ModelSerializer):
    # как отправить данные на авторизацию через postman?
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

    def validate_transfer_amount(self, value):
        min_value = 0.1  # 0,1 - мин сумма при комиссии 10%. 0,01/(10%)*(100%) = 0,1
        if float(value) < min_value:
            raise serializers.ValidationError(
                f'This amount less than minimum value: {min_value}')
        return value
    
    def create(self, validated_data):
        try:
            s = Wallet.objects.get(name=validated_data['sender'])
            r = Wallet.objects.get(name=validated_data['receiver'])
        except:
            raise serializers.ValidationError(
                f'Not exist wallet'
            )
        # блок проверок перед выполнением транзакции и сохранением в БД
        if s.name == r.name:  # имя кошелька-отправителя не должно совпадать с получателем
            raise serializers.ValidationError(
                f'The sender cannot be the receiver'
            )
        if s.currency != r.currency:  # валюты должны совпадать
            raise serializers.ValidationError(
                f'The receiver has other type currency'
            )
        if float(s.balance) < float(validated_data['transfer_amount']):  # сумма перевода не должна превышать баланс
            raise serializers.ValidationError(
                f'Amount gross than your balance'
            )
        if s.user != self.context['request'].user:  # нельзя отправить средства с чужого кошелька
            raise serializers.ValidationError(
                f'The current user cannot be the sender'
            )
        if s.user != r.user:  # устанавливаем комиссию при отправке на чужой кошелек
            validated_data['fee'] = Transaction.FEE
        fee_amount = round(
            float(validated_data['transfer_amount']) * float(validated_data.get('fee', 0.00)), 2
        )

        with transaction.atomic():
            # уменьшаем баланс отправителя
            s.balance = F('balance') - validated_data['transfer_amount']
            # увеличиваем баланс получателя с учетом комиссии
            r.balance = F('balance') + validated_data['transfer_amount'] - str(fee_amount)
            # сохраняем результат в БД
            s.save()
            r.save()
            # меняем статус транзакции
            validated_data['status'] = 'PAID'
        return Transaction.objects.create(**validated_data)
