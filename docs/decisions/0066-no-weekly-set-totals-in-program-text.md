# 0066. No weekly-set totals in the program text; code shows the real counts
**Date:** 2026-10-02 · **Step:** Phase 2, P3 · **Status:** accepted

## Context
Since Q1 ([0057](0057-program-quality-checks-weekly-sets-patterns-day-labels.md)), code counts weekly sets per muscle group and the prompt tells the agent not to state totals. In the first live browser test the rationale said "chest: 6, back: 6, shoulders: 9, quads: 9, glutes/hamstrings: 15". Code counted shoulders 12 and glutes/hamstrings 21. The page now shows code's counts as bars, so the program would have shown two different numbers for the same thing.

## Options considered
- **Stronger prompt wording.** Pros: free. Cons: the existing instruction was already ignored.
- **Strip the numbers from the text after the fact.** Pros: the client never sees them. Cons: editing model text can leave broken sentences; the agent never learns.
- **A checker rule: reject per-muscle totals in the text.** Pros: same path as every other check, with an exact fix sent back; consistent with "count, don't trust". Cons: a regex (text pattern) can miss phrasings or catch legitimate ones.

## Decision
A checker rule: "no weekly-set totals stated in the text (code shows the real ones)". `VOLUME_CLAIM` in `src/ragmotion/program.py` matches a muscle-group name followed by a number (e.g. "glutes/hamstrings: 15") or "N–M sets per muscle group". Citing research ("at least 6 weekly sets per muscle") is still allowed. The test is built from the live text.

## Tradeoffs
- Phrasings the pattern doesn't know can still slip through.
- A rejection costs another submission (time and money).

## Revisit when
- A stated total gets past the pattern, or a legitimate research citation is rejected.
