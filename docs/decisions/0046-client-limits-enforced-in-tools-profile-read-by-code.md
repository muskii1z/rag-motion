# 0046. Client limits enforced inside the tools; the profile is read by code, not the agent
**Date:** 2026-10-01 · **Step:** Phase 2, step 1 · **Status:** accepted

## Context
The program agent needs to respect the client's equipment, level, and age. Phase 1F showed that prompt rules alone let forbidden items through (5 of 13 limit questions before the filters) and that filters in code fixed it ([0026](0026-equipment-prefilter-from-llm-read-limits.md), [0027](0027-population-tags-from-structure-keep-general-filter.md)). An agent adds a new question: who decides what the client's limits are, and where are they applied?

## Options considered
- **Tell the agent the limits in the prompt and let it pick from the full catalog.** Pros: simple. Cons: the same prompt-rule ceiling as Phase 1F; the agent could pick a barbell exercise for a dumbbell-only client.
- **Let the agent read the profile and pass limits as tool arguments.** Pros: one fewer LLM call. Cons: the agent could pass the wrong limits, or drop them.
- **Code reads the profile; tools filter by it.** `read_profile()` runs `extract_profile` (Step 6) on the whole conversation; `owned_equipment`, `max_level`, `population`, and `banned_patterns` are computed in code; `find_exercises` and `search_sources` filter by them. Pros: whatever the agent asks for, it only gets usable exercises and age-appropriate passages. Cons: an extra extraction call each turn; coach rules (no jumps for 65+, "full gym" = everything) are hard-coded.

## Decision
Code reads the profile from the conversation and computes the limits; the tools filter by them. The agent sees the profile and what's missing, but never edits it. A pregnancy mention is also handled in code: no program, a referral to a health professional, and an offer of the Guidelines' pregnancy section.

## Tradeoffs
- An extra `extract_profile` call per turn (cost and time).
- The profile is still read by an LLM, so a wrong or manipulated reading changes the filters (Step 6 showed extraction can be manipulated).
- Coach rules live in code (`max_level`, `banned_patterns`), so changing them means a code change, not a prompt edit.
- "Full gym" is detected by the word "gym" in unmapped equipment.

## Revisit when
- The step 4 test set shows profiles read wrongly often enough to matter.
- The coach's rules grow beyond a few lines: move them into data (a rules table or config).
