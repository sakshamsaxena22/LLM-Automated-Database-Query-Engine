"""
User management service — list, get, update users.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status

from app.db.repositories.user_repo import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    """Business logic for user management (admin operations)."""

    def __init__(self, user_repo: UserRepository) -> None:
        self._repo = user_repo

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 50,
        org_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        users = await self._repo.list_all(skip=skip, limit=limit, org_id=org_id)
        total = await self._repo.count(org_id=org_id)
        return {"users": users, "total": total, "skip": skip, "limit": limit}

    async def get_user(self, user_id: str) -> Dict[str, Any]:
        user = await self._repo.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        user.pop("hashed_password", None)
        return user

    async def update_user(
        self, user_id: str, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Prevent updating sensitive fields directly
        update_data.pop("hashed_password", None)
        update_data.pop("_id", None)

        success = await self._repo.update(user_id, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or no changes applied",
            )
        logger.info("Updated user %s with fields: %s", user_id, list(update_data.keys()))
        return await self.get_user(user_id)
