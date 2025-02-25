from rest_framework import routers
from .api import MajorViewSet

router = routers.DefaultRouter()

router.register('api/majors', MajorViewSet, 'majors')

urlpatterns = router.urls
