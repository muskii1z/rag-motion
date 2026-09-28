"""Step 12: chunk every source in data/sources.toml and store the chunks in Postgres.

Run from the project folder (PDF sources must be extracted first with extract_document.py):
    uv run python scripts/chunk_documents.py              # all sources
    uv run python scripts/chunk_documents.py pag2         # one source
    uv run python scripts/chunk_documents.py --show 12    # also print chunk #12 of each source

Re-running replaces that source's chunks for the current chunker settings (embeddings for
those rows are cleared too, and get recomputed in Step 13).
"""

import argparse
import statistics

from ragmotion.chunking import chunk_source, chunker_label, embed_text_for, populations_for
from ragmotion.db import get_connection
from ragmotion.ingestion import load_sources

INSERT_SQL = """
INSERT INTO document_chunk (
    source_id, source_type, source_title, source_url, license, license_group,
    chunk_index, chapter, headings, page_start, page_end, text, embed_text, word_count, chunker, populations
) VALUES (
    %(source_id)s, %(source_type)s, %(source_title)s, %(source_url)s, %(license)s, %(license_group)s,
    %(chunk_index)s, %(chapter)s, %(headings)s, %(page_start)s, %(page_end)s,
    %(text)s, %(embed_text)s, %(word_count)s, %(chunker)s, %(populations)s
)
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_ids", nargs="*", help="default: every source in the manifest")
    parser.add_argument("--show", type=int, help="print this chunk number from each source")
    args = parser.parse_args()

    sources = load_sources()
    selected = [sources[s] for s in args.source_ids] if args.source_ids else list(sources.values())
    label = chunker_label()
    print(f"Chunker: {label}\n")

    with get_connection() as conn:  # one transaction for everything
        for source in selected:
            if source.license_group not in ("A", "B", "C"):
                print(f"SKIP {source.id}: license group {source.license_group} is never ingested")
                continue
            chunks = chunk_source(source)
            conn.execute("DELETE FROM document_chunk WHERE source_id = %s AND chunker = %s", (source.id, label))
            for c in chunks:
                conn.execute(INSERT_SQL, {
                    "source_id": source.id, "source_type": source.type, "source_title": source.title,
                    "source_url": source.url, "license": source.license, "license_group": source.license_group,
                    "chunk_index": c.chunk_index, "chapter": c.chapter, "headings": c.headings,
                    "page_start": c.page_start, "page_end": c.page_end, "text": c.text,
                    "embed_text": embed_text_for(source, c), "word_count": c.word_count, "chunker": label,
                    "populations": populations_for(source.id, c.chapter, c.headings, c.text),
                })

            w = [c.word_count for c in chunks]
            print(f"{source.id:<26} {len(chunks):>4} chunks | words min {min(w)}, median {statistics.median(w):.0f}, "
                  f"max {max(w)} | total {sum(w):,}")
            if args.show is not None and args.show < len(chunks):
                c = chunks[args.show]
                pages = f"pages {c.page_start}-{c.page_end}" if c.page_start else "no pages (notes)"
                print(f"\n----- chunk {c.chunk_index} of {source.id}, {c.word_count} words, {pages} -----")
                print(embed_text_for(source, c))
                print("-" * 60 + "\n")

        rows = conn.execute(
            "SELECT source_type, count(*), sum(word_count) FROM document_chunk WHERE chunker = %s GROUP BY 1 ORDER BY 1",
            (label,),
        ).fetchall()
    print("\nIn the database:", ", ".join(f"{t}: {n} chunks / {w:,} words" for t, n, w in rows))


if __name__ == "__main__":
    main()
