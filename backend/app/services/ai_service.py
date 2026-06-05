"""
AI service — refactored from the original ``llm.py``.

Preserves:
* Groq client + model selection
* Retry logic with exponential back-off
* JSON extraction from markdown fences
* Time-injection into system prompt

Adds:
* Async interface
* Returns ``QueryRepresentation`` (IQR) instead of raw dict
* Redis cache integration (check-before-call)
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from groq import Groq

from app.core.config import settings
from app.iqr.builder import build_iqr_from_llm_output
from app.iqr.models import QueryRepresentation
from app.iqr.validator import validate_query
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)

# ── Load prompt template ──────────────────────────────────────────────
_PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "mongo_query_prompt.txt"
if not _PROMPT_PATH.exists():
    # Fall back to project root
    _PROMPT_PATH = Path(__file__).resolve().parents[3] / "prompts" / "mongo_query_prompt.txt"

if _PROMPT_PATH.exists():
    _SYSTEM_PROMPT_TEMPLATE = _PROMPT_PATH.read_text(encoding="utf-8")
else:
    raise RuntimeError(f"Prompt file not found (searched {_PROMPT_PATH})")

MAX_RETRIES = 2
RETRY_DELAY = 1.0


# ── JSON extraction (preserved from original llm.py) ─────────────────

def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Try to extract a JSON object from LLM output that may contain
    markdown fences or surrounding explanation text."""
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    start = text.find("{")
    if start != -1:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    break
    return None


def _query_hash(query: str) -> str:
    """Deterministic hash for cache keys."""
    return hashlib.sha256(query.strip().lower().encode()).hexdigest()[:16]


class AIService:
    """Async AI query generation service backed by Groq."""

    def __init__(self, cache_service: Optional[CacheService] = None) -> None:
        self._client = Groq(api_key=settings.GROQ_API_KEY)
        self._cache = cache_service

    async def generate_query(
        self,
        user_query: str,
        org_id: str = "",
        entity: str = "transactions",
    ) -> QueryRepresentation:
        """Translate a natural-language question into a validated IQR.

        1. Check Redis cache.
        2. Call Groq LLM (with retries).
        3. Parse / extract JSON.
        4. Build IQR.
        5. Validate IQR.
        6. Store in cache.
        7. Return IQR.
        """
        if not isinstance(user_query, str) or not user_query.strip():
            raise ValueError("User query must be a non-empty string")

        # ── 1. Cache check ───────────────────────────────────────────
        cache_key = f"org_{org_id}:query_{_query_hash(user_query)}"
        if self._cache:
            cached = await self._cache.get_query_cache(org_id, _query_hash(user_query))
            if cached:
                logger.info("Cache HIT for query: %s", user_query[:60])
                return build_iqr_from_llm_output(cached, entity=entity)

        # ── 2. Call LLM ──────────────────────────────────────────────
        current_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        system_prompt = _SYSTEM_PROMPT_TEMPLATE.replace("{current_utc}", current_utc)

        last_error: Optional[Exception] = None
        for attempt in range(1, MAX_RETRIES + 2):
            try:
                logger.info("LLM request attempt %d for query: %s", attempt, user_query[:80])
                t0 = time.perf_counter()

                # Groq client is synchronous — run in thread pool
                response = await asyncio.to_thread(
                    self._client.chat.completions.create,
                    model=settings.LLM_MODEL,
                    temperature=0,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_query},
                    ],
                )

                elapsed = (time.perf_counter() - t0) * 1000
                raw = response.choices[0].message.content.strip()
                logger.info("LLM responded in %.0f ms: %s", elapsed, raw[:200])

                # ── 3. Parse JSON ────────────────────────────────────
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    data = _extract_json(raw)
                    if data is None:
                        logger.warning("LLM returned non-JSON: %s", raw[:300])
                        raise ValueError("LLM did not return valid JSON")

                if "error" in data:
                    raise ValueError(data["error"])

                # Normalise find queries
                if "filter" in data:
                    data.setdefault("projection", None)
                    data.setdefault("sort", [])
                    data.setdefault("limit", settings.MAX_RESULTS)
                elif "pipeline" in data:
                    data.setdefault("limit", settings.MAX_RESULTS)
                else:
                    raise ValueError("Unknown query type returned by LLM")

                # ── 4. Build IQR ─────────────────────────────────────
                iqr = build_iqr_from_llm_output(data, entity=entity)

                # ── 5. Validate ──────────────────────────────────────
                validate_query(iqr)

                # ── 6. Cache ─────────────────────────────────────────
                if self._cache:
                    await self._cache.set_query_cache(org_id, _query_hash(user_query), data)

                return iqr

            except (ConnectionError, TimeoutError) as exc:
                last_error = exc
                logger.warning("LLM attempt %d failed: %s", attempt, exc)
                if attempt <= MAX_RETRIES:
                    await asyncio.sleep(RETRY_DELAY * attempt)
                continue

        raise RuntimeError(
            f"LLM request failed after {MAX_RETRIES + 1} attempts: {last_error}"
        )
