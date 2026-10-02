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

## Update 2026-10-01 (Phase 2 quality pass, Q3): a new research source competes
After Iversen et al. 2021 (a CC BY narrative review on time-efficient training) was added, it ranked first on `prog-frequency`, and the question's passage MRR fell from 0.50 to 0.00. Iversen is research, so it meets this decision's rule ("research or Guidelines only"), but it isn't in the key. Pending with the coach: add Iversen as an additional expected source for `prog-frequency`, and also for `prog-weekly-sets`, `prog-rest-intervals`, and `prog-rep-ranges`. See [0062](0062-q3-sources-iversen-refalo-bastos-cc-by.md).

## Update 2026-10-01 (Phase 2, P3): Iversen accepted
The coach decided Iversen 2021 counts as correct evidence for `prog-frequency`, `prog-weekly-sets`, `prog-rest-intervals`, and `prog-rep-ranges` (commit `eac0c4f`). The key stays "research or Guidelines only"; Iversen is research. Passage MRR back to 0.86, passage hit rate 1.00. See [0064](0064-iversen-counts-as-correct-evidence-for-four-program-design-keys.md).
