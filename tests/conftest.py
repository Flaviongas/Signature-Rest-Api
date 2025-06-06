import pytest
from django.urls import reverse
from rest_framework import status
from signature.models import Major
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client():
    user = User.objects.create_user(
        username='testuser', password='testpass123')
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    return client, user


@pytest.fixture
def admin_client():
    admin_user = User.objects.create_superuser(
        username='admin', password='admin123')
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=admin_user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    return client, admin_user


@pytest.fixture
def test_major():
    return Major.objects.create(name='Test Major', faculty='Test Faculty')
