import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from signature.models import Major, Subject

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def auth_client():
    user = User.objects.create_user(username='testuser', password='testpass123')
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    return client, user

@pytest.fixture
def admin_client():
    admin_user = User.objects.create_superuser(username='admin', password='admin123')
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=admin_user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    return client, admin_user

@pytest.fixture
def test_major():
    return Major.objects.create(name='Test Major', faculty='Test Faculty')

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
    
    def test_create_major_success(self, admin_client):
        """Probar que un administrador puede crear una carrera con datos válidos"""
        client, _ = admin_client
        url = reverse('majors-list')
        data = {
            'name': 'New Major',
            'faculty': 'New Faculty'
        }
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Major.objects.filter(name='New Major').exists()
    
    def test_create_major_with_non_admin(self, auth_client):
        """Probar que un usuario no administrador no puede crear una carrera (solo debe recibir error de permisos)"""
        client, _ = auth_client
        url = reverse('majors-list')
        data = {
            'name': 'New Major',
            'faculty': 'New Faculty'
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED  
    
    def test_create_major_empty_name(self, admin_client):
        """Probar que no se puede crear una carrera con nombre vacío"""
        client, _ = admin_client
        url = reverse('majors-list')
        data = {
            'name': '',
            'faculty': 'Test Faculty'
        }
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_major_empty_faculty(self, admin_client):
        """Probar que no se puede crear una carrera con facultad vacía"""
        client, _ = admin_client
        url = reverse('majors-list')
        data = {
            'name': 'Test Major',
            'faculty': ''
        }
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_update_major_success(self, admin_client, test_major):
        """Probar que un administrador puede actualizar una carrera con datos válidos"""
        client, _ = admin_client
        url = reverse('majors-detail', kwargs={'pk': test_major.id})
        data = {
            'name': 'Updated Major',
            'faculty': 'Updated Faculty'
        }
        response = client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        test_major.refresh_from_db()
        assert test_major.name == 'Updated Major'
        assert test_major.faculty == 'Updated Faculty'
    
    def test_partial_update_major_success(self, admin_client, test_major):
        """Probar que un administrador puede actualizar parcialmente una carrera"""
        client, _ = admin_client
        url = reverse('majors-detail', kwargs={'pk': test_major.id})
        data = {
            'name': 'Partially Updated Major'
        }
        response = client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        test_major.refresh_from_db()
        assert test_major.name == 'Partially Updated Major'
        assert test_major.faculty == 'Test Faculty'  # No cambia
    
    def test_update_major_empty_name(self, admin_client, test_major):
        """Probar que no se puede actualizar una carrera con nombre vacío"""
        client, _ = admin_client
        url = reverse('majors-detail', kwargs={'pk': test_major.id})
        data = {
            'name': '',
            'faculty': 'Updated Faculty'
        }
        response = client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_delete_major_success(self, admin_client, test_major):
        """Probar que un administrador puede eliminar una carrera"""
        client, _ = admin_client
        url = reverse('majors-detail', kwargs={'pk': test_major.id})
        response = client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Major.objects.filter(id=test_major.id).exists()
    
    def test_delete_nonexistent_major(self, admin_client):
        """Probar que intentar eliminar una carrera inexistente devuelve 404"""
        client, _ = admin_client
        url = reverse('majors-detail', kwargs={'pk': 99999})
        response = client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
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
        
        # Verificar que el formato de la respuesta es el correcto
        found = False
        for major in response.data:
            if major['id'] == test_major.id and major['name'] == test_major.name:
                found = True
                break
        assert found
    
    def test_major_with_subjects(self, auth_client, test_major):
        """Probar que se pueden obtener las materias asociadas a una carrera"""
        # Crear una materia y asociarla con la carrera
        subject = Subject.objects.create(name='Test Subject')
        subject.major.add(test_major)
        
        client, _ = auth_client
        url = reverse('majors-detail', kwargs={'pk': test_major.id})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['subjects']) == 1
        assert response.data['subjects'][0]['name'] == 'Test Subject'