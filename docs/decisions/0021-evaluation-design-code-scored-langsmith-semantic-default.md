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

## Update 2026-09-25 (after Step 15): eval set v2 after adding two research papers
See the [build log](../build-log.md#after-step-15-trace-cleanup-two-research-papers-eval-set-v2).
- **Why a v2.** After Kons 2023 and Haugen 2019 were added ([0022](0022-research-papers-europe-pmc-jats-xml-not-pdfs.md)), some v1 expectations were out of date. On the same 29 questions: semantic passage MRR 0.70 → 0.65 (53 new passages compete for top ranks), hybrid passage recall 0.92 → 0.83, keyword 0.75 → 0.67, partly because the plyometrics question expected only the youth notes. The answer eval (`answers-semantic-165701c5`, dataset `rag-motion-eval-116f4e9c`): citations 28/29, coverage 26/29, expected evidence 28/28, forbidden 2/5; `gap-sprint` "failed" because the answer was now genuinely `full`.
- **Changes (31 questions):** `ex-explosive-speed` expects the papers and `full`; `gap-plyo-program` accepts the notes, Kons, and Haugen's "Plyometric" section, still `partial`; `gap-sprint` became `research-sprint-acceleration` (`full`); new `research-plyo-effects` and `research-sprint-recovery`. Two dose page lists widened after correct answers cited pages outside them (62–63; 108–110).
- **Retrieval v2** (`evals/results/retrieval-20260925-203046.json`): semantic exercise recall 0.89, passage recall 0.97, passage MRR 0.78; hybrid 0.84 / 0.89 / 0.80; keyword 0.66 / 0.69 / 0.55.
- **Answers v2, final** (dataset `rag-motion-eval-5e040651`, experiment `answers-semantic-a9b4cded`): `citations_valid` 31/31, `used_expected_evidence` 30/30, `coverage_correct` 27/31, `no_forbidden_citations` 2/5.
- **Retry decision (brief).** The first v2 run (`answers-semantic-5f70f0cd`) scored only 29 of 31: two answers crashed on cut-off JSON. `llm.structured_completion()` now retries once on a pydantic `ValidationError`. One retry, not a loop, so a persistent problem still surfaces; the cost is an extra call on those cases.
- **Semantic stays the default.** Hybrid now has slightly better passage MRR (0.80 vs 0.78) but lower recall; within noise on 31 questions, and no hybrid answer run on v2.
- **Lesson added to the method:** when the corpus changes, update the expected answers too, version the set, and report the old questions alongside the new ones. When a score drops, check whether the system or the expectation is wrong before fixing either.
- **Still true:** all expectations are `reviewed: false`; one run per question; constraint and population failures need Phase 1F filters.

## Update 2026-09-28 (Eval walkthrough, part 1): coach review, acceptable tier, answer-level rules, reviewed baseline
See the [build log](../build-log.md#eval-walkthrough-part-1-the-answer-key-grading-by-hand-and-the-coachs-full-review).

- **The "Revisit when: the coach finishes reviewing" signal has fired.** The developer, as the coach, reviewed all 31 questions in batches of 5 (commits `b19481e` through `a66c382`). For each question they saw the key plus the matching catalog exercises, or the verbatim source sentences for document questions, but never the system's results. The file header now says the key was drafted by Claude, then reviewed by the coach, all 31, on 2026-09-28.
- **What changed in the key.** Seven questions' expected, forbidden, or page lists changed:
  - `ex-glutes-dumbbells`: BSS removed (the question says beginner), step-up added after a full-catalog check;
  - `ex-upper-back`: farmer carry added;
  - `jargon-rdl`: only the dumbbell RDL expected;
  - `constraint-no-equipment`: all 15 equipment exercises forbidden (the draft forbade 4);
  - `constraint-dumbbells-only`: bodyweight exercises expected; box jump and kettlebell swing forbidden;
  - `dose-kids`: p. 7 added;
  - `pop-beginner-adult`: no required exercises; all 14 beginner exercises acceptable; pages widened to 62–63.

  The rest were confirmed, each with a `notes` line giving the reason.
- **New field: `acceptable_exercises`.** Fine to mention if the answer labels it (secondary muscle, or intermediate for a beginner); neither required nor penalized. Added to `EvalQuestion` and passed into the LangSmith dataset. No scorer uses it yet. The key now has three tiers: expected, acceptable, forbidden. This was kept inside this record rather than given its own, because it extends the eval design here and no alternative designs were recorded.
- **Four answer-level rules, recorded but not yet coded:**
  1. an intermediate exercise suggested to a beginner is labeled intermediate;
  2. rows offered for biceps or grip say that muscle is trained secondarily;
  3. for "dumbbells only", bodyweight exercises are labeled as needing no equipment;
  4. for the beginner adult, exercises are listed by muscle group, covering all major muscle groups.

  They are candidates for new answer checks.
- **Reviewed baseline** (k=5, `structure-v1(min=150,max=450)`, voyage-4-lite; `evals/results/retrieval-20260928-124738.json`):

  | Mode | Exercise recall | Exercise hit | Exercise MRR | Passage recall | Passage hit | Passage MRR | Forbidden |
  |---|---|---|---|---|---|---|---|
  | semantic | 0.91 | 1.00 | 0.97 | 0.97 | 1.00 | 0.78 | 0.10 |
  | keyword | 0.66 | 0.76 | 0.65 | 0.69 | 0.75 | 0.56 | 0.06 |
  | hybrid | 0.85 | 1.00 | 0.86 | 0.95 | 1.00 | 0.87 | 0.13 |

  Answers (dataset `rag-motion-eval-a2d30357`, experiment `answers-semantic-9f0524fd`): `citations_valid` 31/31, `coverage_correct` 29/31, `used_expected_evidence` 30/30, `no_forbidden_citations` 2/5. Failures: both constraint questions and the beginner adult (forbidden items cited), band pull (overclaimed `full`), overhead (underclaimed `partial`).
- **Scores moved with no system change** while the key was being reviewed (semantic exercise recall 0.89 → 0.90 → 0.91 → 0.90 → 0.91; hybrid passage recall 0.89 → 0.95). Rule added to the method: compare only runs graded by the same version of the key. When a key must change, change it deliberately with a written reason, and re-baseline.
- **Semantic stays the default.** Hybrid now has better passage MRR (0.87 vs 0.78) but lower exercise recall and MRR; no hybrid answer run on the reviewed key.
- **New tradeoff surfaced: top-k vs complete answers.** A reviewed question expects 7 exercises, so top 5 caps recall at 0.71. The key was not trimmed to fit k; the gap is left visible as a finding. What to do about k is not decided.
- **Revisit when (added):** the answer-level rules get checks (the walkthrough's Lesson 4); new sources change what's correct (for example program-design papers before Phase 2), and then the affected keys are updated deliberately and re-baselined.
- **Still true:** one run per question; constraint and population failures need Phase 1F filters.

## Update (2026-09-28, Step 16): unit tests for the scorer; Phase 1F starts with the eval
- **The scoring code is now unit-tested** (`tests/test_evaluation.py`): the passage matchers, the Lesson 2 hand-graded example (recall 1, hit 1, MRR 1), partial-credit cases (recall 0.5, MRR 0.5), forbidden items, and a check that the real eval set loads with 31 unique ids, all reviewed, with valid coverage values. Tests confirm the ruler is built correctly; the eval itself still measures quality.
- **Weaknesses of the eval, named before building filters:** only 3 questions test limits (2 constraint, 1 population), so one flip moves that score 33–50%; the four answer-level rules aren't checked; precision isn't measured.
- **Planned next** (Phase 1F, eval first): about 8–10 coach-written limit questions (bands only; kettlebell plus bench; a bodyweight beginner home workout; an older adult; a youth athlete; pregnancy; one with no limits stated, to catch over-filtering); code checks where possible (for example, "intermediate" must appear) and an LLM grader, validated against the coach's grades, for rules like "grouped by muscle group"; then a new baseline before the filters. See [0023](0023-phase-1-completion-tests-and-errors-before-retrieval-changes.md).

## Update (2026-09-28, Phase 1F F2): 40 questions, a fifth evaluator judged by an LLM, new baseline
- **Eval set now 40 questions.** Keys updated for the 42-exercise catalog (mechanical keys generated from `equipment` and `difficulty`; judgment keys approved by the coach). 9 coach-set questions added: 6 equipment (including a no-limits trap question for over-filtering) and 3 population (older adult, youth, pregnancy). Dataset `rag-motion-eval-0b0fc360`.
- **Not code-only any more.** The four answer-level rules are graded by an AI judge (`coach_rules` evaluator), only on the 13 questions tagged with `answer_rules`. Exact-fact checks stay in code. Reasoning in [0025](0025-ai-judge-for-coach-labeling-rules.md).
- **F2 baseline** (`evals/results/retrieval-20260928-140007.json`; experiment `answers-semantic-0b42f62a`): semantic exercise recall 0.80, hit 1.00, MRR 0.96; passage recall 0.97, MRR 0.79; forbidden 0.17. Keyword 0.59 / 0.66 (exercise / passage recall); hybrid 0.75 / 0.93, passage MRR 0.86. Answers: citations 40/40, coverage 36/40, expected evidence 38/39, no forbidden citations 8/13. **Semantic stays the default.**
- This is the frozen "before" for the filters. F6 re-runs the same 40 questions.

## Update (2026-09-28, Phase 1F F6): coverage keys set by the coach; final before/after
- **Three keys changed:** `constraint-bands-only`, `constraint-one-kettlebell`, `constraint-pullup-bar-only` now expect `partial`, not `full`. Coach's reason, stored as a YAML comment on each: "only a few exercises fit this equipment, so a full workout isn't possible from our catalog." New dataset `rag-motion-eval-23e1f7fa`.
- **Comparison method:** 3 runs per version, same key ([0028](0028-before-after-averaged-over-three-runs.md)). No filters (`answers-semantic-bfb70035`, `-bb82b648`, `-bf8a7a2f`) vs filters (`answers-semantic-filtered-ff75447b`, `-df4717be`, `-f4ea8417`).
- **Result:** no forbidden advice 27/39 (69%) → 39/39 (100%); citations 118/120 both; expected evidence 115/117 both; coverage 106/120 (88%) → 109/120 (91%).
- **Retrieval** (F5 file `retrieval-20260928-144918.json`): semantic + filters is now the default row: exercise recall 0.83, passage recall 0.97, passage MRR 0.86, 0% of questions with a forbidden item.
- **Evaluator errors:** the AI judge lost most verdicts to a rate limit when 6 evals ran in parallel; fixed with retry ([0025 update](0025-ai-judge-for-coach-labeling-rules.md)).
- **Still failing:** `ex-band-pull` and `ex-overhead` coverage claims across runs (keys may need the coach); `pop-beginner-adult` group-by-muscle (top-5 ceiling).
