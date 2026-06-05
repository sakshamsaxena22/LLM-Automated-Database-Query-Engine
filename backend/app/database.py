import logging
from pymongo import MongoClient
from app.config import MONGODB_URI

logger = logging.getLogger(__name__)

client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
    tlsAllowInvalidCertificates=True,  # Atlas compatibility
)
db = client.payments
collection = db.transactions


def check_health() -> dict:
    """Ping MongoDB and return connection status."""
    try:
        client.admin.command("ping")
        count = collection.estimated_document_count()
        return {"status": "connected", "document_count": count}
    except Exception as e:
        logger.error("MongoDB health check failed: %s", e)
        return {"status": "disconnected", "error": str(e)}
