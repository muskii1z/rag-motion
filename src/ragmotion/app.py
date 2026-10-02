"""Minimal local web app for asking the exercise database questions (Step 10).

    browser (static/index.html)  --POST /api/ask-->  this server  -->  rag.answer_question()

The browser never sees the OpenRouter key: only this server calls the LLM.

Run from the project folder:
    uv run uvicorn ragmotion.app:app --host 127.0.0.1 --port 8010 --reload
Then open http://127.0.0.1:8010
"""

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from ragmotion.config import settings
from ragmotion.db import get_connection
from ragmotion.errors import friendly_message
from ragmotion.ingestion import load_sources
from dataclasses import asdict

from ragmotion.agent import run_turn
from ragmotion.rag import answer_question

STATIC_DIR = Path(__file__).parent / "static"
log = logging.getLogger("ragmotion")

app = FastAPI(title="rag-motion", description="Grounded answers from the exercise knowledge base.")


MAX_QUESTION_CHARS = 500


class AskRequest(BaseModel):
    question: str  # length is checked in ask(), so the user gets a plain sentence, not a validation dump
    k: int = Field(default=5, ge=1, le=10)  # how many exercises AND how many passages to retrieve


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/program", include_in_schema=False)
def program_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "program.html")


@app.get("/api/info")
def info() -> dict:
    """What the assistant knows and which models it uses, for the sidebar and header."""
    try:
        conn_ctx = get_connection()
    except Exception as e:
        status, message = friendly_message(e)
        raise HTTPException(status_code=status, detail=message) from e
    with conn_ctx as conn:
        chunk_counts = dict(conn.execute(
            "SELECT source_id, count(*) FROM document_chunk WHERE embedding IS NOT NULL GROUP BY source_id"
        ).fetchall())
        exercise_count = conn.execute("SELECT count(*) FROM exercise WHERE embedding IS NOT NULL").fetchone()[0]
    sources = [
        {"id": s.id, "title": s.title, "type": s.type, "passages": chunk_counts.get(s.id, 0)}
        for s in load_sources().values()
    ]
    return {
        "llm_model": settings.llm_model,
        "agent_model": settings.agent_model or settings.llm_model,
        "embedding_model": settings.embedding_model,
        "retrieval": "semantic",
        "sources": sources,
        "exercises": exercise_count,
    }


@app.post("/api/ask")
def ask(req: AskRequest) -> dict:
    question = req.question.strip()
    if len(question) < 3:
        raise HTTPException(status_code=400, detail="Please type a question.")
    if len(question) > MAX_QUESTION_CHARS:
        raise HTTPException(status_code=400, detail=f"Questions can be up to {MAX_QUESTION_CHARS} characters; "
                                                    f"this one has {len(question)}. Please shorten it.")
    try:
        # Failures inside are also recorded on the answer_question trace in LangSmith.
        r = answer_question(question, k_exercises=req.k, k_passages=req.k, use_filters=settings.use_filters)
    except Exception as e:
        log.exception("Failed to answer %r", req.question)  # full details for debugging
        status, message = friendly_message(e)
        raise HTTPException(status_code=status, detail=message) from e

    return {
        "question": r.question,
        "answer": r.answer.answer,
        "evidence_coverage": r.answer.evidence_coverage,
        "gaps": r.answer.gaps,
        "general_guidance": r.answer.general_guidance,
        "citation_problems": r.citation_problems,
        "exercises": [
            {**h.model_dump(), "id": h.slug, "rank": i, "cited": h.slug in r.cited}
            for i, h in enumerate(r.exercises, start=1)
        ],
        "passages": [
            {**p.model_dump(), "id": p.passage_id, "rank": i, "cited": p.passage_id in r.cited}
            for i, p in enumerate(r.passages, start=1)
        ],
        "usage": {
            "model": r.usage.model,
            "prompt_tokens": r.usage.prompt_tokens,
            "completion_tokens": r.usage.completion_tokens,
            "cost_usd": r.usage.cost_usd,
        },
        "timings_ms": {name: round(ms) for name, ms in r.timings_ms.items()},
    }


# ---- Phase 2 (P3): the program builder ----

MAX_TURNS, MAX_MESSAGE_CHARS = 30, 1000


class ChatMessage(BaseModel):
    role: str
    content: str


class ProgramRequest(BaseModel):
    conversation: list[ChatMessage]  # the whole chat so far; the server keeps no memory


@app.post("/api/program")
def program(req: ProgramRequest) -> dict:
    convo = [{"role": m.role, "content": m.content.strip()} for m in req.conversation]
    if not convo or convo[-1]["role"] != "user" or not convo[-1]["content"]:
        raise HTTPException(status_code=400, detail="Please type a message.")
    if len(convo) > MAX_TURNS:
        raise HTTPException(status_code=400, detail="This conversation is long. Start a new program to keep going.")
    if any(m["role"] not in ("user", "assistant") for m in convo):
        raise HTTPException(status_code=400, detail="Messages must come from the user or the assistant.")
    if any(len(m["content"]) > MAX_MESSAGE_CHARS for m in convo):
        raise HTTPException(status_code=400, detail=f"Messages can be up to {MAX_MESSAGE_CHARS} characters. Please shorten it.")
    try:
        turn = run_turn(convo)
    except Exception as e:
        log.exception("Program turn failed")
        status, message = friendly_message(e)
        raise HTTPException(status_code=status, detail=message) from e
    return asdict(turn)
