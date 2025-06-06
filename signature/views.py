import re
import pandas as pd
from validate_email import validate_email
import socket
import dns.resolver
from Asistencia.settings import EMAIL_ADDRESS, EMAIL_APP_PASSWORD
from signature.utils import generate_email_text, digito_verificador
from .models import Major, Subject, Student, MajorCode
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
from numpy import dot

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
                return Response({'status': 'Estudiante borrado'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

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

        self.request.META['RESOURCE_NAME'] = getattr(
            instance, 'name', str(instance))
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

        self.request.META['RESOURCE_NAME'] = getattr(
            instance, 'name', str(instance))
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
        self.request.META['RESOURCE_NAME'] = getattr(
            instance, 'name', str(instance))
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


# Podriamos usar esta ruta para deslogear al usuario en caso de que se borre su cuenta
@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def userExists(request):
    print(request)
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
def uploadStudentSubjectCSV(request):
    print("Uploading CSV file")

    expected_columns = ['Rut']

    csv = request.FILES['file']
    major_id = request.data.get('major_id')
    subject_id = request.data.get('subject_id')
    print(f"Major ID: {major_id}")
    print(f"Subject ID: {subject_id}")
    df = pd.read_csv(csv)

    columns = df.columns.tolist()
    print(f"CSV columns: {columns}")

    if not all(col in columns for col in expected_columns):
        print("CSV file does not contain the expected columns")
        return Response({"error": "El CSV no contiene las columnas correctas"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        print("CSV file contains the expected columns")

    for col in columns:
        if df[col].isnull().any():
            print(f"Column {col} contains null values")
            return Response({"error": f"La columna {col} no puede tener valores nulos"}, status=status.HTTP_400_BAD_REQUEST)

    students = df['Rut'].drop_duplicates().tolist()

    if len(students) > 2000:
        return Response({"error": "El archivo CSV no puede tener más de 2000 alumnos"}, status=status.HTTP_400_BAD_REQUEST)

    if not major_id:
        print(f"Major is empty ")
        return Response({"error": "El ID de la carrera no puede estar vacío"}, status=status.HTTP_400_BAD_REQUEST)
    if not subject_id:
        print(f"Subject is empty ")
        return Response({"error": "El ID de la asignatura no puede estar vacío"}, status=status.HTTP_400_BAD_REQUEST)

    for rut in students:
        found_student = None
        try:
            found_student = Student.objects.get(rut=rut)
            found_student_major = found_student.major.id
            if found_student_major != int(major_id):
                print(f"El estudiante {
                      found_student.first_name} no pertenece a la carrera")
                return Response({"error": f"El estudiante {found_student.first_name} no pertenece a la carrera"}, status=status.HTTP_400_BAD_REQUEST)
            print(f"Found student: {found_student.first_name}")
        except Student.DoesNotExist:
            print(f"Didn't find student {rut} by rut")
            return Response({"error": f"El estudiante con RUT {rut} no fue encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubjectEnrollmentSerializer(
            data={'student_id': found_student.id, 'subject_id': subject_id})
        if serializer.is_valid():
            serializer.save()
            print(f"Student {found_student.first_name} enrolled in subject")
        else:
            print(f"Error creating subject enrollment for student {
                  rut}: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"status": "CSV file uploaded successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def uploadStudentCSV(request):
    print("Uploading CSV file")

    expected_columns = ['Rut', 'Nombre', 'Segundo_Nombre',
                        'Apellido', 'Segundo_Apellido']

    csv = request.FILES['file']
    major_id = request.data.get('major_id')
    print(f"Major ID: {major_id}")
    df = pd.read_csv(csv)

    columns = df.columns.tolist()

    print(f"CSV columns: {columns}")

    if not all(col in columns for col in expected_columns):
        print("CSV file does not contain the expected columns")
        return Response({"error": "El CSV no contiene las columnas correctas"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        print("CSV file contains the expected columns")

    for col in columns:
        if df[col].isnull().any():
            print(f"Column {col} contains null values")
            return Response({"error": f"La columna {col} no puede tener valores nulos"}, status=status.HTTP_400_BAD_REQUEST)
    if not pd.api.types.is_numeric_dtype(df['Rut']):
        print("Rut column contains non-numeric values")
        return Response({"error": "La columna Rut debe contener solo valores numéricos"}, status=status.HTTP_400_BAD_REQUEST)

    students = df['Rut'].drop_duplicates().tolist()

    if len(students) > 2000:
        return Response({"error": "El archivo CSV no puede tener más de 2000 alumnos"}, status=status.HTTP_400_BAD_REQUEST)

    if not major_id:
        print(f"Major is empty ")
        return Response({"error": "El ID de la carrera no puede estar vacío"}, status=status.HTTP_400_BAD_REQUEST)

    for student in students:
        print(f"Processing student: {student}")
        nombre = df[df['Rut'] ==
                    student]['Nombre'].drop_duplicates().tolist()[0].upper()
        if not nombre:
            print(f"Nombre is empty for student {student}")
            return Response({"error": f"El nombre del estudiante {student} no puede estar vacío"}, status=status.HTTP_400_BAD_REQUEST)
        print(f"Nombre: {nombre}")
        segundo_nombre = df[df['Rut'] ==
                            student]['Segundo_Nombre'].drop_duplicates().tolist()[0].upper()
        if not segundo_nombre:
            print(f"Segundo nombre is empty for student {student}")
            return Response({"error": f"El segundo nombre del estudiante {student} no puede estar vacío"}, status=status.HTTP_400_BAD_REQUEST)
        apellido = df[df['Rut'] ==
                      student]['Apellido'].drop_duplicates().tolist()[0].upper()
        if not apellido:
            print(f"Apellido is empty for student {student}")
            return Response({"error": f"El apellido del estudiante {student} no puede estar vacío"}, status=status.HTTP_400_BAD_REQUEST)
        segundo_apellido = df[df['Rut'] ==
                              student]['Segundo_Apellido'].drop_duplicates().tolist()[0].upper()
        if not segundo_apellido:
            print(f"Segundo apellido is empty for student {student}")
            return Response({"error": f"El segundo apellido del estudiante {student} no puede estar vacío"}, status=status.HTTP_400_BAD_REQUEST)

        found_student = None
        try:
            found_student = Student.objects.get(rut=student)
            print(f"Found student: {found_student.first_name}")
            return Response({"error": f"El estudiante {found_student.first_name} ya existe"}, status=status.HTTP_400_BAD_REQUEST)
        except Student.DoesNotExist:
            print(f"Didn't find student {student} by rut")
        print(digito_verificador(student))
        new_student = {
            "rut": student,
            "dv": str(digito_verificador(student)),
            "first_name": nombre if nombre else "",
            "second_name": segundo_nombre if segundo_nombre else "",
            "last_name": apellido if apellido else "",
            "second_last_name": segundo_apellido[0] if segundo_apellido else "",
            "major_id": major_id
        }
        serializer = CreateStudentSerializer(data=new_student)
        if serializer.is_valid():
            serializer.save()
            print(f"Student {serializer.data['first_name']} created")
        else:
            print(f"Error creating student {student}: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"status": "Archivo CSV subido correctamente"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def uploadUserCSV(request):
    print("Uploading CSV file")

    expected_columns = ['Usuario', 'Contraseña',
                        'Nombre_Carrera', 'Codigo_Carrera']

    csv = request.FILES['file']
    df = pd.read_csv(csv)

    columns = df.columns.tolist()

    if not all(col in columns for col in expected_columns):
        print("CSV file does not contain the expected columns")
        return Response({"error": "El CSV no contiene las columnas correctas"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        print("CSV file contains the expected columns")

    for col in columns:
        if df[col].isnull().any():
            print(f"Column {col} contains null values")
            return Response({"error": f"La columna {col} no puede tener valores nulos"}, status=status.HTTP_400_BAD_REQUEST)

    users = df['Usuario'].drop_duplicates().tolist()

    if len(users) > 2000:
        return Response({"error": "El archivo CSV no puede tener más de 2000 usuarios"}, status=status.HTTP_400_BAD_REQUEST)

    for user in users:
        print(f"Processing user: {user}")
        password = df[df['Usuario'] ==
                      user]['Contraseña'].drop_duplicates().tolist()
        majors = df[df['Usuario'] ==
                    user]['Nombre_Carrera'].drop_duplicates().tolist()
        major_codes = df[df['Usuario'] ==
                         user]['Codigo_Carrera'].drop_duplicates().tolist()

        found_majors = []

        for major, code in zip(majors, major_codes):
            found = False
            try:
                major_obj = Major.objects.get(name=major.upper())
                if major_obj:
                    found_majors.append(major_obj.id)
                    found = True
                    print(f"Found major: {major_obj.name} by name")
            except Major.DoesNotExist:
                print(f"Didn't find major {major} by name")

            if not found:
                try:
                    major_obj_code = MajorCode.objects.get(code=code)

                    if major_obj_code:
                        found_majors.append(major_obj_code.major.id)
                        print(f"Found major {major} with code {code}")
                except MajorCode.DoesNotExist:
                    print(f"Major {major} with code {code} does not exist")
                    return Response({"error": f"Major {major} with code {code} does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(
            data={"username": user, "password": password[0], "major_ids": found_majors})
        if serializer.is_valid():
            user_instance = serializer.save()
            print(f"User {user_instance.username} created")
        else:
            print(f"Error creating user {user}: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"status": "Archivo CSV subido correctamente"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def sendEmail(request):
    filename = request.POST['filename']
    recipient = request.POST['email']
    subject = request.POST['subject']
    excel = request.FILES['file']
    print(f"filename: {filename}")
    print(f"recipient: {recipient}")
    print(f"subject: {subject}")

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
        email.attach(MIMEText(generate_email_text(filename, subject), 'plain'))

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
