# 0030. Answer prompt stays without the coach's presentation rules (three versions measured, reverted)
**Date:** 2026-09-28 · **Step:** Phase 1F, F7b · **Status:** proposed (recommended to the developer; their confirmation of the revert is pending)

## Context
The coach has four presentation rules for answers: group exercises by muscle group; label intermediate or advanced exercises for beginners; label bodyweight exercises when the person states their equipment; label exercises that train the target muscle only as a secondary muscle. Since F2, an AI judge grades answers on these rules ([0025](0025-ai-judge-for-coach-labeling-rules.md)). F7a found that the answer prompt (`ANSWER_SYSTEM_PROMPT` in `src/ragmotion/rag.py`) never states them, which is why a bigger k didn't fix grouping ([Matching the fix to the failure](../concepts.md#matching-the-fix-to-the-failure-filters-k-prompt-instructions)).

The obvious fix was to add the rules to the prompt. The developer asked whether that would box the system in. It wouldn't (a few removable sentences), but it could make rules fire where they don't fit, or make answers longer. So it was measured.

F7b tried three versions, 3 answer-eval runs each (semantic, filters on, k = 5, same dataset), against the 3 k = 5 runs from F7a with no rules ([build log](../build-log.md#phase-1f-f7b-experiment-with-the-coachs-presentation-rules-in-the-answer-prompt-reverted)). Totals over 3 runs:

| Check | No rules | v1 all four | v2 narrow grouping | v3 labels only |
|---|---|---|---|---|
| Citations valid | 120/120 | 120/120 | 116/120 | 120/120 |
| Coverage claim correct | 111/120 | 107/120 | 104/120 | 105/120 |
| Exercise completeness | 0.80 | 0.83 | 0.80 | 0.81 |
| No extra exercises | 87% | 81% | 83% | 81% |

The judge's rule scores rest on 0 to 4 applicable cases each, so no per-rule gain could be shown.

## Options considered
- **Keep v1 (all four rules).** Pros: answers used muscle-group headings; bodyweight labeled 4/4. Cons: the grouping rule padded focused answers (an overhead-press question got bench press, push-up, triceps extension, band pull-apart; an anti-rotation question got dead bug, which the coach says is not anti-rotation); coverage 111 → 107; no extras 87% → 81%; the beginner-adult answer still failed "covers all major muscle groups" with only 5 exercises.
- **Keep v3 (labels only, no grouping).** Pros: no grouping side effect; citations stayed 120/120. Cons: extras on the anti-rotation question in all 3 runs; coverage 111 → 105; the labeling cases rarely triggered, so no measurable gain.
- **(Tried and dropped) v2, grouping only for list questions.** Its narrowed condition didn't trigger on the beginner-adult question, so that answer stopped grouping at all; citations fell to 116/120 and coverage to 104/120.
- **Revert to the original prompt.** Pros: best coverage and "no extra exercises" of the four; no untested behavior shipped. Cons: the coach's style isn't enforced in answers.

## Decision
Revert the answer prompt to the original, with no presentation rules (recommended; developer confirmation pending). No version beat the baseline overall, and each one added extra exercises to focused answers or hurt coverage-claim accuracy.

## Tradeoffs
The coach's grouping and labeling style isn't enforced in answers yet. The judge's four rule checks will keep failing or rarely applying. About $0.90 of eval runs produced no shipped change, only the evidence for not shipping one.

## Revisit when
- **Labels move into code.** The labels are catalog facts (level, equipment, primary muscles), so the web page could show level and bodyweight badges next to cited exercises, deterministically, with no prompt change. Not built yet.
- **A stronger answer model** is tried. The lesson here is about `google/gemini-2.5-flash-lite` following extra instructions unreliably; a stronger model may follow them without side effects.
- **List questions get more than 5 exercises** (the F7a k decision, [0029](0029-exercise-k-stays-5-for-all-questions.md), changes). Grouping a full beginner list needs enough exercises to cover every muscle group.
- Any future prompt-rule attempt should be measured the same way: 3 runs, the same dataset, and a look at focused questions, not just the rule's own score.
