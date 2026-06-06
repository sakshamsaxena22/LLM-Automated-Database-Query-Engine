"""
Shared pytest fixtures for auth tests.

Sets up env vars, FakeAdapter, UserRepository, and AuthService
so every test module gets a clean, isolated auth stack.
"""

import os

# ── Environment overrides (must happen before any app imports) ────────
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017/test_db")
os.environ.setdefault("GROQ_API_KEY", "dummy_key_for_tests")
os.environ.setdefault("DATABASE_NAME", "test_db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests")

import pytest
import pytest_asyncio

from tests.fake_adapter import FakeAdapter
from app.db.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService
from app.core.security import hash_password


@pytest.fixture
def fake_adapter():
    """Fresh in-memory adapter, reset per test."""
    adapter = FakeAdapter()
    yield adapter
    adapter.reset()


@pytest.fixture
def user_repo(fake_adapter):
    """UserRepository wired to the fake adapter."""
    return UserRepository(fake_adapter)


@pytest.fixture
def auth_service(user_repo):
    """AuthService wired to the fake user repo."""
    return AuthService(user_repo)


@pytest_asyncio.fixture
async def seeded_user(fake_adapter, user_repo, auth_service):
    """Pre-register a user and return their info for 'existing data' tests.

    Returns a dict with: user_id, email, password (plain), full_name, org_id
    """
    email = "existing@example.com"
    password = "securepass123"
    full_name = "Existing User"
    org_id = "org_001"

    result = await auth_service.register(
        email=email,
        password=password,
        full_name=full_name,
        org_id=org_id,
    )
    return {
        "user_id": result["user_id"],
        "email": email,
        "password": password,
        "full_name": full_name,
        "org_id": org_id,
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
    }
