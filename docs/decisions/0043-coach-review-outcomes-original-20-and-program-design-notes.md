# 0043. Coach review outcomes: original 20 exercises and program-design notes
**Date:** 2026-10-01 · **Step:** Finishing Phase 1F (going public) · **Status:** accepted

## Context
[0041](0041-both-coach-reviews-before-going-public.md) made two coach reviews a gate before going public: the original 20 exercises (AI-drafted in Step 5, "pending coach review" since) and the AI-drafted program-design notes ([0039](0039-program-design-notes-from-general-practice-not-nsca.md)). Both were already reaching answers.

For each item the coach had to decide: keep as written, or change. Changes to exercise data can also change the eval's answer keys.

## Options considered
For each flagged exercise, the options were to keep Claude's draft or take the coach's change:
- **Broad Jump: intermediate (draft) or beginner.** Beginner adds a jump to beginner lists. The coach: beginner.
- **Inverted Row: barbell only (draft) or barbell + rack.** Barbell + rack is what the movement actually needs, and the equipment filter then drops it for anyone without a rack. The coach: barbell + rack.
- **Farmer Carry: drop glutes as a main muscle, or keep them.** The coach kept them: "it's really a full body workout". Its `body_region` was already `full`.

For the answer keys after the broad jump change:
- **Leave the keys as they were.** Cons: the key would forbid a beginner exercise for beginners, punishing correct answers.
- **Update every affected key, but keep the coach's population rules.** The coach's call.

For the notes: approve, edit, or rewrite the 11 claims (loads and rest by goal, beginner sets, frequency, splits, session order, the progression rule, deloads, progressions). The coach: "those look fine".

## Decision
- Broad Jump → beginner. Inverted Row → barbell + rack. Farmer Carry unchanged. The other 17 unchanged. All 42 exercises marked "reviewed by M. Saraswat"; re-seeded and re-embedded.
- Keys: broad jump moved from forbidden to acceptable in `constraint-beginner-home`, added to acceptable in `pop-beginner-adult` and `pop-youth-start`. Still forbidden for older adults (coach: no jumps).
- Notes approved as written; `author` line, sources line, and manifest title and attribution updated to "reviewed by M. Saraswat, 2026-10-01". Re-chunked and re-embedded (278 passages).

## Tradeoffs
- The keys changed, so scores before and after this commit are graded by different rulers ([When the answer key changes, the scores change](../concepts.md#when-the-answer-key-changes-the-scores-change)). The final eval was run after the change.
- The notes are reviewed by one coach against their own knowledge, not checked against a published text. Citations to them still point to "project notes".
- Exercise level stays a label, not a filter, so the broad jump change affects keys and answers but not search.

## Revisit when
- A second expert disagrees with a level or equipment call.
- Level becomes a filter: the beginner/intermediate labels then decide what search returns, and borderline calls like the broad jump matter more.
- The notes are extended or the coach writes notes from the NSCA chapters.
