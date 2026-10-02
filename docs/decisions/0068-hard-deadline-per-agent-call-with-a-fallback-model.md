# 0068. A hard deadline per agent call, with one retry on a fallback model
**Date:** 2026-10-02 · **Step:** Phase 2, P3 · **Status:** accepted

## Context
A program request hung for minutes. Tracing showed one Qwen3.5 Flash call took 847 s. The OpenRouter client has a 25 s timeout ([0031](0031-openrouter-timeout-25s-one-retry.md)), but it is a read timeout: it restarts whenever bytes arrive, and OpenRouter sends keep-alive bytes on slow requests. So the limit never fired.

## Options considered
- **Lower the client timeout.** Pros: one setting. Cons: still a per-read limit, so keep-alive bytes still defeat it.
- **A wall-clock deadline: run the call in a thread and wait with `result(timeout)`.** Pros: a real limit on total time that bytes on the wire can't reset. Cons: the abandoned call keeps running in its thread; Python waits for such threads at process exit.
- **Deadline plus a fallback model.** Pros: the user often still gets a program when one model stalls. Cons: a second model to keep compatible with the tools and prompt; worst case is two deadlines.

## Decision
`_call_model` in `src/ragmotion/agent.py` submits each agent model call to a thread pool and waits up to `agent_call_deadline_seconds = 40`. On a miss it retries once on `settings.agent_fallback_model`. If both miss, it raises `AgentModelTimeout`, returned as HTTP 503 "The program builder took too long to respond. Try again in a minute." Tested with fake slow models; with a real call, a 5 s deadline returned at 5.0 s.

## Tradeoffs
- An abandoned call finishes in the background and is ignored. Whether it is still billed wasn't checked.
- Scripts can exit late, because Python waits for abandoned threads at exit. The server is unaffected.
- Worst case for one call is about 80 s (40 s × 2 models), and a turn makes several calls.
- 40 s could cut off a slow but valid long answer.

## Revisit when
- Deadlines fire on normal requests (check how often in traces or logs).
- Abandoned calls turn out to be billed and add up.
- A whole-turn limit is needed for the page (no total turn limit is recorded).
