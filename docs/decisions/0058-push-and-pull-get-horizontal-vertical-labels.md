# 0058. Push and pull get horizontal/vertical labels; one per pattern and direction per day
**Date:** 2026-10-01 · **Step:** Phase 2 quality pass, Q1 (to be built in Q2) · **Status:** accepted

## Context
Q1's rule "one exercise per movement pattern per day" ([0057](0057-program-quality-checks-weekly-sets-patterns-day-labels.md)) was meant to stop near-duplicates such as glute bridge + hip thrust. In 3 replays it kept rejecting upper days with two pushes or two pulls. But a standard upper day has a horizontal press and a vertical press, and a row and a pulldown. The catalog only labels "push" and "pull", so the rule can't tell a good pair from a near-duplicate. Developer's choice, via a question.

## Options considered
- **Allow 2 push and 2 pull on upper days.** Pros: simple, fits upper/lower splits. Cons: doesn't stop near-duplicates (two bench-style presses).
- **Keep the strict rule.** Pros: no work. Cons: the agent fights every upper/lower split, burning retries.
- **Add horizontal/vertical labels to push and pull exercises.** Pros: the rule can say what a coach means. Cons: catalog work and coach review; the vocabulary grows.

## Decision
During Q2 (catalog work), label every push and pull exercise horizontal or vertical. The rule becomes one per pattern **and direction** per day: a bench press plus an overhead press is fine; two bench-style presses are not; glute bridge + hip thrust (both hinge) is still caught.

## Tradeoffs
- More data to keep consistent. Where the label lives (a new column, or new movement-pattern values) isn't designed yet; other controlled vocabulary in this project has to change in the schema's CHECK constraints and `models.py` together.
- Not built yet. Until Q2, upper/lower programs keep failing the one-per-pattern check.
- Squat, lunge, and hinge have no direction split, so near-duplicates there are still judged by pattern alone.

## Revisit when
- Q2 is built: check that replays of the full-gym conversation stop failing on double push/pull.
- The coach finds a direction label that doesn't fit an exercise.

## Update 2026-10-01 (Phase 2 quality pass, Q2): built
- Direction is a separate column, `exercise.direction`, required for push/pull by a model validator ([0060](0060-machine-and-cable-equipment-and-a-direction-column.md)). All 16 push/pull exercises in the 60-exercise catalog have one; bench dip's (vertical) awaits the coach.
- The check counts "horizontal push", "vertical pull" and so on separately. A test confirms flat + overhead press passes and two horizontal presses are flagged.
- Result: full-gym upper/lower replays went from 0/3 to 2/3 passing every check, then 4/6 after the narration fix ([0061](0061-narration-forces-a-submission.md)).
