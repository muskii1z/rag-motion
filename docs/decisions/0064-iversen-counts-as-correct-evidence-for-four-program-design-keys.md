# 0064. Iversen 2021 counts as correct evidence for four program-design keys
**Date:** 2026-10-01 · **Step:** Phase 2, P3 (before the page) · **Status:** accepted

## Context
Q3 added Iversen et al. 2021, a CC BY narrative review (a broad expert summary, without pooled numbers) on time-efficient training ([0062](0062-q3-sources-iversen-refalo-bastos-cc-by.md)). It covers sets, rest, loads, and frequency, so it ranked first on four program-design questions whose answer keys listed only specific meta-analyses (studies that pool many trials into one estimate). Passage MRR (mean reciprocal rank: how high the first expected passage ranks) fell from 0.84 to 0.76, while answers still used expected evidence 52/54 times. The question was whether the key or the search was wrong. That is a coaching call.

## Options considered
- **Keep the keys strict (meta-analyses only).** Pros: rewards the most specific evidence. Cons: marks a legitimate, relevant research source as a miss; MRR keeps reporting a problem that isn't one.
- **Add Iversen as an additional expected source.** Pros: the key matches what a coach accepts; meets [0040](0040-prog-frequency-key-strict-research-or-guidelines-only.md)'s rule ("research or Guidelines only"). Cons: the eval no longer tells us when a broad review outranks the specific study.
- **Change retrieval to favor meta-analyses.** Pros: specific evidence first. Cons: a code change to fix what may be a key problem; no measurement said answers were worse.

## Decision
The coach: Iversen counts as correct. `iversen2021-time-efficient` is now an additional expected passage source for `prog-weekly-sets`, `prog-rest-intervals`, `prog-rep-ranges`, and `prog-frequency`, with a YAML note in `evals/eval_set.yaml` (commit `eac0c4f`).

## Tradeoffs
- The eval no longer flags a broad review ranked above the specific meta-analysis on these four questions.
- The key changed, so earlier passage MRR numbers aren't directly comparable. After the change: passage MRR 0.86, passage hit rate 1.00 (`evals/results/retrieval-20261001-173849-160974.json`).

## Revisit when
- Answers start citing Iversen in place of a meta-analysis where the specific number matters (for example, weekly sets), and the coach judges the answer weaker for it.
- More broad reviews are added and start crowding specific studies out of the top 5.
