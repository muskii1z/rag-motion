# 0060. Machine and cable equipment, and push/pull direction as its own column
**Date:** 2026-10-01 · **Step:** Phase 2 quality pass, Q2 · **Status:** accepted

## Context
Real gym programs use machines (chest press, leg press) and cable stations (lat pulldown, seated row), but the equipment vocabulary (the fixed list of allowed equipment values) had no word for either. And [0058](0058-push-and-pull-get-horizontal-vertical-labels.md) decided to label push and pull exercises horizontal or vertical, but left open where the label would live. One coach call also raised a smaller question: the box squat can be loaded, so should its equipment list say so?

## Options considered
- **Direction as new movement-pattern values** (for example "horizontal-push"). Pros: no new column. Cons: every filter, prompt, eval key and check that says "push" or "pull" would have to change.
- **Direction as a separate column, `exercise.direction`.** Pros: "push" and "pull" keep their meaning everywhere; the rule can add direction only where it matters. Cons: one more field to keep consistent; every query that builds an `Exercise` must select it.
- **Box squat equipment `['box', 'dumbbell']`.** Pros: the filter knows it can be loaded. Cons: with the "only needs what I own" filter (`<@`), a client with only a box would lose it.
- **Box squat equipment `['box']`, loading in the text.** Pros: box-only clients keep it. Cons: the loading option lives in the description and instructions, where filters can't see it.

The brief didn't record why the column was chosen over new pattern values; the pros and cons above are what the build shows.

## Decision
- Equipment gains `machine` and `cable` (schema CHECK, `Equipment` Literal, profile and limits prompts, the agent's equipment question).
- `exercise.direction` is a nullable column with CHECK `('horizontal','vertical')`. A Pydantic `model_validator` on `Exercise` requires it for push and pull and forbids it for everything else.
- The seed script sets direction with its own update, so changing it never clears an embedding (direction isn't part of the embedded text).
- Box squat stays `['box']`; the coach's "loadable" goes into the description and instructions (hold a dumbbell or kettlebell at the chest).

## Tradeoffs
- The vocabulary now lives in three places that must agree: schema CHECK, `models.py`, and the prompts that name equipment.
- Every query that loads exercises must select `direction`. Three didn't at first (`SEARCH_SQL`, `KEYWORD_EXERCISE_SQL`, `embed_exercises.py`); the validator caught it as a crash.
- Squat, lunge and hinge still have no direction split, so near-duplicates there are judged by pattern alone.
- "Machine" is one value for many different machines. A client with only a leg press would be offered a chest press machine too.

## Revisit when
- The coach disagrees with a direction label (bench dip's vertical label is still unconfirmed).
- Clients with partial machine access show up, and "machine" is too coarse.
- A loaded-only exercise needs to be filtered by the weight it uses.
