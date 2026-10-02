# 0078. Exercises the client names are found by code and passed to the agent
**Date:** 2026-10-02 · **Step:** Phase 2 follow-up (full-gym detection) · **Status:** accepted

## Context
A client said "I love back squats and hip thrusts". Even once the equipment problem was found ([0077](0077-a-gym-mention-always-means-all-equipment.md)), nothing made sure the agent noticed the favorite lifts: they were only words in the conversation. A program that leaves out the lifts a client asked for passes every check but fails the client.

## Options considered
- **Leave it to the agent.** Pros: no code; the model can read the conversation. Cons: it depends on the model noticing, which is how the no-bodyweight preference was ignored before [0074](0074-no-bodyweight-preference-read-by-code.md).
- **Add a "favorite exercises" field to the profile reader.** Pros: the LLM understands phrasing like "I hate deadlifts". Cons: another field the reader can drop or invent; it has to map free text to catalog slugs.
- **Match catalog names in code and pass the list to the agent.** Pros: deterministic and cheap; returns real catalog slugs. Cons: only finds names close to the catalog's wording; can't tell likes from dislikes.
- **Force the named exercises into slots in code.** Pros: guaranteed. Cons: overrides coaching judgment (a named lift might not fit the client's level or the slot).

## Decision
Match in code, choose in the agent. `mentioned_exercises(conversation)` in `src/ragmotion/agent.py` strips equipment words (barbell, dumbbell, kettlebell, cable, machine, band, bodyweight, one-arm, single-arm) from each catalog name and looks for the rest in the client's messages, allowing a plural. The matches go into the profile note as `exercises_the_client_mentioned`, and the prompt says to use them where a slot offers them. The agent still chooses; the skeleton still decides what's allowed.

## Tradeoffs
- Names, not feelings: a scribe probe found "I hate deadlifts" returns `barbell-deadlift` and `kettlebell-deadlift`, which the prompt then presents as liked.
- Short leftovers match broadly: "back squats" also returns `bodyweight-squat` (its name minus "bodyweight" is "squat").
- Unusual wording is missed: "planks" doesn't match "Front Plank".
- A prompt nudge, not a guarantee. The eval checks it for one client ([0079](0079-eval-expectations-for-favorite-lifts-and-full-days.md)).

## Revisit when
- A client who names a disliked exercise gets it.
- A client's named lift is missing from their program even though a slot offered it.
- More clients name exercises in slang or abbreviations (the Phase 1F slang dictionary could be reused).
