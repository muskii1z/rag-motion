# 0003. LLM: Claude Opus 5
**Date:** 2026-09-23 · **Step:** 0 · **Status:** superseded by [0013](0013-llm-openrouter-openai-sdk-qwen.md) (Step 6)

## Context
The app needs an LLM (large language model) to read text and write answers. Claude Code offered three Claude models. The developer deferred the choice.

## Options considered
- **Claude Opus 5.** $5 per million input tokens, $25 per million output tokens.
- **Claude Sonnet 5.** $2 input, $10 output per million tokens.
- **Claude Haiku 4.5.** $1 input, $5 output per million tokens.

(A token is a small chunk of text, roughly part of a word. APIs charge per token.)

## Decision
Use Claude Opus 5 (model ID `claude-opus-5`) through the official `anthropic` Python SDK. Because the developer deferred, Claude defaulted to Opus 5 as the standard current model. Structured outputs will use `client.messages.parse` with a Pydantic model (a Python class that defines the exact shape the output must have). The key goes in `ANTHROPIC_API_KEY`.

## Tradeoffs
Opus 5 is the most expensive of the three options. Volume in this project is tiny, so cost stays low. Changing the model is one config line.

## Revisit when
Running evals many times makes cost noticeable. Then try Sonnet 5.

## Note (2026-09-24, Step 5): under review
In Step 5 the developer said they probably won't use Claude's model and would prefer to reach the LLM through [OpenRouter](../concepts.md#openrouter), a service that gives one API key for many models from different providers.
- **Why:** one key for many models, which makes comparing models easy later.
- **Tradeoffs:** an extra middleman between the app and the model provider, and support for structured output (the model returning data in an exact shape) varies by model. The `client.messages.parse` plan above is specific to the `anthropic` SDK and may not apply.
- **What changed already:** `.env.example` now has `OPENROUTER_API_KEY` (needed from Step 6); `ANTHROPIC_API_KEY` is kept but marked optional. `CLAUDE.md` says the LLM is "likely via OpenRouter", confirmed at Step 6.
- **Still open:** which model, and which Python library to call it with. Both will be chosen and recorded at Step 6. No new decision record has been created yet; this one stays under review until then.

See [Step 5](../build-log.md#step-5-write-20-exercises-seed-script-query-by-hand).

## Note (2026-09-24, Step 6): superseded
Resolved at Step 6 by [0013. LLM via OpenRouter with the openai SDK; default Qwen3 235B](0013-llm-openrouter-openai-sdk-qwen.md). The LLM is now reached through OpenRouter with the `openai` library, and the default model is `qwen/qwen3-235b-a22b-2507`. Claude models remain available through OpenRouter: `anthropic/claude-haiku-4.5` was one of the three models compared in Step 6. The `anthropic` package stays installed but unused, and `ANTHROPIC_API_KEY` stays optional in `.env.example`. See [Step 6](../build-log.md#step-6-first-llm-call-via-openrouter-prose-to-structured-client-profile).
