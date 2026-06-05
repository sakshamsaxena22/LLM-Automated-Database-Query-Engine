"""
Organization repository — CRUD operations on the ``organizations`` collection.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.db.adapters.mongo_adapter import MongoAdapter

logger = logging.getLogger(__name__)

COLLECTION = "organizations"


class OrgRepository:
    """Async data-access layer for organization documents."""

    def __init__(self, adapter: MongoAdapter) -> None:
        self._adapter = adapter

    async def find_by_id(self, org_id: str) -> Optional[Dict[str, Any]]:
        from bson import ObjectId

        try:
            return await self._adapter.find_one(COLLECTION, {"_id": ObjectId(org_id)})
        except Exception:
            return None

    async def find_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        return await self._adapter.find_one(COLLECTION, {"slug": slug})

    async def create(self, org_data: Dict[str, Any]) -> str:
        org_data.setdefault("created_at", datetime.now(timezone.utc))
        org_data.setdefault("updated_at", datetime.now(timezone.utc))
        org_data.setdefault("is_active", True)
        org_data.setdefault("members", [])
        org_data.setdefault("allowed_databases", [])
        doc_id = await self._adapter.insert_one(COLLECTION, org_data)
        logger.info("Created organization %s", doc_id)
        return doc_id

    async def update(self, org_id: str, update_data: Dict[str, Any]) -> bool:
        from bson import ObjectId

        update_data["updated_at"] = datetime.now(timezone.utc)
        return await self._adapter.update_one(
            COLLECTION, {"_id": ObjectId(org_id)}, update_data
        )

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        return await self._adapter.find_many(
            COLLECTION, {}, sort=[("created_at", -1)], skip=skip, limit=limit
        )

    async def add_member(self, org_id: str, user_id: str) -> bool:
        from bson import ObjectId

        result = await self._adapter._db[COLLECTION].update_one(
            {"_id": ObjectId(org_id)},
            {
                "$addToSet": {"members": user_id},
                "$set": {"updated_at": datetime.now(timezone.utc)},
            },
        )
        return result.modified_count > 0

    async def count(self) -> int:
        return await self._adapter.count(COLLECTION, {})
