from django.contrib.auth.models import User
from django.test import TestCase

from .models import Wallet, Transaction
from .utils import wallet_name_generator


class UserTestCase(TestCase):
    def setUp(self) -> None:
        self.u1 = User.objects.create(username='Pupkin', password='Pup12345')
        self.w1 = Wallet.objects.create(
            name=wallet_name_generator(),
            type='v',
            currency='usd',
            balance='5.00',
            user=self.u1,
        )
        self.w2 = Wallet.objects.create(
            name=wallet_name_generator(),
            type='m',
            currency='usd',
            balance='0.00',
            user=self.u1,
        )
        self.t1 = Transaction.objects.create(
            sender=self.w1,
            receiver=self.w2,
            transfer_amount='1.00',
            fee='0.00',
            status='PAID'
        )
        print(self.u1)
