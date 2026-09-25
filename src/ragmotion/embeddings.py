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

from ragmotion.config import settings
from ragmotion.llm import get_client

InputType = Literal["query", "document"]


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
