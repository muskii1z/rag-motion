# 0027. Population tags on passages from document-structure rules, with a keep-general filter
**Date:** 2026-09-28 · **Step:** Phase 1F, F5 · **Status:** accepted

## Context
Population mixing (an answer for one group using numbers written for another) was first seen in Step 13 and measured in Step 15: for "beginner adult" questions, search returned older-adult and youth passages, and the model used their numbers. A prompt rule reduced it but didn't stop it. After the equipment filter ([0026](0026-equipment-prefilter-from-llm-read-limits.md)), it was the last forbidden failure: forbidden rate 0.03 (1 of 40 questions), forbidden citations 12/13. [0019](0019-structure-aware-chunking-150-450-labels-no-overlap.md) had planned a population tag per passage but left open how passages get their tag.

Choices needed: how to tag passages, what shape the tag takes, what the filter does with untagged passages, how to read the population from the question, and whether exercises are filtered too.

## Options considered
How to tag passages:
- **Rules from the document's structure.** The Physical Activity Guidelines have a chapter per population; the NSCA notes are one file per group. Pros: free, deterministic (same answer every time), unit-testable, and possible without re-chunking because every chunk already stores its chapter and headings. Cons: each new source needs its own rule; a research paper about one group gets tagged general unless someone writes a rule.
- **An LLM tags each passage.** Pros: works on any source without writing rules. Cons: costs a call per passage, can guess wrong, and the answer can change between runs; the tags would need checking anyway.
- **Tag by hand.** Pros: most accurate. Cons: 200 passages, and again for every new source.

Shape of the tag:
- **One value per passage.** Simple. Cons: summary passages and chronic-conditions passages are about more than one group.
- **A list (`text[]`) with a CHECK on allowed values.** Handles multi-group passages; the database rejects unknown values.

What to do with untagged (general) passages:
- **Keep only passages tagged for the question's group.** Cons: 132 of 200 passages are general, so most useful material would disappear.
- **Keep general passages; remove only other groups' passages.** Pros: no over-filtering of shared material. Cons: general material may be less specific.

Reading the population from the question:
- **A second LLM call.** Cons: more cost and time.
- **Add a field to the existing `extract_limits` form.** No extra call; one form for all limits (as [0026](0026-equipment-prefilter-from-llm-read-limits.md) planned).

## Decision
Tag passages with rules from where they sit in their source (`populations_for()` in `src/ragmotion/chunking.py`): Guidelines Chapter 3 youth, 4 adults, 5 older adults, 6 pregnancy (if headings or opening text mention pregnancy or postpartum) or else adults + older adults; summary passages get every group whose "Key Guidelines for ..." block they contain; NSCA older-adult and youth notes get their group; everything else, including the weightlifting notes and research papers, is general. Store tags as `document_chunk.populations text[] NOT NULL DEFAULT '{}'` with a CHECK limiting values to `adults`, `older-adults`, `youth`, `pregnancy`; empty means general. Read the question's population as a new `population` field in `QuestionLimits`, filled by the same `extract_limits` call. Filter both passage searches with `population IS NULL OR cardinality(populations) = 0 OR population = ANY(populations)`. Exercises are not population-filtered.

## Evidence
Same 40 questions as the F2 baseline ([build-log entry](../build-log.md#phase-1f-f5-population-tags-on-passages-and-a-population-filter)):
- Tags: 200 passages, 132 general, 68 tagged, matching the chapters.
- Question reading: after one prompt fix, correct on all 40 (12 name a group, 28 don't).
- Retrieval (F4 → F5): forbidden rate 0.03 → 0.00; passage MRR 0.79 → 0.86; passage recall 0.97 unchanged.
- Answers (F4 → F5): no forbidden citations 12/13 → 13/13; citations valid 39/40 → 40/40. Coverage correct 36/40 → 33/40, mostly `partial` claims on filtered questions whose keys the coach still has to settle.

## Tradeoffs
- New sources need their own tagging rule; research papers are general even if a study used a specific group.
- A misread population silently removes passages. The first prompt read "athletes" as adults on 4 questions; it was caught by checking all 40 by eye, not by a runtime check.
- General passages still reach every question, so less specific material can take top-5 slots.
- Exercise suitability by age is not filtered. That is a level or coaching question, and no level filter exists yet.
- The four population values mirror the database in a Python `Literal`; both must change together.

## Revisit when
- A new source mixes populations inside chapters, or has no structure to tag from (consider LLM tagging checked by the coach).
- Population mixing shows up again in the eval or in use.
- A question names a group outside the four values (for example a specific chronic condition), or a coach wants exercises filtered by population.
- Coverage labels on filtered questions stay "wrong" after the coach settles the keys.
