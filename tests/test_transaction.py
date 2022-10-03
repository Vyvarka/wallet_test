from decimal import Decimal

import pytest
from rest_framework.exceptions import ErrorDetail

from .data import *
from api.models import Transaction, Wallet


@pytest.mark.django_db
def test_create_transaction_user1_admin(first_wallet_admin, first_wallet_user1, two_wallets_user1):
    payload = dict(
        sender=first_wallet_user1,
        receiver=first_wallet_admin,
        transfer_amount=Decimal(1.00)
    )
    response = two_wallets_user1.post('/api/wallets/transactions/', payload)

    assert response.status_code == 201
    assert Transaction.objects.count() == 1
    assert len(response.data) == 7
    assert response.data['fee'] == '0.10'
    assert Wallet.objects.get(name=payload['sender']).balance == Decimal('2.00')
    assert Wallet.objects.get(name=payload['receiver']).balance == Decimal('3.90')


@pytest.mark.django_db
def test_create_transaction_admin_admin(two_wallets_admin, first_wallet_admin, last_wallet_admin):
    payload = dict(
        sender=first_wallet_admin,
        receiver=last_wallet_admin,
        transfer_amount=Decimal(1.00)
    )
    response = two_wallets_admin.post('/api/wallets/transactions/', payload)

    assert response.status_code == 201
    assert Transaction.objects.count() == 1
    assert len(response.data) == 7
    assert response.data['fee'] == '0.00'
    assert Wallet.objects.get(name=payload['sender']).balance == Decimal('2.00')
    assert Wallet.objects.get(name=payload['receiver']).balance == Decimal('4.00')


@pytest.mark.django_db
def test_get_two_transaction_admin(two_transactions_admin, first_wallet_admin):
    response = two_transactions_admin.get('/api/wallets/transactions/')

    assert response.status_code == 200
    assert Transaction.objects.count() == 2
    assert response.data[0]['fee'] == '0.00'
    assert response.data[0]['status'] == 'PAID'
    assert Wallet.objects.get(name=first_wallet_admin).balance == Decimal('3.00')


@pytest.mark.django_db
def test_get_list_transactions_user2(
        first_wallet_admin,
        first_wallet_user1,
        first_wallet_user2,
        two_wallets_user2
):
    t1 = Transaction.objects.create(
        sender=Wallet.objects.get(name=first_wallet_admin),
        receiver=Wallet.objects.get(name=first_wallet_user1),
        transfer_amount=Decimal(1.00)
    )
    t2 = Transaction.objects.create(
        sender=Wallet.objects.get(name=first_wallet_user1),
        receiver=Wallet.objects.get(name=first_wallet_user2),
        transfer_amount=Decimal(2.00)
    )
    t3 = two_wallets_user2.post('/api/wallets/transactions/', dict(
        sender=first_wallet_user2,
        receiver=first_wallet_user1,
        transfer_amount=Decimal(2.50)
    ))
    response = two_wallets_user2.get('/api/wallets/transactions/')

    assert t3.status_code == 201
    assert response.status_code == 200
    assert Transaction.objects.count() == 3
    assert len(response.data) == 2  # we didn't get one transaction, because have worked permission
    assert response.data[0]['sender'] == first_wallet_user2
    assert Wallet.objects.count() == 6


@pytest.mark.django_db
def test_get_detail_transaction_user2(
        first_wallet_admin,
        first_wallet_user1,
        first_wallet_user2,
        two_wallets_user2
):
    # transaction N1
    t1 = Transaction.objects.create(
        sender=Wallet.objects.get(name=first_wallet_admin),
        receiver=Wallet.objects.get(name=first_wallet_user2),
        transfer_amount=Decimal(1.00)
    )
    # transaction N2
    t2 = Transaction.objects.create(
        sender=Wallet.objects.get(name=first_wallet_user1),
        receiver=Wallet.objects.get(name=first_wallet_user2),
        transfer_amount=Decimal(2.00)
    )
    # transaction N3
    t3 = two_wallets_user2.post('/api/wallets/transactions/', dict(
        sender=first_wallet_user2,
        receiver=first_wallet_admin,
        transfer_amount=Decimal(2.50)
    ))
    pk = Transaction.objects.first().id
    response = two_wallets_user2.get(f'/api/wallets/transactions/{pk}/')

    assert response.status_code == 200
    assert Transaction.objects.count() == 3
    assert response.data['sender'] == first_wallet_user2


