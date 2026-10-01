# 0042. A request for bodyweight exercises is a no-equipment limit; naming an exercise or its equipment is not
**Date:** 2026-10-01 · **Step:** Finishing Phase 1F (going public) · **Status:** accepted

## Context
The first final eval (52 questions, filters + slang dictionary) found `jargon-bw-squat` ("BW squat progression") retrieving the barbell back squat, which its key forbids. One of 3 answer runs cited it. The dictionary had already expanded "BW" to "bodyweight". But `extract_limits` (the small LLM call that reads equipment and population from the question, see [0026](0026-equipment-prefilter-from-llm-read-limits.md)) didn't read "bodyweight squat progression" as a limit. With no limit, no equipment filter ran, so the barbell squat could rank on similarity.

Before this, "limited" meant only: the question says what the person has, or that they have nothing.

## Options considered
- **Leave the limit reader alone; accept the occasional barbell citation.** Pros: no prompt change, no risk to the other 51 questions. Cons: a forbidden citation in 1 of 3 runs, on a question built to test exactly this slang.
- **Add a keyword rule in code** (if the rewritten question contains "bodyweight", set no equipment). Pros: deterministic. Cons: "bodyweight" also appears in questions that aren't requests for bodyweight-only work; a blunt rule would over-filter.
- **Add one line to `LIMITS_SYSTEM_PROMPT`:** asking specifically for bodyweight exercises means no equipment. Pros: the reader already handles varied phrasing; one line. Cons: a prompt change reaches every question.

## Decision
The prompt line, plus a second line after the first over-reached. Final wording in `src/ragmotion/llm.py`:
- Asking specifically for bodyweight exercises ("bodyweight squat progression", "BW leg exercises") means no equipment: `equipment_limited` true, `equipment_owned` empty.
- Naming an exercise or the equipment for an exercise ("kettlebell swing for hip power", "band pulling exercises") is not a limit: false.

The second line was needed because the first alone made `jargon-kbs` ("KBS (kettlebell swing) for hip power") kettlebell-only and `ex-band-pull` band-only, which would have hidden good exercises.

Verified on all 52 questions, twice: exactly the 7 constraint questions plus `jargon-bw-squat` are equipment-limited, and the 12 population readings are unchanged. Final answer runs: no forbidden citations 45/45 (from 44/45 before the fix). See the [build log](../build-log.md#finishing-phase-1f-for-a-public-portfolio-coach-reviews-final-evals-readme-rewrite-pre-public-checks).

## Tradeoffs
- The line between "asking for bodyweight exercises" and "naming equipment" is decided by a model reading a prompt, not by code. It's checked on 52 questions, not guaranteed.
- A bodyweight request now hides every equipment exercise, even ones the person might own. That is what the coach's key wants for this question, but a person who says "bodyweight squat progression" and owns a barbell gets no barbell options.
- Every extraction-prompt change now needs a full 52-question re-check, run twice. That's slower than checking the one failing question.

## Revisit when
- A real or eval question that names equipment gets filtered (over-reach again), or a bodyweight request isn't filtered.
- The eval gains new equipment phrasings: re-run the 52-question check.
- Limit reading moves from a prompt to something more deterministic (for example a rules layer on top of the dictionary).
