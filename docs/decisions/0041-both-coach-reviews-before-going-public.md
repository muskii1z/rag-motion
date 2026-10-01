# 0041. Both coach reviews before going public; Phase 2 as a separate project
**Date:** 2026-10-01 · **Step:** Pre-Phase 2 · **Status:** accepted

## Context
The developer shared their remaining to-do list to finish the project: more slang questions, the slang dictionary, a README rewrite, a final secrets check, then make the repo public and pin it. Two pieces of content are still unreviewed by the coach: the original 20 exercises (since Step 5) and the new AI-drafted program-design notes ([0039](0039-program-design-notes-from-general-practice-not-nsca.md)). Both already appear in answers.

## Options considered
- **Go public now, with the "pending review" labels.** Pros: faster. Cons: a public repo would show AI-drafted content as the knowledge base of a coaching tool.
- **Review only the program-design notes first.** Pros: the notes are the newest and least checked content. Cons: the original 20 exercises stay unreviewed.
- **Both reviews before going public.** Pros: both pending items are checked by the coach before anyone outside sees them. Cons: going public waits on two reviews.

## Decision
The developer chose both reviews before going public. Approved order: (1) commit pending work, (2) coach reviews the program-design notes, (3) coach reviews the original 20 exercises, (4) add 1RM, RPE, and RIR to the slang glossary, (5) final evals (3 answer runs with the AI judge), (6) README rewrite, (7) pre-public checks, (8) the developer makes the repo public and pins it. The Phase 2 program generator becomes a separate next project.

## Tradeoffs
- Publishing waits on the coach's time.
- Splitting Phase 2 into its own project means this repo ends as a RAG system, not a program generator.
- The developer's own reason for choosing both reviews was not recorded.

## Revisit when
- A review finds errors that change eval keys: re-run the final evals after fixing them.
- The reviews stall and a public version is needed sooner.

## Update (2026-10-01): steps 1–7 done
Both reviews done ([0043](0043-coach-review-outcomes-original-20-and-program-design-notes.md)); glossary terms added; final evals run (52 questions, 3 answer runs with the judge: no forbidden citations 45/45, citations 96.7%, expected evidence 94.6%, coverage 91.4%); README rewritten; pre-public checks clean (90 commits, 0 key patterns, no tracked `.env` or raw sources, 55 tests pass). The first "Revisit when" signal fired: the broad jump review changed three answer keys, and the final evals were run after that change. Step 8 (make the repo public and pin it) is the developer's action.
