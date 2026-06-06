"""
Integration tests — full HTTP layer via FastAPI TestClient.

Uses dependency_overrides to inject FakeAdapter into the real app,
so the entire request→router→service→repo→adapter chain is tested
without MongoDB.
"""

from __future__ import annotations

import os

# Env overrides before any app imports
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017/test_db")
os.environ.setdefault("GROQ_API_KEY", "dummy_key_for_tests")
os.environ.setdefault("DATABASE_NAME", "test_db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests")

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.auth.router import _auth_service
from app.services.auth_service import AuthService
from app.db.repositories.user_repo import UserRepository
from tests.fake_adapter import FakeAdapter

# ── Shared adapter for the integration tests ─────────────────────────
_shared_adapter = FakeAdapter()


def _fake_auth_service() -> AuthService:
    return AuthService(UserRepository(_shared_adapter))


# Override the dependency in the FastAPI app
app.dependency_overrides[_auth_service] = _fake_auth_service

client = TestClient(app, raise_server_exceptions=False)

# Test user credentials
REG_EMAIL = "integration@example.com"
REG_PASSWORD = "integrationPass123"
REG_NAME = "Integration User"


@pytest.fixture(autouse=True)
def _reset_adapter():
    """Reset the fake adapter before each test."""
    _shared_adapter.reset()
    yield
    _shared_adapter.reset()


# ── 1. Register endpoint returns 201 ─────────────────────────────────

def test_register_endpoint_201():
    r = client.post("/api/v1/auth/register", json={
        "email": REG_EMAIL,
        "password": REG_PASSWORD,
        "full_name": REG_NAME,
    })
    assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.text}"
    data = r.json()
    assert "user_id" in data
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


# ── 2. Duplicate register → 409 ──────────────────────────────────────

def test_register_endpoint_duplicate_409():
    # First register
    client.post("/api/v1/auth/register", json={
        "email": REG_EMAIL,
        "password": REG_PASSWORD,
        "full_name": REG_NAME,
    })
    # Second register with same email
    r = client.post("/api/v1/auth/register", json={
        "email": REG_EMAIL,
        "password": "differentpass",
        "full_name": "Other Name",
    })
    assert r.status_code == 409


# ── 3. Login endpoint returns 200 ────────────────────────────────────

def test_login_endpoint_200():
    # Register first
    client.post("/api/v1/auth/register", json={
        "email": REG_EMAIL,
        "password": REG_PASSWORD,
        "full_name": REG_NAME,
    })
    # Login
    r = client.post("/api/v1/auth/login", json={
        "email": REG_EMAIL,
        "password": REG_PASSWORD,
    })
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


# ── 4. Login with wrong password → 401 ───────────────────────────────

def test_login_endpoint_wrong_password_401():
    # Register
    client.post("/api/v1/auth/register", json={
        "email": REG_EMAIL,
        "password": REG_PASSWORD,
        "full_name": REG_NAME,
    })
    # Login with wrong password
    r = client.post("/api/v1/auth/login", json={
        "email": REG_EMAIL,
        "password": "WRONG",
    })
    assert r.status_code == 401


# ── 5. GET /me with valid token → 200 ────────────────────────────────

def test_me_endpoint_with_valid_token():
    # Register and capture token
    reg = client.post("/api/v1/auth/register", json={
        "email": REG_EMAIL,
        "password": REG_PASSWORD,
        "full_name": REG_NAME,
    })
    token = reg.json()["access_token"]

    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert data["email"] == REG_EMAIL
    assert data["full_name"] == REG_NAME
    # Password must NOT be in the response
    assert "hashed_password" not in data


# ── 6. GET /me without token → 401 ───────────────────────────────────

def test_me_endpoint_without_token_401():
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401


# ── 7. Refresh endpoint → new tokens ─────────────────────────────────

def test_refresh_endpoint_200():
    # Register
    reg = client.post("/api/v1/auth/register", json={
        "email": REG_EMAIL,
        "password": REG_PASSWORD,
        "full_name": REG_NAME,
    })
    refresh_tok = reg.json()["refresh_token"]

    r = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_tok})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data


# ── 8. Using access_token as refresh → 401 ───────────────────────────

def test_refresh_with_access_token_fails():
    # Register
    reg = client.post("/api/v1/auth/register", json={
        "email": REG_EMAIL,
        "password": REG_PASSWORD,
        "full_name": REG_NAME,
    })
    access_tok = reg.json()["access_token"]

    # Try to refresh using the access token (wrong type)
    r = client.post("/api/v1/auth/refresh", json={"refresh_token": access_tok})
    assert r.status_code == 401
