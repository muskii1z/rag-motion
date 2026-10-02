# 0053. The agent runs on Qwen3.5 Flash after a 6-model test
**Date:** 2026-10-01 · **Step:** Phase 2, step 2 follow-up · **Status:** superseded by [0069](0069-agent-back-on-gemini-2-5-flash-with-flash-lite-fallback.md) (it superseded [0050](0050-agent-model-gemini-2-5-flash.md))

## Context
[0050](0050-agent-model-gemini-2-5-flash.md) put the program agent on Gemini 2.5 Flash: reliable, but about 0.6 cents ($0.006) per program. The developer: *"0.6 is a lot bud, can we explore other models that will do the same job but cheaper."* At about $6 per 1,000 programs it isn't much yet, but the developer wanted to know whether the same reliability was available for less.

In step 1 ([0048](0048-agent-keeps-gemini-2-5-flash-lite-compare-models-later.md)) Qwen3.5 Flash had been considered on listed price alone, and the developer chose to "keep Gemini". This time the question was answered by measurement, at the developer's request.

## Options considered
Candidates: OpenRouter models that support tools and `tool_choice` (forcing a specific tool call), at $0.30 or less per million input tokens. Same replayed conversation as step 2 (beginner, build muscle and get stronger, 4 days, "dumbbells, a bench and resistance bands"), 3 runs each, models switched with the `AGENT_MODEL` environment variable. Costs include profile extraction (Flash-Lite) and embeddings.

| Model | Passed all checks | Accepted on first submission | Time per program | Cost per program |
|---|---|---|---|---|
| Gemini 2.5 Flash (0050; earlier test) | 3/3 | 3/3 | 11–13 s | $0.0060–0.0067 |
| `qwen/qwen3.5-flash-02-23` | 3/3 | 3/3 | 19 s each | $0.0013–0.0015 |
| `mistralai/mistral-small-3.2-24b-instruct` | 3/3 | 2/3 | 22–48 s | $0.0010–0.0017 |
| `qwen/qwen3-235b-a22b-2507` | 3/3 | 3/3 | 19–53 s | $0.0011–0.0050 |
| `openai/gpt-oss-120b` | 3/3 | 1/3 (two "invalid shape, sent back") | 96–136 s | $0.0010–0.0014 |
| `deepseek/deepseek-v4-flash` | 0/3 (3–4 checks still failing after 3 submissions) | 0/3 | 126–143 s | $0.0058–0.0065 |

- **Keep Gemini 2.5 Flash.** Pros: fastest (11–13 s), 3/3 first try, Google-hosted. Cons: 4–5x the cost of Qwen3.5 Flash.
- **Qwen3.5 Flash.** Pros: 3/3 first try, steady 19 s, about $0.0014 per program. Cons: about 7 s slower; open-weight model, so served by third-party hosts (Qwen was slow and unpredictable in Step 10).
- **Mistral Small 3.2.** Pros: cheapest at the low end. Cons: one retry in 3, time doubled between runs (22–48 s).
- **Qwen3 235B.** Pros: 3/3 first try. Cons: cost varied 5x, time 19–53 s.
- **GPT-OSS 120B.** Cons: shape errors, 1.5–2+ minutes per program.
- **DeepSeek V4 Flash.** Cons: failed every run, and cost about as much as Gemini Flash.

## Decision
`config.agent_model` defaults to `qwen/qwen3.5-flash-02-23`. It matched Gemini 2.5 Flash's reliability (3/3 first try) with steady timing at about a quarter of the cost. The Q&A app stays on `google/gemini-2.5-flash-lite`.

## Tradeoffs
- About 7 s slower per program than Gemini 2.5 Flash (19 s vs 11–13 s).
- A third model family to watch (Gemini for Q&A and profile extraction, Qwen for the agent).
- Depends on third-party hosts for an open-weight model; speed and behavior may vary by host, which wasn't recorded.
- Evidence is one conversation, 3 runs per model; Gemini Flash's numbers come from an earlier test, not the same parallel batch.

## Revisit when
- Step 4's test set (about 10 fictional clients) shows Qwen3.5 Flash failing checks that Gemini 2.5 Flash passes.
- The program page (step 3) makes 19 s feel too slow to users.
- Timing or failures start varying by host.
- Prices change, or a new cheap model with tool support appears.

## Update 2026-10-01 (Phase 2 quality pass, Q1)
- Candidates were picked for supporting `tool_choice`, but Qwen3.5 Flash's only provider rejected a *named* `tool_choice` (OpenRouter 404). The test never reached the forced submit, so it didn't show. The agent no longer names a tool; it offers only the submit tool instead ([0047 update](0047-agent-loop-guardrails-repeat-refusal-nudge-forced-submit.md)). The model choice stands.
- The 6-model test ran before Q1's stricter quality checks ([0057](0057-program-quality-checks-weekly-sets-patterns-day-labels.md)). With them, Qwen3.5 Flash passed 0 of 3 replays fully. Whether another model does better under the new checks is untested.

## Update 2026-10-02 (Phase 2, P3): superseded
In live browser use Qwen3.5 Flash was intermittently extremely slow on the program-writing call: one call ran 847 s, one turn 116 s, a traced run 400+ s inside one call (short calls about 1 s). The 6-model test's steady 19 s didn't hold in use. The developer switched the agent back to Gemini 2.5 Flash with Flash-Lite as fallback. See [0069](0069-agent-back-on-gemini-2-5-flash-with-flash-lite-fallback.md).
