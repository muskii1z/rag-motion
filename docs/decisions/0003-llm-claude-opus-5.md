# 0003. LLM: Claude Opus 5
**Date:** 2026-09-23 · **Step:** 0 · **Status:** accepted

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
