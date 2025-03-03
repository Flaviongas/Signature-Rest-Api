from rest_framework import routers
from django.urls import re_path
from .views import MajorViewSet, SubjectViewSet, StudentViewSet, login, signup, test_token

router = routers.DefaultRouter()

router.register('api/majors', MajorViewSet, 'majors')
router.register('api/subjects', SubjectViewSet, 'subjects')
router.register('api/students', StudentViewSet, 'students')


urlpatterns = router.urls

urlpatterns += [re_path('login', login, ),
                re_path('signup', signup, ),
                re_path('test_token', test_token, )]
