"""
Analytics routes — dashboard overview metrics.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.db.session import get_database
from app.db.adapters.mongo_adapter import MongoAdapter
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
async def analytics_overview(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    db = get_database()
    adapter = MongoAdapter(db)
    svc = AnalyticsService(adapter)
    org_id = current_user.get("org_id", "")
    return await svc.get_overview(org_id=org_id)
