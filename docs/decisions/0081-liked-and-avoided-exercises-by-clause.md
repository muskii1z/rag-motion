# 0081. Liked and avoided exercises are read by clause; avoided ones leave the options where an alternative remains
**Date:** 2026-10-02 · **Step:** Phase 2 follow-up (gym detection, likes vs dislikes) · **Status:** accepted (extends [0078](0078-exercises-the-client-names-found-by-code.md); coach may revise the deadlift rule)

## Context
`mentioned_exercises` ([0078](0078-exercises-the-client-names-found-by-code.md)) found catalog exercises the client named, but not whether they liked them. A scribe probe showed "I hate deadlifts" returned two deadlifts, which the prompt then presented as exercises the client mentioned and should use. It also matched "squats" to Bodyweight Squat.

## Options considered
- **Ask the LLM profile reader for likes and dislikes.** Pros: understands phrasing. Cons: another field it can drop or invent, and it has to map free text to catalog slugs.
- **Look for dislike words in the whole sentence.** Pros: simple. Cons: tried first and failed: "I like push-ups and I don't want burpees" marked push-ups as disliked, because the "don't" in the second half applied to the whole sentence.
- **Look for dislike words in each clause.** Pros: a "not" usually applies only to its own part of the sentence (negation scope), and splitting into clauses approximates that cheaply. Cons: still a word list; unusual phrasings and abbreviations are missed.

For a dislike named by a general word ("I hate deadlifts"):
- **Avoid only an exercise with exactly that name.** Cons: nothing in the catalog is called just "deadlift" or "lunge", so "I can't do lunges" found nothing.
- **Avoid every exercise whose name ends in that word.** Pros: conservative. Cons: "I hate deadlifts" also removes Romanian deadlifts, which some clients would happily do.

## Decision
- `mentioned_exercises` returns `(liked, avoided)`. The text is split into clauses on `. ! ? ;`, "but", and "and I / and I'm". A `DISLIKE` pattern (hate, dislike, don't/do not/doesn't like/want/enjoy/do, can't, cannot, avoid, no more, not a fan, never again, skip) marks a clause as a dislike.
- Liked: specific multi-word names (equipment word removed, e.g. "back squat", "hip thrust") in clauses without a dislike word. A general word alone ("squats") is never counted as liked.
- Avoided: specific names in dislike clauses, plus a general word ("deadlifts", "lunges") covers every exercise whose name ends in it, unless the clause named a more specific one ("I hate Romanian deadlifts" → only the Romanian deadlift).
- The agent's profile note lists `exercises_the_client_likes` and `exercises_the_client_wants_to_avoid`. `build_skeleton(..., avoid=...)` removes avoided exercises from each slot's options **only where another option remains**, so a slot is never left empty. The prompt says never to use avoided exercises.
- "I hate deadlifts" avoids all four deadlift variations, including RDLs. The developer chose the conservative reading; alternatives such as the hip thrust remain.

Eval: new client `hates-deadlifts` ("Full gym, intermediate, get stronger, 3 days a week. I hate deadlifts."), expected to include none of the four deadlifts: 3/3 runs passed.

## Tradeoffs
- A word list, not understanding. Scribe probes after the commit: "I don't like RDLs" finds nothing (abbreviations aren't matched); "I hate Romanian deadlifts" avoids Dumbbell Romanian Deadlift but not Single-Leg Romanian Deadlift (its name doesn't match the phrase as written); "I like planks" and "I love squats" find no liked exercise.
- "Removed where an alternative remains" means a disliked exercise can still appear if it's the only option for a slot. Then only the prompt stands between the client and that exercise.
- "Never done deadlifts" is correctly not a dislike, but a client who is merely nervous about deadlifts gets them.

## Revisit when
- The coach decides "I hate deadlifts" shouldn't remove RDLs.
- A client gets an exercise they said they dislike, or misses one they asked for.
- Clients use abbreviations or slang for exercises (the Phase 1F slang dictionary, `src/ragmotion/rewrite.py`, could be reused).
