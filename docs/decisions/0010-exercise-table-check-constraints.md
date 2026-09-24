# 0010. Exercise table: metadata columns with CHECK constraints
**Date:** 2026-09-24 · **Step:** 4 · **Status:** accepted

## Context
The exercise table has several metadata columns (structured fields used for filtering): `movement_pattern`, `equipment`, `difficulty`, `laterality`, and `body_region`. In Phase 1F, after Step 12, retrieval will filter on these columns, for example "only exercises whose equipment is dumbbells, at beginner difficulty". A filter is only trustworthy if the values are consistent. If one row says `dumbbell` and another says `Dumbell`, a filter for `dumbbell` silently misses the second one, and nothing reports an error. So we needed to decide how strictly the database should control these values.

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
