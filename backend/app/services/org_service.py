"""
Organization management service — create, list, get orgs.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Optional

from fastapi import HTTPException, status

from app.db.repositories.org_repo import OrgRepository

logger = logging.getLogger(__name__)


def _slugify(name: str) -> str:
    """Convert an org name to a URL-safe slug."""
    slug = re.sub(r"[^\w\s-]", "", name.lower().strip())
    return re.sub(r"[\s_]+", "-", slug)


class OrgService:
    """Business logic for organization management."""

    def __init__(self, org_repo: OrgRepository) -> None:
        self._repo = org_repo

    async def create_org(
        self,
        name: str,
        owner_id: str,
        allowed_databases: list[str] | None = None,
    ) -> Dict[str, Any]:
        slug = _slugify(name)
        existing = await self._repo.find_by_slug(slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Organization with slug '{slug}' already exists",
            )

        org_data = {
            "name": name,
            "slug": slug,
            "owner_id": owner_id,
            "members": [owner_id],
            "allowed_databases": allowed_databases or [],
            "settings": {},
        }
        org_id = await self._repo.create(org_data)
        logger.info("Created org %s (%s)", org_id, name)
        return {"org_id": org_id, "name": name, "slug": slug}

    async def list_orgs(
        self, skip: int = 0, limit: int = 50
    ) -> Dict[str, Any]:
        orgs = await self._repo.list_all(skip=skip, limit=limit)
        total = await self._repo.count()
        return {"organizations": orgs, "total": total, "skip": skip, "limit": limit}

    async def get_org(self, org_id: str) -> Dict[str, Any]:
        org = await self._repo.find_by_id(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        return org

    async def update_org(
        self, org_id: str, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        update_data.pop("_id", None)
        update_data.pop("owner_id", None)  # cannot change owner via update
        success = await self._repo.update(org_id, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found or no changes applied",
            )
        return await self.get_org(org_id)
