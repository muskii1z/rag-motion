# Concepts

A glossary of everything learned while building rag-motion, in plain language. Each entry says when it first came up in the [build log](build-log.md).

---

## LLMs

### LLM vs embedding model
The app uses two different AI models. The LLM (large language model, here Claude) reads text and writes text; it answers questions. The embedding model does a narrower job: it turns a piece of text into a fixed-length list of numbers (a vector) that captures its meaning. That is how the database finds relevant exercises before Claude ever sees the question.

**In an interview:** "The system uses two models with different jobs. The embedding model turns text into vectors so the database can find relevant exercises, and the LLM reads those exercises and writes the answer."

*First seen: Step 0.*

### Why Anthropic doesn't sell embeddings
Anthropic's API only offers LLMs, not embedding models. So a RAG system (retrieval-augmented generation: look up relevant data first, then give it to the LLM) built on Claude needs a second provider or a local model for embeddings. Anthropic recommends Voyage AI.

**In an interview:** "Anthropic doesn't offer embeddings, so I paired Claude with Voyage AI, which is Anthropic's recommended embeddings partner."

*First seen: Step 0.*

---

## Embeddings and retrieval

### Embedding
An embedding is a list of numbers that represents the meaning of a piece of text. Two embeddings can be compared to measure how similar their meanings are: "dumbbell glute exercise" and "hip thrust with weights" give similar vectors. An embedding does not store facts, and it cannot enforce hard constraints like "must use dumbbells". That is why metadata filtering (filtering on structured fields such as equipment or difficulty) will still be needed later.

**In an interview:** "An embedding is a numeric fingerprint of meaning. It's great for finding similar text, but it can't guarantee hard constraints, so I combine it with metadata filters."

