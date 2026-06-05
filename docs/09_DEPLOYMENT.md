# Deployment & Infrastructure Guide — LLM Real-Time Database Query Engine

This document outlines deployment pipelines, container specifications, and cloud provider profiles.

## 1. Local Deployment (Manual Setup)

### Backend Services Startup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and configure `backend/.env` with MongoDB, Groq, and JWT secrets.
3. Install dependencies and start the Uvicorn development server:
   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Console Startup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install the frontend dependencies:
   ```bash
   npm install
   ```
3. Start the Vite server:
   ```bash
   npm run dev
   ```

---

## 2. Docker & Compose Orchestration (`docker-compose.yml`)

The system is fully containerized using Docker Compose to orchestrate dependencies.

### Services Architecture
* **`mongo`**: Runs `mongo:7` with health check command checking database connection state. Persists collections on `mongo_data` volume.
* **`redis`**: Runs `redis:7-alpine` with persistence enabled.
* **`chroma`**: Runs vector database `chromadb/chroma` persisting embeddings to `chroma_data` volume.
* **`backend`**: Multi-stage build (`backend/Dockerfile`). Depends on healthy `mongo` and `redis`.
* **`frontend`**: Built using Node 20 (`frontend/Dockerfile`) and served asynchronously via Nginx on port 5173.

### Startup Command
```bash
docker compose up --build -d
```

---

## 3. Render Cloud Deployment Configuration (`render.yaml`)

Deploys the backend and frontend services as independent cloud components:

### Backend Service Profile
* **Service Type**: Web Service
* **Runtime**: Python
* **Build Command**: `pip install -r requirements.txt`
* **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
* **Environment Variables**: Requires manual definition of `MONGODB_URI` and `GROQ_API_KEY`.

### Frontend Service Profile
* **Service Type**: Static Site
* **Build Command**: `npm install && npm run build`
* **Publish Path**: `dist`
* **Environment Variables**: Requires `VITE_API_URL` pointing to the live backend URL.
