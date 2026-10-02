# 0052. Building tools refuse until goal, days, equipment, and level are known
**Date:** 2026-10-01 · **Step:** Phase 2, step 2 · **Status:** accepted

## Context
In the developer's live test, the client said "I am a beginner, give me an exercise routine". The agent asked for goal and days but not equipment, although the prompt said to ask for everything missing. Unknown equipment left the profile's equipment empty, which the code read as bodyweight only. `find_exercises` correctly returned almost nothing (squat 0, pull 0, carry 0), and the agent then returned an empty reply.

## Options considered
- **Stronger prompt wording.** Pros: no code. Cons: the prompt already said to ask for everything missing.
- **Treat unknown equipment as "assume bodyweight".** Pros: the agent can always build. Cons: silently wrong for most clients, which is what happened.
- **Refuse in code.** `find_exercises`, `search_sources`, and `submit_program` return "Not enough information yet. Ask the client about: ..." until goal, sessions per week, equipment, and experience level are all known.

## Decision
Refuse in code. The refusal names the missing fields, so the agent's natural next move is to ask the client. Uses `missing_for_program()` from step 1.

## Tradeoffs
- A client who won't or can't give one of the four details gets no program. There's no "build with what you have" path.
- One extra round trip when the agent tries a tool too early.
- The agent can still ask the question badly (for example in plain text instead of `ask_user`); the refusal only blocks building.

## Revisit when
- Test clients get stuck in a loop of refusals without being asked the right question.
- Sensible defaults exist for a field (for example, "no equipment mentioned, client says they train at home") that the coach agrees with.

## Update 2026-10-01 (step 2 fixes): bypassed by the profile reader's guess
In the developer's next live run the refusal didn't fire: the profile reader guessed `['bodyweight']` for "beginner to the gym" (1 of 3 reads), so equipment counted as known. The refusal is only as good as the profile it reads. Fixed in [0055](0055-bodyweight-only-when-the-client-says-so.md): bodyweight counts only when the client says so.

## Update 2026-10-02 (Phase 2, P3): a gym counts as known equipment
"Full gym" was stored as unmapped equipment, and the missing-details check only looked at the equipment list, so the agent asked for equipment a gym member had already given. A shared `has_gym()` now decides for both functions, with a backstop when the reader drops "gym", and a nudge when the agent asks with nothing missing. See [0067](0067-agent-asks-only-when-something-is-missing.md).
