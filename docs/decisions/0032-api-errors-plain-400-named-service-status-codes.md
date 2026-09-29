# 0032. API errors: plain 400s for bad questions, the failing service named, status codes by cause
**Date:** 2026-09-29 · **Step:** 16 (revisited) · **Status:** accepted

## Context
Step 16 gave the web API plain error messages for a database that's down and a rejected key ([0015 update](0015-local-web-ui-fastapi-static-html.md)). Several failures still reached the user badly:
- An empty or too-long question was rejected by Pydantic `Field` limits on the request model. FastAPI then sent its automatic 422 reply, a technical list of field errors, and the web page showed "Unprocessable Entity".
- When the model sent unreadable JSON twice, the user saw "Unexpected error (ValidationError)".
- Failures of the embedding call and the answer call looked alike, so the user couldn't tell whether search or the answer model was down.

## Options considered
**Where to check the question's length:**
- **Pydantic `Field(min_length=3, max_length=500)` on the request model (as before).** Pros: automatic; the limit appears in the API's published schema (the OpenAPI description FastAPI generates). Cons: failures come back as a technical 422 that the page can't turn into a helpful sentence.
- **Check in the endpoint (`ask()` in `app.py`).** Pros: a plain 400 sentence ("Please type a question." / "Questions can be up to 500 characters; this one has N. Please shorten it."); spaces are trimmed first, so `"   "` counts as empty. Cons: the limit lives in code, not in the schema.

**How specific the "service down" message should be:**
- **One generic "a service is unavailable" message.** Pros: simpler. Cons: doesn't say where to look.
- **Name the failing service (search vs answer).** Pros: the user, or the developer, knows which dependency broke. Cons: one more error type (`SearchServiceUnavailable`) to maintain.

## Decision
- Question length is checked in the endpoint: under 3 characters after trimming, or over 500, returns HTTP 400 with a plain sentence. `k` keeps its `Field` limits (1–10).
- Messages name the failing service. Embedding failures (connection error, timeout, 5xx) raise `SearchServiceUnavailable`; answer-model failures say "the answer service".
- Status codes by cause:
  - **400** bad input;
  - **503** a service is unavailable (database, embeddings, model timeout or 5xx, connection, rate limit);
  - **502** a service sent a bad reply (unreadable model output twice, a rejected key, other provider errors);
  - **500** anything unknown, with no internals shown.

Every case is covered by a mocked test in `tests/test_api.py`.

## Tradeoffs
- The question-length rule is no longer visible in the OpenAPI schema; a future client reading the schema won't see it.
- Two new error types (`SearchServiceUnavailable`, `ModelOutputError`) and more branches in `friendly_message()`, whose order matters ([Exception hierarchy order](../concepts.md#exception-hierarchy-order-check-the-child-before-the-parent)).
- Naming the service tells a user a little about how the system is built (search and answering are separate services). This was not discussed. The messages show no provider names, file paths, or keys.

## Revisit when
- A second client (a real frontend, a mobile app) needs the limits from the schema.
- The app is deployed beyond localhost and error messages need a security review.
- A new outside dependency is added: it needs its own named message and test.

See [Step 16 (revisited)](../build-log.md#step-16-revisited-mocked-web-api-tests-and-clean-handling-of-outside-service-failures).
