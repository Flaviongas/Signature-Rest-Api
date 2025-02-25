from .models import Major, Subject, Student
from rest_framework import viewsets, permissions
from .serializers import MajorSerializer, SubjectSerializer, StudentSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = StudentSerializer


class MajorViewSet(viewsets.ModelViewSet):
    queryset = Major.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = MajorSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = SubjectSerializer
