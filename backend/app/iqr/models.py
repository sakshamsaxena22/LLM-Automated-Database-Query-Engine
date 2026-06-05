"""
IQR dataclasses — database-agnostic query representation (Section 9).

The ``QueryRepresentation`` is the lingua franca between the AI service
(which produces it) and the translators (which convert it to a native query
for the target database).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Condition:
    """A single filter predicate."""

    field: str
    operator: str  # eq, neq, gt, gte, lt, lte, in, contains, regex
    value: Any


@dataclass
class QueryRepresentation:
    """Database-agnostic intermediate query representation."""

    operation: str  # find, insert, update, delete, aggregate
    entity: str  # collection / table name

    filters: List[Condition] = field(default_factory=list)
    updates: Optional[Dict[str, Any]] = None
    projection: Optional[List[str]] = None
    sort: Optional[List[Tuple[str, int]]] = None
    limit: int = 100
    skip: int = 0
    aggregates: Optional[List[Dict[str, Any]]] = None
    group_by: Optional[List[str]] = None

    # Metadata (not translated; used for audit/logging)
    raw_llm_output: Optional[Dict[str, Any]] = None
    risk_level: str = "low"

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a plain dict for JSON responses / logging."""
        return {
            "operation": self.operation,
            "entity": self.entity,
            "filters": [
                {"field": c.field, "operator": c.operator, "value": c.value}
                for c in self.filters
            ],
            "updates": self.updates,
            "projection": self.projection,
            "sort": self.sort,
            "limit": self.limit,
            "skip": self.skip,
            "aggregates": self.aggregates,
            "group_by": self.group_by,
            "risk_level": self.risk_level,
        }
