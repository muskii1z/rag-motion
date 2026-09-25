"""Embed every exercise that doesn't have an embedding yet, and store the vectors.

Run from the project folder:
    uv run python scripts/embed_exercises.py            # only rows missing an embedding
    uv run python scripts/embed_exercises.py --all      # re-embed everything (e.g. after
                                                        # changing exercise_to_text or the model)
Safe to re-run: with nothing missing, it does nothing and costs nothing.
"""

import sys

from pgvector import Vector
from psycopg.rows import dict_row

from ragmotion.config import settings
from ragmotion.db import get_connection
from ragmotion.embeddings import embed_documents, exercise_to_text
from ragmotion.models import Exercise

EXERCISE_COLUMNS = (
    "slug, name, description, instructions, primary_muscles, movement_pattern, "
    "equipment, difficulty, laterality, body_region, source"
)


def main() -> None:
    redo_all = "--all" in sys.argv

    with get_connection() as conn:
        # Rows needing work: no embedding yet, or made by a different model than the current one.
        where = "" if redo_all else "WHERE embedding IS NULL OR embedding_model IS DISTINCT FROM %(model)s"
        rows = conn.cursor(row_factory=dict_row).execute(
            f"SELECT {EXERCISE_COLUMNS} FROM exercise {where} ORDER BY slug",
            {"model": settings.embedding_model},
        ).fetchall()

        if not rows:
            print("Nothing to embed: every exercise already has an embedding from", settings.embedding_model)
            return

        exercises = [Exercise.model_validate(r) for r in rows]
        texts = [exercise_to_text(ex) for ex in exercises]

        print(f"Embedding {len(texts)} exercises with {settings.embedding_model} (one batch call)...")
        print(f"\nExample of the exact text embedded ({exercises[0].slug}):\n---\n{texts[0]}\n---\n")

        vectors = embed_documents(texts)

        # One transaction: all vectors are stored, or none are.
        for ex, vec in zip(exercises, vectors):
            conn.execute(
                "UPDATE exercise SET embedding = %s, embedding_model = %s WHERE slug = %s",
                (Vector(vec), settings.embedding_model, ex.slug),
            )

        done = conn.execute(
            "SELECT count(*) FROM exercise WHERE embedding IS NOT NULL AND embedding_model = %s",
            (settings.embedding_model,),
        ).fetchone()[0]
        total = conn.execute("SELECT count(*) FROM exercise").fetchone()[0]

    print(f"Stored {len(vectors)} embeddings. {done}/{total} exercises now embedded with {settings.embedding_model}.")


if __name__ == "__main__":
    main()
