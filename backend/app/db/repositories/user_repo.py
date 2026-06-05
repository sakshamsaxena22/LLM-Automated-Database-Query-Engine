"""
User repository — CRUD operations on the ``users`` collection.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.db.adapters.mongo_adapter import MongoAdapter

logger = logging.getLogger(__name__)

COLLECTION = "users"


class UserRepository:
    """Async data-access layer for user documents."""

    def __init__(self, adapter: MongoAdapter) -> None:
        self._adapter = adapter

    async def find_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        from bson import ObjectId

        try:
            return await self._adapter.find_one(COLLECTION, {"_id": ObjectId(user_id)})
        except Exception:
            return None

    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return await self._adapter.find_one(COLLECTION, {"email": email})

    async def create(self, user_data: Dict[str, Any]) -> str:
        user_data.setdefault("created_at", datetime.now(timezone.utc))
        user_data.setdefault("updated_at", datetime.now(timezone.utc))
        user_data.setdefault("is_active", True)
        user_data.setdefault("role", "viewer")
        doc_id = await self._adapter.insert_one(COLLECTION, user_data)
        logger.info("Created user %s", doc_id)
        return doc_id

    async def update(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        from bson import ObjectId

        update_data["updated_at"] = datetime.now(timezone.utc)
        return await self._adapter.update_one(
            COLLECTION, {"_id": ObjectId(user_id)}, update_data
        )

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 50,
        org_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        filters: Dict[str, Any] = {}
        if org_id:
            filters["org_id"] = org_id
        users = await self._adapter.find_many(
            COLLECTION, filters, sort=[("created_at", -1)], skip=skip, limit=limit
        )
        # Strip hashed_password from results
        for u in users:
            u.pop("hashed_password", None)
        return users

    async def count(self, org_id: Optional[str] = None) -> int:
        filters: Dict[str, Any] = {}
        if org_id:
            filters["org_id"] = org_id
        return await self._adapter.count(COLLECTION, filters)

    async def delete(self, user_id: str) -> bool:
        from bson import ObjectId

        return await self._adapter.delete_one(COLLECTION, {"_id": ObjectId(user_id)})
