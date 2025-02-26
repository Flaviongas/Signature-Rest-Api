from .models import Major, Subject, Student
from rest_framework import viewsets, permissions
from .serializers import MajorSerializer, SubjectSerializer, StudentSerializer
from rest_framework.decorators import action
from rest_framework.response import Response


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

    @action(detail=False, methods=["GET"])
    def getMajors(self, request):
        """
        Endpoint para obtener los tipos de productos
        /products/types/
        """
        queryset = super().get_queryset()
        majors = [{"id": major.id, "name": major.name}
                  for major in queryset]
        return Response(majors)


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = SubjectSerializer
