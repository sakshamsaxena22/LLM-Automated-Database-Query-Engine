# Agent Prompt & System Configuration — LLM Real-Time Database Query Engine

This document details the configuration, prompt design, and context Injection mechanics of the translation agent.

## 1. Prompt Architecture (`mongo_query_prompt.txt`)

The system prompt defines a highly constrained persona and context ruleset to ensure predictable and safe output.

### Role & Persona
* **Constraint**: `You are a Principal MongoDB Database Administrator operating on a PRODUCTION system.`
* **Goal**: Ground behavior in database safety and compliance, emphasizing the production nature of the target environment to minimize loose execution behavior.

### Schema Grounding (Data Constraints)
The prompt specifies the case-sensitive field list, data types, and enum domains:
* `transaction_id` (string), `user_id` (string), `amount` (number), `currency` (string), `status` (SUCCESS/FAILED/PENDING), `merchant` (string), `payment_method` (UPI/CARD/NETBANKING), and `timestamp` (ISODate).

### Context Injections
* **Current UTC Time**: The template expects `{current_utc}`. The translation service (`ai_service.py`) dynamically replaces this tag with the current UTC timestamp at runtime (e.g. `2026-06-05T03:06:00Z`).
* **Time Range Handling**: Instructs the model to use relative range calculations against the injected timestamp using `$gte` / `$lte` with ISO8601 formatting.

---

## 2. Guardrails & Refusal Rules

* **Deterministic Formatting**: Strict JSON-only response requirement (no markdown wrappers or conversational filler).
* **Strict Read-Only**: Command explicitly blocks updates, deletions, and inserts.
* **Safety Refusals**:
  * If the user prompt is ambiguous, unsafe, or requests modifications, the LLM is instructed to refuse by returning a structured error JSON payload:
    ```json
    { "error": "Query cannot be safely generated" }
    ```
  * The service parser intercepts this key, raising a `ValueError` which prevents any execution attempts.
