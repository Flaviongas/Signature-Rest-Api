import requests

def checkUser(token):
    url = "http://localhost:8000/userExists/"
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    return response

def test_token_admin():
    # Test token of admin account
    response = checkUser("5f576384a4af9d36bda6f60fd9e3e9238bd79fa3")
    print(response.json())
    assert response.json()[0].split()[0] == "passed"

def test_token_user():
    # Test token of any account
    response = checkUser("88c8753b9cbc97b5621198bc9161722b8fb36b75")
    print(response.json())
    assert response.json()[0].split()[0] == "passed"

def test_email():
    url = "http://localhost:8000/sendEmail/"
    token = "5f576384a4af9d36bda6f60fd9e3e9238bd79fa3"
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
    response = requests.post(url, headers=headers,data=data, files=files)
    print(response.status_code)

    print(response.json())

