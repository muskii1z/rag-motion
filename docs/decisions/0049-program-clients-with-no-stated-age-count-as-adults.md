# 0049. Program clients with no stated age count as adults
**Date:** 2026-10-01 · **Step:** Phase 2, step 1 · **Status:** accepted

## Context
`search_sources` filters passages by the client's age group. When the client gave no age, `population()` returned nothing, so no filter was applied. In run 2 the program for an adult cited `notes-nsca-youth-ltad-1` (youth notes): the same [population mixing](../concepts.md#population-mixing-context-bleed-across-populations) seen in Step 13.

## Options considered
- **No filter when age is unknown (before).** Pros: nothing is hidden. Cons: youth and older-adult passages can reach an adult's program, as happened.
- **Treat unknown age as adults.** Pros: matches the most common client; wrong-group passages stop. Cons: an unstated teenager or older adult gets adult sources.

Not discussed in this step: adding age to the fields the agent must ask for.

## Decision
For programs, an unknown age counts as adults (`population()` returns "adults"). Covered by a test.

## Tradeoffs
- A youth or older client who doesn't state their age gets adult passages. The level cap and the no-jumps rule for 65+ also apply only when the age is known.

## Revisit when
- The step 4 test set includes youth or older clients who don't give their age.
- The coach wants age to be a required intake question.
