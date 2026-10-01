# 0061. A text reply after building has started forces a submission
**Date:** 2026-10-01 · **Step:** Phase 2 quality pass, Q2 · **Status:** accepted

## Context
In one full-gym replay the agent ended its turn with text instead of a program: `"</think>\n\nPerfect! I have the information I need. Let me summarize..."`. The client would have seen a promise, no program, and a leaked `</think>` tag (part of the model's hidden reasoning). Existing guardrails ([0047](0047-agent-loop-guardrails-repeat-refusal-nudge-forced-submit.md)) only forced a submission after 10 tool calls or after a rejection, so a text reply earlier than that ended the turn.

## Options considered
- **Prompt only** ("never describe the program; submit it"). Pros: no code. Cons: the prompt already asks for a submission; a prompt rule is a request, not a guarantee.
- **Force a submission after any text reply.** Pros: simple. Cons: breaks asking the client for missing details, which is a correct text reply.
- **Force a submission after a text reply once building has started.** "Started" means a successful `find_exercises` or `search_sources`; refused lookups (details missing) don't count. Pros: asking for details still works; narration after real progress can't end the turn. Cons: a genuine mid-build question to the client is now impossible.

## Decision
The third option, in `agent.py`. After a successful lookup, a plain-text reply sets `must_submit`: the text is kept in the conversation, a system message says "Don't describe the program. Call submit_program with it now.", and the next call offers only the submit tool. Separately, `_visible()` strips `<think>...</think>` (and anything before a stray `</think>`) from every reply shown or stored.

The refused-lookup exception wasn't in the first version. An existing test failed, which showed that a refused lookup followed by a question to the client was being forced into a submission.

## Tradeoffs
- Once building has started, the agent can't stop to ask the client something. Not seen in any run so far, and not tested.
- The rule depends on reading tool results as text (a result starting with "refused"). Renaming that message would silently change the guardrail.
- Stripping reasoning hides it from the client, but the tokens are still generated and billed.

## Revisit when
- A run shows the agent needing a follow-up question mid-build.
- The agent model changes (another model may narrate differently, or not at all).
- The P4 program eval shows forced submissions producing worse programs than unforced ones.
