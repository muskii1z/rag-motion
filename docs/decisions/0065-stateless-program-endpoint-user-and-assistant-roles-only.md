# 0065. Stateless program endpoint: the page sends the whole conversation; only user and assistant roles
**Date:** 2026-10-01 to 2026-10-02 · **Step:** Phase 2, P3 · **Status:** accepted

## Context
The program agent needed a web endpoint for the new page. The agent's `run_turn` already took the whole conversation and kept nothing between turns ([Phase 2, step 1](../build-log.md#phase-2-step-1-the-program-agent-loop-conversation-and-tools)). A web endpoint that accepts a conversation from the browser also accepts whatever the browser sends, including messages pretending to be the app's own instructions.

## Options considered
- **Server-side sessions.** The server stores each conversation under an id. Pros: the client can't edit history; less data sent per turn. Cons: storage, expiry, and a session id to manage; any server process must reach the same store.
- **Stateless: the page sends the whole conversation each turn.** Pros: no storage; any server process can answer any turn; matches `run_turn`. Cons: the client controls the history, so input must be checked; more data sent per turn.

## Decision
Stateless. `POST /api/program` takes the whole conversation and checks it before any paid call: not empty; last message from the user; at most 30 messages; each at most 1,000 characters; roles only `user` or `assistant`. A `system` message is rejected, so a client can't inject the app's own kind of instruction. Failures go through `friendly_message()`. The page also sends a short text summary of the program back into the conversation so follow-ups ("swap the squat") have context.

## Tradeoffs
- The client still controls `assistant` messages, so it could write fake assistant turns. Not addressed in this step.
- Long conversations are capped at 30 messages; a very long chat would be refused.
- The program summary sent back is text, not the full program, so a follow-up sees only what the summary contains.

## Revisit when
- Real users (not just the developer and coach) use the page: then consider server-side sessions or signing the assistant turns.
- The 30-message or 1,000-character limits cut off real conversations.
