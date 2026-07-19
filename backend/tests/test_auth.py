import pytest

def test_signup_success(client):
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "securepassword123"
    }
    response = client.post("/api/auth/signup", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    # Verify cookie was set
    assert "access_token" in response.cookies

def test_signup_duplicate_email(client):
    payload = {
        "name": "User One",
        "email": "duplicate@example.com",
        "password": "password1"
    }
    response1 = client.post("/api/auth/signup", json=payload)
    assert response1.status_code == 200
    
    # Try creating with duplicate email
    response2 = client.post("/api/auth/signup", json=payload)
    assert response2.status_code == 400
    data = response2.json()
    assert "error" in data
    assert data["error"]["code"] == "EMAIL_ALREADY_EXISTS"

def test_login_success(client):
    # First sign up
    signup_payload = {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "password": "password123"
    }
    client.post("/api/auth/signup", json=signup_payload)
    
    # Try to login
    login_payload = {
        "email": "alice@example.com",
        "password": "password123"
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "access_token" in response.cookies

def test_login_invalid_credentials(client):
    login_payload = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "INVALID_CREDENTIALS"

def test_read_users_me_authenticated(client):
    signup_payload = {
        "name": "Bob Jones",
        "email": "bob@example.com",
        "password": "password123"
    }
    # Sign up returns cookie
    signup_resp = client.post("/api/auth/signup", json=signup_payload)
    token = signup_resp.json()["access_token"]
    
    # Try using Header authentication
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/me", headers=headers)
    assert response.status_code == 200, f"Header auth failed: {response.status_code} - {response.json()}"
    data = response.json()
    assert data["name"] == "Bob Jones"
    assert data["email"] == "bob@example.com"
    assert "id" in data

    # Try using Cookie authentication (without headers)
    response_cookie = client.get("/api/me") # client keeps cookie automatically
    assert response_cookie.status_code == 200
    assert response_cookie.json()["email"] == "bob@example.com"

def test_read_users_me_unauthenticated(client):
    response = client.get("/api/me")
    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "UNAUTHORIZED"

def test_logout_success(client):
    signup_payload = {
        "name": "Charlie",
        "email": "charlie@example.com",
        "password": "password123"
    }
    client.post("/api/auth/signup", json=signup_payload)
    
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    # Cookie should be deleted/expired
    # In fastapi response, delete_cookie sets the cookie value to "" and max-age to 0
    cookie = response.cookies.get("access_token")
    assert cookie == "" or cookie is None
