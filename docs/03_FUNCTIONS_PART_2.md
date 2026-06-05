# Function Analysis — Part 2: Query Translation, Validation & IQR Builder

This document documents core functions involved in query translation, static security validation, and AI coordination.

## 1. Query Representation Builder (`iqr/builder.py`)

### `_parse_filter_conditions(filter_dict: Dict[str, Any]) -> List[Condition]`
* **Input**: MongoDB filter dictionary.
* **Output**: List of resolved generic IQR Condition objects.
* **Logic**:
  * Scans keys. For logical operators (`$and`, `$or`), recursively processes children arrays.
  * For operator expressions (`{"amount": {"$gte": 1000}}`), resolves operator names against `_MONGO_OP_MAP` mapping.
  * For simple scalar values (`{"status": "SUCCESS"}`), registers equality ("eq") conditions.

### `build_iqr_from_llm_output(llm_output: Dict[str, Any], entity: str) -> QueryRepresentation`
* **Input**: JSON payload from the LLM, target collection name.
* **Output**: Standardized `QueryRepresentation` wrapper object.
* **Logic**:
  * Identifies query type: if `pipeline` key is present, treats as aggregate operation. Parses `$match` and `$group` blocks.
  * If `filter` is present, treats as find operation. Parses selections, projection blocks, sorting scopes, and limits.

---

## 2. Query Guard Validation (`iqr/validator.py`)

### `validate_query(iqr: QueryRepresentation)`
* **Input**: Query representation wrapper.
* **Output**: None (throws `ValueError` on validation failure).
* **Logic**:
  * Validates raw JSON using legacy key, field and operator blocklists.
  * For insert operations, confirms schema field alignment.
  * For updates and deletes, blocks parameter-less calls and enforces filtering conditions.
  * Triggers risk level calculations.

### `assess_risk(iqr: QueryRepresentation) -> str`
* **Input**: Query representation wrapper.
* **Output**: Risk classification level string (`"low"`, `"medium"`, or `"high"`).
* **Logic**:
  * Read/aggregate and inserts are marked as `"low"`.
  * Targeted updates (with equality filters) are marked as `"medium"`.
  * Global updates (without equality filters) and deletions are marked as `"high"`.

---

## 3. Orchestrator Service (`services/ai_service.py`)

### `generate_query(user_query: str, org_id: str, entity: str) -> QueryRepresentation`
* **Input**: Natural language prompt, tenant group identifier, collection entity.
* **Output**: Validated Query Representation wrapper.
* **Logic**:
  * Hashes query to verify against Redis Cache first (returns parsed cache hit immediately).
  * Injects current ISO timestamp into prompt. Calls Groq API in thread-pool wrapper (to prevent blocking async event loop).
  * Automatically retries up to 2 times with exponential backoff on connection or timeout failures.
  * Parses output, extracts JSON from fences if necessary, generates IQR model, validates safety, cache-records outcome, and returns result.
