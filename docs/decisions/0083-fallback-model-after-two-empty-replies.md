# 0083. After two empty replies, the rest of the turn uses the fallback model
**Date:** 2026-10-02 · **Step:** Phase 2 follow-up (gym detection, likes vs dislikes) · **Status:** accepted

## Context
The agent's model sometimes returns an empty reply (no text, no tool call). Until now, the first empty reply got a nudge ("Your last reply was empty. Call a tool, or answer the client.") and a second one ended the turn with "The program builder didn't respond. Please try again." ([Fail visibly](../concepts.md#fail-visibly-retry-budget-then-show-the-failure)). In the first eval run of this step, Gemini 2.5 Flash sent two empty replies in a row in 2 of 42 runs, at the same moment, which looked like a short provider problem rather than a bad prompt. The fallback model ([0068](0068-hard-deadline-per-agent-call-with-a-fallback-model.md), [0069](0069-agent-back-on-gemini-2-5-flash-with-flash-lite-fallback.md)) was only used when a call missed its 40 s deadline.

## Options considered
- **Keep the error after two empty replies.** Pros: simple; the user retries. Cons: a passing provider blip becomes a failed turn.
- **More nudges on the same model.** Pros: no second model. Cons: if the provider is having a bad moment, more calls to it likely fail the same way.
- **Switch to the fallback model for one more try.** Pros: a different model, likely served differently, gets the turn done. Cons: the fallback (Flash-Lite) is weaker; the rest of the turn runs on it.

## Decision
On the second empty reply, `run_turn` in `src/ragmotion/agent.py` sends the nudge again and switches `model` to `agent_fallback_model` (`google/gemini-2.5-flash-lite`) for the rest of the turn. A third empty reply still ends with the clear error. Two tests with a scripted fake model: the fallback is used after two empty replies, and the fallback rescues a turn.

## Tradeoffs
- A turn rescued by the fallback was built by the weaker model. The checker still runs on its program.
- How often the fallback actually rescued a turn in the eval isn't recorded. The final run had 0 errors.

## Revisit when
- Empty replies become frequent (then it's a model or prompt problem, not a blip).
- Programs built on the fallback fail checks more often than the main model's.
- The eval records which model finished each turn, so the rescue rate can be measured.
