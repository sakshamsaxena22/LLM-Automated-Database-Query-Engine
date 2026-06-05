# Technical Documentation — LLM Real-Time Database Query Engine

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Backend Modules](#backend-modules)
5. [Frontend](#frontend)
6. [LLM Prompt Engineering](#llm-prompt-engineering)
7. [Query Validation Pipeline](#query-validation-pipeline)
8. [Database Design](#database-design)
9. [Configuration](#configuration)
10. [Deployment](#deployment)
11. [Security Model](#security-model)
12. [API Reference](#api-reference)

---

## System Overview

The LLM Real-Time Database Query Engine translates natural-language questions into safe, read-only MongoDB queries using Groq's Llama 3.1 8B Instant model. It consists of a **FastAPI backend** (query generation, validation, execution) and a **React + Vite + TypeScript frontend** (console user interface).

The system enforces a strict **read-only security model** — the LLM is instructed to generate only read queries, and a multi-layered validator rejects any query containing write operators, dangerous stages, or references to non-schema fields before execution.

---

## Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                    React Frontend Console                     │
│  • Landing, Auth (JWT), Console, & CRUD Manager views         │
│  • Query input & history list                                 │
│  • Interactive tables with execution metrics                  │
│  • DB health connection status indicators                     │
└────────────────────────┬──────────────────────────────────────┘
                         │ POST /query  { "query": "..." }
                         ▼
┌───────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                            │
│                                                               │
│  config.py  ← Environment loading (.env), logging setup      │
│  routes.py  ← API endpoints, request timing                  │
│  llm.py     ← Groq LLM client, prompt injection, retry       │
│  validator.py ← Operator blocklist, field validation,        │
│                 pipeline stage validation, recursive scan     │
│  database.py ← MongoDB connection, health check              │
│  models.py  ← Pydantic request/response schemas              │
│  security.py ← Role-based permission definitions             │
│  main.py    ← App factory, CORS, lifespan events             │
└────────────────────────┬──────────────────────────────────────┘
                         │ PyMongo find() / aggregate()
                         ▼
┌───────────────────────────────────────────────────────────────┐
│                       MongoDB                                │
│  Database: payments                                           │
│  Collection: transactions                                     │
│  Indexes: timestamp↓, status↑, amount↑, transaction_id↑(U)  │
└───────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend framework | FastAPI | 0.110.0 |
| ASGI server | Uvicorn | 0.27.1 |
| Database driver | PyMongo | 4.6.1 |
| DNS resolver | dnspython | 2.4.2 |
| LLM provider | Groq SDK | 0.9.0 |
| Data validation | Pydantic | 2.6.1 |
| Environment config | python-dotenv | 1.0.1 |
| HTTP client | HTTPX | 0.26.0 |
| Testing | Pytest | 7.4.0 |
| Frontend | React + Vite + TS | 19.2+ |
| Container runtime | Docker + Compose | 3.9 |

---

## Backend Modules

### `config.py`

Centralized configuration module. Loads environment variables from `backend/.env` using an absolute path (no reliance on `cwd`).

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MONGODB_URI` | Yes | — | MongoDB connection string |
| `GROQ_API_KEY` | Yes | — | Groq API authentication key |
| `MAX_RESULTS` | No | `100` | Maximum documents returned per query |
| `LOG_LEVEL` | No | `INFO` | Python logging level |

Also configures structured logging with format: `timestamp | level | module | message`.

### `database.py`

MongoDB connection management:
- Uses `MONGODB_URI` from `config.py` (not raw `os.getenv`)
- Configured with `serverSelectionTimeoutMS=5000` and `connectTimeoutMS=5000`
- `tlsAllowInvalidCertificates=True` for MongoDB Atlas compatibility
- `check_health()` — pings the server and returns connection status + document count

### `llm.py`

LLM query generation:
- **Model:** Llama 3.1 8B Instant (via Groq)
- **Temperature:** 0 (deterministic)
- **Prompt:** Loaded from `prompts/mongo_query_prompt.txt`
- **Time injection:** Current UTC timestamp injected into system prompt via `{current_utc}` placeholder
- **Retry:** Up to 2 retries with linear backoff (1s × attempt) for `ConnectionError` / `TimeoutError`
- **Output parsing:** Validates JSON structure, expects `filter` or `pipeline` key

### `validator.py`

Multi-layered query validation:

1. **Top-level key validation** — only `filter`, `projection`, `sort`, `limit`, `pipeline` allowed
2. **Recursive operator scan** — blocks `$where`, `$expr`, `$function`, `$merge`, `$out`, `$set`, `$unset`, `$rename`, `$push`, `$pull`, `$addToSet`, `$pop`, `$inc`, `$mul`, `$min`, `$max`, `$currentDate`
3. **Filter field validation** — only schema-defined fields (`transaction_id`, `user_id`, `amount`, `currency`, `status`, `merchant`, `payment_method`, `timestamp`)
4. **Pipeline stage validation** — only `$match`, `$group`, `$sort`, `$limit`, `$skip`, `$project`, `$count`, `$addFields`, `$unwind`

### `routes.py`

API endpoints:
- `POST /query` — main query endpoint with timing, validation, and execution
- `GET /db-health` — MongoDB health check

### `models.py`

Pydantic schemas:
- `QueryRequest` — `query: str` (min 3 chars)
- `QueryResponse` — `generated_query`, `count`, `results`, `raw_response`, `execution_time_ms`

### `security.py`

Role-based permission definitions (currently defined but not enforced at the route level):
- `viewer` → `find` only
- `analyst` → `find`, `aggregate`
- `admin` → `find`, `aggregate`, `insert`, `update`

### `main.py`

FastAPI application factory:
- CORS middleware (allows all origins for development)
- Lifespan events: logs MongoDB connection status on startup
- API metadata: title, description, version

---

## Frontend

### React Console

The frontend is a React single-page application built using Vite, TypeScript, and TailwindCSS:

| Feature / Page | Description |
|---------|-------------|
| **Landing Page** | Platform landing and introductory layout |
| **Auth Views** | Secure registration and login forms with JWT handling |
| **Query Console** | Formatted query input, custom schema guide, history sidebar, and results layout |
| **Data Manager** | Multi-entity CRUD controller (analytical & data listings) |
| **Analytics Console** | Interactive dashboards and chart elements using Recharts |
| **State Management** | Local state via Zustand, server state via TanStack Query |
| **Container serving** | Containerized with a multi-stage Docker build served via Nginx |

---

## LLM Prompt Engineering

The system prompt (`prompts/mongo_query_prompt.txt`) is structured as:

1. **Role definition** — "Principal MongoDB DBA on a PRODUCTION system"
2. **Schema specification** — All fields with types, enums, and examples
3. **Current UTC timestamp** — Injected at runtime for time-relative queries
4. **Rules** — Read-only, no empty filters, uppercase status values, schema-only fields, JSON-only output
5. **Output format examples** — FIND query and AGGREGATION query templates
6. **Error format** — Structured refusal for unsafe/ambiguous queries

---

## Query Validation Pipeline

```
LLM Output (JSON)
    │
    ├──▶ Top-level key check ── reject if unknown keys
    │
    ├──▶ Recursive operator scan ── reject if blocklisted operator found
    │
    ├──▶ Filter field validation ── reject if non-schema field referenced
    │
    ├──▶ Pipeline stage validation ── reject if disallowed stage used
    │
    └──▶ ✅ SAFE — execute against MongoDB
```

---

## Database Design

### Collection: `payments.transactions`

```javascript
{
  _id: ObjectId,                         // Auto-generated
  transaction_id: "TXN000123",           // Unique
  user_id: "USER001",                    // 50 distinct users
  amount: 4599.50,                       // Merchant-specific range
  currency: "INR",                       // Always INR
  status: "SUCCESS",                     // SUCCESS | FAILED | PENDING
  merchant: "Amazon",                    // 10 merchants
  payment_method: "UPI",                 // UPI | CARD | NETBANKING
  timestamp: ISODate("2026-05-10T...")   // UTC, past 14 days
}
```

### Indexes

| Index | Direction | Purpose |
|-------|-----------|---------|
| `timestamp` | Descending | Fast temporal queries |
| `status` | Ascending | Status filtering |
| `amount` | Ascending | Range queries |
| `transaction_id` | Ascending (unique) | Deduplication |

### Seed Data

The `backend/seed_data/seed_transaction.py` script generates 500 records with:
- Realistic distribution (65% success, 20% failed, 15% pending)
- UPI-heavy payment methods (55% UPI, 30% card, 15% netbanking)
- Merchant-specific amount ranges (e.g., Swiggy: ₹100–₹1,500; Amazon: ₹500–₹15,000)
- Timestamps spread across the past 14 days

---

## Configuration

### Environment Variables

All loaded from `backend/.env`:

```bash
MONGODB_URI=mongodb://localhost:27017/payments
GROQ_API_KEY=gsk_...
MAX_RESULTS=100
LOG_LEVEL=INFO
```

### Frontend Environment

```bash
BACKEND_URL=http://127.0.0.1:8000   # Default, overridable
```

---

## Deployment

### Local (Development)

```bash
# Terminal 1 — Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm install && npm run dev

# Seed data (one-time)
python -m backend.seed_data.seed_transaction --drop
```

### Docker Compose

```bash
docker compose up --build
```

Services:
- `mongo` — MongoDB 7 with health check and persistent volume
- `backend` — FastAPI on port 8000 (depends on healthy mongo)
- `frontend` — React console on port 5173 (depends on backend, served via Nginx)

### Render (Cloud)

Pre-configured `render.yaml` deploys backend and frontend as separate web services. Requires manual configuration of `MONGODB_URI`, `GROQ_API_KEY`, and `BACKEND_URL` environment variables in the Render dashboard.

---

## Security Model

### Defense-in-Depth

| Layer | Mechanism |
|-------|-----------|
| **Prompt** | LLM instructed to refuse unsafe queries |
| **Structural** | Top-level key whitelist |
| **Operator** | 20+ blocked MongoDB operators |
| **Field** | Schema-field-only filter access |
| **Stage** | Pipeline stage whitelist |
| **Recursive** | Deep scan of all nested structures |
| **Network** | CORS middleware, timeouts |
| **Credential** | `.env` file isolation |

---

## API Reference

### `POST /query`

Translate a natural-language question into a MongoDB query and return results.

**Request:**
```json
{ "query": "Show all failed transactions from Amazon" }
```

**Response (200):**
```json
{
  "generated_query": {
    "filter": { "status": "FAILED", "merchant": "Amazon" },
    "projection": null,
    "sort": [["timestamp", -1]],
    "limit": 100
  },
  "count": 12,
  "results": [ ... ],
  "raw_response": { ... },
  "execution_time_ms": 456.2
}
```

### `GET /db-health`

**Response (200):**
```json
{ "status": "connected", "document_count": 500 }
```

### `GET /health`

**Response (200):**
```json
{ "status": "ok" }
```

---

*Last updated: May 2026*