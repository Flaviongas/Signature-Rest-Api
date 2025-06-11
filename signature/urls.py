from rest_framework import routers
from django.urls import path, include
from .views import MajorViewSet, SubjectViewSet, StudentViewSet, UserViewSet, login, signup, userExists, isAdmin, sendEmail, uploadUserCSV, uploadStudentCSV, uploadStudentSubjectCSV

router = routers.DefaultRouter()
router.register('majors', MajorViewSet, basename='majors')
router.register('subjects', SubjectViewSet, basename='subjects')
router.register('students', StudentViewSet, basename='students')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('api/', include(router.urls)),
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('userExists/', userExists, name='userExists'),
    path('isAdmin/', isAdmin, name='isAdmin'),
    path('sendEmail/', sendEmail, name='sendEmail'),
    path('uploadUserCSV/', uploadUserCSV, name='uploadUserCSV'),
    path('uploadStudentCSV/', uploadStudentCSV, name='uploadStudentCSV'),
    path('uploadStudentSubjectCSV/', uploadStudentSubjectCSV,
         name='uploadStudentSubjectCSV'),
]
