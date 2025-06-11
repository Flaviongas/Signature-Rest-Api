from io import StringIO
import pandas as pd
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from signature.models import Student


@pytest.mark.django_db
def test_upload_student_csv_valid(auth_client, test_major):
    client, user = auth_client
    rut = "12345678"

    csv_data = (
        "Rut,Nombre,Segundo_Nombre,Apellido,Segundo_Apellido\n"
        f"{rut},Juan,Pablo,González,Pérez\n"
    )
    csv_file = SimpleUploadedFile(
        "test.csv", csv_data.encode(), content_type="text/csv")

    response = client.post(
        "/uploadStudentCSV/",
        # Major.objects.create(name='Test Major', faculty='Test Faculty')
        {"file": csv_file, "major_id": test_major.id},
        format="multipart"
    )

    assert response.status_code == 204
    assert Student.objects.filter(rut=rut).exists()


@pytest.mark.django_db
def test_upload_student_csv_missing_columns(auth_client, test_major):
    client, _ = auth_client
    csv_data = (
        "Rut,Nombre,Apellido,Segundo_Apellido\n"  # Falta 'Segundo_Nombre'
        "12345678,Juan,González,Pérez\n"
    )
    file = SimpleUploadedFile("missing_column.csv",
                              csv_data.encode(), content_type="text/csv")
    response = client.post(
        "/uploadStudentCSV/", {"file": file, "major_id": test_major.id}, format="multipart")

    assert response.status_code == 400
    assert "columnas correctas" in response.json()["error"]


@pytest.mark.django_db
def test_upload_student_csv_too_many(auth_client, test_major):
    client, _ = auth_client
    df = pd.DataFrame({
        "Rut": [str(10000000 + i) for i in range(2001)],
        "Nombre": ["Juan"] * 2001,
        "Segundo_Nombre": ["Pablo"] * 2001,
        "Apellido": ["González"] * 2001,
        "Segundo_Apellido": ["Pérez"] * 2001,
    })
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    file = SimpleUploadedFile(
        "too_many.csv", csv_buffer.getvalue().encode(), content_type="text/csv")

    response = client.post(
        "/uploadStudentCSV/", {"file": file, "major_id": test_major.id}, format="multipart")

    assert response.status_code == 400
    assert "más de 2000" in response.json()["error"]


@pytest.mark.django_db
def test_upload_subject_csv_student_not_found(auth_client, test_major):
    client, _ = auth_client
    csv_data = "Rut\n99999999\n"  # RUT inexistente

    file = SimpleUploadedFile("student_not_found.csv",
                              csv_data.encode(), content_type="text/csv")
    response = client.post("/uploadStudentSubjectCSV/", {
        "file": file,
        "major_id": test_major.id,
        "subject_id": 1
    }, format="multipart")

    assert response.status_code == 404
    assert "no fue encontrado" in response.json()["error"]


@pytest.mark.django_db
def test_upload_user_csv_major_not_found(auth_client):
    client, _ = auth_client
    csv_data = (
        "Usuario,Contraseña,Nombre_Carrera,Codigo_Carrera\n"
        "usuario1,pass123,Carrera Inexistente,COD999\n"
    )
    file = SimpleUploadedFile(
        "user_major_not_found.csv", csv_data.encode(), content_type="text/csv")
    response = client.post(
        "/uploadUserCSV/", {"file": file}, format="multipart")

    assert response.status_code == 400
    assert "does not exist" in response.json()["error"]


@pytest.mark.django_db
def test_upload_student_csv_missing_major_id(auth_client):
    client, _ = auth_client
    csv_data = "Rut,Nombre,Segundo_Nombre,Apellido,Segundo_Apellido\n12345678,Juan,Carlos,López,Mora\n"
    file = SimpleUploadedFile(
        "no_major.csv", csv_data.encode(), content_type="text/csv")

    response = client.post("/uploadStudentCSV/",
                           {"file": file}, format="multipart")
    assert response.status_code == 400
    assert "carrera no puede estar vacío" in response.json()["error"]


