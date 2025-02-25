from rest_framework import routers
from .api import MajorViewSet, SubjectViewSet, StudentViewSet

router = routers.DefaultRouter()

router.register('api/majors', MajorViewSet, 'majors')
router.register('api/subjects', SubjectViewSet, 'subjects')
router.register('api/students', StudentViewSet, 'students')


urlpatterns = router.urls
