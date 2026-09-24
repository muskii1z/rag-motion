# 0006. Interface: CLI first, thin FastAPI at Step 12
**Date:** 2026-09-23 · **Step:** 0 · **Status:** accepted

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
