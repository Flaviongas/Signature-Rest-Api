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
    response = check_admin_status("5f576384a4af9d36bda6f60fd9e3e9238bd79fa3", "admin")
    print(response)
    assert response.json().get('isAdmin') == True

def test_is_admin_invalid():
    # Test case 2: Non-admin account
    response = check_admin_status("88c8753b9cbc97b5621198bc9161722b8fb36b75", "d")
    assert response.json().get('isAdmin') == False

