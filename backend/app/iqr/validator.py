"""
IQR Validator — extended from the original validator.py.

Preserves ALL original validation logic (disallowed operators, field
allowlists, pipeline-stage checks) and adds:

* INSERT validation (schema compliance)
* UPDATE validation (allowed fields + risk scoring)
* DELETE validation (require confirmation, risk scoring)
* Risk scoring (Section 11, Layer 5):
    - SELECT / find  → low
    - UPDATE 1 record → medium
    - DELETE / UPDATE many → high
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Set

from app.iqr.models import QueryRepresentation

logger = logging.getLogger(__name__)

# ── Schema-allowed fields (preserved from original validator.py) ──────
ALLOWED_FIELDS: Set[str] = {
    "transaction_id",
    "user_id",
    "amount",
    "currency",
    "status",
    "merchant",
    "payment_method",
    "timestamp",
}

# ── Top-level keys the LLM is allowed to return ──────────────────────
ALLOWED_TOP_LEVEL_KEYS: Set[str] = {
    "filter",
    "projection",
    "sort",
    "limit",
    "pipeline",
}

# ── Operators that MUST be blocked (write / dangerous) ────────────────
DISALLOWED_OPERATORS: Set[str] = {
    "$where",
    "$expr",
    "$function",
    "$merge",
    "$out",
    "$lookup",
    "$facet",
    "$graphLookup",
    "$set",
    "$unset",
    "$rename",
    "$push",
    "$pull",
    "$addToSet",
    "$pop",
    "$inc",
    "$mul",
    "$min",
    "$max",
    "$currentDate",
}

# ── Allowed aggregation pipeline stages ───────────────────────────────
ALLOWED_PIPELINE_STAGES: Set[str] = {
    "$match",
    "$group",
    "$sort",
    "$limit",
    "$skip",
    "$project",
    "$count",
    "$addFields",
    "$unwind",
}


# ── Core recursive checks (preserved from original) ──────────────────

def _check(obj: Any) -> None:
    """Recursively scan for disallowed operators in any nested structure."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in DISALLOWED_OPERATORS:
                raise ValueError(f"Unsafe operator detected: {k}")
            _check(v)
    elif isinstance(obj, list):
        for item in obj:
            _check(item)


def _validate_filter_fields(filter_dict: dict) -> None:
    """Ensure filter only references schema-allowed fields."""
    if not isinstance(filter_dict, dict):
        return
    for key in filter_dict:
        if key.startswith("$"):
            _check_nested_fields(filter_dict[key])
            continue
        if key not in ALLOWED_FIELDS:
            raise ValueError(f"Query references disallowed field: {key}")


def _check_nested_fields(obj: Any) -> None:
    """Check nested $and / $or arrays for disallowed fields."""
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                _validate_filter_fields(item)
    elif isinstance(obj, dict):
        _validate_filter_fields(obj)


def _validate_pipeline(pipeline: list) -> None:
    """Validate each stage in an aggregation pipeline."""
    if not isinstance(pipeline, list):
        raise ValueError("Pipeline must be a list")
    for stage in pipeline:
        if not isinstance(stage, dict):
            raise ValueError("Each pipeline stage must be a dict")
        for stage_name in stage:
            if stage_name not in ALLOWED_PIPELINE_STAGES:
                raise ValueError(f"Disallowed pipeline stage: {stage_name}")


# ── Raw-query validation (original entry-point, kept for compat) ──────

def validate_raw_query(query: dict) -> None:
    """Validate a complete LLM-generated *raw* query dict for safety.

    This is the original ``validate()`` function, preserved as-is.
    """
    if not isinstance(query, dict):
        raise ValueError("Query must be a JSON object")

    for key in query:
        if key not in ALLOWED_TOP_LEVEL_KEYS:
            raise ValueError(f"Unsafe top-level key: {key}")

    _check(query)

    if "filter" in query:
        _validate_filter_fields(query["filter"])

    if "pipeline" in query:
        _validate_pipeline(query["pipeline"])


# ── NEW: IQR-level validation ─────────────────────────────────────────

def _validate_insert(iqr: QueryRepresentation) -> None:
    """Validate an INSERT IQR for schema compliance."""
    if iqr.updates is None:
        raise ValueError("INSERT requires a document body (updates)")
    unknown = set(iqr.updates.keys()) - ALLOWED_FIELDS - {"_id"}
    if unknown:
        raise ValueError(f"INSERT contains unknown fields: {unknown}")


def _validate_update(iqr: QueryRepresentation) -> None:
    """Validate an UPDATE IQR — allowed fields + risk scoring."""
    if iqr.updates is None:
        raise ValueError("UPDATE requires update data (updates)")
    unknown = set(iqr.updates.keys()) - ALLOWED_FIELDS
    if unknown:
        raise ValueError(f"UPDATE references disallowed fields: {unknown}")
    if not iqr.filters:
        raise ValueError("UPDATE without filters is too dangerous")


def _validate_delete(iqr: QueryRepresentation) -> None:
    """Validate a DELETE IQR — require at least one filter."""
    if not iqr.filters:
        raise ValueError("DELETE without filters is not allowed")


def validate_query(iqr: QueryRepresentation) -> None:
    """Validate a ``QueryRepresentation`` depending on its operation type.

    Raises ``ValueError`` on any violation.
    """
    # For find / aggregate coming from the LLM, also validate the raw output
    if iqr.raw_llm_output is not None:
        validate_raw_query(iqr.raw_llm_output)

    if iqr.operation == "insert":
        _validate_insert(iqr)
    elif iqr.operation == "update":
        _validate_update(iqr)
    elif iqr.operation == "delete":
        _validate_delete(iqr)
    # find / aggregate are validated via validate_raw_query above

    # Attach risk assessment
    iqr.risk_level = assess_risk(iqr)


# ── Risk scoring (Section 11, Layer 5) ────────────────────────────────

def assess_risk(iqr: QueryRepresentation) -> str:
    """Return ``'low'``, ``'medium'``, or ``'high'`` for the given IQR.

    Rules:
    * SELECT / find / aggregate → low
    * UPDATE with specific filter (≤ 1 expected match) → medium
    * UPDATE without narrow filter → high
    * DELETE (any) → high
    * INSERT → low
    """
    op = iqr.operation.lower()

    if op in ("find", "aggregate"):
        return "low"

    if op == "insert":
        return "low"

    if op == "update":
        # If there is at least one equality filter, treat as targeted → medium
        has_eq = any(c.operator == "eq" for c in iqr.filters)
        return "medium" if has_eq else "high"

    if op == "delete":
        return "high"

    return "medium"
