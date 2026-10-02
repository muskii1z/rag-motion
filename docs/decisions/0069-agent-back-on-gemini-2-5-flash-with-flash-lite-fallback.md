# 0069. The agent goes back to Gemini 2.5 Flash, with Flash-Lite as fallback
**Date:** 2026-10-02 · **Step:** Phase 2, P3 · **Status:** accepted (supersedes [0053](0053-agent-model-qwen3-5-flash-after-six-model-test.md))

## Context
[0053](0053-agent-model-qwen3-5-flash-after-six-model-test.md) chose Qwen3.5 Flash after a 6-model test (3/3 first try, 19 s each, about $0.0014 per program). In live browser use it was intermittently extremely slow on the program-writing call: one call ran 847 s, one turn 116 s, a traced run 400+ s inside one call. Short calls took about 1 s. A reasoning-on vs reasoning-off speed test was stopped by the time limit with no result. Hypothesis, not proven: Qwen3.5 Flash is a reasoning model and long structured answers stall on its provider. The new deadline ([0068](0068-hard-deadline-per-agent-call-with-a-fallback-model.md)) stops the hang, but a user still waits up to the deadline and then gets the fallback.

## Options considered
- **Keep Qwen3.5 Flash, rely on the deadline and fallback.** Pros: cheapest per program. Cons: unpredictable waits; many turns would end on the fallback anyway.
- **Gemini 2.5 Flash, with Flash-Lite as fallback.** Pros: 3/3 first try in step 2 ([0050](0050-agent-model-gemini-2-5-flash.md)); predictable latency. Cons: about 3–4× Qwen's cost per program.

## Decision
The developer: *"ok let's switch back to Gemini then"*. `agent_model = google/gemini-2.5-flash`, `agent_fallback_model = google/gemini-2.5-flash-lite` (commit `ae97bef`).

Verification, 3 fictional clients × 2 runs in parallel: 5 of 6 passed every check, 8–21 s, 0.4–1.2 cents per program. The one failure (full gym, 4 days, intermediate) still failed "squat/lunge on 2+ days" and "one per pattern per day" after 3 submissions. In the browser: a beginner dumbbell program in under 18 s, five sources cited, no stated volume numbers, $0.0048.

## Tradeoffs
- About 3–4× Qwen3.5 Flash's cost per program. A cheap model that stalls isn't cheap for the person waiting.
- Six runs on three clients is a small sample.
- The Qwen stall's cause is unproven; Qwen might be fine on another provider or with reasoning off.

## Revisit when
- P4 (~10 fictional clients) shows Gemini 2.5 Flash failing checks repeatedly, especially the full-gym squat/lunge failure.
- Cost per program matters at real usage.
- Qwen3.5 Flash (or another cheap model) is shown to answer program-sized requests steadily, for example with reasoning off.
