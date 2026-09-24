# rag-motion: working rules

An AI-native movement and exercise programming app, built as an AI engineering portfolio and learning project. The developer has an exercise science background and is new to Python tooling and AI infrastructure. The goal is understanding, not speed.

Current phase: **Phase 1, Production RAG Fundamentals.** Do not jump ahead to agents, LangGraph, or a frontend.

## How every session works

1. **One step per turn.** Do the current step, then stop and wait for the developer to say go. Never batch several steps.
2. **Explain before building.** Say what the component is, why we need it, where it fits, and the main tradeoff. Use plain language. Define any term the developer may not know.
3. **Build the smallest version, run it, show the result.** The developer inspects it by hand.
4. **Document.** After each step, invoke the `build-scribe` subagent with a structured brief. It cannot see the conversation, so the brief must hold everything worth recording.
5. **Commit.** One small commit per step, conventional-commit style (`feat:`, `chore:`, `docs:`).

## Step sequence for Phase 1

| Step | What | Status |
|---|---|---|
| 0 | Documentation setup: this file, build-scribe agent, docs/ | done |
| 1 | Install uv, create the Python project, add dependencies | done |
| 2 | .gitignore, .env.example, git init, first commit, private GitHub repo | next |
| 3 | Docker Compose, start Postgres, confirm pgvector | |
| 4 | Exercise schema, create the table, inspect it in psql | |
| 5 | Write 20 exercises, seed script, query by hand | |
| 6 | First Claude call: prose to structured client profile | |
| 7 | First embedding: embed one sentence, look at the numbers | |
| 8 | Embed all exercises, store vectors, compare two by hand | |
| 9 | Similarity search CLI, judge results by eye | |
| 10 | RAG: retrieved evidence to Claude, cited answer | |
| 11 | First 20–30 eval questions, baseline run | |
| 12 | Thin FastAPI /ask, tests, README | |

Update the Status column as steps complete.

## Stack decisions (see docs/decisions/ for the reasoning)

- Python 3.12, managed with **uv** (`pyproject.toml` + `uv.lock`)
- **PostgreSQL 16 + pgvector** in Docker (`pgvector/pgvector:pg16`)
- **psycopg 3** with hand-written SQL. No ORM yet
- **Voyage AI** `voyage-4-lite` embeddings (1024 dimensions), key in `VOYAGE_API_KEY`
- **Claude Opus 5** (`claude-opus-5`) via the `anthropic` SDK, key in `ANTHROPIC_API_KEY`
- CLI scripts first. FastAPI only at step 12

## Rules

- Secrets live in `.env`, which is git-ignored. Never commit keys.
- Exercise data is original, author-written content. No scraped material.
- Use fictional client data only. No medical or diagnostic claims.
- Don't add frameworks, services, or abstractions before a step needs them.

## build-scribe brief template

When invoking build-scribe, send:

```
STEP: <number and title>
DATE: <YYYY-MM-DD>
GOAL: <one sentence>
WHAT WE DID: <bullets>
COMMANDS RUN: <commands, with short notes on output>
OBSERVATIONS: <what we saw when we ran/inspected it>
PROBLEMS AND FIXES: <or "none">
CONCEPTS LEARNED: <term: plain explanation>
DECISIONS: <choice, options considered, why, tradeoff>
DEVELOPER QUESTIONS: <questions the developer asked and the answers>
COMMIT: <hash and message, or "not committed yet">
```
