import pytest
from rest_framework.exceptions import ErrorDetail

from .data import *
from api.models import Wallet


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
    assert Wallet.objects.get(type='v').user == Wallet.objects.get(type='m').user


@pytest.mark.django_db
def test_create_six_wallets(force_auth_user):  # max wallets = 5
    response = ''
    for x in range(6):
        force_auth_user.post('/api/wallets/', WALLET_1)
        if x == 5:
            response = force_auth_user.post('/api/wallets/', WALLET_2)

    assert response.status_code == 400
    assert Wallet.objects.count() == 5
    assert isinstance(response.data[0], ErrorDetail)


@pytest.mark.django_db
def test_create_wallet_fail(force_auth_user):
    response1 = force_auth_user.post('/api/wallets/', WALLET_FAIL_1)
    response2 = force_auth_user.post('/api/wallets/', WALLET_FAIL_2)

    assert response1.status_code == 400
    assert bool(response1.data['currency'])
    assert response2.status_code == 400
    assert bool(response2.data['type'])


@pytest.mark.django_db
def test_create_wallet_unauth_user(client, user):
    response1 = client.post('/api/wallets/', WALLET_1)

    assert response1.status_code == 401
    assert bool(response1.data)


@pytest.mark.django_db
def test_get_list_wallets(wallet_user):
    response = wallet_user.get('/api/wallets/')

    assert response.status_code == 200
    assert len(response.data) == 1
    assert bool(response.data[0]['name'])
    assert response.data[0]['type'] == WALLET_1['type']
    assert response.data[0]['balance'] == '3.00'


@pytest.mark.django_db
def test_get_detail_wallet(wallet_user):
    prefix = wallet_user.get('/api/wallets/').data[0]['name']
    response = wallet_user.get(f'/api/wallets/{prefix}/')

    assert response.status_code == 200
    assert response.data['name'] == prefix
    assert response.data['balance'] == '3.00'


@pytest.mark.django_db
def test_get_detail_wallet_other_user(wallet_user, two_wallets_admin):
    prefix = two_wallets_admin.get('/api/wallets/').data[0]['name']
    response = wallet_user.get(f'/api/wallets/{prefix}/')

    assert response.status_code == 403
    assert Wallet.objects.get(name=prefix).user.username == ADMIN['username']
    assert Wallet.objects.count() == 3


@pytest.mark.django_db
def test_get_detail_non_wallet(wallet_user):
    response = wallet_user.get(f'/api/wallets/failname/')

    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_wallet(wallet_user):
    prefix = wallet_user.get('/api/wallets/').data[0]['name']
    response = wallet_user.delete(f'/api/wallets/{prefix}/')

    assert response.status_code == 204
    assert Wallet.objects.count() == 0
