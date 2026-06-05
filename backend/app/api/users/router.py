"""
User management routes — list, get, update users.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.core.permissions import RoleChecker
from app.core.security import get_current_user
from app.db.adapters.mongo_adapter import MongoAdapter
from app.db.session import get_database
from app.db.repositories.user_repo import UserRepository
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


def _user_service() -> UserService:
    db = get_database()
    return UserService(UserRepository(MongoAdapter(db)))


@router.get("/")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: Dict[str, Any] = Depends(RoleChecker(["admin", "super_admin"])),
    svc: UserService = Depends(_user_service),
):
    org_id = current_user.get("org_id", "")
    return await svc.list_users(skip=skip, limit=limit, org_id=org_id or None)


@router.get("/{user_id}")
async def get_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    svc: UserService = Depends(_user_service),
):
    return await svc.get_user(user_id)


@router.put("/{user_id}")
async def update_user(
    user_id: str,
    body: UpdateUserRequest,
    current_user: Dict[str, Any] = Depends(RoleChecker(["admin", "super_admin"])),
    svc: UserService = Depends(_user_service),
):
    update_data = body.model_dump(exclude_none=True)
    return await svc.update_user(user_id, update_data)