@pytest.mark.django_db
def test_get_detail_transaction_other_user(
        first_wallet_user1,
        first_wallet_user2,
        first_wallet_admin,
        two_wallets_admin
):
    # transaction N1
    t1 = Transaction.objects.create(
        sender=Wallet.objects.get(name=first_wallet_user1),
        receiver=Wallet.objects.get(name=first_wallet_user2),
        transfer_amount=Decimal(2.00)
    )
    pk = Transaction.objects.first().pk
    response = two_wallets_admin.get(f'/api/wallets/transactions/{pk}/')

    assert response.status_code == 403
    assert Transaction.objects.count() == 1
    assert Wallet.objects.count() == 6
    assert t1.sender != first_wallet_admin
    assert t1.receiver != first_wallet_admin


@pytest.mark.django_db
def test_delete_transaction_admin(
        first_wallet_user1,
        first_wallet_admin,
        two_wallets_admin
):
    # transaction N1
    t1 = two_wallets_admin.post('/api/wallets/transactions/', dict(
        sender=first_wallet_admin,
        receiver=first_wallet_user1,
        transfer_amount=Decimal(2.00)
    ))
    pk = t1.data['id']
    response = two_wallets_admin.delete(f'/api/wallets/transactions/{pk}/')

    assert response.status_code == 405


@pytest.mark.django_db
def test_create_transaction_admin_fail_amount(
        first_wallet_user1,
        first_wallet_admin,
        two_wallets_admin
):
    response = two_wallets_admin.post('/api/wallets/transactions/', dict(
        sender=first_wallet_admin,
        receiver=first_wallet_user1,
        transfer_amount=Decimal(4.00)
    ))
    error = ErrorDetail('The transfer amount grosser than your balance', code='invalid')

    assert response.status_code == 400
    assert response.data[0] == error
    assert Transaction.objects.count() == 0


@pytest.mark.django_db
def test_create_transaction_admin_fail_sender(
        first_wallet_user1,
        first_wallet_admin,
        two_wallets_admin
):
    response = two_wallets_admin.post('/api/wallets/transactions/', dict(
        sender=first_wallet_user1,
        receiver=first_wallet_admin,
        transfer_amount=Decimal(1.00)
    ))
    error = ErrorDetail(
        f'The current user cannot be the sender from this wallet {first_wallet_user1}',
        code='invalid'
    )

    assert response.status_code == 400
    assert response.data[0] == error
    assert Transaction.objects.count() == 0


@pytest.mark.django_db
def test_create_transaction_admin_fail_receiver(
        first_wallet_admin,
        two_wallets_admin
):
    response = two_wallets_admin.post('/api/wallets/transactions/', dict(
        sender=first_wallet_admin,
        receiver=first_wallet_admin,
        transfer_amount=Decimal(1.00)
    ))
    error = ErrorDetail(f'The sender cannot be the receiver', code='invalid')

    assert response.status_code == 400
    assert response.data[0] == error
    assert Transaction.objects.count() == 0


@pytest.mark.django_db
def test_create_transaction_admin_fail_currency(
        last_wallet_user2,
        first_wallet_admin,
        two_wallets_admin
):
    response = two_wallets_admin.post('/api/wallets/transactions/', dict(
        sender=first_wallet_admin,
        receiver=last_wallet_user2,
        transfer_amount=Decimal(1.00)
    ))
    error = ErrorDetail(f'The receiver has other type currency', code='invalid')

    assert response.status_code == 400
    assert response.data[0] == error
    assert Transaction.objects.count() == 0
