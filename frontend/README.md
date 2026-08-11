# Ask Your Data — frontend

A React + Vite + TypeScript + Tailwind UI for the text-to-SQL agent, built for
non-technical stakeholders: ask a question in plain English, get a written
answer, a chart (when the result shape supports one), and a data table. The
generated SQL is tucked behind a "How was this calculated?" section for anyone
who wants it.

## Local development

```bash
npm install
cp .env.example .env.local   # points VITE_API_URL at your local backend
npm run dev                  # http://localhost:7173
```

The backend must be running separately with CORS open for this origin — see
the root `README.md` and `app/main.py` (`ALLOWED_ORIGINS` env var).

## Building for production

```bash
npm run build      # outputs to dist/
npm run preview    # sanity-check the production build locally
```

## Deploying

This is a static site (no server-side code), so it can be hosted for free on
Netlify. The FastAPI backend it talks to is a separate Python process and
**cannot** run on Netlify — it needs its own host. Render's free tier works
well for a small demo like this one. The two are deployed independently and
wired together with an environment variable + a CORS allowlist.

### 1. Deploy the backend to Render (free)

1. Push this repo to GitHub (if it isn't already).
2. Go to [render.com](https://render.com) → **New** → **Web Service** → connect
   the repo.
3. Configure:
   - **Root directory**: leave blank (repo root)
   - **Runtime**: Python 3
   - **Build command**: `pip install -r requirements.txt && python scripts/seed_db.py`
   - **Start command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance type**: Free
4. Add environment variables (Render dashboard → Environment):
   - `GROQ_API_KEY` (and `GEMINI_API_KEY` if you use the fallback) — same
     values as your local `.env`
   - `ALLOWED_ORIGINS` — set this **after** step 2 below, once you know your
     Netlify URL, e.g. `https://your-site-name.netlify.app`
5. Deploy. Render gives you a URL like `https://your-api.onrender.com` — copy
   it, you'll need it next.

Notes on the free tier: the service spins down after periods of inactivity,
so the first request after a while sleeping can take ~30–60 seconds to wake
up — the frontend's loading state covers this, it just takes longer than
usual on a cold start. The seeded SQLite file (`data/store.db`) is rebuilt on
every deploy since Render's free tier has no persistent disk; that's fine
here since the seed script is deterministic.

### 2. Deploy the frontend to Netlify (free)

**Option A — Netlify UI:**
1. Go to [app.netlify.com](https://app.netlify.com) → **Add new site** →
   **Import an existing project** → connect the same GitHub repo.
2. Configure:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
3. Add an environment variable: `VITE_API_URL` = your Render backend URL from
   step 1 (e.g. `https://your-api.onrender.com`).
4. Deploy. Netlify gives you a URL like `https://your-site-name.netlify.app`.

**Option B — Netlify CLI:**
```bash
npm install -g netlify-cli
cd frontend
netlify deploy --build --prod
```
(Set `VITE_API_URL` in the Netlify site's dashboard under **Site
configuration → Environment variables** either way — the CLI won't prompt
for it.)

A `netlify.toml` is included in this folder so the build/publish settings
above are picked up automatically if you use Option B or link the site via
the CLI.

### 3. Close the loop: update backend CORS

Now that you have the Netlify URL, go back to the Render dashboard and set
`ALLOWED_ORIGINS` to include it (comma-separated if you keep localhost too):

```
ALLOWED_ORIGINS=https://your-site-name.netlify.app,http://localhost:7173
```

Redeploy the backend (Render redeploys automatically when you save an env
var). Reload the Netlify site and it should be able to reach the API.

### Custom domains

Both Netlify and Render support attaching a custom domain for free (you pay
only for the domain itself, if you want one). If you do this, add the custom
domain to `ALLOWED_ORIGINS` too.
