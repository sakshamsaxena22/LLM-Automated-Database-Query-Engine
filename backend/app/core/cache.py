"""
Redis cache wrapper — thin async layer over ``redis.asyncio``.

Falls back gracefully (returns ``None`` / no-ops) when Redis is unavailable
so the application can still work without a running Redis instance.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

_redis: Optional[aioredis.Redis] = None


async def connect_redis() -> Optional[aioredis.Redis]:
    """Open the Redis connection pool.  Returns the client or ``None``."""
    global _redis
    try:
        _redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=3,
        )
        await _redis.ping()
        logger.info("✅ Redis connected at %s", settings.REDIS_URL)
        return _redis
    except Exception as exc:
        logger.warning("⚠️ Redis not available (%s) — caching disabled", exc)
        _redis = None
        return None


async def close_redis() -> None:
    """Gracefully close the Redis connection pool."""
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None
        logger.info("🛑 Redis connection closed")


def get_redis() -> Optional[aioredis.Redis]:
    """Return the current Redis client (may be ``None``)."""
    return _redis


async def cache_get(key: str) -> Any:
    """Get a JSON-decoded value from Redis.  Returns ``None`` on miss or error."""
    if _redis is None:
        return None
    try:
        raw = await _redis.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as exc:
        logger.debug("cache_get(%s) failed: %s", key, exc)
        return None


async def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    """Store a JSON-serialisable *value* with a TTL (seconds)."""
    if _redis is None:
        return
    try:
        await _redis.set(key, json.dumps(value, default=str), ex=ttl)
    except Exception as exc:
        logger.debug("cache_set(%s) failed: %s", key, exc)


async def cache_delete(key: str) -> None:
    """Remove a key from Redis."""
    if _redis is None:
        return
    try:
        await _redis.delete(key)
    except Exception as exc:
        logger.debug("cache_delete(%s) failed: %s", key, exc)
