# Interview prep

The interview questions from the project brief, grouped by topic. Under each question, "Evidence so far" links to the build log, concepts, and decisions that help answer it. Questions with nothing built yet are marked *Not yet covered*.

Last updated: Step 5.

---

## Teach-backs

The developer explains what has been built in their own words, gets corrections, and saves a polished version to say in interviews. This section grows over time.

### Teach-back 1: after Step 4 (2026-09-24)

**The developer's explanation** (lightly condensed, their wording kept):
"So far we installed uv, it's a Python library, I think. Then we made the GitHub. Then we created our database, inside a Docker container. Then we created the database table structure. It's PostgreSQL, and it has a pgvector extension. PostgreSQL is just regular, you can store text, like type of exercise, equipment, what muscle, etc. The vector extension and vector storage basically allows us to identify those specific parts of the table, or any item, with a number, labels it with a number, and the idea is that if I have three leg exercises, those numbers would be closer than an arm and a leg exercise."

**What was right.** The overall picture.
- GitHub. Plus: `.gitignore` keeps API keys off GitHub ([.gitignore](concepts.md#gitignore)).
- Database in a Docker container. Plus: the volume is where the data actually lives, so containers can be rebuilt ([Docker volume](concepts.md#docker-volume)).
- PostgreSQL is the database and `exercise` is the table in it, with regular columns for equipment, muscles, and difficulty ([Schema](concepts.md#schema)).
- The leg-vs-arm intuition is exactly right: similar exercises sit closer together.

**What was corrected.**
1. **uv is not a library, it's a tool.** Libraries are code the project uses (anthropic, voyageai). uv installs them into the project's private folder and records exact versions. uv is the delivery driver; libraries are the packages. See [Package manager](concepts.md#package-manager).
2. **The vector isn't a label or a single number; it's a list of 1,024 numbers.** The labels are the `id` and `slug` (e.g. `goblet-squat`). The vector describes the exercise's meaning, not its name. Think of coordinates: a map location needs 2 numbers, meaning needs about 1,024. Similar meanings sit near each other, and `<=>` measures the distance. See [Embedding](concepts.md#embedding).
- Also clarified: the `embedding` column is currently empty. Postgres doesn't create vectors. Voyage reads each description and returns the 1,024 numbers (Step 8); pgvector stores them and measures distance. See [pgvector](concepts.md#pgvector).

**Interview version** (saved verbatim at the developer's request):

> I used uv to set up the Python project and its dependencies, and pushed it to a private GitHub repo with secrets git-ignored. I run PostgreSQL in Docker, with a volume so the data persists. I created an exercise table with regular columns for things like equipment and difficulty, plus a vector column from the pgvector extension. Each exercise's description gets turned into a 1,024-number embedding, so exercises with similar meanings sit close together, and I can search by meaning and filter by the regular columns in the same query.

Note: the last sentence describes the design. Embeddings are created in Step 8 and search is built in Step 9; neither exists yet. (As of Step 5 the table holds 20 seeded exercises, all with empty embeddings.)

---

## LLM

### How did you structure your LLM outputs?
Evidence so far:
- Planned only, not built yet. Structured outputs will use `client.messages.parse` with a Pydantic model (a Python class defining the exact output shape). See [0003. LLM: Claude Opus 5](decisions/0003-llm-claude-opus-5.md).
- First structured Claude call is planned for Step 6 (prose to structured client profile).
- [Step 1](build-log.md#step-1-install-uv-create-the-python-project-add-dependencies): pydantic 2.13.5 and the anthropic SDK 1.8.0 are installed and import cleanly. See [What each library is for](concepts.md#what-each-library-is-for).
- [Step 5](build-log.md#step-5-write-20-exercises-seed-script-query-by-hand): the provider is now open. The developer prefers [OpenRouter](concepts.md#openrouter) (one key, many models), so 0003 is "under review" until Step 6. Point to make: structured-output support varies by model on OpenRouter, so the model choice has to be checked against the output shape we need. The `client.messages.parse` plan may not apply.
- [Step 5](build-log.md#step-5-write-20-exercises-seed-script-query-by-hand): the same technique already works on input data. The `Exercise` [Pydantic model](concepts.md#pydantic-model-and-literal-types) with `Literal` types validates every seed entry and names the failing field. A structured LLM output would be checked against a model like this.

## RAG

### Why did you use RAG instead of simply prompting the model?
Evidence so far:
- [LLM vs embedding model](concepts.md#llm-vs-embedding-model): the database finds relevant exercises before Claude ever sees the question.
- [0002. Embeddings with Voyage AI](decisions/0002-embeddings-voyage-4-lite.md)
- [Why RAG beats a plain chatbot here](concepts.md#why-rag-beats-a-plain-chatbot-here) (discussed before [Step 4](build-log.md#before-we-started-how-much-does-the-table-lock-us-in)): the honest four-point answer. A general chatbot already knows training principles and would write a decent program, so the advantage is not that the model knows more. It is: (1) every claim has a source a coach can check; (2) it only uses catalog exercises that fit the client's equipment and level; (3) the knowledge is controlled and vetted by the developer, not whatever the model absorbed from the internet; (4) it is measurable through evaluation.
- Supporting pieces already built in [Step 4](build-log.md#step-4-exercise-schema-create-the-table-inspect-it-in-psql): the required `source` column (point 1), the constrained `equipment` and `difficulty` columns (point 2), and the unique `slug` used for citations and eval tests (points 1 and 4).
- [Structured vs unstructured knowledge](concepts.md#structured-vs-unstructured-knowledge): a strong answer needs both an exercise catalog (rows) and training principles (document text). Only the catalog exists so far.
- [Content licensing in RAG](concepts.md#content-licensing-in-rag): part of point 3. The knowledge must be content we have permission to use, so copyrighted textbooks can't go in the public repo. Source choice is still open.
- [Step 5](build-log.md#step-5-write-20-exercises-seed-script-query-by-hand): [RAG: Retrieve, Augment, Generate](concepts.md#rag-retrieve-augment-generate). A clear breakdown to say out loud: retrieve evidence from your own data, augment the prompt with it, generate a cited answer. Seeding and a single LLM call are pieces of RAG, not RAG. Step 5 gives R something to search; Step 6 is G alone; Steps 7 to 9 are R alone; Step 10 connects them.
- [Step 5](build-log.md#before-we-started-four-questions-and-a-plan-change): why a structured catalog **and** documents. Documents answer "why and how to train"; the catalog answers "what exists". An agent that builds programs needs filterable rows ("3 lower-body power exercises that only need a box"), which can't be pulled reliably from paragraphs. See [Structured vs unstructured knowledge](concepts.md#structured-vs-unstructured-knowledge) (extended).
- [Step 5](build-log.md#step-5-write-20-exercises-seed-script-query-by-hand): why clean data first. [Seeding](concepts.md#seeding) is the simplest ingestion; document ingestion (Steps 12 to 14) adds failure points (garbled PDF text, chunks cut mid-sentence, wrong chunk sizes, lost metadata). Building it first would make failures impossible to locate. Good story: the developer challenged the order, and the plan was revised ([0011](decisions/0011-phase-1-plan-revision-ingestion-and-langsmith.md)).
- [Step 5](build-log.md#step-5-write-20-exercises-seed-script-query-by-hand): provenance is honest. Every exercise's `source` is "Drafted with AI assistance; pending coach review" until the developer reviews it.
- Full answer still needs Step 10 (retrieved evidence to the LLM, cited answer), Steps 12 to 14 (documents), and Step 15 (eval baseline).

## Embeddings

### What is an embedding?
Evidence so far:
- [Embedding](concepts.md#embedding)
- [LLM vs embedding model](concepts.md#llm-vs-embedding-model)
- [Why Anthropic doesn't sell embeddings](concepts.md#why-anthropic-doesnt-sell-embeddings)
- [0002. Embeddings with Voyage AI voyage-4-lite](decisions/0002-embeddings-voyage-4-lite.md): 1024 dimensions, separate `"document"` and `"query"` input types.
- [Between Steps 2 and 3](build-log.md#between-steps-2-and-3-understanding-the-database-and-search-types): where embeddings live and what they are bad at.
  - [pgvector](concepts.md#pgvector): each exercise's embedding is stored as a `vector(1024)` column in the same row as its name, equipment, and difficulty, and compared with the `<=>` cosine distance operator.
  - [Semantic search](concepts.md#semantic-search): embeddings match by meaning ("hip hinge" finds "Romanian deadlift") but are weak on exact terms ("RDL" is just three letters to the model).
  - [Embedding](concepts.md#embedding) (extended with the exact-terms weakness).
- [Step 3](build-log.md#step-3-docker-compose-start-postgres-confirm-pgvector): how embeddings are compared. On toy 3-number vectors, pgvector's `<=>` gave 0 for identical, 0.024 for very similar, 1 for unrelated, and 2 for opposite. See [pgvector](concepts.md#pgvector). No real embeddings yet (Step 7).
- [Step 5](build-log.md#step-5-write-20-exercises-seed-script-query-by-hand): [Stale embeddings](concepts.md#stale-embeddings). An embedding describes the text as it was when embedded. The seed script clears an exercise's vector whenever its content changes, so it gets recomputed instead of silently matching old meaning. Also: each description was written to say what the exercise is, what it trains, and where it's useful, because the description is the text that gets embedded.

## Retrieval

### Why isn't vector similarity enough?
Evidence so far:
- [Embedding](concepts.md#embedding): embeddings don't store facts and can't enforce hard constraints like "must use dumbbells", so metadata filtering is still needed.
- [0004. Database: PostgreSQL 16 + pgvector](decisions/0004-database-postgres-pgvector.md): structured fields and vectors in one database so they can be combined in one query.
- [Between Steps 2 and 3](build-log.md#between-steps-2-and-3-understanding-the-database-and-search-types): the main answer, using the example question "beginner RDL variations with dumbbells".
  - [Semantic search](concepts.md#semantic-search) misses exact terms: it may rank loosely related exercises above "Dumbbell RDL". [Keyword search](concepts.md#keyword-search) catches that exact name but misses paraphrases.
  - [Metadata filtering](concepts.md#metadata-filtering): a barbell exercise can be very close in meaning to a dumbbell one, so "dumbbells only" must be a `WHERE` clause, not a hope.
  - [Hybrid search](concepts.md#hybrid-search): keyword plus semantic, merged, so each covers the other's blind spot.
  - [Reranking](concepts.md#reranking): retrieve 20 cheaply, let a more careful model pick the best 5.
  - [Basic vs production-style RAG](concepts.md#basic-vs-production-style-rag): the full pipeline diagram, and the plan to add each technique one at a time against an eval baseline. Planned, not built.
- [Step 4](build-log.md#step-4-exercise-schema-create-the-table-inspect-it-in-psql): the filter columns now exist, ready for Phase 1F. `equipment`, `difficulty`, `movement_pattern`, `laterality`, and `body_region` are separate columns with [CHECK constraints](concepts.md#check-constraints), so a filter like "dumbbells only, beginner" will be a trustworthy `WHERE` clause. See [Metadata filtering](concepts.md#metadata-filtering) (extended) and [0010](decisions/0010-exercise-table-check-constraints.md).
  - Point to make: filters are only as good as the data. A typo like "Dumbell" in a free-text column would silently drop an exercise from filtered results; the CHECK rejects it on insert.
  - Design rule from Step 4: anything you want to filter on gets its own column; everything else stays in the description for the embedding. See [Schema](concepts.md#schema).
- [Step 5](build-log.md#step-5-write-20-exercises-seed-script-query-by-hand): the first hand-run filters, and a real insight. See [Array operators: ANY vs contained-by](concepts.md#array-operators-any-vs-contained-by) and [Metadata filtering](concepts.md#metadata-filtering) (extended).
  - `'dumbbell' = ANY(equipment)` ("uses dumbbells") for beginner lower-body returned 5 rows, including Dumbbell Hip Thrust `{dumbbell,bench}` and Dumbbell Step-Up `{dumbbell,box}`. Wrong for a client who owns only dumbbells.
  - `equipment <@ ARRAY['dumbbell','bodyweight']` ("only needs what I own") returned 11 rows across the catalog. That is the client's actual question.
  - Point to make: a filter can be valid SQL and still answer the wrong question. This feeds Phase 1F filtering and Phase 2 program building.
  - Why only 20 exercises: results can be judged by eye. A push-up in "unilateral lower-body" results is instantly wrong; with 2,000 rows it wouldn't be.

## PostgreSQL

### Why PostgreSQL + pgvector?
Evidence so far:
- [0004. Database: PostgreSQL 16 + pgvector in Docker](decisions/0004-database-postgres-pgvector.md): options compared, tradeoffs, and when to revisit. Now includes a note that the between-Steps-2-and-3 discussion confirmed the rationale.
- [0005. Database access: psycopg 3 with raw SQL](decisions/0005-database-access-psycopg-raw-sql.md)
- [Step 0](build-log.md#step-0-planning-environment-audit-and-documentation-setup): the `pgvector/pgvector:pg16` image was already on the machine.
- [Between Steps 2 and 3](build-log.md#between-steps-2-and-3-understanding-the-database-and-search-types):
  - [SQLite vs PostgreSQL](concepts.md#sqlite-vs-postgresql): a server handles concurrent writes, supports extensions, and matches production. Good story: the developer came from SQLite and Supabase.
  - [pgvector](concepts.md#pgvector): vector column, distance operator, and indexes. Meaning-based ranking and column filters in one SQL query, instead of splitting data across a relational database and a vector database.
  - [Basic vs production-style RAG](concepts.md#basic-vs-production-style-rag): keyword search (built-in full-text search), semantic search (pgvector), and filters (`WHERE`) all run in one database. Only reranking needs an outside model.
  - [Supabase is PostgreSQL](concepts.md#supabase-is-postgresql): Supabase supports pgvector, so the skills and schema transfer to a hosted deployment.
- [Step 3](build-log.md#step-3-docker-compose-start-postgres-confirm-pgvector): now running, not just planned.
  - PostgreSQL 16.15 with pgvector 0.8.6, in Docker via [Docker Compose](concepts.md#docker-compose). Commit `5d66ed2`.
  - [Extension available vs enabled](concepts.md#extension-available-vs-enabled): the image only makes pgvector available; the `ragmotion` database switched it on with `CREATE EXTENSION`. Shown before and after with `pg_available_extensions` and `\dx`.
  - [pgvector](concepts.md#pgvector): the `<=>` cosine distance scale checked by hand (0 identical, 1 unrelated, 2 opposite).
  - [Docker volume](concepts.md#docker-volume): persistence proven. Deleted the container, started a new one, and pgvector was still enabled.
  - [Port mapping](concepts.md#port-mapping) and [0009](decisions/0009-local-db-port-5434-localhost-only.md): checked what other projects used before picking a port, and chose 5434 to avoid a collision. A small story about looking before building.
- [Step 4](build-log.md#step-4-exercise-schema-create-the-table-inspect-it-in-psql): a schema with constraints, tested by trying to break it. Commit `46e9b11`.
  - [Schema](concepts.md#schema) in `db/schema.sql`: 14 columns, one [idempotent](concepts.md#idempotent-script) file that also enables pgvector.
  - [NOT NULL, DEFAULT, UNIQUE, PRIMARY KEY](concepts.md#not-null-default-unique-primary-key) and [CHECK constraints](concepts.md#check-constraints): four bad inserts, four rejections, each naming the rule that failed (`exercise_difficulty_check`, `exercise_equipment_check1`, the not-null on `source`, and pgvector's `expected 1024 dimensions, not 3`).
  - Structured metadata and the `vector(1024)` embedding sit in the same row, which is the payoff of pgvector described above. The vector column also rejects the wrong size, which would catch a mismatched embedding model.
  - [Transaction (BEGIN and ROLLBACK)](concepts.md#transaction-begin-and-rollback): a valid insert was tested and undone, leaving the table empty for seeding.
  - [Identity column and ID gaps](concepts.md#identity-column-and-id-gaps) and [Slug vs id](concepts.md#slug-vs-id): the test row got id 4 because failed inserts used up numbers. A concrete story for why citations use a slug.
  - [0010](decisions/0010-exercise-table-check-constraints.md): why CHECK constraints over free text or lookup tables.
- [Between Steps 4 and 5](build-log.md#between-steps-4-and-5-deployment-options-teach-back-and-a-machine-correction): "Why not Pinecone?"
  - [Dedicated vector database (Pinecone)](concepts.md#dedicated-vector-database-pinecone): Pinecone is vector-only, so it would sit next to Postgres and need syncing on every exercise change. Pinecone does support metadata filters, so the real argument is one source of truth: rows and vectors joinable in one query and updated in one transaction.
  - [Hosted Postgres (Supabase, Neon, etc.)](concepts.md#hosted-postgres-supabase-neon-etc): the same stack is available hosted, so the local choice carries into deployment.
  - Full reasoning in the [0004 note](decisions/0004-database-postgres-pgvector.md#note-2026-09-24-between-steps-4-and-5-deployment-path-and-why-not-pinecone).
- [Step 5](build-log.md#step-5-write-20-exercises-seed-script-query-by-hand): loading data safely. Commit `408130e`.
  - [Upsert](concepts.md#upsert): `INSERT ... ON CONFLICT (slug) DO UPDATE`, only when `IS DISTINCT FROM` shows a real change, reporting inserted vs updated with `RETURNING (xmax = 0)`. Run 1: 20 inserted. Run 2: 0, 0, 20 unchanged. [Idempotent](concepts.md#idempotent-script) by proof.
  - [Transaction](concepts.md#transaction-begin-and-rollback) and [Validate before write](concepts.md#validate-before-write): whole file validated first, all rows written in one transaction, so the table is never half-loaded.
  - Array operators `= ANY` vs `<@` on a `text[]` column, run by hand in psql. See [Array operators: ANY vs contained-by](concepts.md#array-operators-any-vs-contained-by).
  - `db.py` calls `register_vector` so psycopg understands pgvector's type ([0005](decisions/0005-database-access-psycopg-raw-sql.md): hand-written SQL, no ORM).

## Evaluation

### How do you know your RAG system works?
Evidence so far:
- Planned, not done. See [Basic vs production-style RAG](concepts.md#basic-vs-production-style-rag), discussed [between Steps 2 and 3](build-log.md#between-steps-2-and-3-understanding-the-database-and-search-types).
  - Step 15 (was Step 11 before the [Step 5 plan change](build-log.md#before-we-started-four-questions-and-a-plan-change)) builds an evaluation set (questions paired with the exercises, and now also document passages, that should come back) and records a baseline score. It moved after document ingestion (Steps 12 to 14) so the baseline measures the whole system, not just the catalog. See [0011](decisions/0011-phase-1-plan-revision-ingestion-and-langsmith.md).
  - Our own scoring script comes first; results are then viewed in LangSmith. Writing the scorer by hand means knowing exactly what the number measures. See [LangSmith (tracing and evals)](concepts.md#langsmith-tracing-and-evals).
  - In Phase 1F (after Step 16), hybrid search, metadata filters, and reranking are added one at a time, with the same eval rerun after each, so each improvement is a number ("hits went from X to Y"), not a claim.
- [Step 4](build-log.md#step-4-exercise-schema-create-the-table-inspect-it-in-psql): each exercise has a unique, stable `slug` (e.g. `goblet-squat`), which eval cases will use to name the expected exercises. See [Slug vs id](concepts.md#slug-vs-id).
- [Step 5](build-log.md#step-5-write-20-exercises-seed-script-query-by-hand): the catalog is kept to 20 exercises so results can be judged by eye before a formal eval exists. Hand queries already checked the data: 20 rows, lower 11 / upper 5 / core 2 / full 2; difficulty beginner 14 / intermediate 6 / advanced 0 (a gap flagged for review).
- No eval set or scores exist yet.

## Agents

### What makes this an agent rather than a chatbot?
*Not yet covered.*

## LangGraph

### Why did you use LangGraph?
*Not yet covered.*

## Workflows

### What happens if the program fails validation?
*Not yet covered.*

## Human-in-the-loop

### Why does a human approve the program?
*Not yet covered.*

## Observability

### How do you debug an agent that made a bad decision?
Evidence so far:
- No agent exists yet (Phase 2). The debugging approach is being set up on the RAG pipeline first.
- [LangSmith (tracing and evals)](concepts.md#langsmith-tracing-and-evals): planned for **Step 11**, right after basic RAG and before document ingestion. A trace records every stage of one request: the question, the embedding call, retrieved rows and scores, the exact prompt, the answer, tokens, and latency. That answers the key debugging question: was the right evidence never retrieved, or retrieved and ignored? Decided in [Step 5](build-log.md#before-we-started-four-questions-and-a-plan-change) ([0011](decisions/0011-phase-1-plan-revision-ingestion-and-langsmith.md)).
- Until Step 11, manual tracing: our scripts print every stage, so the developer knows what a trace should contain before relying on a dashboard.
- Tradeoff to mention: traces, including prompts, are stored on LangSmith's servers. Acceptable here because only fictional client data is used.
- Nothing traced yet.

## Production

### How would you deploy this?
Evidence so far:
- [0004. Database in Docker](decisions/0004-database-postgres-pgvector.md): reproducible database setup with docker-compose.
- [0001. Packaging with uv](decisions/0001-packaging-uv.md): lockfile means identical installs on another machine.
- [0006. Interface: CLI first, thin FastAPI at Step 12](decisions/0006-interface-cli-first.md) (amended in Step 5: FastAPI is now Step 16, minimal local UI at Step 10)
- [Step 1](build-log.md#step-1-install-uv-create-the-python-project-add-dependencies): reproducible environment built. `pyproject.toml` declares minimum versions; `uv.lock` (2,217 lines) pins the exact versions of all 62 packages. See [pyproject.toml](concepts.md#pyprojecttoml) and [Lockfile](concepts.md#lockfile).
- [Runtime vs dev dependencies](concepts.md#runtime-vs-dev-dependencies): pytest sits in a dev group, so a production install can skip it.
- [Virtual environment](concepts.md#virtual-environment): isolation checked by hand (project anthropic 1.8.0 vs global 0.86.0; voyageai only inside the project).
- [.python-version](concepts.md#python-version): Python 3.12 pinned for the project.
- [Step 2](build-log.md#step-2-git-setup-secret-protection-and-private-github-repo): code backed up to a private GitHub repo (https://github.com/muskii1z/rag-motion). `.env.example` lists every setting a new environment needs (`DATABASE_URL`, `ANTHROPIC_API_KEY`, `VOYAGE_API_KEY`), so configuration comes from the environment, not from code. [.gitignore](concepts.md#gitignore) keeps `.venv` out because it is rebuilt from `uv.lock`.
- [Localhost and port 5432](concepts.md#localhost-and-port-5432) and [Supabase is PostgreSQL](concepts.md#supabase-is-postgresql) (between Steps 2 and 3): the app only knows a `DATABASE_URL`, and Supabase supports pgvector, so one possible path is pointing that setting at a hosted Supabase database. Discussed, not decided.
- [Docker volume](concepts.md#docker-volume): database data lives outside the container, so the container can be recreated without data loss.
- [Step 3](build-log.md#step-3-docker-compose-start-postgres-confirm-pgvector): the database is now reproducible.
  - [Docker Compose](concepts.md#docker-compose): `docker-compose.yml` is checked into the repo and defines the image, port, volume, and healthcheck. One command (`docker compose up -d --wait`) brings it up on any machine with Docker.
  - [Healthcheck (started vs ready)](concepts.md#healthcheck-started-vs-ready): `pg_isready` every 5 seconds, and `--wait` returns only once Postgres can accept connections. Point to make: "started" is not "ready".
  - [Docker volume](concepts.md#docker-volume): tested, not assumed. The container was deleted and rebuilt, and the data survived. `down -v` would delete it.
  - `DATABASE_URL` in `.env.example` now points at `localhost:5434`. Deploying means replacing that one setting with a hosted database's URL ([0009](decisions/0009-local-db-port-5434-localhost-only.md) revisit signal).
- [Step 4](build-log.md#step-4-exercise-schema-create-the-table-inspect-it-in-psql): `db/schema.sql` starts with `CREATE EXTENSION IF NOT EXISTS vector;` and is [idempotent](concepts.md#idempotent-script), so a fresh database is set up by one re-runnable file, applied with `-v ON_ERROR_STOP=1` so it stops at the first error.
- [Between Steps 4 and 5](build-log.md#between-steps-4-and-5-deployment-options-teach-back-and-a-machine-correction): a deployment plan, discussed not done.
  - Database: [Hosted Postgres (Supabase, Neon, etc.)](concepts.md#hosted-postgres-supabase-neon-etc). Enable pgvector, run `db/schema.sql` unchanged, change `DATABASE_URL`, rerun the seed and embedding scripts. No code changes. Neon, Railway, Render, and AWS are alternatives.
  - Rest of the app: backend on Render, Fly.io, or Railway; frontend on Netlify or Vercel; API keys move from `.env` into the host's secret settings. Phase 6 in the master context document.
  - [Where the database runs in this project](concepts.md#where-the-database-runs-in-this-project): code travels through GitHub, the database doesn't. Any machine rebuilds it from the repo (clone, start Docker, apply the schema, seed). That is why schema and seed data are files in git.
- [Step 5](build-log.md#step-5-write-20-exercises-seed-script-query-by-hand): the rebuild recipe is now complete for the data too. `uv run python scripts/seed_exercises.py` loads `data/exercises.json` from git and is safe to re-run ([Upsert](concepts.md#upsert)). Configuration comes from one [config module](concepts.md#config-module-pydantic-settings): `DATABASE_URL` has a local default and would be overridden in production; keys are read from the environment.
- Actual deployment not yet done.

## Security

### Where are your API keys stored?
Evidence so far:
- [Why .env stays out of git](concepts.md#why-env-stays-out-of-git): keys in a git-ignored `.env`, with a committed `.env.example` of blank values.
- Variable names: `ANTHROPIC_API_KEY` ([0003](decisions/0003-llm-claude-opus-5.md)) and `VOYAGE_API_KEY` ([0002](decisions/0002-embeddings-voyage-4-lite.md)).
- [Step 2](build-log.md#step-2-git-setup-secret-protection-and-private-github-repo): built and verified.
  - [.gitignore](concepts.md#gitignore) blocks `.env` and every `.env.*` variant, with one exception for `.env.example`. It was the very first commit (`b536be5`), so the rules were in place before anything else was tracked.
  - `.env.example` documents all three settings: `DATABASE_URL` (local Docker default, not a real secret), and `ANTHROPIC_API_KEY` and `VOYAGE_API_KEY` left blank.
  - [Secret check before the first commit](concepts.md#secret-check-before-the-first-commit): previewed the 21 files git would track, confirmed `.env` and `.venv` were ignored with `git check-ignore`, and grepped for key-shaped strings (`sk-ant-`, `ghp_`, `gho_`, Voyage-style keys, `API_KEY=<value>`). None found.
  - After the push, listed the repo contents through the GitHub API: no `.env` or `.venv` on GitHub.
  - The repo is private ([0007](decisions/0007-version-control-git-github.md)).
- Point to make: a secret pushed to GitHub counts as leaked and must be rotated, even if deleted afterwards. That is why the checks happen before the first commit, not after.
- [Credential helper](concepts.md#credential-helper): the push was pinned to the intended GitHub account (muskii1z) for that one command, and GitHub confirmed all commits were linked to it.
- [Step 0](build-log.md#step-0-planning-environment-audit-and-documentation-setup): the environment audit checked for key variables by printing their names only, never their values.
- [Step 1](build-log.md#step-1-install-uv-create-the-python-project-add-dependencies): pydantic-settings is installed to read keys from `.env`. Not wired up yet.
- Related supply-chain point: [Transitive dependencies](concepts.md#transitive-dependencies). 6 requested libraries became 62 installed packages, each one code we are trusting.
- [Step 3](build-log.md#step-3-docker-compose-start-postgres-confirm-pgvector): the database password, and network exposure.
  - [Binding the database to localhost only](concepts.md#binding-the-database-to-localhost-only): the port is `127.0.0.1:5434`, so only this Mac can connect, not other devices on the network. Docker's default would listen on all interfaces.
  - The password `postgres` is in plain text in `docker-compose.yml`. That's acceptable only because it is a local development credential for a database bound to 127.0.0.1. In production it would come from a secret manager. See [0009](decisions/0009-local-db-port-5434-localhost-only.md).
- [Step 5](build-log.md#step-5-write-20-exercises-seed-script-query-by-hand): keys wired up. See [Why .env stays out of git](concepts.md#why-env-stays-out-of-git) (extended).
  - `.env` created from `.env.example` and confirmed ignored with `git check-ignore`. `.env.example` now lists `OPENROUTER_API_KEY`, `VOYAGE_API_KEY`, and `ANTHROPIC_API_KEY` (optional).
  - The developer pastes keys into `.env` in an editor, never into the chat with the AI coding assistant. Point to make: a key typed into a chat is a key shared with another system.
  - Keys are read in one place, the [config module](concepts.md#config-module-pydantic-settings) (pydantic-settings), and are optional until the step that uses them.
  - Planned third-party data flow: LangSmith (Step 11) stores traces, including prompts, on its servers. Acceptable because client data is fictional only.

## Architecture

### What happens from the moment a user submits a request until they receive an answer?
Evidence so far:
- [LLM vs embedding model](concepts.md#llm-vs-embedding-model): the question is embedded, the database finds relevant exercises, then Claude answers.
- [0006. Interface](decisions/0006-interface-cli-first.md): requests come through CLI scripts, then a minimal local UI at Step 10, then a FastAPI endpoint at Step 16 (renumbered from Step 12 in Step 5).
- [Package layout](concepts.md#package-layout): all app code lives in one importable package, `src/ragmotion/`, so CLI scripts, tests, and the future API share it.
- [Where the database runs in this project](concepts.md#where-the-database-runs-in-this-project) (extended in Step 3): the storage layer is built. Python code connects to `localhost:5434`, which reaches container `rag-motion-db-1`, whose data sits in volume `rag-motion_pgdata`.
- [Step 4](build-log.md#step-4-exercise-schema-create-the-table-inspect-it-in-psql): the `exercise` table exists, holding each exercise's text, filterable metadata, provenance (`source`), and an empty `embedding` column in one row. Discussed but not built: a second table of document chunks for training principles ([Structured vs unstructured knowledge](concepts.md#structured-vs-unstructured-knowledge), [Chunking](concepts.md#chunking)).
- [Teach-back 1](#teach-back-1-after-step-4-2026-09-24): the developer's polished interview version covers the storage layer (uv project, private GitHub repo, Postgres in Docker with a volume, exercise table with metadata columns and a pgvector column). Partial answer; it stops before the request path.
- [Step 5](build-log.md#step-5-write-20-exercises-seed-script-query-by-hand): the first application code, split into small modules in `src/ragmotion/`:
  - `config.py`: one [config module](concepts.md#config-module-pydantic-settings) that reads `.env`.
  - `db.py`: `get_connection()`, which also registers pgvector's type with psycopg.
  - `models.py`: the `Exercise` [Pydantic model](concepts.md#pydantic-model-and-literal-types), mirroring the database's CHECK constraints.
  - Seed pipeline (`scripts/seed_exercises.py`): read JSON, validate everything, reject duplicate slugs, upsert in one transaction, clear stale embeddings, report inserted/updated/unchanged. See [Validate before write](concepts.md#validate-before-write), [Upsert](concepts.md#upsert), [Stale embeddings](concepts.md#stale-embeddings).
- The planned request path, from [RAG: Retrieve, Augment, Generate](concepts.md#rag-retrieve-augment-generate): question → embedding (Voyage) → pgvector similarity over exercises (and from Step 14, document chunks) → prompt with the retrieved evidence → LLM (likely via OpenRouter) → answer citing slugs. Shown in a minimal local UI at Step 10, traced in LangSmith from Step 11, and exposed through FastAPI at Step 16.
- The full request path is not built yet.

## Tradeoffs

### What would you change if this system had 100,000 users?
Evidence so far:
- [0004](decisions/0004-database-postgres-pgvector.md) revisit signal: millions of vectors or latency beyond what pgvector indexes deliver.
- [pgvector](concepts.md#pgvector): vector indexes (for example HNSW) are skipped for 20 exercises but would be needed at scale.
- [0002](decisions/0002-embeddings-voyage-4-lite.md) revisit signal: embedding cost at scale.
- [0003](decisions/0003-llm-claude-opus-5.md): LLM cost per token and cheaper model options.
- [0005](decisions/0005-database-access-psycopg-raw-sql.md) revisit signal: add SQLAlchemy and Alembic when the schema changes often.
- [0006](decisions/0006-interface-cli-first.md): no frontend yet.
- [0002](decisions/0002-embeddings-voyage-4-lite.md) tradeoff added in Step 1: the voyageai SDK pulls in LangChain core and LangSmith as [transitive dependencies](concepts.md#transitive-dependencies), which means a bigger install and more packages to keep patched.
- [0010](decisions/0010-exercise-table-check-constraints.md) (Step 4): CHECK constraints with fixed lists vs lookup tables with foreign keys. CHECKs are simple and visible in one file, but adding a new equipment type means editing the schema. Revisit signal: vocabularies grow large or need their own attributes.
- [Schema](concepts.md#schema) (Step 4): schema changes are cheap now, while the table is empty. Once real data and code depend on it, changes go through migrations. [0005](decisions/0005-database-access-psycopg-raw-sql.md) already plans a migration tool (Alembic) for when the schema changes often.
- [Dedicated vector database (Pinecone)](concepts.md#dedicated-vector-database-pinecone) (between Steps 4 and 5): at large scale (tens or hundreds of millions of vectors, very high search traffic) a dedicated vector database becomes a real option, at the cost of running and syncing two systems. At 50 to 5,000 exercises it is not worth it. See the [0004 note](decisions/0004-database-postgres-pgvector.md#note-2026-09-24-between-steps-4-and-5-deployment-path-and-why-not-pinecone).
- [0011](decisions/0011-phase-1-plan-revision-ingestion-and-langsmith.md) (Step 5): plan revision. Catalog first, then RAG, then LangSmith tracing, then ingestion, then evaluation. Tradeoff: ingestion starts about six steps later than "ingestion first", in exchange for failures that can be located. Revisit if the catalog steps drag.
- [Validate before write](concepts.md#validate-before-write) (Step 5): two validation layers (Pydantic and CHECK constraints) give clearer errors plus a safety net, at the cost of keeping two lists of allowed values in sync. See the [0010 note](decisions/0010-exercise-table-check-constraints.md).
- [OpenRouter](concepts.md#openrouter) (Step 5): one key for many models vs an extra middleman and uneven structured-output support. Decided at Step 6.
- Scoping story (Step 4): the developer chose to build the simple exercise table first and defer knowledge sources and a document table, rather than design for the full vision up front. See [Before we started](build-log.md#before-we-started-how-much-does-the-table-lock-us-in).
