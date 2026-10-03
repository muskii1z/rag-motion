# 0087. Disliked exercises: shorthand is expanded first, and a disliked name also removes its variants
**Date:** 2026-10-03 · **Step:** Phase 2 follow-up 2 (coach answers applied) · **Status:** accepted (extends [0081](0081-liked-and-avoided-exercises-by-clause.md))

## Context
[0081](0081-liked-and-avoided-exercises-by-clause.md) reads liked and avoided exercises from the client's words, clause by clause. Scribe probes after that commit found two gaps:
- "I don't like RDLs" → nothing avoided. RDL (Romanian deadlift) is gym shorthand, and the matcher only knew full catalog names.
- "I hate Romanian deadlifts" → avoided the Dumbbell Romanian Deadlift but **not** the Single-Leg Romanian Deadlift.

The coach also answered the open question from 0081 (2026-10-03): "I hate deadlifts" should remove all deadlifts, RDLs included ("include rdls"). That was already the behavior.

## Options considered
For shorthand:
- **A new list of abbreviations just for the program builder.** Cons: a second list that can drift from the first.
- **Reuse the glossary from Phase 1F query rewriting** (`GLOSSARY` in `src/ragmotion/rewrite.py`, which turns "RDL", "BSS", "KB" and similar into full names before a Q&A search). Pros: one list, already reviewed and tested for questions. Cons: the expansions were written for search, not for matching catalog names exactly.

For variants:
- **Avoid only the exact name.** Cons: the client who hates Romanian deadlifts still gets the single-leg one.
- **Avoid every exercise whose name contains the disliked name.** Pros: matches what a coach would assume. Cons: removes more than asked when one name is contained in another.

## Decision
- **Shorthand.** `_expand_shorthand(text)` in `src/ragmotion/agent.py` replaces glossary terms in the client's messages with their full names before matching. It's plural-aware: "RDLs" → "Romanian deadlifts". It uses whole-word, longest-first matching, the same approach as the Q&A rewrite.
- **Variants.** In a dislike clause, any catalog exercise whose name contains a disliked specific name is avoided too. "I hate Romanian deadlifts" → Dumbbell Romanian Deadlift and Single-Leg Romanian Deadlift.
- The 0081 rule stays: avoided exercises leave a slot's options only where another option remains.

Tests: "I don't like RDLs" and "I hate Romanian deadlifts" both avoid the two Romanian deadlifts; "I hate deadlifts" avoids all four deadlifts. Eval (`programs-20261003-113258`): `hates-deadlifts` 3/3 with no deadlift; 42/42 expectations overall.

## Tradeoffs
Over-removal is accepted on purpose: a client who loses one extra exercise still gets a full program, because alternatives always remain. Known leftovers (from the brief, confirmed by scribe probes):
- "I hate SL RDLs" also removes the regular Dumbbell RDL: the expansion "single-leg Romanian deadlifts" contains "Romanian deadlift", which matches the regular one.
- "I love BSS" marks both Bulgarian Split Squat and plain Split Squat as liked: the expansion contains "split squat".
- "I like DB bench" finds nothing: it expands to "dumbbell bench", and no catalog name matches that (the exercise is "Dumbbell Bench Press", matched as "bench press").
- "I like planks" and "I love squats" find no liked exercise. General words never count as likes, on purpose.

## Revisit when
- A client is denied an exercise they want because of an over-broad match, or the coach objects to one of the leftovers above.
- The glossary changes for Q&A in a way that breaks program matching (both now share one list).
