# Onboarding & Developer Guide — LLM Real-Time Database Query Engine

This document provides a starting point for new developers onboarding onto the Enterprise AI Database Query platform.

## 1. Local Environment Requirements

Ensure the following environments are installed locally:
* **Python** (`>= 3.12`)
* **Node.js** (`>= 20.0`)
* **Docker & Compose** (For quick infrastructure setup)
* **MongoDB Compass** (Optional — for database inspection)

---

## 2. Fast Track (Docker Compose Setup)

The fastest way to spin up the entire application stack is with Docker Compose:

1. Clone the repository and navigate to the project root.
2. Verify docker is running.
3. Start the services:
   ```bash
   docker compose up --build
   ```
4. Access the React Console at `http://localhost:5173`.
5. Access the FastAPI documentation at `http://localhost:8000/docs`.

---

## 3. Local Development Architecture Map

When building features, use the following files:

* **FastAPI Entrypoint**: [`backend/app/main.py`](file:///d:/LLMAutomatedDB/backend/app/main.py) — Register routers, middleware, and configure startup lifespan dependencies here.
* **LLM Prompts & Configuration**: [`backend/prompts/mongo_query_prompt.txt`](file:///d:/LLMAutomatedDB/backend/prompts/mongo_query_prompt.txt) — Tweak this file to modify database schema descriptions or LLM rules.
* **Translation Service logic**: [`backend/app/services/ai_service.py`](file:///d:/LLMAutomatedDB/backend/app/services/ai_service.py) — Controls the core LLM execution, query hashing, and caching mechanisms.
* **Safety Validator**: [`backend/app/iqr/validator.py`](file:///d:/LLMAutomatedDB/backend/app/iqr/validator.py) — Add disallowed operators or fields to ensure queries remain read-only.
* **Frontend Entrypoint**: [`frontend/src/main.tsx`](file:///d:/LLMAutomatedDB/frontend/src/main.tsx) — Main rendering file.
* **Frontend Routing**: [`frontend/src/routes/index.tsx`](file:///d:/LLMAutomatedDB/frontend/src/routes/index.tsx) — Register new pages and route permissions here.

---

## 4. Seeding the Database

To run testing scenarios with realistic transactions data, seed the database:
```bash
cd backend
python -m seed_data.seed_transaction --drop
```
This drops the existing transactions collections and populates 500 transaction records with variable amounts, payment methods, status types, and timestamps distributed over the past 14 days.
