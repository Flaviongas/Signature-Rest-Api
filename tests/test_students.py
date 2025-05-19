import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from signature.models import Student, Major

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
    return Major.objects.create(name='Computer Science', faculty='Engineering')

@pytest.fixture
def test_student(test_major):
    return Student.objects.create(
        rut='12345678',
        dv='9',
        first_name='John',
        second_name='Robert',
        last_name='Doe',
        second_last_name='Smith',
        major=test_major
    )

@pytest.mark.django_db
class TestStudentAPI:
    
    def test_list_all_students(self, auth_client, test_student):
        client, _ = auth_client
        url = reverse('students-list')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[-1]['first_name'] == test_student.first_name
    
    def test_filter_students_by_major(self, auth_client, test_major, test_student):
        client, _ = auth_client
        # Create a second major and student in that major
        second_major = Major.objects.create(name='Biology', faculty='Science')
        Student.objects.create(
            rut='98765432',
            dv='1',
            first_name='Jane',
            second_name='Mary',
            last_name='Smith',
            second_last_name='Johnson',
            major=second_major
        )
        
        url = reverse('students-get-student-bymajor')
        response = client.post(url, {'major_id': test_major.id}, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['first_name'] == test_student.first_name
    
    def test_create_student_success(self, auth_client, test_major):
        client, _ = auth_client
        url = reverse('students-create-student')
        data = {
            'rut': '11222333',
            'dv': '4',
            'first_name': 'Alice',
            'second_name': 'Marie',
            'last_name': 'Johnson',
            'second_last_name': 'Brown',
            'major_id': test_major.id
        }
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Student.objects.filter(rut='11222333', dv='4').exists()
    
    def test_create_student_missing_required_field(self, auth_client, test_major):
        client, _ = auth_client
        url = reverse('students-create-student')
        data = {
            'rut': '11222333',
            # Missing 'dv'
            'first_name': 'Alice',
            'second_name': 'Marie',
            'last_name': 'Johnson',
            'second_last_name': 'Brown',
            'major_id': test_major.id
        }
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_student_invalid_rut(self, auth_client, test_major):
        client, _ = auth_client
        url = reverse('students-create-student')
        data = {
            'rut': '11222ABC', # Non-numeric characters
            'dv': '4',
            'first_name': 'Alice',
            'second_name': 'Marie',
            'last_name': 'Johnson',
            'second_last_name': 'Brown',
            'major_id': test_major.id
        }
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_student_invalid_dv(self, auth_client, test_major):
        client, _ = auth_client
        url = reverse('students-create-student')
        data = {
            'rut': '11222333',
            'dv': 'X', # Non-numeric/non-K character
            'first_name': 'Alice',
            'second_name': 'Marie',
            'last_name': 'Johnson',
            'second_last_name': 'Brown',
            'major_id': test_major.id
        }
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_student_nonexistent_major(self, auth_client):
        client, _ = auth_client
        url = reverse('students-create-student')
        data = {
            'rut': '11222333',
            'dv': '4',
            'first_name': 'Alice',
            'second_name': 'Marie',
            'last_name': 'Johnson',
            'second_last_name': 'Brown',
            'major_id': 99999 # Non-existent major
        }
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_student_special_chars_in_name(self, auth_client, test_major):
        client, _ = auth_client
        url = reverse('students-create-student')
        data = {
            'rut': '11222333',
            'dv': '4',
            'first_name': 'Alice*', # Special character
            'second_name': 'Marie',
            'last_name': 'Johnson',
            'second_last_name': 'Brown',
            'major_id': test_major.id
        }
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_duplicate_student(self, auth_client, test_student, test_major):
        client, _ = auth_client
        url = reverse('students-create-student')
        data = {
            'rut': test_student.rut,
            'dv': test_student.dv,
            'first_name': 'Different',
            'second_name': 'Name',
            'last_name': 'Same',
            'second_last_name': 'RUT',
            'major_id': test_major.id
        }
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_delete_student_success(self, auth_client, test_student):
        client, _ = auth_client
        url = reverse('students-delete-student')
        data = {
            'student_id': test_student.id
        }
        response = client.delete(url, data, format='json')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Student.objects.filter(id=test_student.id).exists()
    
    def test_delete_nonexistent_student(self, auth_client):
        client, _ = auth_client
        url = reverse('students-delete-student')
        data = {
            'student_id': 99999
        }
        response = client.delete(url, data, format='json')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_student_success(self, auth_client, test_student, test_major):
        client, _ = auth_client
        url = reverse('students-update-student')
        data = {
            'id': test_student.id,
            'rut': test_student.rut,
            'dv': test_student.dv,
            'first_name': 'UpdatedName',
            'second_name': test_student.second_name,
            'last_name': test_student.last_name,
            'second_last_name': test_student.second_last_name,
            'major_id': test_major.id
        }
        response = client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        test_student.refresh_from_db()
        assert test_student.first_name == 'UpdatedName'
    
    def test_unauthorized_access(self, api_client):
        url = reverse('students-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED