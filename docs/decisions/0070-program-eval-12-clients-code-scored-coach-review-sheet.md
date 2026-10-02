# 0070. Program eval: 12 fictional clients, scored in code, with a coach review sheet
**Date:** 2026-10-02 · **Step:** Phase 2, P4 · **Status:** accepted

## Context
The program builder (an agent: a model that picks its own tool calls) had been tested by unit tests with a fake model, by replays of one conversation, and by the developer in the browser. None of these measured it across many kinds of client. The Q&A side had a 55-question eval; the program side had nothing equivalent. Some important behavior also lives outside the program checker: asking for missing details, refusing to program for pregnancy, referring a client with a sore knee, not citing adult research for a teenager.

## Options considered
- **Keep testing by hand in the browser.** Pros: finds surprises ([P3](../build-log.md#phase-2-step-3-p3-the-program-page-fixes-from-live-browser-tests-and-the-agent-back-on-gemini-25-flash) found five). Cons: not repeatable; no before/after numbers.
- **Single-message prompts scored by the checker only.** Pros: simple. Cons: misses multi-turn behavior and everything the checker doesn't check.
- **An AI judge grading each program.** Pros: can judge quality. Cons: costs more, varies run to run, and the coach's judgment is what matters.
- **Scenario conversations with per-client expectations, scored in code, plus a review sheet for the coach.** Pros: repeatable, cheap (about $0.20 for 24 runs), covers behavior beyond the checker, and keeps the quality call with a human. Cons: expectations are simple word or field checks; 12 clients is a small sample.

## Decision
`evals/program_clients.yaml` holds 12 fictional client conversations with expectations. `evals/run_program_eval.py` plays each through `run_turn`, scores the last turn in code, records errors, runs 4 clients in parallel with tracing off, supports `--runs N`, and saves a JSON file plus a Markdown review sheet with a "Coach verdict" line per program.

## Tradeoffs
- Word checks are crude: `has_referral` only looks for "professional" in the safety notes; `mentions_any` only looks for a word.
- Only the last turn is scored.
- 12 clients × 2 runs can't separate small differences from noise.
- Program quality still depends on the coach reading the sheet; there's no automated quality score.

## Revisit when
- The coach's verdicts disagree with the code scores often (the expectations miss what matters).
- The app gets a new behavior (for example program edits or approval) that needs new scenarios.
- Results need to be compared across models or prompts; then add more runs per client.
