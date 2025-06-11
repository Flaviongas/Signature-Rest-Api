import pytest
from django.urls import reverse
from rest_framework import status
from signature.models import Major, Subject


@pytest.mark.django_db
class TestMajorAPI:

    def test_list_majors(self, auth_client, test_major):
        """Probar que un usuario autorizado puede ver la lista de carreras"""
        client, _ = auth_client
        url = reverse('majors-list')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert any(major['name'] == test_major.name for major in response.data)

    def test_get_major_detail(self, auth_client, test_major):
        """Probar que un usuario autorizado puede ver los detalles de una carrera"""
        client, _ = auth_client
        url = reverse('majors-detail', kwargs={'pk': test_major.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == test_major.name
        assert response.data['faculty'] == test_major.faculty

    def test_post_not_allowed(self, admin_client):
        """Probar que POST no está permitido en majors"""
        client, _ = admin_client
        url = reverse('majors-list')
        data = {'name': 'New Major', 'faculty': 'New Faculty'}
        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_put_not_allowed(self, admin_client, test_major):
        """Probar que PUT no está permitido en majors"""
        client, _ = admin_client
        url = reverse('majors-detail', kwargs={'pk': test_major.id})
        data = {'name': 'Updated Major', 'faculty': 'Updated Faculty'}
        response = client.put(url, data, format='json')

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_patch_not_allowed(self, admin_client, test_major):
        """Probar que PATCH no está permitido en majors"""
        client, _ = admin_client
        url = reverse('majors-detail', kwargs={'pk': test_major.id})
        data = {'name': 'Partially Updated Major'}
        response = client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_delete_not_allowed(self, admin_client, test_major):
        """Probar que DELETE no está permitido en majors"""
        client, _ = admin_client
        url = reverse('majors-detail', kwargs={'pk': test_major.id})
        response = client.delete(url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_unauthorized_access(self, api_client):
        """Probar que un usuario no autenticado no puede acceder a la API de carreras"""
        url = reverse('majors-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_majors_action(self, auth_client, test_major):
        """Probar la acción personalizada getMajors"""
        client, _ = auth_client
        url = reverse('majors-getMajors')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) >= 1

        found = any(major['id'] == test_major.id and major['name'] == test_major.name for major in response.data)
        assert found

    def test_major_with_subjects(self, auth_client, test_major):
        """Probar que se pueden obtener las materias asociadas a una carrera"""
        subject = Subject.objects.create(name='Test Subject')
        subject.major.add(test_major)

        client, _ = auth_client
        url = reverse('majors-detail', kwargs={'pk': test_major.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['subjects']) == 1
        assert response.data['subjects'][0]['name'] == 'Test Subject'
