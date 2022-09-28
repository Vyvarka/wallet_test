import pytest

from rest_framework.test import APIClient
from django.contrib.auth.models import User

from data import *


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(**USER_1)


@pytest.fixture
def admin():
    return User.objects.create_superuser(**ADMIN)


@pytest.fixture
def auth_user(user, client):
    client.post('/api/login/', USER_1)
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
def wallet1_user(force_auth_user):
    force_auth_user.post('/api/wallets/', WALLET_1)
    return force_auth_user
