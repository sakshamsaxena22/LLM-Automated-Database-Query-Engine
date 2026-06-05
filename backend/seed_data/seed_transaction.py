"""
Seed script — Populate the payments.transactions collection with
realistic sample data for development and testing.

Usage:
    python -m seed_data.seed_transaction          # append 500 records
    python -m seed_data.seed_transaction --drop    # drop + re-seed
"""

import argparse
import os
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pymongo import MongoClient, ASCENDING, DESCENDING
from dotenv import load_dotenv

# ── Load environment ──────────────────────────────────────────────
# Try backend/.env first (same pattern as the backend app)
backend_env = Path(__file__).resolve().parent.parent / ".env"
if backend_env.exists():
    load_dotenv(dotenv_path=backend_env, override=True)
else:
    load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    print("❌ MONGODB_URI environment variable not set")
    sys.exit(1)

# ── MongoDB connection ────────────────────────────────────────────
client = MongoClient(MONGODB_URI, tlsAllowInvalidCertificates=True)
db = client.payments
collection = db.transactions

# ── Seed configuration ────────────────────────────────────────────
TOTAL_RECORDS = 500

STATUSES = ["SUCCESS", "FAILED", "PENDING"]
STATUS_WEIGHTS = [0.65, 0.20, 0.15]  # realistic distribution

MERCHANTS = [
    "Amazon", "Flipkart", "Swiggy", "Zomato", "Uber",
    "Myntra", "BigBasket", "PhonePe", "Paytm", "BookMyShow",
]

PAYMENT_METHODS = ["UPI", "CARD", "NETBANKING"]
PAYMENT_WEIGHTS = [0.55, 0.30, 0.15]  # UPI-heavy like real India

AMOUNT_RANGES = {
    "Amazon":      (500, 15000),
    "Flipkart":    (300, 12000),
    "Swiggy":      (100, 1500),
    "Zomato":      (100, 1200),
    "Uber":        (80, 3000),
    "Myntra":      (400, 8000),
    "BigBasket":   (200, 5000),
    "PhonePe":     (50, 10000),
    "Paytm":       (50, 5000),
    "BookMyShow":  (150, 2500),
}


def generate_documents(n: int) -> list:
    """Generate n realistic transaction documents."""
    now_utc = datetime.now(timezone.utc)
    documents = []

    for i in range(n):
        merchant = random.choice(MERCHANTS)
        lo, hi = AMOUNT_RANGES[merchant]

        documents.append({
            "transaction_id": f"TXN{i:06d}",
            "user_id": f"USER{random.randint(1, 50):03d}",
            "amount": round(random.uniform(lo, hi), 2),
            "currency": "INR",
            "status": random.choices(STATUSES, STATUS_WEIGHTS)[0],
            "merchant": merchant,
            "payment_method": random.choices(PAYMENT_METHODS, PAYMENT_WEIGHTS)[0],
            "timestamp": now_utc - timedelta(minutes=random.randint(0, 14 * 24 * 60)),
        })

    return documents


def main():
    parser = argparse.ArgumentParser(description="Seed transactions collection")
    parser.add_argument("--drop", action="store_true", help="Drop collection before seeding")
    args = parser.parse_args()

    # ── Indexes (idempotent) ──
    print("📑 Creating indexes...")
    collection.create_index([("timestamp", DESCENDING)])
    collection.create_index([("status", ASCENDING)])
    collection.create_index([("amount", ASCENDING)])
    collection.create_index([("transaction_id", ASCENDING)], unique=True)

    if args.drop:
        print("🗑️  Dropping existing documents...")
        collection.delete_many({})

    # ── Generate & insert ──
    print(f"⏳ Generating {TOTAL_RECORDS} transactions...")
    documents = generate_documents(TOTAL_RECORDS)

    try:
        result = collection.insert_many(documents, ordered=False)
        print(f"✅ Inserted {len(result.inserted_ids)} transactions")
    except Exception as e:
        print(f"⚠️  Some records may already exist: {e}")

    # ── Final count ──
    count = collection.count_documents({})
    print(f"📊 Total documents in collection: {count}")


if __name__ == "__main__":
    main()
