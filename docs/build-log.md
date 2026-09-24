# Build log

A step-by-step journal of building rag-motion, an AI movement and exercise programming app. It is a portfolio and learning project that grows in stages: LLM, then RAG (retrieval-augmented generation: looking up relevant data first and handing it to the model), then agent, then workflow, then production. Newest entry at the bottom.

---

## Step 0: Planning, environment audit, and documentation setup
**Date:** 2026-09-23 to 2026-09-24 · **Commit:** `18c5cdf` docs: add working rules, build-scribe agent, and planning records (committed during Step 2, when git was set up)

**Goal.** Understand the starting point on the Mac Mini, agree on the Phase 1 stack before writing any code, and set up a way to record every step, decision, and lesson.

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
- [0006. Interface: CLI first, thin FastAPI at Step 12](decisions/0006-interface-cli-first.md)
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
- `README.md` was created by `uv init` but is currently empty. The real README is planned for Step 12.

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
- Replaced the empty `README.md` that `uv init` created with a short placeholder: what the project is, the current phase, the RAG pipeline in one line, the stack, and links to the build log, decisions, and concepts. The full README is planned for Step 12.
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
  Supabase already is PostgreSQL, hosted in the cloud with extra tools on top. The difference from SQLite is that Postgres is a server (a program that runs all the time and accepts connections), not a file. In this project it runs on the Mac Mini inside a Docker container, with its data saved in a Docker volume, and our code reaches it at `localhost:5432`. pgvector adds a vector column type, distance operators for measuring similarity, and special indexes for speed. The payoff is meaning-based search and normal column filters in one SQL query.
  See [SQLite vs PostgreSQL](concepts.md#sqlite-vs-postgresql), [Supabase is PostgreSQL](concepts.md#supabase-is-postgresql), [Docker, images, and containers](concepts.md#docker-images-and-containers), [Docker volume](concepts.md#docker-volume), [localhost and port 5432](concepts.md#localhost-and-port-5432), [Where the database runs in this project](concepts.md#where-the-database-runs-in-this-project), [pgvector](concepts.md#pgvector).
- *"So is this what you meant by semantic search and hybrid vs just regular search RAG?"*
  Partly. Vector search plus column filters is "semantic search plus metadata filtering". "Hybrid" means something narrower: keyword search and semantic search run together, with the two result lists merged. Reranking is a further, optional stage. We start with basic semantic search, measure it with an evaluation set at Step 11, then add the other techniques one at a time and measure again.
  See [Keyword search](concepts.md#keyword-search), [Semantic search](concepts.md#semantic-search), [Metadata filtering](concepts.md#metadata-filtering), [Hybrid search](concepts.md#hybrid-search), [Reranking](concepts.md#reranking), [Basic vs production-style RAG](concepts.md#basic-vs-production-style-rag).

**Problems and fixes.** None.

**Learned.**
- Databases: [SQLite vs PostgreSQL](concepts.md#sqlite-vs-postgresql), [Supabase is PostgreSQL](concepts.md#supabase-is-postgresql), [Docker, images, and containers](concepts.md#docker-images-and-containers), [Docker volume](concepts.md#docker-volume), [localhost and port 5432](concepts.md#localhost-and-port-5432), [Where the database runs in this project](concepts.md#where-the-database-runs-in-this-project), [pgvector](concepts.md#pgvector) (all new)
- Embeddings and retrieval: [Keyword search](concepts.md#keyword-search), [Semantic search](concepts.md#semantic-search), [Metadata filtering](concepts.md#metadata-filtering), [Hybrid search](concepts.md#hybrid-search), [Reranking](concepts.md#reranking), [Basic vs production-style RAG](concepts.md#basic-vs-production-style-rag) (all new); [Embedding](concepts.md#embedding) (extended)

**Decisions.**
- No new decision records.
- Updated [0004. Database: PostgreSQL 16 + pgvector in Docker](decisions/0004-database-postgres-pgvector.md) with a note that this discussion confirmed its rationale.
