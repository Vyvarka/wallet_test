from decimal import Decimal

import pytest

from rest_framework.test import APIClient
from django.contrib.auth.models import User

from .data import *


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(**USER_1)


@pytest.fixture
def user2():
    return User.objects.create_user(**USER_2)


@pytest.fixture
def admin():
    return User.objects.create_superuser(**ADMIN)


@pytest.fixture
def auth_user(user, client):
    client.post('/api/login/', USER_1)
    return client


@pytest.fixture
def auth_user2(user2, client):
    client.post('/api/login/', USER_2)
    return client


@pytest.fixture
def auth_admin(admin, client):
    client.post('/api/login/', ADMIN)
    return client


@pytest.fixture
def force_auth_user(user):
    client = APIClient()
    client.force_authenticate(user=user, token=None)
    return client


@pytest.fixture
def wallet_user(force_auth_user):
    force_auth_user.post('/api/wallets/', WALLET_1)
    return force_auth_user


@pytest.fixture
def two_wallets_admin(auth_admin):
    auth_admin.post('/api/wallets/', WALLET_1)  # USD
    auth_admin.post('/api/wallets/', WALLET_2)  # USD
    return auth_admin


@pytest.fixture
def two_wallets_user1(auth_user):
    auth_user.post('/api/wallets/', WALLET_1)  # USD
    auth_user.post('/api/wallets/', WALLET_5)  # RUB
    return auth_user


@pytest.fixture
def two_wallets_user2(auth_user2):
    auth_user2.post('/api/wallets/', WALLET_2)  # USD
    auth_user2.post('/api/wallets/', WALLET_4)  # EUR
    return auth_user2


@pytest.fixture
def last_wallet_admin(two_wallets_admin):
    return two_wallets_admin.get(f"/api/wallets/").data[0]['name']


@pytest.fixture
def first_wallet_admin(two_wallets_admin):
    return two_wallets_admin.get(f"/api/wallets/").data[-1]['name']


@pytest.fixture
def first_wallet_user1(two_wallets_user1):
    return two_wallets_user1.get(f"/api/wallets/").data[-1]['name']


@pytest.fixture
def first_wallet_user2(two_wallets_user2):
    return two_wallets_user2.get(f"/api/wallets/").data[-1]['name']


@pytest.fixture
def last_wallet_user2(two_wallets_user2):
    return two_wallets_user2.get(f"/api/wallets/").data[0]['name']


@pytest.fixture
def two_transactions_admin(two_wallets_admin, first_wallet_admin, last_wallet_admin):
    payload1 = dict(
        sender=first_wallet_admin,
        receiver=last_wallet_admin,
        transfer_amount=Decimal(1.00)
    )
    payload2 = dict(
        sender=last_wallet_admin,
        receiver=first_wallet_admin,
        transfer_amount=Decimal(1.00)
    )
    two_wallets_admin.post('/api/wallets/transactions/', payload1)
    two_wallets_admin.post('/api/wallets/transactions/', payload2)

    return two_wallets_admin
