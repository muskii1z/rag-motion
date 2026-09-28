"""Checks against the running database. No API calls, no cost. Skipped if Postgres is down."""

import pytest

from ragmotion.db import get_connection
from ragmotion.retrieval import keyword_search_all

pytestmark = pytest.mark.integration


def test_every_exercise_and_chunk_is_embedded():
    with get_connection() as conn:
        missing_ex = conn.execute("SELECT count(*) FROM exercise WHERE embedding IS NULL").fetchone()[0]
        missing_chunks = conn.execute("SELECT count(*) FROM document_chunk WHERE embedding IS NULL").fetchone()[0]
    assert (missing_ex, missing_chunks) == (0, 0)


def test_only_needs_what_i_own_equipment_query():
    # The Step 5 query the Phase 1F filters will use: everything the exercise needs is owned.
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT slug FROM exercise WHERE equipment <@ ARRAY['dumbbell', 'bodyweight']"
        ).fetchall()
    slugs = {r[0] for r in rows}
    assert "goblet-squat" in slugs
    assert "dumbbell-step-up" not in slugs  # needs a box
    assert "dumbbell-hip-thrust" not in slugs  # needs a bench


def test_keyword_search_finds_exercises_that_mention_biceps():
    # Since F1 the catalog has direct biceps curls, which rightly outrank rows that list biceps secondarily.
    exercises, _ = keyword_search_all("biceps", k_exercises=5, k_passages=1)
    slugs = {h.slug for h in exercises}
    assert "dumbbell-biceps-curl" in slugs
    assert all("biceps" in h.primary_muscles or "biceps" in h.name.lower() for h in exercises)


def test_equipment_filter_only_returns_usable_exercises():
    # F4: reuse a stored vector as the "question", so no API call is needed.
    from psycopg.rows import dict_row

    from ragmotion.config import settings
    from ragmotion.retrieval import SEARCH_SQL

    with get_connection() as conn:
        q = conn.execute("SELECT embedding FROM exercise WHERE slug = 'goblet-squat'").fetchone()[0]
        cur = conn.cursor(row_factory=dict_row)
        params = {"q": q, "model": settings.embedding_model, "k": 50}
        filtered = cur.execute(SEARCH_SQL, {**params, "owned": ["band", "bodyweight"]}).fetchall()
        unfiltered = cur.execute(SEARCH_SQL, {**params, "owned": None}).fetchall()
    assert filtered and all(set(r["equipment"]) <= {"band", "bodyweight"} for r in filtered)
    assert len(unfiltered) == 42


def test_population_filter_skips_other_groups_but_keeps_general_passages():
    # F5: reuse a stored passage vector as the "question", so no API call is needed.
    from psycopg.rows import dict_row

    from ragmotion.config import settings
    from ragmotion.retrieval import CHUNK_SEARCH_SQL

    with get_connection() as conn:
        q = conn.execute("SELECT embedding FROM document_chunk WHERE 'older-adults' = ANY(populations) LIMIT 1").fetchone()[0]
        cur = conn.cursor(row_factory=dict_row)
        rows = cur.execute(CHUNK_SEARCH_SQL, {"q": q, "model": settings.embedding_model, "k": 300, "population": "adults"}).fetchall()
        tags = {r["passage_id"]: r for r in rows}
        pops = conn.execute("SELECT source_id || '-' || chunk_index, populations FROM document_chunk").fetchall()
    kept = {pid for pid, p in pops if not p or "adults" in p}
    assert set(tags) == kept  # exactly the adult and general passages
