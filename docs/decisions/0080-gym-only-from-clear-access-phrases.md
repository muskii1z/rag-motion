# 0080. A gym counts only from clear access phrases, and at-home wording cancels it
**Date:** 2026-10-02 · **Step:** Phase 2 follow-up (gym detection, likes vs dislikes) · **Status:** accepted (narrows [0077](0077-a-gym-mention-always-means-all-equipment.md))

## Context
[0077](0077-a-gym-mention-always-means-all-equipment.md) made any mention of "gym" (except the exact words "home gym") mean the client has all equipment. A scribe probe after that commit showed the pattern also matched "I quit the gym", "beginner to the gym, I train at home with dumbbells", "gym at home", and "home-gym setup". A home trainer with dumbbells who said they were new to the gym would have been given barbell, machine, and cable exercises they can't do.

A regex (regular expression: a text pattern code searches for) can be broad or narrow. Broad catches more real gym clients but also wrong ones (false positives). Narrow makes fewer wrong calls but misses some phrasings (false negatives).

## Options considered
- **Keep the broad rule.** Pros: never misses a gym client. Cons: wrong equipment for home trainers who mention a gym in passing; the program is then built around exercises they can't do.
- **Let the LLM profile reader decide alone.** Pros: understands context. Cons: it dropped "full gym" in P3 and turned "full gym" into barbell + machine in 3 of 3 reads ([0077](0077-a-gym-mention-always-means-all-equipment.md)).
- **Narrow the rule to clear access phrases, with an at-home rule that cancels it.** Pros: no wrong equipment for the phrasings tested. Cons: some real gym phrasings won't match, and then the reader's own list (or a question to the client) decides.

## Decision
`GYM` in `src/ragmotion/agent.py` now matches only clear access phrases: "full/commercial/public/local gym", "gym access/membership", "access to a/the gym", "go/train/lift/work out at/to/in the gym", and "at/in the gym" (not followed by "at home"). A new `AT_HOME` pattern ("home gym", "home-gym", "gym at home", "at/from home") cancels it. `read_profile` adds "gym" only if `GYM` matches and `AT_HOME` doesn't. Tested with 8 gym phrasings (parametrized test) and a new eval client, `home-dumbbells-not-gym` ("I'm new to the gym scene but I train at home with dumbbells"), which must get no barbell, machine, or cable exercises: 3/3 runs passed.

## Tradeoffs
The cost of a miss is smaller than the cost of a wrong match: a missed gym phrase falls back to the reader, and if equipment is still unknown the agent asks; a wrong match builds a program the client can't do. Gaps found by scribe probes (not in the eval):
- "I work out at home but have gym access" → no gym, because any at-home wording cancels the match.
- "I have a gym at work" → no match.
- "I quit the gym" and "beginner to the gym, I train at home with dumbbells" → correctly no gym now.

## Revisit when
- A real or eval client with gym access gets asked for equipment or gets a home-equipment program.
- Clients often describe both home and gym training (then the rule needs to decide which one the program is for, probably by asking).
