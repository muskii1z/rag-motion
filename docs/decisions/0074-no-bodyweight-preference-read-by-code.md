# 0074. A "no bodyweight" preference is read by code
**Date:** 2026-10-02 · **Step:** Phase 2 structure fix (after P4) · **Status:** accepted

## Context
The P4 eval client `no-bodyweight-please` says "I don't want bodyweight exercises." In P4 (before the skeleton), one of its 3 runs included a Front Plank and failed "no bodyweight-only exercises"; another failed the core/carry check instead. After the skeleton, it missed 3/3: every program passed every check but included bodyweight-only core and push options. The profile has no field for exercise preferences.

## Options considered
- **A prompt rule.** Pros: no code. Cons: this project has seen prompt rules skipped many times; the agent already had the client's words and didn't act on them.
- **A new field read by the profile AI.** Pros: catches more phrasings. Cons: one more thing the reader can get wrong, and a schema change for one preference.
- **A regex on the client's messages, applied while building the skeleton.** Pros: deterministic, testable, removes the options before the model sees them. Cons: only catches phrasings the pattern knows.

## Decision
`AVOID_BODYWEIGHT` in `src/ragmotion/agent.py` matches "no", "don't want", "not", "without", "avoid", or "hate" followed within 30 characters by "bodyweight" or "body weight". When it matches, `build_skeleton(profile, avoid_bodyweight=True)` drops bodyweight-only options wherever another option exists. A slot with only bodyweight options becomes a carry if a loaded carry exists (a dumbbell client's core options are all bodyweight). With no equipment, bodyweight options stay.

## Tradeoffs
- Phrasings outside the pattern are missed (for example "only weights, please").
- A plank now counts as a bodyweight exercise the client wanted to avoid. The coach hasn't confirmed that reading.
- Core work is replaced by carries for these clients; a carry trains the trunk differently from a plank.

Result: `no-bodyweight-please` 0/3 → 3/3 (final run: core slots filled with Farmer Carry and Suitcase Carry).

## Revisit when
- More preferences show up (favorite exercises, disliked exercises). The `loves-back-squats` client's favorites were ignored in 9 of 9 runs; a general "preferences" field may be worth it then.
- The coach says planks should be allowed for "no bodyweight" clients.
