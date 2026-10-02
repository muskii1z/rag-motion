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

## Update 2026-10-02 (Phase 2 structure fix)
Three more runs, 3 repeats each, after the skeleton change ([0073](0073-code-builds-the-program-skeleton-agent-fills-slots.md)): 33/36, 33/36, then 36/36 expectations; 30/30 programs passed every check in each; 0 errors; final median 8.4 s, $0.159 total. Each run found one new miss, both fixed in code ([0074](0074-no-bodyweight-preference-read-by-code.md), [0076](0076-reply-kind-labeled-from-state.md)). The review sheet for the coach is now `evals/results/programs-review-20261002-154909.md`. A gap in the expectations: `loves-back-squats` passed in 9 of 9 runs without any back squat or hip thrust, because no expectation checks that a client's stated favorites appear.

## Update 2026-10-02 (Phase 2 follow-up)
The gap above is closed with two new expectation types ([0079](0079-eval-expectations-for-favorite-lifts-and-full-days.md)): `includes_any` and `min_exercises_per_day` (4 on the four full-gym clients). With them, after the gym and named-exercise fixes: 36/36 expectations, 30/30 programs passing every check, 28/30 accepted on the first submission, 0 errors, median 8.0 s, $0.166 (`evals/results/programs-20261002-155746.json`). New review sheet for the coach: `evals/results/programs-review-20261002-155746.md`.

## Update 2026-10-02 (gym detection, likes vs dislikes)
Now 14 clients (`home-dumbbells-not-gym`, `hates-deadlifts`) and two more expectation types ([0079](0079-eval-expectations-for-favorite-lifts-and-full-days.md)). Three runs of 3 repeats each:
- First: 38/42 expectations. `missing-everything` didn't ask for the goal 2× (fixed by [0082](0082-vague-goal-counts-as-missing.md)); 2 turns ended "didn't respond" after two empty replies (fixed by [0083](0083-fallback-model-after-two-empty-replies.md)).
- Second: 36/42, with 5 errors from OpenRouter timeouts on embeddings and profile reading (an outside outage) and 1 empty-reply failure.
- Final: 42/42 expectations, 36/36 programs pass every check, 34/36 accepted on the first submission, 0 errors, median 8.5 s, $0.185 for 42 runs (`evals/results/programs-20261002-161458.json`). New review sheet for the coach: `evals/results/programs-review-20261002-161458.md`.

The first two runs' files (`programs-20261002-160746.*`, `programs-20261002-161126.*`) were left uncommitted.
