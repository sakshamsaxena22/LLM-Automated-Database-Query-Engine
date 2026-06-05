"""
Query Validator — ensures LLM-generated queries are safe and schema-compliant.
"""

# ── Schema-allowed fields ──────────────────────────────────────────
ALLOWED_FIELDS = {
    "transaction_id",
    "user_id",
    "amount",
    "currency",
    "status",
    "merchant",
    "payment_method",
    "timestamp",
}

# ── Top-level keys the LLM is allowed to return ───────────────────
ALLOWED_TOP_LEVEL_KEYS = {
    "filter",
    "projection",
    "sort",
    "limit",
    "pipeline",
}

# ── Operators that MUST be blocked (write / dangerous) ─────────────
DISALLOWED_OPERATORS = {
    # Dangerous query operators
    "$where",
    "$expr",
    "$function",
    # Write-oriented aggregation stages
    "$merge",
    "$out",
    # Cross-collection / complex stages
    "$lookup",
    "$facet",
    "$graphLookup",
    # Update operators (should never appear in a read query)
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

# ── Allowed aggregation pipeline stages ────────────────────────────
ALLOWED_PIPELINE_STAGES = {
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


def _check(obj):
    """Recursively scan for disallowed operators in any nested structure."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in DISALLOWED_OPERATORS:
                raise ValueError(f"Unsafe operator detected: {k}")
            _check(v)
    elif isinstance(obj, list):
        for item in obj:
            _check(item)


def _validate_filter_fields(filter_dict: dict):
    """Ensure filter only references schema-allowed fields."""
    if not isinstance(filter_dict, dict):
        return
    for key in filter_dict:
        # Skip MongoDB operators like $and, $or, $gt, etc.
        if key.startswith("$"):
            # Recursively validate nested conditions
            _check_nested_fields(filter_dict[key])
            continue
        if key not in ALLOWED_FIELDS:
            raise ValueError(f"Query references disallowed field: {key}")


def _check_nested_fields(obj):
    """Check nested $and / $or arrays for disallowed fields."""
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                _validate_filter_fields(item)
    elif isinstance(obj, dict):
        _validate_filter_fields(obj)


def _validate_pipeline(pipeline: list):
    """Validate each stage in an aggregation pipeline."""
    if not isinstance(pipeline, list):
        raise ValueError("Pipeline must be a list")
    for stage in pipeline:
        if not isinstance(stage, dict):
            raise ValueError("Each pipeline stage must be a dict")
        for stage_name in stage:
            if stage_name not in ALLOWED_PIPELINE_STAGES:
                raise ValueError(f"Disallowed pipeline stage: {stage_name}")


def validate(query: dict):
    """Validate a complete LLM-generated query for safety."""
    if not isinstance(query, dict):
        raise ValueError("Query must be a JSON object")

    for key in query:
        if key not in ALLOWED_TOP_LEVEL_KEYS:
            raise ValueError(f"Unsafe top-level key: {key}")

    # Deep-scan for dangerous operators
    _check(query)

    # Field-level validation for find queries
    if "filter" in query:
        _validate_filter_fields(query["filter"])

    # Pipeline stage validation for aggregation queries
    if "pipeline" in query:
        _validate_pipeline(query["pipeline"])
