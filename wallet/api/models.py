from django.db import models
from django.contrib.auth.models import User


class Wallet(models.Model):
    TYPE = (
        ('v', 'Visa'),
        ('m', 'Mastercard'),
    )
    CURRENCY = (
        ('usd', 'USD'),
        ('eur', 'EUR'),
        ('rub', 'RUB'),
    )
    
    name = models.CharField(max_length=8, unique=True)
    type = models.CharField(max_length=1, choices=TYPE, default='v')
    currency = models.CharField(max_length=3, choices=CURRENCY)
    balance = models.DecimalField(max_digits=15, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
        
    class Meta:
        ordering = ['-modified_on', ]
    

class Transaction(models.Model):
    sender = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='send_wallet')
    receiver = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='receive_wallet')
    transfer_amount = models.DecimalField(max_digits=15, decimal_places=2)
    fee = models.DecimalField(max_digits=3, decimal_places=2)
    status = models.CharField(max_length=6)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.sender}-{self.receiver}'
    
    class Meta:
        ordering = ['-pk', ]
