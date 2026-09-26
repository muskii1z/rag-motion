# 0021. Evaluation design: 29-question eval set, code-based scoring, LangSmith experiments; semantic stays default
**Date:** 2026-09-25 · **Step:** 15 · **Status:** accepted

## Context
Until Step 15, every quality judgment was made by eye on a handful of questions ("it seems to work"). The plan since [0011](0011-phase-1-plan-revision-ingestion-and-langsmith.md) and [0012](0012-keyword-baseline-and-query-rewriting.md) called for a baseline: a fixed set of test questions with expected answers, scored the same way every time, so later changes (more documents, the Phase 1F experiments) could be measured instead of claimed. 0012 also required comparing three retrieval modes: keyword only (Postgres full-text search), semantic only (pgvector), and both combined (hybrid).

Several design choices had to be made:
- how to split the evaluation (retrieval alone vs whole answers);
- how to name expected document passages, when passage ids like `pag2-57` can change after re-chunking (the Step 13 caution);
- who or what scores the answers;
- where results live;
- which retrieval mode the app uses after the numbers are in.

See [Step 15](../build-log.md#step-15-evaluation-baseline-for-retrieval-and-answers).

## Options considered

**Eval set format**
- **Chunk ids as expected passages.** Simple and exact. But re-chunking can give the same id to a different passage, silently breaking the eval.
- **Matchers: source + pages, heading, or chapter (chosen).** Expectations survive re-chunking, which matters because chunking variants are a planned experiment. Cons: a generous page list can make a question too easy to pass.

**Scoring answers**
- **LLM-as-judge.** A second model reads each answer and grades it. Can judge fuzzy qualities (is this helpful, is this claim supported). Cons: costs a call per check, gives different results on different runs, and a model grading its own kind of output is not an independent check (the warning in the master context document, and a point from the Step 5–6 article review).
- **Code-based evaluators (chosen).** Plain functions: citations valid, coverage label equals the expected one, cited at least one expected item, cited no forbidden item. Deterministic (same input, same score), free, and each score means exactly what the code says. Cons: can't judge whether prose is correct or well-reasoned, only what is structurally checkable.

**Where results live**
- **Local script output only.** Simple. But no history, no side-by-side comparison.
- **LangSmith experiments (chosen) plus local JSON for retrieval.** The retrieval eval is a local script (no LLM, instant) that saves JSON to `evals/results/`. The answer eval is a LangSmith experiment: each run is stored against a dataset and can be compared side by side with others. The dataset name includes a hash of the YAML file (`rag-motion-eval-<8 chars>`), so each version of the questions gets its own dataset and old results are never overwritten or deleted. Cons: another dependency on LangSmith; answers and prompts are stored on its servers (same tradeoff as [0020](0020-observability-langsmith-wrap-client-decorate-steps.md)).

**Default retrieval mode after the baseline**
- **Keyword.** The article's recommendation. Clearly worst on this data (below).
- **Hybrid (RRF, equal weights).** Best passage ranking, but slightly worse overall and the most forbidden retrievals.
- **Semantic (chosen).** Best or tied on almost every metric.

## Decision
- A 29-question eval set in `evals/eval_set.yaml`, in 7 categories (exercise-selection 10, jargon 3, constraint 2, dose 7, population 1, notes 3, coverage-gap 3), with expected and forbidden exercises (slugs), expected and forbidden passages (matchers), and expected coverage. Expected answers are Claude's drafts, marked `reviewed: false` until the developer reviews them as a coach.
- Two evals:
  - **Retrieval:** `evals/run_retrieval_eval.py`, recall@5, hit@5, MRR, forbidden rate, all 3 modes.
  - **Answers:** `evals/run_answer_eval.py`, a LangSmith experiment with 4 code-based evaluators.
- **Semantic search stays the default.** Hybrid is kept in code as a mode but needs weight tuning (Phase 1F) before it can be the default.

**Baseline numbers** (k=5, chunker `structure-v1(min=150,max=450)`, voyage-4-lite):

| Mode | Exercise recall | Exercise hit | Exercise MRR | Passage recall | Passage hit | Passage MRR | Forbidden |
|---|---|---|---|---|---|---|---|
| semantic | 0.89 | 1.00 | 0.94 | 1.00 | 1.00 | 0.70 | 0.10 |
| keyword | 0.66 | 0.78 | 0.67 | 0.75 | 0.75 | 0.42 | 0.10 |
| hybrid | 0.84 | 1.00 | 0.87 | 0.92 | 0.92 | 0.76 | 0.14 |

Answer eval (dataset `rag-motion-eval-116f4e9c`, `google/gemini-2.5-flash-lite`, about 1.5 cents per run):

| Check | semantic | hybrid |
|---|---|---|
| citations_valid | 29/29 | 27/29 |
| coverage_correct | 25/29 | 25/29 |
| used_expected_evidence | 28/28 | 28/28 |
| no_forbidden_citations | 2/5 | 2/5 |

## Tradeoffs
- **Unreviewed expectations.** Until the coach reviews them, the scores measure agreement with Claude's drafts, not with an expert. The dose questions all scoring 1.00 may mean the page lists were generous. One expected value ("no equipment": full vs partial) is already in doubt.
- **Small sample.** 29 questions, one run each. Differences under about 0.05 are treated as noise, and the answer checks were not repeated to measure run-to-run variance.
- **What code can't see.** No evaluator judges whether the answer's prose is correct, whether general guidance is sound, or whether a claim matches its cited passage beyond the id. Those need a human (the coach) or, later, a carefully validated LLM judge.
- **Hybrid set aside for now.** Equal-weight RRF lost some good semantic results to keyword noise. Keeping semantic as default gives up hybrid's better passage ranking (MRR 0.76 vs 0.70) and its advantage on literal-word questions (biceps).
- **Dataset sprawl.** A new LangSmith dataset for every edit to the YAML keeps history but leaves many datasets to clean up by hand eventually.

## Revisit when
- **The coach finishes reviewing the expected answers.** Re-run both evals; this baseline is provisional until then.
- **A tuned hybrid (for example weighted RRF), query rewriting, or metadata filters** beat semantic by more than noise on the same eval (Phase 1F).
- **The corpus grows** (plyometrics review, sprint review, Army ATP 7-22.02) and semantic retrieval drops.
- **Questions need judgments code can't make** (quality of general guidance, claim-level groundedness). Then consider a human-review step or an LLM judge checked against the coach's own grades.
