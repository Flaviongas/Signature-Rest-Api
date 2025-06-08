import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from signature.models import Major, Subject
import requests
import os
import pytest
from django.core import mail
from django.urls import reverse

# Integration test


def dont_test_email():
    url = "http://localhost:8000/sendEmail/"
    token = "54297b8e32ea02ef3fe47d0c0b2595b8bb71a036"
    headers = {
        "Authorization": f"Token {token}",
    }
    data = {
        "filename": "REGISTROS DE ASISTENCIA - SAAC ( MARTES 14-05 ARQUITECTURA )",
        "email": "flaviojara58@gmail.com",
        "subject": "RAMO DE PRUEBA",
    }
    files = {
        "file": open("tests/REGISTROS DE ASISTENCIA - SAAC ( MARTES 14-05 ARQUITECTURA ).xlsx", "rb")
    }
    response = requests.post(url, headers=headers, data=data, files=files)
    assert response.status_code == 200
