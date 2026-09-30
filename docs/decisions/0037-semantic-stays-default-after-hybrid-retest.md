# 0037. Semantic search stays the default after re-testing hybrid with filters
**Date:** 2026-09-30 · **Step:** Phase 1F, F7d · **Status:** accepted

## Context
In Step 15, equal-weight hybrid search (keyword + semantic, merged with reciprocal rank fusion) was slightly worse than semantic search overall, but ranked the right passage higher (passage MRR 0.76 vs 0.70). Semantic stayed the default and tuned hybrid weights went on the Phase 1F list ([0021](0021-evaluation-design-code-scored-langsmith-semantic-default.md), [0012](0012-keyword-baseline-and-query-rewriting.md)).

Since then, three changes went in: the equipment filter (F4), the population (age-group) filter on passages (F5), and the slang dictionary (F7c, [0036](0036-query-rewriting-dictionary-default.md)). Hybrid had to be re-tested on top of them. The developer also proposed a design of their own: semantic for exercises (where keyword search is weak) and hybrid for passages (where it had helped). See the [F7d build log entry](../build-log.md#phase-1f-f7d-hybrid-search-re-tested-with-filters-weightings-and-a-split-mode-readme-results-update).

MRR (mean reciprocal rank) measures how high the first right item ranks; 1.0 means always first. Weighted RRF multiplies each list's rank points by a weight; "2:1" means semantic ranks count double.

## Options considered
Measured on 46 questions, filters + slang dictionary on, top 5 (exercise recall / passage recall / passage MRR; all 0% forbidden):

- **Semantic (current default).** 0.87 / 0.97 / 0.86. Pros: best passage ranking with filters, best or tied exercise recall, one search per question. Cons: no exact-word matching.
- **Hybrid 1:1, 2:1, 3:1.** 0.83 / 0.96 / 0.83, 0.84, 0.79. Pros: exact phrases can lift a passage. Cons: lower exercise recall at every weight (keyword search is weak on short exercise entries and slang); a second query per search; no weight beat semantic on passages.
- **Split (developer's idea): semantic exercises, hybrid passages.** 0.87 / 0.96 / 0.83, 0.84, 0.79 (1:1, 2:1, 3:1). Pros: keeps semantic's exercise recall. Cons: passages still no better than semantic; on full answers (split 2:1 vs semantic, 3 runs each, judge skipped): coverage claim correct 0.855 vs 0.906, no extra exercises 0.655 vs 0.724, citations 0.978 vs 0.986; better on expected evidence (1.000 vs 0.978) and completeness (0.862 vs 0.852); no forbidden citations 1.000 both.

## Decision
Semantic search stays the default. Hybrid (with `settings.hybrid_semantic_weight`) and split stay in the code, selectable in the evals with `--mode hybrid|split --weight N`. Claude recommended keeping semantic; the developer made the call on the data.

## Tradeoffs
- Gives up keyword search's strength on exact phrases. If future sources rely on exact terms, semantic may miss what hybrid would catch.
- Split's small gains on expected evidence and completeness are given up with it.
- The retrieval comparison is one run per weighting; differences of 0.01 to 0.02 may be noise. Not re-checked.
- Two unused search modes stay in the code to maintain.

## Revisit when
- New sources (for example the program-design papers) bring questions that depend on exact terms and semantic search misses them.
- A filter or data change alters passage ranking again; the hybrid advantage disappeared because of the F5 filter, so another big change could bring it back.
- Reranking is tested: a reranker may make a wider hybrid candidate pool worth it.
