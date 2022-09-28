import pytest

from data import *
from wallet.api.models import Wallet


@pytest.mark.django_db
def test_create_two_wallets(force_auth_user):
    response1 = force_auth_user.post('/api/wallets/', WALLET_1)
    response2 = force_auth_user.post('/api/wallets/', WALLET_2)

    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response1.data['type'] == 'v'
    assert response2.data['type'] == 'm'
    assert response1.data['balance'] == response2.data['balance']
    assert Wallet.objects.count() == 2


@pytest.mark.django_db
def test_get_list_wallets(wallet1_user):
    response = wallet1_user.get('/api/wallets/')

    assert response.status_code == 200
    assert len(response.data) == 1
    assert bool(response.data[0]['name'])

@pytest.mark.django_db
def test_get_wallet(wallet1_user):
    prefix = wallet1_user.get('/api/wallets/').data[0]['name']
    response = wallet1_user.get(f'/api/wallets/{prefix}/')

    assert response.status_code == 200
    assert response.data['name'] == prefix
    assert response.data['balance'] == '3.00'

