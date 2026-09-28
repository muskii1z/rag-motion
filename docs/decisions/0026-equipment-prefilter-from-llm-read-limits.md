# 0026. Equipment pre-filter from LLM-read limits
**Date:** 2026-09-28 · **Step:** Phase 1F, F3 + F4 · **Status:** accepted

## Context
The F2 baseline measured the system's main weakness: it suggests exercises the person can't do. On 40 questions, 17% of questions retrieved a forbidden item in the top 5, and only 8 of 13 limit questions were answered without citing one. For example, the "beginner at home" answer suggested inverted row, bench dip, and band curl to someone with no equipment. The evidence sent to the model already listed each exercise's equipment, and the model was expected to respect the person's limits; it didn't reliably ([Prompt rules have a ceiling](../concepts.md#prompt-rules-have-a-ceiling-especially-on-small-models)). Every search mode failed these questions the same way, so this was a filtering problem, not a ranking problem ([Filtering problems vs search problems](../concepts.md#filtering-problems-vs-search-problems)).

Two choices were needed: **where** to enforce the limit, and **how** to learn the limit from the question.

## Options considered
Where to enforce it:
- **Prompt instructions.** Tell the model to use only exercises that fit the stated equipment. Pros: no code change. Cons: already failing (5 of 13); a rule makes a mistake less likely, not impossible.
- **Post-filter the LLM's answer.** Check cited exercises against the owned equipment after answering, and remove or reject. Pros: catches mistakes at the end. Cons: the answer may be written around an exercise that must then be cut; forbidden items still use top-5 slots, so fewer usable exercises reach the model.
- **Pre-filter in SQL.** Add `equipment <@ owned` to the search query, so unusable exercises are removed before similarity ranking. Pros: forbidden exercises never reach the model; deterministic; free; the top 5 fill with usable items. Cons: if the limit is read wrong, good exercises disappear silently.

How to read the limit:
- **Keyword rules in code** ("only", "no equipment", equipment names). Pros: free, deterministic. Cons: phrasing varies ("a pair of dumbbells", "at home with no equipment"), and naming equipment isn't always a limit ("dumbbell exercises for glutes").
- **A small structured LLM call.** Pros: handles varied phrasing; returns allowed names only. Cons: one extra call per question (cost and time); can misread.

## Decision
Pre-filter exercises in SQL with `equipment <@ owned`, where `owned` comes from a structured LLM call (`extract_limits`, `google/gemini-2.5-flash-lite`, temperature 0, `max_tokens` 300) that fills `QuestionLimits`. "Limited" is strict: true only if the question says what the person has, or that they have nothing. Code, not the model, adds `bodyweight` to every owned list; with no limit, `owned` is NULL and nothing is filtered. Equipment only in this step; level and population wait for their own filters, one change at a time. Passages are not equipment-filtered. F3 (read limits) and F4 (filter) were combined into one step at the developer's request, because neither works without the other.

## Evidence
Same 40 questions as the F2 baseline ([build-log entry](../build-log.md#phase-1f-f3--f4-read-equipment-limits-from-the-question-and-filter-exercises)):
- Limit reading correct on all 40. Filters applied to exactly the 7 questions that state what the person has; not applied to the full-gym trap question or to three questions that name equipment without limiting it. Cost $0.0013 for all 40.
- Retrieval (semantic → semantic+filter): forbidden rate 0.17 → 0.03, exercise recall 0.80 → 0.83, constraint-category recall 0.66 → 0.76; passages unchanged. The trap question still retrieves all 4 barbell lifts.
- Answers (`answers-semantic-0b42f62a` → `answers-semantic-filtered-a2703a28`): no forbidden citations 8/13 → 12/13. The one left (`pop-beginner-adult`) is a wrong-population passage, which this filter doesn't cover.

## Tradeoffs
- One extra LLM call per question: about $0.00003 and a few hundred milliseconds.
- A misread limit hides good exercises silently. Mitigated by the by-eye check on all 40 questions and the over-filtering trap question, not by a runtime check.
- The strict meaning of "limited" means "dumbbell glute exercises" can still return an exercise that also needs a bench. Acceptable: nothing is forbidden for that question.
- The filter is only as right as the catalog's equipment data. Goblet squat is listed as dumbbell, so it is dropped for kettlebell-only questions even though the coach said it counts with a kettlebell (it was only "acceptable" there).
- Level ("beginner") is not filtered yet.

## Revisit when
- A question's limit is misread in the eval or in use (a wrong or missing filter). Tighten the prompt or add cases to the eval.
- Latency or cost of the extra call matters. Consider combining it with another step (for example query rewriting in F7) or a cheaper path for questions with no equipment words.
- Level or population filters (F5 and later) are added: extend `QuestionLimits` rather than adding a second reading call, and measure each filter separately.
- The catalog needs "either/or" equipment (goblet squat with a dumbbell or a kettlebell); `<@` on one list can't express that.
