# 0004. Database: PostgreSQL 16 + pgvector in Docker
**Date:** 2026-09-23 · **Step:** 0 · **Status:** accepted

## Context
The app needs to store exercises with structured data (such as equipment and difficulty) and their embedding vectors, and search them. The environment audit found no local Postgres, but Docker was running and the `pgvector/pgvector:pg16` image was already pulled.

## Options considered
- **PostgreSQL + pgvector.** A production-grade relational database. pgvector is an extension that adds vector storage and similarity search. Structured data and vectors live in one database and can be combined in one query.
- **A dedicated vector database (e.g. Pinecone, Qdrant).** More specialized for vectors at huge scale. Structured data would live elsewhere.
- **SQLite.** A database stored in a single file, with no server to run. Zero setup and built into Python. But vector search needs a separate extension (sqlite-vec) that is less mature than pgvector, it handles many simultaneous writers poorly, and it's not what production web apps typically run. The master context document explicitly chose PostgreSQL over SQLite to learn a production-oriented database.

## Decision
Use PostgreSQL 16 with pgvector, run in Docker with docker-compose (a tool that starts containers from a config file), using the `pgvector/pgvector:pg16` image. Structured data and vectors sit together and can be filtered and searched in one query, and the developer learns a production-grade relational database. Docker means nothing is installed directly on the Mac and the setup is reproducible.

## Tradeoffs
Docker must be running. pgvector is less specialized than a dedicated vector database at huge scale.

## Revisit when
There are millions of vectors, or latency needs exceed what pgvector indexes can deliver.

## Note (2026-09-24, between Steps 2 and 3)
A concepts discussion before Step 3 confirmed the rationale. Keyword search (Postgres's built-in full-text search), semantic search (pgvector), and metadata filtering (`WHERE` clauses) can all run in one Postgres query. Only reranking would need an outside model. Supabase also supports pgvector, which gives a possible deployment path: point the app at a hosted database by changing the connection string. See the [build log entry](../build-log.md#between-steps-2-and-3-understanding-the-database-and-search-types) and [pgvector](../concepts.md#pgvector).

## Implemented in Step 3 (2026-09-24)
`docker-compose.yml` runs `pgvector/pgvector:pg16` with a named volume and a healthcheck. Running versions: PostgreSQL 16.15 and pgvector 0.8.6, enabled in the `ragmotion` database with `CREATE EXTENSION`. Deleting and recreating the container kept the data, confirming the volume works. The Mac-side port is 5434, not 5432, to avoid clashing with other local projects; see [0009](0009-local-db-port-5434-localhost-only.md). Commit `5d66ed2`. See the [Step 3 build log entry](../build-log.md#step-3-docker-compose-start-postgres-confirm-pgvector).

## Note (2026-09-24, between Steps 4 and 5): deployment path, and why not Pinecone
The developer asked whether deploying would mean moving to Supabase or Pinecone. Short answer: Supabase yes, Pinecone probably not; they solve different problems. Nothing was changed; this records the reasoning.

**Supabase migration path.** Supabase is hosted PostgreSQL with pgvector, the same technology used locally. Steps: create a Supabase project and enable pgvector (one click); run `db/schema.sql` unchanged; change `DATABASE_URL` to Supabase's connection string; run the seed and embedding scripts. No code or SQL changes, only the address. Neon, Railway, Render, and AWS also offer hosted Postgres with pgvector. See [Hosted Postgres](../concepts.md#hosted-postgres-supabase-neon-etc).

**Why not Pinecone.** Pinecone is a vector-only database. It does not replace Postgres, since exercises (and later clients, programs, and sessions) still need a regular database. Using it means running two systems and keeping them in sync: every exercise change must also update its vector in Pinecone, and when they drift, search returns edited or deleted exercises. Pinecone does support metadata filters, so that is not the deciding point. The stronger argument for Postgres is one source of truth: exercises, vectors, and later clients and programs in one place, joinable in one query, and updated together in one transaction. See [Dedicated vector database](../concepts.md#dedicated-vector-database-pinecone).

**When Pinecone would make sense.** Tens or hundreds of millions of vectors, very high search traffic, or a team that doesn't want to tune database indexes. This project expects 50 to 5,000 exercises. This sharpens the "Revisit when" signal above.

**Deployment is more than the database.** Backend on Render, Fly.io, or Railway; frontend on Netlify or Vercel; API keys move from `.env` into the host's secret settings. That is Phase 6 in the master context document.

**Machine note.** The local database lives in a Docker volume on the developer's MacBook Air only (the plan named a Mac Mini). Code travels through GitHub; the data does not. Another machine rebuilds it from the repo: clone, start Docker, apply `db/schema.sql`, run the seed script (Step 5). See the [build log entry](../build-log.md#between-steps-4-and-5-deployment-options-teach-back-and-a-machine-correction).
