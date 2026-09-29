# 0031. Every OpenRouter call: 25-second time limit, 1 retry
**Date:** 2026-09-29 · **Step:** 16 (revisited) · **Status:** accepted

## Context
Every model call goes through one OpenRouter client, `get_client()` in `src/ragmotion/llm.py`: the answer, the limit reader (`extract_limits`), the embeddings, and the AI judge. No time limit was set on it. So the `openai` library's defaults applied: wait up to 10 minutes for a reply, and retry twice. A slow or stuck provider could leave a user staring at a spinner for many minutes, and nothing would tell them why. A timeout is the longest the app waits for a reply before giving up; a retry is trying the same call again. See [Timeouts and retries on outside calls](../concepts.md#timeouts-and-retries-on-outside-calls).

A normal answer takes 2–5 s. The judge also works within the limit.

## Options considered
- **Keep the library defaults (10 minutes, 2 retries).** Pros: nothing to choose or maintain; very slow replies still arrive. Cons: a stuck call can hang a request for far longer than any user will wait, and the user gets no message until it ends.
- **25-second limit, 1 retry, for every OpenRouter call.** Pros: worst case about 25 × 2 ≈ 50 s per call; a slow provider becomes a clear "took too long, try again in a minute" message; one setting covers the LLM and the embeddings. Cons: a legitimately slow, long answer could be cut off.

Other values (per-call limits, shorter limits for embeddings) were not discussed.

## Decision
`api_timeout_seconds = 25.0` and `api_max_retries = 1` in `src/ragmotion/config.py`, passed by `get_client()` to the shared OpenRouter client. A timeout is reported as HTTP 503: "The answer service took too long to respond. Try again in a minute." (from the answer model), or as the search service not responding (from the embedding call).

## Tradeoffs
- A legitimately slow, long answer could be cut off at 25 s.
- One limit for every kind of call, though an embedding call is normally much faster than an answer.
- About 50 s is the worst case for one call. A whole question makes several calls (limit reader, embedding, answer, plus a possible retry on broken JSON). The worst case for a whole question was not calculated.
- This retry is separate from the retry on unreadable JSON in `structured_completion()`, and from the judge's rate-limit backoff ([0025](0025-ai-judge-for-coach-labeling-rules.md)). There are now three retry mechanisms to keep in mind.

## Revisit when
- Timeouts appear in LangSmith traces on normal questions.
- A slower model becomes the default, or answers get much longer.
- The app is deployed and many users hit it at once; per-call limits or a total limit per request may then be needed.

See [Step 16 (revisited)](../build-log.md#step-16-revisited-mocked-web-api-tests-and-clean-handling-of-outside-service-failures).
