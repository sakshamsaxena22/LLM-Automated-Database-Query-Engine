import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from groq import Groq
from app.config import GROQ_API_KEY

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "mongo_query_prompt.txt"

if not PROMPT_PATH.exists():
    raise RuntimeError(f"Prompt file not found at {PROMPT_PATH}")

SYSTEM_PROMPT_TEMPLATE = PROMPT_PATH.read_text(encoding="utf-8")

client = Groq(api_key=GROQ_API_KEY)

MAX_RETRIES = 2
RETRY_DELAY = 1.0  # seconds


def _extract_json(text: str) -> dict | None:
    """Try to extract a JSON object from LLM output that may contain
    markdown fences or surrounding explanation text."""
    import re

    # Try markdown code fence: ```json ... ``` or ``` ... ```
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try extracting the first top-level { ... } block
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


def generate_query(user_query: str) -> dict:
    """Translate a natural-language question into a MongoDB query dict."""
    if not isinstance(user_query, str) or not user_query.strip():
        raise ValueError("User query must be a non-empty string")

    # Inject current UTC timestamp for time-aware queries
    current_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    system_prompt = SYSTEM_PROMPT_TEMPLATE.replace("{current_utc}", current_utc)

    last_error = None
    for attempt in range(1, MAX_RETRIES + 2):  # 1 initial + MAX_RETRIES
        try:
            logger.info(
                "LLM request attempt %d for query: %s", attempt, user_query[:80]
            )
            t0 = time.perf_counter()

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                temperature=0,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query},
                ],
            )

            elapsed = (time.perf_counter() - t0) * 1000
            raw = response.choices[0].message.content.strip()
            logger.info("LLM responded in %.0f ms: %s", elapsed, raw[:200])

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                # Fallback: extract JSON from markdown fences or surrounding text
                data = _extract_json(raw)
                if data is None:
                    logger.warning("LLM returned non-JSON: %s", raw[:300])
                    raise ValueError("LLM did not return valid JSON")

            # Handle LLM refusal explicitly
            if "error" in data:
                raise ValueError(data["error"])

            # Valid query types
            if "filter" in data:
                data.setdefault("projection", None)
                data.setdefault("sort", [])
                data.setdefault("limit", 100)
                return data

            if "pipeline" in data:
                data.setdefault("limit", 100)
                return data

            raise ValueError("Unknown query type returned by LLM")

        except (ConnectionError, TimeoutError) as e:
            last_error = e
            logger.warning("LLM attempt %d failed: %s", attempt, e)
            if attempt <= MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
            continue

    raise RuntimeError(f"LLM request failed after {MAX_RETRIES + 1} attempts: {last_error}")
