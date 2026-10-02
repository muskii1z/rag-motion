# 0051. Program checks in code, with exact fixes, up to 3 submissions, failures shown
**Date:** 2026-10-01 · **Step:** Phase 2, step 2 · **Status:** accepted

## Context
Step 1's first finished program passed the schema check and still broke coaching rules the prompt stated: 7 exercises a day for a beginner (the prompt says 4–6) and a plank in reps instead of a timed hold. A schema only checks shape. Something had to check content, and decide what happens when a program fails.

## Options considered
- **Firmer prompt rules.** Pros: no code. Cons: the prompt already said 4–6 and was ignored ([Prompt rules have a ceiling](../concepts.md#prompt-rules-have-a-ceiling-especially-on-small-models)).
- **The model checks its own program.** Pros: flexible. Cons: it can "decide" a check passed when it didn't, the risk named in [0045](0045-program-builder-guided-agent-with-code-guardrails.md).
- **Checks in code, failures sent back as a list of failed rules.** Tried first. Flash-Lite resubmitted the same mistakes 3 times.
- **Checks in code, each failure with an exact fix instruction.** For example "'Day 1' has 7 exercises: remove 1", or "change reps to a time such as '20-30 s' on every day".

## Decision
`check_program()` in `src/ragmotion/program.py` runs up to 16 checks (days, catalog, equipment, level, excluded movements, patterns on 2+ days, core or carry, exercises per day, repeats, sets/reps/rest, timed holds and carries, citations from the agent's own searches, health-professional reminder when health words appear). A rejection goes back to the agent with the failed checks and `exactly_what_to_change`. The agent may submit up to 3 times (`MAX_SUBMISSIONS`). After that the program is returned with its checks attached and `passed_checks = False`, so the client sees the failures.

## Tradeoffs
- Only rules someone wrote down are checked. A program can pass all 16 and still be one a coach would reject.
- A failed program can still reach the client after 3 tries, labeled with its failures rather than withheld.
- Each retry costs another model call and adds time (Flash-Lite: 15–21 s per program).
- Rules can misfire: the referral rule first fired on "little lifting experience" until it was tied to health words.

## Revisit when
- Step 4's test clients show programs passing all checks that a coach would still reject: add the missing rule.
- A check fires falsely on test clients.
- The coach approval step (human review) is built; decide whether a failed program should be withheld instead of shown.

## Update 2026-10-01 (step 2 fixes)
- The referral check now uses `profile.health_issues` (read by the profile AI) plus a broad backup word pattern on context notes ([0054](0054-health-issues-read-by-profile-ai-plus-broad-backup-pattern.md)).
- A main pattern with no usable exercises for the client isn't required ([0056](0056-patterns-with-no-usable-exercises-are-not-required.md)). The pull check could never pass for a bodyweight client.

## Update 2026-10-01 (Phase 2 quality pass, Q1)
- The "Revisit when" signal happened: the developer's program passed 15/15 and a coach would still change it (chest 3 sets a week, glute bridge + hip thrust on one day). Three quality checks were added ([0057](0057-program-quality-checks-weekly-sets-patterns-day-labels.md)): one exercise per pattern per day, day names match their exercises, and a weekly-set minimum per major muscle group. Weekly sets are now counted in code and shown with every program.

## Update 2026-10-02 (after P4 and the structure fix)
- "Core or carry at least once a week" was the only check with no fix text (flagged in the P4 build-log entry). It now names up to 4 core or carry exercises the client can use (commit `4506ba2`).
- Programs are now assembled by code from slot picks ([0073](0073-code-builds-the-program-skeleton-agent-fills-slots.md)). Bad picks (empty slot, slot filled twice, not an option, same exercise twice in a day) are sent back with the allowed options *before* the checker runs. A malformed submission is also sent back before the checker and isn't counted as one of the 3 submissions; this explains the "4 submit steps" in one P4 run. In the final eval, 26 of 30 programs were accepted on the first submission.
