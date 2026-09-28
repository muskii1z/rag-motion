# 0025. AI judge for the coach's labeling rules
**Date:** 2026-09-28 · **Step:** Phase 1F, F2 · **Status:** accepted

## Context
During the eval walkthrough, the coach recorded four rules about how answers should be written, not what search should find:
1. `label-level`: an intermediate or advanced exercise must be labeled with its level.
2. `label-secondary`: an exercise that trains the asked-about muscle only secondarily (rows for biceps, or for grip) must say so.
3. `label-bodyweight`: when the person names their equipment, bodyweight exercises must be labeled as needing no equipment.
4. `group-by-muscle`: for the beginner adult, exercises are listed by muscle group, covering the major groups.

None was checked. F2's job was to make the eval complete before the filters are built ([0024](0024-phase-1f-order-data-then-eval-then-filters.md)), so these rules needed a check. Until now every answer check was code ([0021](0021-evaluation-design-code-scored-langsmith-semantic-default.md)). These rules need reading comprehension: is the Turkish get-up *labeled* intermediate, is the list *grouped* by muscle group?

The developer's view: "the rules are straightforward, the AI should be able to determine them."

## Options considered
- **Word matching in code.** Look for "intermediate" (or "secondary", "no equipment") in the same sentence as the exercise name. Pros: free, deterministic (same answer, same score). Cons: rough; misses paraphrases like "a harder progression for later"; bad at "grouped by muscle group", which is about the answer's structure.
- **AI judge (LLM-as-judge).** A second model reads the answer and grades each rule. Pros: handles paraphrase and structure; gives a reason. Cons: about half a cent per judged question; can be wrong; results can vary between runs.

Sub-choices within the AI judge:
- **Judge model.** `anthropic/claude-sonnet-5.5` ($2 / $10 per million input / output tokens) vs cheaper Gemini flash models. The answering model is `google/gemini-2.5-flash-lite`, so a Gemini judge would be the same family grading itself. Chose Sonnet: a different family, and stronger at reading.
- **Where rules apply.** On every question vs only on questions where the coach stated them. Chose per question, with a new eval field `answer_rules` (13 questions), matching where the coach actually stated the rules.

## Decision
Use an AI judge for the four labeling rules, and keep every exact-fact check in code. The judge (`src/ragmotion/judge.py`, model `anthropic/claude-sonnet-5.5` via OpenRouter) gets the question, the answer, the `general_guidance` text, and the whole exercise catalog as a table (name | level | equipment | primary muscles), so it judges against our data, not its memory. It returns structured output: per rule, `pass` / `fail` / `not_applicable` and a one-sentence reason naming the exercises. One call per tagged question. It runs as a fifth evaluator, `coach_rules`, in `evals/run_answer_eval.py`: one LangSmith score per rule, `None` when not applicable, and every verdict and reason printed for the coach to check.

## Evidence
- Smoke test on a planted mistake (a beginner glute answer naming the Bulgarian split squat without a level label): verdict `fail`, correct reason. Cost $0.0058, 2,424 prompt tokens.
- F2 baseline: 15 verdicts on 13 questions. 13 `not_applicable`, 1 pass (`constraint-one-kettlebell`: swing and Turkish get-up labeled intermediate), 1 fail (`pop-beginner-adult`: no muscle-group headings, missing groups; expected, since top 5 can't list everything). The reasons read as accurate. Cost about $0.07 for the 13 questions. See the [F2 build-log entry](../build-log.md#phase-1f-f2-strengthen-the-eval-and-record-the-before-baseline).

## Tradeoffs
- Small cost per run (about half a cent per judged question) and a network call in the eval.
- The judge can be wrong, and its verdicts may vary between runs. Mitigated by: a different, stronger model family; narrow rules with explicit `not_applicable` conditions; a required reason; grounding in the catalog; the coach spot-checking verdicts; exact facts staying in code.
- Scores are no longer fully deterministic for this one evaluator.
- With 13 of 15 verdicts `not_applicable`, the rule scores currently rest on very few real cases.

## Revisit when
- The coach's spot-checks find the judge wrong on more than an occasional verdict: tighten the rule wording, or move that rule to code.
- A rule turns out to be checkable exactly by code (for example once answers use a fixed structure), which would make it free and deterministic.
- Judge cost matters (many more questions, or repeated runs): try a cheaper model from a different family and compare its verdicts with Sonnet's on the same answers.
- The answering model changes to a Claude model: the judge would then share its family, and should change.
