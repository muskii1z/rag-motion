"""Load data/exercises.json into the exercise table.

Run from the project folder:
    uv run python scripts/seed_exercises.py

Safe to run repeatedly ("upsert"):
  - new slugs are inserted
  - existing slugs are updated only if something changed
  - when an exercise's text changes, its embedding is cleared (set to NULL)
    so it gets re-embedded later instead of silently going stale
"""

import json
from pathlib import Path

from pydantic import TypeAdapter

from ragmotion.db import get_connection
from ragmotion.models import Exercise

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "exercises.json"

UPSERT_SQL = """
INSERT INTO exercise (
    slug, name, description, instructions, primary_muscles,
    movement_pattern, equipment, difficulty, laterality, body_region, source
)
VALUES (
    %(slug)s, %(name)s, %(description)s, %(instructions)s, %(primary_muscles)s,
    %(movement_pattern)s, %(equipment)s, %(difficulty)s, %(laterality)s, %(body_region)s, %(source)s
)
ON CONFLICT (slug) DO UPDATE SET
    name             = EXCLUDED.name,
    description      = EXCLUDED.description,
    instructions     = EXCLUDED.instructions,
    primary_muscles  = EXCLUDED.primary_muscles,
    movement_pattern = EXCLUDED.movement_pattern,
    equipment        = EXCLUDED.equipment,
    difficulty       = EXCLUDED.difficulty,
    laterality       = EXCLUDED.laterality,
    body_region      = EXCLUDED.body_region,
    source           = EXCLUDED.source,
    embedding        = NULL
WHERE (exercise.name, exercise.description, exercise.instructions, exercise.primary_muscles,
       exercise.movement_pattern, exercise.equipment, exercise.difficulty,
       exercise.laterality, exercise.body_region, exercise.source)
  IS DISTINCT FROM
      (EXCLUDED.name, EXCLUDED.description, EXCLUDED.instructions, EXCLUDED.primary_muscles,
       EXCLUDED.movement_pattern, EXCLUDED.equipment, EXCLUDED.difficulty,
       EXCLUDED.laterality, EXCLUDED.body_region, EXCLUDED.source)
RETURNING slug, (xmax = 0) AS inserted
"""


def main() -> None:
    # 1. Read and validate the whole file before touching the database.
    raw = json.loads(DATA_FILE.read_text())
    exercises = TypeAdapter(list[Exercise]).validate_python(raw)

    slugs = [e.slug for e in exercises]
    duplicates = {s for s in slugs if slugs.count(s) > 1}
    if duplicates:
        raise SystemExit(f"Duplicate slugs in {DATA_FILE.name}: {sorted(duplicates)}")

    print(f"Validated {len(exercises)} exercises from {DATA_FILE.name}")

    # 2. Upsert them all in one transaction: either every row lands or none do.
    inserted, updated = 0, 0
    with get_connection() as conn:
        for ex in exercises:
            row = conn.execute(UPSERT_SQL, ex.model_dump()).fetchone()
            if row is None:
                continue  # slug existed and nothing changed
            if row[1]:
                inserted += 1
            else:
                updated += 1
        total = conn.execute("SELECT count(*) FROM exercise").fetchone()[0]

    unchanged = len(exercises) - inserted - updated
    print(f"Inserted {inserted}, updated {updated}, unchanged {unchanged}")
    print(f"exercise table now has {total} rows")


if __name__ == "__main__":
    main()
