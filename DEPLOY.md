# Deployment Guide — Restock Copilot Lite

This guide outlines how to deploy the containerized FastAPI backend to any cloud platform that supports Docker (e.g., Render, Railway, Fly.io).

---

## 1. Required Cloud Environment Secrets
Before launching your service, configure the following **three environment variables** in your hosting dashboard settings:

| Secret Name | Value Description | Example Value |
|---|---|---|
| `LLM_BASE_URL` | Base URL for AMD Token Factory | `https://notebooks.amd.com/tokenfactory/v1` |
| `LLM_API_KEY` | Your AMD AI Developer API key | `amd_live_xxxxxxxxxxxxxxxx` |
| `LLM_MODEL` | Exact model name selected in Token Factory | `meta-llama/Llama-3.1-8B-Instruct` |

> ⚠️ **IMPORTANT SECURITY NOTICE:**  
> Never commit `.env` into Git. Secrets must only be entered directly in your hosting platform's web dashboard settings.

---

## 2. Deploying on Render (Recommended Free/Easy Option)
1. Push your repository to GitHub.
2. Sign in to [Render.com](https://render.com) and click **New +** → **Web Service**.
3. Connect your GitHub repository.
4. Select **Docker** as the Runtime environment.
5. In **Environment Variables**, add:
   * `LLM_BASE_URL`
   * `LLM_API_KEY`
   * `LLM_MODEL`
6. Click **Create Web Service**.
7. Render will build the container and provide your public URL: `https://restock-copilot-xxxx.onrender.com`.

---

## 3. Deploying on Railway
1. Sign in to [Railway.app](https://railway.app) and create a **New Project**.
2. Select **Deploy from GitHub repo**.
3. Under service **Variables**, add `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL`.
4. Under service **Settings** → **Networking**, click **Generate Domain** to get your public HTTPS URL.

---

## 4. Post-Deployment Verification (Submission Checklist)
Once deployed:
1. Open the public URL in your browser (and on mobile data on your phone).
2. Verify the 8-week replay banner loads with comparison statistics.
3. Verify the 3 product cards display with stock and reorder quantities.
4. Click **Explain with AMD AI** on a product card:
   * Verify the badge shows **`live (AMD)`** (or **`saved`** if credentials are still pending).
   * Verify the 3-sentence plain English reasoning text renders properly.
