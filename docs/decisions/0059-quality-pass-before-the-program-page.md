# 0059. A quality pass (Q1–Q3) before the program page
**Date:** 2026-10-01 · **Step:** Phase 2 quality pass · **Status:** accepted

## Context
The next planned step was P3, the program page. Then the developer's coach review showed a program passing every check while being poorly designed, and the catalog lacks basics such as a dumbbell bench press. The developer: "I want to ensure we have the correct amount of knowledge and function to provide really well researched and informed programs." The plan was agreed in plan mode before any code changed.

## Options considered
- **Build the program page next (P3), fix quality later.** Pros: a visible demo sooner. Cons: shows programs a coach would reject.
- **Quality pass first, then the page.** Pros: the page shows better programs; the P4 eval measures a stronger system. Cons: the page and eval come later.

## Decision
Do a quality pass before P3:
- **Q1:** program-quality checks (done, [0057](0057-program-quality-checks-weekly-sets-patterns-day-labels.md)).
- **Q2:** about 20 new exercises including machines and cables, with horizontal/vertical labels ([0058](0058-push-and-pull-get-horizontal-vertical-labels.md)), coach-reviewed. Developer's choice (the recommended option).
- **Q3:** sources on time-efficient program design and proximity to failure (RIR, reps in reserve), license-checked first.

Then P3 (program page) and P4 (program eval).

## Tradeoffs
- The program page and eval move later.
- Q2 means new equipment values (machines, cables) and coach review of about 20 exercises; the eval set and filters may need updating for the bigger catalog (not yet assessed).
- Q3 depends on finding openly licensed sources (licensing policy: [0017](0017-knowledge-source-licensing-policy.md)).

## Revisit when
- Q2 or Q3 stalls (for example, no openly licensed sources for Q3): move on to P3 with what exists.

## Update 2026-10-01: Q2 and Q3 done
- Q2: see [0060](0060-machine-and-cable-equipment-and-a-direction-column.md) and [0061](0061-narration-forces-a-submission.md). The coach's Q2 answer-key calls were applied (`cdcb98b`).
- Q3: three CC BY papers (Iversen 2021 time-efficient training, Refalo 2023 proximity to failure, Bastos 2024 RIR scales), three eval questions (55 total). See [0062](0062-q3-sources-iversen-refalo-bastos-cc-by.md). Open before P3: the coach's decision on Iversen in four answer keys.
