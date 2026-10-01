# 0056. Movement patterns with no usable exercises aren't required
**Date:** 2026-10-01 · **Step:** Phase 2, step 2 fixes · **Status:** accepted

## Context
The checker requires squat or lunge, hinge, push, and pull each on 2 or more days ([0051](0051-program-checker-in-code-exact-fixes-three-submissions.md)). In the developer's live run, the client was treated as bodyweight only, and the catalog has no pull exercise usable without equipment (`find_exercises` returned pull 0). So the pull check could never pass for that client: the agent spent 3 submissions and the program was shown with a failed check. A rule no answer can satisfy fails forever and burns retries.

## Options considered
- **Keep the rule as is.** Pros: simple. Cons: bodyweight clients always fail; every run uses all 3 submissions.
- **Add bodyweight pull exercises to the catalog.** Pros: the rule becomes satisfiable. Cons: content work that needs coach review; doesn't cover other equipment combinations.
- **Don't require a pattern when nothing in the catalog fits this client.** Pros: the rule only asks for what's possible. Cons: the program lacks that pattern, so the agent must explain the gap.

## Decision
When no usable catalog exercise exists for a main pattern, given the client's equipment and limits, that check passes with the detail "no exercises available with this equipment". The agent's prompt says to leave the pattern out and say in the rationale which equipment would add it (pull-up bar or resistance bands for pull).

## Tradeoffs
- A program can pass without a pull movement, which a coach would normally want.
- Explaining the gap is a prompt instruction only; no check confirms the rationale says it.
- The check still counts as "passed" in the X/Y total, which can look better than the program is.

## Revisit when
- The catalog gains bodyweight exercises for a missing pattern (then the rule applies again automatically).
- The coach wants such programs flagged rather than passed.
- Programs regularly ship without the explanation in the rationale.
