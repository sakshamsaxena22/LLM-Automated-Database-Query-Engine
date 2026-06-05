"""
Query history domain model — stored in the ``query_history`` collection.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QueryHistoryInDB(BaseModel):
    """Records every AI-generated query for audit and analytics."""

    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    org_id: str = ""
    natural_language_query: str
    generated_query: Dict[str, Any] = Field(default_factory=dict)
    result_count: int = 0
    execution_time_ms: float = 0.0
    risk_level: str = "low"
    status: str = "success"  # success | failure | validation_error
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True}

    def to_mongo(self) -> dict:
        data = self.model_dump(by_alias=False, exclude={"id"})
        return data
