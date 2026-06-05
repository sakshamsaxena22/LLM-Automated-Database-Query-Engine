"""
MongoDB adapter — concrete implementation of ``BaseDBAdapter`` using Motor.

Handles ObjectId serialisation transparently: every document returned has
its ``_id`` converted to a string.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.adapters.base import BaseDBAdapter

logger = logging.getLogger(__name__)


def _serialise_id(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert ``_id`` from ``ObjectId`` to ``str`` in-place and return doc."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


class MongoAdapter(BaseDBAdapter):
    """Async MongoDB adapter backed by Motor."""

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self._db = database

    # ── Read ──────────────────────────────────────────────────────────

    async def find_one(
        self,
        collection: str,
        filters: Dict[str, Any],
        projection: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        doc = await self._db[collection].find_one(filters, projection)
        return _serialise_id(doc) if doc else None

    async def find_many(
        self,
        collection: str,
        filters: Dict[str, Any],
        projection: Optional[Dict[str, Any]] = None,
        sort: Optional[List[Tuple[str, int]]] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[Dict[str, Any]]:
        cursor = self._db[collection].find(filters, projection)
        if sort:
            cursor = cursor.sort(sort)
        cursor = cursor.skip(skip).limit(limit)
        results = await cursor.to_list(length=limit)
        return [_serialise_id(d) for d in results]

    # ── Create ────────────────────────────────────────────────────────

    async def insert_one(
        self,
        collection: str,
        document: Dict[str, Any],
    ) -> str:
        result = await self._db[collection].insert_one(document)
        return str(result.inserted_id)

    async def insert_many(
        self,
        collection: str,
        documents: List[Dict[str, Any]],
    ) -> List[str]:
        result = await self._db[collection].insert_many(documents)
        return [str(oid) for oid in result.inserted_ids]

    # ── Update ────────────────────────────────────────────────────────

    async def update_one(
        self,
        collection: str,
        filters: Dict[str, Any],
        update: Dict[str, Any],
    ) -> bool:
        # Ensure update uses $set if no operator present
        if not any(k.startswith("$") for k in update):
            update = {"$set": update}
        result = await self._db[collection].update_one(filters, update)
        return result.modified_count > 0

    async def update_many(
        self,
        collection: str,
        filters: Dict[str, Any],
        update: Dict[str, Any],
    ) -> int:
        if not any(k.startswith("$") for k in update):
            update = {"$set": update}
        result = await self._db[collection].update_many(filters, update)
        return result.modified_count

    # ── Delete ────────────────────────────────────────────────────────

    async def delete_one(
        self,
        collection: str,
        filters: Dict[str, Any],
    ) -> bool:
        result = await self._db[collection].delete_one(filters)
        return result.deleted_count > 0

    async def delete_many(
        self,
        collection: str,
        filters: Dict[str, Any],
    ) -> int:
        result = await self._db[collection].delete_many(filters)
        return result.deleted_count

    # ── Aggregation ───────────────────────────────────────────────────

    async def aggregate(
        self,
        collection: str,
        pipeline: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        cursor = self._db[collection].aggregate(pipeline)
        results = await cursor.to_list(length=1000)
        return [_serialise_id(d) for d in results]

    # ── Count ─────────────────────────────────────────────────────────

    async def count(
        self,
        collection: str,
        filters: Dict[str, Any],
    ) -> int:
        return await self._db[collection].count_documents(filters)
