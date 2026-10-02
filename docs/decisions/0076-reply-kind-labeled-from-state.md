# 0076. A text reply is labeled a question when details are missing
**Date:** 2026-10-02 · **Step:** Phase 2 structure fix (after P4) · **Status:** accepted

## Context
Each agent turn ends with a kind: "program", "question", or "message". The kind was set by how the agent replied: through the `ask_user` tool meant "question", plain text meant "message". In the eval run after the no-bodyweight fix, `missing-everything` ("I want a workout program") came back as "message" in 3/3 runs. The agent asked for goal, days, and equipment in plain text instead of calling `ask_user`. The words were right; the label was wrong.

## Options considered
- **A prompt rule ("always use ask_user to ask").** Pros: no code. Cons: another prompt rule the model can skip.
- **Force `ask_user` when details are missing.** Pros: one path. Cons: extra model call; overrides a reply that was already fine.
- **Label from state.** Code already knows whether details are missing (`missing_for_program(profile)`). If they are, a text reply is a question.

## Decision
In `run_turn`, a plain text reply is labeled "question" when `missing_for_program(profile)` returns anything, otherwise "message". Result: `missing-everything` 3/3 back to "question"; the final eval met 36/36 expectations.

## Tradeoffs
- A text reply while details are missing that isn't really a question (for example a refusal) would be labeled a question.

## Revisit when
- The page or the eval needs to tell a question apart from other text sent while details are missing.
