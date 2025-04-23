from rest_framework import routers
from django.urls import path, include
from .views import MajorViewSet, SubjectViewSet, StudentViewSet, UserViewSet, login, signup, test_token, isAdmin

router = routers.DefaultRouter()
router.register('majors', MajorViewSet, basename='majors')
router.register('subjects', SubjectViewSet, basename='subjects')
router.register('students', StudentViewSet, basename='students')
router.register('users', UserViewSet, basename='users') 

urlpatterns = [
    path('api/', include(router.urls)),
    
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('test_token/', test_token, name='test_token'),
    path('isAdmin/', isAdmin, name='isAdmin'),
]
