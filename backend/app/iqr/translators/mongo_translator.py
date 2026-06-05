"""
MongoDB translator — convert ``QueryRepresentation`` into native Mongo queries.

If the IQR carries ``raw_llm_output`` (i.e. the LLM already produced valid
Mongo JSON) the translator simply passes it through. Otherwise it builds the
query from the structured IQR fields.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from app.iqr.models import Condition, QueryRepresentation
from app.iqr.translators.base import BaseTranslator

logger = logging.getLogger(__name__)

# ── IQR operator → Mongo operator ────────────────────────────────────
_OP_MAP: Dict[str, str] = {
    "eq": "$eq",
    "neq": "$ne",
    "gt": "$gt",
    "gte": "$gte",
    "lt": "$lt",
    "lte": "$lte",
    "in": "$in",
    "regex": "$regex",
    "contains": "$regex",
}


def _build_filter(conditions: List[Condition]) -> Dict[str, Any]:
    """Convert a list of ``Condition`` objects into a Mongo filter dict."""
    if not conditions:
        return {}

    mongo_filter: Dict[str, Any] = {}
    for c in conditions:
        if c.operator == "eq":
            mongo_filter[c.field] = c.value
        elif c.operator == "contains":
            mongo_filter[c.field] = {"$regex": c.value, "$options": "i"}
        else:
            mongo_op = _OP_MAP.get(c.operator, f"${c.operator}")
            mongo_filter.setdefault(c.field, {})[mongo_op] = c.value
    return mongo_filter


class MongoTranslator(BaseTranslator):
    """Convert an IQR into a MongoDB-native query dict."""

    def translate(self, iqr: QueryRepresentation) -> Dict[str, Any]:
        # ── Fast path: pass through raw LLM output ───────────────────
        if iqr.raw_llm_output is not None and iqr.operation in ("find", "aggregate"):
            return iqr.raw_llm_output

        # ── Build from structured IQR ────────────────────────────────
        result: Dict[str, Any] = {"operation": iqr.operation, "collection": iqr.entity}

        if iqr.operation == "find":
            result["filter"] = _build_filter(iqr.filters)
            if iqr.projection:
                result["projection"] = {f: 1 for f in iqr.projection}
            result["sort"] = iqr.sort or []
            result["limit"] = iqr.limit
            result["skip"] = iqr.skip

        elif iqr.operation == "aggregate":
            if iqr.aggregates:
                result["pipeline"] = iqr.aggregates
            else:
                pipeline: List[Dict[str, Any]] = []
                filt = _build_filter(iqr.filters)
                if filt:
                    pipeline.append({"$match": filt})
                result["pipeline"] = pipeline
            result["limit"] = iqr.limit

        elif iqr.operation == "insert":
            result["document"] = iqr.updates or {}

        elif iqr.operation == "update":
            result["filter"] = _build_filter(iqr.filters)
            result["update"] = {"$set": iqr.updates} if iqr.updates else {}

        elif iqr.operation == "delete":
            result["filter"] = _build_filter(iqr.filters)

        return result
