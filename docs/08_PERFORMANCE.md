# Performance Audit & Telemetry — LLM Real-Time Database Query Engine

This document analyzes the caching systems, database indexes, thread scheduling, and response monitoring.

## 1. Caching Strategy & Fallbacks (`core/cache.py`)

* **Redis Caching**:
  * Saves translated JSON representations under cache keys structured as `org_<org_id>:query_<sha256_hash>`.
  * Standard TTL is set to 300 seconds (5 minutes).
* **Robust Fail-Safe**:
  * The Redis connector uses a 3-second connection timeout (`socket_connect_timeout=3`).
  * If Redis goes offline, the exception is caught, caching is bypassed (`_redis = None`), and requests fallback directly to live Groq API translation without interrupting service.

---

## 2. Event-Loop Performance & Multi-Threading

* **Sync-to-Async Bridge**:
  * Groq SDK client commands are synchronous blocking processes.
  * In `ai_service.py`, LLM calls are wrapped inside `asyncio.to_thread()`:
    ```python
    response = await asyncio.to_thread(
        self._client.chat.completions.create,
        ...
    )
    ```
  * This shifts the blocking operations from the primary FastAPI event loop to a dedicated background worker thread pool, preventing CPU starvation and keeping the server highly responsive under concurrent user load.

---

## 3. Database Indexes & Query Constraints

* **Index Optimization Matrix**:
  * `timestamp` (Descending): Optimized for time-relative filters (e.g. *last 24 hours*).
  * `status` (Ascending) & `amount` (Ascending): Quick scan resolution for transaction subsets.
  * `transaction_id` (Ascending, Unique): Deduplication and immediate index searches.
* **Response Payload Cap**:
  * Query execution limits default to a hard cap of 100 documents (`limit=settings.MAX_RESULTS`).
  * Aggregation pipeline cursors enforce a maximum fetch limit of 1000 documents to avoid memory starvation on the FastAPI server instance.

---

## 4. Telemetry Logging Middleware (`core/middleware.py`)

* **Correlation Tracking**:
  * Custom logging middleware intercepts incoming requests, attaches a unique `X-Correlation-ID` header, and records the request lifecycle.
  * Outputs start and complete logs displaying endpoints, status codes, and execution latencies in milliseconds.
