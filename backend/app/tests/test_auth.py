from __future__ import annotations

from fastapi.testclient import TestClient


def register_payload(email: str = "founder@example.com") -> dict[str, object]:
    return {
        "email": email,
        "password": "password-123",
        "full_name": "Founder",
        "organization_name": "Founder Org",
    }


def test_register_creates_user_org_and_token(client: TestClient) -> None:
    response = client.post("/auth/register", json=register_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "founder@example.com"
    assert "password_hash" not in body["user"]
    assert body["organizations"][0]["name"] == "Founder Org"
    assert body["organizations"][0]["role"] == "owner"


def test_register_duplicate_email_fails(client: TestClient) -> None:
    assert client.post("/auth/register", json=register_payload()).status_code == 201

    response = client.post("/auth/register", json=register_payload())

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"


def test_login_succeeds_with_correct_password(client: TestClient) -> None:
    assert client.post("/auth/register", json=register_payload()).status_code == 201

    response = client.post("/auth/login", json={"email": "founder@example.com", "password": "password-123"})

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["user"]["email"] == "founder@example.com"


def test_login_fails_with_wrong_password(client: TestClient) -> None:
    assert client.post("/auth/register", json=register_payload()).status_code == 201

    response = client.post("/auth/login", json={"email": "founder@example.com", "password": "wrong-password"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_me_requires_token(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_returns_current_user(client: TestClient) -> None:
    register = client.post("/auth/register", json=register_payload())
    token = register.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["user"]["email"] == "founder@example.com"
    assert response.json()["organizations"][0]["role"] == "owner"
