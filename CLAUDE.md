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
| 7 | First embedding: embed one sentence, look at the numbers | done |
| 8 | Embed all exercises, store vectors, compare two by hand | done |
| 9 | Similarity search CLI, judge results by eye | done |
| 10 | RAG: retrieved evidence to the LLM, cited answer, labeled general guidance, plus a minimal local UI | done |
| 11 | Document ingestion: pull text out of a real, openly licensed document (e.g. a PDF) | done (Physical Activity Guidelines) |
| 12 | Chunking: split into passages, store in a second table with metadata | done (structure-aware, 150–450 words) |
| 13 | Embed chunks, search exercises + documents together, answers cite both | done |
| 14 | LangSmith tracing on the RAG pipeline (moved after ingestion by developer choice) | done |
| 15 | Evaluation set: compare keyword-only (Postgres full-text) vs semantic-only (pgvector) vs combined on the same questions; own scoring script first, then viewed in LangSmith | done (baseline; expected answers pending coach review) |
| 16 | Harden the FastAPI app (built in Step 10): tests, error handling, README | done: **Phase 1 complete**. Revisited 2026-09-29: time limits on every OpenRouter call, clear messages for slow/down services, broken JSON twice, bad questions; mocked web API tests (`tests/test_api.py`); evals unchanged |

Update the Status column as steps complete.

## Phase 1F: better RAG (data, then test, then fix)

| Step | What | Status |
|---|---|---|
| F1 | Expand exercise catalog (20 -> 42; Claude drafts, coach reviews) | done (22 new reviewed; original 20 still pending review) |
| F2 | Strengthen the eval: update expected AND forbidden lists for the 42-exercise catalog; coach writes ~8-10 equipment/population questions; AI judge for the four answer-level rules; new baseline | done (40 questions; baseline 2026-09-28) |
| F3 | Read limits (equipment, population, level) from the question | done for equipment + population (`extract_limits`, `QuestionLimits`); level not filtered |
| F4 | Equipment filter (`equipment <@ owned`) | done: no forbidden citations 8/13 -> 12/13 |
| F5 | Population tags on chunks + filter | done: rule-based tags (`populations_for`, `scripts/tag_populations.py`); no forbidden citations 12/13 -> 13/13 |
| F6 | Re-run the eval and compare; README update | done: no forbidden advice 69% -> 100% (3 runs each); coverage keys for 3 equipment questions set to partial by coach |
| F7a | Test 5 vs 10 exercises per question | done: developer kept 5 (lists +12% complete, but more unasked-for extras on focused questions) |
| F7b | Coach's presentation rules in the answer prompt (3 versions, 3 runs each) | tried and reverted: no version beat the plain prompt; side effects on focused answers (decision 0030, accepted). Later idea: show level/bodyweight labels in code |
| F7+ | Query rewriting, reranking | not started |
| Pre-Phase 2 | Program-design sources (Schoenfeld 2021, Pelland 2024, coach's notes on NSCA Essentials ch. 18-19) | |

**Where we are (2026-09-28):** Phase 1F filters done and measured (no forbidden advice 69% -> 100%, 3 runs each). Exercises per question stay at 5 (F7a, decision 0029). Open choice for the developer: (1) optional: add the coach's presentation rules (group by muscle group; label intermediate, bodyweight, secondary) to the answer prompt and re-measure; or (2) program-design sources (Schoenfeld 2021, Pelland 2024, coach's notes on NSCA Essentials ch. 18–19), then Phase 2.

**Original Phase 1F note:** Add metadata filtering, hybrid search (keyword + semantic, run separately and merged), reranking, and query rewriting (an LLM rewrites the question before search, using a glossary of exercise abbreviations like RDL, BSS, SL RDL, KB) one at a time. Rerun the Step 15 evaluation after each change and record the scores against the baseline.

## Stack decisions (see docs/decisions/ for the reasoning)

- Python 3.12, managed with **uv** (`pyproject.toml` + `uv.lock`)
- **PostgreSQL 16 + pgvector** in Docker (`pgvector/pgvector:pg16`), on Mac port **5434** (`docker compose up -d --wait`)
- **psycopg 3** with hand-written SQL. No ORM yet
- **Voyage AI** `voyage-4-lite` embeddings (1024 dimensions) through OpenRouter as `voyageai/voyage-4-lite`, same OpenRouter key (verified Step 7). Always store text with `embed_documents()` and embed questions with `embed_query()` (`src/ragmotion/embeddings.py`)
- **LLM via OpenRouter** with the `openai` SDK (OpenAI-compatible API), key in `OPENROUTER_API_KEY`. Default model `google/gemini-2.5-flash-lite` (switched from Qwen in Step 10 for speed), set in `src/ragmotion/config.py` or overridden with `LLM_MODEL` in .env. Always set `max_tokens`. The `anthropic` package is installed but unused (decision 0003)
- **Documents**: listed in `data/sources.toml` (committed manifest with license and sha256); files in git-ignored `data/raw/`; PDFs extracted and cleaned with PyMuPDF (`src/ragmotion/ingestion.py`, `scripts/extract_document.py <source_id>`); research articles read from Europe PMC JATS XML (`format = "jats-xml"`, no PDF step); notes are Markdown; then chunked into the `document_chunk` table (`src/ragmotion/chunking.py`, `scripts/chunk_documents.py`). NSCA material enters only as original notes in `data/notes/`. Licensing policy: decision 0017
- **Tracing**: LangSmith (`langsmith` SDK). `LANGSMITH_API_KEY`, `LANGSMITH_TRACING` (false by default since 2026-09-30: the free plan's monthly trace allowance ran out; set true to debug), `LANGSMITH_PROJECT=rag-motion` in .env; `config.py` loads .env into the environment. Traced steps: answer_question > search_all > embed, llm (OpenRouter), check_citations; extract_profile. Traces include prompts and evidence (fictional/public data only)
- **Evaluation**: `evals/eval_set.yaml` (v3: 40 coach-reviewed questions; `answer_rules` graded by an AI judge, `src/ragmotion/judge.py`, model `anthropic/claude-sonnet-5.5`). `evals/run_retrieval_eval.py` (keyword vs semantic vs hybrid, no LLM) and `evals/run_answer_eval.py [--mode] [--no-filters] [--k-exercises N] [--langsmith]` (runs locally by default and saves every answer and score to `evals/results/answers-*.json`; `--langsmith` also records a LangSmith experiment). Baseline results in `evals/results/`. Semantic stays the default retrieval (best in the Step 15 baseline)
- **Tests**: `uv run pytest` (53 tests, offline; outside services mocked in `tests/test_api.py`; DB integration tests skip if Postgres is down). Friendly errors in `src/ragmotion/errors.py`
- CLI scripts plus a local web app (FastAPI + one HTML page, `src/ragmotion/app.py`). Run: `uv run uvicorn ragmotion.app:app --host 127.0.0.1 --port 8010 --reload`, open http://127.0.0.1:8010 (port 8010 avoids another local project on 8000)

## Rules

- Secrets live in `.env`, which is git-ignored. Never commit keys.
- Exercise data is original, author-written content. No scraped material.
- Use fictional client data only. No medical or diagnostic claims.
- Don't add frameworks, services, or abstractions before a step needs them.
- Answers: facts only from retrieved evidence, cited. General LLM knowledge only in the separate, labeled `general_guidance` field, never blended into the answer.

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
