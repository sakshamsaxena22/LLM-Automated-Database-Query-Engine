"""
Audit log domain model — stored in the ``audit_logs`` collection.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AuditLogInDB(BaseModel):
    """Immutable audit trail entry for every significant operation."""

    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    org_id: str = ""
    operation: str  # read | create | update | delete | query
    entity: str  # collection or resource name
    entity_id: Optional[str] = None
    risk_level: str = "low"  # low | medium | high
    status: str = "success"  # success | failure
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True}

    def to_mongo(self) -> dict:
        data = self.model_dump(by_alias=False, exclude={"id"})
        return data
