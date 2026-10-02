# 0071. Fat-loss programs must say nutrition isn't covered, enforced in code
**Date:** 2026-10-02 · **Step:** Phase 2, P4 · **Status:** accepted

## Context
The sources the program builder can cite don't cover nutrition, and fat loss depends heavily on it. The agent's prompt already told it to say so on fat-loss programs. In the first P4 run, the one-kettlebell fat-loss client got a program with no such sentence.

## Options considered
- **Leave it as a prompt rule.** Pros: no code. Cons: already ignored once.
- **Add the sentence in code after the program is built.** Pros: always present. Cons: the program text is the model's; stitching text in can read badly.
- **A checker rule with an exact fix.** Pros: same path as every other check; the agent writes the sentence itself. Cons: costs a resubmission when missed; a word match can't tell what the sentence actually says.

## Decision
A checker rule, "fat-loss program says nutrition isn't covered by the sources". It applies when the goal mentions fat, weight loss, lose weight, or lean. It passes when the rationale or safety notes mention "nutrition" or "diet". Fix: "Add a sentence to the rationale saying nutrition matters for fat loss but isn't covered by these sources." Tested.

## Tradeoffs
- The check matches a word, not a meaning. A sentence that mentions diet without saying the sources don't cover it would pass.
- A missed sentence costs a resubmission (time and money).

## Revisit when
- Nutrition sources are added (the statement would no longer be true).
- The coach finds passing programs whose nutrition sentence is wrong or misleading.
