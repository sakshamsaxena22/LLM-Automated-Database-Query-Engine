"""
Audit log routes — view audit trail (Section 11 Layer 7).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query

from app.core.permissions import RoleChecker
from app.db.adapters.mongo_adapter import MongoAdapter
from app.db.session import get_database
from app.db.repositories.audit_repo import AuditRepository
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/audit", tags=["audit"])


def _audit_service() -> AuditService:
    db = get_database()
    return AuditService(AuditRepository(MongoAdapter(db)))


@router.get("/logs")
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    operation: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(RoleChecker(["admin", "super_admin"])),
    svc: AuditService = Depends(_audit_service),
):
    org_id = current_user.get("org_id", "")
    return await svc.get_logs(
        org_id=org_id or None,
        user_id=user_id,
        operation=operation,
        skip=skip,
        limit=limit,
    )
