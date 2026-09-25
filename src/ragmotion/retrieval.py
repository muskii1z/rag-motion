"""Retrieval: find the exercises most relevant to a question.

Step 9 is semantic search only: embed the question, then ask pgvector for the
closest exercise vectors. Later steps add keyword search, filters, and more.
"""

from pgvector import Vector
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
