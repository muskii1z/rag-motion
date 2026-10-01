# 0055. Bodyweight counts only when the client says so, enforced in code
**Date:** 2026-10-01 · **Step:** Phase 2, step 2 fixes · **Status:** accepted

## Context
[0052](0052-agent-building-tools-refuse-until-profile-complete.md) made the building tools refuse until equipment is known. In the developer's next live run ("i am a beginner to the gym, i want a full exercise routine"), the agent again built a bodyweight-only program without asking about equipment. Re-reading the profile 3 times showed why: the profile reader (`extract_profile`, an LLM at temperature 0) guessed `['bodyweight']` in 1 of 3 reads. That made equipment "known", so the refusal let the agent build. The program passed 14 of 15 checks, repeated the same few exercises on all 4 days, and cost $0.0142 (about 10x a normal run). Developer: "it didn't ask me for equipment again... it should have asked."

## Options considered
- **Prompt fix only.** Tell the reader to record only equipment mentioned and never default to bodyweight. Pros: no code. Cons: prompt rules have a ceiling, and this guess happened in only 1 of 3 runs, so a few clean runs prove little.
- **Code guard only.** Pros: deterministic. Cons: the reader keeps guessing, and the guard has to undo it.
- **Both.** Prompt fix, plus in `agent.read_profile`: if equipment is exactly `['bodyweight']` and the client's own messages don't match `NO_EQUIPMENT` (no equipment, without equipment, bodyweight, body weight, no weights, nothing at home, don't have (any) equipment/weights, own body), reset equipment to `[]`, which counts as missing.
- **Assume bodyweight when unknown.** Rejected in 0052: silently wrong for most clients.

## Decision
Both. Bodyweight is used only when the client's own words say so; otherwise equipment stays unknown and the agent must ask. After the fix, 6 of 6 reads reported equipment missing, and the full agent asked for equipment in 2 of 2 runs ($0.0002 each).

## Tradeoffs
- A client who means "no equipment" but phrases it in a way `NO_EQUIPMENT` doesn't cover gets asked once more.
- The guard covers one specific guess: exactly `['bodyweight']`. Other guesses (for example "dumbbells" from "gym") aren't caught.
- `NO_EQUIPMENT` matches anywhere in the client's messages, so "I don't want bodyweight exercises" would let a guessed bodyweight through (untested).

## Revisit when
- Test clients show the reader guessing other equipment.
- Clients who said "no equipment" in their own words get asked again.
- The profile reader moves to a model that doesn't guess in repeated reads.
