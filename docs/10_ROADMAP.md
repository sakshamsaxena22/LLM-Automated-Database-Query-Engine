# Future Roadmap & Evolution — LLM Real-Time Database Query Engine

This document details the planned milestones, feature improvements, and extensions for the Enterprise AI Query Platform.

## 1. Dynamic Schema Ingestion & Multi-Collection Support
* **Current Limitation**: Schema fields (`ALLOWED_FIELDS`) and collections are statically defined.
* **Goal**: Build an automated Schema Discovery service:
  * Inspects target MongoDB metadata structures.
  * Dynamically populates database mappings, allowing the LLM translation engine to adapt prompts to target any chosen database schema instantly.

---

## 2. Advanced RAG & Few-Shot Prompting via Chroma
* **Current Limitation**: Chroma database is provisioned in Docker but not actively utilized in the core translation loop.
* **Goal**: Store validated natural-language-to-MongoDB query pairs in Chroma:
  * On receipt of a query request, execute a vector search against Chroma to fetch the 3 most similar historically successful queries.
  * Inject these historical examples as few-shot demonstrations into the system prompt, improving Groq translation accuracy for complex user requests.

---

## 3. Autonomous Performance Tuning Loop
* **Current Limitation**: System registers query timings but does not take action on high latency.
* **Goal**: Implement automatic slow-query analysis:
  * If a query execution exceeds 500ms, run MongoDB `explain()` on the execution path.
  * Feed explain outputs to the LLM query assistant to recommend index creations or pipeline stage adjustments automatically.

---

## 4. Enhanced Security Auditing
* **Current Limitation**: Basic logging of operations is captured.
* **Goal**: Introduce secure tamper-proof ledger logging for write operations (insert, update, delete) to track execution histories for audit compliance.
