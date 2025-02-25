from .models import Major
from rest_framework import viewsets, permissions
from .serializers import MajorSerializer


class MajorViewSet(viewsets.ModelViewSet):
    queryset = Major.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = MajorSerializer
