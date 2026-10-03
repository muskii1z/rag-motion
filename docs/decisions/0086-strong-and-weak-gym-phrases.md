# 0086. Strong gym phrases always count; weak ones are cancelled by at-home wording
**Date:** 2026-10-03 · **Step:** Phase 2 follow-up 2 (coach answers applied) · **Status:** accepted (amends [0080](0080-gym-only-from-clear-access-phrases.md))

## Context
[0080](0080-gym-only-from-clear-access-phrases.md) narrowed gym detection to clear access phrases and let any at-home wording ("at home", "home gym", "gym at home") cancel a match. Scribe probes after that commit found two misses:
- "I work out at home but have gym access" → no gym. "Gym access" is about as clear as it gets, but "at home" cancelled it.
- "I have a gym at work" → no gym. The phrase wasn't in the list.

The underlying issue: some phrases are decisive on their own ("gym membership"), while others are only a hint ("at the gym" could be past, hypothetical, or someone else's gym). One cancel rule treated both the same.

## Options considered
- **Keep 0080 as is.** Pros: fewest wrong matches. Cons: misses clients who clearly have gym access but also train at home.
- **Drop the at-home cancel.** Pros: catches both misses. Cons: brings back the original bug: "beginner to the gym, I train at home with dumbbells" would get barbell and machine exercises.
- **Split into strong and weak phrases.** Strong phrases always count; weak phrases count only when there is no at-home wording. Pros: both misses fixed, the home-trainer cases still correct. Cons: two lists to maintain, and strong phrases have no negation check.

## Decision
`mentions_gym(text)` in `src/ragmotion/agent.py`, used by the `read_profile` backstop (the code rule that adds "gym", meaning all equipment, to the profile):
- `STRONG_GYM`, always counts: "full/commercial/public/local/work/office/university/school/hotel gym", "gym access", "gym membership", "access to a/the gym", "gym at work / the office / my work / my job / my office / school / uni".
- `WEAK_GYM`, counts only if `AT_HOME` doesn't match: "go/going/train/training/lift/lifting/work out/working out to/at/in a/the/my gym", "at/in a/the gym" (not followed by "at home").
- `AT_HOME` is unchanged: "home gym", "home-gym", "gym at home", "at/from home".

Tests (parametrized): "I work out at home but have gym access", "I have a gym at work", and "I use my work gym" → gym; "I quit the gym", "Home gym in my garage", "beginner to the gym, I train at home with dumbbells" → not gym (as confirmed in the brief). Eval (`programs-20261003-113258`): `home-dumbbells-not-gym` still 3/3 with no barbell, machine, or cable exercises; 42/42 expectations overall.

## Tradeoffs
Strong phrases win even when the sentence says the access is gone. Scribe probes after the commit (not in the brief, not in the tests or the eval) all return **gym**:
- "I cancelled my gym membership"
- "I used to have gym access"
- "I train at home, no gym access"
- "My work gym closed, so I train at home now"

Each of these would give a home trainer barbell, machine, and cable exercises: the more costly error that [0080](0080-gym-only-from-clear-access-phrases.md) set out to avoid. "No gym access" is the most likely of these to appear in real use.

## Revisit when
- A client with no gym gets gym equipment (any of the probe phrasings above, or similar).
- The word lists keep growing. Then the LLM profile reader may need a dedicated "has gym access: yes / no / unclear" field, with the regex as a backup.

## Update 2026-10-03 (12d200b)

The negation gap above is fixed. `mentions_gym` splits the client text into clauses and ignores any clause containing a negation or past-tense word (`GYM_GONE`: no, not, without, don't, cancelled, quit, used to, lost, closed, shut, ended, gave up, former, ex). "I train at home, no gym access", "I cancelled my gym membership", "I used to have gym access" and "My work gym closed, so I train at home now" now read as no gym; "I have gym access but I also train at home" still reads as gym. 173 tests pass; program eval (1 run) 14/14 expectations, 12/12 programs pass.
