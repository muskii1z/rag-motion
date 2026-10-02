# 0077. A gym mention always means all equipment (except "home gym")
**Date:** 2026-10-02 · **Step:** Phase 2 follow-up (full-gym detection) · **Status:** superseded by [0080](0080-gym-only-from-clear-access-phrases.md)

## Context
The profile reader (an LLM call, `extract_profile`) turns the conversation into a client profile, including equipment. For "I love back squats and hip thrusts. Intermediate, build muscle, 4 days a week, full gym." it returned equipment `['barbell', 'machine']` and unmapped equipment `[]` in 3 of 3 reads: it dropped "full gym" and guessed equipment from the exercise names. The code backstop from [0067](0067-agent-asks-only-when-something-is-missing.md) only added "gym" when the reader had recorded **no** equipment, so it didn't fire. The client got no back squat (no rack), 3-exercise upper days, and a suggestion to buy a pull-up bar. Equipment decides every exercise option in the skeleton, so one wrong reading changes the whole program.

## Options considered
- **Prompt fix only.** Tell the reader that "full gym" means a gym and not to infer equipment from exercise names. Pros: no new code. Cons: the reader had already dropped "full gym" once before (P3) despite earlier prompt work; a fact this important shouldn't depend on the model noticing.
- **Backstop only when the reader returned nothing** (the old rule). Pros: the reader's list wins when it has one. Cons: misses exactly this case, a partial list.
- **Backstop whenever a gym is mentioned, plus the prompt fix.** Pros: deterministic (same input, same result) for the fact with the biggest effect on the program. Cons: a word rule can't tell "full gym" from other uses of "gym".

## Decision
Both layers. In `read_profile`, if the client's messages match the `GYM` regex (`(?<!home )\bgym\b`), "gym" is added to `unmapped_equipment` even if the reader listed some equipment; `has_gym()` / `owned_equipment()` then treat the client as having all equipment. "Home gym" is excluded. The reader's prompt now maps "full gym", "gym access", and "I train at a gym" to "full gym" and says never to infer equipment from exercise names.

## Tradeoffs
- Any other mention of "gym" now counts as owning a full gym. A scribe probe after the commit: the regex matches "beginner to the gym, I train at home with dumbbells", "I quit the gym", "gym at home", "home-gym setup", and "Home  gym" (two spaces). Such a client would get barbell and machine exercises they can't do. Not covered by any eval client.
- The reader's own equipment list is ignored whenever a gym is mentioned.

## Revisit when
- A client who trains at home but mentions "the gym" gets gym-only exercises (live use, or an eval client added for that phrasing).
- The reader reliably reports "full gym" on its own across repeated reads, so the backstop could narrow again.

## Update 2026-10-02 (superseded)
The tradeoff above happened as predicted in the scribe probe, so the rule was narrowed in [0080](0080-gym-only-from-clear-access-phrases.md): only clear access phrases ("full gym", "gym membership", "I train at the gym", ...) count, and any at-home wording ("home gym", "at home") cancels them. The backstop itself stays: when one of those phrases matches, "gym" is still added even if the reader listed some equipment.
