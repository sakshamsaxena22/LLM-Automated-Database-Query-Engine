"""
Tests for user login — existing data, wrong credentials, edge cases.

Covers: successful login, wrong password, non-existent user,
deactivated account, user_id correctness, JWT claims,
register→login round-trip, and case-sensitive email.
"""

from __future__ import annotations

import pytest
from jose import jwt
from fastapi import HTTPException

from app.core.config import settings


# ── 1. Login with correct credentials (existing user) ────────────────

@pytest.mark.asyncio
async def test_login_existing_user_success(auth_service, seeded_user):
    """Login with correct email/password returns tokens."""
    result = await auth_service.login(
        email=seeded_user["email"],
        password=seeded_user["password"],
    )

    assert "access_token" in result
    assert "refresh_token" in result
    assert result["token_type"] == "bearer"
    assert result["user_id"] == seeded_user["user_id"]


# ── 2. Wrong password → 401 ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_login_wrong_password_401(auth_service, seeded_user):
    """Wrong password must raise HTTP 401."""
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.login(
            email=seeded_user["email"],
            password="totallyWrongPassword",
        )
    assert exc_info.value.status_code == 401
    assert "invalid" in exc_info.value.detail.lower()


# ── 3. Non-existent email → 401 ──────────────────────────────────────

@pytest.mark.asyncio
async def test_login_nonexistent_email_401(auth_service):
    """Login with an email that was never registered must raise 401."""
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.login(
            email="ghost@nowhere.com",
            password="anything",
        )
    assert exc_info.value.status_code == 401


# ── 4. Deactivated account → 403 ─────────────────────────────────────

@pytest.mark.asyncio
async def test_login_deactivated_account_403(auth_service, seeded_user, user_repo):
    """A user with is_active=False must get HTTP 403 on login."""
    # Deactivate the seeded user
    await user_repo.update(seeded_user["user_id"], {"is_active": False})

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.login(
            email=seeded_user["email"],
            password=seeded_user["password"],
        )
    assert exc_info.value.status_code == 403
    assert "deactivated" in exc_info.value.detail.lower()


# ── 5. Returned user_id matches DB record ────────────────────────────

@pytest.mark.asyncio
async def test_login_returns_correct_user_id(auth_service, seeded_user):
    """The user_id in the login response must match the registered user."""
    result = await auth_service.login(
        email=seeded_user["email"],
        password=seeded_user["password"],
    )
    assert result["user_id"] == seeded_user["user_id"]


# ── 6. JWT claims are correct ────────────────────────────────────────

@pytest.mark.asyncio
async def test_login_token_contains_correct_claims(auth_service, seeded_user):
    """Decoded JWT must carry sub, email, role, org_id, type."""
    result = await auth_service.login(
        email=seeded_user["email"],
        password=seeded_user["password"],
    )

    payload = jwt.decode(
        result["access_token"],
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    assert payload["sub"] == seeded_user["user_id"]
    assert payload["email"] == seeded_user["email"]
    assert payload["role"] == "viewer"
    assert payload["org_id"] == seeded_user["org_id"]
    assert payload["type"] == "access"


# ── 7. Register then login round-trip ────────────────────────────────

@pytest.mark.asyncio
async def test_login_after_register_roundtrip(auth_service):
    """Register a new user, then immediately login with the same creds."""
    email = "roundtrip@example.com"
    password = "roundtripPass99"

    import asyncio
    reg = await auth_service.register(email=email, password=password)
    await asyncio.sleep(1)
    login = await auth_service.login(email=email, password=password)

    assert login["user_id"] == reg["user_id"]
    assert login["access_token"]  # non-empty
    # Tokens from login should differ from registration (new issuance)
    assert login["access_token"] != reg["access_token"]


# ── 8. Case-sensitive email ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_login_case_sensitive_email(auth_service, seeded_user):
    """Email lookup is case-sensitive — different case should fail."""
    upper_email = seeded_user["email"].upper()  # "EXISTING@EXAMPLE.COM"

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.login(
            email=upper_email,
            password=seeded_user["password"],
        )
    assert exc_info.value.status_code == 401
