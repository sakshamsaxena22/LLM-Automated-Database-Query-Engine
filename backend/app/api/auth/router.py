"""
Auth routes — register, login, refresh, me.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.core.security import get_current_user
from app.db.session import get_database
from app.db.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService

from app.db.adapters.mongo_adapter import MongoAdapter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


# ── Request / Response schemas ────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field("", max_length=120)
    org_id: str = ""


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    user_id: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ── Dependency ────────────────────────────────────────────────────────

def _auth_service() -> AuthService:
    db = get_database()
    adapter = MongoAdapter(db)
    return AuthService(UserRepository(adapter))


# ── Endpoints ─────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, svc: AuthService = Depends(_auth_service)):
    result = await svc.register(
        email=body.email,
        password=body.password,
        full_name=body.full_name,
        org_id=body.org_id,
    )
    return result


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, svc: AuthService = Depends(_auth_service)):
    result = await svc.login(email=body.email, password=body.password)
    return result


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, svc: AuthService = Depends(_auth_service)):
    result = await svc.refresh(body.refresh_token)
    return result


@router.get("/me")
async def me(
    current_user: Dict[str, Any] = Depends(get_current_user),
    svc: AuthService = Depends(_auth_service),
):
    return await svc.get_me(current_user["sub"])
