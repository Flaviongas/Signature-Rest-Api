import pytest
from django.urls import reverse
from rest_framework import status
from signature.models import Subject


@pytest.mark.django_db
class TestSubjectAPI:

    def test_list_all_subjects(self, auth_client, test_subject):
        client, _ = auth_client
        url = reverse('subjects-list')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[-1]['name'] == test_subject.name

    def test_get_subject_detail(self, auth_client, test_subject):
        client, _ = auth_client
        url = reverse('subjects-detail', kwargs={'pk': test_subject.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == test_subject.name

    def test_unauthorized_access(self, api_client):
        url = reverse('subjects-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_subjects_by_major(self, auth_client, test_major, test_subject):
        client, _ = auth_client
        url = reverse('subjects-get-subjects-by-major')
        data = {"major_id": test_major.id}
        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert any(s["name"] == test_subject.name for s in response.data)
