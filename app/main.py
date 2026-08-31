import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.agent import answer_question

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure sqlite database exists (crucial when freshly deployed on Render/containers)
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "store.db"
if not DB_PATH.exists() or DB_PATH.stat().st_size == 0:
    try:
        from scripts.seed_db import build_db
        logger.info("Initializing and seeding database at %s...", DB_PATH)
        build_db()
    except Exception as e:
        logger.warning("Could not auto-seed database: %s", e)

app = FastAPI(title="Text-to-SQL Agent")

# CORS configuration
raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
if raw_origins.strip() == "*":
    _allowed_origins = ["*"]
else:
    _allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_origin_regex=r"^https?://.*$",  # Fallback to allow netlify & localhost origins
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "question": "",
            "sql": None,
            "columns": [],
            "rows": [],
            "summary": None,
            "provider": None,
            "attempts": 0,
            "error": f"Server error: {str(exc)}",
        },
    )


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    question: str
    sql: str | None
    columns: list[str]
    rows: list[tuple]
    summary: str | None
    provider: str | None
    attempts: int
    error: str | None


@app.post("/ask", response_model=QuestionResponse)
def ask(req: QuestionRequest) -> QuestionResponse:
    try:
        result = answer_question(req.question)
        return QuestionResponse(**result.__dict__)
    except Exception as e:
        logger.exception("Error processing question: %s", e)
        return QuestionResponse(
            question=req.question,
            sql=None,
            columns=[],
            rows=[],
            summary=None,
            provider=None,
            attempts=1,
            error=str(e),
        )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "has_groq_key": bool(os.getenv("GROQ_API_KEY")),
        "has_gemini_key": bool(os.getenv("GEMINI_API_KEY")),
        "db_exists": DB_PATH.exists(),
    }
