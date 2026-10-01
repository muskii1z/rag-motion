# 0050. The agent uses Gemini 2.5 Flash; the Q&A app stays on Flash-Lite
**Date:** 2026-10-01 · **Step:** Phase 2, step 2 · **Status:** superseded by [0053](0053-agent-model-qwen3-5-flash-after-six-model-test.md) (it superseded [0048](0048-agent-keeps-gemini-2-5-flash-lite-compare-models-later.md))

## Context
With the program checker in place, Gemini 2.5 Flash-Lite still struggled. Even with exact fix instructions it passed 2 of 3 replays of the developer's conversation, never on the first submission, and one run still had the wrong number of exercises per day after 3 tries. [0048](0048-agent-keeps-gemini-2-5-flash-lite-compare-models-later.md) had kept Flash-Lite and planned a model comparison "if needed". It was needed now.

## Options considered
Same conversation (beginner, build muscle and get stronger, 4 days, "dumbbells, a bench and resistance bands"), 3 runs each:

| Model | Passed checks | Accepted on first submission | Time | Cost per program |
|---|---|---|---|---|
| Gemini 2.5 Flash-Lite | 2/3 | 0/3 | 15–21 s | $0.0021–0.0026 |
| Gemini 2.5 Flash | 3/3 | 3/3 | 11–13 s | $0.0060–0.0067 |

- **Keep Flash-Lite.** Pros: cheapest per run. Cons: retries, slower, one program in three still failed.
- **Gemini 2.5 Flash.** Pros: every program passed first time, and faster, because no retries. Cons: about 2.5x the cost per run.
- Other families weren't tested. The developer asked to "keep Gemini".

## Decision
`config.agent_model` defaults to `google/gemini-2.5-flash` (set to `None` to fall back to `llm_model`). The Q&A app stays on `google/gemini-2.5-flash-lite`.

## Tradeoffs
- About 2.5x the cost per program run, around 0.6 cents. Still trivial at this scale.
- By the recorded numbers, Flash also costs more per *passing* program (about $0.006–0.0067 vs about $0.003–0.004 for Flash-Lite), so the gain is reliability and speed, not money.
- Two model settings to keep track of instead of one.
- Evidence is one conversation, 3 runs per model.

## Revisit when
- Step 4's test set (about 10 fictional clients) shows Flash failing checks, or Flash-Lite passing them reliably.
- Cost per program starts to matter at real usage.
- A cheaper model is shown to pass the same checks first time.

## Update 2026-10-01 (Phase 2, step 2 follow-up): superseded
The developer asked for a cheaper model that does the same job. Five cheap OpenRouter models with tool support were tested on the same conversation, 3 runs each. Qwen3.5 Flash (`qwen/qwen3.5-flash-02-23`) passed 3/3 on the first submission, like Gemini 2.5 Flash, in a steady 19 s, at $0.0013–0.0015 per program, about 4–5x cheaper. The agent now runs on Qwen3.5 Flash. The Q&A app stays on Flash-Lite. See [0053](0053-agent-model-qwen3-5-flash-after-six-model-test.md).

This also corrects a claim made at the time of this decision: Gemini 2.5 Flash was faster and more reliable than Flash-Lite, but not cheaper per passing program (about 1.5–2x more).
