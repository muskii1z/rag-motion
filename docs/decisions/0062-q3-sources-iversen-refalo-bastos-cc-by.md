# 0062. Q3 sources: Iversen, Refalo, Bastos (CC BY); Robinson 2024 and a no-derivatives trial skipped
**Date:** 2026-10-01 · **Step:** Phase 2 quality pass, Q3 · **Status:** accepted

## Context
The quality pass ([0059](0059-quality-pass-before-the-program-page.md)) planned sources on time-efficient program design and proximity to failure, including RIR (reps in reserve: how many more reps you could have done when you stopped a set). The program builder had research on sets, reps, rest, and weekly volume ([0038](0038-program-design-sources-three-cc-by-papers-pelland-preprint.md)), but none on session length or how hard each set should be. Every candidate had to pass the licensing policy ([0017](0017-knowledge-source-licensing-policy.md)) before download.

## Options considered
- **Iversen et al. 2021, *No Time to Lift?* (Sports Med, narrative review, PMC8449772).** Pros: covers time-efficient programs; CC BY 4.0 inside the XML. Cons: broad; it touches sets, rest, loads, and frequency, so it competes with the specific papers already in the corpus.
- **Refalo et al. 2023, proximity to failure and hypertrophy (Sports Med, systematic review with meta-analysis, PMC9935748).** Pros: answers "how close to failure" directly; CC BY 4.0.
- **Bastos, Machado, Teixeira 2024, RIR scales (Percept Mot Skills, scoping review, PMC11127506).** Pros: explains RIR scales for choosing loads; CC BY 4.0.
- **Robinson et al. 2024, proximity-to-failure dose-response.** Pros: on topic. Cons: the published version is paywalled; Refalo covers the topic.
- **A 2024 *Journal of Sports Sciences* trial.** Cons: CC BY-NC-ND. NoDerivatives forbids sharing adapted versions; chunked text is arguably an adaptation, so the policy doesn't allow it.

## Decision
Ingest Iversen, Refalo, and Bastos as license group A, each with its license sentence quoted from its own XML, sha256, and full attribution in `data/sources.toml`. Tag all three `adults` (`ADULT_RESEARCH` in `chunking.py`). Skip Robinson 2024 and the NC-ND trial. The developer approved the downloads: "all is fine, just get it done".

## Tradeoffs
- Iversen, a broad review, now ranks first on the weekly-sets, rest, rep-range, and frequency questions, ahead of the specific meta-analyses their keys expect. Passage MRR fell 0.84 → 0.76; answers still used expected evidence 52/54 times (1 run, no judge). Whether Iversen joins those keys is pending with the coach.
- No dose-response paper on proximity to failure (Robinson); Refalo stands alone on that question.
- The `adults` tag keeps all three out of youth, older-adult, and pregnancy answers.
- Bastos needed a reader fix for tables nested in paragraphs ([0063](0063-jats-tables-nested-in-paragraphs-read-separately.md)).

## Revisit when
- The coach decides on Iversen in the answer keys (accept it, or keep the keys strict and look at why it outranks the meta-analyses).
- Robinson 2024 or a similar dose-response paper becomes openly licensed.
- The program builder's answers on effort or session length turn out thin when the coach reviews programs (P4).

## Update 2026-10-01 (Phase 2, P3): the Iversen key decision
The coach accepted Iversen as an additional expected source on the four program-design questions. Passage MRR 0.76 → 0.86 with no search change. See [0064](0064-iversen-counts-as-correct-evidence-for-four-program-design-keys.md).
