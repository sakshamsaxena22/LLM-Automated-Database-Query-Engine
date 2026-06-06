import logging
from typing import Optional
from pymongo import MongoClient
from app.config import MONGODB_URI

logger = logging.getLogger(__name__)

# ── Lazy client — no DNS lookup at import time ────────────────────────
_client: Optional[MongoClient] = None


def _get_client() -> MongoClient:
    """Return (and lazily create) the shared MongoClient."""
    global _client
    if _client is None:
        _client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            tlsAllowInvalidCertificates=True,  # Atlas compatibility
        )
    return _client


class _LazyCollection:
    """Proxy that resolves the real collection on first attribute access."""

    def __getattr__(self, name):
        return getattr(_get_client().payments.transactions, name)

    def __iter__(self):
        return iter(_get_client().payments.transactions)


collection = _LazyCollection()


def check_health() -> dict:
    """Ping MongoDB and return connection status."""
    try:
        client = _get_client()
        client.admin.command("ping")
        count = client.payments.transactions.estimated_document_count()
        return {"status": "connected", "document_count": count}
    except Exception as e:
        logger.error("MongoDB health check failed: %s", e)
        return {"status": "disconnected", "error": str(e)}
