"""
Organization management routes — create, list, get, update.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.core.permissions import RoleChecker
from app.core.security import get_current_user
from app.db.adapters.mongo_adapter import MongoAdapter
from app.db.session import get_database
from app.db.repositories.org_repo import OrgRepository
from app.services.org_service import OrgService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/organizations", tags=["organizations"])


class CreateOrgRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    allowed_databases: List[str] = []


class UpdateOrgRequest(BaseModel):
    name: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    allowed_databases: Optional[List[str]] = None


def _org_service() -> OrgService:
    db = get_database()
    return OrgService(OrgRepository(MongoAdapter(db)))


@router.get("/")
async def list_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: Dict[str, Any] = Depends(get_current_user),
    svc: OrgService = Depends(_org_service),
):
    return await svc.list_orgs(skip=skip, limit=limit)


@router.post("/", status_code=201)
async def create_organization(
    body: CreateOrgRequest,
    current_user: Dict[str, Any] = Depends(RoleChecker(["admin", "super_admin"])),
    svc: OrgService = Depends(_org_service),
):
    return await svc.create_org(
        name=body.name,
        owner_id=current_user["sub"],
        allowed_databases=body.allowed_databases,
    )


@router.get("/{org_id}")
async def get_organization(
    org_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    svc: OrgService = Depends(_org_service),
):
    return await svc.get_org(org_id)


@router.put("/{org_id}")
async def update_organization(
    org_id: str,
    body: UpdateOrgRequest,
    current_user: Dict[str, Any] = Depends(RoleChecker(["admin", "super_admin"])),
    svc: OrgService = Depends(_org_service),
):
    update_data = body.model_dump(exclude_none=True)
    return await svc.update_org(org_id, update_data)
