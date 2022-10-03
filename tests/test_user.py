import pytest
from django.contrib.auth.models import User

from .data import *


@pytest.mark.django_db
def test_register_user(client):
    payload = USER_1
    response = client.post("/api/users/", payload)

    assert response.data['username'] == payload['username']
    assert response.status_code == 201
    assert User.objects.count() == 1
    assert 'password' in response.data


@pytest.mark.django_db
def test_register_user_fail_data(client):
    payload = USER_FAIL  # don't have password
    response = client.post("/api/users/", payload)

    assert response.status_code == 400
    assert bool(response.data['password'])


@pytest.mark.django_db
def test_login_user(client, user):
    response = client.post('/api/login/', USER_1)

    assert response.status_code == 302  # redirect to the wallets page
    assert response.url == '/api/wallets/'


@pytest.mark.django_db
def test_login_user_fail_data(client):
    response = client.post('/api/login/', dict(
        username='testuserfail',
        password='test123'
    ))
    assert response.status_code == 200  # it's standard work of Django


@pytest.mark.django_db
def test_get_list_users_auth_user(auth_user, admin):
    response = auth_user.get('/api/users/')

    assert response.status_code == 200
    assert len(response.data) == 1
    assert User.objects.count() == 2

@pytest.mark.django_db
def test_get_list_users_admin(auth_admin, user):
    response = auth_admin.get('/api/users/')

    assert response.status_code == 200
    assert len(response.data) == 2
    assert User.objects.count() == 2


@pytest.mark.django_db
def test_get_list_users_unauth_user(client):
    response = client.get('/api/users/')

    assert response.status_code == 200
    assert response.data == []


@pytest.mark.django_db
def test_get_detail_user_auth_user(auth_user, admin):
    pk_user = auth_user.get('/api/users/').data[0]['id']
    response = auth_user.get(f'/api/users/{pk_user}/')

    assert response.status_code == 200
    assert User.objects.count() == 2
    assert response.data['username'] == USER_1['username']
    assert len(response.data) == 3


@pytest.mark.django_db
def test_get_detail_other_user_auth_user(auth_user, admin):
    pk_admin = User.objects.get(username=ADMIN['username']).id
    response = auth_user.get(f'/api/users/{pk_admin}/')

    assert response.status_code == 403
    assert User.objects.count() == 2


@pytest.mark.django_db
def test_get_detail_other_user_admin(auth_admin, user):
    pk_user = User.objects.get(username=USER_1['username']).id
    response = auth_admin.get(f'/api/users/{pk_user}/')

    assert response.status_code == 200
    assert User.objects.count() == 2
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
    # result = response.cookies
