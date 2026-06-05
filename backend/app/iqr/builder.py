"""
IQR Builder — convert raw LLM JSON output into a ``QueryRepresentation``.

Handles both ``filter``-style (find) and ``pipeline``-style (aggregate)
outputs that the existing Groq prompt returns.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from app.iqr.models import Condition, QueryRepresentation

logger = logging.getLogger(__name__)

# ── Mongo operator → IQR operator mapping ────────────────────────────
_MONGO_OP_MAP = {
    "$eq": "eq",
    "$ne": "neq",
    "$gt": "gt",
    "$gte": "gte",
    "$lt": "lt",
    "$lte": "lte",
    "$in": "in",
    "$regex": "regex",
}


def _parse_filter_conditions(
    filter_dict: Dict[str, Any],
) -> List[Condition]:
    """Recursively convert a MongoDB filter dict into ``Condition`` objects."""
    conditions: List[Condition] = []

    for key, value in filter_dict.items():
        # Logical operators
        if key in ("$and", "$or"):
            if isinstance(value, list):
                for sub in value:
                    conditions.extend(_parse_filter_conditions(sub))
            continue

        if isinstance(value, dict):
            # Operator expressions like {"amount": {"$gte": 1000}}
            for op, v in value.items():
                iqr_op = _MONGO_OP_MAP.get(op, op.lstrip("$"))
                conditions.append(Condition(field=key, operator=iqr_op, value=v))
        else:
            # Simple equality like {"status": "SUCCESS"}
            conditions.append(Condition(field=key, operator="eq", value=value))

    return conditions


def build_iqr_from_llm_output(
    llm_output: Dict[str, Any],
    entity: str = "transactions",
) -> QueryRepresentation:
    """Convert raw LLM JSON into a ``QueryRepresentation``.

    Supports:
    - ``filter``-based find queries
    - ``pipeline``-based aggregation queries
    """

    # ── Aggregation pipeline ─────────────────────────────────────────
    if "pipeline" in llm_output:
        pipeline = llm_output["pipeline"]

        # Extract filters from $match stages
        filters: List[Condition] = []
        for stage in pipeline:
            if "$match" in stage:
                filters.extend(_parse_filter_conditions(stage["$match"]))

        # Extract group_by from $group stages
        group_by: List[str] | None = None
        for stage in pipeline:
            if "$group" in stage:
                gid = stage["$group"].get("_id")
                if isinstance(gid, str) and gid.startswith("$"):
                    group_by = [gid.lstrip("$")]
                elif isinstance(gid, dict):
                    group_by = [v.lstrip("$") for v in gid.values() if isinstance(v, str)]

        return QueryRepresentation(
            operation="aggregate",
            entity=entity,
            filters=filters,
            aggregates=pipeline,
            group_by=group_by,
            limit=llm_output.get("limit", 100),
            raw_llm_output=llm_output,
            risk_level="low",
        )

    # ── Find query ───────────────────────────────────────────────────
    if "filter" in llm_output:
        conditions = _parse_filter_conditions(llm_output["filter"])

        projection: List[str] | None = None
        proj_raw = llm_output.get("projection")
        if isinstance(proj_raw, dict):
            projection = [k for k, v in proj_raw.items() if v]
        elif isinstance(proj_raw, list):
            projection = proj_raw

        sort_raw = llm_output.get("sort", [])
        sort_list = None
        if sort_raw:
            if isinstance(sort_raw, list):
                sort_list = [(s[0], s[1]) for s in sort_raw if isinstance(s, (list, tuple)) and len(s) == 2]

        return QueryRepresentation(
            operation="find",
            entity=entity,
            filters=conditions,
            projection=projection,
            sort=sort_list,
            limit=llm_output.get("limit", 100),
            raw_llm_output=llm_output,
            risk_level="low",
        )

    raise ValueError("LLM output does not contain 'filter' or 'pipeline'")
