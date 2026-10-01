# 0039. Program-design notes drafted from general practice, not attributed to NSCA, pending coach review
**Date:** 2026-10-01 · **Step:** Pre-Phase 2 · **Status:** accepted

## Context
The plan listed "coach's notes on NSCA Essentials ch. 18–19" as a program-design source. The developer asked Claude to "make the notes". Claude has no access to the book. Earlier NSCA notes were written from locally extracted position-statement text ([0017](0017-knowledge-source-licensing-policy.md)), so their NSCA citations could be checked. Here there was no text to check against.

## Options considered
- **Write "NSCA notes" anyway.** Pros: matches the original plan; NSCA carries weight with coaches. Cons: a false citation. The notes would claim a source nobody had read, the same failure the project's citation checks exist to prevent, and the same kind of error as the web tool that invented figures from an unreadable PDF.
- **Draft notes from widely taught principles, labeled honestly.** Pros: gives the system program-design structure (needs analysis, splits, session order, progression, deloads) that the research papers don't; the label is true. Cons: no external authority behind them; AI-drafted text of uncertain accuracy until reviewed.
- **Wait for the coach to write notes from the book.** Pros: real NSCA grounding. Cons: no program-design notes until then.

## Decision
Claude drafted `data/notes/program-design.md` from widely taught program-design principles. Its `author` line says "Drafted with AI assistance from widely taught program-design principles; not copied from or checked against any book; pending review by M. Saraswat". Registered as `notes-program-design` (group A, project-owned), tagged `adults`, 3 passages.

## Tradeoffs
- The notes are live in retrieval before review. `pop-beginner-adult` already ranks 2 of their passages ahead of the Guidelines, and `prog-frequency`'s answer cited them. Unreviewed text can reach answers now.
- Citations to these notes point to "project notes", not an authority a reader can check.
- The coach's review is the only accuracy check. The notes' sources line asks the coach to check them against their program-design textbook.

## Revisit when
- The coach reviews the notes (planned before going public, [0041](0041-both-coach-reviews-before-going-public.md)): update the `author` line, fix errors, and decide whether any eval key should accept them.
- The coach writes notes from the NSCA chapters themselves: those can cite NSCA.
- The draft notes keep outranking primary sources on questions they shouldn't answer.
