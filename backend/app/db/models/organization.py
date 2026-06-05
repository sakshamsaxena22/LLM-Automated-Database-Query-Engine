"""
Organization domain model — stored in the ``organizations`` collection.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class OrganizationInDB(BaseModel):
    """Representation of an organization document in MongoDB."""

    id: Optional[str] = Field(None, alias="_id")
    name: str
    slug: str
    owner_id: str
    members: List[str] = Field(default_factory=list)
    allowed_databases: List[str] = Field(default_factory=list)
    settings: Dict[str, str] = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True}

    def to_mongo(self) -> dict:
        data = self.model_dump(by_alias=False, exclude={"id"})
        return data
