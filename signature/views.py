from .models import Major, Subject, Student
from rest_framework import viewsets, permissions, status
from .serializers import MajorSerializer, SubjectSerializer, StudentSerializer, UserSerializer
from rest_framework.decorators import action, api_view
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


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


@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response({"error": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)
    token = Token.objects.get_or_create(user=user)
    return Response({"token": token[0].key, "user": UserSerializer(user).data})


@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=serializer.data['username'])
        # Automatic hashing with set_password
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({"token": token.key, "user": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def test_token(request):
    return Response({})
