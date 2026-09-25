# 0017. Knowledge source licensing policy (groups A–D)
**Date:** 2026-09-25 · **Step:** before 11 · **Status:** proposed (the developer chose the first document but has not formally approved this policy)

## Context
Step 11 ingests real documents: extracting their text, chunking it (splitting it into passages), and storing it in the database, possibly also committing processed text to the repo. The repo is meant to become a public portfolio. So every source's license decides what we may do with it. The developer asked for the Physical Activity Guidelines first, then NSCA material rewritten as notes, then open documents covering strength, conditioning, weightlifting, stretching, plyometrics, athletic exercises, and nutrition. Research found a wide spread of licenses, including free-to-read material that forbids reuse, and a publisher that reserves text and data mining and AI training rights. The full findings are in [candidates.md](../sources/candidates.md); the story is in the [build log](../build-log.md#before-step-11-finding-and-license-checking-knowledge-sources).

## Options considered
- **Ingest anything free to read.** Most content, least effort. But it breaks terms of use (NSCA forbids use "on any other Web site or networked computer environment"; Wolters Kluwer reserves "text and data mining and artificial intelligence training") and can't be shown publicly.
- **Only public domain and CC BY (group A).** Simplest and fully safe. But it drops useful sources such as the WHO guidelines, OpenStax A&P, BJSM articles, and the wger exercise dataset.
- **Tiered policy by license group, with provenance on every chunk (proposed).** Uses the most material safely, but needs license tracking in the data and some discipline.
- **Keep copyrighted material local only.** Fine for learning, but can't be shown in a portfolio, and still conflicts with terms such as NSCA's.

## Decision
Proposed: sort every source into one of four groups before use (definitions in [candidates.md](../sources/candidates.md#why-licenses-decide-what-we-can-use)):
- **A. Free to reuse** (US federal public domain, UK Open Government Licence v3.0, CC BY): ingest; processed text may be committed; attribute every source.
- **B. Reuse with conditions** (NC and/or SA): ingest with attribution and a license tag on every chunk, so NonCommercial chunks can be filtered out; ShareAlike-derived text kept in its own folder under the same license.
- **C. CC BY-NC-ND:** local only, don't commit processed text, or skip.
- **D. All rights reserved** (NSCA, Human Kinetics, Wolters Kluwer journals): never ingest. The developer reads them and writes original notes in their own words, with citations. Claude does not rewrite or closely paraphrase these texts into notes.

Engineering pattern, part of the proposal ([Source manifest and provenance fields on chunks](../concepts.md#source-manifest-and-provenance-fields-on-chunks)):
- Commit a source manifest (URL, license, attribution) and the ingestion script.
- Keep downloaded files in a git-ignored `data/raw/` folder (not yet added to `.gitignore`).
- Store `source_url` and `license` on every chunk.

First document, chosen by the developer: the Physical Activity Guidelines for Americans, 2nd ed. (group A, public domain). Next group-A candidates are listed in the [recommended ingestion order](../sources/candidates.md#recommended-ingestion-order).

## Tradeoffs
- Skips or limits valuable material: NSCA's *Essentials* and position statements, JSCR articles, the ACSM 2026 position stand (CC BY-NC-ND).
- NSCA-based knowledge depends on the developer's time to write notes.
- Extra columns and a manifest to maintain. Licenses change (OpenStax moved from CC BY to CC BY-NC-SA) and vary within one journal (some JISSN stands are CC BY-NC), so checks are per item and dated.
- Some licenses are UNVERIFIED (for example the ATP 7-22.02 public-release statement, seen only in search snippets) and must be confirmed before use.
- This is a project policy, not legal advice.

## Revisit when
- The developer approves, amends, or rejects this proposal.
- The project becomes commercial (group B NonCommercial sources would have to be filtered out or dropped).
- The developer wants to grow the exercise table from wger (CC BY-SA). The `CLAUDE.md` rule "Exercise data is original, author-written content" would have to change first.
- A publisher grants permission, or a license changes.
