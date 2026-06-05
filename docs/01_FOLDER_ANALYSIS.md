# Folder Analysis — LLM Real-Time Database Query Engine

This document analyzes the directory structure of the repository, explaining the purpose and architectural role of each folder.

## 1. Backend Subsystem (`backend/app/`)

### `api/` — Request Routing Layer
Defines FastAPI router modules, separating operations by feature and domains:
* [`api/ai/`](file:///d:/LLMAutomatedDB/backend/app/api/ai) — Manages translation requests from natural language to structured MongoDB queries.
* [`api/analytics/`](file:///d:/LLMAutomatedDB/backend/app/api/analytics) — Metrics endpoints for dashboard visualization.
* [`api/audit/`](file:///d:/LLMAutomatedDB/backend/app/api/audit) — Manages the system-wide query audit trail.
* [`api/auth/`](file:///d:/LLMAutomatedDB/backend/app/api/auth) — Manages user session registrations, logins, and JWT token issuance.
* [`api/crud/`](file:///d:/LLMAutomatedDB/backend/app/api/crud) — Generic CRUD routes for managing collections.
* [`api/organizations/`](file:///d:/LLMAutomatedDB/backend/app/api/organizations) — Multi-tenant organization configurations.
* [`api/users/`](file:///d:/LLMAutomatedDB/backend/app/api/users) — Profile and management endpoints for users.

### `core/` — Infrastructure & Cross-Cutting Concerns
Shared infrastructure components used across the entire application:
* Cache wrappers, unified configurations, logging middleware, security utilities, and global permissions settings.

### `db/` — Database Operations & Repository Layer
Manages the interfaces and implementations for database persistence:
* [`db/adapters/`](file:///d:/LLMAutomatedDB/backend/app/db/adapters) — Base adapter interface and custom database client adapters (such as `mongo_adapter.py`).
* [`db/models/`](file:///d:/LLMAutomatedDB/backend/app/db/models) — ODM schemas and database models (Audit log, Org, Query history, User).
* [`db/repositories/`](file:///d:/LLMAutomatedDB/backend/app/db/repositories) — Repository pattern implementations separating query logic from business logic.

### `iqr/` — Intelligent Query Translation (IQR) Engine
The core compiler subsystem of the project:
* Houses the translation pipeline converting abstract nodes into valid database queries.
* [`iqr/translators/`](file:///d:/LLMAutomatedDB/backend/app/iqr/translators) — Adapter-specific query translators (e.g., translating natural language/intermediate syntax directly to MongoDB structures).

### `services/` — Business Logic Layer
Orchestrates work between routing and persistence layers, performing model validation and business rules verification.

---

## 2. Frontend Subsystem (`frontend/src/`)

### `api/` — Backend API Connectors
Axios HTTP client configurations and typed API request methods for interaction with FastAPI routes.

### `components/` — Shared & Structural UI Elements
* [`components/common/`](file:///d:/LLMAutomatedDB/frontend/src/components/common) — Utility elements like spinners and route guards.
* [`components/layout/`](file:///d:/LLMAutomatedDB/frontend/src/components/layout) — Interface shells (Topbar, Sidebar, Dashboard wrapper).

### `hooks/` — custom React Hooks
Reusable state logic providers (authentication status, dark/light theme triggers, debounce controllers).

### `pages/` — Main Page Components
Top-level views rendered by the router (Query terminal, Analytics dashboards, Auditing, User management, Settings, Auth).

### `store/` — Zustand Global State
Client-side centralized store configurations partition-managed (Auth, Query history, UI configuration state).
