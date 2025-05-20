import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from signature.models import Major 


pytestmark = pytest.mark.django_db
User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def major():
    return Major.objects.create(name="Ingeniería", faculty="Facultad X")

@pytest.fixture
def user(major):
    user = User.objects.create_user(username="tester", password="Test1234")
    user.majors.add(major)
    return user

@pytest.fixture
def auth_client(user):
    token, _ = Token.objects.get_or_create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return client

def test_get_users(auth_client):
    response = auth_client.get("/api/users/")
    assert response.status_code == 200
    assert isinstance(response.data, list)
    
def test_user_creation(auth_client, major):
    data = {
        "username": "nuevoUser",
        "password": "Password123",
        "major_ids": [major.id],
    }
    response = auth_client.post("/api/users/", data, format='json')
    assert response.status_code == 201
    assert response.data['username'] == "nuevoUser"

def test_create_user_missing_password(auth_client, major):
    data = {
        "username": "nuevoUser",
        "major_ids": [major.id],
    }
    response = auth_client.post("/api/users/", data, format='json')
    assert response.status_code == 400
    assert "password" in response.data

def test_create_user_invalid_username(auth_client, major):
    data = {
        "username": "inv@lid!", 
        "password": "Password123",
        "major_ids": [major.id],
    }
    response = auth_client.post("/api/users/", data, format='json')
    assert response.status_code == 400
    assert "username" in response.data
