# 0073. Code builds the program skeleton; the agent fills the slots
**Date:** 2026-10-02 · **Step:** Phase 2 structure fix (after P4) · **Status:** accepted

## Context
After P4, about 1 in 4 programs (5/20 in the second run) still failed a structural rule after 3 submissions: one exercise per pattern per day, every main pattern on 2+ days, core or carry once a week, enough weekly sets per muscle group. The model designed the whole week at once while juggling about 18 rules. The developer: "We can't go public with this. It's not complete."

## Options considered
- **More retries.** Pros: no design change. Cons: P4 already showed programs stuck on the same failure for 3 tries; more tries cost more time and money and still don't guarantee a pass.
- **Better fix text.** Pros: worked before ([Actionable feedback](../concepts.md#actionable-feedback-exact-fix-instructions)). Cons: already applied to every check; the failures that remained were the model re-breaking structure while fixing something else.
- **Looser rules.** Pros: more programs pass. Cons: the rules are the coach's; loosening them lets real design problems through.
- **Code builds the week's skeleton, the agent fills the slots.** Pros: structure is math, which code gets right every time; the model keeps the judgment work (exercise choice, dosage, explanation). Cons: the week's layout is fixed per day count, so the model can no longer design an unusual split.

## Decision
Code lays out the days and slots for the client's day count (`LAYOUTS` in `src/ragmotion/program.py`, from the coach-reviewed program-design notes), lists the usable exercises for each slot, and handles gaps with fallbacks (squat ↔ lunge, v-push ↔ h-push, v-pull ↔ h-pull, carry ↔ core, never doubling a pattern on one day) or by switching small 4–6-day splits to the full-body A/B/C rotation. The agent calls `get_plan_skeleton` (replacing `find_exercises`) and submits one pick plus sets, reps, and rest per slot. Code assembles the program (days, names, order) and rejects bad picks with the allowed options; then the existing checker runs.

## Tradeoffs
- The model can't propose a different split (for example push/pull/legs). Every week shape comes from six fixed layouts.
- The layouts encode coaching choices in code, so the coach has to review them; they aren't reviewed yet.
- The checker still runs on every program, so structure is now enforced twice (by construction and by check). That costs nothing at runtime and catches skeleton bugs, which the all-combinations test showed it can.
- Passing every check no longer says much about whether the program fits the client: in the eval, a "full gym" client who loves back squats got neither back squats nor hip thrusts in 9 of 9 runs and still passed.

Result: programs passing every check 15/20 (2 runs) → 30/30 (3 runs, every run of three); expectations 19/24 → 36/36 after two follow-up fixes; median 11.5 s → 8.4 s; total cost $0.20 (24 runs) → $0.159 (36 runs).

## Revisit when
- The coach rejects or changes a layout.
- Clients need splits the six layouts can't express (for example a sport-specific week or push/pull/legs).
- The coach's review finds programs that pass every check but don't fit the client (the back-squat case already points this way).
