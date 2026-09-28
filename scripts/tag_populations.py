"""F5: tag every stored passage with who it's about (adults, older adults, youth, pregnancy).

New chunks get tagged by chunk_documents.py; this fills in existing rows without re-chunking or
re-embedding. Safe to re-run.

    uv run python scripts/tag_populations.py
"""

from ragmotion.chunking import populations_for
from ragmotion.db import get_connection


def main() -> None:
    with get_connection() as conn:
        rows = conn.execute("SELECT id, source_id, chapter, headings, text FROM document_chunk").fetchall()
        for id_, source_id, chapter, headings, text in rows:
            conn.execute("UPDATE document_chunk SET populations = %s WHERE id = %s",
                         (populations_for(source_id, chapter, headings, text), id_))
        summary = conn.execute("""
            SELECT source_id, split_part(chapter, ':', 1) AS chapter, populations, count(*)
            FROM document_chunk GROUP BY 1, 2, 3 ORDER BY 1, min(chunk_index)""").fetchall()
    print(f"Tagged {len(rows)} passages.\n")
    for source_id, chapter, pops, n in summary:
        print(f"{source_id:<26} {chapter[:48]:<48} {n:>3}  {', '.join(pops) or 'general'}")


if __name__ == "__main__":
    main()
