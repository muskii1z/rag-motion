"""Shared test setup and helpers.

Unit tests run offline: no database, no API calls, no cost. Tests that need the running
database are marked `integration` and skip automatically when Postgres isn't reachable.
"""

import os

# Must happen before importing ragmotion: config.py loads .env with override=False, so this wins.
os.environ["LANGSMITH_TRACING"] = "false"

import pytest  # noqa: E402

from ragmotion.retrieval import ChunkHit, ExerciseHit  # noqa: E402


def make_exercise(slug: str, **overrides) -> ExerciseHit:
    """A valid exercise search hit with sensible defaults."""
    fields = dict(
        slug=slug, name=slug.replace("-", " ").title(), description="An exercise.", instructions=None,
        primary_muscles=["glutes"], movement_pattern="squat", equipment=["dumbbell"], difficulty="beginner",
        laterality="bilateral", body_region="lower", source="test", similarity=0.5,
    )
    fields.update(overrides)
    return ExerciseHit(**fields)


def make_passage(source_id: str, chunk_index: int, **overrides) -> ChunkHit:
    """A valid document-passage search hit with sensible defaults."""
    fields = dict(
        passage_id=f"{source_id}-{chunk_index}", source_id=source_id, source_type="document",
        source_title="A Source", source_url=None, license="Public domain", chapter="Chapter 4. Active Adults",
        headings=["Key Guidelines for Adults"], page_start=56, page_end=56, text="Passage text.", similarity=0.5,
    )
    fields.update(overrides)
    return ChunkHit(**fields)


def database_available() -> bool:
    try:
        from ragmotion.db import get_connection

        with get_connection() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False


def pytest_collection_modifyitems(config, items):
    if database_available():
        return
    skip = pytest.mark.skip(reason="Postgres not reachable (start it with: docker compose up -d --wait)")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)
