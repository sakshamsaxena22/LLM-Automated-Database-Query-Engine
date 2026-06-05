"""
Analytics service — dashboard overview and usage metrics.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from app.db.adapters.mongo_adapter import MongoAdapter

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Compute analytics and dashboard metrics."""

    def __init__(self, adapter: MongoAdapter) -> None:
        self._adapter = adapter

    async def get_overview(self, org_id: str = "") -> Dict[str, Any]:
        """Return a high-level dashboard overview."""
        now = datetime.now(timezone.utc)
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        # ── User counts ──────────────────────────────────────────────
        total_users = await self._adapter.count("users", {})

        # ── Query history stats ──────────────────────────────────────
        total_queries = await self._adapter.count("query_history", {})
        queries_24h = await self._adapter.count(
            "query_history", {"timestamp": {"$gte": last_24h}}
        )
        queries_7d = await self._adapter.count(
            "query_history", {"timestamp": {"$gte": last_7d}}
        )

        # ── Audit log stats ──────────────────────────────────────────
        total_audit = await self._adapter.count("audit_logs", {})
        high_risk_ops = await self._adapter.count(
            "audit_logs", {"risk_level": "high"}
        )

        # ── Top operations breakdown (last 7 days) ───────────────────
        op_breakdown_pipeline = [
            {"$match": {"timestamp": {"$gte": last_7d}}},
            {"$group": {"_id": "$operation", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10},
        ]
        try:
            op_breakdown = await self._adapter.aggregate("query_history", op_breakdown_pipeline)
        except Exception:
            op_breakdown = []

        # ── Error rate (last 24h) ────────────────────────────────────
        failed_queries = await self._adapter.count(
            "query_history",
            {"timestamp": {"$gte": last_24h}, "status": "failure"},
        )
        error_rate = (
            round(failed_queries / queries_24h * 100, 1) if queries_24h > 0 else 0.0
        )

        return {
            "total_users": total_users,
            "total_queries": total_queries,
            "queries_last_24h": queries_24h,
            "queries_last_7d": queries_7d,
            "total_audit_logs": total_audit,
            "high_risk_operations": high_risk_ops,
            "error_rate_24h_pct": error_rate,
            "operation_breakdown_7d": op_breakdown,
            "generated_at": now.isoformat(),
        }
