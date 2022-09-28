import pytest
from django.contrib.auth.models import User

from data import *


@pytest.mark.django_db
def test_register_user(client):
    payload = USER_1
    response = client.post(path="/api/users/", data=payload)
    data = response.data

    assert data['username'] == payload['username']
    assert response.status_code == 201
    assert User.objects.count() == 1
    assert 'password' in data


@pytest.mark.django_db
def test_login_user(client, user):
    response = client.post('/api/login/', USER_1)

    assert response.status_code == 302  # перенаправляет на страницу с кошельками
    assert response.url == '/api/wallets/'


@pytest.mark.django_db
def test_login_user_fail(client):
    response = client.post('/api/login/', dict(
        username='testuserfail',
        password='test123'
    ))
    assert response.status_code == 200  # стандартная работа аутентификации Django


@pytest.mark.django_db
def test_get_page_auth_user(client, auth_user):
    response = client.get('/api/wallets/')

    assert response.status_code == 200
    assert response.data == []


@pytest.mark.django_db
def test_get_list_users_unauth_user(client):
    response = client.get('/api/users/')

    assert response.status_code == 200
    assert response.data == []


@pytest.mark.django_db
def test_get_detail_user_auth_user(auth_user):
    prefix = auth_user.get('/api/users/').data[0]['id']
    response = auth_user.get(f'/api/users/{prefix}/')

    assert response.status_code == 200
    assert response.data['username'] == USER_1['username']
    assert len(response.data) == 3


@pytest.mark.django_db
def test_get_detail_user_unauth_user(client, user):
    pk = user.id
    response = client.get(f'/api/users/{pk}/')

    assert response.status_code == 401
    assert response.data['detail'] == 'Учетные данные не были предоставлены.'


@pytest.mark.django_db
def test_logout_user(auth_user):
    response = auth_user.get('/api/logout/')

    assert response.status_code == 200
    # assert response.cookie



