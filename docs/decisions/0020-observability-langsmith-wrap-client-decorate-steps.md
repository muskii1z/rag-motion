# 0020. Observability with LangSmith: wrap the LLM client, decorate pipeline steps
**Date:** 2026-09-25 · **Step:** 14 · **Status:** accepted

## Context
Until Step 14, the only way to see inside a request was manual tracing: `scripts/ask.py` and the web page printed each stage (retrieved evidence, cited or not used, checks, tokens, cost, time). That worked, and it found every Step 10 and Step 13 bug. But it only showed what someone chose to print, only in the terminal or the page that ran it, and nothing was kept afterwards. There was no way to look back at yesterday's answer, or to compare two runs of the same question.

Observability means being able to see what a system did and why, after the fact. A **trace** is the record of one request as a tree of steps (called runs), each with its inputs, outputs, timing, and cost. The plan since [0011](0011-phase-1-plan-revision-ingestion-and-langsmith.md) was LangSmith, a hosted tracing and evaluation service, placed after ingestion by developer choice (see the [0011 update](0011-phase-1-plan-revision-ingestion-and-langsmith.md#update-2026-09-25-after-step-10-ingestion-moved-before-langsmith)). Step 14 had to decide how to add it. See [Step 14](../build-log.md#step-14-langsmith-tracing-on-the-rag-pipeline).

## Options considered
- **Keep manual printing only.** Nothing new to learn or trust, no data leaves the machine. But nothing is stored, runs can't be compared, and every new stage needs new print code.
- **LangSmith (chosen).** Named in the master context document. Free tier. Has built-in views for retriever steps (shows retrieved documents) and LLM steps (shows the exact prompt, response, and tokens). The SDK (`langsmith`) was already installed as a transitive dependency. Cons: a hosted service, so traces leave the machine; the code now depends on its SDK; free-tier limits.
- **Langfuse.** Open source and self-hostable, so traces could stay on our own machine or server. Not tried; more setup, and not the tool named in the master context document.
- **Plain structured logs.** Write each stage as a JSON line to a file. No third party, no account. But no tree view, no UI for retrieved documents, and comparison tooling would have to be built.

Within LangSmith, two ways to record steps, used together:
- **Wrap the client** (auto-instrumentation): `wrap_openai(client)` patches the `openai` client so every chat call is traced without touching the calling code. Inspecting the SDK showed it covers chat calls including `parse()` (structured outputs), but **not embeddings**.
- **Decorate functions** with `@traceable`: each decorated function becomes a run in the tree, nested under whichever decorated function called it. Needed for embeddings, retrieval, and our own checks.

## Decision
Use LangSmith. Wrap the LLM client once in `llm.py` (`get_client()` returns `wrap_openai(client, chat_name="llm (OpenRouter)")`), and decorate the pipeline steps with `@traceable` and a run type: `answer_question` and `extract_profile` (chain), `search_all` (retriever), `_embed` (embedding, named `embed`), `check_citations` (tool). Large outputs are summarized with `process_outputs` (vectors as `{count, dimensions}`; retrieved rows as LangSmith "documents"; the final result as answer, coverage, gaps, cited ids, citation problems, cost). Tracing is switched on by `LANGSMITH_TRACING=true` in `.env`, and traces go to the project `rag-motion`.

## Tradeoffs
- **Traces leave the machine.** Every trace, including the full prompt and the retrieved evidence, is stored on LangSmith's servers. Fine today: client data is fictional and the documents are public or project-owned. Real client data would need a review first, or a self-hosted tool.
- **SDK coupling.** Decorators from `langsmith` now sit on core functions. Removing LangSmith means removing them (or swapping in another tool's). Small cost at this size.
- **Free-tier limits.** The exact limits were not checked in this step (open question).
- **One harmless warning silenced.** Wrapping `parse()` made Pydantic print a "serializer warnings" message on every structured call. It was silenced with a targeted filter on that one message only. If a real serialization problem ever shows up with that same wording, it would be hidden too.

## Revisit when
- Before any real client data enters the system (review data handling, or self-host with something like Langfuse).
- If free-tier limits or costs start to bite, for example during repeated eval runs in Step 15 and Phase 1F.

## Note 2026-09-25 (after Step 15): trace cleanup and retention
- The retrieval eval (no LLM calls) now runs with `tracing_context(enabled=False)`; it had sent about 87 search-only traces per run and buried real questions.
- `answer_question`'s trace input is only the question (`process_inputs`); `retrieval_mode`, `k_exercises`, `k_passages` go into trace metadata. Commit `87af333`. See [Trace hygiene](../concepts.md#trace-hygiene-disable-preview-friendly-inputs-metadata).
- Free-plan retention is 14 days (part of the open free-tier question). Eval results are also kept locally in `evals/results/`.

## Note 2026-09-30: the revisit signal was hit
- The "free-tier limits or costs start to bite" signal above happened. LangSmith returned HTTP 429 "Monthly unique traces usage limit exceeded" (free plan). The app was unaffected; traces weren't stored.
- Response: tracing is off by default ([0034](0034-langsmith-tracing-off-by-default.md)), and the answer eval runs locally with LangSmith optional ([0033](0033-answer-eval-local-first-optional-langsmith.md)).
- The wrapper and decorators stay in the code. They do nothing when tracing is off, and work again as soon as it is switched on.
- The exact allowance and reset date were not recorded (still part of the open free-tier question).
