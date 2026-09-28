# 0010. Exercise table: metadata columns with CHECK constraints
**Date:** 2026-09-24 · **Step:** 4 · **Status:** accepted

## Context
The exercise table has several metadata columns (structured fields used for filtering): `movement_pattern`, `equipment`, `difficulty`, `laterality`, and `body_region`. In Phase 1F, after Step 12 (now after Step 16, see [0011](0011-phase-1-plan-revision-ingestion-and-langsmith.md)), retrieval will filter on these columns, for example "only exercises whose equipment is dumbbells, at beginner difficulty". A filter is only trustworthy if the values are consistent. If one row says `dumbbell` and another says `Dumbell`, a filter for `dumbbell` silently misses the second one, and nothing reports an error. So we needed to decide how strictly the database should control these values.

## Options considered
- **Free-text columns.** Any text is accepted. Most flexible, and nothing to maintain. But typos and variants (`Dumbell`, `DB`, `dumbbells`) get in without any error and quietly break filters.
- **Separate lookup tables with foreign keys.** Each vocabulary (equipment, difficulty, and so on) gets its own small table, and the exercise table can only reference rows that exist there (a foreign key is that link, enforced by the database). The most rigorous option, and each value could carry its own attributes. But it means more tables, joins (queries that combine tables), and concepts to learn right now, for vocabularies of 2 to 8 values.
- **CHECK constraints with fixed lists.** Each column has a rule listing its allowed values, enforced by Postgres on every insert and update. Simple, enforced by the database itself, and every allowed value is visible in one file (`db/schema.sql`).

## Decision
Use CHECK constraints with fixed lists. `equipment` is a list column (`text[]`) with two checks: it must not be empty, and every item must be one of bodyweight, dumbbell, band, kettlebell, barbell, bench, box. The other metadata columns are required text with one allowed-values check each. The `source` column is also required (`NOT NULL`), which supports the master context document's provenance rule: nothing enters without a source.

In Step 4 the rules were tested by hand. `difficulty = 'expert'` and `equipment = {trx}` were both rejected, and Postgres named the failing constraint (`exercise_difficulty_check`, `exercise_equipment_check1`). A row without a source was rejected too. See [Step 4](../build-log.md#step-4-exercise-schema-create-the-table-inspect-it-in-psql).

## Tradeoffs
Adding a new equipment type or movement pattern (for example a TRX strap) means editing the CHECK in `schema.sql`, not just inserting a row. The table is empty now, so that is cheap. Once real data and code depend on it, it becomes a migration (a scripted, versioned change to a live database's structure); see [0005](0005-database-access-psycopg-raw-sql.md), which already plans a migration tool for when the schema changes often. Allowed values also can't carry extra attributes (such as a description of each equipment type) the way lookup-table rows could.

## Revisit when
The vocabularies grow large, change often, or need their own attributes. Then move them to lookup tables with foreign keys.

## Note (2026-09-24, Step 5): the allowed values now live in two places
Step 5 added an `Exercise` Pydantic model in `src/ragmotion/models.py` whose `Literal` types mirror these CHECK lists, so the seed script can reject bad entries in Python, with the slug and field named, before anything reaches the database. The CHECK constraints stay as the final safety net. Tradeoff: adding an allowed value (for example a TRX strap) now means editing both `schema.sql` and `models.py`, and the two lists must be kept in sync by hand. See [Validate before write](../concepts.md#validate-before-write) and [Step 5](../build-log.md#step-5-write-20-exercises-seed-script-query-by-hand).

## Update (2026-09-28, Phase 1F F1): the lists grew, through a real migration
The catalog grew from 20 to 42 exercises (see the [F1 entry](../build-log.md#phase-1f-begins-f1-exercise-catalog-expanded-to-42)), and the fixed lists had to change for the first time since Step 4. This is the "adding a value means editing the schema" tradeoff above, now paid for real.

- **Movement patterns** added: `isolation` (single-joint or targeted work: curls, triceps extension, Nordic curl, band lateral walk) and `sprint` (running drills: A-skip, bounding). Full list: squat, hinge, lunge, push, pull, carry, core, jump, isolation, sprint.
- **Equipment** added: `rack` (back squat, bench press), `pullup-bar` (pull-up), and `anchor` (see below). Full list: bodyweight, dumbbell, band, kettlebell, barbell, bench, box, rack, pullup-bar, anchor.
- **How it was changed.** The table already held data, so editing `CREATE TABLE` alone would do nothing (`IF NOT EXISTS` skips it). `db/schema.sql` now drops and re-adds the two constraints by their Postgres default names, `exercise_movement_pattern_check` and `exercise_equipment_check1`, using `DROP CONSTRAINT IF EXISTS`, so the file stays safe to re-run. The `CREATE TABLE` lists were updated too, for fresh installs. See [Migration: changing allowed values](../concepts.md#migration-changing-allowed-values-drop-and-re-add-a-check).
- **Both copies updated.** The `Literal` types in `src/ragmotion/models.py` were changed in the same commits. The two lists still have to be kept in sync by hand; nothing checks this automatically.

### Why `anchor` is an equipment value
The Nordic hamstring curl uses no weights, but the heels must be held down by a partner or an anchoring device. Labeled `bodyweight`, it would pass a "no equipment" filter (`equipment <@ ARRAY['bodyweight']`) and be suggested to someone who can't do it alone. The coach flagged this in review. Options considered in the session were not recorded beyond the choice itself; the chosen fix was a new value, `anchor`, meaning "needs something or someone to hold you in place". Tradeoffs: `anchor` covers two different things (a person and a device), and a client's owned-equipment list must now include it for the Nordic curl to appear. It is the first equipment value that isn't a piece of gym equipment you buy; the vocabulary now describes "what you need besides your body".

### Revisit signal, checked
The vocabularies are now 10 values each, still small, and changed once since Step 4. Not yet at the "large or changes often" threshold. If F4 (the equipment filter) or client profiles need attributes per value (for example "commonly found at home"), that is the signal to move to lookup tables.
