"""Minimal local web app for asking the exercise database questions (Step 10).

    browser (static/index.html)  --POST /api/ask-->  this server  -->  rag.answer_question()

The browser never sees the OpenRouter key: only this server calls the LLM.

Run from the project folder:
    uv run uvicorn ragmotion.app:app --host 127.0.0.1 --port 8010 --reload
Then open http://127.0.0.1:8010
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from ragmotion.config import settings
from ragmotion.db import get_connection
from ragmotion.ingestion import load_sources
from ragmotion.rag import answer_question

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="rag-motion", description="Grounded answers from the exercise knowledge base.")


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    k: int = Field(default=5, ge=1, le=10)  # how many exercises AND how many passages to retrieve


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/info")
def info() -> dict:
    """What the assistant knows and which models it uses, for the sidebar and header."""
    with get_connection() as conn:
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
        "embedding_model": settings.embedding_model,
        "retrieval": "semantic",
        "sources": sources,
        "exercises": exercise_count,
    }


@app.post("/api/ask")
def ask(req: AskRequest) -> dict:
    try:
        r = answer_question(req.question.strip(), k_exercises=req.k, k_passages=req.k)
    except Exception as e:  # show the reason in the page instead of a blank failure
        raise HTTPException(status_code=502, detail=f"{type(e).__name__}: {e}") from e

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
