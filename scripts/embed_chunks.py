"""Step 13: embed every document chunk that doesn't have a current embedding.

Run from the project folder:
    uv run python scripts/embed_chunks.py          # only chunks missing an embedding
    uv run python scripts/embed_chunks.py --all    # re-embed everything
Embeds `embed_text` (location label + chunk text) as a "document". Safe to re-run.
"""

import sys

from pgvector import Vector

from ragmotion.config import settings
from ragmotion.db import get_connection
from ragmotion.embeddings import embed_documents

BATCH = 64  # texts per API call


def main() -> None:
    where = "" if "--all" in sys.argv else "WHERE embedding IS NULL OR embedding_model IS DISTINCT FROM %(m)s"
    with get_connection() as conn:
        rows = conn.execute(f"SELECT id, embed_text FROM document_chunk {where} ORDER BY id", {"m": settings.embedding_model}).fetchall()
        if not rows:
            print("Nothing to embed.")
            return
        print(f"Embedding {len(rows)} chunks with {settings.embedding_model} in batches of {BATCH}...")
        for start in range(0, len(rows), BATCH):
            batch = rows[start:start + BATCH]
            vectors = embed_documents([text for _, text in batch])
            for (chunk_id, _), vec in zip(batch, vectors):
                conn.execute("UPDATE document_chunk SET embedding = %s, embedding_model = %s WHERE id = %s",
                             (Vector(vec), settings.embedding_model, chunk_id))
            print(f"  {min(start + BATCH, len(rows))}/{len(rows)}")
        done = conn.execute("SELECT count(*) FILTER (WHERE embedding IS NOT NULL), count(*) FROM document_chunk").fetchone()
    print(f"Embedded chunks: {done[0]}/{done[1]}")


if __name__ == "__main__":
    main()