*Between Steps 2 and 3 update:* Embeddings are also weak on exact terms. To an embedding model, an abbreviation like "RDL" is just three letters, so search by meaning alone may rank loosely related exercises above the one literally named "Dumbbell RDL". See [Semantic search](#semantic-search), [Keyword search](#keyword-search), and [Metadata filtering](#metadata-filtering).

*First seen: Step 0. Extended: between Steps 2 and 3.*

### Keyword search
Keyword search finds rows that contain the actual words in the question. Using the running example "beginner RDL variations with dumbbells", the word "RDL" (Romanian deadlift) matches an exercise named "Dumbbell RDL" exactly. It fails when the wording differs: "hip hinge" won't find "Romanian deadlift" unless those words appear in the exercise text. PostgreSQL has keyword search built in, called full-text search.

**In an interview:** "Keyword search is precise on exact terms like exercise names and abbreviations, but it's blind to synonyms. Postgres has it built in as full-text search, so it needs no extra service."

*First seen: between Steps 2 and 3.*

### Semantic search
Semantic search compares [embeddings](#embedding) instead of words, using [pgvector](#pgvector) inside the database. It matches by meaning, so "hip hinge" can find "Romanian deadlift" even with no words in common. Its weak spot is exact terms: "RDL" is just three letters to the embedding model, so it may rank loosely related exercises above the one literally named "Dumbbell RDL".

**In an interview:** "Semantic search handles paraphrases, like 'hip hinge' finding Romanian deadlifts, but it's fuzzy on exact names and abbreviations. That's the gap keyword search fills."

*First seen: between Steps 2 and 3.*

### Metadata filtering
Metadata is the structured information stored in regular columns, such as equipment and difficulty. Metadata filtering applies hard rules to those columns (equipment includes dumbbell, difficulty = beginner), written as a SQL `WHERE` clause, the part of a query that says which rows to keep. Embeddings can't guarantee these rules, because a barbell exercise can be very close in meaning to a dumbbell one. Filters turn "dumbbells only" from a hope into a rule. Note that semantic search plus filters is called "semantic search plus metadata filtering", not hybrid search.

**In an interview:** "Similarity is a ranking, not a guarantee. If a client only has dumbbells, that has to be a WHERE clause, because a barbell RDL is semantically almost identical to a dumbbell one."

*First seen: between Steps 2 and 3.*

### Hybrid search
Hybrid search runs [keyword search](#keyword-search) and [semantic search](#semantic-search) on the same question and merges the two ranked lists (results ordered best-first) into one. Each covers the other's blind spot: keyword search catches exact names like "RDL", and semantic search catches meaning like "hip hinge". "Hybrid" means this specific keyword-plus-semantic combination, not semantic search plus filters.

**In an interview:** "Hybrid search means running keyword and vector search together and merging the rankings. Keyword catches exact exercise names, vectors catch paraphrases, and in Postgres both can run against the same table."

*First seen: between Steps 2 and 3.*

### Reranking
Reranking is a second stage after retrieval. First, retrieve a wide set of candidates (say the top 20). Then a second, more careful model reorders them and the best 5 are kept. It is slower but more accurate, which is why it only runs on a short list. Voyage AI sells reranking models, so this could stay with a provider the project already uses. It is the only part of the production-style pipeline that needs a model outside Postgres.

**In an interview:** "Retrieval is tuned for recall, meaning cast a wide net, then a reranker spends more compute on just the top 20 to get precision. Voyage offers rerankers, so it wouldn't add a new vendor."

*First seen: between Steps 2 and 3.*

### Basic vs production-style RAG
The project builds the simple pipeline first and adds the more advanced pieces later, one at a time:

```
Basic RAG (Steps 9–10):
  question → semantic search → top 5 → Claude

Production-style RAG (Phase 1F, after Step 12):
  question → keyword search ┐
           → semantic search┘→ merge → metadata filters → rerank → top 5 → Claude
```

The reason is measurement. Step 11 builds an evaluation set: questions paired with the exercises that should come back. It runs against basic semantic search first, and that score is recorded as the baseline (the starting number every later change is compared to). In Phase 1F, hybrid search, filters, and reranking are added one at a time, and the same evaluation is rerun after each. That turns "better RAG" from a claim into numbers, such as "hybrid search lifted hits from X to Y". Postgres with pgvector can do everything except reranking in one database: full-text search is built in, semantic search comes from pgvector, and filters are `WHERE` clauses. This is a plan; none of it is built yet.

**In an interview:** "The plan is to build basic semantic RAG first and measure it against an eval set as a baseline, then add hybrid search, filters, and reranking one at a time and rerun the same eval, so every improvement has a number behind it." (Update this line with real numbers once Step 11 and Phase 1F are done.)

*First seen: between Steps 2 and 3.*

---

## Python tooling

### Library
A library is code that other people already wrote and published so anyone can reuse it. We don't write libraries in this project; we download and install them into it. For example, the `anthropic` library already knows how to talk to Claude, so we don't have to write that ourselves.

**In an interview:** "I lean on well-maintained libraries for the plumbing, like the Anthropic and Voyage SDKs and psycopg, and keep my own code focused on the retrieval and programming logic."

*First seen: Step 1.*

### Package manager
A Python project depends on other people's code, called libraries. A package manager installs those libraries for you, and can also create a [virtual environment](#virtual-environment) and write a [lockfile](#lockfile). This project uses uv as its package manager.

**In an interview:** "I used uv as the package manager. It handles the environment, the installs, and the lockfile in one tool."

*First seen: Step 0.*

### Virtual environment
A virtual environment is a private folder of installed libraries for one project. It keeps the project's libraries separate so they don't pollute the whole Mac or clash with other projects. For example, the Anthropic SDK was already installed globally on the Mac, but the project will get its own copy inside its environment.

**In an interview:** "Each project gets its own virtual environment, so its dependencies are isolated from the rest of the machine."

*Step 1 update:* uv created the environment in a folder called `.venv` inside the project. It is kept out of git, because it can always be rebuilt from `uv.lock`. We proved the isolation: inside the project, Python ran from `.venv/bin/python` with anthropic 1.8.0 and voyageai working. The Mac's global Python still had anthropic 0.86.0 and could not import voyageai at all. Neither environment affected the other.

**In an interview (with evidence):** "I checked isolation directly: the project had anthropic 1.8.0 while the system Python still had 0.86.0, and Voyage only existed inside the project."

*First seen: Step 0. Extended: Step 1.*

### Lockfile
A lockfile records the exact versions of every library the project used. With it, the project installs identically on another machine. In this project the lockfile is `uv.lock`.

**In an interview:** "The lockfile pins exact versions, so anyone who clones the repo gets the same dependencies I tested with."

*Step 1 update:* `uv.lock` is generated by uv and never edited by hand. It should be committed to git. It pins every installed package, including indirect ones: after Step 1 it was 2,217 lines covering 62 packages. It pairs with [pyproject.toml](#pyprojecttoml): `pyproject.toml` lists minimum versions we need (`anthropic>=1.8.0`), and `uv.lock` records the exact versions we got.

*First seen: Step 0. Extended: Step 1.*

### pyproject.toml
`pyproject.toml` is the project's ID card. It lists the project name, the Python version, the libraries the app needs (with minimum versions), and development-only tools in a separate group. Humans read and edit it; uv also updates it when you run `uv add`.

**In an interview:** "pyproject.toml declares what the project needs, with minimum versions. The lockfile records exactly what was installed. One is intent, the other is the exact result."

*First seen: Step 1.*

### .python-version
A one-line file that tells uv which Python version the project uses. Here it says `3.12`. It means everyone working on the project uses the same Python, not whatever happens to be on their machine.

**In an interview:** "The Python version is pinned in .python-version, so uv uses 3.12 everywhere."

*First seen: Step 1.*

### Transitive dependencies
Transitive dependencies are the libraries your libraries need, and the libraries those need, and so on. In Step 1 we asked for 6 libraries and got 62 packages. `uv tree` showed why: voyageai needs langchain-text-splitters, which needs langchain-core, which needs langsmith. So LangChain packages are installed even though we never asked for LangChain. You don't manage transitive dependencies by hand, but you should be able to inspect them, because they affect install size, security (every package is code you are trusting), and version conflicts.

**In an interview:** "Six direct dependencies turned into 62 installed packages. I traced it with uv tree and found the Voyage SDK pulls in LangChain core. That's a good reminder that your dependency surface is bigger than your pyproject file suggests."

*First seen: Step 1.*

### Runtime vs dev dependencies
Runtime dependencies are libraries the app needs to run: anthropic, voyageai, psycopg, and so on. Dev (development) dependencies are only needed while building the app, such as pytest for running tests. uv keeps them in separate sections of `pyproject.toml` (`dependencies` vs `[dependency-groups] dev`), so a production install can skip the dev tools.

**In an interview:** "I separate runtime and dev dependencies, so production installs don't carry test tooling like pytest."

*First seen: Step 1.*

### uv run
`uv run <command>` runs a command inside the project's virtual environment automatically. Without it, you would have to "activate" the environment by hand first, and it's easy to forget and accidentally use the Mac's global Python. For example, `uv run python` uses the project's Python, while plain `python3` used the global one.

**In an interview:** "I run everything through uv run, so commands always use the project's environment, with no manual activation step."

*First seen: Step 1.*

### Package layout
Our own code lives in a proper Python package at `src/ragmotion/`, created with `uv init --package`. A package is a folder of Python code that can be imported by name (`import ragmotion`). uv's default is a flat script layout, which is simpler but harder to share. With a package, the CLI scripts, the tests, and later the FastAPI app can all import the same code the same way.

**In an interview:** "I used a src-layout package from day one, so scripts, tests, and the API share one importable codebase instead of copying code around."

*First seen: Step 1.*

### What each library is for
The six runtime libraries installed in Step 1, and their jobs:
- **anthropic:** talks to Claude, the LLM.
- **voyageai:** talks to Voyage AI to create embeddings.
- **psycopg:** lets Python talk to PostgreSQL. The `[binary]` extra installs a ready-built version, so nothing has to be compiled.
- **pgvector:** teaches psycopg how to send and receive vector columns.
- **pydantic:** checks that data has the expected shape (for example, sessions per week must be a number).
- **pydantic-settings:** reads settings like API keys from the `.env` file.

The one dev library is **pytest**, which runs tests.

**In an interview:** "The dependency list is deliberately small: two model SDKs, a Postgres driver plus its pgvector adapter, and Pydantic for validating data and loading config."

*First seen: Step 1.*

### uv vs pip and venv
pip (installs libraries) and venv (creates virtual environments) ship with Python, but they are two separate tools and don't lock exact versions. uv is a newer single tool that creates the environment, installs libraries, and writes a lockfile automatically. It is also much faster.

**In an interview:** "I chose uv over pip and venv because it's one tool, it's fast, and it produces a lockfile automatically, with a standard pyproject.toml."

*First seen: Step 0.*

---

## Databases

### SQLite vs PostgreSQL
SQLite is a database stored in a single file. Your code opens that file and reads it directly, with no separate program running. PostgreSQL (Postgres for short) is a database server: a program that runs all the time and accepts connections. Code connects to it over the network, sends SQL, and gets rows back. The server design matters for three reasons: it handles many users writing at once (SQLite struggles with that), it supports extensions that add new abilities ([pgvector](#pgvector) is one), and local development looks the same as production, so when the app is deployed only the connection string changes.

**In an interview:** "SQLite is a file your code opens; Postgres is a server your code connects to. I wanted the server model because it handles concurrent writes, supports extensions like pgvector, and my local setup matches production except for one connection string."

*First seen: between Steps 2 and 3.*

### Supabase is PostgreSQL
Supabase hosts a PostgreSQL database in the cloud and adds a dashboard, auth (user login), and an API on top. The tables and SQL used in Supabase are the same thing this project uses. That is why Supabase gives you a connection string: the address of the database server, plus the login details, in one line of text. Supabase also offers pgvector, so this project's database work transfers directly, and the app could be pointed at Supabase later just by changing the connection string.

**In an interview:** "I'd used Supabase before, which is hosted Postgres. Running Postgres locally in Docker showed me what's underneath, and since Supabase supports pgvector, deploying there would mostly be a connection string change."

*First seen: between Steps 2 and 3.*

### Docker, images, and containers
Docker runs software in a sealed box called a container. The container has its own copy of Postgres and everything Postgres needs, so nothing is installed into the Mac itself. An image is the ready-made template a container is started from. This project uses the image `pgvector/pgvector:pg16`, which is PostgreSQL 16 with pgvector already included. It was already downloaded on the Mac Mini (found in the [Step 0](build-log.md#step-0-planning-environment-audit-and-documentation-setup) audit).

**In an interview:** "Postgres runs in a Docker container from the official pgvector image, so the database is reproducible and nothing is installed on the host machine."

*First seen: between Steps 2 and 3.*

### Docker Compose
Docker Compose reads a YAML file (a plain-text settings format based on indentation), here `docker-compose.yml`, that describes one or more containers: which image, which settings, which ports, and where to store data. One command, `docker compose up -d`, then starts the whole setup, and anyone who clones the repo gets the same setup. Without it, you would type a long `docker run` command with every option by hand and hope to remember it next time. Compose names things after the project folder, so in Step 3 it created container `rag-motion-db-1`, volume `rag-motion_pgdata`, and network `rag-motion_default`.

**In an interview:** "The database is defined in a docker-compose file that's checked into the repo, so the setup is code: image, port, volume, and healthcheck. Anyone can bring it up with one command."

*First seen: Step 3.*

### Port mapping
A container has its own ports, separate from the Mac's. A port mapping connects the two. `"127.0.0.1:5434:5432"` means: Mac port 5434 forwards to container port 5432. So Postgres inside the container still listens on its normal 5432, and our code connects to `localhost:5434` on the Mac. This is why several projects can each run Postgres on 5432 inside their own containers, as long as each one uses a different Mac port. On this Mac, `jobscout` uses 5433, `vh_technology` is set up for 5432, and rag-motion uses 5434. See [0009](decisions/0009-local-db-port-5434-localhost-only.md).

**In an interview:** "I checked what else was running before picking a port. Another project was configured for 5432, so I mapped host port 5434 to the container's 5432. Nothing inside the container changes; only the connection string does."

*First seen: Step 3.*

### Healthcheck (started vs ready)
A container being "started" doesn't mean Postgres is ready to accept connections. Postgres needs a few seconds to set itself up, especially on first run. A healthcheck is a small test Docker runs over and over to ask the program whether it's actually ready. Ours runs `pg_isready -U postgres -d ragmotion` (a tool that ships with Postgres) every 5 seconds. `docker compose up -d --wait` then returns only once the healthcheck passes, and `docker compose ps` shows the container as `(healthy)`. Without this, a script run right after startup could fail with a connection error.

**In an interview:** "Started isn't ready. The compose file has a healthcheck using pg_isready, and I start it with --wait, so nothing tries to connect before Postgres can actually accept connections."

*First seen: Step 3.*

### Extension available vs enabled
A Postgres extension (an add-on that gives the database new abilities) goes through two stages. **Available** means the extension's code is installed on the server; the `pgvector/pgvector:pg16` image ships it. **Enabled** means a specific database has switched it on with `CREATE EXTENSION vector;`. Each database opts in separately. In Step 3, `pg_available_extensions` listed `vector` 0.8.6 with an empty `installed_version`, and `\dx` (the psql command that lists enabled extensions) showed only `plpgsql` (Postgres's built-in procedural language, present in every database). After `CREATE EXTENSION`, `\dx` listed `vector 0.8.6`. Writing it as `CREATE EXTENSION IF NOT EXISTS` makes it safe to run again.

**In an interview:** "The pgvector image only makes the extension available. Each database has to run CREATE EXTENSION to turn it on. I put that line at the top of the schema file so a fresh database sets itself up." (The schema file is planned for Step 4.)

*First seen: Step 3.*

### Docker volume
A volume is a storage area Docker keeps on the Mac where the database files are actually saved. It lives outside the container. So stopping or deleting the container does not delete the data; a new container can pick up the same volume.

**In an interview:** "The container is disposable, the data isn't. Postgres writes to a Docker volume, so I can stop or recreate the container without losing anything."

*Step 3 update:* Proven by hand. The volume is named `rag-motion_pgdata` and is mounted at `/var/lib/postgresql/data`, where Postgres keeps its files. After enabling pgvector, `docker compose down` stopped and **removed** the container and its network, but `docker volume ls` still showed the volume. A brand-new container started with `docker compose up -d --wait` still had pgvector 0.8.6 enabled. Warning: `docker compose down -v` also deletes the volume, and with it all the data. Plain `down` keeps it.

**In an interview (with evidence):** "I tested it: deleted the container, started a fresh one, and the pgvector setting was still there, because the state lives in the volume. The one command to be careful with is down -v, which deletes the volume too."

*First seen: between Steps 2 and 3. Extended: Step 3.*

### localhost and port 5432
`localhost` means "this computer". A port is a numbered entry point on a computer that a particular server program listens on. 5432 is Postgres's standard port. So `localhost:5432` means "the Postgres server on this machine". It plays the same role as a Supabase connection string, just pointing at the local machine. The project's `.env.example` already uses it: `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ragmotion`.

**In an interview:** "Locally the app connects to localhost:5432, Postgres's default port. In production, that one DATABASE_URL setting changes and nothing else does."

*Step 3 update:* This project no longer uses Mac port 5432. Another local project is configured for 5432, so rag-motion maps Mac port **5434** to the container's 5432 (see [Port mapping](#port-mapping)). `.env.example` now says `DATABASE_URL=postgresql://postgres:postgres@localhost:5434/ragmotion`. Postgres inside the container still listens on 5432.

*First seen: between Steps 2 and 3. Extended: Step 3.*

### Where the database runs in this project
The database runs on the developer's Mac Mini, inside Docker. The Python code talks to it over `localhost:5432`, and the data itself sits in a Docker volume.

```
Your Mac
├── rag-motion/          ← our Python code
│      │  connects to localhost:5432
│      ▼
└── Docker
    └── container "db"   ← PostgreSQL 16 + pgvector, running
           │
           ▼
        volume           ← where the data is actually saved
```

**In an interview:** "There are three layers: my Python code, a Postgres container, and a volume holding the data. The code only knows a connection string, so I can swap the container for a hosted database without touching the code."

*Step 3 update:* Built. The real names and port:

```
Your Mac
├── rag-motion/                  ← our Python code
│      │  connects to localhost:5434 (this Mac only)
│      ▼
└── Docker
    └── container rag-motion-db-1   ← PostgreSQL 16.15 + pgvector 0.8.6, listening on 5432 inside
           │
           ▼
        volume rag-motion_pgdata     ← where the data is actually saved
```

*First seen: between Steps 2 and 3. Extended: Step 3.*

### pgvector
pgvector is an extension for PostgreSQL. Plain Postgres stores text, numbers, dates, and lists, but has no idea what an [embedding](#embedding) is. pgvector adds three things:
1. **A vector column type.** `vector(1024)` holds exactly 1,024 numbers, which is what Voyage returns for each exercise. So each exercise's meaning is stored in the same row as its name, equipment, and difficulty.
2. **Distance operators.** The main one, `<=>`, measures how far apart two vectors are, using cosine distance. A small distance means similar meaning. For example, `SELECT name FROM exercise ORDER BY embedding <=> <question vector> LIMIT 5;` means "give me the 5 exercises closest in meaning to this question".
3. **Special indexes.** An index is a lookup structure that makes searching faster, like the index at the back of a book. pgvector's indexes (for example HNSW) make vector search fast at millions of rows. With 20 exercises we don't need one, so we skip it for now.

The payoff is that meaning-based search and regular column conditions fit in one SQL query: "closest in meaning to glute exercises, but only where equipment includes dumbbells and difficulty is beginner". With a separate vector database, meaning and exercise details would be split across two systems. See [0004](decisions/0004-database-postgres-pgvector.md).

**In an interview:** "pgvector gives Postgres a vector column, a distance operator, and vector indexes. That lets me rank by meaning and filter on equipment and difficulty in a single query, instead of stitching a vector database to a relational one."

*Step 3 update:* pgvector 0.8.6 is now running and enabled in the `ragmotion` database (see [Extension available vs enabled](#extension-available-vs-enabled)). We tried `<=>` on made-up 3-number vectors to learn how to read cosine distance:

| Compared with `[1,0,0]` | Meaning | `<=>` result |
|---|---|---|
| `[1,0,0]` | identical | 0.000 |
| `[0.9,0.2,0]` | very similar | 0.024 |
| `[0,0,1]` | unrelated | 1.000 |
| `[-1,0,0]` | opposite | 2.000 |

So the scale runs from 0 (identical) to 2 (opposite), and smaller means more similar. That is why search queries use `ORDER BY embedding <=> ...` ascending. Real Voyage embeddings have 1,024 numbers instead of 3, but they are read the same way.

**In an interview (with evidence):** "Cosine distance in pgvector runs from 0 for identical to 2 for opposite, with 1 meaning unrelated. I checked that on toy vectors before trusting it on real embeddings."

*First seen: between Steps 2 and 3. Extended: Step 3.*

---

## Security

### Why .env stays out of git
API keys and passwords go in a local `.env` file. That file is listed in `.gitignore` (the list of files git must never track), so secrets never reach GitHub. A committed `.env.example` with blank values documents which variables are needed without exposing any real values.

**In an interview:** "Keys live in a git-ignored .env file. The repo only has a .env.example with blank values, so it's clear what's needed but nothing secret is committed."

*Step 2 update:* Both files now exist. `.env` holds the real values and is never committed. `.env.example` is committed and lists three settings: `DATABASE_URL` (pre-filled with the local Docker default, which is a development password, not a real secret), plus `ANTHROPIC_API_KEY` and `VOYAGE_API_KEY` left blank. Someone cloning the repo copies it to `.env` and fills in their own keys. The `.gitignore` rule ignores `.env` and every `.env.*` variant, then makes one exception for `.env.example`, so a file like `.env.local` can't slip in by accident.

**In an interview (with evidence):** "The .env.example documents every setting the app needs. The ignore rule blocks .env and all its variants except the example, and I checked GitHub after the push to confirm no .env was uploaded."

*First seen: Step 0. Extended: Step 2.*

### Secret check before the first commit
Before the first commit, three checks: preview what git would track (`git add -A --dry-run`), confirm the sensitive paths are ignored (`git check-ignore -v .venv .env`, which also names the matching rule), and search the files about to be committed for key-shaped text (for example `sk-ant-` for Anthropic keys, `ghp_` or `gho_` for GitHub tokens). This matters because once a secret is pushed to GitHub it must be treated as leaked and rotated (replaced with a new key), even if it is deleted later. Git history keeps old versions, and public repos get scanned by bots.

**In an interview:** "Before the first commit I previewed the tracked files, confirmed .env was ignored, and grepped for key patterns. A pushed secret counts as leaked even if you delete it, so the cheap time to catch it is before the commit."

*First seen: Step 2.*

### Binding the database to localhost only
A network interface is one of the ways a computer is connected (for example, the Wi-Fi connection, or the internal "this computer only" connection called 127.0.0.1). When Docker publishes a port without saying which interface, it listens on all of them (written 0.0.0.0), so other devices on the same network can try to connect. Writing the port as `"127.0.0.1:5434:5432"` limits it to programs on this Mac. That is also why the plain-text password `postgres` in `docker-compose.yml` is acceptable: it is a local development credential for a database no other device can reach. A deployed database would get its password from a secret manager (a service that stores and hands out secrets), never from a committed file. See [0009](decisions/0009-local-db-port-5434-localhost-only.md).

**In an interview:** "Even locally, I bind the database port to 127.0.0.1, so it isn't exposed to the network. The dev password in the compose file is only acceptable because of that; in production it would come from a secret manager."

*First seen: Step 3.*

---

## Version control

### .gitignore
`.gitignore` is a file listing the files and folders git must never track. It does two jobs. It protects secrets (`.env`). It also keeps out files that can be rebuilt or that only make sense on one machine: the `.venv` folder (rebuilt from `uv.lock`), Python caches, tool caches, macOS `.DS_Store` files, editor settings, and Claude Code's per-machine `.claude/settings.local.json`. The shared `.claude/agents/` folder is deliberately committed, because it defines the build-scribe for anyone working on the repo.

**In an interview:** "The .gitignore keeps out secrets, anything rebuildable like the virtual environment, and anything machine-specific, but it keeps shared project config like the agent definitions."

*First seen: Step 2.*

### Small, ordered commits
Instead of one big first commit, Step 2 made three focused ones: safety files (`.gitignore`, `.env.example`), then the planning docs, then the Python project. Each commit does one thing and has a clear message in conventional-commit style (a prefix such as `chore:` for setup or `docs:` for documentation). The safety files went first, so the ignore rules were in place before anything else was committed. For a portfolio repo, the history itself becomes part of the story a reviewer reads.

**In an interview:** "I commit in small, ordered steps with conventional-commit messages, so the git history reads like the build log: safety first, then planning, then code."

*First seen: Step 2.*

### Credential helper
When git pushes to GitHub over HTTPS (the web protocol), it needs a login token. A credential helper is the program git asks for that token. A Mac can have several: the Mac keychain, the GitHub CLI, and others, and they may hold logins for different GitHub accounts. In Step 2 the push command cleared all saved helpers and used only the GitHub CLI's (`gh auth git-credential`), and only for that one command. That guaranteed the push went as muskii1z without changing any global git settings.

**In an interview:** "With more than one GitHub account on a machine, I don't trust whatever login git picks up. I pinned the push to the GitHub CLI's credentials for that one command, then confirmed on GitHub that the commits were linked to the right account."

*First seen: Step 2.*

---

## Claude Code tooling

### Subagent
A subagent is a separate Claude instance with its own instructions and tools. The main Claude Code session hands it a task. It works only from what it is given, not from the full conversation. This project uses a subagent called build-scribe to write these docs.

**In an interview:** "I used a documentation subagent that gets a structured brief after each step. Because it can't see the conversation, the brief has to be complete, which forces me to summarize what actually happened."

*First seen: Step 0.*

### CLAUDE.md
`CLAUDE.md` is a project instructions file that Claude Code reads at the start of every session. It makes working rules last across sessions, so they don't have to be repeated. In this project it holds the one-step-at-a-time rules, the step table, the stack decisions, and the scribe brief template.

**In an interview:** "I put the project's working rules in CLAUDE.md so every AI coding session starts with the same constraints and context."

*First seen: Step 0.*
