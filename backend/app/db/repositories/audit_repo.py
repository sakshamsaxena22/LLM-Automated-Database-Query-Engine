"""
Audit repository — append-only log storage in the ``audit_logs`` collection.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.db.adapters.mongo_adapter import MongoAdapter

logger = logging.getLogger(__name__)

COLLECTION = "audit_logs"


class AuditRepository:
    """Async data-access layer for audit-log documents."""

    def __init__(self, adapter: MongoAdapter) -> None:
        self._adapter = adapter

    async def insert(self, log_entry: Dict[str, Any]) -> str:
        log_entry.setdefault("timestamp", datetime.now(timezone.utc))
        return await self._adapter.insert_one(COLLECTION, log_entry)

    async def find_many(
        self,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        return await self._adapter.find_many(
            COLLECTION,
            filters or {},
            sort=[("timestamp", -1)],
            skip=skip,
            limit=limit,
        )

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        return await self._adapter.count(COLLECTION, filters or {})
