# 0014. Embedded text: name + description + labeled facts, no instructions
**Date:** 2026-09-24 · **Step:** 8 · **Status:** accepted

## Context
Before storing a vector for each exercise, we had to decide exactly which text goes into the embedding model. An embedding (a list of 1,024 numbers describing the meaning of a text) only knows what is in the text it was given. So this choice decides what a search can match on. Each exercise row holds a name, a description, step-by-step instructions, and metadata columns (movement pattern, body region, laterality, primary muscles, equipment, difficulty). See [What text to embed (document representation)](../concepts.md#what-text-to-embed-document-representation).

## Options considered
- **(a) Description only.** Carries the meaning of the exercise. But a question like "beginner dumbbell exercises" has nothing to match on, because difficulty and equipment aren't in the text.
- **(b) Everything, including instructions.** Nothing left out. But step-by-step cues describe how to move, not what the exercise is, so they add noise that could blur the meaning.
- **(c) Name + description + key facts as short labels, no instructions.** The name and description carry meaning; labeled lines ("Movement pattern: pull. Body region: upper. ..." "Equipment: band." "Difficulty: beginner.") give questions about equipment, level, or muscles something to match. Instructions are left out.

## Decision
Option (c). It is defined in one place, `exercise_to_text(ex)` in `src/ragmotion/embeddings.py`, and every stored vector is built from it. Its docstring says that editing it changes every vector, so re-embed after changes (`uv run python scripts/embed_exercises.py --all`). Example output for band-pull-apart:

```
Band Pull-Apart
A light horizontal pulling exercise, stretching a resistance band across the chest with straight arms. It targets the rear shoulders and upper back and is often used in warm-ups and to balance out pressing volume.
Movement pattern: pull. Body region: upper. Laterality: bilateral.
Primary muscles: rear deltoids, rhomboids, middle trapezius.
Equipment: band.
Difficulty: beginner.
```

## Tradeoffs
- The labels pull exercises with the same equipment or body region closer together, not only exercises with the same movement. Seen at Step 8: Push-Up's nearest neighbor was Inverted Row (0.85), a pull, tied with Dumbbell Overhead Press (0.85). Not wrong, but a push and a pull sitting that close is partly the labels' doing.
- Labels in the text are not filters. "Difficulty: beginner" in the text makes beginner exercises rank a bit higher for "beginner" questions; it does not guarantee that only beginner exercises come back. Hard rules still belong in SQL `WHERE` clauses ([Metadata filtering](../concepts.md#metadata-filtering)).
- Any change to this function means re-embedding the whole catalog. Cheap at 20 exercises (one batch call), not free at scale.

## Revisit when
Step 15 (evaluation). Compare variants on the same eval questions, at least description-only vs description-plus-labels, and keep whichever retrieves the expected exercises more often. Also revisit if hand checks at Step 9 show equipment or region labels overpowering movement meaning.

See [Step 8](../build-log.md#step-8-embed-all-exercises-store-vectors-compare-them-by-hand).
