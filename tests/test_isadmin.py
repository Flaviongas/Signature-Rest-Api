import requests

def check_admin_status(token, username):
    url = "http://localhost:8000/isAdmin/"
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    data = {
        "username": username
    }
    
    response = requests.post(url, json=data, headers=headers)
    return response

def test_is_admin_valid():
    # Test case 1: Admin account
    response = check_admin_status("f9eb392eb84de75065aa14e47ff758d22abac1ab", "admin")
    print(response)
    assert response.json().get('isAdmin') == True

def test_is_admin_invalid():
    # Test case 2: Non-admin account
    response = check_admin_status("91e30c9ee42ac2c6dea8adf3e66c78c0048f21ef", "flavio02")
    assert response.json().get('isAdmin') == False

