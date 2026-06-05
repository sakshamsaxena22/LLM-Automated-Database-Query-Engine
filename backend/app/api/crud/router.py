"""
CRUD routes — generic collection-level CRUD operations.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query as QueryParam
from pydantic import BaseModel

from app.core.permissions import RoleChecker
from app.core.security import get_current_user
from app.db.session import get_database
from app.db.adapters.mongo_adapter import MongoAdapter
from app.db.repositories.audit_repo import AuditRepository
from app.services.crud_service import CrudService
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/crud", tags=["crud"])


class InsertDocumentRequest(BaseModel):
    document: Dict[str, Any]


class UpdateDocumentRequest(BaseModel):
    update: Dict[str, Any]


def _crud_service() -> CrudService:
    db = get_database()
    return CrudService(MongoAdapter(db))


def _audit_service() -> AuditService:
    db = get_database()
    return AuditService(AuditRepository(MongoAdapter(db)))


@router.get("/{collection}")
async def list_documents(
    collection: str,
    skip: int = QueryParam(0, ge=0),
    limit: int = QueryParam(50, ge=1, le=200),
    current_user: Dict[str, Any] = Depends(get_current_user),
    svc: CrudService = Depends(_crud_service),
):
    return await svc.list_documents(collection, skip=skip, limit=limit)


@router.get("/{collection}/{doc_id}")
async def get_document(
    collection: str,
    doc_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    svc: CrudService = Depends(_crud_service),
):
    return await svc.get_document(collection, doc_id)


@router.post("/{collection}", status_code=201)
async def insert_document(
    collection: str,
    body: InsertDocumentRequest,
    current_user: Dict[str, Any] = Depends(RoleChecker(["editor", "manager", "admin", "super_admin"])),
    svc: CrudService = Depends(_crud_service),
    audit: AuditService = Depends(_audit_service),
):
    result = await svc.insert_document(collection, body.document)
    await audit.log(
        user_id=current_user["sub"],
        org_id=current_user.get("org_id", ""),
        operation="insert",
        entity=collection,
        entity_id=result.get("inserted_id", ""),
        risk_level="medium",
    )
    return result


@router.put("/{collection}/{doc_id}")
async def update_document(
    collection: str,
    doc_id: str,
    body: UpdateDocumentRequest,
    current_user: Dict[str, Any] = Depends(RoleChecker(["editor", "manager", "admin", "super_admin"])),
    svc: CrudService = Depends(_crud_service),
    audit: AuditService = Depends(_audit_service),
):
    result = await svc.update_document(collection, doc_id, body.update)
    await audit.log(
        user_id=current_user["sub"],
        org_id=current_user.get("org_id", ""),
        operation="update",
        entity=collection,
        entity_id=doc_id,
        risk_level="medium",
    )
    return result


@router.delete("/{collection}/{doc_id}")
async def delete_document(
    collection: str,
    doc_id: str,
    current_user: Dict[str, Any] = Depends(RoleChecker(["manager", "admin", "super_admin"])),
    svc: CrudService = Depends(_crud_service),
    audit: AuditService = Depends(_audit_service),
):
    result = await svc.delete_document(collection, doc_id)
    await audit.log(
        user_id=current_user["sub"],
        org_id=current_user.get("org_id", ""),
        operation="delete",
        entity=collection,
        entity_id=doc_id,
        risk_level="high",
    )
    return result
