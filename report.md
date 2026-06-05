# Project Report: Enterprise AI Data Management SaaS Platform

**Repository:** [LLMAutomatedDB](https://github.com/sakshamsaxena22/LLMAutomatedDB)

---

## 1. System Overview

The **Enterprise AI Data Management SaaS Platform** is a multi-tenant, secure, high-performance system that translates natural-language questions into safe database queries (currently MongoDB) using LLM reasoning. It consists of a **FastAPI backend** (orchestrating auth, query generation, validation, and database operations) and a **React + Vite + TypeScript frontend** (providing a premium, interactive admin and operator console).

The system enforces a strict role-based access control (RBAC) model and recursive query validation, ensuring that users can only perform database actions aligned with their organization's scope and their personal role permissions.

---

## 2. Architecture & Design

The platform uses a modular, domain-driven architecture:

```
                  ┌─────────────────────────────────────────┐
                  │          React Frontend Console         │
                  │  • Landing, Auth, Console, CRUD Manager │
                  └────────────────────┬────────────────────┘
                                       │ Axios Client (JWT + Refresh)
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │             FastAPI Backend             │
                  │                                         │
                  │  - /api/v1/auth (JWT Sign/Refresh/RBAC) │
                  │  - /api/v1/ai (NL to Query, History)    │
                  │  - /api/v1/crud (Dynamic Entity CRUD)   │
                  │  - /api/v1/health (System status)       │
                  └────────────────────┬────────────────────┘
                                       │ Motor Async Client
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │                 MongoDB                 │
                  │  - Database: enterprise_db              │
                  │  - Collections: transactions, users,    │
                  │    organizations, query_history         │
                  └─────────────────────────────────────────┘
```

---

## 3. Technical Implementation Details

### 3.1 Advanced Auth & RBAC
- **JWT Architecture**: Access tokens are short-lived, while refresh tokens are long-lived and verified securely on endpoint routes.
- **RBAC Matrix**: 
  - `viewer`: Can only read data and check system health.
  - `analyst`: Can execute read and aggregation queries.
  - `editor`: Can perform insertion and update operations.
  - `admin` / `super_admin`: Full system management, organization controls, and audit trails.

### 3.2 Intermediate Query Representation (IQR)
Instead of executing LLM outputs directly against the database, the query pipeline parses the output into a database-agnostic **Intermediate Query Representation**. This structure is validated against:
- Disallowed stages (e.g. `$lookup`, `$merge`, `$out`).
- Blocklisted operators (e.g. `$where`, `$expr`, `$function`).
- Schema-only fields.

---

## 4. Verification & Testing

The platform has been validated across multiple testing suites:
1. **API End-to-End Tests** (`test_api_e2e.py`): Verifies JWT flow, registration collisions, token refresh, and route guarding.
2. **Legacy Route Tests** (`test_query_route.py`, `test_query.py`, `test_e2e.py`): Confirms legacy client scripts requesting `/query` and `/db-health` are answered correctly.
3. **Frontend Compilation**: React frontend compiles cleanly with zero TypeScript errors.

---

## 5. Next Steps: Phase 3 (AI + Local RAG Database)
The system is ready to progress to the RAG layer:
- **Vector Database**: Embedding schema metadata (field names, collection names, types) into a local persistent **ChromaDB** client.
- **Dynamic Prompts**: Query ChromaDB to supply only the relevant schema context to the LLM during query generation.
