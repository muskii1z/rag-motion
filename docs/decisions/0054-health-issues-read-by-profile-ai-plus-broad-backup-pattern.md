# 0054. Health issues are read by the profile AI, with a broad word pattern as backup
**Date:** 2026-10-01 · **Step:** Phase 2, step 2 fixes · **Status:** accepted

## Context
The program checker requires a reminder to see a health professional when the client mentions a health issue (the referral check). It first matched health words as parts of text, which fired on "coming back to lifting". The whole-word fix (`d5050cb`) stopped that, but a probe found it missed "hurt my back", "my back hurts", "tweaked my back", "strained my hamstring", and "herniated disc", and still fired on "hip thrusts" and "shoulder press". People describe pain in too many ways for one word list to catch. For a safety reminder, a miss (no reminder for a real injury) is worse than a false alarm (a reminder nobody needed).

## Options considered
- **Keep tuning one word list.** Pros: simple, no model. Cons: every tightening adds misses, every loosening adds false alarms; the last fix traded one for the other.
- **Only the AI reads health issues.** A new profile field filled by the profile reader. Pros: understands casual phrasing ("tweaked my back"). Cons: the reader is an LLM and can miss things; in this same step it guessed equipment in 1 of 3 reads.
- **Both: the AI reads health issues, and a deliberately broad word pattern checks the context notes as a backup.** Pros: two independent chances to catch an issue. Cons: the broad pattern brings back false alarms on exercise names.

## Decision
Both. `ClientProfile.health_issues` records injuries, pain, conditions, surgeries, and pregnancy in the client's words, never a diagnosis. The checker treats as health items everything in `health_issues` plus any context note matching a broad `HEALTH_PATTERN` (pain, hurt, strain, tweak, disc, surgery, body parts including "back", except in "coming/getting back to/into/in"). The pregnancy guard checks `health_issues` too.

## Tradeoffs
- False alarms are accepted on purpose: a context note like "wants to do hip thrusts" or "back squats are my favorite" matches the backup pattern (found by a scribe probe). Each costs a reminder sentence or one retry.
- Detection now depends partly on an LLM read, which varies between runs; how often it misses isn't measured.
- One more field the profile reader must fill, so a slightly longer prompt.

## Revisit when
- Step 4's test clients show the reader missing health issues the backup also misses.
- False alarms show up often enough on real preferences (exercise names) to annoy users or cost retries.
- The coach approval step is built and could take over the decision about when to refer.
