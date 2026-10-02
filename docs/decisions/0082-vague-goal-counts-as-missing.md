# 0082. A goal that only restates the request counts as missing
**Date:** 2026-10-02 · **Step:** Phase 2 follow-up (gym detection, likes vs dislikes) · **Status:** accepted

## Context
The agent asks for any missing detail (goal, days, equipment, level) before building ([0052](0052-agent-building-tools-refuse-until-profile-complete.md), [0067](0067-agent-asks-only-when-something-is-missing.md)). "Missing" is decided by code from the profile the LLM reader returns. For "I want a workout program", the reader set `goal = "workout program"`. Code then saw a goal, so the agent asked about days, equipment, and level but not the goal. The eval client `missing-everything` failed its "question mentions the goal" expectation in 2 of 3 runs.

## Options considered
- **Tell the reader not to fill the goal from the request.** Pros: fixes it at the source. Cons: depends on the model following a prompt line; the reader has ignored similar lines before ([0077](0077-a-gym-mention-always-means-all-equipment.md)).
- **Check the goal in code.** Pros: deterministic (same result every time). Cons: only catches the phrasings the pattern lists.

## Decision
`VAGUE_GOAL` in `src/ragmotion/program.py` matches goals that only restate the request: an optional "a/an/my", optional "new", optional "workout/training/exercise/gym/fitness/strength", then "program/programme/routine/plan/workout/split". `missing_for_program` treats such a goal as missing. Tested with 5 vague goals. In the final eval, `missing-everything` met all expectations 3/3.

## Tradeoffs
- A pattern, not judgment: "a strength program" counts as vague, though it hints at a goal (get stronger). The agent will ask, which costs one question.
- Vague goals the pattern doesn't list ("something to get in shape") still count as known.

## Revisit when
- A client gives a real goal and gets asked for it anyway.
- The eval or live use shows another vague goal slipping through.
