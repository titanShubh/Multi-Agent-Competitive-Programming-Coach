# Deploying Socratic CP Coach to Production (Option B)

This guide walks you through deploying the **Multi-Agent Competitive Programming Coach** to production using cloud-managed PaaS platforms:
* **Frontend**: Next.js deployed on **Vercel**
* **Backend**: FastAPI (with Docker) deployed on **Render** or **Railway**
* **Databases**: Managed cloud instances of **PostgreSQL**, **Redis**, and **Qdrant Cloud**

---

## 1. Database Provisioning

### Managed PostgreSQL & Redis (Railway / Render)
You can provision a managed PostgreSQL database and a Redis instance instantly:
1. **Railway**: Click **New Project** -> **Provision PostgreSQL** and **Provision Redis**.
2. Copy their respective connection URLs:
   * `DATABASE_URL` (format: `postgresql://user:pass@host:port/db`)
   * `REDIS_URL` (format: `redis://default:pass@host:port/0`)

### Managed Vector DB (Qdrant Cloud)
To run problem similarity searches in production, use Qdrant's managed cloud:
1. Go to [Qdrant Cloud](https://cloud.qdrant.io/) and register for a free account (includes a free cluster with 1GB storage).
2. Create a cluster and copy:
   * **Host URL** (e.g., `xxxx-xxxx.eu-central.aws.qdrant.io`)
   * **API Key** (if you enable access control)

---

## 2. Backend Deployment (Render or Railway)

Both Render and Railway can build and deploy the backend automatically using the `backend/Dockerfile` file.

### Steps on Render:
1. Click **New** -> **Web Service**.
2. Connect your GitHub repository.
3. Configure the following parameters:
   * **Root Directory**: `backend`
   * **Runtime**: `Docker`
   * **Dockerfile Path**: `Dockerfile` (relative to the `backend` root)
4. Add the following **Environment Variables**:
   * `OPENAI_API_KEY`: Your OpenAI API key.
   * `DATABASE_URL`: The production PostgreSQL connection string.
   * `REDIS_URL`: The production Redis connection string.
   * `QDRANT_HOST`: Your Qdrant Cloud host URL.
   * `QDRANT_PORT`: `6333`
   * `JWT_SECRET`: A secure random string (e.g. `openssl rand -hex 32`).
   * `CORS_ORIGINS`: JSON list pointing to your Vercel URL (e.g., `["https://cp-coach.vercel.app"]`).
5. Click **Deploy**. Render will build the Docker image and start the backend service. Copy the URL of the deployed backend (e.g., `https://cp-coach-backend.onrender.com`).

---

## 3. Frontend Deployment (Vercel)

Vercel is the natural host for Next.js applications and deploys directly from your Git pushes.

### Steps:
1. Log in to [Vercel](https://vercel.com/) and click **Add New** -> **Project**.
2. Select your Git repository.
3. Configure project settings:
   * **Framework Preset**: `Next.js`
   * **Root Directory**: `frontend`
4. Expand **Environment Variables** and add:
   * `NEXT_PUBLIC_API_URL`: The URL of your deployed backend service + `/api` (e.g., `https://cp-coach-backend.onrender.com/api`).
5. Click **Deploy**. Vercel will build the frontend and provide you with a production URL (e.g., `https://cp-coach.vercel.app`).

*Note: Once your Vercel URL is active, don't forget to update the `CORS_ORIGINS` variable in your Backend service configuration to match this URL, then trigger a quick reload/redeployment.*

---

## 4. Verification

After both services are deployed:
1. Visit your Vercel frontend URL.
2. Sign up for a new account (this hits the backend, which automatically creates the tables in your production PostgreSQL database).
3. Paste a CP problem statement to verify the problem analysis and Socratic streaming dialog work cleanly!
