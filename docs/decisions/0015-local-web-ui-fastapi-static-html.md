# 0015. Local web UI: FastAPI + one static HTML page
**Date:** 2026-09-25 · **Step:** 10 · **Status:** accepted

## Context
Step 10 was planned to include a minimal local page for asking questions and seeing the answer next to its evidence ([0006 amendment](0006-interface-cli-first.md#amendment-2026-09-24-step-5)). A UI means a web server of some kind. The choice was which tool builds it. Constraints: keep it minimal (the master context document says no polished frontend early), keep the OpenRouter key off the browser ("never put secrets in frontend code"), and don't add something that has to be thrown away at Step 16, when the API gets tests and error handling.

## Options considered
- **Streamlit.** A Python library that turns a script into a web page. Pure Python and the fastest to build. But it hides the split between frontend (what runs in the browser) and backend (the server), so it teaches little about how web apps work, and it is a heavy dependency. Its page would not be reusable as an API.
- **Gradio.** Similar tradeoffs to Streamlit: quick demo pages in Python, aimed at model demos, same hidden split.
- **FastAPI + one static HTML page** (chosen). FastAPI is a Python web-API library; uvicorn is the server that runs it. `GET /` serves one HTML file; `POST /api/ask` takes a validated question and returns JSON. Pros: an explicit API that a future frontend and Step 16 can reuse; teaches routes, validation, JSON, and status codes; keys stay server-side by design. Cons: HTML and JavaScript written and maintained by hand.

## Decision
FastAPI (0.141.1) + uvicorn (0.54.0) serving one static page, `src/ragmotion/static/index.html`, from `src/ragmotion/app.py`. The server runs on port **8010**, bound to **127.0.0.1** (this computer only): `uv run uvicorn ragmotion.app:app --host 127.0.0.1 --port 8010 --reload`. Port 8000 was free, but the developer's stopped vh_technology project maps 8000, so 8010 avoids a future collision (same reasoning as the database's 5434 in [0009](0009-local-db-port-5434-localhost-only.md)). The API returns the answer, coverage, gaps, citation problems, the evidence (rank, similarity, cited flag, source), usage, and timings. All user and model text is HTML-escaped on the page. `.claude/launch.json` lets Claude Code's browser pane start it.

## Tradeoffs
- Hand-written HTML and JavaScript to maintain, instead of a Python-only UI.
- FastAPI now arrives in Step 10 instead of Step 16, so Step 16 changes from "build a thin API" to "harden the one built in Step 10: tests, error handling, README".
- Any error in the RAG step is returned as a generic HTTP 502 with the error text. Fine locally; a deployed version would need specific codes and would not expose internal error messages.
- Two new dependencies (fastapi, uvicorn with its `[standard]` extras).

## Revisit when
- A real frontend is needed to demo to non-technical viewers (the API stays; the page gets replaced).
- The app is deployed beyond localhost: then add authentication, rate limits, and safer error messages.
- Step 16, when tests and error handling are added.

See [Step 10](../build-log.md#step-10-rag-grounded-cited-answers-plus-a-minimal-local-web-ui).

**Update 2026-09-25 (after Step 15):** the page was redesigned into a branded chat layout with a sources drawer, and `GET /api/info` was added (models, search mode, sources, counts). Same architecture. See [UI redesign](../build-log.md#ui-redesign-rag-motion-brand-and-chat-layout-after-step-15).

**Update 2026-09-28 (Step 16):** the "Step 16" revisit signal is handled. Errors are no longer a generic 502 with the raw error text: `friendly_message()` returns 503 (database down, rate limit, connection), 502 (provider rejected the call), or 500 (our own errors), each with one plain sentence and the fix. The full traceback is logged on the server, and unexpected errors don't expose internals. `/api/info` handles errors the same way. Still open for any deployment beyond localhost: authentication and rate limits. See [Step 16](../build-log.md#step-16-tests-error-handling-readme-phase-1-complete).

**Update 2026-09-29 (Step 16 revisited):** bad questions now get HTTP 400 with a plain sentence (checked in the endpoint instead of Pydantic's automatic 422, which the page showed as "Unprocessable Entity"); every OpenRouter call has a 25 s time limit; slow or down services, and unreadable model output twice, each get their own message; the endpoint is covered by 12 mocked tests in `tests/test_api.py`. See [0031](0031-openrouter-timeout-25s-one-retry.md), [0032](0032-api-errors-plain-400-named-service-status-codes.md), and [Step 16 (revisited)](../build-log.md#step-16-revisited-mocked-web-api-tests-and-clean-handling-of-outside-service-failures).
