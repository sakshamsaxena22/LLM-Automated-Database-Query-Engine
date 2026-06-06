"""
In-memory fake database adapter for testing.

Implements BaseDBAdapter with a plain dict store so the full
AuthService → UserRepository → Adapter stack runs without MongoDB.
"""

from __future__ import annotations

import copy
import uuid
from typing import Any, Dict, List, Optional, Tuple

from app.db.adapters.base import BaseDBAdapter


class FakeAdapter(BaseDBAdapter):
    """Dict-backed adapter — every collection is a list of dicts."""

    def __init__(self) -> None:
        self._store: Dict[str, List[Dict[str, Any]]] = {}

    # ── helpers ───────────────────────────────────────────────────────

    def _col(self, name: str) -> List[Dict[str, Any]]:
        return self._store.setdefault(name, [])

    @staticmethod
    def _matches(doc: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        for key, value in filters.items():
            doc_val = doc.get(key)
            if key == "_id":
                if str(doc_val) != str(value):
                    return False
            else:
                if doc_val != value:
                    return False
        return True

    def reset(self) -> None:
        """Clear all collections — call between tests."""
        self._store.clear()

    # ── Read ──────────────────────────────────────────────────────────

    async def find_one(
        self,
        collection: str,
        filters: Dict[str, Any],
        projection: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        for doc in self._col(collection):
            if self._matches(doc, filters):
                return copy.deepcopy(doc)
        return None

    async def find_many(
        self,
        collection: str,
        filters: Dict[str, Any],
        projection: Optional[Dict[str, Any]] = None,
        sort: Optional[List[Tuple[str, int]]] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[Dict[str, Any]]:
        results = [
            copy.deepcopy(d) for d in self._col(collection) if self._matches(d, filters)
        ]
        if sort:
            for key, direction in reversed(sort):
                results.sort(key=lambda d: d.get(key, ""), reverse=(direction == -1))
        return results[skip : skip + limit]

    # ── Create ────────────────────────────────────────────────────────

    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        doc = copy.deepcopy(document)
        doc_id = str(uuid.uuid4().hex[:24])
        doc["_id"] = doc_id
        self._col(collection).append(doc)
        return doc_id

    async def insert_many(
        self, collection: str, documents: List[Dict[str, Any]]
    ) -> List[str]:
        ids = []
        for d in documents:
            ids.append(await self.insert_one(collection, d))
        return ids

    # ── Update ────────────────────────────────────────────────────────

    async def update_one(
        self, collection: str, filters: Dict[str, Any], update: Dict[str, Any]
    ) -> bool:
        # Handle $set operator
        if "$set" in update:
            update = update["$set"]
        elif any(k.startswith("$") for k in update):
            # unsupported operators — just use $set contents
            update = update.get("$set", {})

        for doc in self._col(collection):
            if self._matches(doc, filters):
                doc.update(update)
                return True
        return False

    async def update_many(
        self, collection: str, filters: Dict[str, Any], update: Dict[str, Any]
    ) -> int:
        if "$set" in update:
            update = update["$set"]
        count = 0
        for doc in self._col(collection):
            if self._matches(doc, filters):
                doc.update(update)
                count += 1
        return count

    # ── Delete ────────────────────────────────────────────────────────

    async def delete_one(self, collection: str, filters: Dict[str, Any]) -> bool:
        col = self._col(collection)
        for i, doc in enumerate(col):
            if self._matches(doc, filters):
                col.pop(i)
                return True
        return False

    async def delete_many(self, collection: str, filters: Dict[str, Any]) -> int:
        col = self._col(collection)
        to_remove = [d for d in col if self._matches(d, filters)]
        for d in to_remove:
            col.remove(d)
        return len(to_remove)

    # ── Aggregation ───────────────────────────────────────────────────

    async def aggregate(
        self, collection: str, pipeline: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        # Minimal — just return all docs for testing
        return [copy.deepcopy(d) for d in self._col(collection)]

    # ── Count ─────────────────────────────────────────────────────────

    async def count(self, collection: str, filters: Dict[str, Any]) -> int:
        return sum(1 for d in self._col(collection) if self._matches(d, filters))
