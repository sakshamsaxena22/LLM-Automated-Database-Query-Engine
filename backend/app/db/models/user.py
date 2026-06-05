"""
User domain model — stored in the ``users`` collection.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserInDB(BaseModel):
    """Representation of a user document in MongoDB."""

    id: Optional[str] = Field(None, alias="_id")
    email: EmailStr
    hashed_password: str
    full_name: str = ""
    role: str = "viewer"  # viewer | editor | manager | admin | super_admin
    org_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True}

    def to_mongo(self) -> dict:
        """Return a dict suitable for MongoDB insertion (without ``_id``)."""
        data = self.model_dump(by_alias=False, exclude={"id"})
        return data

    def safe_dict(self) -> dict:
        """Return a dict without the hashed_password."""
        data = self.model_dump(by_alias=False)
        data.pop("hashed_password", None)
        return data
