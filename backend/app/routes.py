import logging
import time
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from app.llm import generate_query
from app.validator import validate
from app.database import collection, check_health
from app.models import QueryRequest, QueryResponse
from app.config import MAX_RESULTS

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query_transactions(payload: QueryRequest):
    t0 = time.perf_counter()

    try:
        # ── Step 1: Generate MongoDB query from natural language ──
        llm_query: Dict[str, Any] = generate_query(payload.query)

        # ── Step 2: Validate safety ──
        validate(llm_query)

        # ── Step 3: Execute query ──
        if "filter" in llm_query:
            cursor = collection.find(
                llm_query["filter"],
                llm_query.get("projection"),
            )
            if llm_query.get("sort"):
                cursor = cursor.sort(llm_query["sort"])
            results: List[Dict] = list(
                cursor.limit(llm_query.get("limit", MAX_RESULTS))
            )

        elif "pipeline" in llm_query:
            pipeline = llm_query["pipeline"] + [
                {"$limit": llm_query.get("limit", MAX_RESULTS)}
            ]
            results = list(collection.aggregate(pipeline))

        else:
            raise HTTPException(400, "Unsupported query structure")

        # ── Step 4: Serialise ObjectIds ──
        for doc in results:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        logger.info(
            "Query completed in %.1f ms — %d results", elapsed_ms, len(results)
        )

        return {
            "generated_query": llm_query,
            "count": len(results),
            "results": results,
            "raw_response": llm_query,
            "execution_time_ms": elapsed_ms,
        }

    except PyMongoError as exc:
        logger.error("Database error: %s", exc)
        raise HTTPException(
            status_code=503,
            detail=f"Database unavailable: {str(exc)}",
        )
    except ValueError as exc:
        logger.warning("Validation error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("Unexpected error: %s", exc, exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/db-health")
def db_health():
    """Return MongoDB connection status and document count."""
    return check_health()
