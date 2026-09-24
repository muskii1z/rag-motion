# 0008. Documentation with a build-scribe subagent
**Date:** 2026-09-24 · **Step:** 0 · **Status:** accepted

## Context
The project should be presentable as an interview case study. That needs a record of every step, decision, and lesson, captured as it happens.

## Options considered
- **Main session writes docs inline.** No handoff needed, but documentation competes with building in the same conversation.
- **A scribe subagent fed a brief each step.** A [subagent](../concepts.md#subagent) is a separate Claude instance with its own instructions. Docs stay consistent. The brief has to be complete, since the scribe can't see the conversation.
- **Write docs only at the end.** Least effort now, but details and lessons get forgotten.

## Decision
Use a dedicated build-scribe subagent (`.claude/agents/build-scribe.md`) that writes to `docs/` after every step, with four document types: build log, concepts glossary, decision records, and interview prep. This keeps docs consistent, means nothing is forgotten, and captures learning as it happens.

## Tradeoffs
The brief has to be complete, since the scribe can't see the conversation.

## Revisit when
Briefs keep missing important context.
