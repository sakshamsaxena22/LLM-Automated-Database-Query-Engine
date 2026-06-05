"""
Authentication service — register, login, refresh, get-me.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException, status

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from app.db.repositories.user_repo import UserRepository

logger = logging.getLogger(__name__)


class AuthService:
    """Stateless authentication logic."""

    def __init__(self, user_repo: UserRepository) -> None:
        self._repo = user_repo

    async def register(
        self,
        email: str,
        password: str,
        full_name: str = "",
        org_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new user and return tokens."""
        existing = await self._repo.find_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        user_data = {
            "email": email,
            "hashed_password": hash_password(password),
            "full_name": full_name,
            "role": "viewer",
            "org_id": org_id or "",
        }
        user_id = await self._repo.create(user_data)
        logger.info("Registered user %s (%s)", user_id, email)

        tokens = self._issue_tokens(user_id, email, "viewer", org_id or "")
        return {"user_id": user_id, **tokens}

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate and return tokens."""
        user = await self._repo.find_by_email(email)
        if not user or not verify_password(password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )

        user_id = str(user["_id"])
        tokens = self._issue_tokens(
            user_id, user["email"], user.get("role", "viewer"), user.get("org_id", "")
        )
        logger.info("User %s logged in", user_id)
        return {"user_id": user_id, **tokens}

    async def refresh(self, refresh_token: str) -> Dict[str, Any]:
        """Issue new tokens from a valid refresh token."""
        payload = verify_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type — expected refresh token",
            )

        user_id = payload["sub"]
        user = await self._repo.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer exists",
            )

        tokens = self._issue_tokens(
            user_id, user["email"], user.get("role", "viewer"), user.get("org_id", "")
        )
        return {"user_id": user_id, **tokens}

    async def get_me(self, user_id: str) -> Dict[str, Any]:
        """Return the current user profile (without password)."""
        user = await self._repo.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        user.pop("hashed_password", None)
        return user

    # ── Private helpers ───────────────────────────────────────────────

    @staticmethod
    def _issue_tokens(
        user_id: str, email: str, role: str, org_id: str
    ) -> Dict[str, str]:
        token_data = {"sub": user_id, "email": email, "role": role, "org_id": org_id}
        return {
            "access_token": create_access_token(token_data),
            "refresh_token": create_refresh_token(token_data),
            "token_type": "bearer",
        }
