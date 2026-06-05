"""
Enterprise AI Data Management Platform — FastAPI application factory.

Registers all middleware, routers, and manages the lifecycle of database
and cache connections.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.middleware import RequestLoggingMiddleware
from app.db.session import connect_db, close_db, check_health
from app.core.cache import connect_redis, close_redis

# ── Route imports ─────────────────────────────────────────────────────
from app.api.auth.router import router as auth_router
from app.api.users.router import router as users_router
from app.api.organizations.router import router as orgs_router
from app.api.ai.router import router as ai_router
from app.api.crud.router import router as crud_router
from app.api.audit.router import router as audit_router
from app.api.analytics.router import router as analytics_router
from app.api.health import router as health_router
from app.routes import router as legacy_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    # ── Startup ──
    logger.info("🚀 Starting Enterprise AI Data Management Platform v2.0.0")

    # Connect MongoDB
    try:
        await connect_db()
        health = await check_health()
        logger.info("MongoDB status: %s", health.get("status"))
    except Exception as exc:
        logger.warning("⚠️ MongoDB not reachable at startup: %s", exc)

    # Connect Redis (optional — app works without it)
    await connect_redis()

    yield

    # ── Shutdown ──
    logger.info("🛑 Application shutting down")
    await close_redis()
    await close_db()


app = FastAPI(
    title="Enterprise AI Data Management Platform",
    description=(
        "AI-Powered Enterprise Database Operations Platform with "
        "RAG-Based Query Intelligence. Supports natural language CRUD, "
        "multi-organization tenancy, and hierarchical permissions."
    ),
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ─────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

# ── Versioned API routes (/api/v1/...) ───────────────────────────────
API_V1_PREFIX = "/api/v1"

app.include_router(auth_router, prefix=API_V1_PREFIX)
app.include_router(users_router, prefix=API_V1_PREFIX)
app.include_router(orgs_router, prefix=API_V1_PREFIX)
app.include_router(ai_router, prefix=API_V1_PREFIX)
app.include_router(crud_router, prefix=API_V1_PREFIX)
app.include_router(audit_router, prefix=API_V1_PREFIX)
app.include_router(analytics_router, prefix=API_V1_PREFIX)
app.include_router(health_router, prefix=API_V1_PREFIX)
app.include_router(legacy_router)


# ── Root redirect ─────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Enterprise AI Data Management Platform",
        "version": "2.0.0",
        "docs": "/docs",
        "health": f"{API_V1_PREFIX}/health",
    }
