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
| 2 | .gitignore, .env.example, git init, first commit, private GitHub repo | done |
| 3 | Docker Compose, start Postgres, confirm pgvector | done |
| 4 | Exercise schema, create the table, inspect it in psql | done |
| 5 | Write 20 exercises, seed script, query by hand | done (coach review pending) |
| 6 | First LLM call (via OpenRouter, model chosen here): prose to structured client profile | done |
| 7 | First embedding: embed one sentence, look at the numbers | next |
| 8 | Embed all exercises, store vectors, compare two by hand | |
| 9 | Similarity search CLI, judge results by eye | |
| 10 | RAG: retrieved evidence to the LLM, cited answer, plus a minimal local UI (question, answer, evidence) | |
| 11 | LangSmith tracing on the RAG pipeline | |
| 12 | Document ingestion: pull text out of a real, openly licensed document (e.g. a PDF) | |
| 13 | Chunking: split into passages, store in a second table with metadata | |
| 14 | Embed chunks, search exercises + documents together, answers cite both | |
| 15 | Evaluation set: compare keyword-only (Postgres full-text) vs semantic-only (pgvector) vs combined on the same questions; own scoring script first, then viewed in LangSmith | |
| 16 | FastAPI endpoint, tests, README | |

Update the Status column as steps complete.

**After Step 16: Phase 1F, better RAG.** Add metadata filtering, hybrid search (keyword + semantic, run separately and merged), reranking, and query rewriting (an LLM rewrites the question before search, using a glossary of exercise abbreviations like RDL, BSS, SL RDL, KB) one at a time. Rerun the Step 15 evaluation after each change and record the scores against the baseline.

## Stack decisions (see docs/decisions/ for the reasoning)

- Python 3.12, managed with **uv** (`pyproject.toml` + `uv.lock`)
- **PostgreSQL 16 + pgvector** in Docker (`pgvector/pgvector:pg16`), on Mac port **5434** (`docker compose up -d --wait`)
- **psycopg 3** with hand-written SQL. No ORM yet
- **Voyage AI** `voyage-4-lite` embeddings (1024 dimensions), likely through OpenRouter as `voyageai/voyage-4-lite` with the same OpenRouter key; confirmed at Step 7 (a separate `VOYAGE_API_KEY` only if we call Voyage directly)
- **LLM via OpenRouter** with the `openai` SDK (OpenAI-compatible API), key in `OPENROUTER_API_KEY`. Default model `qwen/qwen3-235b-a22b-2507`, set in `src/ragmotion/config.py` or overridden with `LLM_MODEL` in .env. Always set `max_tokens`. The `anthropic` package is installed but unused (decision 0003)
- CLI scripts first. Minimal local UI at Step 10. FastAPI endpoint at Step 16

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
