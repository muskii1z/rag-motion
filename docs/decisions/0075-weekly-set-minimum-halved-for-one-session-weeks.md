# 0075. Weekly-set minimum halved for one-session weeks
**Date:** 2026-10-02 · **Step:** Phase 2 structure fix (after P4) · **Status:** accepted (coach to confirm)

## Context
The weekly-set check requires at least 6 hard sets per major muscle group for muscle or strength goals (4 otherwise; [0057](0057-program-quality-checks-weekly-sets-patterns-day-labels.md)). With one session a week, the 1-day layout (squat, hinge, horizontal push, horizontal pull, core) can't reasonably hold 6 sets for every group. A rule every valid input can't pass burns every retry ([Rules must be satisfiable](../concepts.md#rules-must-be-satisfiable-every-valid-input-must-be-able-to-pass)).

## Options considered
- **Keep the minimum.** Pros: one rule for everyone. Cons: one-day programs fail or get bloated sessions.
- **Drop the check for one-day weeks.** Pros: simple. Cons: no floor at all.
- **Halve the minimum for one-day weeks.** Pros: a floor that fits one session. Cons: a judgment call, not from a source.

## Decision
`weekly_set_minimum` returns half (6 → 3, 4 → 2) when `sessions_per_week` is below 2. The all-combinations test passes with this for every client at 1 day.

## Tradeoffs
- The number isn't from the research or the coach; it's a judgment call made in code.
- A one-day client can pass with fewer weekly sets than the research minimum the coach set for everyone else.

## Revisit when
- The coach reviews it and sets a different number or rule.
- One-day programs show up in real use often enough to deserve their own layout.
