import re
from validate_email import validate_email
import socket
import dns.resolver
from Asistencia.settings import EMAIL_ADDRESS, EMAIL_APP_PASSWORD
from signature.utils import generate_email_text
from .models import Major, Subject, Student
from rest_framework import viewsets, status
from .serializers import MajorSerializer, SubjectSerializer, StudentSerializer, UserSerializer, SubjectEnrollmentSerializer, UnenrollSubjectSerializer, DeleteStudentSerializer, CreateStudentSerializer, UpdateStudentSerializer
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
import smtplib
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

User = get_user_model()  # This gets your custom PermissionUser
SMPTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587


class StudentViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    # below are the actions to create, delete and get students
    @action(detail=False, methods=['POST'], url_path='create-student')
    def create_student(self, request):
        try:
            serializer = CreateStudentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'status': 'Estudiante creado'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['POST'], url_path='get-student-bymajor')
    def get_student_bymajor(self, request):
        try:
            
            major_id = request.data.get('major_id')
            if not major_id:
                return Response({'error': 'La carrera no existe'}, status=status.HTTP_400_BAD_REQUEST)

            students = Student.objects.filter(major_id=major_id)
            serializer = self.get_serializer(students, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['DELETE'], url_path='delete-student')
    def delete_student(self, request):
        try:
            serializer = DeleteStudentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'status': 'Estudiante borrado'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['PUT'], url_path='update-student')
    def update_student(self, request):
        try:
            serializer = UpdateStudentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'status': 'Estudiante actualizado'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Below are the actions to add, remove and update subjects for a student
    @action(detail=False, methods=['POST'], url_path='add-subject')
    def add_subject(self, request):
        try:
            serializer = SubjectEnrollmentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'status': 'subject added'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['DELETE'], url_path='remove-subject')
    def unregister_subject(self, request):
        try:
            serializer = UnenrollSubjectSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'status': 'subject removed'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


        
        
class MajorViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = Major.objects.all()
    serializer_class = MajorSerializer

    def get_object(self):
        instance = super().get_object()

        self.request.META['RESOURCE_NAME'] = getattr(instance, 'name', str(instance))
        return instance

    def perform_create(self, serializer):
        major = serializer.save()
        self.request._resource_name = major.name

    @action(detail=False, methods=["GET"])
    def getMajors(self, request):
        queryset = super().get_queryset()
        majors = [{"id": major.id, "name": major.name}
                  for major in queryset]
        return Response(majors)
    
        

class SubjectViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication, )
    queryset = Subject.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = SubjectSerializer

    def get_object(self):
        instance = super().get_object()

        self.request.META['RESOURCE_NAME'] = getattr(instance, 'name', str(instance))
        return instance

    def perform_create(self, serializer):
        subject = serializer.save()
        self.request.META['RESOURCE_NAME'] = subject.name


class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def perform_create(self, serializer):
        user = serializer.save()
        Token.objects.get_or_create(user=user)
        
         # Guardar el nombre del nuevo recurso
        self.request._resource_name = user.username

    def get_object(self):
        instance = super().get_object()

        # Guardar el nombre en el request (solo si no existe aún)
        self.request.META['RESOURCE_NAME'] = getattr(instance, 'name', str(instance))
        return instance

       
        

@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response({"error": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)
    token, _ = Token.objects.get_or_create(user=user)

    serializer = UserSerializer(instance=user)

    return Response({"token": token.key, "user": serializer.data})


@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=serializer.data['username'])
        user.set_password(request.data['password'])
        if 'majors' in request.data:     
            majors = request.data['majors']
            for major in majors:
                major_obj = Major.objects.get(id=major)
                user.majors.add(major_obj)
        user.save()
        token = Token.objects.create(user=user)
        return Response({"token": token.key, "user": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response({"passed for {}".format(request.user.username)})


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def isAdmin(request):
    print(request)
    user = get_object_or_404(User, username=request.data['username'])
    print(user)
    return Response({"isAdmin": user.is_superuser})


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def sendEmail(request):
    filename = request.POST['filename']
    recipient = request.POST['email']
    subject = request.POST['subject']
    excel = request.FILES['file']

    match = re.match(r"[^@]+@[^@]+\.[^@]+", recipient)
    if match == None:
        return Response({"error": "Email inválido"}, status=status.HTTP_400_BAD_REQUEST)

    email_domain = recipient.split('@')[1]

    is_valid = validate_email(
        email_address=recipient,
        check_format=True,
        check_blacklist=True,
        check_dns=True,
        dns_timeout=10,
        check_smtp=True,
        smtp_timeout=10,
        smtp_helo_host=email_domain,
        smtp_from_address=EMAIL_ADDRESS,
        smtp_skip_tls=False,
        smtp_tls_context=None,
        smtp_debug=False)

    
    if is_valid:
        email = MIMEMultipart()
        email['From'] = EMAIL_ADDRESS
        email['To'] = recipient
        email['Subject'] = filename
        email.attach(MIMEText(generate_email_text(filename,subject), 'plain'))

        with smtplib.SMTP(SMPTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
            excel_data = excel.read()
            part = MIMEApplication(excel_data, Name=filename)
            part['Content-Disposition'] = f'attachment; filename="{filename}"'
            email.attach(part)
            server.sendmail(EMAIL_ADDRESS, recipient, email.as_string())
        return Response(200)
    else:
        return Response({"error": "El email ingresado no existe"}, status=status.HTTP_400_BAD_REQUEST)
