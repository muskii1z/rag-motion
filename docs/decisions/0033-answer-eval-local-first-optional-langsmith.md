# 0033. Answer eval runs locally by default; LangSmith upload is optional
**Date:** 2026-09-30 · **Step:** eval resilience (after Phase 1F F7b) · **Status:** accepted

## Context
The answer eval (`evals/run_answer_eval.py`) ran every question through LangSmith's `evaluate()`, which records each run as a LangSmith experiment (a stored, scored run over a dataset). On 2026-09-30 the server log showed LangSmith returning HTTP 429 "Monthly unique traces usage limit exceeded". The free plan's monthly trace allowance was used up. Each eval run makes about 40 traces, one per question.

The app kept working. But the eval would fail or not record its results until the allowance reset. The eval is how every change in Phase 1F was judged, so it could not depend on a free plan. The developer: "we definitely need those locked in so we can keep evals working." See [Vendor dependency](../concepts.md#vendor-dependency-keep-the-core-loop-running-without-it).

## Options considered
- **Wait for the monthly reset.** Pros: no code change. Cons: no answer evals until then; the same thing happens again next month.
- **Pay for a LangSmith plan.** Pros: nothing changes in the code; the comparison UI stays. Cons: a monthly cost for a learning project, and the eval still stops if LangSmith is down.
- **Local-first eval, LangSmith optional.** Run the same checks in our own script with tracing off, save every answer and score to a local file, and upload to LangSmith only when asked. Pros: works whether or not LangSmith is reachable; results are kept in the repo. Cons: comparing runs side by side needs our own tooling.

## Decision
Local-first. `uv run python evals/run_answer_eval.py` runs locally by default: tracing off (`tracing_context(enabled=False)`), 4 questions at a time (`ThreadPoolExecutor(4)`), the same evaluators called by argument name (`run_evaluator`, as LangSmith does), and every answer and score saved to `evals/results/answers-<run>-<timestamp>.json` with metadata (retrieval mode, filters, k, LLM, embedding and judge models, eval set hash). `--langsmith` keeps the old experiment; its results are converted to the same row format and saved locally too. A question whose pipeline fails, or a check that errors, is recorded and listed under "ERRORS" instead of being silently dropped. `reference(q)` builds the answer key for both paths. Commit `41119f8`.

Verified: a full local run while LangSmith was over its limit had no errors, and its scores were in the usual range (citations 40/40, no forbidden citations 13/13).

## Tradeoffs
- LangSmith's side-by-side comparison view only exists for `--langsmith` runs. Local JSON files need our own comparison, which doesn't exist yet.
- Local runs have no traces, so a failed question can't be opened step by step unless it is re-run with tracing on.
- The eval still depends on OpenRouter (answers and judge are model calls). Only the LangSmith dependency was removed.

## Revisit when
- Comparing local runs by hand becomes slow: write a small comparison script, or upload selected runs with `--langsmith`.
- The project moves to a paid LangSmith plan, or to a self-hosted tracing tool.
- Real client data enters the system (then local result files hold real answers and need the same care as traces).
