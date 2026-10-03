# 0084. The weekly-set minimum is told to the agent up front, and the check stays strict
**Date:** 2026-10-02 · **Step:** Phase 2 follow-up (gym detection, likes vs dislikes) · **Status:** accepted; coach question answered by [0085](0085-older-adult-weekly-set-minimum-from-the-sources.md)

## Context
The checker requires a minimum number of weekly sets per major muscle group: 6 for muscle or strength goals, 4 otherwise, halved for one-session weeks ([0057](0057-program-quality-checks-weekly-sets-patterns-day-labels.md), [0075](0075-weekly-set-minimum-halved-for-one-session-weeks.md)). The system prompt already stated the general rule. Still, in an 8-run probe of the `older-adult-new` client (70, new to exercise, get stronger, 2 days, dumbbells and bands), 7 of 8 programs gave 2 sets per exercise, were rejected with "at least 6 weekly sets per major muscle group", and only then were fixed.

## Options considered
- **Lower the minimum for older beginners.** Pros: fewer rejections. Cons: changes a coaching standard to suit the model, with no source or coach input.
- **Leave it; the checker sends it back and the agent fixes it.** Pros: no change; the program is right in the end. Cons: an extra model call (time and cost) on most programs for this client.
- **Tell the agent this client's number when it gets the plan, and keep the check.** Pros: the target is in front of the model when it chooses sets; the check still guarantees it. Cons: one more field in the tool result.

## Decision
`get_plan_skeleton` now returns `weekly_set_minimum_per_muscle_group` (computed by `weekly_set_minimum(profile)`), and the prompt says to choose sets to reach it. The minimum and the check are unchanged. Result for `older-adult-new`: accepted on the first submission 1/8 → 4/8 in the probes; every program passes after at most one fix. Across the final eval, 34 of 36 programs were accepted on the first submission.

## Tradeoffs
- Half the older-adult programs still need a second submission, so the extra call is reduced, not gone.
- The minimum for this client hasn't been confirmed by the coach.

## Revisit when
- The coach answers: is 6 weekly sets per muscle group right for a 70-year-old beginner on 2 days?
- First-try acceptance drops, or a client type keeps failing the same check.

## Update 2026-10-03
The coach answered: "use the sources". [0085](0085-older-adult-weekly-set-minimum-from-the-sources.md) sets the minimum for clients 65 and older from the NSCA older-adults notes: 1 set per muscle group per session for beginners, 2 otherwise, never above the general minimum. The 70-year-old 2-day beginner's minimum went from 6 to 2. Stating the number up front (this decision) stays. First-try acceptance for that client in probes: 5 of 6; in the next eval, 3 of 3.
