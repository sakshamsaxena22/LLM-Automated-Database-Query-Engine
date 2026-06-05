# Deployment Guide: Enterprise AI Data Management SaaS Platform

This guide provides step-by-step instructions for deploying and running the **Enterprise AI Data Management Platform**. 

It covers local development, containerized deployment using Docker Compose, and cloud deployment (specifically Render), and clarifies the status of the database connection.

---

## 🔍 Database Connectivity: Analysis & Status

Based on an audit of the files and active network checks, **your database is already connected**. You do **not** need to deploy or manage a separate database for development and testing.

Here are the details:
1. **Cloud Connection Configured**: The backend loads its configuration from `backend/.env` (and root `.env`), which has a pre-configured `MONGODB_URI` pointing to a cloud-hosted **MongoDB Atlas** cluster:
   ```env
  
   ```
2. **Active & Reachable**: We verified this connection programmatically. The MongoDB Atlas instance is fully online and accessible.
3. **Pre-Seeded Databases**: The database cluster is already populated with the necessary collections and seed data:
   * **`payments` database**: Contains the `transactions` collection pre-loaded with **500 sample transactions**.
   * **`enterprise_db` database**: Contains user roles, audit trails, and history collections (`users`, `audit_logs`, `query_history`).

> [!NOTE]
> Because this cloud-hosted database is pre-configured and seeded, you can run the application immediately without installing or deploying any database locally.
>
> If you want to use a private database or deploy your own local copy, you can run a local MongoDB instance inside Docker Compose or configure a custom MongoDB Atlas connection.

---

## 🏗️ System Architecture

Before deploying, it helps to understand the components:
* **Backend API**: A Python **FastAPI** application running on port `8000`. It handles JWT auth, roles (RBAC), and uses LLM (via Groq API) to generate safe read-only queries.
* **Frontend UI**: A **React + Vite + TypeScript** console running on port `5173`.
* **Database**: MongoDB (Atlas Cloud URI is default; local container is optional).
* **Caching**: Redis (Optional; local container provided for session caching).

---

## 🚀 Deployment Options

Choose the deployment method that fits your environment:

### Option A: Local Development (Manual Setup)

Run the backend and frontend separately on your machine. Useful for quick debugging.

#### Prerequisites
* **Python 3.10+**
* **Node.js 18+** & **npm**

#### Step 1: Run the Backend
1. Open a terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   * *Backend API Docs:* View Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs)

5. **Seed the database (Optional)**:
   To seed your database locally (from the `backend/` directory):
   ```bash
   python -m seed_data.seed_transaction
   ```

