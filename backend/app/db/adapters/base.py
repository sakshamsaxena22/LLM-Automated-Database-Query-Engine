"""
Abstract base class for database adapters (Section 9).

Every concrete adapter (Mongo, Postgres, etc.) must implement this
interface so that upper layers remain database-agnostic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


class BaseDBAdapter(ABC):
    """Database-agnostic CRUD + aggregation interface."""

    @abstractmethod
    async def find_one(
        self,
        collection: str,
        filters: Dict[str, Any],
        projection: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        ...

    @abstractmethod
    async def find_many(
        self,
        collection: str,
        filters: Dict[str, Any],
        projection: Optional[Dict[str, Any]] = None,
        sort: Optional[List[Tuple[str, int]]] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    async def insert_one(
        self,
        collection: str,
        document: Dict[str, Any],
    ) -> str:
        ...

    @abstractmethod
    async def insert_many(
        self,
        collection: str,
        documents: List[Dict[str, Any]],
    ) -> List[str]:
        ...

    @abstractmethod
    async def update_one(
        self,
        collection: str,
        filters: Dict[str, Any],
        update: Dict[str, Any],
    ) -> bool:
        ...

    @abstractmethod
    async def update_many(
        self,
        collection: str,
        filters: Dict[str, Any],
        update: Dict[str, Any],
    ) -> int:
        ...

    @abstractmethod
    async def delete_one(
        self,
        collection: str,
        filters: Dict[str, Any],
    ) -> bool:
        ...

    @abstractmethod
    async def delete_many(
        self,
        collection: str,
        filters: Dict[str, Any],
    ) -> int:
        ...

    @abstractmethod
    async def aggregate(
        self,
        collection: str,
        pipeline: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    async def count(
        self,
        collection: str,
        filters: Dict[str, Any],
    ) -> int:
        ...
