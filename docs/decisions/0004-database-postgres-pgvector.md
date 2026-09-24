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
