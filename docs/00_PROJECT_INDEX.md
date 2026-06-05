# Repository Inventory — LLM Real-Time Database Query Engine

This document contains a complete inventory of the repository files, categorized by their component/subsystem.

## 1. Project Root Configuration & Documentation
* [`.env`](file:///d:/LLMAutomatedDB/.env) - Root level environment configuration file
* [`.gitignore`](file:///d:/LLMAutomatedDB/.gitignore) - Git ignore definitions
* [`DEPLOYMENT.md`](file:///d:/LLMAutomatedDB/DEPLOYMENT.md) - Reference deployment documentation
* [`DOCUMENTATION.md`](file:///d:/LLMAutomatedDB/DOCUMENTATION.md) - Legacy technical documentation
* [`README.md`](file:///d:/LLMAutomatedDB/README.md) - Main repository readme
* [`docker-compose.yml`](file:///d:/LLMAutomatedDB/docker-compose.yml) - Service orchestration config (mongo, backend, frontend)
* [`render.yaml`](file:///d:/LLMAutomatedDB/render.yaml) - Render deployment infrastructure definition
* [`report.md`](file:///d:/LLMAutomatedDB/report.md) - Initial project execution/status report
* [`requirements.txt`](file:///d:/LLMAutomatedDB/requirements.txt) - Root level dependencies reference list

## 2. Backend Subsystem (`backend/`)
The backend component is a FastAPI service that interacts with Groq LLM services and MongoDB.

### Root Configs
* [`backend/.env`](file:///d:/LLMAutomatedDB/backend/.env) - Backend specific environment variables
* [`backend/Dockerfile`](file:///d:/LLMAutomatedDB/backend/Dockerfile) - Docker multi-stage build configuration for backend
* [`backend/requirements.txt`](file:///d:/LLMAutomatedDB/backend/requirements.txt) - Python package dependencies
* [`backend/__init__.py`](file:///d:/LLMAutomatedDB/backend/__init__.py) - Package initialization file

### Core Application (`backend/app/`)
* [`backend/app/__init__.py`](file:///d:/LLMAutomatedDB/backend/app/__init__.py) - App package init
* [`backend/app/config.py`](file:///d:/LLMAutomatedDB/backend/app/config.py) - App configuration and logging setups
* [`backend/app/database.py`](file:///d:/LLMAutomatedDB/backend/app/database.py) - Legacy database setup and health routines
* [`backend/app/llm.py`](file:///d:/LLMAutomatedDB/backend/app/llm.py) - Legacy Groq integration and prompt loading utilities
* [`backend/app/main.py`](file:///d:/LLMAutomatedDB/backend/app/main.py) - FastAPI main application entry point and lifespan handlers
* [`backend/app/models.py`](file:///d:/LLMAutomatedDB/backend/app/models.py) - Legacy request/response Pydantic models
* [`backend/app/routes.py`](file:///d:/LLMAutomatedDB/backend/app/routes.py) - Legacy API routes
* [`backend/app/security.py`](file:///d:/LLMAutomatedDB/backend/app/security.py) - Legacy authentication definitions
* [`backend/app/validator.py`](file:///d:/LLMAutomatedDB/backend/app/validator.py) - Legacy query schema validation rules

### Modern Core Services (`backend/app/core/`)
* [`backend/app/core/__init__.py`](file:///d:/LLMAutomatedDB/backend/app/core/__init__.py) - Core subpackage init
* [`backend/app/core/cache.py`](file:///d:/LLMAutomatedDB/backend/app/core/cache.py) - In-memory and Redis-like cache wrapper
* [`backend/app/core/config.py`](file:///d:/LLMAutomatedDB/backend/app/core/config.py) - Modular application configuration
* [`backend/app/core/middleware.py`](file:///d:/LLMAutomatedDB/backend/app/core/middleware.py) - Logging and request correlation middleware
* [`backend/app/core/permissions.py`](file:///d:/LLMAutomatedDB/backend/app/core/permissions.py) - Granular role permissions definitions
* [`backend/app/core/security.py`](file:///d:/LLMAutomatedDB/backend/app/core/security.py) - Hashing, JWT creation and token validation operations

### API Routing Layer (`backend/app/api/`)
* [`backend/app/api/__init__.py`](file:///d:/LLMAutomatedDB/backend/app/api/__init__.py) - API router package init
* [`backend/app/api/health.py`](file:///d:/LLMAutomatedDB/backend/app/api/health.py) - Router module for health-checks and database statuses
* [`backend/app/api/ai/router.py`](file:///d:/LLMAutomatedDB/backend/app/api/ai/router.py) - Router for AI query translation requests
* [`backend/app/api/ai/__init__.py`](file:///d:/LLMAutomatedDB/backend/app/api/ai/__init__.py) - Subpackage init
* [`backend/app/api/analytics/router.py`](file:///d:/LLMAutomatedDB/backend/app/api/analytics/router.py) - Router for analytics metrics endpoints
* [`backend/app/api/analytics/__init__.py`](file:///d:/LLMAutomatedDB/backend/app/api/analytics/__init__.py) - Subpackage init
* [`backend/app/api/audit/router.py`](file:///d:/LLMAutomatedDB/backend/app/api/audit/router.py) - Router for query audit trail endpoints
* [`backend/app/api/audit/__init__.py`](file:///d:/LLMAutomatedDB/backend/app/api/audit/__init__.py) - Subpackage init
* [`backend/app/api/auth/router.py`](file:///d:/LLMAutomatedDB/backend/app/api/auth/router.py) - Router for user registration and JWT authentication
* [`backend/app/api/auth/__init__.py`](file:///d:/LLMAutomatedDB/backend/app/api/auth/__init__.py) - Subpackage init
* [`backend/app/api/crud/router.py`](file:///d:/LLMAutomatedDB/backend/app/api/crud/router.py) - Generic CRUD routing controller
* [`backend/app/api/crud/__init__.py`](file:///d:/LLMAutomatedDB/backend/app/api/crud/__init__.py) - Subpackage init
* [`backend/app/api/organizations/router.py`](file:///d:/LLMAutomatedDB/backend/app/api/organizations/router.py) - Organization management routes
* [`backend/app/api/organizations/__init__.py`](file:///d:/LLMAutomatedDB/backend/app/api/organizations/__init__.py) - Subpackage init
* [`backend/app/api/users/router.py`](file:///d:/LLMAutomatedDB/backend/app/api/users/router.py) - User administration and profile routes
* [`backend/app/api/users/__init__.py`](file:///d:/LLMAutomatedDB/backend/app/api/users/__init__.py) - Subpackage init

### Database Layer (`backend/app/db/`)
* [`backend/app/db/__init__.py`](file:///d:/LLMAutomatedDB/backend/app/db/__init__.py) - DB subpackage init
* [`backend/app/db/session.py`](file:///d:/LLMAutomatedDB/backend/app/db/session.py) - Session registry and multi-client connectors
* [`backend/app/db/adapters/__init__.py`](file:///d:/LLMAutomatedDB/backend/app/db/adapters/__init__.py) - DB adapters subpackage init
* [`backend/app/db/adapters/base.py`](file:///d:/LLMAutomatedDB/backend/app/db/adapters/base.py) - Abstract base adapter for data operations
* [`backend/app/db/adapters/mongo_adapter.py`](file:///d:/LLMAutomatedDB/backend/app/db/adapters/mongo_adapter.py) - MongoDB adapter implementation for safe read operations
* [`backend/app/db/models/__init__.py`](file:///d:/LLMAutomatedDB/backend/app/db/models/__init__.py) - Database entities subpackage init
* [`backend/app/db/models/audit_log.py`](file:///d:/LLMAutomatedDB/backend/app/db/models/audit_log.py) - Schema definition for query audit entries
* [`backend/app/db/models/organization.py`](file:///d:/LLMAutomatedDB/backend/app/db/models/organization.py) - Schema definition for multi-tenant organizations
* [`backend/app/db/models/query_history.py`](file:///d:/LLMAutomatedDB/backend/app/db/models/query_history.py) - Schema definition for parsed queries cache
* [`backend/app/db/models/user.py`](file:///d:/LLMAutomatedDB/backend/app/db/models/user.py) - Schema definition for system users
* [`backend/app/db/repositories/__init__.py`](file:///d:/LLMAutomatedDB/backend/app/db/repositories/__init__.py) - Repositories subpackage init
* [`backend/app/db/repositories/audit_repo.py`](file:///d:/LLMAutomatedDB/backend/app/db/repositories/audit_repo.py) - Data persistence layer for audit trails
* [`backend/app/db/repositories/org_repo.py`](file:///d:/LLMAutomatedDB/backend/app/db/repositories/org_repo.py) - Data persistence layer for organizations
* [`backend/app/db/repositories/user_repo.py`](file:///d:/LLMAutomatedDB/backend/app/db/repositories/user_repo.py) - Data persistence layer for system users

### Intelligent Query Translation Layer (`backend/app/iqr/`)
* [`backend/app/iqr/__init__.py`](file:///d:/LLMAutomatedDB/backend/app/iqr/__init__.py) - IQR package init
* [`backend/app/iqr/builder.py`](file:///d:/LLMAutomatedDB/backend/app/iqr/builder.py) - Dynamic builder for LLM prompts and schemas
* [`backend/app/iqr/models.py`](file:///d:/LLMAutomatedDB/backend/app/iqr/models.py) - Pydantic structures for translated queries
* [`backend/app/iqr/validator.py`](file:///d:/LLMAutomatedDB/backend/app/iqr/validator.py) - Automated static query validator checking schema boundaries
* [`backend/app/iqr/translators/__init__.py`](file:///d:/LLMAutomatedDB/backend/app/iqr/translators/__init__.py) - Translators subpackage init
* [`backend/app/iqr/translators/base.py`](file:///d:/LLMAutomatedDB/backend/app/iqr/translators/base.py) - Abstract class representing query translators
* [`backend/app/iqr/translators/mongo_translator.py`](file:///d:/LLMAutomatedDB/backend/app/iqr/translators/mongo_translator.py) - Concrete translator mapping abstract nodes to PyMongo actions

### Backend Services (`backend/app/services/`)
* [`backend/app/services/__init__.py`](file:///d:/LLMAutomatedDB/backend/app/services/__init__.py) - Services subpackage init
* [`backend/app/services/ai_service.py`](file:///d:/LLMAutomatedDB/backend/app/services/ai_service.py) - Orchestrates query compilation and LLM coordination
* [`backend/app/services/analytics_service.py`](file:///d:/LLMAutomatedDB/backend/app/services/analytics_service.py) - Computes telemetry and execution metrics
* [`backend/app/services/audit_service.py`](file:///d:/LLMAutomatedDB/backend/app/services/audit_service.py) - Records execution details for audit compliance
* [`backend/app/services/auth_service.py`](file:///d:/LLMAutomatedDB/backend/app/services/auth_service.py) - Manages user authentication state and operations
* [`backend/app/services/cache_service.py`](file:///d:/LLMAutomatedDB/backend/app/services/cache_service.py) - Handles key-value caching logic
* [`backend/app/services/crud_service.py`](file:///d:/LLMAutomatedDB/backend/app/services/crud_service.py) - General CRUD operation executor
* [`backend/app/services/org_service.py`](file:///d:/LLMAutomatedDB/backend/app/services/org_service.py) - Organization profile management service
* [`backend/app/services/user_service.py`](file:///d:/LLMAutomatedDB/backend/app/services/user_service.py) - User account management service

### Backend Background Workers (`backend/app/workers/`)
* [`backend/app/workers/__init__.py`](file:///d:/LLMAutomatedDB/backend/app/workers/__init__.py) - Workers initialization

### Prompts & Seed Data
* [`backend/prompts/mongo_query_prompt.txt`](file:///d:/LLMAutomatedDB/backend/prompts/mongo_query_prompt.txt) - System prompt for MongoDB query translation
* [`backend/seed_data/seed_transaction.py`](file:///d:/LLMAutomatedDB/backend/seed_data/seed_transaction.py) - Seed generation script for test transactions database
* [`backend/seed_data/__init__.py`](file:///d:/LLMAutomatedDB/backend/seed_data/__init__.py) - Seed package initialization

### Testing Suite
* [`backend/tests/test_api_e2e.py`](file:///d:/LLMAutomatedDB/backend/tests/test_api_e2e.py) - End-to-end endpoint verification tests
* [`backend/tests/test_query_route.py`](file:///d:/LLMAutomatedDB/backend/tests/test_query_route.py) - Safe-query route validation and execution tests
* [`backend/tests/__init__.py`](file:///d:/LLMAutomatedDB/backend/tests/__init__.py) - Testing suite initialization
* [`backend/tests/legacy/test_debug.py`](file:///d:/LLMAutomatedDB/backend/tests/legacy/test_debug.py) - Legacy debugging test helper
* [`backend/tests/legacy/test_e2e.py`](file:///d:/LLMAutomatedDB/backend/tests/legacy/test_e2e.py) - Legacy e2e query suite
* [`backend/tests/legacy/test_query.py`](file:///d:/LLMAutomatedDB/backend/tests/legacy/test_query.py) - Legacy query translation assertions

---

## 3. Frontend Subsystem (`frontend/`)
The frontend is a React application built with Vite, Tailwind CSS, TypeScript, and shadcn/ui components.

### Configuration & Infrastructure
* [`frontend/.gitignore`](file:///d:/LLMAutomatedDB/frontend/.gitignore) - Git ignore file for frontend artifacts
* [`frontend/Dockerfile`](file:///d:/LLMAutomatedDB/frontend/Dockerfile) - Multi-stage Nginx-based build definition for frontend
* [`frontend/README.md`](file:///d:/LLMAutomatedDB/frontend/README.md) - Frontend usage documentation
* [`frontend/components.json`](file:///d:/LLMAutomatedDB/frontend/components.json) - shadcn/ui CLI configuration file
* [`frontend/eslint.config.js`](file:///d:/LLMAutomatedDB/frontend/eslint.config.js) - ESLint rules config
* [`frontend/index.html`](file:///d:/LLMAutomatedDB/frontend/index.html) - Main HTML entry point
* [`frontend/nginx.conf`](file:///d:/LLMAutomatedDB/frontend/nginx.conf) - Nginx configuration for serving the built application SPA
* [`frontend/package.json`](file:///d:/LLMAutomatedDB/frontend/package.json) - Dependencies, scripts, and package descriptors
* [`frontend/tsconfig.app.json`](file:///d:/LLMAutomatedDB/frontend/tsconfig.app.json) - Vite app-specific typescript config
* [`frontend/tsconfig.json`](file:///d:/LLMAutomatedDB/frontend/tsconfig.json) - Root typescript configuration
* [`frontend/tsconfig.node.json`](file:///d:/LLMAutomatedDB/frontend/tsconfig.node.json) - Bundler/tooling-specific typescript config
* [`frontend/vite.config.ts`](file:///d:/LLMAutomatedDB/frontend/vite.config.ts) - Vite configuration file

### Shared UI Components (`frontend/@/components/ui/`)
* [`frontend/@/components/ui/avatar.tsx`](file:///d:/LLMAutomatedDB/frontend/@/components/ui/avatar.tsx) - Avatar profile badge element
* [`frontend/@/components/ui/badge.tsx`](file:///d:/LLMAutomatedDB/frontend/@/components/ui/badge.tsx) - Visual status indicator tag
* [`frontend/@/components/ui/button.tsx`](file:///d:/LLMAutomatedDB/frontend/@/components/ui/button.tsx) - Core button element with variations
* [`frontend/@/components/ui/card.tsx`](file:///d:/LLMAutomatedDB/frontend/@/components/ui/card.tsx) - Layout panel component
* [`frontend/@/components/ui/dialog.tsx`](file:///d:/LLMAutomatedDB/frontend/@/components/ui/dialog.tsx) - Overlay modal dialog component
* [`frontend/@/components/ui/dropdown-menu.tsx`](file:///d:/LLMAutomatedDB/frontend/@/components/ui/dropdown-menu.tsx) - Popover dropdown selector
* [`frontend/@/components/ui/input.tsx`](file:///d:/LLMAutomatedDB/frontend/@/components/ui/input.tsx) - Text input component
* [`frontend/@/components/ui/label.tsx`](file:///d:/LLMAutomatedDB/frontend/@/components/ui/label.tsx) - Text label element for form fields
* ... (Contains other shadcn/ui boilerplate components such as select, separator, skeleton, sonner, switch, table, tabs, textarea, tooltip)

### Public Assets (`frontend/public/` and `frontend/src/assets/`)
* [`frontend/public/favicon.svg`](file:///d:/LLMAutomatedDB/frontend/public/favicon.svg) - Favicon SVG resource
* [`frontend/public/icons.svg`](file:///d:/LLMAutomatedDB/frontend/public/icons.svg) - Shared SVG icon pack
* [`frontend/src/assets/hero.png`](file:///d:/LLMAutomatedDB/frontend/src/assets/hero.png) - App main layout background graphic
* [`frontend/src/assets/react.svg`](file:///d:/LLMAutomatedDB/frontend/src/assets/react.svg) - React logo
* [`frontend/src/assets/vite.svg`](file:///d:/LLMAutomatedDB/frontend/src/assets/vite.svg) - Vite logo

### Application Source Code (`frontend/src/`)
* [`frontend/src/App.tsx`](file:///d:/LLMAutomatedDB/frontend/src/App.tsx) - Root application route setup
* [`frontend/src/index.css`](file:///d:/LLMAutomatedDB/frontend/src/index.css) - CSS entry point
* [`frontend/src/main.tsx`](file:///d:/LLMAutomatedDB/frontend/src/main.tsx) - DOM target render point

#### Client API Integration Layer (`frontend/src/api/`)
* [`frontend/src/api/analytics.ts`](file:///d:/LLMAutomatedDB/frontend/src/api/analytics.ts) - Analytics endpoints bindings
* [`frontend/src/api/audit.ts`](file:///d:/LLMAutomatedDB/frontend/src/api/audit.ts) - Query audit listings fetcher
* [`frontend/src/api/auth.ts`](file:///d:/LLMAutomatedDB/frontend/src/api/auth.ts) - JWT login, registration, and refresh bindings
* [`frontend/src/api/client.ts`](file:///d:/LLMAutomatedDB/frontend/src/api/client.ts) - Shared Axios/fetch configuration
* [`frontend/src/api/crud.ts`](file:///d:/LLMAutomatedDB/frontend/src/api/crud.ts) - Base API bindings for CRUD manager
* [`frontend/src/api/queries.ts`](file:///d:/LLMAutomatedDB/frontend/src/api/queries.ts) - Real-time query submission endpoint bindings
* [`frontend/src/api/users.ts`](file:///d:/LLMAutomatedDB/frontend/src/api/users.ts) - User profile details fetchers

#### Shared React Components (`frontend/src/components/`)
* [`frontend/src/components/common/LoadingSpinner.tsx`](file:///d:/LLMAutomatedDB/frontend/src/components/common/LoadingSpinner.tsx) - App spinner element
* [`frontend/src/components/common/ProtectedRoute.tsx`](file:///d:/LLMAutomatedDB/frontend/src/components/common/ProtectedRoute.tsx) - Route guard restricting access to authenticated users
* [`frontend/src/components/layout/DashboardLayout.tsx`](file:///d:/LLMAutomatedDB/frontend/src/components/layout/DashboardLayout.tsx) - Admin layout panel
* [`frontend/src/components/layout/PublicLayout.tsx`](file:///d:/LLMAutomatedDB/frontend/src/components/layout/PublicLayout.tsx) - Main user landing layout shell
* [`frontend/src/components/layout/Sidebar.tsx`](file:///d:/LLMAutomatedDB/frontend/src/components/layout/Sidebar.tsx) - Sidebar console navigation list
* [`frontend/src/components/layout/Topbar.tsx`](file:///d:/LLMAutomatedDB/frontend/src/components/layout/Topbar.tsx) - Header metadata and actions panel

#### custom React Hooks (`frontend/src/hooks/`)
* [`frontend/src/hooks/useAuth.ts`](file:///d:/LLMAutomatedDB/frontend/src/hooks/useAuth.ts) - Authentication status utilities
* [`frontend/src/hooks/useDebounce.ts`](file:///d:/LLMAutomatedDB/frontend/src/hooks/useDebounce.ts) - Search/input performance debouncing
* [`frontend/src/hooks/useTheme.ts`](file:///d:/LLMAutomatedDB/frontend/src/hooks/useTheme.ts) - Dark/light styling logic

#### Utilities & Pages (`frontend/src/lib/`, `frontend/src/pages/`)
* [`frontend/src/lib/utils.ts`](file:///d:/LLMAutomatedDB/frontend/src/lib/utils.ts) - Component helper library
* [`frontend/src/pages/dashboard/AnalyticsPage.tsx`](file:///d:/LLMAutomatedDB/frontend/src/pages/dashboard/AnalyticsPage.tsx) - Data charts and query latency metrics UI
* [`frontend/src/pages/dashboard/AuditLogsPage.tsx`](file:///d:/LLMAutomatedDB/frontend/src/pages/dashboard/AuditLogsPage.tsx) - Admin audit timeline log table UI
* [`frontend/src/pages/dashboard/DatabaseConnectionsPage.tsx`](file:///d:/LLMAutomatedDB/frontend/src/pages/dashboard/DatabaseConnectionsPage.tsx) - MongoDB state monitoring UI
* [`frontend/src/pages/dashboard/DataManagerPage.tsx`](file:///d:/LLMAutomatedDB/frontend/src/pages/dashboard/DataManagerPage.tsx) - Entity view CRUD table UI
* [`frontend/src/pages/dashboard/QueryConsolePage.tsx`](file:///d:/LLMAutomatedDB/frontend/src/pages/dashboard/QueryConsolePage.tsx) - Natural language query terminal console UI
* [`frontend/src/pages/dashboard/SettingsPage.tsx`](file:///d:/LLMAutomatedDB/frontend/src/pages/dashboard/SettingsPage.tsx) - Configuration layout UI
* [`frontend/src/pages/dashboard/UserManagementPage.tsx`](file:///d:/LLMAutomatedDB/frontend/src/pages/dashboard/UserManagementPage.tsx) - System users directory UI
* [`frontend/src/pages/public/LandingPage.tsx`](file:///d:/LLMAutomatedDB/frontend/src/pages/public/LandingPage.tsx) - Project introduction UI page
* [`frontend/src/pages/public/LoginPage.tsx`](file:///d:/LLMAutomatedDB/frontend/src/pages/public/LoginPage.tsx) - JWT Authentication entry form page
* [`frontend/src/pages/public/RegisterPage.tsx`](file:///d:/LLMAutomatedDB/frontend/src/pages/public/RegisterPage.tsx) - User signup form page

#### Routes & Global State (`frontend/src/routes/`, `frontend/src/store/`, `frontend/src/styles/`, `frontend/src/types/`)
* [`frontend/src/routes/index.tsx`](file:///d:/LLMAutomatedDB/frontend/src/routes/index.tsx) - Navigation schema setup
* [`frontend/src/store/authStore.ts`](file:///d:/LLMAutomatedDB/frontend/src/store/authStore.ts) - Zustand authentication slice
* [`frontend/src/store/queryStore.ts`](file:///d:/LLMAutomatedDB/frontend/src/store/queryStore.ts) - Zustand query console slice
* [`frontend/src/store/uiStore.ts`](file:///d:/LLMAutomatedDB/frontend/src/store/uiStore.ts) - Zustand UI display state slice
* [`frontend/src/styles/globals.css`](file:///d:/LLMAutomatedDB/frontend/src/styles/globals.css) - Global styling styles overrides
* [`frontend/src/types/api.ts`](file:///d:/LLMAutomatedDB/frontend/src/types/api.ts) - Base API typings
* [`frontend/src/types/auth.ts`](file:///d:/LLMAutomatedDB/frontend/src/types/auth.ts) - Authentication-specific interface typings
* [`frontend/src/types/crud.ts`](file:///d:/LLMAutomatedDB/frontend/src/types/crud.ts) - CRUD-specific entity typings
* [`frontend/src/types/query.ts`](file:///d:/LLMAutomatedDB/frontend/src/types/query.ts) - Query console data interface typings
