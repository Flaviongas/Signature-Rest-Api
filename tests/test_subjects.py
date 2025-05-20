import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from signature.models import Subject, Major, Student

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

@pytest.fixture
def test_subject(test_major):
    subject = Subject.objects.create(name='Programming 101')
    subject.major.add(test_major)
    return subject

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
    
    def test_create_subject_success(self, auth_client, test_major):
        client, _ = auth_client
        url = reverse('subjects-list')
        data = {
            'name': 'New Subject',
            'major': [test_major.id]
        }
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Subject.objects.filter(name='New Subject').exists()
        
    def test_create_subject_without_major(self, auth_client):
        client, _ = auth_client
        url = reverse('subjects-list')
        data = {
            'name': 'Subject Without Major'
        }
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_subject_with_invalid_name(self, auth_client, test_major):
        client, _ = auth_client
        url = reverse('subjects-list')
        data = {
            'name': '',  # Empty name
            'major': [test_major.id]
        }
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_update_subject_success(self, auth_client, test_subject):
        client, _ = auth_client
        url = reverse('subjects-detail', kwargs={'pk': test_subject.id})
        data = {
            'name': 'Updated Subject Name',
            'major': [m.id for m in test_subject.major.all()]
        }
        response = client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        test_subject.refresh_from_db()
        assert test_subject.name == 'Updated Subject Name'
    
    def test_update_subject_invalid_data(self, auth_client, test_subject):
        client, _ = auth_client
        url = reverse('subjects-detail', kwargs={'pk': test_subject.id})
        data = {
            'name': ''  # Invalid name
        }
        response = client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_delete_subject_success(self, auth_client, test_subject):
        client, _ = auth_client
        url = reverse('subjects-detail', kwargs={'pk': test_subject.id})
        response = client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Subject.objects.filter(id=test_subject.id).exists()
    
    def test_delete_nonexistent_subject(self, auth_client):
        client, _ = auth_client
        url = reverse('subjects-detail', kwargs={'pk': 99999})
        response = client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_enroll_student_to_subject(self, auth_client, test_subject, test_student):
        client, _ = auth_client
        url = reverse('students-add-subject')
        data = {
            'student_id': test_student.id,
            'subject_id': test_subject.id
        }
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        test_subject.refresh_from_db()
        assert test_student in test_subject.students.all()
    
    def test_enroll_nonexistent_student(self, auth_client, test_subject):
        client, _ = auth_client
        url = reverse('students-add-subject')
        data = {
            'student_id': 99999,
            'subject_id': test_subject.id
        }
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_enroll_student_to_nonexistent_subject(self, auth_client, test_student):
        client, _ = auth_client
        url = reverse('students-add-subject')
        data = {
            'student_id': test_student.id,
            'subject_id': 99999
        }
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_unenroll_students_from_subject(self, auth_client, test_subject, test_student):
        # First enroll the student
        test_subject.students.add(test_student)
        
        client, _ = auth_client
        url ='/api/students/remove-subject/'
        data = {
            'student_id': test_student.id,
            'subject_id': test_subject.id
        }
        response = client.delete(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        test_subject.refresh_from_db()
        assert test_student not in test_subject.students.all()
    
    def test_unenroll_nonexistent_student(self, auth_client, test_subject):
        client, _ = auth_client
        url ='/api/students/remove-subject/'
        data = {
            'student_id': 99999,
            'subject_id': test_subject.id
        }
        response = client.delete(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_unauthorized_access(self, api_client):
        url = reverse('subjects-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
