"""
Tests for user registration (create account) — new data & existing data.

Covers: successful registration, duplicate rejection, password hashing,
default role, org_id, JWT token validity, and edge cases.
"""

from __future__ import annotations

import pytest
from jose import jwt
from fastapi import HTTPException

from app.core.config import settings
from app.core.security import verify_password


# ── 1. Register a brand-new user ─────────────────────────────────────

@pytest.mark.asyncio
async def test_register_new_user(auth_service):
    """Registering a new user returns user_id, tokens, and token_type."""
    result = await auth_service.register(
        email="newuser@example.com",
        password="password123",
        full_name="New User",
    )

    assert "user_id" in result
    assert result["user_id"]  # non-empty
    assert "access_token" in result
    assert "refresh_token" in result
    assert result["token_type"] == "bearer"


# ── 2. Password is bcrypt-hashed, not stored in plain text ────────────

@pytest.mark.asyncio
async def test_register_stores_hashed_password(auth_service, user_repo):
    """The password stored in the DB must be bcrypt-hashed, not plaintext."""
    plain = "mysecretpassword"
    await auth_service.register(email="hash@example.com", password=plain)

    user = await user_repo.find_by_email("hash@example.com")
    assert user is not None
    # Must NOT be stored as plaintext
    assert user["hashed_password"] != plain
    # Must verify correctly via bcrypt
    assert verify_password(plain, user["hashed_password"]) is True


# ── 3. Default role is 'viewer' ──────────────────────────────────────

@pytest.mark.asyncio
async def test_register_default_role_viewer(auth_service, user_repo):
    """New users must default to the 'viewer' role."""
    await auth_service.register(email="role@example.com", password="password123")
    user = await user_repo.find_by_email("role@example.com")
    assert user["role"] == "viewer"


# ── 4. Register with org_id ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_with_org_id(auth_service, user_repo):
    """org_id should be persisted when provided."""
    await auth_service.register(
        email="org@example.com",
        password="password123",
        org_id="org_test_42",
    )
    user = await user_repo.find_by_email("org@example.com")
    assert user["org_id"] == "org_test_42"


# ── 5. Duplicate email is rejected with HTTP 409 ─────────────────────

@pytest.mark.asyncio
async def test_register_duplicate_email_409(auth_service):
    """Registering the same email twice must raise HTTP 409 Conflict."""
    await auth_service.register(email="dup@example.com", password="password123")

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.register(email="dup@example.com", password="otherpass")

    assert exc_info.value.status_code == 409
    assert "already registered" in exc_info.value.detail.lower()


# ── 6. Returned tokens are valid JWTs with correct claims ────────────

@pytest.mark.asyncio
async def test_register_tokens_are_valid_jwt(auth_service):
    """access_token and refresh_token must decode with correct claims."""
    result = await auth_service.register(
        email="jwt@example.com",
        password="password123",
        full_name="JWT User",
    )

    # Decode access token
    access_payload = jwt.decode(
        result["access_token"],
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    assert access_payload["sub"] == result["user_id"]
    assert access_payload["email"] == "jwt@example.com"
    assert access_payload["role"] == "viewer"
    assert access_payload["type"] == "access"

    # Decode refresh token
    refresh_payload = jwt.decode(
        result["refresh_token"],
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    assert refresh_payload["sub"] == result["user_id"]
    assert refresh_payload["type"] == "refresh"


# ── 7. Empty full_name is accepted ───────────────────────────────────

@pytest.mark.asyncio
async def test_register_empty_full_name_allowed(auth_service, user_repo):
    """full_name can be an empty string (it's optional)."""
    result = await auth_service.register(
        email="noname@example.com",
        password="password123",
        full_name="",
    )
    assert result["user_id"]

    user = await user_repo.find_by_email("noname@example.com")
    assert user["full_name"] == ""


# ── 8. User is_active defaults to True ───────────────────────────────

@pytest.mark.asyncio
async def test_register_user_is_active_by_default(auth_service, user_repo):
    """Newly registered users must be active by default."""
    await auth_service.register(email="active@example.com", password="password123")
    user = await user_repo.find_by_email("active@example.com")
    assert user["is_active"] is True
