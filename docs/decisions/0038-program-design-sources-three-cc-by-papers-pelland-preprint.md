# 0038. Program-design evidence: three CC BY papers, Pelland as a labeled preprint; paywalled sources skipped
**Date:** 2026-09-30 · **Step:** Pre-Phase 2 · **Status:** accepted

## Context
A future program generator needs cited numbers for sets, reps, load, rest, and weekly volume and frequency. The knowledge base had none of this from research: the Physical Activity Guidelines give weekly minimums, and the NSCA notes cover specific groups (older adults, youth, weightlifting). The licensing policy ([0017](0017-knowledge-source-licensing-policy.md)) allows ingesting only sources whose license permits reuse (group A: public domain or CC BY, where CC BY means anyone may reuse with credit).

## Options considered
- **Schoenfeld 2021 (loading and rep ranges), Singer 2024 (rest between sets), Pelland 2024 (weekly volume and frequency).** Pros: all CC BY; together they cover the three program-design questions; the first two are in Europe PMC as JATS XML (structured text, no PDF cleaning, [0022](0022-research-papers-europe-pmc-jats-xml-not-pdfs.md)). Cons: Pelland's published Sports Medicine version is paywalled, so only the SportRxiv preprint v2 (doi 10.51224/SRXIV.460) can be used, and it is not peer reviewed; its PDF needs page skipping (45 pages, 18 skipped).
- **ACSM 2009 progression-models position stand.** Pros: widely cited. Cons: paywalled. Rejected.
- **Moesgaard 2022 on periodization (Sports Medicine).** Pros: covers periodization. Cons: paywalled. Rejected.
- **NSCA *Essentials* program-design chapters.** Pros: the coach's standard textbook. Cons: copyrighted book (group D), never ingested. See [0039](0039-program-design-notes-from-general-practice-not-nsca.md) for what was done instead.

## Decision
Ingest the three CC BY papers, with license evidence quoted from inside the XML (Schoenfeld, Singer) or from the SportRxiv page (Pelland). Pelland's title in the manifest says "2024 preprint, not peer reviewed", so every citation shows it. All three are tagged `adults` (`ADULT_RESEARCH` in `chunking.py`), because they studied healthy adults. The developer approved all three downloads.

## Tradeoffs
- The volume and frequency evidence is a preprint. The peer-reviewed version may differ, and the system cannot cite it.
- No periodization research source; periodization appears only in the draft program-design notes.
- The `adults` tag keeps these papers out of youth, older-adult, and pregnancy answers, even where a coach might judge a finding transferable.
- Journal boilerplate (data availability, conflicts of interest, publisher's note) had to be added to the JATS skip list after it produced 13–18-word passages.

## Revisit when
- A peer-reviewed version of Pelland becomes openly licensed: swap the preprint for it.
- The coach finds a preprint finding that the published version changed.
- The program generator needs evidence these papers don't cover (for example periodization, power, or specific populations).
