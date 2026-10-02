# 0067. The agent asks only when something is missing: a shared gym rule, a reader backstop, one nudge
**Date:** 2026-10-02 · **Step:** Phase 2, P3 · **Status:** accepted

## Context
For "get stronger, 4 days, full gym, intermediate", the agent asked which equipment the client had. Three separate causes turned up in live tests:
1. The profile reader stored "full gym" as unmapped equipment. `owned_equipment` treated a gym as everything, but `missing_for_program` only looked at the equipment list, so it reported equipment as missing. Two functions disagreed about one fact.
2. In one traced read, the profile reader dropped "full gym" entirely (equipment `[]`, unmapped `[]`).
3. Even with nothing missing, the model sometimes chose to ask anyway.

## Options considered
- **Prompt changes only.** Pros: simple. Cons: doesn't fix causes 1 and 2, which are in code and in the reader.
- **Fix each layer.** One shared rule, a code backstop on the reader, and a nudge for the model. Pros: each cause handled where it happens. Cons: more code paths; the nudge is one more loop rule to test.
- **Forbid asking once nothing is missing.** Pros: never asks needlessly. Cons: blocks a legitimate clarifying question.

## Decision
- One shared `has_gym()` in `program.py`: equipment counts as known if listed or a gym is mentioned. Both functions use it.
- Backstop in `read_profile`: if the client's messages mention "gym" and nothing was recorded, `unmapped_equipment = ["gym"]`.
- If nothing is missing and the agent asks (through `ask_user` or plain text) before building, code sends one system nudge ("You have everything you need... Build the program now"). A second question goes through. Only real questions count as asking; empty replies don't (an existing empty-reply test caught this).

## Tradeoffs
- A word-based backstop: "gym" in an unrelated sense ("I quit the gym") could count as owning gym equipment. Not tested.
- One nudge costs an extra model call when it fires.
- A genuinely needed clarifying question costs one extra round before it reaches the client.

## Revisit when
- P4 or live use shows the agent building on a wrong "gym" reading, or still asking needlessly after the nudge.

## Update 2026-10-02 (Phase 2 follow-up): the "revisit when" signal happened
The P4 eval showed the agent building on a wrong gym reading: for "I love back squats ... full gym" the reader returned barbell + machine (3/3 reads), so this backstop, which only fired when nothing was recorded, didn't fire. The backstop now applies whenever a gym is mentioned, even with a partial list; see [0077](0077-a-gym-mention-always-means-all-equipment.md). The "I quit the gym" risk above is now wider: a scribe probe found the regex also matches "beginner to the gym, I train at home with dumbbells".
