# 0023. Phase 1 completion: tests and friendly errors before retrieval changes
**Date:** 2026-09-28 · **Step:** 16 · **Status:** accepted

## Context
After the coach-reviewed eval baseline ([Lesson 3](../build-log.md#lesson-3-the-reviewed-baseline)), two pieces of work were ready to start:

- **Step 16**, the last Phase 1 step: tests, error handling, and a README.
- **Phase 1F filters**, the fix for the system's biggest measured weakness. Forbidden-item checks passed only 2 of 5: bench exercises suggested for "only dumbbells", equipment exercises for "no equipment", and older-adult advice for a beginner adult.

Both were reasonable next moves. The filter work changes core search code (retrieval, and a new step that reads the person's limits from the question), and at this point the project had no automated tests. Only the eval could catch a mistake, and it takes minutes and costs money.

## Options considered
- **Step 16 first (tests, friendly errors, README), then filters.** Pros: a safety net under the code before the filters change it, since tests catch breakage in seconds (the eval judges answer quality; tests judge whether the code is broken); a clean before/after story for the portfolio (a finished, tested, documented Phase 1, then a measured improvement); clearer error messages speed up all later work. Cons: the biggest weakness waits a little longer.
- **Filters first, then Step 16.** Pros: attacks the biggest measured weakness right away, while the eval results and the coach's review are fresh. Cons: changes core search code with no tests to catch regressions (old bugs coming back); tests written afterwards would be tested against already-changed code, blurring the before/after comparison.

## Decision
The developer chose Step 16 first. Tests, friendly errors, a reproducible setup, and the README were built, and Phase 1 is complete. Phase 1F starts next.

In the same discussion, the order inside Phase 1F was also set, **eval first**: extend the eval (about 8–10 coach-written equipment and population questions, including one with no limits stated to catch over-filtering, plus code checks for the coach's four answer-level rules) → run a new, stricter baseline → build the filters → re-run and compare. Then larger k for "list everything" questions, query rewriting, tuned hybrid, and reranking. Program-design sources come before Phase 2. Recorded in `CLAUDE.md`.

## Tradeoffs
- The known failures (2 of 5 forbidden checks) stay in the system a while longer.
- Some eval context has to be picked up again when filter work starts, although the plan is written down in `CLAUDE.md` and the [Step 16 entry](../build-log.md#step-16-tests-error-handling-readme-phase-1-complete).
- Tests cost upkeep: when behavior changes on purpose, the tests must change with it.
- The 31 tests cover parsing, chunking, scoring, validation, errors, and three database queries. They don't check answer quality; that remains the eval's job.

## Revisit when
- Tests start failing for reasons that aren't bugs (tests too tied to details), or become slow enough to skip.
- A future phase faces the same choice ("harden or improve first"). The signal to harden first is when the next change touches core code that has no tests.
