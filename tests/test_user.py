import pytest
from django.urls import reverse
from rest_framework import status
from signature.models import Major
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


@pytest.mark.django_db
class TestUserAPI:

    def test_list_users_with_authorization(self, auth_client):
        client, _ = auth_client
        url = reverse('users-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0

    def test_create_user_success(self, admin_client):
        client, _ = admin_client
        url = reverse('users-list')
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'newuser@example.com',
            'major_ids': [1]  # Assuming these IDs exist
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username='newuser').exists()

    def test_create_user_without_password(self, admin_client):
        client, _ = admin_client
        url = reverse('users-list')
        data = {
            'username': 'usernopass',
            'email': 'usernopass@example.com'
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_with_invalid_username(self, admin_client):
        client, _ = admin_client
        url = reverse('users-list')
        data = {
            'username': 'invalid@user',
            'password': 'pass123',
            'email': 'invalid@example.com'
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_user_success(self, admin_client, test_major):
        client, _ = admin_client

        # Crear un segundo major para la prueba
        second_major = Major.objects.create(name='Biology', faculty='Science')

        user = User.objects.create_user(
            username='updateme', password='updatemepass')
        user.majors.add(test_major)

        # Al inicio, el usuario tiene solo test_major asignado
        assert list(user.majors.all()) == [test_major]

        url = reverse('users-detail', kwargs={'pk': user.pk})
        data = {
            'first_name': 'Updated',
            'major_ids': [second_major.id]
        }
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()

        # Verificamos que las majors se actualizaron correctamente
        assert list(user.majors.all()) == [second_major]
        assert user.majors.count() == 1

    def test_update_user_invalid_data(self, admin_client):
        client, _ = admin_client
        user = User.objects.create_user(
            username='updateme2', password='pass123')
        url = reverse('users-detail', kwargs={'pk': user.pk})
        data = {
            'username': 'invalid@username'
        }
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_user_success(self, admin_client):
        client, _ = admin_client
        user = User.objects.create_user(
            username='deleteme', password='pass123')
        url = reverse('users-detail', kwargs={'pk': user.pk})
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(username='deleteme').exists()

    def test_delete_nonexistent_user(self, admin_client):
        client, _ = admin_client
        # Assuming a non-existent ID is used
        url = reverse('users-detail', kwargs={'pk': 99999})
        response = client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthorized_access(self, api_client):
        url = reverse('users-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
