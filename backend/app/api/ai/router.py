"""
AI query routes — natural language query endpoint + history.

This is the core of the platform: translate NL → IQR → MongoDB query → results.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_database
from app.db.adapters.mongo_adapter import MongoAdapter
from app.db.repositories.audit_repo import AuditRepository
from app.iqr.translators.mongo_translator import MongoTranslator
from app.services.ai_service import AIService
from app.services.cache_service import CacheService
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["ai"])


# ── Schemas ───────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Natural language query")
    collection: str = Field("transactions", description="Target collection")


class QueryResponse(BaseModel):
    generated_query: Dict[str, Any]
    iqr: Dict[str, Any]
    count: int
    results: List[Dict[str, Any]]
    execution_time_ms: Optional[float] = None
    risk_level: str = "low"
    cached: bool = False


# ── Endpoints ─────────────────────────────────────────────────────────

@router.post("/query", response_model=QueryResponse)
async def ai_query(
    body: QueryRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    t0 = time.perf_counter()
    db = get_database()
    adapter = MongoAdapter(db)
    cache_svc = CacheService()
    ai_svc = AIService(cache_service=cache_svc)
    audit_svc = AuditService(AuditRepository(adapter))
    translator = MongoTranslator()

    user_id = current_user.get("sub", "")
    org_id = current_user.get("org_id", "")

    try:
        # 1. Generate IQR via AI
        iqr = await ai_svc.generate_query(
            user_query=body.query,
            org_id=org_id,
            entity=body.collection,
        )

        # 2. Translate IQR → native MongoDB query
        mongo_query = translator.translate(iqr)

        # 3. Execute
        if "filter" in mongo_query:
            results = await adapter.find_many(
                collection=body.collection,
                filters=mongo_query["filter"],
                projection=mongo_query.get("projection"),
                sort=mongo_query.get("sort") or None,
                limit=mongo_query.get("limit", settings.MAX_RESULTS),
                skip=mongo_query.get("skip", 0),
            )
        elif "pipeline" in mongo_query:
            pipeline = mongo_query["pipeline"]
            limit = mongo_query.get("limit", settings.MAX_RESULTS)
            pipeline.append({"$limit": limit})
            results = await adapter.aggregate(body.collection, pipeline)
        else:
            raise HTTPException(400, "Unsupported query structure")

        elapsed = round((time.perf_counter() - t0) * 1000, 1)

        # 4. Audit log
        await audit_svc.log(
            user_id=user_id,
            org_id=org_id,
            operation="ai_query",
            entity=body.collection,
            risk_level=iqr.risk_level,
            details={"query": body.query, "result_count": len(results)},
        )

        # 5. Save to query history
        await adapter.insert_one("query_history", {
            "user_id": user_id,
            "org_id": org_id,
            "natural_query": body.query,
            "generated_query": mongo_query,
            "result_count": len(results),
            "execution_time_ms": elapsed,
            "status": "success",
        })

        return QueryResponse(
            generated_query=mongo_query,
            iqr=iqr.to_dict(),
            count=len(results),
            results=results,
            execution_time_ms=elapsed,
            risk_level=iqr.risk_level,
        )

    except ValueError as exc:
        logger.warning("AI query validation error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("AI query error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/history")
async def query_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    db = get_database()
    adapter = MongoAdapter(db)
    user_id = current_user.get("sub", "")

    docs = await adapter.find_many(
        collection="query_history",
        filters={"user_id": user_id},
        sort=[("_id", -1)],
        skip=skip,
        limit=limit,
    )
    total = await adapter.count("query_history", {"user_id": user_id})
    return {"history": docs, "total": total, "skip": skip, "limit": limit}
