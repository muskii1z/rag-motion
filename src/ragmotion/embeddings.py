"""Turning text into embeddings (lists of 1024 numbers) through OpenRouter.

All embedding calls in the project go through this module, so switching
provider or model is a change in one place (plus re-embedding stored rows).

Voyage embeds text differently depending on its role:
  - "document": text we store and search over (exercises, later document chunks)
  - "query":    a user's question
Questions must be embedded as queries and stored text as documents. Mixing
them makes search quietly worse, so callers use embed_documents() and
embed_query() instead of choosing the mode themselves.
"""

from typing import Literal

from langsmith import traceable

from ragmotion.config import settings
from ragmotion.llm import get_client
from ragmotion.models import Exercise

InputType = Literal["query", "document"]


def exercise_to_text(ex: Exercise) -> str:
    """The exact text we embed for an exercise.

    Name + description carry the meaning. The labeled facts let questions like
    "beginner dumbbell exercises" match too. Instructions are left out: step-by-step
    cues describe how to move, not what the exercise is, and add noise.
    Changing this function changes every vector, so re-embed after editing it.
    """
    return "\n".join(
        [
            ex.name,
            ex.description,
            f"Movement pattern: {ex.movement_pattern}. Body region: {ex.body_region}. Laterality: {ex.laterality}.",
            f"Primary muscles: {', '.join(ex.primary_muscles)}.",
            f"Equipment: {', '.join(ex.equipment)}.",
            f"Difficulty: {ex.difficulty}.",
        ]
    )


def _summarize_vectors(vectors: list[list[float]]) -> dict:
    return {"count": len(vectors), "dimensions": len(vectors[0]) if vectors else 0}


@traceable(run_type="embedding", name="embed", process_outputs=_summarize_vectors)
def _embed(texts: list[str], input_type: InputType) -> list[list[float]]:
    if not texts:
        return []
    response = get_client().embeddings.create(
        model=settings.embedding_model,
        input=texts,
        # Voyage-specific setting; OpenRouter passes it through (verified in Step 7).
        extra_body={"input_type": input_type},
    )
    # The API may return items out of order; each carries its original index.
    vectors = [item.embedding for item in sorted(response.data, key=lambda d: d.index)]

    if len(vectors) != len(texts):
        raise RuntimeError(f"Asked for {len(texts)} embeddings, got {len(vectors)}.")
    for v in vectors:
        if len(v) != settings.embedding_dimensions:
            raise RuntimeError(
                f"Embedding has {len(v)} numbers, expected {settings.embedding_dimensions}. "
                "Model and database column no longer match."
            )
    return vectors


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Embed text we will store and search over."""
    return _embed(texts, "document")


def embed_query(text: str) -> list[float]:
    """Embed a user's question for searching."""
    return _embed([text], "query")[0]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """How alike two vectors point: 1 = same direction, 0 = unrelated.

    For inspection and demos only; in the database pgvector computes this.
    """
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    return dot / (norm_a * norm_b)
