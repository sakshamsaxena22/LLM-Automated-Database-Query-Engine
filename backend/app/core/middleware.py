"""
Application middleware — CORS setup, request logging, and tenant context.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

logger = logging.getLogger(__name__)


def setup_cors(app: FastAPI) -> None:
    """Attach CORS middleware using origins from settings."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with timing, method, path, and status."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        start = time.perf_counter()
        logger.info(
            "[%s] → %s %s",
            request_id,
            request.method,
            request.url.path,
        )

        response: Response = await call_next(request)

        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        logger.info(
            "[%s] ← %d  %.1f ms",
            request_id,
            response.status_code,
            elapsed_ms,
        )
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = str(elapsed_ms)
        return response


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Extract ``X-Org-ID`` header (if present) and store in request state.

    Downstream handlers can access ``request.state.org_id``.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        org_id = request.headers.get("X-Org-ID", "")
        request.state.org_id = org_id
        response: Response = await call_next(request)
        return response


def setup_middleware(app: FastAPI) -> None:
    """Register all custom middleware on *app*."""
    # Order matters — outermost runs first.
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(TenantContextMiddleware)
    setup_cors(app)
