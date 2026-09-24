# Interview prep

The interview questions from the project brief, grouped by topic. Under each question, "Evidence so far" links to the build log, concepts, and decisions that help answer it. Questions with nothing built yet are marked *Not yet covered*.

Last updated: Step 2.

---

## LLM

### How did you structure your LLM outputs?
Evidence so far:
- Planned only, not built yet. Structured outputs will use `client.messages.parse` with a Pydantic model (a Python class defining the exact output shape). See [0003. LLM: Claude Opus 5](decisions/0003-llm-claude-opus-5.md).
- First structured Claude call is planned for Step 6 (prose to structured client profile).
- [Step 1](build-log.md#step-1-install-uv-create-the-python-project-add-dependencies): pydantic 2.13.5 and the anthropic SDK 1.8.0 are installed and import cleanly. See [What each library is for](concepts.md#what-each-library-is-for).

## RAG

### Why did you use RAG instead of simply prompting the model?
Evidence so far:
- [LLM vs embedding model](concepts.md#llm-vs-embedding-model): the database finds relevant exercises before Claude ever sees the question.
- [0002. Embeddings with Voyage AI](decisions/0002-embeddings-voyage-4-lite.md)
- Full answer still needs Step 10 (retrieved evidence to Claude, cited answer).

## Embeddings

### What is an embedding?
Evidence so far:
- [Embedding](concepts.md#embedding)
- [LLM vs embedding model](concepts.md#llm-vs-embedding-model)
- [Why Anthropic doesn't sell embeddings](concepts.md#why-anthropic-doesnt-sell-embeddings)
- [0002. Embeddings with Voyage AI voyage-4-lite](decisions/0002-embeddings-voyage-4-lite.md): 1024 dimensions, separate `"document"` and `"query"` input types.

## Retrieval

### Why isn't vector similarity enough?
Evidence so far:
- [Embedding](concepts.md#embedding): embeddings don't store facts and can't enforce hard constraints like "must use dumbbells", so metadata filtering is still needed.
- [0004. Database: PostgreSQL 16 + pgvector](decisions/0004-database-postgres-pgvector.md): structured fields and vectors in one database so they can be combined in one query.

## PostgreSQL

### Why PostgreSQL + pgvector?
Evidence so far:
- [0004. Database: PostgreSQL 16 + pgvector in Docker](decisions/0004-database-postgres-pgvector.md): options compared, tradeoffs, and when to revisit.
- [0005. Database access: psycopg 3 with raw SQL](decisions/0005-database-access-psycopg-raw-sql.md)
- [Step 0](build-log.md#step-0-planning-environment-audit-and-documentation-setup): the `pgvector/pgvector:pg16` image was already on the machine.

## Evaluation

### How do you know your RAG system works?
*Not yet covered.* First eval questions and a baseline run are planned for Step 11.

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
*Not yet covered.*

## Production

### How would you deploy this?
Evidence so far:
- [0004. Database in Docker](decisions/0004-database-postgres-pgvector.md): reproducible database setup with docker-compose.
- [0001. Packaging with uv](decisions/0001-packaging-uv.md): lockfile means identical installs on another machine.
- [0006. Interface: CLI first, thin FastAPI at Step 12](decisions/0006-interface-cli-first.md)
- [Step 1](build-log.md#step-1-install-uv-create-the-python-project-add-dependencies): reproducible environment built. `pyproject.toml` declares minimum versions; `uv.lock` (2,217 lines) pins the exact versions of all 62 packages. See [pyproject.toml](concepts.md#pyprojecttoml) and [Lockfile](concepts.md#lockfile).
- [Runtime vs dev dependencies](concepts.md#runtime-vs-dev-dependencies): pytest sits in a dev group, so a production install can skip it.
- [Virtual environment](concepts.md#virtual-environment): isolation checked by hand (project anthropic 1.8.0 vs global 0.86.0; voyageai only inside the project).
- [.python-version](concepts.md#python-version): Python 3.12 pinned for the project.
- [Step 2](build-log.md#step-2-git-setup-secret-protection-and-private-github-repo): code backed up to a private GitHub repo (https://github.com/muskii1z/rag-motion). `.env.example` lists every setting a new environment needs (`DATABASE_URL`, `ANTHROPIC_API_KEY`, `VOYAGE_API_KEY`), so configuration comes from the environment, not from code. [.gitignore](concepts.md#gitignore) keeps `.venv` out because it is rebuilt from `uv.lock`.
- Actual deployment not yet covered.

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

## Architecture

### What happens from the moment a user submits a request until they receive an answer?
Evidence so far:
- [LLM vs embedding model](concepts.md#llm-vs-embedding-model): the question is embedded, the database finds relevant exercises, then Claude answers.
- [0006. Interface](decisions/0006-interface-cli-first.md): requests come through CLI scripts, then a FastAPI `/ask` endpoint at Step 12.
- [Package layout](concepts.md#package-layout): all app code lives in one importable package, `src/ragmotion/`, so CLI scripts, tests, and the future API share it.
- The full request path is not built yet.

## Tradeoffs

### What would you change if this system had 100,000 users?
Evidence so far:
- [0004](decisions/0004-database-postgres-pgvector.md) revisit signal: millions of vectors or latency beyond what pgvector indexes deliver.
- [0002](decisions/0002-embeddings-voyage-4-lite.md) revisit signal: embedding cost at scale.
- [0003](decisions/0003-llm-claude-opus-5.md): LLM cost per token and cheaper model options.
- [0005](decisions/0005-database-access-psycopg-raw-sql.md) revisit signal: add SQLAlchemy and Alembic when the schema changes often.
- [0006](decisions/0006-interface-cli-first.md): no frontend yet.
- [0002](decisions/0002-embeddings-voyage-4-lite.md) tradeoff added in Step 1: the voyageai SDK pulls in LangChain core and LangSmith as [transitive dependencies](concepts.md#transitive-dependencies), which means a bigger install and more packages to keep patched.
