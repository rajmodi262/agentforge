"""Tests for Auth API endpoints."""


def test_register_success(client):
    """Test successful user registration."""
    response = client.post("/api/v1/auth/register", json={
        "email": "newuser@test.com",
        "password": "SecurePass123",
        "name": "New User",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client):
    """Test that duplicate email registration fails."""
    user_data = {"email": "dupe@test.com", "password": "SecurePass123"}
    client.post("/api/v1/auth/register", json=user_data)
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_register_weak_password(client):
    """Test that weak passwords are rejected."""
    response = client.post("/api/v1/auth/register", json={
        "email": "weak@test.com",
        "password": "short",
    })
    assert response.status_code == 422  # Pydantic validation error


def test_register_password_no_number(client):
    """Test that password without numbers is rejected."""
    response = client.post("/api/v1/auth/register", json={
        "email": "nonum@test.com",
        "password": "OnlyLettersHere",
    })
    assert response.status_code == 422


def test_login_success(client):
    """Test successful login."""
    # Register first
    client.post("/api/v1/auth/register", json={
        "email": "login@test.com",
        "password": "LoginPass123",
    })
    # Login
    response = client.post("/api/v1/auth/login", json={
        "email": "login@test.com",
        "password": "LoginPass123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    """Test login with wrong password."""
    client.post("/api/v1/auth/register", json={
        "email": "wrong@test.com",
        "password": "CorrectPass123",
    })
    response = client.post("/api/v1/auth/login", json={
        "email": "wrong@test.com",
        "password": "WrongPass456",
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Test login with email that doesn't exist."""
    response = client.post("/api/v1/auth/login", json={
        "email": "ghost@test.com",
        "password": "DoesntMatter1",
    })
    assert response.status_code == 401


def test_get_me_authenticated(client, auth_headers):
    """Test /me endpoint with valid token."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@startupos.ai"
    assert data["name"] == "Test User"


def test_get_me_unauthenticated(client):
    """Test /me endpoint without token returns 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_me_invalid_token(client):
    """Test /me endpoint with bad token returns 401."""
    response = client.get("/api/v1/auth/me", headers={
        "Authorization": "Bearer invalid-token-here"
    })
    assert response.status_code == 401


def test_login_email_case_insensitive(client):
    """Test that email login is case-insensitive."""
    client.post("/api/v1/auth/register", json={
        "email": "UPPER@test.com",
        "password": "CaseTest123",
    })
    response = client.post("/api/v1/auth/login", json={
        "email": "upper@test.com",
        "password": "CaseTest123",
    })
    assert response.status_code == 200
