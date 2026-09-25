"""Retrieval: find the exercises most relevant to a question.

Step 9 is semantic search only: embed the question, then ask pgvector for the
closest exercise vectors. Later steps add keyword search, filters, and more.
"""

from pgvector import Vector
from pydantic import BaseModel
from psycopg.rows import dict_row

from ragmotion.config import settings
from ragmotion.db import get_connection
from ragmotion.embeddings import embed_query
from ragmotion.models import Exercise


class ExerciseHit(Exercise):
    """An exercise returned by search, with how similar it is to the question."""

    similarity: float  # 1 - cosine distance: higher = more similar. Relative, not absolute.


SEARCH_SQL = """
SELECT slug, name, description, instructions, primary_muscles, movement_pattern,
       equipment, difficulty, laterality, body_region, source,
       1 - (embedding <=> %(q)s) AS similarity
FROM exercise
WHERE embedding IS NOT NULL
  AND embedding_model = %(model)s      -- never compare vectors from different models
ORDER BY embedding <=> %(q)s           -- smallest distance first = nearest neighbors
LIMIT %(k)s
"""


def search_exercises(question: str, k: int = 5) -> list[ExerciseHit]:
    """Return the k exercises whose embeddings are closest to the question's."""
    query_vector = Vector(embed_query(question))
    with get_connection() as conn:
        rows = conn.cursor(row_factory=dict_row).execute(
            SEARCH_SQL, {"q": query_vector, "model": settings.embedding_model, "k": k}
        ).fetchall()
    return [ExerciseHit.model_validate(r) for r in rows]


# ---- Step 13: document passages, and searching both tables ----------------------------------



class ChunkHit(BaseModel):
    """A document passage (or project-note passage) returned by search."""

    passage_id: str  # "<source_id>-<chunk_index>", used as the citation key, e.g. "pag2-57"
    source_id: str
    source_type: str  # "document" or "notes"
    source_title: str
    source_url: str | None
    license: str
    chapter: str
    headings: list[str]
    page_start: int | None
    page_end: int | None
    text: str
    similarity: float


CHUNK_SEARCH_SQL = """
SELECT source_id || '-' || chunk_index AS passage_id, source_id, source_type, source_title, source_url,
       license, chapter, headings, page_start, page_end, text,
       1 - (embedding <=> %(q)s) AS similarity
FROM document_chunk
WHERE embedding IS NOT NULL AND embedding_model = %(model)s
ORDER BY embedding <=> %(q)s
LIMIT %(k)s
"""


def search_all(question: str, k_exercises: int = 5, k_passages: int = 5) -> tuple[list[ExerciseHit], list[ChunkHit]]:
    """Embed the question once, then search exercises and document passages with the same vector."""
    q = Vector(embed_query(question))
    params = {"q": q, "model": settings.embedding_model}
    with get_connection() as conn:
        cur = conn.cursor(row_factory=dict_row)
        exercises = [ExerciseHit.model_validate(r) for r in cur.execute(SEARCH_SQL, {**params, "k": k_exercises}).fetchall()]
        passages = [ChunkHit.model_validate(r) for r in cur.execute(CHUNK_SEARCH_SQL, {**params, "k": k_passages}).fetchall()]
    return exercises, passages
