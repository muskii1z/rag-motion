# 0028. Before/after comparisons use the average of 3 runs per version
**Date:** 2026-09-28 · **Step:** Phase 1F, F6 · **Status:** accepted

## Context
F6's job was the headline number for Phase 1F: how much the equipment and age-group filters changed the answers, on the same 40 questions. Until F5, every comparison used one answer-eval run per version, and suspicious single failures were re-run by hand (F3 + F4: one question, 3 re-runs; F5: one manual re-run).

In F6 that stopped being enough. Right after the coach changed three coverage keys to `partial`, a single filtered run had bands-only and one-kettlebell claiming `full`. In F5 they had claimed `partial`. Nothing in the system had changed. The answering model uses temperature 0.2, so its answers are sampled and vary between identical runs. A single run could make the filters look better or worse by chance, and this number goes in the README.

## Options considered
- **One run per version.** Pros: cheapest (about 10 cents a run) and fastest. Cons: coverage claims flip between runs, so a one-question difference means nothing; the F5 "coverage drop" had already shown how easy it is to misread one run.
- **One run per version, re-run only the questions that fail.** What F3 + F4 did. Pros: cheap; targets the doubt. Cons: only checks failures, not lucky passes; the headline totals are still single-run numbers.
- **3 runs per version, report totals.** Pros: shows the spread; a difference that appears on every run can be trusted; still cheap (about $0.60 for all 6). Cons: 3x the cost and time; 3 runs is still a small sample.
- **5 or more runs per version.** Pros: tighter numbers. Cons: more cost and time, and with the judge's rate limit, slower still. Not needed to see the one effect that matters here.

## Decision
The headline before/after uses 3 runs of `--no-filters` and 3 runs with filters, graded against the same final key, reported as totals (for example 27/39 and 39/39) and percentages. A difference counts only if it is consistent across runs; overlapping run ranges are reported as unchanged.

Result: no forbidden advice 9, 9, 9 of 13 without filters (69%) vs 13, 13, 13 with filters (100%). Citations 98% vs 98%, expected evidence 98% vs 98%, coverage 88% vs 91%: unchanged within noise. See the [F6 build-log entry](../build-log.md#phase-1f-f6-re-run-the-eval-compare-before-and-after-the-filters-update-the-readme).

## Tradeoffs
- Three times the cost and time per comparison (about $0.60 instead of $0.20 for before plus after).
- Running the 6 evals in parallel to save time hit the AI judge's rate limit (20 requests per minute for new OpenRouter accounts on `anthropic/claude-sonnet-5.5`), and most judge verdicts were lost. So the labeling rules have no 3-run comparison. The judge now retries ([0025 update](0025-ai-judge-for-coach-labeling-rules.md)), and evals should not run many at once.
- 3 runs still can't separate small effects (a point or two of coverage) from noise. It only confirms large, consistent ones.

## Revisit when
- A change's expected effect is small (a few questions): use more runs, or more questions.
- Eval cost matters (many more questions, or a pricier answering model): go back to single runs for routine checks and keep repeats for headline numbers.
- The answering model runs at temperature 0 and repeats prove stable: fewer runs may be enough.
- LangSmith's built-in repetitions are adopted: this could move from separate runs to one experiment with repeats (not tried).
