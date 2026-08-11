# Text-to-SQL agent

Turns a natural-language question into SQL, validates it, runs it against a
sandboxed read-only database, and retries automatically on failure — with a
free-tier-only LLM stack (Groq primary, Gemini fallback).

## Why this exists

Most text-to-SQL demos are a single prompt-and-hope call. This one adds the
three things that separate an agent from a wrapper:

1. **Schema-aware prompting** — only relevant tables are retrieved and sent
   to the model, not the whole schema every time.
2. **Validation before execution** — generated SQL is parsed with `sqlglot`,
   restricted to `SELECT`-only, checked against known tables, and capped with
   a row limit, before it ever touches the database.
3. **Self-correcting retry loop** — if validation or execution fails, the
   error is fed back to the model for up to 3 attempts.

## Architecture

```
question -> schema retrieval -> LLM (Groq/Gemini) -> SQL validator
    -> read-only execution -> retry-on-error (up to 3x) -> result + NL summary
```

## Setup

```bash
git clone <your-repo-url>
cd text-to-sql-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# add your free Groq key from https://console.groq.com
# (optional) add a free Gemini key from https://aistudio.google.com/apikey

python scripts/seed_db.py
```

## Run

CLI/API:
```bash
uvicorn app.main:app --reload
# POST http://localhost:8000/ask   {"question": "top 5 customers by spend"}
```

Web UI (React + Vite):
```bash
cd frontend
npm install
npm run dev
# open http://localhost:7173
```

See `frontend/README.md` for deployment instructions (Netlify + Render).

## Evaluate

```bash
python -m eval.run_eval
```

Scores the agent against `eval/questions.json` — 14 hand-written questions
spanning simple lookups, aggregation, joins, ranking, time filters, and
deliberately unanswerable questions (to check the agent declines gracefully
instead of hallucinating). Scoring is by execution match (same result set),
not SQL text match, since there are many valid ways to write the same query.

## Dataset

A generated e-commerce dataset: `customers`, `products`, `orders`,
`order_items`. Seed script is deterministic (`random.seed(42)`), so a fresh
clone reproduces the same data.

## Design notes / tradeoffs

- **Free-tier only.** Groq is primary for speed; Gemini is the fallback if
  Groq errors or rate-limits. Swap providers by editing `LLMClient`.
- **Schema retrieval is keyword-overlap, not embeddings**, since 4 tables
  doesn't need a vector DB. If you extend this to a larger schema, swap
  `schema_store.py`'s `_score()` for `sentence-transformers` + Chroma
  embeddings — the rest of the pipeline doesn't need to change.
- **SQLite read-only enforcement** uses `mode=ro` file URI. For Postgres,
  replace this with a dedicated read-only DB role instead.
