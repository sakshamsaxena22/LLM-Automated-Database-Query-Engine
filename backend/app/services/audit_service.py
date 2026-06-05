"""
Audit service — log every significant operation (Section 11, Layer 7).

Records: user_id, org_id, operation, entity, timestamp, risk_level, status, details.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.db.repositories.audit_repo import AuditRepository

logger = logging.getLogger(__name__)


class AuditService:
    """Append-only audit trail for compliance and observability."""

    def __init__(self, audit_repo: AuditRepository) -> None:
        self._repo = audit_repo

    async def log(
        self,
        user_id: str,
        org_id: str,
        operation: str,
        entity: str,
        risk_level: str = "low",
        status: str = "success",
        entity_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: str = "",
    ) -> str:
        entry = {
            "user_id": user_id,
            "org_id": org_id,
            "operation": operation,
            "entity": entity,
            "entity_id": entity_id or "",
            "risk_level": risk_level,
            "status": status,
            "details": details or {},
            "ip_address": ip_address,
            "timestamp": datetime.now(timezone.utc),
        }
        log_id = await self._repo.insert(entry)
        logger.debug(
            "Audit log %s: user=%s op=%s entity=%s risk=%s",
            log_id,
            user_id,
            operation,
            entity,
            risk_level,
        )
        return log_id

    async def get_logs(
        self,
        org_id: Optional[str] = None,
        user_id: Optional[str] = None,
        operation: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Dict[str, Any]:
        filters: Dict[str, Any] = {}
        if org_id:
            filters["org_id"] = org_id
        if user_id:
            filters["user_id"] = user_id
        if operation:
            filters["operation"] = operation

        logs = await self._repo.find_many(filters=filters, skip=skip, limit=limit)
        total = await self._repo.count(filters=filters)
        return {"logs": logs, "total": total, "skip": skip, "limit": limit}
