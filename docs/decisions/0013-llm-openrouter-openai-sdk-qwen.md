# 0013. LLM via OpenRouter with the openai SDK; default Qwen3 235B
**Date:** 2026-09-24 · **Step:** 6 · **Status:** accepted (default model open for review)

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
