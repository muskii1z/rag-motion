# 0040. prog-frequency answer key stays strict: research or Guidelines only
**Date:** 2026-10-01 · **Step:** Pre-Phase 2 · **Status:** accepted

## Context
`prog-frequency` ("How many days a week should I train each muscle group?") expects evidence from Pelland, Guidelines chapter 4, or page 8. In the first run the answer cited the draft program-design notes ([0039](0039-program-design-notes-from-general-practice-not-nsca.md)), which say at least 2 times a week per muscle. Citations and coverage passed, but "used expected evidence" failed. Retrieval found only Pelland of the three matchers (recall 0.33).

## Options considered
- **Add the program-design notes to the key.** Pros: the question would pass; the notes do address frequency. Cons: the notes are unreviewed AI drafts; accepting them would reward answers that cite them over the research.
- **Keep the key strict.** Pros: the eval keeps asking for research or government evidence on a numeric question. Cons: the question keeps failing while the notes outrank the expected sources.

## Decision
The coach kept the key strict: research or Guidelines only.

## Tradeoffs
- "Used expected evidence" will show a failure on this question until retrieval or the answer favors Pelland or the Guidelines. That is the intended signal, not noise.

## Revisit when
- The coach has reviewed the program-design notes and judges them acceptable evidence for frequency.
- The question keeps failing after the final evals; then look at why the notes outrank Pelland and the Guidelines.
