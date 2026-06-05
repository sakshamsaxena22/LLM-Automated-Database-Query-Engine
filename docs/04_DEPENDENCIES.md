# Dependencies Analysis — LLM Real-Time Database Query Engine

This document details all packages, utilities, frameworks, and testing tools configured for both the backend and frontend subsystems.

## 1. Backend Subsystem Dependencies (`backend/requirements.txt`)

### Core API Framework
* **FastAPI** (`>=0.115.0`) — Modern, high-performance web framework for building APIs.
* **Uvicorn** (`>=0.30.0` with `[standard]`) — Lightweight ASGI server implementation.
* **Pydantic** (`>=2.9.0`) & **Pydantic Settings** (`>=2.5.0`) — Modern data validation and environment variable configuration settings management.

### Database Adapters
* **Motor** (`>=3.6.0`) & **PyMongo** (`>=4.9.0`) — Non-blocking, asynchronous MongoDB driver client adapter.
* **DNSPython** (`>=2.6.0`) — DNS resolver client (mandatory for Atlas connection resolutions).

### Security, Cryptography & Auth
* **Python-Jose** (`>=3.3.0` with `[cryptography]`) — JWT generation, parsing, and signing functions.
* **Passlib** (`>=1.7.4`) & **Bcrypt** (`>=4.0,<5.0`) — Secure password hashing and hash verification.
* **Python-Multipart** (`>=0.0.9`) — Parser for form file transfers.

### Cache & External Connections
* **Redis** (`>=5.0.0`) — Async connection client for caching query states.
* **Groq** (`>=0.11.0`) — Official SDK client connecting the backend to Groq Cloud Llama API services.
* **HTTPX** (`>=0.27.0`) — Modern async HTTP client.

---

## 2. Frontend Subsystem Dependencies (`frontend/package.json`)

### Core Libraries
* **React** & **React DOM** (`^19.2.6`) — Core reactive UI renderer.
* **React Router DOM** (`^7.6.1`) — Router management.
* **TypeScript** (`~6.0.2`) — Static type compiler.
* **Vite** (`^8.0.12`) — Next-generation frontend bundler tool.

### State Management & Networking
* **Zustand** (`^5.0.5`) — Lightweight, client-side state slices manager.
* **TanStack React Query** (`^5.75.5`) — Server-side data-fetching state synchronizer.
* **Axios** (`^1.9.0`) — Promised-based HTTP request builder.

### Forms & Schema Validations
* **React Hook Form** (`^7.56.4`) & **Zod** (`^3.25.20`) — Dynamic forms manager with validation schema support.

### Styling & Animation
* **TailwindCSS** (`^4.1.7`) — Utility-first CSS style definitions.
* **Framer Motion** (`^12.12.1`) — Transition and micro-animation controller.
* **Lucide React** (`^0.510.0`) & **Recharts** (`^2.15.3`) — Icon packs and analytical chart visualizations.
* **Sonner** (`^2.0.7`) — Toast alerts.
