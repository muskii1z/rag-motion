# 0079. Eval expectations for favorite lifts and full days
**Date:** 2026-10-02 · **Step:** Phase 2 follow-up (full-gym detection) · **Status:** accepted

## Context
The program eval ([0070](0070-program-eval-12-clients-code-scored-coach-review-sheet.md)) passed `loves-back-squats` in 9 of 9 runs while every program had no back squat, no hip thrust, and 3-exercise upper days. Its expectations only asked whether the program passed the checker and had no referral. The checker verifies a program against the profile; if the profile is wrong, a wrong program passes. The bug was found by the scribe reading the saved programs, not by any score.

## Options considered
- **Rely on the coach's review sheet.** Pros: catches everything a coach would notice. Cons: slow, and only as often as the coach reads it; this bug passed a whole run unnoticed.
- **Add a checker rule.** Pros: runs in the app too. Cons: the checker can't know what the client asked for beyond the (possibly wrong) profile, which is the problem.
- **Add eval expectations tied to what the client said.** Pros: scored in code every run; written per client from the conversation, independent of the profile reader. Cons: one expectation per lesson learned; doesn't generalise by itself.

## Decision
Two new expectation types in `evals/run_program_eval.py`: `includes_any` (the program includes at least one of these slugs) and `min_exercises_per_day` (every day has at least N exercises). `min_exercises_per_day: 4` is set on the four full-gym clients (`full-gym-intermediate-4day`, `youth-soccer`, `sore-knee`, `loves-back-squats`), and `loves-back-squats` has `includes_any: [barbell-back-squat, dumbbell-hip-thrust]`. First run with them: 36/36 expectations met.

## Tradeoffs
- `includes_any` passes if either favorite appears; a program that drops one of the two would still pass. All 3 runs had both.
- 4 per day is a judgment for full-gym clients, not a coach-set number.
- Like every expectation, these only catch the failures someone thought to write down.

## Revisit when
- The coach's review finds another program that passes every expectation but misses the request.
- A client names two lifts and gets only one (then require all, not any).

## Update 2026-10-02 (likes vs dislikes)
Two more expectation types in `evals/run_program_eval.py`: `includes_all` (the program includes every one of these slugs) and `excludes` (it includes none of them). `loves-back-squats` now uses `includes_all: [barbell-back-squat, dumbbell-hip-thrust]`, which closes the "any passes with one favorite" weakness above. Two new clients use `excludes`: `home-dumbbells-not-gym` (no barbell, machine, or cable exercises) and `hates-deadlifts` (none of the four deadlifts). 14 clients in total. Final run: 42/42 expectations met.
