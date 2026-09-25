# Build log

A step-by-step journal of building rag-motion, an AI movement and exercise programming app. It is a portfolio and learning project that grows in stages: LLM, then RAG (retrieval-augmented generation: looking up relevant data first and handing it to the model), then agent, then workflow, then production. Newest entry at the bottom.

---

## Step 0: Planning, environment audit, and documentation setup
**Date:** 2026-09-23 to 2026-09-24 · **Commit:** `18c5cdf` docs: add working rules, build-scribe agent, and planning records (committed during Step 2, when git was set up)

**Goal.** Understand the starting point on the development machine (the plan named a Mac Mini; work so far has been on a MacBook Air, see the [correction](#between-steps-4-and-5-deployment-options-teach-back-and-a-machine-correction)), agree on the Phase 1 stack before writing any code, and set up a way to record every step, decision, and lesson.

**What we did.**

*Part A: planning and environment audit (2026-09-23)*
- The developer shared a master context document describing the whole project: an AI movement and exercise programming app built progressively from LLM to RAG to agent to workflow to production. We are in Phase 1, Production RAG Fundamentals.
- Audited the machine. The project folder `/Users/musabs1/rag-motion` was empty and was not a git repository.
- Claude Code asked the developer to pick an embedding model, an LLM (large language model, the AI that reads and writes text), a packaging tool, and a git setup. The developer did not know what an embedding model or a packaging tool was. Claude explained both in plain language and asked again.
- Wrote a 13-step Phase 1 plan (steps 0 to 12). The developer approved it but asked to go one step at a time instead of executing the whole plan, and asked for a documentation agent to record everything.

*Part B: documentation setup (2026-09-24)*
- Created `CLAUDE.md` at the repo root. Claude Code reads it automatically at the start of every session. It records the working rules (one step per turn, explain before building, document, commit), the step table, the stack decisions, and the brief template for the scribe.
- Created `.claude/agents/build-scribe.md`, a project-level Claude Code [subagent](concepts.md#subagent) definition.
- Saved the developer's preferences to Claude Code's memory: new to Python tooling, wants plain-language explanations, wants to go one step at a time, and wants every step documented.
- Ran the scribe for the first time to create `docs/` and backfill everything from planning.

**Commands.** All read-only checks from Part A.

```bash
python3 --version        # Python 3.12.8
which uv                 # not found
which poetry             # not found
which psql               # not found
which postgres           # not found
brew info uv             # Homebrew is at /opt/homebrew/bin/brew; uv 0.12.17 is available to install
docker info              # Docker daemon is running
docker images            # pgvector/pgvector:pg16, postgres:15-alpine, postgres:16-alpine already pulled
git --version            # git 2.39.5
gh auth status           # GitHub CLI logged in as muskii1z
docker compose version   # Docker Compose v5.0.1

env | grep -iE '^(ANTHROPIC|OPENAI|VOYAGE|COHERE|LANGSMITH|LANGCHAIN)_' | cut -d= -f1
# Printed only ANTHROPIC_BASE_URL, so no API key variables were set.
# cut -d= -f1 keeps the part before "=", so only variable names print, never values.

python3 -m pip list | grep -iE 'anthropic|openai|fastapi|sqlalchemy|psycopg|pgvector|pydantic|voyage|sentence'
# anthropic 0.86.0, pydantic 2.12.5, pydantic_core 2.41.5 installed globally

ls ~/.config/anthropic   # no Anthropic CLI profile found
```

The `ant` CLI was also not installed.

The globally installed Python packages do not matter, because the project will get its own [virtual environment](concepts.md#virtual-environment).

**What we saw.**
- Everything needed for Postgres is already on the machine through Docker (a tool that runs software in isolated containers). The `pgvector/pgvector:pg16` image is PostgreSQL 16 with pgvector, an extension that lets Postgres store and search vectors. No local Postgres install is needed.
- None of the Python packaging tools (uv, poetry) were installed.
- The developer will supply API keys later. Steps 1 to 5 need no keys, so work can start immediately.
- The scribe cannot see the main conversation. The main session must send it a structured brief after each step. This keeps the docs accurate and keeps the main conversation focused on building.
- Agent definition files are loaded when a Claude Code session starts. So this first scribe run used a general-purpose agent told to follow `build-scribe.md`. Future sessions can call `build-scribe` by name.

**Problems and fixes.** None.

**Open questions.**
- The Anthropic and Voyage API keys have not been supplied yet. They are not needed until the first Claude call (Step 6) and first embedding (Step 7).
- The LLM choice (Claude Opus 5) was a default, because the developer deferred the decision. See [0003](decisions/0003-llm-claude-opus-5.md).

**Learned.**
- [LLM vs embedding model](concepts.md#llm-vs-embedding-model)
- [Why Anthropic doesn't sell embeddings](concepts.md#why-anthropic-doesnt-sell-embeddings)
- [Embedding](concepts.md#embedding)
- [Package manager](concepts.md#package-manager)
- [Virtual environment](concepts.md#virtual-environment)
- [Lockfile](concepts.md#lockfile)
- [uv vs pip and venv](concepts.md#uv-vs-pip-and-venv)
- [Why .env stays out of git](concepts.md#why-env-stays-out-of-git)
- [Subagent](concepts.md#subagent)
- [CLAUDE.md](concepts.md#claudemd)

**Decisions.**
- [0001. Packaging with uv](decisions/0001-packaging-uv.md)
- [0002. Embeddings with Voyage AI voyage-4-lite](decisions/0002-embeddings-voyage-4-lite.md)
- [0003. LLM: Claude Opus 5](decisions/0003-llm-claude-opus-5.md)
- [0004. Database: PostgreSQL 16 + pgvector in Docker](decisions/0004-database-postgres-pgvector.md)
- [0005. Database access: psycopg 3 with raw SQL](decisions/0005-database-access-psycopg-raw-sql.md)
- [0006. Interface: CLI first, thin FastAPI at Step 12](decisions/0006-interface-cli-first.md) (FastAPI renumbered to Step 16 in Step 5)
- [0007. Version control: git and a private GitHub repo](decisions/0007-version-control-git-github.md)
- [0008. Documentation with a build-scribe subagent](decisions/0008-documentation-build-scribe.md)

---

## Step 1: Install uv, create the Python project, add dependencies
**Date:** 2026-09-24 · **Commit:** `35b4345` chore: initialize Python project with uv (committed during Step 2, when git was set up)

**Goal.** Give the project a private, reproducible Python environment with every library later steps need.

**What we did.**
- Installed uv (the [package manager](concepts.md#package-manager) chosen in [0001](decisions/0001-packaging-uv.md)) with Homebrew.
- Turned the folder into a Python project with `uv init`. We chose the "package" layout, so our own code lives in `src/ragmotion/` and scripts, tests, and the later API can all import it the same way. See [Package layout](concepts.md#package-layout).
- Passed `--vcs none` on purpose. `uv init` creates a git repository by default, but git setup is its own step (Step 2).
- Added six runtime [libraries](concepts.md#library) and one development-only library (pytest).
- Replaced uv's placeholder description in `pyproject.toml` with "AI-native movement and exercise programming: RAG over an exercise knowledge base".
- Ran an import check inside the project and compared it with the Mac's global Python.
- Wrote no application code. This step only sets up the workspace.

**Commands.**

```bash
brew install uv
# Installed uv 0.12.18. (Step 0's audit had seen 0.12.17 available; Homebrew had a newer version by now.)

uv init --package --name ragmotion --python 3.12 --vcs none
# Created pyproject.toml, .python-version (3.12), README.md, and src/ragmotion/__init__.py.
# pyproject.toml started with dependencies = [].
# uv filled in the author field from the developer's git config.

uv add anthropic voyageai "psycopg[binary]" pgvector pydantic pydantic-settings
# Asked for 6 libraries. uv installed 62 packages in total.

uv tree --depth 1
uv tree --depth 2
uv tree --invert --package langchain-core --depth 2
# Used to find out why unexpected packages (langchain-core, langsmith, huggingface-hub,
# pillow, numpy) were installed. --invert shows "who depends on this package"
# instead of "what does this package depend on".

uv add --dev pytest
# Added pytest 9.1.1 under [dependency-groups] dev in pyproject.toml.

uv run python -c "import anthropic, voyageai, psycopg, pgvector, pydantic, pydantic_settings, pytest ..."
# Printed the interpreter path and versions, then ALL IMPORTS OK.

python3 -c "import anthropic; print(anthropic.__version__)"   # Mac's global Python: 0.86.0
python3 -c "import voyageai"                                   # Mac's global Python: ModuleNotFoundError

uv run ragmotion
# Ran uv's placeholder entry point. Printed "Hello from ragmotion!"
```

**What we saw.**
- Installed versions: Python 3.12, anthropic 1.8.0, voyageai 0.5.0, psycopg 3.3.6 (with psycopg-binary 3.3.6), pgvector 0.5.0, pydantic 2.13.5, pydantic-settings 2.15.0, pytest 9.1.1.
- **Six libraries became 62 packages.** `uv tree` showed the chain: voyageai depends on langchain-text-splitters, which depends on langchain-core, which depends on langsmith. voyageai also pulls in numpy, pillow, tokenizers, aiohttp, requests, and tenacity. We never asked for LangChain, but it is already in the environment because of Voyage. See [Transitive dependencies](concepts.md#transitive-dependencies).
- `uv.lock` is 2,217 lines and pins the exact version of all 62 packages.
- `pyproject.toml` records minimum versions (for example `"anthropic>=1.8.0"`). `uv.lock` records exact versions. `pyproject.toml` says what we need; the lockfile says exactly what we got.
- Inside the project, `sys.executable` (the path of the Python program actually running) was `/Users/musabs1/rag-motion/.venv/bin/python`.
- **Isolation proof.** The Mac's global Python still has anthropic 0.86.0, and `import voyageai` fails there. The project has anthropic 1.8.0 and voyageai works. The two environments do not affect each other. See [Virtual environment](concepts.md#virtual-environment).
- The project uses the anthropic SDK (software development kit: the official library for calling Anthropic's API) 1.x series, not the 0.x series installed globally.
- `README.md` was created by `uv init` but is currently empty. The real README is planned for Step 12 (renumbered to Step 16 in [Step 5](#step-5-write-20-exercises-seed-script-query-by-hand)).

**Problems and fixes.** None. The surprise was the package count (6 requested, 62 installed), which we investigated with `uv tree` and explained.

**Developer questions.**
- *"So step 1 is installing uv and making the Python libraries?"* Almost. We don't make the libraries; other people wrote and published them, and we download them into the project. Step 1 has three parts: install uv, turn the folder into a Python project, and download the libraries into its private environment. No application code is written.
- *"Is the scribe agent getting this?"* The scribe doesn't see the conversation live. At the end of each step the main session sends it a brief that includes the developer's questions and answers.

**Minor choices (no separate decision record).**
- `--package` layout (code under `src/ragmotion/`) instead of uv's default flat script layout, because later steps need scripts, tests, and a FastAPI app to import the same code.
- `--vcs none`, to keep git setup as its own step (Step 2).

**Learned.**
- [Library](concepts.md#library) (new)
- [pyproject.toml](concepts.md#pyprojecttoml) (new)
- [Lockfile](concepts.md#lockfile) (extended: `uv.lock` specifics)
- [Virtual environment](concepts.md#virtual-environment) (extended: `.venv` and the isolation proof)
- [.python-version](concepts.md#python-version) (new)
- [Transitive dependencies](concepts.md#transitive-dependencies) (new)
- [Runtime vs dev dependencies](concepts.md#runtime-vs-dev-dependencies) (new)
- [uv run](concepts.md#uv-run) (new)
- [Package layout](concepts.md#package-layout) (new)
- [What each library is for](concepts.md#what-each-library-is-for) (new)

**Decisions.**
- No new decision records.
- Updated [0002. Embeddings with Voyage AI voyage-4-lite](decisions/0002-embeddings-voyage-4-lite.md): its Tradeoffs now note that the voyageai library brings LangChain core and LangSmith packages into the environment.

---

## Step 2: Git setup, secret protection, and private GitHub repo
**Date:** 2026-09-24 · **Commit:** `b536be5`, `18c5cdf`, `35b4345` (three commits, listed below)

**Goal.** Put the project under version control with secrets protected, and back it up to a private GitHub repo on the developer's muskii1z account.

**What we did.**
- The developer already knows git from other projects, so explanations were kept short. They asked specifically that the repo go to the **muskii1z** GitHub account.
- Checked, before creating anything, that the GitHub CLI (`gh`, GitHub's command-line tool) was logged in as muskii1z, and that no repo named `rag-motion` existed there yet.
- Wrote `.gitignore` (the list of files git must never track). It excludes:
  - `.env` and any `.env.*` file, except `.env.example`
  - the `.venv` folder, Python caches (`__pycache__`, `*.pyc`), and build output (`build/`, `dist/`, `*.egg-info/`)
  - tool caches (pytest, ruff, mypy)
  - OS and editor noise (`.DS_Store`, `.idea/`, `.vscode/`)
  - `.claude/settings.local.json` (per-machine Claude Code settings). The shared agent definition in `.claude/agents/` **is** committed.
- Wrote `.env.example` with three settings and blank key values:
  - `DATABASE_URL`, pre-filled with the local Docker default `postgresql://postgres:postgres@localhost:5432/ragmotion`. This is a local development password, not a real secret. The database itself arrives in Step 3.
  - `ANTHROPIC_API_KEY`, blank (needed from Step 6).
  - `VOYAGE_API_KEY`, blank (needed from Step 7).
- Replaced the empty `README.md` that `uv init` created with a short placeholder: what the project is, the current phase, the RAG pipeline in one line, the stack, and links to the build log, decisions, and concepts. The full README is planned for Step 12 (now Step 16).
- Ran `git init` on branch `main`. Before committing, previewed exactly which files git would track, confirmed `.venv` and `.env` were ignored, and scanned the files about to be committed for anything shaped like an API key or token. None found. See [Secret check before the first commit](concepts.md#secret-check-before-the-first-commit).
- Made three small commits instead of one big one, so the history reads in order: safety files first, then planning docs (Step 0), then the Python project (Step 1). See [Small, ordered commits](concepts.md#small-ordered-commits).
- Created the private GitHub repo `muskii1z/rag-motion` and pushed.
- Verified on GitHub's side: owner, visibility, the commits, author linking, and that no `.env` or `.venv` was uploaded.

**Commands.**

```bash
# Check the GitHub account before creating anything
gh auth status                       # logged in as muskii1z, the active account, https protocol
gh api user --jq '.login'            # muskii1z (the API agreed with gh auth status)
gh repo view muskii1z/rag-motion     # "Could not resolve", so the repo name was free
git config --global user.name        # Musab Saraswat; commits use the developer's git email
git config --global credential.helper  # nothing set globally

# Initialize and check before the first commit
git init -b main
git add -A --dry-run                 # preview only: 21 files, no .venv, no .env
git check-ignore -v .venv .env       # both ignored, and it printed which .gitignore rule matched
# grep over the to-be-committed files for key-shaped strings:
# sk-ant- (Anthropic), gho_ / ghp_ (GitHub tokens), Voyage-style keys, API_KEY=<value>
# Result: no secrets found

# Three commits
git commit   # b536be5  chore: add gitignore and env template
git commit   # 18c5cdf  docs: add working rules, build-scribe agent, and planning records
git commit   # 35b4345  chore: initialize Python project with uv

# Create the repo and push
gh repo create muskii1z/rag-motion --private --description "..." --source=. --remote=origin
git -c credential.helper= -c 'credential.helper=!gh auth git-credential' push -u origin main
# Pushed main and set it to track origin/main.
# The two -c flags apply to this one command only (explained below).

# Verify on GitHub's side
gh repo view muskii1z/rag-motion                # owner muskii1z, visibility PRIVATE, default branch main
gh api repos/muskii1z/rag-motion/commits        # all 3 commits present, each author linked to GitHub user muskii1z
gh api repos/muskii1z/rag-motion/contents       # no .env or .venv present
```

**What we saw.**
- Repo URL: https://github.com/muskii1z/rag-motion (private).
- All three commits show as authored by muskii1z on GitHub. GitHub links a commit to an account by the commit's email address, and the developer's git email is linked to muskii1z.
- **The push was pinned to one account.** A Mac can hold saved GitHub passwords for more than one account (for example in the Mac keychain). The push command told git, for that single command only, to ignore every saved [credential helper](concepts.md#credential-helper) and use the GitHub CLI's login instead. That guaranteed the push went as muskii1z, without changing the developer's global git settings.
- The dry run and the GitHub contents check agreed: `.env` and `.venv` never left the machine.
- The working tree was clean after the three commits.

**Problems and fixes.**
- `README.md` was empty, because `uv init` creates an empty one (noted in Step 1). The README is the first thing a visitor sees on GitHub, so we wrote a short placeholder before the first push.
- No other problems.

**Developer questions.**
- *"Make sure this will go to the muskii1z account on GitHub."* Checked before and after. Before: the GitHub CLI's active login was muskii1z, and the API confirmed it. During: the repo was created explicitly as `muskii1z/rag-motion`, and the push was forced to use the CLI's muskii1z credentials. After: GitHub shows the repo owned by muskii1z and all three commits linked to muskii1z.

**Minor choices (no separate decision record).**
- Three commits instead of one, ordered safety files, then planning docs, then the Python project. The safety files (`.gitignore`, `.env.example`) went in first, so the ignore rules were in place before anything else was committed.
- `DATABASE_URL` is pre-filled in `.env.example` because it is a local Docker default, not a secret. The two API keys are left blank.

**Learned.**
- [.gitignore](concepts.md#gitignore) (new)
- [Why .env stays out of git](concepts.md#why-env-stays-out-of-git) (extended: the actual `.env.example` contents)
- [Secret check before the first commit](concepts.md#secret-check-before-the-first-commit) (new)
- [Small, ordered commits](concepts.md#small-ordered-commits) (new)
- [Credential helper](concepts.md#credential-helper) (new)

**Decisions.**
- No new decision records.
- Updated [0007. Version control: git and a private GitHub repo](decisions/0007-version-control-git-github.md) with an "Implemented in Step 2" note: repo URL and the three commit hashes.

---

## Between Steps 2 and 3: Understanding the database and search types
**Date:** 2026-09-24 · **Commit:** not committed (this docs update is committed right after it is written)

**Goal.** Make sure the developer understands what the database is, where it runs, what pgvector adds, and how the main types of search in RAG differ, before building any of it.

**What we did.**
- A question-and-answer session only. No code, commands, or project files changed.
- Developer background: before this project, the developer's database experience was SQLite and some Supabase. The answers built on that.
- Most of the substance is in [concepts.md](concepts.md), under Databases and Embeddings and retrieval.

**Commands.** None.

**What we saw.** Nothing was run.

**Developer questions.**
- *"Explain this a bit. I've done nothing with databases besides SQLite and some Supabase. Where is this PostgreSQL, and what does the pgvector extension do exactly?"*
  Supabase already is PostgreSQL, hosted in the cloud with extra tools on top. The difference from SQLite is that Postgres is a server (a program that runs all the time and accepts connections), not a file. In this project it runs on the developer's MacBook Air inside a Docker container, with its data saved in a Docker volume, and our code reaches it at `localhost:5432`. pgvector adds a vector column type, distance operators for measuring similarity, and special indexes for speed. The payoff is meaning-based search and normal column filters in one SQL query.
  See [SQLite vs PostgreSQL](concepts.md#sqlite-vs-postgresql), [Supabase is PostgreSQL](concepts.md#supabase-is-postgresql), [Docker, images, and containers](concepts.md#docker-images-and-containers), [Docker volume](concepts.md#docker-volume), [localhost and port 5432](concepts.md#localhost-and-port-5432), [Where the database runs in this project](concepts.md#where-the-database-runs-in-this-project), [pgvector](concepts.md#pgvector).
- *"So is this what you meant by semantic search and hybrid vs just regular search RAG?"*
  Partly. Vector search plus column filters is "semantic search plus metadata filtering". "Hybrid" means something narrower: keyword search and semantic search run together, with the two result lists merged. Reranking is a further, optional stage. We start with basic semantic search, measure it with an evaluation set at Step 11 (now Step 15, after the plan change in [Step 5](#step-5-write-20-exercises-seed-script-query-by-hand)), then add the other techniques one at a time and measure again.
  See [Keyword search](concepts.md#keyword-search), [Semantic search](concepts.md#semantic-search), [Metadata filtering](concepts.md#metadata-filtering), [Hybrid search](concepts.md#hybrid-search), [Reranking](concepts.md#reranking), [Basic vs production-style RAG](concepts.md#basic-vs-production-style-rag).

**Problems and fixes.** None.

**Learned.**
- Databases: [SQLite vs PostgreSQL](concepts.md#sqlite-vs-postgresql), [Supabase is PostgreSQL](concepts.md#supabase-is-postgresql), [Docker, images, and containers](concepts.md#docker-images-and-containers), [Docker volume](concepts.md#docker-volume), [localhost and port 5432](concepts.md#localhost-and-port-5432), [Where the database runs in this project](concepts.md#where-the-database-runs-in-this-project), [pgvector](concepts.md#pgvector) (all new)
- Embeddings and retrieval: [Keyword search](concepts.md#keyword-search), [Semantic search](concepts.md#semantic-search), [Metadata filtering](concepts.md#metadata-filtering), [Hybrid search](concepts.md#hybrid-search), [Reranking](concepts.md#reranking), [Basic vs production-style RAG](concepts.md#basic-vs-production-style-rag) (all new); [Embedding](concepts.md#embedding) (extended)

**Decisions.**
- No new decision records.
- Updated [0004. Database: PostgreSQL 16 + pgvector in Docker](decisions/0004-database-postgres-pgvector.md) with a note that this discussion confirmed its rationale.

---

## Step 3: Docker Compose, start Postgres, confirm pgvector
**Date:** 2026-09-24 · **Commit:** `5d66ed2` feat: add PostgreSQL 16 + pgvector via docker compose

**Goal.** Run PostgreSQL 16 with pgvector locally in Docker, switch pgvector on in the project database, and prove the data survives a container restart.

**What we did.**
- **Checked the port before choosing one.** Port 5432 (Postgres's standard port) was free on the Mac. But `docker ps -a` showed the developer's other projects also run Postgres in Docker:
  - `jobscout-db-1` (image `pgvector/pgvector:pg16`), running, on Mac port 5433.
  - `vh_technology-db-1` (image `postgres:16-alpine`), stopped, but configured for Mac port 5432. Starting it later would collide with rag-motion if rag-motion also used 5432.
- **Chose Mac port 5434** to avoid both. Inside the container, Postgres still listens on its normal 5432; Docker forwards Mac port 5434 to it. See [Port mapping](concepts.md#port-mapping) and [0009](decisions/0009-local-db-port-5434-localhost-only.md).
- **Wrote `docker-compose.yml`** (a file that describes a container setup so it starts with one command; see [Docker Compose](concepts.md#docker-compose)). It defines one service, `db`:
  - image `pgvector/pgvector:pg16`
  - `POSTGRES_USER=postgres`, `POSTGRES_PASSWORD=postgres`, `POSTGRES_DB=ragmotion`. These are local-only development credentials, not a real secret.
  - ports `"127.0.0.1:5434:5432"`. The `127.0.0.1` part means only this Mac can connect, not other devices on the network. See [Binding the database to localhost only](concepts.md#binding-the-database-to-localhost-only).
  - a named volume `pgdata` mounted at `/var/lib/postgresql/data`, where Postgres keeps its files.
  - a healthcheck that runs `pg_isready -U postgres -d ragmotion` every 5 seconds. See [Healthcheck (started vs ready)](concepts.md#healthcheck-started-vs-ready).
  - A comment header listing the start, stop, and wipe commands.
- **Updated `DATABASE_URL`** in `.env.example` to `postgresql://postgres:postgres@localhost:5434/ragmotion`.
- Started the database, checked the version, showed that pgvector was available but not yet enabled, enabled it, and tried the `<=>` distance operator on tiny made-up vectors.
- **Persistence test.** Deleted the container, started a brand-new one, and checked that pgvector was still enabled.
- Updated `CLAUDE.md`: Step 3 marked done, Step 4 next, and the stack line now notes port 5434 and the start command.

**Commands.**

```bash
# Before starting: is the port free, and what else is running?
lsof -nP -iTCP:5432 -sTCP:LISTEN   # nothing listening, so 5432 was free right now
docker ps -a                       # found jobscout-db-1 (5433, running) and vh_technology-db-1 (5432, stopped)
docker volume ls                   # no rag-motion volumes yet

# Start the database
docker compose up -d --wait
# Created network rag-motion_default, volume rag-motion_pgdata, container rag-motion-db-1.
# --wait returned only after the healthcheck passed: "Healthy".
docker compose ps
# rag-motion-db-1  Up 5 seconds (healthy)  127.0.0.1:5434->5432/tcp

# Which Postgres is this?
docker compose exec -T db psql -U postgres -d ragmotion -tAc "SELECT version();"
# PostgreSQL 16.15 (Debian) on aarch64

# Is pgvector available? Is it enabled?
docker compose exec -T db psql -U postgres -d ragmotion -c \
  "SELECT name, default_version, installed_version FROM pg_available_extensions WHERE name = 'vector';"
# vector | 0.8.6 | (empty)   -> shipped in the image, but not enabled in this database
docker compose exec -T db psql -U postgres -d ragmotion -c "\dx"
# Only plpgsql (Postgres's built-in procedural language, present in every database)

# Enable it
docker compose exec -T db psql -U postgres -d ragmotion -c "CREATE EXTENSION IF NOT EXISTS vector;"
# CREATE EXTENSION. \dx now lists: vector 0.8.6, "vector data type and ivfflat and hnsw access methods"

# Try cosine distance on made-up 3-number vectors
SELECT '[1,0,0]'::vector <=> '[1,0,0]'::vector      -- identical  0.000
     , '[1,0,0]'::vector <=> '[0.9,0.2,0]'::vector  -- similar    0.024
     , '[1,0,0]'::vector <=> '[0,0,1]'::vector      -- unrelated  1.000
     , '[1,0,0]'::vector <=> '[-1,0,0]'::vector;    -- opposite   2.000

# Persistence test
docker compose down            # stopped AND removed the container and network; the volume was kept
docker volume ls               # rag-motion_pgdata still present
docker compose up -d --wait    # a brand-new container, Healthy
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
# vector 0.8.6 -> the setting survived, because it lives in the volume
```

`docker compose exec -T db psql ...` runs `psql` (Postgres's command-line client) inside the running `db` container, so no Postgres tools need to be installed on the Mac.

**What we saw.**
- Versions: **PostgreSQL 16.15** and **pgvector 0.8.6**.
- Docker Compose named everything after the project folder: container `rag-motion-db-1`, volume `rag-motion_pgdata`, network `rag-motion_default`.
- **Available is not the same as enabled.** The image ships the pgvector code, but each database has to opt in with `CREATE EXTENSION`. Before: `installed_version` was empty and `\dx` showed only `plpgsql`. After: `vector 0.8.6` was listed. See [Extension available vs enabled](concepts.md#extension-available-vs-enabled).
- **How to read cosine distance.** 0 means identical, a small number (0.024) means very similar, 1 means unrelated, and 2 means opposite. Real Voyage embeddings have 1,024 numbers instead of 3, but they are read the same way. See [pgvector](concepts.md#pgvector).
- **Containers are disposable; the volume holds the state.** `docker compose down` deleted the container, but the volume stayed, and a brand-new container still had pgvector enabled. See [Docker volume](concepts.md#docker-volume).
- **Warning:** `docker compose down -v` also deletes the volume, and with it all the data. Plain `down` keeps it. The compose file header spells this out.
- `CREATE EXTENSION` was run by hand in this step so the developer could see the before and after. For reproducibility, the plan is for Step 4's `db/schema.sql` to begin with `CREATE EXTENSION IF NOT EXISTS vector;`, so a fresh setup doesn't depend on remembering a manual command. Planned, not built yet.

**Problems and fixes.**
- A likely port collision was spotted before it happened. The developer's `vh_technology` project is configured for Mac port 5432 and `jobscout` uses 5433. Using 5432 would have worked today (the port was free) but would break whenever `vh_technology` was started. We used 5434 instead. No actual failure occurred.

**Open questions.**
- There is no `.env` file in the repo yet, only `.env.example`. When `.env` is created (before Step 6, when the first API key is needed), it should be copied from the updated `.env.example` so it gets port 5434, not the old 5432.

**Developer questions.** None new this step. The developer said "let's do it" after the database concepts discussion, which is recorded in [Between Steps 2 and 3](#between-steps-2-and-3-understanding-the-database-and-search-types).

**Minor choices (no separate decision record).**
- The plain-text password `postgres` in `docker-compose.yml` is acceptable because the database is local-only and bound to 127.0.0.1. A deployed database would get its password from a secret manager (a service that stores and hands out secrets), never from a committed file.

**Learned.**
- [Docker Compose](concepts.md#docker-compose) (new)
- [Port mapping](concepts.md#port-mapping) (new)
- [Healthcheck (started vs ready)](concepts.md#healthcheck-started-vs-ready) (new)
- [Extension available vs enabled](concepts.md#extension-available-vs-enabled) (new, includes `\dx`)
- [Binding the database to localhost only](concepts.md#binding-the-database-to-localhost-only) (new)
- [pgvector](concepts.md#pgvector) (extended: the cosine distance scale, with real numbers)
- [Docker volume](concepts.md#docker-volume) (extended: `down` vs `down -v`, and the persistence test)
- [localhost and port 5432](concepts.md#localhost-and-port-5432) and [Where the database runs in this project](concepts.md#where-the-database-runs-in-this-project) (extended: this project now uses Mac port 5434)

**Decisions.**
- [0009. Local database on port 5434, bound to 127.0.0.1](decisions/0009-local-db-port-5434-localhost-only.md) (new)
- Updated [0004. Database: PostgreSQL 16 + pgvector in Docker](decisions/0004-database-postgres-pgvector.md) with an "Implemented in Step 3" note.

---

## Step 4: Exercise schema, create the table, inspect it in psql
**Date:** 2026-09-24 · **Commit:** `46e9b11` feat: add exercise table schema

**Goal.** Define the exercise table: its columns, their types, and the rules that keep bad data out.

### Before we started: how much does the table lock us in?

Before any SQL was written, the developer stepped back and asked a bigger question. No code or files changed during this discussion.

**The question (paraphrased).** *"How much does the table actually define things? I don't know yet what material we'll do RAG on. I'm thinking of official documentation, maybe from NASM or similar. My vision: a list of exercises with what they do and what they're for. But if I asked regular ChatGPT, it would also give me a workout structure. This should be better because it uses official documentation. For example, if I ask for 'a functional athletic lower-body workout to make me more explosive and run faster', it should fetch all the relevant things and build a really good, complete program or protocol. How much does the table matter?"*

**The answer, in five parts.**

1. **How much the table locks you in.** A table is a contract: every exercise has a name, an equipment list, a difficulty, and so on, and Postgres enforces it. Right now changing it is cheap, because the table is empty and can be dropped and recreated in seconds. Changes only get costly once real data and code depend on the table, and even then there is a standard process for it, called migrations (scripted, versioned changes to a live database's structure). The one rule that matters now: anything you want to filter on must be its own column. "Only dumbbells" needs an `equipment` column. Everything else, like coaching cues or why an exercise works, can be text in the description, and the embedding captures its meaning. See [Schema](concepts.md#schema).
2. **The vision needs two kinds of knowledge.** See [Structured vs unstructured knowledge](concepts.md#structured-vs-unstructured-knowledge).
   - *Principles:* how to train for power (low reps, maximal intent, full rest, plyometrics, sequencing, progression). These come from textbooks and guidelines. They are paragraphs of text, not rows. They would be stored by splitting documents into passages, embedding each passage, and saving them in a second table. The master context document calls this the knowledge ingestion pipeline. See [Chunking](concepts.md#chunking).
   - *Exercises:* box jumps, broad jumps, kettlebell swings, split squats, each with equipment and difficulty. That is the exercise table.
   - A strong answer to the "explosive lower body" example would pull principles from documents and matching exercises from the catalog, and cite both. The exercise catalog is needed whichever documents are chosen, so Step 4 is not wasted work. A document table would be a later step, suggested after Step 10. (Made concrete in [Step 5](#step-5-write-20-exercises-seed-script-query-by-hand): ingestion is now Steps 12 to 14.)
3. **Sources.** The organization the developer had in mind is NASM, the National Academy of Sports Medicine. For explosiveness and speed, the NSCA (National Strength and Conditioning Association) and its textbook *Essentials of Strength Training and Conditioning* is probably the better fit. Both are copyrighted textbooks, and the repo is meant to become a public portfolio, so their text cannot go in it. Three options were laid out: (a) the developer writes their own notes summarizing principles in their own words, citing NSCA or NASM for each, and we ingest the notes; this is the cleanest and uses their kinesiology background; (b) openly licensed sources, such as government guidelines (for example the U.S. Physical Activity Guidelines for Americans) and open-access research papers; (c) keep copyrighted material local only, out of git and unpublished; fine for learning, but it can't be shown in the portfolio. This matches the master context document's rule: only use content we have permission to use or redistribute. See [Content licensing in RAG](concepts.md#content-licensing-in-rag).
4. **What makes this better than ChatGPT, answered honestly.** ChatGPT already knows general training principles and would write a decent explosive lower-body program. The advantage is not that the model knows more. It is that: every claim has a source a coach can check; it only uses exercises from the catalog that fit the client's equipment and level; the developer controls and vetted the knowledge instead of trusting whatever the model absorbed from the internet; and it is measurable through evaluation. See [Why RAG beats a plain chatbot here](concepts.md#why-rag-beats-a-plain-chatbot-here).
5. **Scope.** Building a complete multi-week program is Phase 2 (the agent). Phase 1 is the foundation: ask a question, retrieve the right exercises (and later principles), and get a cited answer.

**The developer's call.** *"I'm trying to think too far ahead. Let's just continue with version one. Real simple."* This was a deliberate scoping decision: build the exercise table now, and defer both the choice of knowledge sources and the document table. It is recorded here, not as a decision record, because nothing was chosen between options yet; the options were only parked.

### Step 4 itself

**What we did.**
- The developer asked, *"What do you want to have on that table?"* Claude proposed the columns as a table, with an example value and a reason for each. The developer accepted: *"you can build that table."*
- Wrote `db/schema.sql`. It does two things, and both are safe to run again (see [Idempotent script](concepts.md#idempotent-script)):
  - `CREATE EXTENSION IF NOT EXISTS vector;` So a fresh database no longer depends on the manual command typed in [Step 3](#step-3-docker-compose-start-postgres-confirm-pgvector). This was planned in Step 3 and is now built.
  - `CREATE TABLE IF NOT EXISTS exercise (...)`.
  - The file header documents the command to apply it.
- The 14 columns and why each exists (types explained in [Column types](concepts.md#column-types)):

| Column | Type and rules | Why |
|---|---|---|
| `id` | `integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY` | Auto-numbered row ID managed by Postgres. The modern replacement for `serial`. See [Identity column and ID gaps](concepts.md#identity-column-and-id-gaps). |
| `slug` | `text NOT NULL UNIQUE` | Stable human-readable ID, e.g. `'goblet-squat'`. Used by citations and eval tests. See [Slug vs id](concepts.md#slug-vs-id). |
| `name` | `text NOT NULL` | Display name. |
| `description` | `text NOT NULL` | What the exercise is and what it trains. The main text we embed; semantic search matches against it. |
| `instructions` | `text`, optional | How to perform it. |
| `primary_muscles` | `text[] NOT NULL DEFAULT '{}'` | Filterable list of muscles. |
| `movement_pattern` | `text NOT NULL`, CHECK in (squat, hinge, lunge, push, pull, carry, core, jump) | Filterable. `jump` was included with the developer's explosiveness example in mind. |
| `equipment` | `text[] NOT NULL`, two CHECKs: non-empty (`cardinality(equipment) > 0`) and every item in (bodyweight, dumbbell, band, kettlebell, barbell, bench, box) | A list, because some exercises need two things (dumbbell + bench). |
| `difficulty` | `text NOT NULL`, CHECK in (beginner, intermediate, advanced) | Filterable. |
| `laterality` | `text NOT NULL`, CHECK in (bilateral, unilateral) | Filterable: both sides at once, or one side at a time. |
| `body_region` | `text NOT NULL`, CHECK in (lower, upper, core, full) | Filterable. |
| `source` | `text NOT NULL` | Provenance (where the information came from) is required. Nothing enters without a source. |
| `embedding` | `vector(1024)`, nullable | Empty until Step 8, then filled with Voyage `voyage-4-lite` embeddings. |
| `created_at` | `timestamptz NOT NULL DEFAULT now()` | When the row was added, filled automatically. |

- Applied the schema and inspected it with `\dt` and `\d exercise`.
- Tested the rules with four bad inserts (all rejected) and one good insert inside a [transaction](concepts.md#transaction-begin-and-rollback) that was rolled back, so the table stays empty for Step 5.
- Marked Step 4 done and Step 5 next in `CLAUDE.md`.

**Commands.**

```bash
# Apply the schema (runs psql inside the db container, reading the file from the Mac)
docker compose exec -T db psql -U postgres -d ragmotion -v ON_ERROR_STOP=1 < db/schema.sql
# CREATE EXTENSION   (NOTICE: extension "vector" already exists, skipping)
# CREATE TABLE
# ON_ERROR_STOP=1 makes psql stop at the first error instead of carrying on through the file.

docker compose exec -T db psql -U postgres -d ragmotion -c "\dt"
# \dt lists tables. One table: exercise.

docker compose exec -T db psql -U postgres -d ragmotion -c "\d exercise"
# \d describes one table: all 14 columns with types, nullability, and defaults;
# indexes exercise_pkey (id) and exercise_slug_key (the unique slug);
# and six named check constraints.
```

Rule tests. The brief recorded the result of each test, not the exact SQL typed.

| Test | Result |
|---|---|
| `difficulty` = `'expert'` | `ERROR: ... violates check constraint "exercise_difficulty_check"` |
| `equipment` = `{trx}` | `ERROR: ... violates check constraint "exercise_equipment_check1"` |
| no `source` | `ERROR: null value in column "source" ... violates not-null constraint` |
| `embedding` = `'[1,2,3]'` | `ERROR: expected 1024 dimensions, not 3` |
| valid `goblet-squat` row inside `BEGIN ... ROLLBACK` | Inserted and selected fine: `embedding` empty, `created_at` filled automatically. Then undone. `SELECT count(*)` afterwards: 0. |

**What we saw.**
- **Postgres names every constraint and reports which one failed**, for example `exercise_difficulty_check`. The equipment column has two checks, so Postgres numbered the second one `exercise_equipment_check1` (the "must be a known item" rule). This will help when debugging seed data in Step 5.
- **`vector(1024)` enforces the exact size.** A 3-number vector was rejected. So if the wrong embedding model (one with a different number of dimensions) were ever used, the database would catch it on the first insert.
- **The valid test row got `id` 4, not 1.** Each rejected insert still used up an ID number. Gaps in identity IDs are normal in Postgres, which is one reason citations use the slug, not the id. See [Identity column and ID gaps](concepts.md#identity-column-and-id-gaps).
- The table is empty and ready for Step 5.

**Problems and fixes.** None.

**Open questions.**
- Which knowledge sources to use for training principles: the developer's own notes citing NSCA or NASM, openly licensed sources, or local-only copyrighted material. Deferred by the developer's scoping decision above.
- Whether to add a document-ingestion step (a document/chunk table plus chunking and embedding) after Step 10. Not yet in the Phase 1 step table. *Resolved in [Step 5](#step-5-write-20-exercises-seed-script-query-by-hand): ingestion is now Steps 12 to 14 ([0011](decisions/0011-phase-1-plan-revision-ingestion-and-langsmith.md)).*
- The ID counter now starts past 4 because of the tests, so seeded exercises in Step 5 will not start at `id` 1. This does not matter if citations use the slug, but it will be visible when inspecting the table. (Inferred from the observation above; not checked.)

**Developer questions.**
- *"How much does the table actually define things?"* Answered in [Before we started](#before-we-started-how-much-does-the-table-lock-us-in).
- *"What do you want to have on that table?"* Answered with the column proposal above, which the developer accepted.

**Minor choices (no separate decision record).**
- Scope kept to the exercise table only. Knowledge sources and a document table are deferred (the developer's "version one, real simple" call).
- `CREATE EXTENSION` moved into `db/schema.sql`, so the database setup lives in one re-runnable file.
- `source` is required, which supports the master context document's provenance rule.

**Learned.**
- RAG design: [Structured vs unstructured knowledge](concepts.md#structured-vs-unstructured-knowledge), [Chunking](concepts.md#chunking) (not built yet), [Content licensing in RAG](concepts.md#content-licensing-in-rag), [Why RAG beats a plain chatbot here](concepts.md#why-rag-beats-a-plain-chatbot-here) (all new)
- Databases: [Schema](concepts.md#schema), [Column types](concepts.md#column-types), [NOT NULL, DEFAULT, UNIQUE, PRIMARY KEY](concepts.md#not-null-default-unique-primary-key), [CHECK constraints](concepts.md#check-constraints), [Identity column and ID gaps](concepts.md#identity-column-and-id-gaps), [Transaction (BEGIN and ROLLBACK)](concepts.md#transaction-begin-and-rollback), [Idempotent script](concepts.md#idempotent-script), [Slug vs id](concepts.md#slug-vs-id) (all new)
- Extended: [Extension available vs enabled](concepts.md#extension-available-vs-enabled) (the schema file now enables pgvector), [pgvector](concepts.md#pgvector) (dimension check), [Metadata filtering](concepts.md#metadata-filtering) (the filter columns now exist)

**Decisions.**
- [0010. Exercise table: metadata columns with CHECK constraints](decisions/0010-exercise-table-check-constraints.md) (new)

---

## Between Steps 4 and 5: Deployment options, teach-back, and a machine correction
**Date:** 2026-09-24 · **Commit:** not committed (this docs update is committed right after it is written)

**Goal.** Answer a deployment question, check the developer's understanding with a teach-back, and correct a wrong fact in the docs.

**What we did.**
- Q&A and a teach-back only. No project code, commands, or schema changed.
- **Machine correction.** The master context document said development happens on a Mac Mini, and these docs repeated it. In fact Steps 0 to 4 were all built on the developer's MacBook Air; the Mac Mini is currently unavailable. The terminal prompt showed `Musabs-MacBook-Air` and the developer confirmed it. Every "Mac Mini" mention in `docs/` was corrected.
- **Consequence recorded:** the Postgres data lives in a Docker volume on the MacBook Air only. Code travels through GitHub; the database doesn't. On another machine: clone the repo, start Docker, apply `db/schema.sql`, run the seed script (Step 5). This is one reason schema and seed data live in the repo. See [Where the database runs in this project](concepts.md#where-the-database-runs-in-this-project).
- Answered the question "Supabase or Pinecone?" (below).
- The developer explained the system back in their own words. The full teach-back, what was right, what was corrected, and the polished interview version are saved in [interview-prep.md, Teach-backs](interview-prep.md#teach-backs).

**Commands.**

```bash
# From the home folder (~):
docker compose exec db psql -U postgres -d ragmotion -c "\d exercise"
# no configuration file provided: not found

# From the project folder:
cd ~/rag-motion
docker compose exec db psql -U postgres -d ragmotion -c "\d exercise"
# Showed the exercise table.
```

**What we saw.**
- `docker compose` finds the project by looking for `docker-compose.yml` in the current folder.

**Problems and fixes.**
- **Terminal mix-up.** The `\d exercise` command above failed when run from `~`, because Docker Compose looks for `docker-compose.yml` in the current folder. Fix: `cd ~/rag-motion` first. Rule from now on: every `docker compose` and `uv` command for this project runs from `~/rag-motion`. See [Commands run relative to the current folder](concepts.md#commands-run-relative-to-the-current-folder).
- **Wrong machine in the docs.** Fixed as described above.

**Developer questions.**
- *"If I want to put this out there, would we move the database to something like Supabase or Pinecone?"* Supabase yes, Pinecone probably not; they solve different problems. Supabase is the same PostgreSQL + pgvector we run locally, hosted, so moving is: enable pgvector, run `db/schema.sql` unchanged, change `DATABASE_URL`, rerun the seed and embedding scripts. No code changes. Pinecone is vector-only, so it would sit next to Postgres, not replace it, and the two would have to be kept in sync. It makes sense at tens or hundreds of millions of vectors or very high traffic, not at 50 to 5,000 exercises. Deploying the whole app also means a backend host (Render, Fly.io, Railway), a frontend host (Netlify, Vercel), and API keys in the host's secret settings; that is Phase 6. Full reasoning in [0004](decisions/0004-database-postgres-pgvector.md#note-2026-09-24-between-steps-4-and-5-deployment-path-and-why-not-pinecone).
- *Teach-back.* The developer asked to quiz themselves by explaining what's been built. Overall picture right; two fixes: uv is a tool, not a library, and a vector is 1,024 coordinates of meaning, not a label. See [Teach-backs](interview-prep.md#teach-backs).

**Learned.**
- New: [Commands run relative to the current folder](concepts.md#commands-run-relative-to-the-current-folder) (new group: Terminal basics), [Hosted Postgres (Supabase, Neon, etc.)](concepts.md#hosted-postgres-supabase-neon-etc), [Dedicated vector database (Pinecone)](concepts.md#dedicated-vector-database-pinecone)
- Extended: [Package manager](concepts.md#package-manager) (uv is a tool, not a library), [Embedding](concepts.md#embedding) and [pgvector](concepts.md#pgvector) (a vector is coordinates of meaning; Voyage creates it, pgvector stores and compares it), [Where the database runs in this project](concepts.md#where-the-database-runs-in-this-project) (MacBook Air; code travels, the database doesn't)

**Decisions.**
- No new decision records.
- Updated [0004. Database: PostgreSQL 16 + pgvector in Docker](decisions/0004-database-postgres-pgvector.md) with the Supabase migration path, the "why not Pinecone" reasoning, and the machine note.

---

## Step 5: Write 20 exercises, seed script, query by hand
**Date:** 2026-09-24 · **Commit:** `408130e` feat: seed 20 exercises into Postgres

**Goal.** Put the first real data into the exercise table so retrieval has something to search.

### Before we started: four questions and a plan change

Before any data was written, the developer asked four questions. Together they changed the Phase 1 plan.

**Q1. "Are we drafting exercises just to do the simple version? What's the point of made-up exercises when the thing I'm supposed to learn is how to extract and chunk documents? When does that part come?"**
- The exercises are real exercises. Only the descriptions are drafted, and the developer reviews them as the domain expert.
- The catalog is not throwaway. Phase 2's program-building agent needs filterable rows, for example "3 lower-body power exercises that only need a box". That can't be pulled reliably out of textbook paragraphs. Documents answer "why and how to train"; the catalog answers "what exists". See [Structured vs unstructured knowledge](concepts.md#structured-vs-unstructured-knowledge).
- Clean, known data comes first so embeddings and search can be learned in isolation. Ingestion (getting documents into the system) adds new ways to fail: garbled text from PDFs, chunks cut mid-sentence, wrong chunk sizes, lost metadata. If ingestion is built first and results are bad, you can't tell which layer broke.
- Claude agreed the plan had a real gap. Ingestion was only "maybe after Step 10", too vague for the part the developer most wants to learn. This led to the plan change below.

**Q2. "Isn't LangSmith what helps us see what went wrong and why, and evaluate? Or am I trying to do too much?"**
- Not too much; the instinct is right. LangSmith does two things. Tracing: it records every stage of a request (the question, the embedding call, the retrieved rows and their scores, the exact prompt, the answer, tokens, latency). Evals: it stores test questions, runs the system on them, scores the results, and compares runs. See [LangSmith (tracing and evals)](concepts.md#langsmith-tracing-and-evals).
- Not yet, because there is nothing to trace until the first full pipeline exists (Step 10).
- Best placement: right after basic RAG and before ingestion. Then, when answers built from document chunks go wrong, the trace shows whether the right chunk was never retrieved, or was retrieved and ignored.
- LangSmith is already installed as a [transitive dependency](concepts.md#transitive-dependencies) of voyageai (found in [Step 1](#step-1-install-uv-create-the-python-project-add-dependencies)). It works without LangChain by wrapping our own API calls.
- Order matters. Until Step 11, our scripts print every stage themselves (manual tracing), so the developer knows what a trace should contain before using a dashboard. Likewise, we write our own eval scoring first, then view it in LangSmith.
- It needs a free account and an API key. Traces, including prompts, are stored on LangSmith's servers. That is acceptable because the project only uses fictional client data.

**Q3. "I'm not understanding the point of seeding data. 20 exercises and an LLM call, what does that do for me? That's not RAG."**
- Correct: those are pieces of RAG, not RAG.
- "Seeding" means loading the first data into a database. It is the simplest form of ingestion. The exercise data is already clean, so we just insert it. Documents (Steps 12 to 14) add "extract the text" and "chunk it" before inserting. See [Seeding](concepts.md#seeding).
- RAG means **R**etrieve from your data, **A**ugment the prompt with it, **G**enerate the answer:

```
Question: "beginner lower-body exercises with dumbbells"
   ▼  Voyage turns the question into 1,024 numbers
   ▼  pgvector compares it to all 20 exercise vectors       ← RETRIEVAL
   │     1. Goblet Squat 0.18   2. Dumbbell RDL 0.21   3. Reverse Lunge 0.24
   ▼  Prompt: "Answer using ONLY these exercises: [goblet-squat] ... Question: ..."   ← AUGMENTED
   ▼  LLM writes an answer citing [goblet-squat] etc.       ← GENERATION
```

  The scores in the diagram are illustrative, not measured. Nothing has been embedded yet.
- Which steps build which letter: Step 5 gives retrieval something to search. Step 6 is G alone. Steps 7 to 9 are R alone. Step 10 connects them into RAG. See [RAG: Retrieve, Augment, Generate](concepts.md#rag-retrieve-augment-generate).
- Why only 20 exercises: small data the developer understands can be judged by eye. A push-up showing up in "unilateral lower-body" results is instantly wrong. With 2,000 rows you couldn't tell.
- Developer's response: *"It's clear to me. Let's do it quickly."*

**Q4. "What do you need me to do meanwhile? Grab an API key from OpenRouter? I probably won't use Claude's model. And we'll need a little UI to interact with it on localhost, right?"**
- **Developer tasks.** Get an OpenRouter key (for the LLM) and a Voyage key (for embeddings; OpenRouter does not replace Voyage). Paste both into `.env` yourself, in an editor, never into the chat. Review the 20 exercises.
- **LLM provider change.** The plan ([0003](decisions/0003-llm-claude-opus-5.md)) said Claude Opus 5 through the `anthropic` library. The developer now prefers OpenRouter: one key for many models, handy for comparing models later. Tradeoffs: an extra middleman, and support for structured output varies by model. The model and library will be chosen and recorded at Step 6. Decision 0003 is now marked "under review". See [OpenRouter](concepts.md#openrouter).
- **UI.** Yes: a small local page added at Step 10, when RAG first works. It shows a question box, the answer, and the retrieved exercises with scores. This matches the master context document's "first major demo" (the answer shown next to its evidence). Before Step 10, the terminal is faster.

**Plan change.** The step table in `CLAUDE.md` was updated in this step's commit. New Phase 1 sequence:

| Step | What |
|---|---|
| 0–4 | Done |
| 5 | Exercise catalog (this step) |
| 6 | First LLM call via OpenRouter (model chosen here) |
| 7 | First embedding |
| 8 | Embed all exercises |
| 9 | Similarity search CLI |
| 10 | RAG with citations, plus a minimal local UI |
| 11 | LangSmith tracing on the RAG pipeline |
| 12 | Document ingestion: extract text from a real, openly licensed document (for example a PDF) |
| 13 | Chunking: split into passages, second table with metadata |
| 14 | Embed chunks, search exercises and documents together, answers cite both |
| 15 | Evaluation set (own scoring script first, then viewed in LangSmith) |
| 16 | FastAPI endpoint, tests, README |

- Phase 1F (metadata filters, hybrid search, reranking) comes after Step 16 and is measured against the Step 15 baseline.
- Evaluation moved after ingestion, so the baseline measures the whole system, not just the catalog.
- Renumbering: the old Step 11 (evaluation) is now Step 15; the old Step 12 (FastAPI, tests, README) is now Step 16. Earlier entries in this log keep their original wording, with notes where the numbers changed.
- Candidate first document: the U.S. Physical Activity Guidelines for Americans (a government publication, free to use and redistribute). The developer's own notes on NSCA power principles could be a second. Not decided yet. See [Content licensing in RAG](concepts.md#content-licensing-in-rag).
- Recorded as [0011](decisions/0011-phase-1-plan-revision-ingestion-and-langsmith.md).

### Step 5 itself

**What we did.**
- **Config and keys.** Updated `CLAUDE.md` (step table; stack line now says the LLM is likely via OpenRouter, confirmed at Step 6; minimal UI at Step 10; FastAPI at Step 16). In `.env.example`, added `OPENROUTER_API_KEY` (needed from Step 6), kept `VOYAGE_API_KEY`, and moved `ANTHROPIC_API_KEY` to "optional". Created `.env` by copying `.env.example` and confirmed git ignores it. The developer will paste the keys in.
- **The data: `data/exercises.json`.** 20 original exercise entries:
  - Lower body: goblet-squat, dumbbell-romanian-deadlift, glute-bridge, dumbbell-hip-thrust, dumbbell-reverse-lunge, bulgarian-split-squat, dumbbell-step-up, single-leg-romanian-deadlift
  - Power: kettlebell-swing, box-jump, broad-jump, lateral-bound (three jumps and the swing, chosen with the developer's explosiveness example in mind)
  - Upper body: push-up, dumbbell-overhead-press, one-arm-dumbbell-row, band-pull-apart, inverted-row
  - Core and carry: dead-bug, pallof-press, farmer-carry
  - Every movement pattern in the schema is covered. From the file: hinge 5, lunge 3, jump 3, pull 3, push 2, core 2, squat 1, carry 1.
  - Each description says what the exercise is, what it trains, and where it's useful. This matters because the description is the text that gets embedded and matched against questions. Each entry also has short instructions.
  - `source` for all 20 is "Drafted with AI assistance; pending coach review". That is honest provenance (a record of where content came from). After the developer reviews, it becomes "Drafted with AI assistance, reviewed by M. Saraswat".
- **New code** (in the `src/ragmotion/` package and `scripts/`):
  - `src/ragmotion/config.py`: a pydantic-settings `Settings` class that reads `.env`. `database_url` defaults to the local Docker URL, so the database works before `.env` exists. API keys are optional here, and each later step checks for the key it needs. See [Config module (pydantic-settings)](concepts.md#config-module-pydantic-settings).
  - `src/ragmotion/db.py`: `get_connection()` opens a psycopg connection and calls `register_vector`, so psycopg understands pgvector's vector type. Used as a context manager (a `with` block that commits and closes the connection automatically).
  - `src/ragmotion/models.py`: an `Exercise` Pydantic model. Its allowed values (`Literal` types) mirror the CHECK constraints in `db/schema.sql`. `slug` must be lowercase words joined by hyphens; `equipment` must be non-empty. See [Pydantic model and Literal types](concepts.md#pydantic-model-and-literal-types).
  - `scripts/seed_exercises.py`: reads and validates the whole JSON file first, rejects duplicate slugs, then [upserts](concepts.md#upsert) all rows in one [transaction](concepts.md#transaction-begin-and-rollback) with `INSERT ... ON CONFLICT (slug) DO UPDATE`. It only updates a row when something actually changed (`IS DISTINCT FROM`). When an exercise's content changes, it sets `embedding = NULL`, so the old vector gets recomputed later instead of silently mismatching the new text (see [Stale embeddings](concepts.md#stale-embeddings)). It reports inserted, updated, and unchanged counts using `RETURNING (xmax = 0)`, a Postgres trick that tells whether a row was newly inserted.

**Commands.**

```bash
cp .env.example .env
# Created .env. git check-ignore confirmed it is ignored.

uv run python scripts/seed_exercises.py
# Run 1: Validated 20 exercises. Inserted 20, updated 0, unchanged 0. Table has 20 rows.

uv run python scripts/seed_exercises.py
# Run 2: Inserted 0, updated 0, unchanged 20. Table has 20 rows.
# Proves the script is safe to re-run (idempotent).
```

Hand queries, all run with `docker compose exec -T db psql ...` from `~/rag-motion`. The brief recorded the results, not the exact SQL typed.

| Query | Result |
|---|---|
| All rows, ordered by `body_region` and `movement_pattern` | 20 rows. Lower 11, upper 5, core 2, full 2. |
| Beginner, lower body, `'dumbbell' = ANY(equipment)` | 5 rows: Dumbbell Hip Thrust `{dumbbell,bench}`, Dumbbell Reverse Lunge, Dumbbell RDL, Dumbbell Step-Up `{dumbbell,box}`, Goblet Squat. |
| Jumps plus the kettlebell swing | Box Jump, Broad Jump, Kettlebell Swing, Lateral Bound (unilateral). |
| `equipment <@ ARRAY['dumbbell','bodyweight']` (needs nothing beyond dumbbells or bodyweight) | 11 rows. |
| Count by difficulty | beginner 14, intermediate 6, advanced 0. |
| Rows with and without an embedding | 20 without, 0 with. Embeddings are filled at Step 8. |

**What we saw.**
- **"Uses dumbbells" and "only needs what I own" are different questions.** `= ANY` asks "does the equipment list contain dumbbell?". `<@` (contained by) asks "is everything this exercise needs in the set I have?". The beginner-dumbbell query with `= ANY` returned the hip thrust and the step-up, which also need a bench or a box. For a client who owns only dumbbells, those are wrong answers. The `<@` query answers the right question. This matters for metadata filtering in Phase 1F and for program building in Phase 2. See [Array operators: ANY vs contained-by](concepts.md#array-operators-any-vs-contained-by).
- **No advanced exercises.** The catalog has 14 beginner and 6 intermediate. Flagged for the developer's review.
- **Two validation layers now exist:** Pydantic in Python, CHECK constraints in Postgres. Pydantic gives clearer errors (which slug, which field) before anything reaches the database; the constraints stay as the final safety net. Tradeoff: the allowed-value lists live in two places (`models.py` and `schema.sql`) and must be kept in sync. See [Validate before write](concepts.md#validate-before-write).
- Upserting the same file twice changed nothing the second time, so re-running the seed after editing one description will touch only that row and clear only that row's embedding. (The first half was shown by run 2; the "one row" behaviour follows from the SQL and has not been tested by editing a description yet.)

**Problems and fixes.** None.

**Open questions.**
- Coach review of all 20 descriptions is pending. When it is done, `source` changes to "Drafted with AI assistance, reviewed by M. Saraswat" and the seed is re-run.
- Should the catalog include any advanced exercises? Currently 0.
- The LLM model and library (OpenRouter vs the `anthropic` SDK) are open until Step 6.
- The first document for ingestion (Step 12) is not chosen. The U.S. Physical Activity Guidelines for Americans is the candidate.
- The LangSmith account and API key are not set up yet (needed at Step 11).
- The Step 4 open question about ID gaps (seeded rows starting past `id` 4) was not checked in this step.

**Developer questions.** Q1 to Q4, answered in [Before we started](#before-we-started-four-questions-and-a-plan-change).

**Minor choices (no separate decision record).**
- Seed data lives in a JSON file in the repo, so any machine can rebuild the table from git.
- Slugs are the upsert key (`ON CONFLICT (slug)`), consistent with [Slug vs id](concepts.md#slug-vs-id).
- API keys are optional in `Settings`; each step checks for its own key, so early steps don't fail for a missing key they don't use.

**Learned.**
- New: [Seeding](concepts.md#seeding), [RAG: Retrieve, Augment, Generate](concepts.md#rag-retrieve-augment-generate), [Upsert](concepts.md#upsert), [Stale embeddings](concepts.md#stale-embeddings), [Validate before write](concepts.md#validate-before-write), [Pydantic model and Literal types](concepts.md#pydantic-model-and-literal-types), [Config module (pydantic-settings)](concepts.md#config-module-pydantic-settings), [Array operators: ANY vs contained-by](concepts.md#array-operators-any-vs-contained-by), [OpenRouter](concepts.md#openrouter), [LangSmith (tracing and evals)](concepts.md#langsmith-tracing-and-evals) (planned for Step 11)
- Extended: [Structured vs unstructured knowledge](concepts.md#structured-vs-unstructured-knowledge), [Chunking](concepts.md#chunking), [Basic vs production-style RAG](concepts.md#basic-vs-production-style-rag), [Metadata filtering](concepts.md#metadata-filtering), [Content licensing in RAG](concepts.md#content-licensing-in-rag), [Idempotent script](concepts.md#idempotent-script), [Transaction (BEGIN and ROLLBACK)](concepts.md#transaction-begin-and-rollback), [Why .env stays out of git](concepts.md#why-env-stays-out-of-git)

**Decisions.**
- [0011. Phase 1 plan revision: ingestion and LangSmith get concrete steps](decisions/0011-phase-1-plan-revision-ingestion-and-langsmith.md) (new)
- Updated [0003. LLM: Claude Opus 5](decisions/0003-llm-claude-opus-5.md): status now "under review", resolved at Step 6.
- Updated [0006. Interface](decisions/0006-interface-cli-first.md): minimal local UI at Step 10, FastAPI moved to Step 16.
- Updated [0010](decisions/0010-exercise-table-check-constraints.md): the allowed values are now mirrored in `models.py`; Phase 1F renumbered.

---

## Between Steps 5 and 6: API keys, OpenRouter setup, and the 'RAG Is Simpler Than You Think' article
**Date:** 2026-09-24 · **Commit:** not committed (this docs update and the `CLAUDE.md` change are committed and pushed right after it is written)

**Goal.** Get a working, safely stored OpenRouter key before Step 6, and decide whether a popular article on RAG strategies should change the plan.

**What we did.**
- No application code changed.
- **A.** The developer created an OpenRouter account and API key (a secret password that identifies you to a paid service) and pasted it into `.env`. We checked its format through the project's config module, then confirmed OpenRouter accepts it, without calling any model. The Voyage key is not set yet.
- **B.** The developer shared the article "RAG Is Simpler Than You Think" by Rafael Pierre (Lighthouse newsletter, June 2026) and asked for an opinion on its strategies. Claude reviewed it. The developer approved two plan changes, and the Step 15 row and the Phase 1F note in `CLAUDE.md` were updated. Neither change affects Step 6. Recorded as [0012](decisions/0012-keyword-baseline-and-query-rewriting.md).

### A. API keys and OpenRouter setup

**Developer questions.**
- *"What do I do with OpenRouter and Voyage? I've never used Voyage."* Both are websites where you create an account and copy a key into `.env`. OpenRouter gives the code access to many LLMs (Claude, GPT, Llama, and others) through one key. Voyage is a separate company that provides the embedding model; OpenRouter doesn't replace it. OpenRouter: sign in, add a few dollars of credit, create a key named `rag-motion` on the Keys page (optionally with a spending limit), and copy it immediately. Voyage: sign up at dashboard.voyageai.com and create a key under API Keys. New Voyage accounts get free usage, but Voyage may keep request rate limits (how many calls you may make per minute) very low until a payment method is added.
- *"Is a $5 limit cool?"* Yes. Claude's rough Phase 1 cost estimate with a mid-priced model: Step 6 extraction about half a cent per call; one RAG answer 1 to 2 cents (maybe 100 answers while building); one eval run 30 to 60 cents (a few runs). Total roughly $2 to $4; a top-tier model roughly doubles it. These are estimates, not measured. The limit also protects against bugs, for example a loop that calls the model over and over. When the limit is hit, calls fail with an error and nothing is charged beyond it. The time to raise it is Phase 1F, when the eval is rerun after every change. Claude committed to giving a cost estimate before any step that makes many calls.
- *"Where do I paste it / how do I get to .env?"* `.env` is in `~/rag-motion`. Finder hides files whose names start with a dot. Open it with `open -e ~/rag-motion/.env` (opens in TextEdit), paste each key right after its `=` with no quotes or spaces, and save. Alternative: in Finder, press Cmd+Shift+Period to show hidden files. Never paste keys into the chat, a screenshot, or any file other than `.env`.
- *"How do I choose a model on OpenRouter for the key?"* You don't choose it on the key. One key works with every model. The model is chosen in the code, per request, with an ID like `"provider/model-name"`. So switching models is a one-line change, and the eval step can compare models. The model will be picked at the start of Step 6 from OpenRouter's live model list, comparing price, speed, and structured-output support (the feature that forces the reply into an exact data format). Not every model has it, and Step 6 depends on it.

**Commands.**

```bash
# Suggested way to open the hidden .env file in TextEdit
open -e ~/rag-motion/.env
```

```text
# Check 1: a short Python check that loaded ragmotion.config.settings
#   Printed only: is each key set, its length, and any format problems. Never the key itself.

# Check 2: OpenRouter's free key-info endpoint (does not call any model)
GET https://openrouter.ai/api/v1/key
Authorization: Bearer <OPENROUTER_API_KEY from .env>
#   First attempt with Python's built-in urllib: SSL certificate error (see Problems and fixes)
#   Second attempt with the requests library: key accepted
```

The exact Python code for both checks is not recorded here.

**What we saw.**
- `OPENROUTER_API_KEY`: set, 73 characters, correct `sk-or-` prefix, no stray spaces or quotes.
- `VOYAGE_API_KEY`: not set yet. It is needed at Step 7, so nothing is blocked.
- Key-info endpoint: key accepted. `limit` 10, `limit_remaining` 10, `usage` 0, `is_free_tier` False. No model was called, so nothing was spent.
- The key's spending limit is $10, not the $5 the developer mentioned. See Open questions.

**Problems and fixes.**
- **SSL certificate error on the first validation attempt.** The first try used Python's built-in web tool, `urllib`, and failed with `ssl.SSLCertVerificationError: CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate`. SSL (the "S" in https) is how your computer confirms a website is really who it claims to be; it checks the site's certificate against a list of trusted certificate authorities. Cause: this Mac's Python was installed from python.org, and that installer doesn't set up the trusted list until you run its one-time "Install Certificates" setup. `urllib` relies on that list. **Fix:** used the `requests` library instead, which ships its own certificate bundle (`certifi`), and it worked immediately. The libraries the project actually uses (OpenRouter/OpenAI-style clients, `voyageai`, `requests`) bring their own certificates, so they are not affected. The global Python installation was deliberately left unchanged, because changing it affects every project on the Mac. See [SSL certificate errors on python.org Python](concepts.md#ssl-certificate-errors-on-pythonorg-python).

### B. Article review: "RAG Is Simpler Than You Think"

**The article, in brief (our summary, not a quote).** It argues that most teams over-engineer RAG. Its recommended order is keyword search first (BM25, or Postgres full-text search), then an LLM that rewrites the user's question into better search terms, and only then embeddings. It lays out six "recipes", from full-text search only up to embedding everything in advance, with a decision tree based on how fresh the data must be, what the questions look like, scale, and the team's skills. It also covers splitting questions that ask for several things at once into separate sub-searches.

**Claude's assessment: what it gets right.**
- **Start simple and measure.** Keyword search is a strong baseline that teams often skip. Adding complexity only when data shows a need matches the master context document.
- **Query rewriting is cheap and powerful.** An LLM turns a conversational question into better search terms, and you improve it by editing a prompt, not by re-indexing the data. See [Query rewriting](concepts.md#query-rewriting).
- **Jargon breaks general embeddings.** Directly relevant here. Coaches write RDL, BSS, SL RDL, Pallof. A general embedding model may not know BSS means Bulgarian split squat. Keyword matching plus a glossary handles that. See [Semantic search](concepts.md#semantic-search) (extended).
- **Multi-intent questions should be split.** "Explosive lower-body program to run faster" is really several searches: power principles, jump exercises, single-leg strength, progression. The right idea for Phase 2. See [Query decomposition (multi-intent questions)](concepts.md#query-decomposition-multi-intent-questions).

**Claude's assessment: where it's weak.**
- **Its "hybrid" has a hole.** It uses keyword search to pick about 50 candidates, then reorders them with embeddings. But keyword search misses synonyms (the article's own point), so anything keyword search never finds can't be rescued by the embedding step. The more common hybrid runs both searches separately and merges the two lists. That is the version this project plans. See [Retrieve-then-rerank vs parallel hybrid](concepts.md#retrieve-then-rerank-vs-parallel-hybrid).
- **It overstates the pain of embedding everything in advance** ("needs an ML team", "deprecation nightmare"). True at 10 million documents. At this project's scale, embedding everything should take seconds and fractions of a cent (an estimate; nothing has been embedded yet), and switching embedding models means re-running one script. By the article's own decision factors (small, stable data), pre-computing embeddings is the right call here. See [On-the-fly vs pre-computed embeddings](concepts.md#on-the-fly-vs-pre-computed-embeddings).
- **"No chunking needed with full-text search" is half true.** Chunking isn't only for embeddings. You can't paste a 200-page PDF into a prompt, and citations need to point at a specific passage. See [Chunking](concepts.md#chunking).
- **"No evaluation complexity" is wrong.** Every retrieval method needs evaluation.
- **Its numbers are illustrative, not measured**: a 60/25/10/5 split, "15x cheaper", a 0.15 similarity example.
- **Its decision tree assumes live users** (2 to 4 weeks of feedback, A/B tests, meaning showing two versions to different users and comparing). This project has no users, so the evaluation set plays that role.
- **Minor:** its agentic loop has an LLM judge its own search results. The master context document warns against relying on an LLM to evaluate its own output without independent checks.

**Plan changes (developer approved both).**
1. **Step 15 compares three retrieval modes** on the same test questions: keyword only (Postgres full-text search), semantic only (pgvector), and both combined. This gives evidence for whether embeddings actually beat keyword search on this data. Postgres already has full-text search, so it is cheap to add. Later implementation: a full-text index (`tsvector`) over name and description, and a `keyword_search()` function next to the semantic one. See [Keyword search](concepts.md#keyword-search) (extended with BM25 and Postgres full-text search).
2. **Phase 1F gains a query-rewriting experiment**, alongside metadata filtering, hybrid search, and reranking. An LLM rewrites the question before search, using a small glossary of exercise abbreviations (RDL, BSS, SL RDL, KB). Measured against the Step 15 baseline.
- `CLAUDE.md` updated: the Step 15 row and the Phase 1F note. Neither change affects Step 6.

### Wrap-up

**Open questions.**
- The key's spending limit is $10, but the developer mentioned $5. If $5 was meant, change it on OpenRouter's Keys page.
- `VOYAGE_API_KEY` is not set yet (needed at Step 7).
- The LLM model is chosen at the start of Step 6 from OpenRouter's live model list (price, speed, structured-output support). [0003](decisions/0003-llm-claude-opus-5.md) stays "under review" until then.
- Step 5's open questions (coach review, advanced exercises, first document, LangSmith key, ID gaps) are unchanged.

**Learned.**
- New: [API key hygiene](concepts.md#api-key-hygiene), [SSL certificate errors on python.org Python](concepts.md#ssl-certificate-errors-on-pythonorg-python), [Query rewriting](concepts.md#query-rewriting), [Query decomposition (multi-intent questions)](concepts.md#query-decomposition-multi-intent-questions), [Retrieve-then-rerank vs parallel hybrid](concepts.md#retrieve-then-rerank-vs-parallel-hybrid), [On-the-fly vs pre-computed embeddings](concepts.md#on-the-fly-vs-pre-computed-embeddings)
- Extended: [OpenRouter](concepts.md#openrouter) (one key, many models; model chosen per request in code), [Keyword search](concepts.md#keyword-search) (BM25 and Postgres full-text search), [Semantic search](concepts.md#semantic-search) (coaching abbreviations), [Hybrid search](concepts.md#hybrid-search) (parallel, not keyword-first), [Basic vs production-style RAG](concepts.md#basic-vs-production-style-rag) (keyword baseline at Step 15, query rewriting in Phase 1F)

**Decisions.**
- [0012. Evaluate keyword search as a baseline; add query rewriting to Phase 1F](decisions/0012-keyword-baseline-and-query-rewriting.md) (new)
- Note added to [0011](decisions/0011-phase-1-plan-revision-ingestion-and-langsmith.md): Step 15 and Phase 1F scope extended by 0012.
