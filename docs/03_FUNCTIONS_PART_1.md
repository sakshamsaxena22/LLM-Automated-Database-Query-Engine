# Function Analysis — Part 1: Configuration, Session & Cryptography

This document documents core functions and classes that handle authentication, session management, and LLM communication helper utilities.

## 1. Application Security (`core/security.py`)

### `hash_password(password: str) -> str`
* **Input**: Plain-text password string.
* **Output**: Bcrypt hashed password string.
* **Logic**: Enforces UTF-8 encoding of input, generates salt via `bcrypt.gensalt()`, hashes and returns decoded string representation.

### `verify_password(plain_password: str, hashed_password: str) -> bool`
* **Input**: Plain-text password, target hashed password.
* **Output**: Verification outcome boolean.
* **Logic**: Compares plain password bytes to hash bytes via bcrypt check method.

### `create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str`
* **Input**: Token metadata payload, optional lifespan delta.
* **Output**: JWT encoded token string.
* **Logic**: Clones payload, adds exp claim (default: settings config expiry), sets `type: "access"`, signs with secret key using HS256 algorithm.

---

## 2. Session Lifecycle (`db/session.py`)

### `connect_db() -> AsyncIOMotorDatabase`
* **Input**: None.
* **Output**: Active Motor async database client instance.
* **Logic**: Instantiates `AsyncIOMotorClient` with environment parameters, issues a ping command to check connectivity, assigns local database reference.

### `check_health() -> dict`
* **Input**: None.
* **Output**: Status and diagnostic metrics dictionary.
* **Logic**: Resolves connection state, counts active collections, logs failures and returns structured connection information.

---

## 3. LLM Translation Extraction (`services/ai_service.py` & legacy `llm.py`)

### `_extract_json(text: str) -> Optional[Dict[str, Any]]`
* **Input**: Raw LLM completion text.
* **Output**: Extracted dictionary parsed from JSON, or `None`.
* **Logic**:
  1. Utilizes regex to match markdown code fences: ```` ```json ... ``` ```` or ```` ``` ... ``` ````.
  2. If code block is missing or corrupt, falls back to parsing the first balanced curly-braces block (`{ ... }`) recursively.
  3. Returns parsed JSON or catches `JSONDecodeError` yielding `None`.
