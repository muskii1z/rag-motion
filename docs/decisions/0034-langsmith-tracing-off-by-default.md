# 0034. LangSmith tracing off by default; on to debug
**Date:** 2026-09-30 · **Step:** eval resilience (after Phase 1F F7b) · **Status:** accepted

## Context
Since Step 14 every request was traced into LangSmith (`LANGSMITH_TRACING=true`): from the terminal, the web page, and the evals. A trace is one recorded request with every step inside it. The free plan has a monthly trace allowance, and on 2026-09-30 it ran out (HTTP 429 "Monthly unique traces usage limit exceeded"). Everyday use of the app was spending the same allowance that debugging and evals need. See [Trace allowance and sampling](../concepts.md#trace-allowance-and-sampling-observability-cost).

## Options considered
- **Keep tracing everything.** Pros: every request can be looked up later. Cons: the allowance runs out again; most everyday traces are never opened.
- **Sampling** (trace a share of requests, plus all failures). Raised as what production teams do, not as something to build now. Pros: the standard production approach. Cons: more setup than this project needs today.
- **Off by default, on when debugging.** Pros: one line in `.env`; no traces wasted. Cons: a bad answer from everyday use has no trace; it must be reproduced with tracing on.

## Decision
`LANGSMITH_TRACING=false` in `.env` (only that line changed) and in `.env.example`, with a comment explaining it. To debug, set it to `true`, or put `LANGSMITH_TRACING=true` in front of one command. The app was restarted to pick it up. Commit `41119f8` (for `.env.example`; `.env` is git-ignored).

## Tradeoffs
- No automatic traces for everyday requests. A bad answer has to be reproduced with tracing on to be inspected.
- The model's answers vary between runs, so a reproduced answer may not be the same bad answer.

## Revisit when
- The app has real users: switch to sampling plus tracing all failures.
- The project moves to a paid plan or a self-hosted tracing tool with no tight allowance.
