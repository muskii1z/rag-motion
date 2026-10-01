# 0044. README reports errored runs and rejected changes, not only the best numbers
**Date:** 2026-10-01 · **Step:** Finishing Phase 1F (going public) · **Status:** accepted

## Context
The README is the public front page. The final answer eval (52 questions, 3 runs) had 4 of 156 question-runs fail with an error: 3 timeouts while two runs hit the provider at the same moment, and 1 unreadable model reply after a retry. A clean table was one re-run away. Phase 1F had also built several changes that didn't help (LLM rewrite, hybrid and split search, 10 exercises per question, formatting rules in the prompt).

## Options considered
- **Re-run the failed questions until they pass, report only the clean totals.** Pros: tidy numbers. Cons: that's selecting results; it hides that the system can time out or get an unreadable reply, which a user would see.
- **Report the totals with errors excluded, and say so.** Pros: honest; the totals still describe the questions that ran. Cons: the denominators are uneven (152, 149, 83) and need explaining.
- **Show only kept changes.** Pros: a shorter README. Cons: hides what was tried and why it was rejected, which is most of the engineering.
- **Show a "what changed the numbers" table with kept and not-kept rows.** Pros: shows each change was measured before it was kept. Cons: longer; shows failures.

## Decision
The README states the 4 errored runs and their causes, excludes them from the totals, and doesn't re-run them. It shows a table of every measured change with a kept (✅) or not kept (❌) mark: filters ✅, glossary ✅, LLM rewrite ❌, hybrid / split ❌, 10 exercises ❌, prompt formatting rules ❌. It reports the final run set even though an earlier set (before the limit fix, 0 errors) scored about a point higher on some checks, because the final set measures the shipped system. Limitations name the rare unreadable reply (about 1 in 150).

## Tradeoffs
- The headline numbers are slightly lower than a cherry-picked version would be.
- The error rate (1 unreadable reply in 156) rests on a single event.
- A reader has to read more to understand uneven denominators.

## Revisit when
- Errors become frequent enough to change the conclusion: then they're a reliability problem to fix, not a footnote.
- The README gets new results: keep the same rule (report errors, keep rejected rows).
