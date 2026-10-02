# 0057. Program-quality checks in code: weekly sets, one per pattern per day, day labels
**Date:** 2026-10-01 · **Step:** Phase 2 quality pass, Q1 · **Status:** accepted

## Context
The developer's 4-day upper/lower program passed all 15 checks and was still weak on a coach's review: chest got 3 sets a week, glute bridge and hip thrust sat on the same day, volume was uneven, and the rationale claimed "10–13 sets per muscle group" that nothing had verified. The checker ([0051](0051-program-checker-in-code-exact-fixes-three-submissions.md)) covered safety and structure, not quality. The developer wanted programs that are "really well researched and informed".

## Options considered
- **Prompt rules only.** Ask the agent for balanced volume and no near-duplicates. Pros: no code. Cons: the model already claimed balanced volume and was wrong ([Prompt rules have a ceiling](../concepts.md#prompt-rules-have-a-ceiling-especially-on-small-models)).
- **Trust the model's stated volume.** Pros: nothing to build. Cons: chest had 3 sets against a claim of 10–13.
- **Quality checks in code, with exact fixes.** Pros: the same pattern that already works for structure; numbers are real. Cons: more rejections, retries, and cost; rules only as good as the data they read.

## Decision
Three new checks in `check_program()` (`src/ragmotion/program.py`), each with an exact fix:
- **One exercise per movement pattern per day** for squat, lunge, hinge, push, pull (core, carry, isolation exempt). Developer's choice.
- **Day names match their exercises**: "upper" days have no squat, lunge, or hinge; "lower" days have no push or pull.
- **At least N weekly sets per major muscle group** (chest, back, shoulders, quads, glutes/hamstrings), counted in code from the catalog's primary muscles with the lower bound of a range. N = 6 for muscle or strength goals, 4 otherwise (developer's choice). Only groups the client's usable exercises can reach are required.

Code attaches the weekly-set table to every program; the prompt tells the agent not to state totals.

## Tradeoffs
- More rejections: in 3 replays, 0/3 passed every check, at $0.0038–0.0076 and 35–67 s, against $0.0015 and 19 s for a first-try program.
- One per pattern per day conflicts with upper/lower practice (horizontal + vertical press on one day). To be fixed with direction labels ([0058](0058-push-and-pull-get-horizontal-vertical-labels.md)), not by loosening the rule.
- The volume count is coarse: an exercise counts fully toward every group its primary muscles touch; arms aren't counted.
- Day-name matching only reads the words "upper" and "lower".

## Revisit when
- Direction labels land in Q2 (update the one-per-pattern rule).
- The P4 program eval shows the coach disagreeing with the volume count or the minimums.
- Retry cost or failure rate stays high after Q2.

## Update 2026-10-01 (Phase 2 quality pass, Q2): direction and more day names
- The one-per-pattern check now counts push and pull by direction (check name: "one exercise per movement pattern (and push/pull direction) per day"); see [0058](0058-push-and-pull-get-horizontal-vertical-labels.md), [0060](0060-machine-and-cable-equipment-and-a-direction-column.md).
- Day names now cover upper, lower, leg(s), push (no lower body, no pull) and pull (no lower body, no push), matched as whole words.
- Replays: 0/3 passing every check before Q2; 2/3 after (18/18 checks, first try, $0.0016, 16 s); 4/6 after the narration fix, $0.0017–0.0059.

## Update 2026-10-02 (Phase 2, P3): stated totals rejected
The prompt's "don't state totals" was ignored in the first browser test ("glutes/hamstrings: 15" vs 21 counted by code). A checker rule now rejects per-muscle set totals in the text; research citations are allowed. The page shows code's counts as bars with the minimum marked. See [0066](0066-no-weekly-set-totals-in-program-text.md).
