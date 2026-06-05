# File Analysis — Part 1: Core Configuration, Security & Adapters

This document analyzes the primary infrastructure, configuration, security, and database adapter files within the backend subsystem.

## 1. Application Configuration

### [`backend/app/core/config.py`](file:///d:/LLMAutomatedDB/backend/app/core/config.py)
* **Purpose**: Typed, centralized configuration manager using `pydantic-settings`.
* **Key Mechanisms**:
  * Loads environment variables from the `.env` file located relative to this file (`../../.env`).
  * Enforces constraints on critical fields: `MONGODB_URI` and `GROQ_API_KEY` are required strings.
  * Supplies defaults for JWT settings (`JWT_ALGORITHM="HS256"`, expiry times), Redis settings (`REDIS_URL`), and CORS configuration.
  * Dynamically parses `CORS_ORIGINS` into a list of allowed origins.
  * Configures structured logging on import with format: `timestamp | level | module | message`.

---

## 2. Authentication & Cryptography

### [`backend/app/core/security.py`](file:///d:/LLMAutomatedDB/backend/app/core/security.py)
* **Purpose**: Provides JWT token generation, parsing, and password hashing utility functions.
* **Key Mechanisms**:
  * Hashing via `bcrypt`: `hash_password` and `verify_password` use salt-based encoding.
  * Token generation using `jose`:
    * `create_access_token` generates short-lived access JWTs with subject and token type.
    * `create_refresh_token` produces long-lived tokens for session refreshing.
  * FastAPI Integration:
    * `oauth2_scheme` captures bearer tokens via the standard header route.
    * `get_current_user` acts as a FastAPI dependency, extracting and validating the JWT, returning claims including `sub`, `org_id`, and `role`.

---

## 3. Database Layer

### [`backend/app/db/session.py`](file:///d:/LLMAutomatedDB/backend/app/db/session.py)
* **Purpose**: Async client connection lifecycle for MongoDB using Motor.
* **Key Mechanisms**:
  * `connect_db`: Instantiates `AsyncIOMotorClient` using `MONGODB_URI` with a 5000ms timeout limit. Validates database connection with an immediate `ping` command.
  * `close_db`: Closes the connection client gracefully on application teardown.
  * `get_database`: Dependency injector supplying the configured `AsyncIOMotorDatabase` handle to repository and service layers.
  * `check_health`: Health check query returns client connectivity and collection size metrics.

### [`backend/app/db/adapters/base.py`](file:///d:/LLMAutomatedDB/backend/app/db/adapters/base.py)
* **Purpose**: Abstract base adapter declaring standard async CRUD signatures: `find_one`, `find_many`, `insert_one`, `insert_many`, `update_one`, `update_many`, `delete_one`, `delete_many`, `aggregate`, and `count`.

### [`backend/app/db/adapters/mongo_adapter.py`](file:///d:/LLMAutomatedDB/backend/app/db/adapters/mongo_adapter.py)
* **Purpose**: Implements `BaseDBAdapter` using Motor's async MongoDB client.
* **Key Mechanisms**:
  * Automatically serializes default MongoDB `ObjectId` values into standard strings in-place (`_serialise_id`).
  * Enforces a standard update wrapper: automatically wraps raw updates under `$set` if no update operators are specified.
  * Supports cursor modification (skip, limit, sort) natively in `find_many`.
