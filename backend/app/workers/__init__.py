"""
Celery worker configuration — Phase 2.

Will handle: exports, reports, embedding generation, schema indexing,
backups, AI summarization.
"""

from __future__ import annotations

# Celery will be configured in Phase 2 with Redis as broker
# from celery import Celery
# celery_app = Celery("enterprise_platform", broker="redis://localhost:6379/1")