#### Step 2: Run the Frontend
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   * *Frontend Console:* Access the dashboard at [http://localhost:5173](http://localhost:5173)

---

### Option B: Containerized Deployment (Docker Compose)

Run the entire stack (including local MongoDB, Redis, and ChromaDB cache instances) inside Docker.

#### Prerequisites
* **Docker** & **Docker Compose** installed.

#### Step 1: Verify Configuration Files
1. Check that `docker-compose.yml` in the root matches your ports.
2. In Docker mode:
   * **Backend** uses `./backend/.env` environment settings.
   * **Frontend** uses `VITE_API_URL=http://localhost:8000` to contact the backend.

#### Step 2: Run the Stack
Run the following command in the project root directory:
```bash
docker compose up --build
```

This starts:
* **Local MongoDB**: `mongodb://localhost:27017`
* **Local Redis**: `redis://localhost:6379`
* **Backend API**: `http://localhost:8000`
* **React Frontend**: `http://localhost:5173` (built and served securely via Nginx)

#### Step 3: Seed Local Database (Optional)
If you are running a local MongoDB instance inside Docker Compose and want to populate it with test data:
```bash
# Seed transactions database inside the container
docker compose exec backend python -m seed_data.seed_transaction
```

---

### Option C: Cloud Deployment (Production Setup)

For a production deployment, we recommend deploying the **Frontend to Vercel** and the **Backend to Render or Railway**.

---

#### 1. Frontend Deployment on Vercel

Vercel provides optimized hosting for Vite-based React single-page applications.

##### Step 1: Prepare the Code
Ensure you have the [vercel.json](file:///d:/LLMAutomatedDB/frontend/vercel.json) file in your `frontend` directory. This is already created and configures SPA rewrites so that page refreshes on sub-routes do not cause `404 Not Found` errors.

##### Step 2: Import Project on Vercel
1. Log in to [Vercel](https://vercel.com).
2. Click **Add New** > **Project** and select your GitHub repository containing the project.
3. In the configuration settings, modify the following fields:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Vite` (automatically detected)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Expand the **Environment Variables** section and add the following variable:
   - `VITE_API_BASE_URL`: The full URL of your deployed backend (e.g., `https://llm-db-backend.onrender.com/api/v1` or `https://backend-production.up.railway.app/api/v1`).
     *(Note: If you do not set this, the client will fall back to `http://localhost:8000/api/v1`.)*

##### Step 3: Deploy
Click **Deploy**. Once the build finishes, Vercel will provide a public URL for your frontend application (e.g., `https://your-project.vercel.app`).

---

#### 2. Backend Deployment on Render

Render is a robust PaaS platform that can deploy FastAPI applications as Web Services.

##### Step 1: Create a Render Web Service
1. Log in to [Render](https://render.com).
2. Click **New** > **Web Service**.
3. Connect your GitHub repository.
4. Set the following configuration options:
   - **Name**: `llm-db-backend`
   - **Language**: `Python 3` (or choose `Docker` if you wish to build from the backend Dockerfile)
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

##### Step 2: Configure Environment Variables
Expand the **Advanced** section and add the following variables:
- `MONGODB_URI`: *Your MongoDB Atlas connection URI*
- `GROQ_API_KEY`: *Your Groq API authentication key*
- `DATABASE_NAME`: `enterprise_db` (or your custom database name)
- `JWT_SECRET_KEY`: *A long, secure random string for signing JWT tokens*
- `CORS_ORIGINS`: *The URL of your deployed Vercel frontend* (e.g., `https://your-project.vercel.app`)

##### Step 3: Apply & Deploy
Click **Create Web Service**. Render will provision a container, install dependencies, and launch FastAPI. You can monitor progress in Render's logs.

---

#### 3. Backend Deployment on Railway

Railway is an alternative developer-centric cloud platform offering extremely fast deployments.

##### Step 1: Create a New Project on Railway
1. Log in to [Railway](https://railway.app).
2. Click **New Project** > **Deploy from GitHub repo**.
3. Select your repository.
4. When prompted, select to configure settings first or configure them right after import.
5. In the service settings, specify:
   - **Root Directory**: `backend`
   - **Build Command**: (Nixpacks detects Python/FastAPI automatically, but you can override if needed)
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

##### Step 2: Configure Environment Variables
Go to the **Variables** tab of the backend service and add:
- `MONGODB_URI`: *Your MongoDB Atlas connection URI*
- `GROQ_API_KEY`: *Your Groq API authentication key*
- `DATABASE_NAME`: `enterprise_db`
- `JWT_SECRET_KEY`: *A long, secure random string*
- `CORS_ORIGINS`: *The URL of your deployed Vercel frontend* (e.g., `https://your-project.vercel.app`)
- `PORT`: (Railway automatically assigns a random port and binds it, but setting it explicitly is a good practice or Railway will inject it into `$PORT`)

##### Step 3: Deploy
Railway will trigger an automatic build and expose a public domain. You can generate a domain under the **Settings** tab.

---

## 🔒 Security Post-Deployment Checklist

Before exposing the application to the public internet:
1. **Update Secret Key**: In production, change the `JWT_SECRET_KEY` in your backend environment variables from the default fallback to a long cryptographically secure random string.
2. **Review CORS Origins**: Restrict `CORS_ORIGINS` in your environment settings to the specific domains where your frontend is hosted instead of allowing all or localhost.
3. **Database Credentials**: Ensure your MongoDB connection user has only the permissions required (`readWrite` on `enterprise_db` and `read` on `payments` database for maximum security).
