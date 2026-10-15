# PayPath MSME — Vercel Deployment Guide

This guide describes how to deploy **PayPath MSME** (React 18 + Vite Frontend with FastAPI Python Serverless Backend) to [Vercel](https://vercel.com).

---

## 1. Architecture Overview on Vercel

- **Frontend:** Static React Single Page Application (SPA) built via Vite, served globally across Vercel's Edge CDN.
- **Backend API:** FastAPI application routed as a serverless function via `api/index.py` handling `/api/(.*)`.
- **Database & Persistence:** SQLite database located in the serverless writable volume `/tmp/paypath.db` with automated seed initialization on cold start.
- **Configuration:** Managed via `vercel.json` and root `package.json` with dependency manifests (`requirements.txt`).

---

## 2. Option A: 1-Click GitHub Deployment (Recommended)

Because the repository is already pushed to GitHub at [Lovish-creator/paypath-msme](https://github.com/Lovish-creator/paypath-msme.git), this is the fastest and most reliable deployment method:

1. **Log in to Vercel:**
   - Go to [vercel.com](https://vercel.com) and sign in with your GitHub account.

2. **Import Repository:**
   - Click **Add New...** → **Project** (or navigate to [vercel.com/new](https://vercel.com/new)).
   - Find **`Lovish-creator/paypath-msme`** in your Git list and click **Import**.

3. **Configure Project:**
   - **Framework Preset:** `Vite` (automatically detected from `vercel.json`).
   - **Root Directory:** `./` (leave default).
   - **Build Command:** `npm run build` (pre-configured in root `package.json`).
   - **Output Directory:** `frontend/dist` (pre-configured in `vercel.json`).

4. **Environment Variables (Optional):**
   - In the **Environment Variables** section, you may add:
     - `SECRET_KEY`: Any unpredictable 32+ character random string (e.g. `paypath-msme-production-jwt-secret-xyz-2026`).
     - `ENVIRONMENT`: `development` (or `production` if using a custom PostgreSQL database).
     - `ENABLE_DEMO_SEEDING`: `true` (auto-seeds the initial MSME workspace).

5. **Deploy:**
   - Click **Deploy**.
   - Vercel will install the Python dependencies (`requirements.txt`), build the Vite frontend (`npm run build`), and deploy the full stack.
   - You will receive a live URL: `https://paypath-msme.vercel.app` (or custom name).

---

## 3. Option B: CLI Deployment from Terminal

If you prefer to deploy from your terminal:

```bash
# 1. Login to Vercel (opens browser verification)
npx vercel login

# 2. Deploy preview to Vercel
npx vercel

# 3. Deploy to production
npx vercel --prod
```

When prompted:
- **Set up and deploy?** → `Y`
- **Which scope?** → Select your Vercel account
- **Link to existing project?** → `N`
- **Project name?** → `paypath-msme` (or press enter)
- **In which directory is your code located?** → `./`
- **Want to modify build settings?** → `N` (settings are auto-read from `vercel.json`)

---

## 4. Verification Checklist Post-Deployment

Once deployed, verify:
- [ ] **Home page:** Loads the dashboard and MSME workspace.
- [ ] **API Health Check:** Visit `https://<your-project>.vercel.app/api` (should return JSON status `{"status": "active", ...}`).
- [ ] **Interactive Ledger:** Check `/invoices` to view pre-seeded records.
- [ ] **PDF Generator:** Test generating and downloading pre-litigation PDF reports under Cases.
- [ ] **Supplier Matching:** Test contextual vendor recommendations in the B2B directory.
