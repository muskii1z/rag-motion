# 0029. Exercise k stays at 5 for every question (measured against 10 and 15; no adaptive k)
**Date:** 2026-09-28 · **Step:** Phase 1F, F7a · **Status:** accepted

## Context
k is how many search results the answer model sees. Exercise k has been 5 since Step 9, a common default that was never tested. The developer asked whether a larger k would be better for every search. Two pressures pull in opposite directions:
- **List questions** ("no equipment", "dumbbells only", "beginner adult") have more right answers than 5 slots. "No equipment" has 11 expected exercises, so top 5 caps recall well below 1.0 ([Recall ceiling from top-k](../concepts.md#recall-ceiling-from-top-k)).
- **Focused questions** (one exercise, a research finding) may get worse, because the model gets more loosely related exercises it could wrongly include.

Cost was not a factor: exercise entries are short and the catalog has 42.

F7a measured it instead of guessing ([build log](../build-log.md#phase-1f-f7a-experiment-with-5-10-and-15-exercises-per-question)). Retrieval with filters, exercise recall: 0.83 at k = 5, 0.94 at k = 10, 0.99 at k = 15; one question (`constraint-beginner-home`) retrieved forbidden advanced bodyweight exercises at k = 10 and 15. Answers, filters on, 3 runs each at k = 5 vs 10: exercise completeness 0.80 → 0.92; answers citing only keyed exercises 87% → 78%; no forbidden citations 39/39 both; the extras concentrated on focused and research questions (`jargon-bss`, `research-sprint-acceleration`). The beginner-adult "group by muscle group" rule failed on all runs at both k values, because the answer prompt never states it, so a bigger k was not the fix for that.

## Options considered
- **Keep k = 5 for every question.** Pros: simplest; no new moving parts; focused and research answers stay cleaner (87% cite only keyed exercises). Cons: list questions stay capped at 5 exercises (completeness 0.80).
- **k = 10 for every question.** Pros: simple; list answers more complete (0.80 → 0.92). Cons: more unasked-for exercises on focused and research questions (87% → 78% clean); one question starts retrieving forbidden exercises, because exercises aren't filtered by level.
- **Adaptive k: 10 only for list questions.** Read a `wants_list` flag from the question on the existing intake form (`extract_limits`). Pros: list questions get the gain; focused questions keep k = 5. Cons: one more field for the small model to read correctly (a misread picks the wrong k) and one more thing to test. This was the recommendation given to the developer.

## Decision
Exercise k stays at 5 for every question. No adaptive k. The developer: "I think we should just do 5." The reason: it is simpler, and the gain in list completeness (0.80 → 0.92) wasn't worth the extra unasked-for exercises on focused and research questions (87% → 78% clean). The `--k` option in `evals/run_retrieval_eval.py` and `--k-exercises` in `evals/run_answer_eval.py` stay, for future tests.

## Tradeoffs
List questions (for example "exercises that need no equipment", or the beginner-adult question whose rule is "group by muscle group") stay limited to 5 exercises, so they can never name everything the key expects. The recommended adaptive-k option was not taken.

## Revisit when
- Users or the coach say list answers are too short.
- The coach reviews the extras list and many of them turn out to be good choices that belong in the acceptable lists. Then the precision cost of k = 10 is smaller than 87% → 78% suggests.
- A level filter is added, which would remove the forbidden advanced exercises that k = 10 lets in for `constraint-beginner-home`.
- Reranking arrives (planned in F7+): retrieving more and letting a reranker pick the best 5 is another way to get breadth without more noise.
