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

## Update (2026-09-28, Phase 1F F6): retry on rate limits; README claim updated
- **The judge hit a rate limit.** Six answer evals ran in parallel, and OpenRouter returned HTTP 429 (`RateLimitError`): "new accounts are limited to 20 requests per minute for this model". Most judge verdicts in those runs were lost; the code checks were unaffected. The problem showed up as missing scores, not low ones.
- **Fix in code:** `judge_answer()` catches `openai.RateLimitError` and retries after 10, 20, 40, then 60 seconds, then raises. Chosen over lowering eval concurrency (how many evals may run at once) globally. Also: don't run many evals in parallel on this account. A sequential re-run (`answers-semantic-filtered-ac5b7163`) had 0 evaluator errors.
- **Verdicts from that run:** `label-level` pass on `constraint-one-kettlebell`; `group-by-muscle` fail on `pop-beginner-adult` (five exercises in one sentence, missing core, glutes/hamstrings, and arms; the top-5 ceiling).
- **Lost:** the judge's rules have no 3-run before/after comparison ([0028](0028-before-after-averaged-over-three-runs.md)).
- **README:** the design row "Code-based eval checks, not an LLM judge" was replaced by "Code checks for facts; an AI judge only for the coach's labeling rules", which matches this decision.
- **Revisit when (added):** the account's rate limit rises, or the judge moves to a provider with a higher limit; then parallel runs are safe again.

## Update (2026-09-30): judge cost checked; cheaper judge proposed, not decided
- **Spend so far:** $2.77 of the $10 OpenRouter limit in total. Most of it is the judge: about 8 cents per eval run, over about 30 runs. The judge runs only in evals, never in the app.
- The developer asked: "Do we need Claude Sonnet as the judge? It's quite expensive." This is the "judge cost matters" revisit signal above.
- **Options proposed:**
  - GPT-5 mini, about 1 cent per run, a different family from the Gemini answerer. Recommended, but only after an agreement check: both judges grade the same answers and their verdicts are compared.
  - Claude Haiku 4.5, about 4 cents per run.
  - Gemini Flash-Lite: rejected, same family as the answering model.
- **Status:** not decided. The agreement check has not been run. Sonnet 5.5 stays the judge until then.