@pytest.mark.django_db
def test_upload_subject_csv_missing_subject_id(auth_client, test_major):
    test_student = Student.objects.create(
        rut="234123432", dv="0", first_name="Juan", last_name="López", major=test_major)
    client, _ = auth_client
    csv_data = f"Rut\n{test_student.rut}\n"
    file = SimpleUploadedFile(
        "no_subject.csv", csv_data.encode(), content_type="text/csv")

    response = client.post("/uploadStudentSubjectCSV/", {
        "file": file,
        "major_id": test_major.id
    }, format="multipart")

    assert response.status_code == 400
    assert "asignatura no puede estar vacío" in response.json()["error"]


@pytest.mark.django_db
def test_upload_student_csv_empty_first_name(auth_client, test_major):
    client, _ = auth_client
    csv_data = "Rut,Nombre,Segundo_Nombre,Apellido,Segundo_Apellido\n12345678,,Carlos,López,Mora\n"
    file = SimpleUploadedFile(
        "empty_name.csv", csv_data.encode(), content_type="text/csv")

    response = client.post(
        "/uploadStudentCSV/", {"file": file, "major_id": test_major.id}, format="multipart")
    assert response.status_code == 400


@pytest.mark.django_db
def test_upload_student_csv_invalid_rut_serializer(auth_client, test_major):
    client, _ = auth_client
    # Rut inválido que forzará error en el serializer
    csv_data = "Rut,Nombre,Segundo_Nombre,Apellido,Segundo_Apellido\nINVALIDO,Pedro,Andrés,Rojas,Salas\n"
    file = SimpleUploadedFile(
        "bad_rut.csv", csv_data.encode(), content_type="text/csv")

    response = client.post(
        "/uploadStudentCSV/", {"file": file, "major_id": test_major.id}, format="multipart")
    assert response.status_code == 400


@pytest.mark.django_db
def test_upload_student_csv_multiple(auth_client, test_major):
    client, _ = auth_client
    csv_data = (
        "Rut,Nombre,Segundo_Nombre,Apellido,Segundo_Apellido\n"
        "10000001,Juan,Pedro,López,Mora\n"
        "10000002,Marta,Elena,Salas,Gómez\n"
    )
    file = SimpleUploadedFile(
        "multi.csv", csv_data.encode(), content_type="text/csv")

    response = client.post(
        "/uploadStudentCSV/", {"file": file, "major_id": test_major.id}, format="multipart")
    assert response.status_code == 204
    assert Student.objects.filter(rut="10000001").exists()
    assert Student.objects.filter(rut="10000002").exists()


@pytest.mark.django_db
def test_upload_user_csv_multiple(auth_client, test_major):
    client, _ = auth_client
    csv_data = (
        "Usuario,Contraseña,Nombre_Carrera,Codigo_Carrera\n"
        f"juanito,clave123,Arquitectura,ARQUI_111\n"
        f"marcela,clave456,Informática,ICINF_111\n"
    )
    file = SimpleUploadedFile(
        "multi_user.csv", csv_data.encode(), content_type="text/csv")

    response = client.post(
        "/uploadUserCSV/", {"file": file}, format="multipart")
    assert response.status_code == 204


@pytest.mark.django_db
def test_upload_student_csv_unauthenticated():
    from rest_framework.test import APIClient
    client = APIClient()
    csv_data = "Rut,Nombre,Segundo_Nombre,Apellido,Segundo_Apellido\n12345678,Juan,Carlos,López,Mora\n"
    file = SimpleUploadedFile(
        "unauth.csv", csv_data.encode(), content_type="text/csv")

    response = client.post("/uploadStudentCSV/",
                           {"file": file, "major_id": 1}, format="multipart")
    assert response.status_code == 403 or response.status_code == 401
