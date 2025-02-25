from rest_framework import routers
from .api import MajorViewSet, SubjectViewSet

router = routers.DefaultRouter()

router.register('api/majors', MajorViewSet, 'majors')
router.register('api/subjects', SubjectViewSet, 'subjects')

urlpatterns = router.urls
