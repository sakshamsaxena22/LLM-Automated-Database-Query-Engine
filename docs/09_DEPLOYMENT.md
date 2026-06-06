# Deployment & Infrastructure Guide — Enterprise AI SaaS Platform

This document outlines deployment pipelines, container specifications, and cloud provider profiles.

## 1. Production Architecture Overview

The production deployment moves away from local instances in favor of fully managed serverless infrastructure:
* **Database Layer**: Hosted on **MongoDB Atlas** (shared cluster or dedicated tiers). Provides automated backups, TLS encryption, and global availability.
* **Caching Layer**: Powered by **Upstash Redis** (serverless). Restricts Redis cache management to standard Redis URI endpoints using secure authentication over SSL, avoiding local connection bottlenecks.
* **Backend Layer**: Deployed to **Render** or **Railway** as a Python Web Service running FastAPI.
* **Frontend Layer**: Deployed to **Vercel** as a static single-page React application with path rewrites enabled.

---

## 2. Environment Variables & Secret Configuration

To wire these components together, the following production configurations are required:

### Backend Environment Settings
```env
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/payments?retryWrites=true&w=majority
DATABASE_NAME=enterprise_db
GROQ_API_KEY=gsk_...
LLM_MODEL=llama-3.1-8b-instant
JWT_SECRET_KEY=your-secure-production-signature-hash
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
REDIS_URL=rediss://default:<password>@<endpoint>.upstash.io:<port>
CORS_ORIGINS=https://your-frontend.vercel.app
MAX_RESULTS=100
LOG_LEVEL=INFO
```

### Frontend Environment Settings
```env
VITE_API_BASE_URL=https://your-backend.onrender.com/api/v1
```

---

## 3. Deployment Steps

### Option A: Cloud Deployment (Render/Vercel)

#### 1. Backend on Render/Railway
* Register a new **Web Service** tied to your GitHub repo.
* **Root Directory**: `backend`
* **Build Command**: `pip install -r requirements.txt`
* **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
* Bind env vars listed above.

#### 2. Frontend on Vercel
* Connect the repository, set **Root Directory** to `frontend`.
* Vercel will auto-detect **Vite** and configure the build settings.
* Bind `VITE_API_BASE_URL` env variable.
* Ensure SPA routing redirection is active (configured in [vercel.json](file:///d:/LLMAutomatedDB/frontend/vercel.json)).

### Option B: Local Setup (Using Cloud DB + Cache)
1. Configure `backend/.env` with your MongoDB Atlas and Upstash Redis URIs.
2. In the `backend` folder, run:
   ```bash
   venv\Scripts\activate
   uvicorn app.main:app --reload --port 8000
   ```
3. In the `frontend` folder, run:
   ```bash
   npm run dev
   ```
