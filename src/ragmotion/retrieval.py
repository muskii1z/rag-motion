"""Retrieval: find the exercises most relevant to a question.

Step 9 is semantic search only: embed the question, then ask pgvector for the
closest exercise vectors. Later steps add keyword search, filters, and more.
"""

from langsmith import traceable
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
  AND (%(owned)s::text[] IS NULL          -- F4 equipment filter: when the question limits equipment,
       OR equipment <@ %(owned)s::text[])  -- keep only exercises needing nothing beyond what's owned
ORDER BY embedding <=> %(q)s           -- smallest distance first = nearest neighbors
LIMIT %(k)s
"""


def search_exercises(question: str, k: int = 5, owned: list[str] | None = None) -> list[ExerciseHit]:
    """Return the k exercises whose embeddings are closest to the question's (only usable ones if `owned` is set)."""
    query_vector = Vector(embed_query(question))
    with get_connection() as conn:
        rows = conn.cursor(row_factory=dict_row).execute(
            SEARCH_SQL, {"q": query_vector, "model": settings.embedding_model, "k": k, "owned": owned}
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
  AND (%(population)s::text IS NULL OR cardinality(populations) = 0 OR %(population)s = ANY(populations))  -- F5
ORDER BY embedding <=> %(q)s
LIMIT %(k)s
"""


def _as_trace_documents(result: tuple[list[ExerciseHit], list["ChunkHit"]]) -> dict:
    """LangSmith shows retriever outputs nicely when they look like documents."""
    if result is None:  # the call failed; LangSmith records the error itself
        return {}
    exercises, passages = result
    docs = [
        {"page_content": p.text, "type": "Document",
         "metadata": {"id": p.passage_id, "kind": "passage", "source": p.source_title, "chapter": p.chapter,
                      "pages": f"{p.page_start}-{p.page_end}" if p.page_start else None, "similarity": round(p.similarity, 3)}}
        for p in passages
    ] + [
        {"page_content": f"{h.name}: {h.description}", "type": "Document",
         "metadata": {"id": h.slug, "kind": "exercise", "similarity": round(h.similarity, 3)}}
        for h in exercises
    ]
    return {"documents": docs}


@traceable(run_type="retriever", name="search_all", process_outputs=_as_trace_documents)
def search_all(question: str, k_exercises: int = 5, k_passages: int = 5,
               owned: list[str] | None = None, population: str | None = None) -> tuple[list[ExerciseHit], list[ChunkHit]]:
    """Embed the question once, then search exercises and document passages with the same vector.

    owned: equipment the person has (F4). If set, exercises needing anything else are skipped.
    population: who the question is about (F5). If set, passages about other groups are skipped;
    general passages (no population tag) always stay.
    """
    q = Vector(embed_query(question))
    params = {"q": q, "model": settings.embedding_model}
    with get_connection() as conn:
        cur = conn.cursor(row_factory=dict_row)
        exercises = [ExerciseHit.model_validate(r) for r in cur.execute(SEARCH_SQL, {**params, "k": k_exercises, "owned": owned}).fetchall()]
        passages = [ChunkHit.model_validate(r) for r in cur.execute(CHUNK_SEARCH_SQL, {**params, "k": k_passages, "population": population}).fetchall()]
    return exercises, passages


# ---- Step 15: keyword search and hybrid search, for comparison --------------------------------
#
# Keyword search uses Postgres full-text search: text is reduced to stemmed words ("lexemes",
# e.g. "exercises" -> "exercis") with stop words removed, then matched against the question's
# words. Any shared word counts (OR), ranked by ts_rank_cd. At this size (~170 rows) the text
# vectors are computed per query; at scale they'd be stored in a column with a GIN index.
#
# Hybrid search merges the keyword and semantic rankings with Reciprocal Rank Fusion (RRF):
# each item scores sum(1 / (RRF_K + rank)) over the lists it appears in.

EXERCISE_TEXT_SQL = (
    "name || ' ' || description || ' ' || array_to_string(primary_muscles, ' ') || ' ' || "
    "array_to_string(equipment, ' ') || ' ' || movement_pattern || ' ' || difficulty || ' ' || "
    "laterality || ' ' || body_region"
)
OR_QUERY_SQL = "to_tsquery('english', array_to_string(tsvector_to_array(to_tsvector('english', %(qtext)s)), ' | '))"

KEYWORD_EXERCISE_SQL = f"""
SELECT slug, name, description, instructions, primary_muscles, movement_pattern,
       equipment, difficulty, laterality, body_region, source,
       ts_rank_cd(to_tsvector('english', {EXERCISE_TEXT_SQL}), {OR_QUERY_SQL}) AS similarity
FROM exercise
WHERE to_tsvector('english', {EXERCISE_TEXT_SQL}) @@ {OR_QUERY_SQL}
  AND (%(owned)s::text[] IS NULL OR equipment <@ %(owned)s::text[])
ORDER BY similarity DESC
LIMIT %(k)s
"""

KEYWORD_CHUNK_SQL = f"""
SELECT source_id || '-' || chunk_index AS passage_id, source_id, source_type, source_title, source_url,
       license, chapter, headings, page_start, page_end, text,
       ts_rank_cd(to_tsvector('english', embed_text), {OR_QUERY_SQL}) AS similarity
FROM document_chunk
WHERE to_tsvector('english', embed_text) @@ {OR_QUERY_SQL}
  AND (%(population)s::text IS NULL OR cardinality(populations) = 0 OR %(population)s = ANY(populations))  -- F5
ORDER BY similarity DESC
LIMIT %(k)s
"""

RRF_K = 60


def keyword_search_all(question: str, k_exercises: int = 5, k_passages: int = 5,
                       owned: list[str] | None = None, population: str | None = None) -> tuple[list[ExerciseHit], list[ChunkHit]]:
    """Full-text keyword search over both tables. `similarity` holds the text-rank score."""
    params = {"qtext": question}
    with get_connection() as conn:
        cur = conn.cursor(row_factory=dict_row)
        if not cur.execute("SELECT numnode(" + OR_QUERY_SQL + ") > 0 AS ok", params).fetchone()["ok"]:
            return [], []  # the question was only stop words
        exercises = [ExerciseHit.model_validate(r) for r in cur.execute(KEYWORD_EXERCISE_SQL, {**params, "k": k_exercises, "owned": owned}).fetchall()]
        passages = [ChunkHit.model_validate(r) for r in cur.execute(KEYWORD_CHUNK_SQL, {**params, "k": k_passages, "population": population}).fetchall()]
    return exercises, passages


def _rrf(rankings: list[list], key) -> list:
    scores, items = {}, {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            k = key(item)
            scores[k] = scores.get(k, 0.0) + 1.0 / (RRF_K + rank)
            items.setdefault(k, item)
    ordered = sorted(scores, key=scores.get, reverse=True)
    return [items[k].model_copy(update={"similarity": scores[k]}) for k in ordered]


def hybrid_search_all(question: str, k_exercises: int = 5, k_passages: int = 5, pool: int = 20,
                      owned: list[str] | None = None, population: str | None = None) -> tuple[list[ExerciseHit], list[ChunkHit]]:
    """Semantic + keyword, each retrieving `pool` candidates, merged with RRF. `similarity` holds the RRF score."""
    sem_ex, sem_ps = search_all(question, k_exercises=pool, k_passages=pool, owned=owned, population=population)
    kw_ex, kw_ps = keyword_search_all(question, k_exercises=pool, k_passages=pool, owned=owned, population=population)
    exercises = _rrf([sem_ex, kw_ex], key=lambda h: h.slug)[:k_exercises]
    passages = _rrf([sem_ps, kw_ps], key=lambda p: p.passage_id)[:k_passages]
    return exercises, passages


SEARCH_MODES = {"semantic": search_all, "keyword": keyword_search_all, "hybrid": hybrid_search_all}
