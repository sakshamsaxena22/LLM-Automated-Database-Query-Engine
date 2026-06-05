"""
Async MongoDB connection management using Motor.

Provides a module-level ``connect_db`` / ``close_db`` pair that should be
called from the FastAPI lifespan, and a ``get_database`` helper used by
repositories and adapters.
"""

from __future__ import annotations

import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

logger = logging.getLogger(__name__)

_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


async def connect_db() -> AsyncIOMotorDatabase:
    """Open the Motor client and return the default database."""
    global _client, _database

    _client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        tlsAllowInvalidCertificates=True,
    )
    # Force a round-trip so we fail fast if the URI is wrong
    await _client.admin.command("ping")
    _database = _client[settings.DATABASE_NAME]
    logger.info(
        "✅ MongoDB connected — database: %s",
        settings.DATABASE_NAME,
    )
    return _database


async def close_db() -> None:
    """Gracefully close the Motor client."""
    global _client, _database
    if _client is not None:
        _client.close()
        _client = None
        _database = None
        logger.info("🛑 MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """Return the current database handle.

    Raises ``RuntimeError`` if called before ``connect_db``.
    """
    if _database is None:
        raise RuntimeError("Database not initialised — call connect_db() first")
    return _database


async def check_health() -> dict:
    """Ping MongoDB and return connection status."""
    try:
        if _client is None:
            return {"status": "disconnected", "error": "Client not initialised"}
        await _client.admin.command("ping")
        db = get_database()
        collections = await db.list_collection_names()
        return {
            "status": "connected",
            "database": settings.DATABASE_NAME,
            "collections": len(collections),
        }
    except Exception as exc:
        logger.error("MongoDB health check failed: %s", exc)
        return {"status": "disconnected", "error": str(exc)}
