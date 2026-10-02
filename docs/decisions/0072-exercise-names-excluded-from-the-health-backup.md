# 0072. Exercise names are excluded from the health backup pattern
**Date:** 2026-10-02 · **Step:** Phase 2, P4 · **Status:** accepted

## Context
Health issues are caught twice: the profile AI reads them into `health_issues`, and a deliberately broad word pattern, `HEALTH_PATTERN`, scans context notes as a backup ([0054](0054-health-issues-read-by-profile-ai-plus-broad-backup-pattern.md)). 0054 accepted that the backup would match exercise names like "back squats" and "hip thrusts". In the first P4 run that happened: for "I love back squats and hip thrusts", the AI correctly found no health issue, but the backup fired, so the client got a referral reminder for no reason and the program took 3 submissions.

## Options considered
- **Keep accepting the false alarm.** Pros: no risk of new misses. Cons: a client who names favorite exercises gets told to see a health professional, which looks broken.
- **Drop the backup and trust the AI read.** Pros: no false alarms from words. Cons: loses the second layer for real complaints.
- **Exclude exercise names from the pattern.** Pros: keeps the backup; removes the alarms seen. Cons: a longer regex (text pattern) that has to know exercise vocabulary.

## Decision
Exclude exercise names. A body part (knee, shoulder, hip, ankle, wrist, neck, elbow, hamstring) doesn't count when followed by press, thrust, hinge, bridge, raise, curl, extension, tuck, or abduct. "Back" doesn't count before squat(s), extension(s), or row(s), in addition to the existing "coming/getting back" exclusions. Tests confirm real complaints still match: sore knee, my hip hurts, bad shoulder, lower back pain, tweaked my back.

## Tradeoffs
- A complaint that names a body part only inside an exercise name and uses no pain word is no longer caught by the backup. A scribe probe: "shoulder presses feel off" doesn't match, while "knee raises hurt" still does (through "hurt"). The AI read is still the first layer.
- The exclusion list must grow with the catalog's exercise names.

## Revisit when
- A new exercise name triggers a false referral.
- A real complaint is missed by both layers.
