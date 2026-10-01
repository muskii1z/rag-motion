# 0047. Agent loop guardrails: refuse repeats, nudge after 3 searches, force submit after 10 tool calls
**Date:** 2026-10-01 · **Step:** Phase 2, step 1 · **Status:** accepted

## Context
In run 1, turn 2, the agent (Gemini 2.5 Flash-Lite) made 7 `find_exercises` calls, then 8 `search_sources` calls including exact repeats, and never called `submit_program`. It ended at the 15-step cap with "The agent didn't finish within 15 steps." Cost $0.0025, no program.

## Options considered
- **Prompt only.** Tell it to search 2–3 times and never repeat. Pros: no code. Cons: the prompt-rule ceiling on a small model ([Prompt rules have a ceiling](../concepts.md#prompt-rules-have-a-ceiling-especially-on-small-models)).
- **A stronger model.** Pros: may loop less. Cons: cost; the model choice was kept ([0048](0048-agent-keeps-gemini-2-5-flash-lite-compare-models-later.md)); no guarantee.
- **Code guardrails plus the prompt line.** Pros: the loop always ends with a program; cheap. Cons: the forced program may be built on fewer searches than ideal.

## Decision
Code guardrails, plus a prompt line ("Two or three searches are enough; never repeat a search"):
- A repeated search (same query, case-insensitive) returns "Already searched; use the earlier results."
- After 3 distinct searches, a system message: "You have enough sources. Submit the program now."
- After 10 tool calls (`FORCE_SUBMIT_AFTER`), `tool_choice` forces `submit_program`.
- `MAX_STEPS = 15` stays as the hard cap.

Run 2 after the change: 7 + 3 tool calls, then submit, $0.0012, a complete 3-day program.

## Tradeoffs
- A program for a client that needs many patterns could be forced out before every pattern was searched (7 patterns already use 7 of the 10 calls).
- Repeat refusal only catches identical queries; reworded repeats still count as new searches.
- The thresholds (3, 10, 15) were set by judgment after one failed run, not measured.

## Revisit when
- The step 4 test set shows forced submits with missing patterns: raise `FORCE_SUBMIT_AFTER`, or let `find_exercises` take several patterns per call.
- A model change makes the agent finish on its own reliably.

## Update 2026-10-01 (Phase 2, step 2): more loop guardrails
- `MAX_STEPS` raised from 15 to 18 (the reason isn't recorded). New `MAX_SUBMISSIONS = 3`: the checker can send a program back up to 3 times ([0051](0051-program-checker-in-code-exact-fixes-three-submissions.md)).
- `tool_choice` now also forces `submit_program` right after a checker rejection, because the agent had asked the client to fix its program.
- An empty model reply gets one nudge ("Your last reply was empty. Call a tool, or answer the client."), then the turn ends with "The program builder didn't respond. Please try again."
- Building tools refuse until the client's details are known ([0052](0052-agent-building-tools-refuse-until-profile-complete.md)).
- Not recorded: whether the 10-call forced submit fired in any Gemini 2.5 Flash run.
