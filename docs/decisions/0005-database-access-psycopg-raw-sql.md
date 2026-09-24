# 0005. Database access: psycopg 3 with raw SQL
**Date:** 2026-09-23 · **Step:** 0 · **Status:** accepted

## Context
Python code needs a way to talk to Postgres. The developer is learning, so seeing what the database actually does matters.

## Options considered
- **psycopg 3 with hand-written SQL.** psycopg is the standard Python driver for Postgres. Every query is visible. More boilerplate.
- **SQLAlchemy ORM.** An ORM (object-relational mapper) lets you work with Python objects instead of writing SQL. Less boilerplate, but it hides the queries.

## Decision
Use psycopg 3 with hand-written SQL, no ORM, so the developer sees and understands every query while learning.

## Tradeoffs
More boilerplate. No automatic migrations (scripted changes to the database schema).

## Revisit when
The schema starts changing often. Then add SQLAlchemy and Alembic (a migration tool).
