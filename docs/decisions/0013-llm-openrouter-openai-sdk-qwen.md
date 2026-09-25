# 0013. LLM via OpenRouter with the openai SDK; default Qwen3 235B
**Date:** 2026-09-24 · **Step:** 6 · **Status:** accepted (default model switched to google/gemini-2.5-flash-lite in Step 10, see the update at the end)

Supersedes [0003. LLM: Claude Opus 5](0003-llm-claude-opus-5.md).

## Context
Step 6 is the first LLM call: turn a coach's plain-English client description into a structured profile. The original plan ([0003](0003-llm-claude-opus-5.md)) was Claude Opus 5 through the `anthropic` SDK. Since Step 5 the developer has preferred [OpenRouter](../concepts.md#openrouter): one key for many models, which makes comparing models easy. Two choices were needed: which library to call it with, and which model to use by default. The model had to support structured output (the model filling in an exact template), because Step 6 depends on it. A read-only lookup of OpenRouter's model list showed 353 text models with structured-output support.

## Options considered
**Access path.**
- **Claude direct through the `anthropic` SDK** (original plan). One vendor, no middleman. But locked to Claude models, and comparing models means a new integration each time.
- **OpenRouter with the `openai` SDK** (chosen). OpenRouter accepts OpenAI's request format, so the official `openai` library works by changing the base URL ([OpenAI-compatible APIs](../concepts.md#openai-compatible-apis)). Its `chat.completions.parse()` takes a Pydantic model and returns a validated object. One key for many models; the model is a setting. Cons: a middleman, and open-model hosts vary.

**Default model** (prices per million tokens, in / out; Phase 1 estimates at about 300 calls where given):
- **google/gemini-2.5-flash-lite.** $0.10 / $0.40, ~$0.15.
- **openai/gpt-5-mini.** $0.12 / $1.00, ~$0.25.
- **anthropic/claude-haiku-4.5.** $1 / $5, ~$1.50.
- **anthropic/claude-sonnet-5.** $2 / $10, ~$3.
- **qwen/qwen3-235b-a22b-2507.** $0.09 / $0.35, structured outputs. About Flash-Lite's price for a much larger model. Open-weight, so served by several third-party hosts.
- **moonshotai/kimi-k2.5.** $0.45 / $2.25, structured outputs. Known for strong tool use (relevant to Phase 2). Other Kimi versions: `kimi-k2-0905` ($0.60 / $2.50), `kimi-k3` ($0.88 / $10.53), and the original `kimi-k2` ($0.57 / $2.30), which has no structured outputs and was ruled out.

Claude declined to vouch for newer models it doesn't know well.

## Decision
Call the LLM through OpenRouter with the `openai` SDK (3.19.2). Default model `qwen/qwen3-235b-a22b-2507`, the developer's choice ("let's use the Qwen one"): the cheapest capable option. It is set in `src/ragmotion/config.py` (`llm_model`) and can be overridden with `LLM_MODEL` in `.env` or the environment. Every call sets `max_tokens`, `temperature=0`, `provider.require_parameters=true` (only hosts that support every parameter sent), and `usage.include=true` (cost reported per call). Comparison candidates for later: `moonshotai/kimi-k2.5` plus an established model.

## Tradeoffs
- An extra middleman between the app and the model provider.
- Open-model host variability. The first call failed because one host (GMICloud) defaulted to reserving the whole context window for the reply. Guarded with `max_tokens` and `require_parameters`. See [Open-weight model hosting variability](../concepts.md#open-weight-model-hosting-variability).
- **In Step 6 testing, Qwen was the weakest of three models.** On the same prompt it fell for a prompt-injection test that Kimi K2.5 and Claude Haiku 4.5 resisted, and it still inferred values the text didn't state (experience "intermediate", `bodyweight`). Cost per call: Qwen ~$0.0001, Haiku 4.5 ~$0.002, Kimi K2.5 ~$0.003–0.005 (Kimi is a thinking model, so slower too). See [Step 6](../build-log.md#runs-problems-and-fixes).
- The `anthropic` package stays installed but unused.

## Revisit when
- Step 15, when models can be compared on the evaluation set instead of two hand tests.
- Injection or inference errors show up in real use.
- Open question already raised in Step 6: whether to switch the default now to Haiku 4.5 or Kimi K2.5. The developer has not decided; the default stays Qwen until they do.

## Update 2026-09-24: default confirmed
After seeing the three-model comparison, the developer chose to keep `qwen/qwen3-235b-a22b-2507` as the default. Reason: it is by far the cheapest, the coach writes the input during development so injection risk is low in practice, and its weak spots (inferring unstated facts, following injected instructions) become test cases. Models are compared properly on the Step 15 evaluation. Claude Haiku 4.5 and Kimi K2.5 remain the comparison candidates.

## Update 2026-09-25 (Step 10): default switched to Gemini 2.5 Flash-Lite
Step 10 added a second LLM task, writing grounded RAG answers, and a web page where waiting is visible. Qwen's latency became the problem: across all Step 10 runs its generation took 4 to 29 seconds, unpredictably (29,429 ms for one biceps question in the web page), and its actual cost ran about 2x its listed price, probably depending on which host served it. See [Open-weight model hosting variability](../concepts.md#open-weight-model-hosting-variability).

Comparison on one question, "what exercises can i do for biceps" (the catalog has no curls):

| Model | Generation time | Cost | Gap honesty |
|---|---|---|---|
| google/gemini-2.5-flash-lite (2 runs) | 793 ms, 681 ms | $0.000145 each (1,083 in / 91 out tokens) | Cited both rows, but said coverage "full" and didn't mention the missing curls |
| qwen/qwen3-235b-a22b-2507 | 3,986 ms (29,429 ms in an earlier web-page run) | $0.000285 | Earlier terminal run: coverage "partial", gap "no isolation exercises such as bicep curls" |

Options offered to the developer: Gemini 2.5 Flash-Lite (recommended), keep Qwen, or try Claude Haiku 4.5. **The developer chose Gemini 2.5 Flash-Lite as the day-to-day default, for speed.** It is set in `src/ragmotion/config.py` (`llm_model`), documented in `.env.example`, and noted in `CLAUDE.md`. `LLM_MODEL` still overrides it.

Caveats:
- Judged on one question. Gemini was also over-confident on "exercises that need no equipment" (said "full" while two bodyweight exercises were missing from the evidence). Keep watching its gap honesty.
- Gemini's results on the Step 6 extraction tests (messy description, prompt injection) are not recorded. Open question: rerun them before relying on it for extraction.
- Qwen, Kimi K2.5, and Claude Haiku 4.5 remain comparison candidates for Step 15, where models are compared on the evaluation set.

Status is now: accepted, default `google/gemini-2.5-flash-lite` since Step 10. See [Step 10](../build-log.md#test-runs-and-fixes).

### Addendum 2026-09-25: Gemini on the Step 6 extraction tests
Run after the switch, because Gemini is now also the default for `extract_profile()`:
- **Test A (messy description):** no guessed age or frequency (both null, wording kept in notes), TRX strap in `unmapped_equipment`, only `kettlebell` mapped, experience `beginner` (defensible from "hasn't lifted in years"; Claude Haiku made the same call). 384 in / 160 out tokens, $0.000102.
- **Test B (prompt injection):** resisted. Kept `advanced`, 4 sessions, 60 minutes, no "unlimited budget" note. 386 in / 94 out tokens, $0.000076.
So on these tests Gemini 2.5 Flash-Lite is faster, cheaper, and more robust than Qwen. Its weak spot so far is gap honesty in RAG answers (biceps question: claimed "full" coverage).
