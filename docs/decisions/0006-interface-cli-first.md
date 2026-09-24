# 0006. Interface: CLI first, thin FastAPI at Step 12
**Date:** 2026-09-23 · **Step:** 0 · **Status:** accepted (amended in Step 5: minimal local UI at Step 10, FastAPI moved to Step 16)

## Context
The project needs some way to run and demo the system. The master context document says not to build a polished UI early; the AI and backend are the focus.

## Options considered
- **CLI scripts first, thin FastAPI later.** CLI scripts are command-line programs run from the terminal. Fastest feedback and nothing hidden: every step is a command the developer can run and read. Not demo-friendly to non-technical viewers.
- **FastAPI from the start.** FastAPI is a Python framework for building web APIs. Gives an API shape early. But it adds web concepts (routes, request bodies, servers) before the RAG concepts are understood.
- **Web frontend (React/Next.js) early.** Gives a visual demo. But it is a large time sink that teaches frontend work, not AI engineering. The context document says explicitly not to build a polished UI early.

## Decision
Use CLI scripts first. Add a thin FastAPI `/ask` endpoint (a small web API) only at Step 12. No frontend in Phase 1.

## Tradeoffs
No visual demo until after Phase 1. The FastAPI endpoint at Step 12 keeps the door open for a UI.

## Revisit when
After Phase 1, when a UI is needed to demo.

## Amendment (2026-09-24, Step 5)
- **Renumbered.** The Phase 1 plan was revised ([0011](0011-phase-1-plan-revision-ingestion-and-langsmith.md)). The FastAPI endpoint, tests, and README are now **Step 16**, not Step 12.
- **A minimal local UI at Step 10.** The developer asked for a small page to interact with the app on localhost (this computer). Agreed: a small local page is added at Step 10, when RAG first works. It shows a question box, the answer, and the retrieved exercises with their scores. This matches the master context document's "first major demo" (an answer shown next to its evidence). It is deliberately minimal, not a polished frontend, so it stays within the context document's rule. Before Step 10, the terminal is faster.
- This replaces "No frontend in Phase 1" with "a minimal local evidence page only, at Step 10". The revisit signal above still applies to anything beyond that.

See [Step 5](../build-log.md#step-5-write-20-exercises-seed-script-query-by-hand).
