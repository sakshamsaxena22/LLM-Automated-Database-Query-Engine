"""
Health check routes.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.db.session import check_health as db_health_check
from app.core.cache import get_redis

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health():
    redis = get_redis()
    redis_status = "connected"
    if redis:
        try:
            await redis.ping()
        except Exception:
            redis_status = "disconnected"
    else:
        redis_status = "disabled"

    return {
        "status": "ok",
        "service": "Enterprise AI Data Management Platform",
        "version": "2.0.0",
        "redis": redis_status,
    }


@router.get("/db")
async def db_health():
    return await db_health_check()
