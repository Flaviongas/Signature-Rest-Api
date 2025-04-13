import requests

def login(username, password):
    url = "http://localhost:8000/login/"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(url, json=data, headers=headers)
    return response

def test_login_valid():
    # Test case 1: Valid credentials
    response = login("flavio02", "signature")
    assert response.status_code == 200
    assert "token" in response.json()

def test_login_invalid():
    # Test case 2: Invalid credentials
    response = login("invalid_user", "invalid_password")
    assert response.json().get('detail') == "No User matches the given query."
    assert "detail" in response.json()
