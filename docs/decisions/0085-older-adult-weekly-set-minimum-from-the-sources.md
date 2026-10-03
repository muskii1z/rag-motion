# 0085. The weekly-set minimum for clients 65 and older comes from the sources: 1 set per group per session for beginners, 2 otherwise
**Date:** 2026-10-03 · **Step:** Phase 2 follow-up 2 (coach answers applied) · **Status:** accepted (answers the coach question left open in [0084](0084-weekly-set-minimum-stated-up-front.md))

## Context
The program checker requires a minimum number of weekly sets per major muscle group: 6 for muscle or strength goals, 4 otherwise, halved for one-session weeks ([0057](0057-program-quality-checks-weekly-sets-patterns-day-labels.md), [0075](0075-weekly-set-minimum-halved-for-one-session-weeks.md)). The `older-adult-new` eval client (70, new to exercise, get stronger, 2 days, dumbbells and bands) kept failing it: the agent gave 2 sets per exercise, and the checker sent the program back. Stating the target up front ([0084](0084-weekly-set-minimum-stated-up-front.md)) raised first-try acceptance from 1/8 to 4/8, but nobody had checked whether 6 sets was the right number for this client. The scribe asked the coach. The coach's answer (2026-10-03): "use the sources".

What the sources in the system say:
- **`notes-nsca-older-adults-1`** (coach-reviewed notes on the NSCA position statement on older adults), for healthy older adults: frequency "2–3 sessions per week per muscle group"; "beginners and frail clients start with 1 set and build to 2–3"; "1–2 multijoint exercises per major muscle group".
- **`pag2-77`** (Physical Activity Guidelines, page 72): older adults should do muscle-strengthening activities "at least 2 days a week" that "involve all the major muscle groups". No number of sets.

## Options considered
- **Keep 6 sets for everyone.** Pros: no change; the checker already enforces it. Cons: no source supports it for an untrained 70-year-old; the sources say beginners start at 1 set. It also costs a rejected submission on many runs.
- **The coach picks a number by judgment.** Pros: quick. Cons: the coach asked for the sources instead, and a judgment number would be hard to defend.
- **Derive the minimum from the sources.** Pros: every number traces to a passage the system itself retrieves; the code comment cites the passage id. Cons: the notes describe a starting point ("start with 1 set and build to 2–3"), so the floor is a starting dose, not a target.

## Decision
In `weekly_set_minimum(profile)` (`src/ragmotion/program.py`), for clients aged 65 or older: the minimum is 1 set per muscle group per session for beginners and 2 per session otherwise, times sessions per week, and never above the general minimum. The code comment cites `[notes-nsca-older-adults-1]`. Adults under 65 and clients with no age are unchanged.

| Client | Before | After |
|---|---|---|
| 70, beginner, 2 days, get stronger | 6 | **2** |
| 70, intermediate, 2 days, get stronger | 6 | 4 |
| 70, intermediate, 3 days, build muscle | 6 | 6 (capped at the general minimum) |
| 30, beginner, 2 days, get stronger | 6 | 6 |
| no age, beginner, 3 days, general fitness | 4 | 4 |

These five cases are a parametrized test in `tests/test_program_checker.py`.

Results:
- Probe of the 70-year-old 2-day client: accepted on the first submission in 5 of 6 runs (was 1/8 before [0084](0084-weekly-set-minimum-stated-up-front.md), 4/8 after). One of the 6 runs ended "didn't respond" after 2 submissions; it was not reproduced in 8 more runs, all of which ran with no error.
- Eval (`programs-20261003-112019`): 42/42 expectations, 36/36 programs pass every check, 0 errors, and every program was accepted on its first submission (scribe count from the saved file). The 70-year-old's run 1 program used 3 sets on every exercise, above the new floor.

## Tradeoffs
- The minimum is now a floor at the start of training, not a goal. A program with 1 set per group per session passes, even though the same source says to build to 2–3. Progression over time isn't modeled.
- The age line is a single number, 65. The brief doesn't say why 65; the NSCA note frames its intensity target for adults "older than 60". A 64-year-old beginner still gets the general minimum of 6.
- The rule covers "beginner" vs everything else. "Frail" isn't a field the profile reader fills, so frail clients who aren't labeled beginners get 2 per session.

## Revisit when
- The program builder adds progression across weeks (then the floor can rise from 1 toward 2–3 sets as the source describes).
- The coach wants a different age line, or a source gives a set number for older adults that differs from these notes.
- An older-adult program that passes looks too light to the coach in the review sheet.
