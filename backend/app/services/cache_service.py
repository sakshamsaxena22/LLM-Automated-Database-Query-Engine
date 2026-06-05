"""
Cache service — higher-level caching interface on top of ``core.cache``.

Key format: org_{id}:user_{id}:query_{hash}  (Section 8).
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.core.cache import cache_delete, cache_get, cache_set

logger = logging.getLogger(__name__)

QUERY_TTL = 300  # 5 minutes
SCHEMA_TTL = 600  # 10 minutes


class CacheService:
    """Application-level caching helpers layered over Redis."""

    async def get(self, key: str) -> Any:
        return await cache_get(key)

    async def set(self, key: str, value: Any, ttl: int = QUERY_TTL) -> None:
        await cache_set(key, value, ttl)

    async def delete(self, key: str) -> None:
        await cache_delete(key)

    # ── Query cache ───────────────────────────────────────────────────

    async def get_query_cache(
        self, org_id: str, query_hash: str
    ) -> Optional[dict]:
        key = f"org_{org_id}:query_{query_hash}"
        return await cache_get(key)

    async def set_query_cache(
        self, org_id: str, query_hash: str, result: dict
    ) -> None:
        key = f"org_{org_id}:query_{query_hash}"
        await cache_set(key, result, QUERY_TTL)

    # ── Schema cache ──────────────────────────────────────────────────

    async def get_schema_cache(
        self, org_id: str, db_name: str
    ) -> Optional[dict]:
        key = f"org_{org_id}:schema_{db_name}"
        return await cache_get(key)

    async def set_schema_cache(
        self, org_id: str, db_name: str, schema: dict
    ) -> None:
        key = f"org_{org_id}:schema_{db_name}"
        await cache_set(key, schema, SCHEMA_TTL)

    async def invalidate_schema_cache(
        self, org_id: str, db_name: str
    ) -> None:
        key = f"org_{org_id}:schema_{db_name}"
        await cache_delete(key)
