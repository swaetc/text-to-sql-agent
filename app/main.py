import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.core.agent import answer_question

app = FastAPI(title="Text-to-SQL Agent")

_default_origins = "http://localhost:7173,http://127.0.0.1:7173"
_allowed_origins = os.getenv("ALLOWED_ORIGINS", _default_origins).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
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
    result = answer_question(req.question)
    return QuestionResponse(**result.__dict__)


@app.get("/health")
def health():
    return {"status": "ok"}
