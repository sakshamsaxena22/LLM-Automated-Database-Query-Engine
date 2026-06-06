"""
Seed script for ChromaDB schema repository.
"""

from __future__ import annotations

import logging
import sys
from app.services.rag_service import RAGService

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# Sample metadata for payments.transactions
TRANSACTIONS_SCHEMA = [
    {"field_name": "transaction_id", "type": "string", "description": "Unique ID like TXN000123"},
    {"field_name": "user_id", "type": "string", "description": "User ID like USER001"},
    {"field_name": "amount", "type": "number", "description": "Transaction amount in INR (100-20000)"},
    {"field_name": "currency", "type": "string", "description": "Always INR"},
    {"field_name": "status", "type": "string", "description": "SUCCESS / FAILED / PENDING"},
    {"field_name": "merchant", "type": "string", "description": "Merchant name like Amazon, Flipkart, Swiggy, Zomato, Uber"},
    {"field_name": "payment_method", "type": "string", "description": "UPI / CARD / NETBANKING"},
    {"field_name": "timestamp", "type": "ISODate", "description": "UTC ISO 8601 datetime of transaction"}
]

USERS_SCHEMA = [
    {"field_name": "email", "type": "string", "description": "User email address"},
    {"field_name": "role", "type": "string", "description": "User role: viewer / analyst / editor / admin / super_admin"},
    {"field_name": "org_id", "type": "string", "description": "Organization tenant identifier"},
    {"field_name": "is_active", "type": "boolean", "description": "Deactivated account status check flag"}
]

AUDIT_LOG_SCHEMA = [
    {"field_name": "user_id", "type": "string", "description": "Who performed the action"},
    {"field_name": "operation", "type": "string", "description": "Action performed (find / insert / update / delete / login)"},
    {"field_name": "entity", "type": "string", "description": "Entity collection target"},
    {"field_name": "risk_level", "type": "string", "description": "Low / Medium / High assessment"},
    {"field_name": "timestamp", "type": "ISODate", "description": "When action happened"}
]


def seed_rag() -> None:
    logger.info("Initializing ChromaDB seed...")
    rag = RAGService()
    
    # Reset first to clear out test schemas
    rag.reset_db()
    
    # Ingest schemas
    rag.add_schema(
        collection_name="transactions",
        fields_metadata=TRANSACTIONS_SCHEMA,
        description="Records of payments, money transfers, and transaction logs. Supports financial querying."
    )
    
    rag.add_schema(
        collection_name="users",
        fields_metadata=USERS_SCHEMA,
        description="User configuration, credential definitions, active roles, and association to organizations."
    )
    
    rag.add_schema(
        collection_name="audit_logs",
        fields_metadata=AUDIT_LOG_SCHEMA,
        description="Security audit trails, logging database modification operations, risk evaluations, and caller ids."
    )
    
    logger.info("Verifying search query...")
    results = rag.retrieve_relevant_schemas("financial transactions and payment status", limit=1)
    logger.info("Search test results: %s", results)
    logger.info("ChromaDB schema metadata seeded successfully.")


if __name__ == "__main__":
    seed_rag()
