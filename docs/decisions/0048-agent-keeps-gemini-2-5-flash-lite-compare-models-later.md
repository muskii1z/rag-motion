# 0048. The agent keeps Gemini 2.5 Flash-Lite; compare models in step 4
**Date:** 2026-10-01 · **Step:** Phase 2, step 1 · **Status:** accepted

## Context
The developer asked whether to switch to a Qwen model for the agent (cheaper or better?). The app's default is `google/gemini-2.5-flash-lite` ([0013 update](0013-llm-openrouter-openai-sdk-qwen.md)).

## Options considered
Checked on OpenRouter:
- **Qwen3.5 Flash.** About 30% cheaper than Gemini 2.5 Flash-Lite.
- **Qwen3 235B.** About the same price.
- **Qwen3.7 Flash.** About 3x cheaper, but no structured outputs.
- **Keep Gemini 2.5 Flash-Lite.** Already used across the app; costs already about $0.0004 per answer.

Project history: a Qwen host rejected parameters (Step 6) and Qwen was too slow (Step 10).

## Decision
Keep Gemini 2.5 Flash-Lite for the agent. Compare 2–3 models in step 4 on the same test clients if needed. Developer: "it's fine, we'll keep Gemini."

## Tradeoffs
- At these prices the saving from switching is fractions of a cent; reliability matters more for an agent, which makes many calls per turn.
- A small model loops and follows prompt rules loosely (run 1 looped; run 2 gave 7 exercises a day against a 4–6 rule), so more of the work moves into code guardrails and the checker.

## Revisit when
- The step 4 test set (about 10 fictional clients) shows the agent failing in ways a different model might fix.
- Agent cost per program becomes meaningful at real usage.
