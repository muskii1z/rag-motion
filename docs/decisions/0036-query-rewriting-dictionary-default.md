# 0036. Query rewriting: slang dictionary by default, not an LLM rewrite
**Date:** 2026-09-30 · **Step:** Phase 1F, F7c · **Status:** accepted

## Context
Coaches write in gym slang: RFESS, BW, DB, SL RDL, KBS. [0012](0012-keyword-baseline-and-query-rewriting.md) planned query rewriting (changing the question before search so it matches how the catalog is written) as a Phase 1F experiment, with an LLM and an abbreviation glossary.

A probe of 20 slang questions (search only, filters on) found 16 already ranked the right exercise #1. The failures were narrow: RFESS (#5 in one wording, missed in "RFESS with DBs"), "BW squat progression" (BW read as barbell, so the barbell back squat ranked #1), and "DB row for the lats" (#2 behind the barbell row). Four failing questions and two guard questions (already passing, must not break) were added to the eval, approved by the coach (46 questions total). See the [F7c build log entry](../build-log.md#phase-1f-f7c-query-rewriting-for-coach-slang-dictionary-vs-llm-rewrite).

## Options considered
- **No rewriting.** Pros: nothing to build or maintain. Cons: the four slang failures stay; "BW squat progression" cited the barbell back squat in all 3 answer runs.
- **Dictionary (`expand_slang()`).** An 18-term glossary applied by one regular expression: longest term first, whole words only, case-insensitive, one pass; keeps the abbreviation and adds the full term. Pros: deterministic, free, 0 ms, unit-tested. Cons: the glossary is maintained by hand; unknown slang passes through unchanged.
- **LLM rewrite (`rewrite_with_llm()`).** A structured call on the default model (temperature 0, `max_tokens` 200) with the same glossary in the prompt. Pros: can handle phrasing the glossary never saw. Cons: about 640 ms median per question, one more call that can fail, output can vary.

Measured on 46 questions (retrieval: semantic + filters, top 5; answers: 3 runs each, judge skipped):

| | None | Dictionary | LLM |
|---|---|---|---|
| Retrieval MRR | 0.86 | 0.97 | 0.97 |
| Retrieval forbidden rate | 0.02 | 0.00 | 0.02 |
| Answers: no forbidden citations | 0.929 | 1.000 | 1.000 |
| Answers: used expected evidence | 0.956 | 0.978 | 0.993 |
| Answers: coverage claim correct | 0.891 | 0.906 | 0.935 |
| Answers: no extra exercises | 0.793 | 0.724 | 0.736 |
| Median total time per question | 2.42 s | 2.42 s | 3.08 s |

## Decision
The dictionary is the default: `settings.query_rewrite = "dictionary"` in `src/ragmotion/config.py`. The rewritten question is used only to read the limits and to search; the answer model still gets the coach's original question. The LLM version stays in the code, selectable with `--rewrite llm` in the evals. Reasons: same answer quality as the LLM rewrite, it fixed the BW-squat retrieval that the LLM rewrite didn't (the LLM wrote "Bodyweight squat progression" and search still retrieved the barbell back squat), zero added time (the LLM added about 26%), and no extra call to fail. Claude set the default with a stated recommendation; the developer can revert it with one line.

## Tradeoffs
- The glossary has to be maintained by hand. Slang not in it isn't expanded.
- Single-exercise slang answers mention more related variants: "no extra exercises" 0.79 → 0.72. Mostly acceptable variants (for example SL RDL in a beginner RDL answer, which the coach allows only if labeled intermediate).
- The LLM version scored slightly higher on coverage (0.935 vs 0.906) and expected evidence (0.993 vs 0.978). Over 3 runs each this may be noise; it was not tested further.

## Revisit when
- New slang failures show up in evals or real use, especially slang the glossary can't reasonably list.
- The catalog grows enough that keeping the glossary current becomes real work.
