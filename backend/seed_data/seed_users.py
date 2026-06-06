"""
Seed script — populate the database with default accounts for different RBAC roles.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

from pymongo import MongoClient
from dotenv import load_dotenv
import bcrypt

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# Load environment
backend_env = Path(__file__).resolve().parent.parent / ".env"
if backend_env.exists():
    load_dotenv(dotenv_path=backend_env, override=True)
else:
    load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    logger.error("MONGODB_URI environment variable not set")
    sys.exit(1)

DATABASE_NAME = os.getenv("DATABASE_NAME", "enterprise_db")

# Default users to seed
USERS = [
    {
        "email": "superadmin@enterprise.com",
        "password": "SuperSecureAdmin123!",
        "full_name": "SaaS Super Admin",
        "role": "super_admin",
        "org_id": "org_enterprise",
        "is_active": True
    },
    {
        "email": "admin@enterprise.com",
        "password": "SecureAdmin123!",
        "full_name": "SaaS Admin",
        "role": "admin",
        "org_id": "org_enterprise",
        "is_active": True
    },
    {
        "email": "editor@enterprise.com",
        "password": "SecureEditor123!",
        "full_name": "SaaS Editor",
        "role": "editor",
        "org_id": "org_enterprise",
        "is_active": True
    },
    {
        "email": "viewer@enterprise.com",
        "password": "SecureViewer123!",
        "full_name": "SaaS Viewer",
        "role": "viewer",
        "org_id": "org_enterprise",
        "is_active": True
    }
]


def seed_users() -> None:
    logger.info("Connecting to MongoDB at %s...", MONGODB_URI.split("@")[-1])
    client = MongoClient(MONGODB_URI, tlsAllowInvalidCertificates=True)
    db = client[DATABASE_NAME]
    collection = db.users

    # Delete existing seeded users if any
    seeded_emails = [u["email"] for u in USERS]
    logger.info("Purging existing seeded user accounts: %s", seeded_emails)
    collection.delete_many({"email": {"$in": seeded_emails}})

    logger.info("Hashing passwords and seeding default accounts...")
    now_utc = datetime.now(timezone.utc)
    
    for u in USERS:
        # Hash password using bcrypt (matching app.core.security logic)
        hashed_password = bcrypt.hashpw(
            u["password"].encode("utf-8"), 
            bcrypt.gensalt()
        ).decode("utf-8")
        
        user_doc = {
            "email": u["email"],
            "hashed_password": hashed_password,
            "full_name": u["full_name"],
            "role": u["role"],
            "org_id": u["org_id"],
            "is_active": u["is_active"],
            "created_at": now_utc,
            "updated_at": now_utc
        }
        
        collection.insert_one(user_doc)
        logger.info("Created user: %s (Role: %s)", u["email"], u["role"])

    logger.info("Database user seeding completed successfully.")


if __name__ == "__main__":
    seed_users()
