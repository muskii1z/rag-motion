# 0024. Phase 1F order: data, then eval, then filters
**Date:** 2026-09-28 · **Step:** Phase 1F, F1 · **Status:** accepted

## Context
Phase 1 ended with a clear weakness: the system doesn't respect a person's limits (forbidden-item checks passed 2 of 5 on the coach-reviewed baseline). [0023](0023-phase-1-completion-tests-and-errors-before-retrieval-changes.md) already set "eval first, then filters" inside Phase 1F.

Then the developer asked two more things: should we add more exercises, and should we add program-design information (sets, reps, frequency)? The catalog had 20 exercises, no advanced exercises, no direct arm work, and little equipment variety. Adding data raised an ordering question, because the eval's answer keys (the expected results for each question) are written against the catalog. For example, "I only have dumbbells" expects every dumbbell exercise in the catalog, and "no equipment" forbids every exercise that needs equipment.

## Options considered
- **Data first, then the eval, then the filters.** Grow the catalog, then update and extend the eval against it, record a new baseline, then build the filters and compare. Pros: the answer keys are written once, for the catalog the filters will actually search; the baseline and the after-filter run use the same data, so the comparison is clean. Cons: the filters, the fix for the known weakness, wait two more stages; the old reviewed baseline can no longer be compared directly with anything after F1.
- **Eval first on the 20-exercise catalog, then add data.** Pros: the eval work starts at once, while the review is fresh. Cons: every key that depends on the catalog (equipment, muscle group, level questions) would have to be rewritten after the data grew, and the baseline recorded again; the coach would review the same questions twice.
- **Filters first, data and eval later.** Pros: the fastest route to fixing the known failures. Cons: nothing trustworthy to measure them with; the limit questions are only 3, so one flip moves the score 33–50%.
- **Program-design sources now, with the exercises.** Pros: all data work done at once. Cons: not needed for the equipment and population filters; they are what the Phase 2 programming agent needs, and the ingestion pipeline for papers already exists ([0022](0022-research-papers-europe-pmc-jats-xml-not-pdfs.md)).

## Decision
Data first, then the test, then the fix. F1 expands the catalog (about 20 → 40; Claude drafts, the coach reviews). F2 updates the answer keys for the new catalog, adds about 8–10 coach-written equipment and population questions, adds code checks for the four answer-level rules, and records a new baseline. F3–F6 build the filters (read limits from the question, equipment filter, population tags on passages) and re-run the eval. F7+ covers larger k, query rewriting, and search tuning. Program-design sources (Schoenfeld 2021, Pelland 2024, the coach's notes on NSCA *Essentials* chapters 18–19) come right before Phase 2.

Authoring for F1: Claude drafts, the coach reviews. The developer chose this over writing all exercises personally and over importing from wger (an open exercise database). All four gap areas were filled: arms, advanced lifts, equipment variety, and bodyweight plus speed.

## Evidence
F1 itself showed why keys must follow the data. On the same 31 reviewed questions, after the catalog grew from 20 to 42, semantic exercise recall fell from 0.91 to 0.76 (hit 0.94, MRR 0.75; hybrid recall 0.76; keyword 0.58). Search didn't get worse. The keys are out of date: the biceps question still expects the two rows that list biceps as a secondary muscle, while three new curls now correctly fill the top spots, so it scores 0. The saved results also show the opposite error: for "no equipment", `bench-dip` and `band-biceps-curl` were returned but aren't on the old forbidden list, so a wrong result passed. Stale keys undercount both hits and mistakes. See the [F1 build-log entry](../build-log.md#phase-1f-begins-f1-exercise-catalog-expanded-to-42).

## Tradeoffs
- The known limit failures stay in the system through F1 and F2.
- The reviewed baseline (exercise recall 0.91) is no longer comparable with later runs. The new F2 baseline replaces it; the old number stays in the log, labeled with its catalog size.
- AI-drafted exercises need the coach's time to review, and the original 20 are still unreviewed.
- A bigger catalog means more candidates competing for the top 5, which makes "list everything" questions harder (see [Recall ceiling from top-k](../concepts.md#recall-ceiling-from-top-k)).

## Revisit when
- The catalog needs to grow again after F2's baseline. Then update the affected keys deliberately and re-baseline, rather than comparing against a stale key.
- The filters (F3–F5) turn out to need data the catalog doesn't carry (for example population suitability on exercises), which would send us back to data before measuring.
- Phase 2 planning starts: pull program-design sources forward if the agent design needs them earlier.
