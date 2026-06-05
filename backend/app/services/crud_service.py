"""
CRUD service — generic collection-level CRUD operations via the DB adapter.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastapi import HTTPException, status

from app.db.adapters.mongo_adapter import MongoAdapter
from app.core.config import settings

logger = logging.getLogger(__name__)

# Collections that users are NOT allowed to CRUD directly
_PROTECTED_COLLECTIONS = {"users", "organizations", "audit_logs"}


class CrudService:
    """Generic async CRUD operations on arbitrary MongoDB collections."""

    def __init__(self, adapter: MongoAdapter) -> None:
        self._adapter = adapter

    def _guard(self, collection: str) -> None:
        if collection in _PROTECTED_COLLECTIONS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Direct CRUD on '{collection}' is not allowed — use dedicated APIs",
            )

    async def list_documents(
        self,
        collection: str,
        skip: int = 0,
        limit: int = 50,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self._guard(collection)
        limit = min(limit, settings.MAX_RESULTS)
        docs = await self._adapter.find_many(
            collection, filters or {}, skip=skip, limit=limit
        )
        total = await self._adapter.count(collection, filters or {})
        return {"documents": docs, "total": total, "skip": skip, "limit": limit}

    async def get_document(self, collection: str, doc_id: str) -> Dict[str, Any]:
        self._guard(collection)
        try:
            doc = await self._adapter.find_one(collection, {"_id": ObjectId(doc_id)})
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID"
            )
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )
        return doc

    async def insert_document(
        self, collection: str, document: Dict[str, Any]
    ) -> Dict[str, Any]:
        self._guard(collection)
        doc_id = await self._adapter.insert_one(collection, document)
        logger.info("Inserted document %s into %s", doc_id, collection)
        return {"inserted_id": doc_id, "collection": collection}

    async def update_document(
        self, collection: str, doc_id: str, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        self._guard(collection)
        update_data.pop("_id", None)
        try:
            success = await self._adapter.update_one(
                collection, {"_id": ObjectId(doc_id)}, update_data
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID"
            )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or no changes applied",
            )
        logger.info("Updated document %s in %s", doc_id, collection)
        return await self.get_document(collection, doc_id)

    async def delete_document(
        self, collection: str, doc_id: str
    ) -> Dict[str, Any]:
        self._guard(collection)
        try:
            success = await self._adapter.delete_one(
                collection, {"_id": ObjectId(doc_id)}
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID"
            )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )
        logger.info("Deleted document %s from %s", doc_id, collection)
        return {"deleted_id": doc_id, "collection": collection}
